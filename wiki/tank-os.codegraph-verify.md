---
name: tank-os-codegraph-verify
tags: [tank-os, codegraph-verify, bootc, deployment, fedora, podman, quadlet, container]
description: "Codegraph Verification: tank-os — validating wiki claims against indexed source code"
source: sources/tank-os/
---

# Codegraph Verification: tank-os

**Date:** 2026-07-12

## Claim 1: Fedora bootc image pinned to Fedora 44, not latest
- **Wiki says:** "Based on quay.io/fedora/fedora-bootc:44 — pinned to Fedora 44, not latest. LABEL containers.bootc=1."

- **Source evidence:**
  - `bootc/Containerfile:1-5` — Comment: "Pinned to Fedora 44, not `latest` — the OpenShell RPM filenames below are hardcoded to the `fc44` build"; `ARG FEDORA_BOOTC_BASE=quay.io/fedora/fedora-bootc:44`
  - `bootc/Containerfile:8` — `LABEL containers.bootc=1` marks the image bootc-compatible
  - `bootc/Containerfile:10` — Description: "Fedora bootc image for OpenClaw on rootless Podman"
  - `bootc/Containerfile:13-16` — `OPENCLAW_UID=1000`, `OPENCLAW_GID=1000`, `OPENCLAW_SUBID_START=100000`, `OPENCLAW_SUBID_COUNT=65536`
  - `bootc/Containerfile:57-67` — Creates `openclaw` user (UID/GID 1000, home `/var/home/openclaw`), appends `/etc/subuid` + `/etc/subgid` ranges, touches `/var/lib/systemd/linger/openclaw`
  - `bootc/Containerfile:69` — `COPY rootfs/ /` copies Quadlet units, scripts, and system config

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 10 dnf packages plus checksum-verified NVIDIA OpenShell RPMs and a derived OpenClaw image
- **Wiki says:** "10 packages installed via dnf: cloud-init, curl, openssh-server, podman, python3, qemu-guest-agent, shadow-utils, sudo, vim-enhanced; plus openshell + openshell-gateway RPMs, checksum-verified."

- **Source evidence:**
  - `bootc/Containerfile:34-44` — `dnf -y install cloud-init curl openssh-server podman python3 qemu-guest-agent shadow-utils sudo vim-enhanced`
  - `bootc/Containerfile:45-54` — Downloads `openshell-${OPENSHELL_VERSION}-1.fc44.${arch}.rpm` + `openshell-gateway-...rpm` (v0.0.92) from GitHub releases, verifies both against `openshell-checksums-sha256.txt` with `sha256sum -c -`, then installs them
  - `bootc/Containerfile:22-28` — `OPENCLAW_REF=2026.7.1`; `OPENCLAW_OPENSHELL_IMAGE=quay.io/redhat-et/tank-claw-openshell:2026.7.1`
  - `bootc/openclaw-openshell/Containerfile:15-44` — Derived image: `FROM ghcr.io/openclaw/openclaw:${OPENCLAW_REF}` + `openssh-client` + the `openshell` musl CLI tarball (also checksum-verified)
  - `bootc/Containerfile:82-83` — Build-time `sed -i` rewrites the Quadlet `Image=` line to the derived openshell image
  - `Makefile:8,13,19` — `OPENCLAW_REF ?= 2026.7.1`, `OPENSHELL_VERSION ?= 0.0.92`, `IMAGE_OPENCLAW_OPENSHELL_URI ?= quay.io/redhat-et/tank-claw-openshell`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Quadlet units — openclaw uses Network=host, service-gator binds 127.0.0.1
- **Wiki says:** "openclaw.container runs with Network=host, Pull=newer, :Z volume, EnvironmentFile, User=%U:%G, TimeoutStartSec=900, After=openshell-gateway.service, two ExecStartPre scripts. Only service-gator binds 127.0.0.1:8080."

- **Source evidence:**
  - `bootc/rootfs/etc/containers/systemd/users/1000/openclaw.container:1-29` — `After=openshell-gateway.service`, `Pull=newer`, `UserNS=keep-id`, `Network=host`, `User=%U:%G`, `Volume=%h/.openclaw:/home/node/.openclaw:Z`, `EnvironmentFile=%h/.openclaw/openclaw.env`, `Exec=node dist/index.js gateway --allow-unconfigured --bind lan --port 18789`, `ExecStartPre=bootstrap-openclaw`, `ExecStartPre=bootstrap-openshell-sandbox`, `TimeoutStartSec=900`
  - `bootc/rootfs/etc/containers/systemd/users/1000/service-gator.container:5-25` — `PublishPort=127.0.0.1:8080:8080`, `:Z` volumes, `Environment=GH_TOKEN_FILE=/run/secrets/gh_token` (+ gitlab/forgejo/jira), `ExecStartPre=bootstrap-service-gator`
  - `bootc/Containerfile:88-89` — Symlinks `openshell-gateway.service` into the user `default.target.wants`
  - `docs/openshell.md:30-33,66-85` — Explains `Network=host` is required so the in-container `openshell` CLI can reach the host gateway on `https://127.0.0.1:17670`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (old wiki snippet with HealthCmd/PublishPort 18789/18790 was replaced; openclaw no longer binds ports at all — it uses the host network)

## Claim 4: Secret management — 7 OpenClaw + 4 service-gator secrets, drop-ins + openclaw.json rewrite
- **Wiki says:** "sync-podman-secrets writes Quadlet drop-ins for detected secrets and rewrites openclaw.json (model allowlist, primary model, base URLs, Telegram channel)."

- **Source evidence:**
  - `bootc/rootfs/usr/libexec/tank-os/sync-podman-secrets:30-36` — 7 OpenClaw secrets: `anthropic_api_key`, `openai_api_key`, `gemini_api_key`, `google_api_key`, `openrouter_api_key`, `model_endpoint_api_key`, `telegram_bot_token`
  - `bootc/rootfs/usr/libexec/tank-os/sync-podman-secrets:53-56` — 4 service-gator secrets: `gh_token`, `gitlab_token`, `forgejo_token`, `jira_api_token`
  - `bootc/rootfs/usr/libexec/tank-os/sync-podman-secrets:9-12,38-63` — Writes `openclaw.container.d/10-secrets.conf` + `service-gator.container.d/10-secrets.conf` Quadlet drop-ins
  - `bootc/rootfs/usr/libexec/tank-os/sync-podman-secrets:65-211` — Embedded python3 rewrites `~/.openclaw/openclaw.json`: `ALLOWLIST_MODELS` map, `PRIMARY_MODEL_PREFERENCE`, provider `baseUrl`/`api` backfill, Telegram `botToken`
  - `bootc/rootfs/usr/local/bin/tank-openclaw-secrets:1-13` — sudo-delegating wrapper into `sync-podman-secrets`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (secrets list expanded from 5 to 7 OpenClaw secrets)

## Claim 5: CLI wrapper — sudo-delegating, --container flag, running-container check
- **Wiki says:** "Host `openclaw` command delegates into the running container: re-executes via sudo as openclaw if needed, supports --container, checks the container is running, then podman exec openclaw "$@".

- **Source evidence:**
  - `bootc/rootfs/usr/local/bin/openclaw:28-34` — `if [[ "$(id -un)" != "openclaw" ]]` → `exec sudo -iu openclaw -- /usr/local/bin/openclaw --container ...`
  - `bootc/rootfs/usr/local/bin/openclaw:8-26` — `--container` / `--container=` flag parsing; `OPENCLAW_CONTAINER` env default
  - `bootc/rootfs/usr/local/bin/openclaw:36-40` — Running-container check via `podman inspect --format '{{.State.Running}}'` with a `systemctl --user start openclaw.service` hint
  - `bootc/rootfs/usr/local/bin/openclaw:42-49` — `podman exec [-it] <container> openclaw "${args[@]}"` (executes the container's `openclaw` binary, not `node dist/index.js`)
  - `bootc/Containerfile:72-79` — `chmod 0755` on the wrapper + bootstrap scripts

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Build system — derived-image, QCOW2, containerDisk, ISO, multi-arch
- **Wiki says:** "Makefile targets: build-openclaw-openshell, push-openclaw-openshell, build, push, build-qcow2, build-containerdisk, push-containerdisk, push-containerdisk-arch, build-iso, lint, verify, clean. Multi-arch bootc-image-builder with --rootfs xfs."

- **Source evidence:**
  - `Makefile:112-123` — `build-openclaw-openshell` / `push-openclaw-openshell` (derived image, built BEFORE the main image)
  - `Makefile:89-97` — `build` with a warning if the derived openshell image is missing locally
  - `Makefile:125-145` — `build-qcow2`: rootful `bootc-image-builder` run with `--type qcow2`, `--rootfs xfs`, `--target-arch $(ARCH)`, `--local`
  - `Makefile:150-186` — `build-containerdisk` (wraps `out-tank-os/qcow2/disk.qcow2`), `push-containerdisk`, `push-containerdisk-arch` (safe multi-arch merging)
  - `Makefile:188-208` — `build-iso` (`--type anaconda-iso`); `Makefile:26-36` — `uname -m` → ARCH auto-detection
  - `deploy/containerdisk/Containerfile:12-13` — `FROM scratch; COPY disk.qcow2 /disk/` (KubeVirt containerDisk convention)
  - `VERSION` + `.github/workflows/create-release.yml`/`build-release.yml` — `python-semantic-release` versioning, cosign signing, SBOM/provenance, Trivy

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: OpenShell sandbox integration (gateway, plugin install, sandbox pre-create, config backfill)
- **Wiki says:** "openshell-gateway runs on the VM host as a rootless user service (unit ships in the RPM); bootstrap-openshell-sandbox installs the plugin, registers the gateway, and pre-creates the tankos-openclaw sandbox; bootstrap-openclaw backfills openclaw.json."

- **Source evidence:**
  - `bootc/Containerfile:88-89` — Symlinks the RPM-shipped `openshell-gateway.service` into the user default target
  - `bootc/rootfs/usr/libexec/tank-os/bootstrap-openshell-sandbox:35-50` — Derived-image default `__OPENCLAW_OPENSHELL_IMAGE_DEFAULT__` (sed-rewritten at build), gateway endpoint `https://127.0.0.1:17670`, digest-pinned sandbox image
  - `bootc/rootfs/usr/libexec/tank-os/bootstrap-openshell-sandbox:52-68` — One-shot `podman run` installs `@openclaw/openshell-sandbox` into the persisted `~/.openclaw` volume (`:z` shared relabel)
  - `bootc/rootfs/usr/libexec/tank-os/bootstrap-openshell-sandbox:84-102` — `openshell gateway add` + `sandbox create --name tankos-openclaw --from <digest>` (with `timeout 600` guard)
  - `bootc/rootfs/usr/libexec/tank-os/bootstrap-openclaw:15-69` — First-run `openclaw.json` with `agents.defaults.sandbox.backend: "openshell"` and `plugins.entries.openshell`
  - `bootc/rootfs/usr/libexec/tank-os/bootstrap-openclaw:71-109` — In-place python3 backfill of sandbox/plugin config for pre-OpenShell configs
  - `docs/openshell.md:12-41` — Documents where each OpenShell piece runs; `docs/openshell.md:171-194` — CAP_SYS_PTRACE egress-policy limitation

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Cloud-init, qemu-guest-agent, KubeVirt/OpenShift Virtualization, Lima
- **Wiki says:** "cloud-init services enabled; qemu-guest-agent included; KubeVirt containerDisk + ArgoCD ApplicationSet per-user VMs; Lima configs for local prebuilt-disk testing."

- **Source evidence:**
  - `bootc/Containerfile:90-101` — Enables `cloud-init-local`, `cloud-init-network`, `cloud-init`, `cloud-config`, `cloud-final`, `cloud-init.target`
  - `bootc/Containerfile:41` — `qemu-guest-agent` in the dnf install list
  - `examples/cloud-init/openclaw-user-data.yaml` — NoCloud user-data (openclaw user, wheel, passwordless sudo, SSH keys, `loginctl enable-linger`)
  - `deploy/base/virtualmachine.yaml:44-70` — KubeVirt VirtualMachine with `containerDisk` volume + `cloudInitNoCloud` userData
  - `deploy/applicationset.yaml:9-35` — ArgoCD ApplicationSet with `goTemplate: true` and a list generator (one Application per user)
  - `examples/lima/tank-os-qemu.yaml:32-43` (+ `tank-os-krunkit.yaml`, `tank-os-vz.yaml`) — Lima configs with `vmType: qemu`/`krunkit`/`vz`, no guest agent, disk extracted from the containerDisk image
  - `examples/bootc-config.toml` — bootc-image-builder customization template with SSH key injection

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the Tank OS wiki have been verified against the source code:
- ✅ **Fedora 44 pin:** `fedora-bootc:44` with `containers.bootc=1`, UID 1000 user, subuid/subgid, linger
- ✅ **Packages:** 10 dnf packages + checksum-verified OpenShell RPMs + derived `tank-claw-openshell` image
- ✅ **Quadlets:** openclaw `Network=host` (no port publish), service-gator loopback-only, :Z volumes, bootstrap ExecStartPre
- ✅ **Secrets:** 7 OpenClaw + 4 service-gator, drop-ins + openclaw.json config rewrite
- ✅ **CLI wrapper:** sudo-delegating with `--container`, running-container check, container `openclaw` binary
- ✅ **Build system:** derived-image/QCOW2/containerDisk/ISO targets, multi-arch, semantic-release CI
- ✅ **OpenShell:** host gateway + in-container CLI + pre-created sandbox + config backfill
- ✅ **Cloud-init / virtualization:** qemu-guest-agent, KubeVirt containerDisk, ArgoCD ApplicationSet, Lima configs

The image is a well-scoped bootc appliance that packages OpenClaw as a rootless Podman service with Quadlet, NVIDIA OpenShell sandboxing, cloud-init, and a secret-sync engine — validating its claim as a deployment exemplar.

## Related

- [[tank-os]] -- Main wiki entry
- [[tank-os-architecture]] -- Architecture description
- [[tank-os-deployment]] -- Deployment guide
- [[tank-os-quadlet]] -- Quadlet unit file configuration

## Cross-project

- [[openclaw.codegraph-verify]] -- Agent gateway packaged by tank-os
- [[podman.codegraph-verify]] -- Container runtime foundation
- [[bootc]] -- Bootable container technology
- [[hermes-agent.codegraph-verify]] -- Comparable agent deployment pattern
