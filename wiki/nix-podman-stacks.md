# nix-podman-stacks

**Source**: `tarow/nix-podman-stacks` on GitHub
**Repository path**: `/Users/admin1/Documents/knowledge/sources/nix-podman-stacks/`
**Type**: Declarative Podman Quadlet management via Nix / Home Manager
**License**: MIT

## Overview

nix-podman-stacks is a collection of opinionated, declarative Podman container stacks managed through Home Manager (Nix). It provides 80+ self-hosted service stacks that can be enabled with a single boolean flag, with automatic integration for reverse proxying, dashboards, monitoring, and secrets management.

**Key design principles:**
- NOT NixOS-specific -- works on most Linux distros (Ubuntu, Arch, Mint, Fedora, etc.)
- Uses rootless Podman with Quadlets under the hood
- Home Manager-based Nix module system (no NixOS required)
- Declarative configuration: enables/disables stacks, defines settings, auto-wires integrations
- Secrets via sops-nix or agenix

## What It Provides

1. **Declarative Quadlet service definitions** -- each stack module defines Podman containers, volumes, networks, and systemd integration as Nix configs that Home Manager renders into Quadlet files
2. **80+ self-hosted stack modules** -- from AdGuard and Authelia to Vaultwarden and Wikijs
3. **Automatic Traefik reverse proxy integration** -- enabling a stack with `traefik.name` auto-registers it behind the reverse proxy
4. **Automatic Homepage dashboard integration** -- enabled stacks appear in the Homepage dashboard automatically
5. **Automatic monitoring integration** -- Prometheus scrape configs and Grafana dashboards auto-configure
6. **OIDC integration** -- Authelia-based single sign-on that auto-registers OIDC clients per stack
7. **Secret management** -- sops-nix / agenix integration, plus flexible `fromFile`/`fromTemplate`/`fromCommand` env injection

## Architecture

nix-podman-stacks is structured as a set of interdependent Nix modules that extend Home Manager's `services.podman` subsystem.

### Module System

The project is a single Nix flake (`flake.nix`) that exports `homeModules`. The entry point is `modules/module_list.nix`, which wraps every individual stack module into a top-level `nps` (nix-podman-stacks) meta-module:

```nix
# module_list.nix (simplified)
modules = {
  settings = ./settings.nix;
  traefik = ./traefik;
  n8n = ./n8n;
  # ... 80+ more
};
# Combined into:
nps = { imports = builtins.attrValues modules; };
```

Each user activates the system by importing `self.homeModules.nps`, which pulls in all stack modules (they are gated by `enable` flags).

### The `nps.stacks` Configuration Namespace

All configuration lives under `nps.stacks.<stack-name>`, defined by each module's `options.nps.stacks.<stack-name>` block. The base module (`modules/settings.nix`) provides global options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `nps.package` | package | `pkgs.podman` | Podman package to use |
| `nps.enableSocket` | bool | `true` | Enable Podman user socket |
| `nps.hostUid` | int | `1000` | Host user UID for socket location |
| `nps.defaultUid` | int | `0` | Default container UID |
| `nps.defaultGid` | int | `0` | Default container GID |
| `nps.defaultTz` | str | `"Etc/UTC"` | Default TZ for containers |
| `nps.storageBaseDir` | path | `$HOME/stacks` | Base dir for persistent volumes |
| `nps.externalStorageBaseDir` | path | required | Base dir for large data (external disk) |
| `nps.mediaStorageBaseDir` | path | `externalStorageBaseDir/media` | Media file storage |
| `nps.hostIP4Address` | str | required | Host IPv4 for explicit bindings |
| `nps.preferHostIds` | bool | `false` | Map container UIDs to host user |

### Container Extension System

The `modules/extension.nix` module extends Home Manager's `services.podman.containers` with powerful options:

- **`volumeMap`** -- Attrset-based volume mappings (replaces raw `volumes` list; allows single-entry overrides)
- **`extraEnv`** -- Flexible env vars supporting `fromFile`, `fromTemplate` (gomplate), and `fromCommand` sources
- **`fileEnvMount`** -- Convenience wrapper for `_FILE` pattern env vars (volume mount + env var in one)
- **`templateMount`** -- Bind mounts that render templates via gomplate before mounting
- **`socketActivation`** -- systemd socket activation, used by Traefik for real-IP passthrough
- **`dependsOn` / `dependsOnContainer`** -- Hard container dependencies (systemd `Requires` + `After`)
- **`wants` / `wantsContainer`** -- Soft container dependencies (systemd `Wants` + `After`)
- **`stack`** -- Network group; all containers with same `stack` join a shared Podman bridge network
- **`port`** -- Main container port (used by Traefik for routing)

The `mkAliases.nix` module creates convenience aliases like `nps.stacks.<name>.containers.<c>` and `nps.containers.<c>` that redirect to `services.podman.containers.<c>`.

### How Quadlet Files Are Generated

Each stack module sets `services.podman.containers.<name>` with container options. Home Manager's podman module then renders these into Quadlet `.container` files (stored under `$HOME/.config/containers/systemd/`). systemd --user picks these up and manages the containers as user services.

## Available Stacks (Important Ones for Agent Deployment)

| Stack | Category | Description |
|-------|----------|-------------|
| **n8n** | Workflow Automation | n8n workflow engine (our core system) |
| **traefik** | Reverse Proxy | Traefik v3 with Let's Encrypt, geo-blocking, CrowdSec |
| **authelia** | Auth | OIDC identity provider for SSO |
| **lldap** | Directory | Lightweight LDAP server |
| **monitoring** | Observability | Prometheus + Grafana + Loki + Alloy + Alertmanager |
| **homepage** | Dashboard | Homepage dashboard (auto-populated from enabled stacks) |
| **crowdsec** | Security | CrowdSec IPS with Traefik bouncer plugin |
| **docker-socket-proxy** | Infrastructure | Secure proxy for the Podman socket |
| **blocky** | DNS | DNS-level adblocker |
| **postgres** | Database | (auto-provisioned per stack) |
| **redis** | Cache | (auto-provisioned per stack) |

## Networking: Traefik Integration

Traefik is the central reverse proxy. It uses Podman socket activation for real-IP passthrough (no network translation). Key features:

1. **Automatic router registration** -- any container with `traefik.name` set gets a Traefik router, service, and middleware config injected via Docker provider labels
2. **Let's Encrypt** -- automatic wildcard certificate with DNS challenge (default: Cloudflare)
3. **Geo-blocking** -- optional `geoblock` plugin restricts access by country
4. **CrowdSec integration** -- optional Traefik bouncer middleware blocks malicious requests
5. **Middleware chains** -- `private` (internal IPs only, default) and `public` (rate-limited, geoblocked, secured headers)

The Traefik extension (`modules/traefik/extension.nix`) extends every container with `traefik.*` options:
- `traefik.name` -- service name / subdomain
- `traefik.subDomain` -- custom subdomain
- `traefik.serviceHost` -- computed FQDN
- `traefik.serviceUrl` -- computed HTTPS URL
- `expose` -- bool: public vs private middleware
- `traefik.middleware.*` -- enable/order custom middlewares

## Monitoring Stack

The monitoring stack (Prometheus + Grafana + Loki + Alloy + Alertmanager + Podman Exporter) provides full observability:

- **Prometheus** -- metrics collection with auto-scrape configs from enabled stacks
- **Grafana** -- dashboards with auto-provisioning from enabled stacks
- **Loki** -- log aggregation
- **Alloy** -- log collector (scrapes containers with `alloy.enable = true` label)
- **Podman Exporter** -- container/pod metrics from the Podman API
- **Alertmanager** -- alert routing to ntfy

Stacks that support Prometheus metrics set `nps.stacks.monitoring.prometheus.settings.scrape_configs` to auto-register. Stacks with Grafana dashboards append to `nps.stacks.monitoring.grafana.dashboards`.

## Secret Management

Secrets are handled through `fromFile` in `extraEnv` or dedicated secret options on each module. The project supports:

- **sops-nix** -- decrypts encrypted secrets at build time; referenced as `config.sops.secrets."path".path`
- **agenix** -- alternative encrypted secret management
- **fromFile** -- reads any file at container runtime into an env variable
- **fromTemplate** -- renders gomplate templates (supports file reads, env vars)
- **fromCommand** -- executes a command to produce the env var value

All secret options use `lib.types.path` to support runtime file reads.

## Compatibility with Our Stack

This project directly intersects with our architecture in several ways:

1. **n8n module** -- an n8n stack module is already built-in and well-integrated with Traefik, Homepage, and the monitoring stack
2. **Rootless Podman + Quadlets** -- aligns with our container runtime strategy (same foundation as Tank OS)
3. **Declarative deployment** -- provides a Nix-native alternative to bootc-based deployment (Tank OS)
4. **Traefik + Let's Encrypt** -- matches our reverse proxy / TLS strategy
5. **OIDC with Authelia** -- provides SSO integration that our agent gateway can leverage

## Relationship to Our Deployment Architecture

nix-podman-stacks represents a **Nix-native container management** approach that complements our bootc-based (Tank OS) strategy:

- **Tank OS** uses bootc for full OS-level image-based updates, running containers via systemd or Quadlet
- **nix-podman-stacks** manages only the user-space containers via Home Manager, without OS coupling
- Together they provide two tiers: OS-level immutability (Tank OS) and declarative container config (nix-podman-stacks)

For our **Hermes agent workspace**, nix-podman-stacks can serve as the declarative configuration layer for the n8n, Traefik, and monitoring containers that the agent infrastructure depends on.

## Key Files and Their Roles

| File | Role |
|------|------|
| `flake.nix` | Flake entry point; defines inputs, outputs, CI config |
| `modules/module_list.nix` | Aggregates all stack modules into the `nps` meta-module |
| `modules/settings.nix` | Global nps options and base Podman config |
| `modules/extension.nix` | Container option extensions (volumeMap, extraEnv, socketActivation, etc.) |
| `modules/types.nix` | Shared Nix types (fromFile, fromTemplate, fromCommand submodules) |
| `modules/mkAliases.nix` | Creates convenience aliases for container configs |
| `modules/traefik/` | Traefik reverse proxy module + static/dynamic config templates |
| `modules/traefik/extension.nix` | Extends containers with `traefik.*` and `port` options |
| `modules/monitoring/` | Prometheus + Grafana + Loki + Alloy + Alertmanager stack |
| `modules/monitoring/extension.nix` | Extends containers with `alloy.enable` for log collection |
| `modules/homepage/` | Homepage dashboard module |
| `modules/homepage/extension.nix` | Auto-populates homepage services from container definitions |
| `modules/n8n/` | n8n workflow automation module |
| `ci_config.nix` | CI test configuration enabling all stacks |
| `docs/` | mdbook documentation |

## How to Use

```nix
# In your Home Manager configuration
{config, ...}: {
  imports = [ inputs.nix-podman-stacks.homeModules.nps ];

  nps = {
    hostIP4Address = "192.168.1.100";
    storageBaseDir = "/home/user/stacks";
    externalStorageBaseDir = "/mnt/data";

    stacks = {
      traefik = {
        enable = true;
        domain = "example.com";
      };
      n8n.enable = true;
      monitoring.enable = true;
      homepage.enable = true;
    };
  };
}
```

## Domain docs & assets

- [Architecture](domains/architecture/nix-podman-stacks-architecture.md) — Nix module system, `nps.stacks` namespace, cross-stack integrations (Traefik, Homepage, Monitoring, OIDC), secret injection
- [n8n Integration](integrations/nix-podman-stacks-n8n.md) — How the n8n module works, options, Traefik/Homepage/Monitoring integration, production gaps and extension patterns
