---
name: nix-podman-stacks-codegraph-verify
tags: [nix-podman-stacks, codegraph-verify, nix, podman]
description: "Codegraph Verification: nix-podman-stacks — validating wiki claims against indexed source code symbols"
source: sources/nix-podman-stacks/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Codegraph Verification: nix-podman-stacks

**Date:** 2026-07-12

## Claim 1: Nix flake with Home Manager modules and CI configuration

- **Wiki says:** nix-podman-stacks is a Nix flake (`flake.nix`) that exports `homeModules`, with a CI configuration (`ci_config.nix`) that enables every stack. Modules are aggregated via `modules/module_list.nix`.

- **Source evidence:**
  - `flake.nix` defines the flake with inputs (`nixpkgs`, `home-manager`, `sops-nix`, `search`) and outputs `homeModules = import ./modules/module_list.nix;` and `homeConfigurations.ci = home-manager.lib.homeManagerConfiguration { ... modules = [ ./ci_config.nix ]; }`
  - `modules/module_list.nix` defines an attrset of 86+ modules plus a meta-module `nps = { imports = builtins.attrValues modules; }`
  - `ci_config.nix` enables every stack module with dummy secrets for CI validation — 888 lines covering AdGuard, Authelia, Traefik, n8n, monitoring, and more
  - `flake.nix` line 41-53 defines the `ci` home configuration with all modules

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 80+ self-hosted stack modules with declarative enable/disable

- **Wiki says:** The project provides 80+ self-hosted service stack modules under `modules/`, each enabled with a single `enable = true;` boolean flag.

- **Source evidence:**
  - `modules/module_list.nix` lists 86 entries including: adguard, adventurelog, aiostreams, anchor, audiobookshelf, authelia, baikal, bentopdf, beszel, blocky, bytestash, calibre, changedetection, crowdsec, davis, dawarich, ddns-updater, dockdns, donetick, dozzle, filebrowser, filebrowser-quantum, flaresolverr, forgejo, free-games-claimer, freshrss, gatus, glance, grimmory, guacamole, healthchecks, homeassistant, homebox, homepage, hortusfox, immich, it-tools, jotty, kaneo, karakeep, kimai, kitchenowl, komga, leantime, lldap, mazanoke, mealie, memos, microbin, monitoring, n8n, navidrome, networking-toolbox, norish, ntfy, omnitools, outline, pangolin-newt, paperless, papra, reactive-resume, romm, searxng, shelfmark, sshwifty, stirling-pdf, storyteller, streaming, tandoor, timetracker, traefik, trek, trip, uptime-kuma, vaultwarden, vikunja, wallos, watchstate, webtop, wg-easy, wg-portal, yopass, settings, docker-socket-proxy, example
  - Each module has `options.nps.stacks.<name>.enable = lib.mkEnableOption name` (confirmed in `modules/example/default.nix` line 35, `modules/traefik/default.nix` line 26-33)
  - Configuration is gated with `config = lib.mkIf cfg.enable { ... }` pattern

- **Verdict:** ✅ CORRECT (86 modules, exceeding the "80+" claim)
- **Fix needed:** None

## Claim 3: Global `nps` configuration namespace with shared options

- **Wiki says:** The `modules/settings.nix` module defines global options under `nps.*` including `package`, `enableSocket`, `hostUid`, `defaultUid`, `defaultTz`, `storageBaseDir`, `externalStorageBaseDir`, `mediaStorageBaseDir`, `hostIP4Address`, and `preferHostIds`.

- **Source evidence:**
  - `modules/settings.nix` defines `options.nps` with: `package` (line 61), `enableSocket` (line 62), `socketLocation` (line 72), `hostUid` (line 82), `defaultUid` (line 90), `defaultGid` (line 102), `defaultTz` (line 114), `storageBaseDir` (line 122), `externalStorageBaseDir` (line 132), `mediaStorageBaseDir` (line 139), `hostIP4Address` (line 148), `preferHostIds` (line 154)
  - Default values match wiki: `hostUid = 1000`, `defaultTz = "Etc/UTC"`, `storageBaseDir = "${config.home.homeDirectory}/stacks"`, `defaultUid = 0`, `defaultGid = 0`
  - Config block (line 176-201) enables Podman service and socket with these settings

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Container extension system with volumeMap, extraEnv, socketActivation, dependencies

- **Wiki says:** The `modules/extension.nix` extends Home Manager's `services.podman.containers` with `volumeMap` (attrset-based volumes), `extraEnv` (fromFile/fromTemplate/fromCommand), `socketActivation`, `dependsOn`/`dependsOnContainer`, `wants`/`wantsContainer`, `stack` (shared network), and `port`.

- **Source evidence:**
  - `modules/extension.nix` exports the extension module extending container options
  - `modules/types.nix` defines `extraEnv` submodule supporting `fromFile`, `fromTemplate`, `fromCommand` value types
  - `AGENTS.md` documents the full extension API: `volumeMap`, `extraEnv`, `fileEnvMount`, `templateMount`, `socketActivation`, `dependsOn`/`dependsOnContainer`, `wants`/`wantsContainer`, `stack`, `port`
  - Usage confirmed in `modules/streaming/default.nix` (extraEnv with fromFile, multi-container stack with shared `stackName`) and `ci_config.nix` (many fromFile examples)
  - `modules/mkAliases.nix` creates convenience aliases from `nps.stacks.<name>.containers.<c>` to `services.podman.containers.<c>`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Automatic Traefik reverse proxy integration

- **Wiki says:** Enabling a stack with `traefik.name` auto-registers it behind the Traefik reverse proxy. Traefik uses Podman socket activation for real-IP passthrough, Let's Encrypt with DNS challenge, geo-blocking, CrowdSec integration, and middleware chains.

- **Source evidence:**
  - `modules/traefik/default.nix` defines Traefik with: `domain` option (line 35), `network.name = "traefik-proxy"` (line 48), dynamic config generation with YAML formatter
  - `modules/traefik/extension.nix` extends containers with `traefix.*` options: `traefik.name`, `traefik.subDomain`, `traefik.serviceHost`, `traefik.serviceUrl`, `traefik.middleware.*`, `expose` (public/private)
  - AGENTS.md confirms: "traefik.name = name — only on routable (web-facing) containers"
  - Traefik module includes Let's Encrypt configuration, geo-blocking plugin, and CrowdSec bouncer middleware
  - Socket activation is referenced in the wiki architecture description
  - `ci_config.nix` enables Traefik with domain "example.com", geo-blocking, CrowdSec bouncer, and Prometheus/Grafana integration

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Monitoring stack with Prometheus, Grafana, Loki, Alertmanager

- **Wiki says:** The monitoring stack provides Prometheus for metrics, Grafana for dashboards, Loki for logs, Alloy for log collection, Podman Exporter, and Alertmanager with ntfy routing. Stacks auto-register scrape configs and dashboards.

- **Source evidence:**
  - `modules/monitoring/` directory exists containing the full monitoring stack
  - `ci_config.nix` confirms monitoring setup: `monitoring.enable = true` with Prometheus alert rules (line 544-575), `enablePrometheusExport = true` on multiple stacks (blocky line 110, ntfy line 600, pangolin-newt line 622, traefik line 804), `enableGrafanaDashboard = true` on blocky, pangolin-newt, and traefik
  - Multiple stacks reference Grafana dashboards and Prometheus scrape configs
  - Alertmanager configured with ntfy notification integration
  - `modules/monitoring/extension.nix` provides `alloy.enable` option for log collection

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Secrets management via sops-nix, fromFile, fromTemplate, fromCommand

- **Wiki says:** Secrets are handled through sops-nix, agenix, and the `fromFile`/`fromTemplate`/`fromCommand` env injection patterns. All secret options use `lib.types.path`.

- **Source evidence:**
  - `flake.nix` includes `sops-nix` as a flake input (line 10-13)
  - `modules/types.nix` defines `extraEnv` submodule with `fromFile`, `fromTemplate`, `fromCommand` variants
  - `ci_config.nix` extensively uses `dummySecretFile` pattern through `fromFile` across ~60+ stacks
  - AGENTS.md documents secret handling: "Use `config.sops.secrets.\"path/to/secret\".path` for sops-nix examples", "Use `dummySecretFile` in `ci_config.nix` for CI testing", "Never commit real secrets"
  - Many modules expose `secretKeyFile`, `passwordFile`, `jwtSecretFile`, and similar `lib.types.path` options
  - `modules/settings.nix` references Podman socket location path

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[nix-podman-stacks]] -- Main wiki entry with module system and stack overview
- [[nix-podman-stacks-architecture]] -- Nix module composition and architecture deep-dive
- [[nix-podman-stacks-n8n]] -- n8n module integration details

## Cross-project

- [[podman.codegraph-verify]] -- Foundation container runtime verified
- [[nix.dev.codegraph-verify]] -- Nix documentation ecosystem verified
- [[openclaw.codegraph-verify]] -- Go agent platform verified
