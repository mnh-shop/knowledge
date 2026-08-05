---
name: docker-netbird-codegraph-verify
tags: [docker, netbird, rootless, distroless, wireguard, ztna, container, wiki]
description: "Codegraph Verification: docker-netbird — validating wiki claims against indexed source code symbols"
source: sources/docker-netbird/
---

# Codegraph Verification: docker-netbird

**Date:** 2026-07-30

## Claim 1: Rootless (1000:1000) + distroless (no shell) NetBird image
- **Wiki says:** The container runs rootless as user/group 1000:1000 and is distroless with no shell.
- **Source evidence:**
  - `README.md:24` states: "this image runs [rootless] as 1000:1000"
  - `README.md:25` states: "this image has no shell since it is [distroless]"
  - `README.md:191-192` default settings table: `uid` = 1000, `gid` = 1000
  - `README.md:42-43` comparison table shows distroless ✅ for this image, ❌ for netbirdio/*
- **Verdict:** ✅ CORRECT

## Claim 2: Single image for all NetBird services, dashboard via --dashboard flag
- **Wiki says:** A single container image runs all NetBird services; the dashboard is started with the `--dashboard` command flag.
- **Source evidence:**
  - `README.md:17` states: "this image supports all netbird images as a single image, the dashboard image needs a custom command entry"
  - `compose.yml:40-41` dashboard service uses `command: "--dashboard"` under the same image (`11notes/netbird:0.76.0`)
  - `compose.yml:39` comment confirms: "# start dashboard instead of mangement server"
- **Verdict:** ✅ CORRECT

## Claim 3: 70MB vs 331MB, runs as non-root
- **Wiki says:** This image is 70MB compared to the official netbirdio/* images at 331MB.
- **Source evidence:**
  - `README.md:42` comparison table: `| 11notes/netbird | 70MB | 1000:1000 | ✅ | amd64, arm64 |`
  - `README.md:43` comparison table: `| netbirdio/* | 331MB | 0:0 | ❌ | amd64, arm64, armv7 |`
  - `README.md:4` badge: `image_size-70MB`
- **Verdict:** ✅ CORRECT

## Claim 4: Read-only + no-new-privileges + tmpfs mounts
- **Wiki says:** The container runs read-only with no-new-privileges; transient paths are tmpfs (uid=1000,gid=1000) so the root filesystem stays read-only.
- **Source evidence:**
  - `README.md:28` confirms: "this image runs read-only"
  - `compose.yml:5-8` defines `x-lockdown: &lockdown` with `read_only: true` and `security_opt: ["no-new-privileges=true"]`; all services inherit via `<<: *lockdown`
  - `compose.yml:28-29` server tmpfs `/tmp:uid=1000,gid=1000`; `compose.yml:49-51` dashboard tmpfs `/nginx/cache`, `/nginx/run`; `compose.yml:72-74` postgres tmpfs `/postgres/run`, `/postgres/log`
- **Verdict:** ✅ CORRECT

## Claim 5: Pinned semver build + multi-arch + CVE scanning
- **Wiki says:** The image is built at a pinned semver version (0.76.0, no `:latest`) via a multi-arch CI/CD pipeline with automatic CVE scanning before and after publishing.
- **Source evidence:**
  - `compose.yml:11` pins `image: "11notes/netbird:0.76.0"`
  - `README.md:209` documents the no-`:latest` policy and short semver tags (`:0`, `:0.76`); `README.md:211` documents the `:rolling` tag
  - `arch.dockerfile:100-104` accepts `TARGETPLATFORM` / `TARGETOS` / `TARGETARCH` / `TARGETVARIANT` build args
  - `.github/workflows/org.container.yml:370` sets `DOCKER_IMAGE_DOCKERFILE` default to `arch.dockerfile`; `org.container.yml:257-258` wires grype scanning with fail-on-severity; `org.container.yml:91-105` builds an amd64/arm64/arm/v7 platform matrix
- **Verdict:** ✅ CORRECT

## Claim 6: Ports 3478/udp + 8080/tcp (server) and 3000 (dashboard); 9000/9090 from default config; 443 is only an exposedAddress string
- **Wiki says:** The shipped compose maps 3478:3478/udp and 8080:8080/tcp (server) plus 3000:3000 (dashboard). Health (:9000) and metrics (:9090) come from the default config. Port 443 is not bound by the container — it appears only as the `exposedAddress` string behind a reverse proxy.
- **Source evidence:**
  - `compose.yml:34-35` server ports `- "3478:3478/udp"` and `- "8080:8080/tcp"`
  - `compose.yml:56` dashboard port `- "3000:3000/tcp"`
  - `README.md:52-54` default config: `listenAddress: ":8080"`, `metricsPort: 9090`, `healthcheckAddress: ":9000"`
  - `README.md:59` default config: `exposedAddress: "https://${NETBIRD_FQDN}:443"` (a string; README:241 recommends a reverse proxy to terminate TLS)
- **Verdict:** ✅ CORRECT

## Claim 7: PostgreSQL 18 backend with nightly backups and internal backend network
- **Wiki says:** All NetBird stores use a Postgres backend; the compose uses `11notes/postgres:18` with a `POSTGRES_BACKUP_SCHEDULE`, and the backend network is internal-only.
- **Source evidence:**
  - `README.md:79-89` default config uses `engine: "postgres"` for `store`, `activityStore`, and `authStore` with `dsn: "host=postgres ... port=5432"`
  - `compose.yml:62` postgres service image `11notes/postgres:18`
  - `compose.yml:67` `POSTGRES_BACKUP_SCHEDULE: "0 3 * * *"` with `postgres.backup` volume (`compose.yml:71`)
  - `compose.yml:87-90` networks: `backend: internal: true`
  - `README.md:246` cautions: distroless image only works with PostgreSQL/MySQL, **not SQLite**
- **Verdict:** ✅ CORRECT

## Summary

All 7 key claims from the docker-netbird wiki have been verified against the source code:
- ✅ Rootless (1000:1000) + distroless: Confirmed in README.md
- ✅ Single image with --dashboard flag: compose.yml confirms dashboard command
- ✅ 70MB vs 331MB: Size comparison table confirmed
- ✅ Read-only + no-new-privileges + tmpfs: Lockdown config and tmpfs mounts confirmed in compose.yml
- ✅ Pinned semver + multi-arch + CVE scanning: arch.dockerfile and org.container.yml confirmed
- ✅ Ports: 3478/udp + 8080/tcp + 3000 mapped; 9000/9090 from config; 443 is exposedAddress string
- ✅ PostgreSQL 18 backend: All three stores use postgres engine; postgres:18 service with backup schedule and internal network confirmed

## Related

- [[docker-netbird]] -- Main wiki entry

## Cross-project

- [[bootc.codegraph-verify]] -- Similar container verification
- [[podman-quadlet.codegraph-verify]] -- Similar container deployment verification
