---
name: nix-podman-stacks-extension-api
tags: [nix-podman-stacks, architecture, nix, home-manager, podman, quadlet, systemd, traefik, monitoring, secrets, sops-nix, container-options]
description: "nix-podman-stacks extension API — the services.podman.containers option extensions (volumeMap, extraEnv, fileEnvMount, templateMount, socketActivation, dependsOn, wants, stack, port) and how Traefik, monitoring, and secret injection wire through them"
source: sources/nix-podman-stacks/
---

# nix-podman-stacks Extension API

**Source:** `sources/nix-podman-stacks/`
**License:** MIT
**Repository:** github.com/Tarow/nix-podman-stacks

This document is the reference for the **container extension system** at the heart of nix-podman-stacks: how `modules/extension.nix` extends Home Manager's `services.podman.containers` submodule with integration options, and how Traefik, the monitoring stack, and the secrets system consume those options. It complements [[nix-podman-stacks-architecture]] (module composition and cross-stack wiring) by focusing on the per-container API surface.

## 1. The `services.podman.containers` Extension (`modules/extension.nix`)

Every stack module declares containers through `services.podman.containers.<name>`. The extension module wraps that submodule and adds the following per-container options:

| Option | Line | Type / Default | Behavior |
|---|---|---|---|
| `dependsOn` | :25 | `listOf str` / `[]` | Hard dependency on a service name — emits systemd `Requires` + `After` |
| `dependsOnContainer` | :39 | `listOf str` / `[]` | Hard dependency on another container (auto-applies name pre/suffix) |
| `wants` | :50 | `listOf str` / `[]` | Soft dependency — systemd `Wants` + `After` |
| `wantsContainer` | :64 | `listOf str` / `[]` | Soft dependency on another container |
| `extraEnv` | :80 | `attrsOf (nullOr primitiveOrSubmodule)` | Flexible env vars — literal values, or `fromFile`/`fromTemplate`/`fromCommand` submodules (from `types.nix`) |
| `volumeMap` | :105 | attrset of volume mappings | Attrset-based volume definitions; replaces the raw `volumes` list and allows single-entry overrides |
| `fileEnvMount` | :121 | attrs of `{sourcePath; destPath}` | `_FILE`-pattern convenience: bind-mount a file and inject its path as an env var in one option |
| `templateMount` | :187 | `listOf {destPath; template}` | Bind mounts that render a gomplate template before mounting |
| `socketActivation` | :249 | `listOf {port; fileDescriptorName}` | Creates a systemd socket that socket-activates the container — used by Traefik for real-IP passthrough (no pasta/slirp4netns proxying) |
| `stack` | :284 | `nullOr str` / `null` | Network group — all containers with the same `stack` join a shared Podman bridge network |
| `port` | :253 (within socketActivation entries) / per-stack | port | Main container port, consumed by Traefik for routing |

### Rendered systemd/quadlet output

The extension's `config` block folds these options into the underlying Home Manager container representation (`extension.nix:300-354`):

- `extraLiteralEnv`/`extraFileContentEnv`/`extraTemplateEnv`/`extraCommandEnv` split `extraEnv` by value type and are mounted into `/run/user/${hostUid}/${name}/extra_env/{from_file_content,from_template_string,from_command}` for the container's environment setup.
- `volumes` are assembled from `volumeMap` (attrValues :344) plus `fileEnvMount` and `templateMount` destinations (:345-346).
- `systemd.services."podman-<name>".unit.Requires/Wants/After` are set from `dependsOn`/`dependsOnContainer`/`wants`/`wantsContainer` (:351-353).
- Setup units (`podman-<name>-setup-volumes` :371, `podman-<name>-create-extra-files` :381) provision volumes and render templates before container start.
- `mkAliases.nix` exposes convenience aliases `nps.stacks.<name>.containers.<c>` and `nps.containers.<c>` that redirect to `services.podman.containers.<c>`.

Home Manager then renders these container options into Quadlet `.container` files (`settings.nix:176-201` enables the podman service/socket), which `systemd --user` manages as user services.

## 2. Traefik Label Injection Flow

The Traefik integration is two-sided: the stack module (`modules/traefik/default.nix`) and a container extension (`modules/traefik/extension.nix`).

### Container-side extension (`modules/traefik/extension.nix`)

Adds `traefik.*` options to every container:

| Option | Line | Behavior |
|---|---|---|
| `expose` | :44 | `false` → private middleware (internal IPs only); `true` → public middleware (internet-facing, rate-limited, geoblocked) |
| `traefik.name` | :58 | Service name / subdomain used for routing |
| `traefik.subDomain` | :68 | Custom subdomain (defaults to `traefik.name`) |
| `traefik.serviceHost` | :98 | Computed FQDN — `"${subDomain}.${nps.stacks.traefik.domain}"` |
| `traefik.serviceUrl` | :132 | `"https://${serviceHost}"` — used by other integrations (e.g. OIDC redirects) |
| `traefik.middleware` | :146 | `{private, public, ...}.enable/order` — which middleware chain applies |

**Label generation** (:191-200): when `traefik.name` is set, the extension emits Docker-provider labels for the Traefik container:

```nix
labels = {
  "traefik.enable" = "true";
  "traefik.http.routers.${name}.rule" = "Host(`${serviceHost}`)";
  "traefik.http.routers.${name}.service" = lib.mkDefault name;
  "traefik.http.services.${name}.loadbalancer.server.port" = containerPort;  # when port is set
  "traefik.http.routers.${name}.middlewares" = "...";  # @file middleware chain
};
```

Containers with `traefik.name` are also joined to the shared Traefik bridge network (`network = [stackCfg.network.name]`); if Traefik is disabled the container port falls back to the `ports` section (`ports` at :206).

### Stack-side module (`modules/traefik/default.nix`)

- `domain` option (:34) — base domain; a Let's Encrypt **wildcard** certificate is requested via DNS challenge (:78) and attached to the edge.
- `network.name` (:46-48) — the `traefik-proxy` Podman bridge network that all routable containers join.
- `geoblock` (:113) — optional geoblock plugin; when enabled the `public` middleware chain prepends the geoblock middleware (:217-220).
- `socketActivation` (:288) — Traefik itself runs socket-activated so it receives real client IPs instead of the pasta/slirp4netns translation address.
- CrowdSec bouncer integration and middleware chains (`private` for internal, `public` = rate-limit + security headers + geoblock + CrowdSec) are composed in the dynamic config (`config/traefik.nix`).

## 3. Monitoring Auto-Registration

The monitoring stack (`modules/monitoring/`) is composed of Prometheus, Grafana, Loki, Alloy, Podman Exporter, and Alertmanager (with ntfy routing). Registration happens through the same per-container extension pattern:

- **`modules/monitoring/extension.nix`** — adds `alloy.enable` (:11) per container; when the monitoring stack is enabled and a container opts in, it sets `labels."logging.alloy" = "true"` (:15). Alloy's default config (:190-197) ships logs of every container with that label to Loki.
- **Scrape configs** — stacks with `enablePrometheusExport = true` (per-stack option, e.g. `ntfy/default.nix:22`, `crowdsec/default.nix:144`) append targets to `nps.stacks.monitoring.prometheus.settings.scrape_configs` (prometheus_config at `default.nix:348`; crowdsec :149).
- **Grafana dashboards** — stacks with `enableGrafanaDashboard = true` (e.g. `ntfy/default.nix:21`, `crowdsec/default.nix:143`) append dashboard JSON to `nps.stacks.monitoring.grafana.dashboards`, which the monitoring module stages into Grafana's provisioning directory (`default.nix:38-42`).
- **Alerting** — `alertmanager` settings/rules (`rules` option at `default.nix:223`) route to ntfy; Grafana OIDC via Authelia is wired in the monitoring module config (:37-59).

## 4. Secret Injection Patterns

Secrets flow from encrypted storage into container environments through `types.nix` submodules used by `extraEnv` (and by dedicated per-stack secret options):

| Source type | `types.nix` line | Description |
|---|---|---|
| `fromFile` | :8 | `nullOr path` — read the file's contents as the env var value at runtime |
| `fromTemplate` | :14 | `nullOr str` — a **gomplate** template string rendered before injection (`DB_URL={{ env.getEnv \`DB_USERNAME\` }}:{{ file.Read \`/run/secrets/db_password\` }}@localhost:5432/mydb`) |
| `fromCommand` | :30 | `nullOr str` — a shell command executed to produce the value (must output a single line) |

Exactly one of `fromFile`/`fromTemplate`/`fromCommand` may be set per entry (validation at `extension.nix:508-529`). The values are materialized by the container's `create-extra-files` setup unit (:381) into `/run/user/${hostUid}/${name}/extra_env/` paths, which are then injected as environment variables.

**Encrypted-at-rest options:** the project supports [sops-nix](https://github.com/Mic92/sops-nix) (flake input, README:34) and agenix. Stacks typically expose `secretKeyFile`/`passwordFile`/`jwtSecretFile`-style options of type `lib.types.path`, whose runtime path is provided by `config.sops.secrets."path".path`. Many stack modules additionally accept a `dummySecretFile` for CI (see `ci_config.nix`, 916 lines, which enables every stack with dummy secrets).

## 5. Cross-Stack Wiring Summary

```
nps.stacks.<name>.enable = true
        │
        ├── services.podman.containers.<c> (extension.nix options)
        │     ├── extraEnv{fromFile,fromTemplate,fromCommand} ──► create-extra-files setup unit
        │     ├── volumeMap / fileEnvMount / templateMount ────► volumes + template rendering
        │     ├── dependsOn / wants ──────────────────────────► systemd Requires/Wants/After
        │     ├── stack ──────────────────────────────────────► shared Podman bridge network
        │     └── socketActivation ───────────────────────────► systemd socket units
        │
        ├── traefik.name/port/expose ──────────────────────────► Docker-provider labels → Traefik router/service/middleware
        ├── alloy.enable ──────────────────────────────────────► label logging.alloy=true → Loki via Alloy
        ├── enablePrometheusExport ────────────────────────────► prometheus scrape_configs
        ├── enableGrafanaDashboard ────────────────────────────► grafana dashboards provisioning
        └── homepage.* ────────────────────────────────────────► homepage.extension.nix mergedServices → dashboard services
```

The `homepage` extension (`modules/homepage/extension.nix`) similarly folds containers with a `homepage.category` into `nps.stacks.homepage.services` (mergedServices :11, assigned :28) so enabled stacks appear on the dashboard automatically.

## Related

- [[nix-podman-stacks]] — Wiki overview
- [[nix-podman-stacks-architecture]] — Module composition and cross-stack architecture
- [[nix-podman-stacks-n8n]] — n8n module specifics
- [[podman]] — Runtime underneath the Quadlets
- [[traefik]] — Reverse proxy consumed by this extension API
