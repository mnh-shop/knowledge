---
name: podman-quadlet-codegraph-verify
tags: [podman-quadlet, codegraph-verify, podman, quadlet, containers, systemd, homelab]
description: "Codegraph Verification: podman-quadlet — claims verified against upstream fpatrick/podman-quadlet (local clone is corrupted)"
source: sources/podman-quadlet/
---

# Codegraph Verification: podman-quadlet

**Date:** 2026-07-12

> **Provenance note:** the local clone at `sources/podman-quadlet/` is **corrupted** — it is a
> duplicate of `extension-podman-quadlet` (a TypeScript monorepo), so no filesystem enumeration
> of the local checkout can support these claims. All claims below are verified against the
> **upstream `fpatrick/podman-quadlet` repository** (blog.nerdon.eu) via its GitHub structure and
> README. The local clone must be re-cloned from upstream and re-verified against actual file
> contents before this page is considered fully evidenced (re-clone + re-verification is out of
> scope here). No license is declared upstream, so no license claim is made.

## Claim 1: Exactly 25 self-hosted service Quadlet template directories

- **Wiki says:** The repo provides exactly 25 Quadlet template directories, each containing `.container` (and for some services `.pod`, `.network`, `.env`) files for popular self-hosted services.

- **Source evidence:** Upstream GitHub directory listing confirms exactly 25 template dirs:
  - `changedetection/`, `cloudflare/`, `fullfeedrss/`, `homepage/`, `immich/`, `karakeep/`, `kopia/`, `kopia-photos/`, `lidarr-on-steroids/`, `maintainerr/`, `miniflux/`, `n8n/`, `navidrome/`, `ntfy/`, `omada/`, `plex/`, `profilarr/`, `prowlarr/`, `radarr/`, `searxng/`, `sonarr/`, `syncthing/`, `tautulli/`, `wg-easy/`, `wireguard/`
  - Each directory contains at minimum one `.container` file; pod-based services (immich, plex, searxng) include `.pod` files; network-dependent services reference `.network` files such as `rss.network`, `immich.network`, `wireguard.network`
  - Immich is the most complex service: `immich.pod` plus `immich-server`, `immich-db`, `immich-machine-learning`, and `redis` container files

- **Verdict:** ✅ CORRECT (25 template directories, consistent with upstream structure)
- **Fix needed:** Re-clone upstream and re-enumerate on disk

## Claim 2: Template structure follows standard INI sections: [Unit], [Container], [Service], [Install]

- **Wiki says:** Each `.container` file uses the standard Quadlet INI format with `[Unit]` (description, dependencies), `[Container]` (image, volumes, ports, environment), `[Service]` (restart policy, timeouts), and `[Install]` (systemd target).

- **Source evidence:** The upstream README and template listings document this structure consistently; representative examples cited across upstream files:
  - `n8n/n8n.container`: `[Unit]` with `Description`, `Wants`, `After`; `[Container]` with `ContainerName`, `Image`, `Environment`, `Volume`, `Network`, `PublishPort`, `Label`; `[Service]` with `Restart`, `TimeoutStartSec`; `[Install]` with `WantedBy`
  - Common patterns: `ContainerName=`, `Image=`, `Volume=`, `PublishPort=`, `Environment=`, `AutoUpdate=registry`

- **Verdict:** ✅ CORRECT (consistent with upstream structure)
- **Fix needed:** Re-verify section contents against re-cloned files

## Claim 3: Multi-container pod support via `.pod` files (Immich, Plex, SearXNG)

- **Wiki says:** Multi-service applications use Quadlet Pod files to group containers; the Immich template is a pod with server, ML, database, and Redis containers sharing a network namespace.

- **Source evidence:** Upstream structure contains three `.pod` files:
  - `immich/immich.pod`: `[Pod]` section with `PodName=immich`, `PublishPort=2283:2283`, `Network=immich.network`; the Immich containers reference `Pod=immich.pod`, sharing the pod's network namespace and port mapping
  - `plex/plex.pod`: groups the Plex container with companion containers
  - `searxng/searxng.pod`: groups the search container with a Redis container
  - The pod pattern centralizes `PublishPort` at the pod level and enables inter-container communication over `localhost`

- **Verdict:** ✅ CORRECT (pod layout and `PublishPort=2283:2283` consistent with upstream)
- **Fix needed:** Re-verify exact pod/container references against re-cloned files

## Claim 4: WireGuard template uses NET_ADMIN capability

- **Wiki says:** The WireGuard template requires privileged operation: host networking plus `NET_ADMIN` (and `NET_RAW`) capabilities to manage kernel interfaces.

- **Source evidence:** Upstream `wireguard/wireguard.container` uses `AddCapability=NET_ADMIN NET_RAW` in its `[Container]` section, alongside `Network=wireguard.network` and a `PublishPort` — the standard pattern for userspace WireGuard clients in Quadlet. `AutoUpdate=registry` is also present.

- **Verdict:** ✅ CORRECT (consistent with upstream template)
- **Fix needed:** Re-verify capability list against re-cloned file

## Claim 5: Homepage dashboard integration labels

- **Wiki says:** Many `.container` files include `homepage.*` labels for Homepage dashboard auto-discovery (group, name, icon, href, description), and a dedicated `homepage/` template ships the dashboard itself.

- **Source evidence:** The upstream repo includes a dedicated `homepage/` template, and `Label=homepage.*` keys appear across multiple service templates (e.g. n8n with `homepage.group=Automation`, `homepage.name=n8n`, `homepage.icon=n8n.png`, `homepage.href=...`; immich-server with `homepage.group=Media`, `homepage.name=Immich`, `homepage.href=http://10.0.0.3:2283`). These labels are consumed by the gethomepage/homepage dashboard project.

- **Verdict:** ✅ CORRECT (consistent with upstream structure)
- **Fix needed:** Re-verify label keys/values against re-cloned files

## Claim 6: Rootless and rootful deployment support with AutoUpdate

- **Wiki says:** All templates support both rootless (user) and rootful (system) deployment. Rootless files go in `~/.config/containers/systemd/`; rootful in `/etc/containers/systemd/`. `AutoUpdate=registry` enables automatic image updates via `podman-auto-update.timer`.

- **Source evidence:** The upstream `readme.md` explicitly documents both paths — rootless: place `.container` files in `~/.config/containers/systemd/` and use `systemctl --user`; rootful: place files in `/etc/containers/systemd/` and use `sudo systemctl` (without `--user`). The `AutoUpdate=registry` pattern appears in multiple templates (immich-server, immich-db, wireguard) and the README documents `podman-auto-update.timer` for periodic updates. `[Service] Restart=on-failure` is standard across templates.

- **Verdict:** ✅ CORRECT (consistent with upstream README)
- **Fix needed:** Re-verify README wording against re-cloned copy

## Claim 7: Environment variable management via `.env` files

- **Wiki says:** Templates support `EnvironmentFile=` and `Environment=` directives; `.env` files keep sensitive configuration separate from the `.container` file, while inline `Environment=` handles simple key=value pairs.

- **Source evidence:** The upstream README includes a `.env` file template, and templates use both patterns: `EnvironmentFile=immich.env` in the immich-server container plus inline `Environment=` lines for small public config (e.g. `N8N_SECURE_COOKIE=false` in n8n; `SERVERPORT=55127` in wireguard with `PEERS`/`PEERDNS` as commented examples).

- **Verdict:** ✅ CORRECT (consistent with upstream README and templates)
- **Fix needed:** Re-verify exact `Environment=` lines against re-cloned files

## Summary

The 7 claims above were verified against the **upstream `fpatrick/podman-quadlet`** repository structure and README:

- ✅ **25 template directories:** exactly 25 confirmed (not 27; no duplicate n8n/plex rows)
- ✅ **Standard INI sections:** [Unit] [Container] [Service] [Install]
- ✅ **Pod support:** `.pod` files for Immich, Plex, SearXNG; `immich.pod` `PublishPort=2283:2283`
- ✅ **WireGuard:** `NET_ADMIN` capability pattern
- ✅ **Homepage labels:** `homepage.*` in multiple templates
- ✅ **Rootless/rootful + AutoUpdate:** both paths documented; `AutoUpdate=registry` in multiple templates
- ✅ **Environment management:** `EnvironmentFile=` and `Environment=` patterns

**Outstanding:** the local `sources/podman-quadlet/` clone is corrupted (a duplicate of the
`extension-podman-quadlet` TS monorepo). A re-clone from upstream and on-disk re-verification of
these claims is required and is out of scope for this page.

## Related

- [[podman-quadlet]] -- Main wiki entry
- [[podman]] -- Podman container engine
- [[podlet]] -- Quadlet file generator CLI
- [[extension-podman-quadlet]] -- Podman Desktop Quadlet extension
- [[quadlet]] -- Quadlet systemd unit generator

## Cross-project

- [[podman.codegraph-verify]] -- Podman verification
- [[podlet.codegraph-verify]] -- Podlet CLI verification
- [[extension-podman-quadlet.codegraph-verify]] -- Podman Desktop extension verification
