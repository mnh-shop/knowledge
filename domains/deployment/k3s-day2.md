---
name: k3s-day2
tags: [k3s, kubernetes, day2, operations, install, rootless, cridockerd, channel, release, building, deployment]
description: "K3s day-2 operations — install script variants, rootless mode, cridockerd Docker shim, version channels and release cadence, build process"
source: sources/k3s/
---

# K3s Day-2 Operations

This guide covers the ongoing-operations surface of a K3s cluster: install script variants, rootless mode, the cridockerd Docker runtime shim, the `channel.yaml` version channels and release cadence, and the `BUILDING.md` build process.

## Install Script Variants

The single entry point is `install.sh` (`curl -sfL https://get.k3s.io | sh -`):

- Installs K3s plus utilities `kubectl`, `crictl`, `k3s-killall.sh`, `k3s-uninstall.sh` (README.md:156).
- Writes kubeconfig to `/etc/rancher/k3s/k3s.yaml` (README.md:155).
- Adds a systemd (or openrc) service automatically.

Environment-variable variants:

| Use case | Invocation |
|---|---|
| Server (single node) | `curl -sfL https://get.k3s.io | sh -` |
| Worker node join | `curl -sfL https://get.k3s.io | K3S_URL=https://server:6443 K3S_TOKEN=XXX sh -` (README.md:167) |
| HA first node | `... sh -s - server --cluster-init` |
| HA additional server | `... sh -s - server --server https://server:6443 --token XXX` |
| Air-gapped | `INSTALL_K3S_SKIP_DOWNLOAD=true` with a local binary/tarball |

## Rootless Mode

`k3s-rootless.service` ships in-tree alongside `k3s.service`, enabling the server/agent to run without root privileges. Rootless operation uses `rootlesskit`/user namespaces (via the packaged host utilities) so the cluster can run on constrained and unprivileged hosts.

## cridockerd (Docker Runtime Shim)

`pkg/agent/cridockerd/cridockerd.go` (with `config_linux.go`, `config_windows.go`, `nocridockerd.go`) provides a **dockerd shim**: clusters that must run a Docker-compatible runtime use `--docker` to swap the bundled containerd for a system dockerd, while keeping the rest of the CRI stack intact. This is the supported path for workloads with Docker-specific image/runtime expectations.

## Version Channels & Release Cadence

- **Release cadence** (README.md:135): patch releases within **one week**, new minor versions within **30 days** of upstream Kubernetes.
- **Versioning** (README.md:137): `v1.27.4+k3s1` maps to upstream `v1.27.4` with a `+k3s<N>` postfix for K3s-specific patch releases.
- **`channel.yaml`**: defines the update channels consumed by the install script:
  - `stable` — pinned latest stable (`latest: v1.36.2+k3s1`)
  - `latest` — newest release matching `latestRegexp: .*` with an exclude regexp
  - `testing` — pre-release builds (`-(alpha|beta|rc)`)
  - per-minor channels (`v1.16`, `v1.17`, ...) and `*-testing` variants
- **`updatecli/`** (`updatecli.d/`, `values.yaml`, `scripts/`, `manual.d/`): dependency-bump and release automation that keeps `channel.yaml` and the component versions current.

## Building from Source

`BUILDING.md` documents the build process for the `k3s` binary:

- Build tooling: `Makefile`, `scripts/` (build/package/test scripts), `Dockerfile`/`Dockerfile.manifest` (multi-arch builds), `package/` (packaging assets).
- Multi-arch targets: x86_64, armhf, arm64, and s390x (README.md:173).
- CI: `tests/` (integration + unit coverage workflows), `docker-compose.yml` for dev environments.
- `ADOPTERS.md` lists production adopters; `ROADMAP.md` the forward plan.

## Upgrade Playbook

1. Check the target channel in `channel.yaml` (e.g., `stable` → `v1.36.x+k3sN`).
2. Upgrade servers first: `curl -sfL https://get.k3s.io | sh -` re-runs the installer to the latest channel version.
3. Upgrade agents after servers.
4. For HA: upgrade one server at a time, keeping etcd quorum.
5. Verify with `k3s kubectl get nodes` and the bundled `k3s-killall.sh`/`k3s-uninstall.sh` for clean rollback paths.

## Related

- [[k3s]] — Main wiki entry
- [[k3s-ha]] — HA deployment deep-dive
- [[k3s-edge-networking]] — Edge networking deep-dive
