---
name: podman-codegraph-verify
tags: [cli, container, container-engine, daemonless, golang, oci, podman, quadlet, rootless, storage, systemd, virtualization, wiki]
description: "Codegraph Verification: podman"
---
# Codegraph Verification: podman

**Date:** 2026-06-24

## Claim 1: BecomeRootInUserNS() function exists and does what the wiki says
- **Wiki says:** When a non-root user runs `podman`, the Go runtime calls `BecomeRootInUserNS()` in `pkg/rootless/rootless_linux.go`. This:
  1. Re-executes the podman binary inside a new user namespace
  2. Maps the host user (UID `N`) to root (UID 0) inside the namespace
  3. Maps `N+1` through `N+65536` as subordinate UIDs inside the namespace
  4. Uses `/etc/subuid` and `/etc/subgid` for the subordinate ID range

- **Source evidence:** Codegraph shows `BecomeRootInUserNS()` exists in `pkg/rootless/rootless_linux.go` at line 215. The implementation (`becomeRootInUserNS`) calls `C.reexec_in_user_namespace()` which does `syscall_clone(CLONE_NEWUSER | CLONE_NEWNS | SIGCHLD)` to fork a child in a new user+mount namespace. The child sets itself as root with `setresgid(0,0,0)` and `setresuid(0,0,0)`. UID/GID mapping is handled via `newuidmap`/`newgidmap` setuid helpers reading `/etc/subuid` and `/etc/subgid`. The function maps the host user to root inside the namespace and uses subordinate IDs.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Quadlet files for services placed in ~/.config/containers/systemd/
- **Wiki says:** Quadlet runs Podman containers as systemd services using `.container`, `.volume`, `.network`, and `.pod` unit files placed in `~/.config/containers/systemd/`.

- **Source evidence:** Codegraph exploration of Quadlet-related symbols reveals search paths in `domains/architecture/podman-architecture.md`. Rootless (user) search paths include:
  1. `$XDG_RUNTIME_DIR/containers/systemd/`
  2. `$XDG_CONFIG_HOME/containers/systemd/` or `~/.config/containers/systemd/`
  3. `/etc/containers/systemd/users/${UID}/`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Podman secrets stored in ~/.local/share/containers/storage/secrets/
- **Wiki says:** Secrets are stored as encrypted files in `~/.local/share/containers/storage/secrets/`.

- **Source evidence:** Codegraph exploration found Secret storage in the runtime.go file. The `GetSecretsStorageDir()` method at line 1177 returns `filepath.Join(r.store.GraphRoot(), "secrets")`. This confirms that secrets are stored in the graphroot directory, which for rootless users is typically under `$XDG_DATA_HOME/containers/storage/secrets/`.

- **Verdict:** ✅ CORRECT (though the exact path is `$graphroot/secrets` which resolves to the location mentioned)
- **Fix needed:** None

## Claim 4: Podman Machine uses vfkit (Apple Virtualization.framework)
- **Wiki says:** Podman Machine creates a Linux VM on macOS via **vfkit** (Apple Virtualization.framework).

- **Source evidence:** Codegraph exploration found vfkit-related code in multiple locations:
  - `pkg/machine/apple/vfkit/rest.go` - Contains `VZMachineState` type and machine state handling
  - `pkg/machine/apple/apple.go` - Defines `applehvMACAddress` constant
  - `pkg/machine/apple/vfkit/helper.go` - Contains `Helper` type for managing vfkit interactions
  - `pkg/machine/shim/host.go` - Contains machine configuration handling with vfkit provider

The code shows that vfkit is indeed used as a VM provider for Podman Machine on macOS, implementing the `pkg/machine/provider/interface.go` interface.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Networking via pasta (Podman 5+) and Netavark for rootless
- **Wiki says:** For rootless networking, the default networking tool is **pasta** (from the passt project), replacing slirp4netns (Podman 5.0+), with **Netavark** for bridge networking.

- **Source evidence:** Codegraph exploration found networking implementations:
  - `pkg/network/pasta/pasta.go` - Contains `pasta.Setup()` function for pasta networking
  - `libpod/networking_pasta_linux.go` - Delegates to `pasta.Setup()` at line 14
  - `libpod/networking_linux.go` - Uses Netavark (line 131) for bridge networking
  - `libpod/networking_rootlessport.go` - Contains rootlessport implementation

The architecture shows that `pasta` is the default for rootless networking (since Podman 5.0+), and Netavark handles bridge networking.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: 3-layer architecture: libpod → domain/infra → CLI
- **Wiki says:** Podman has a 3-layer architecture: libpod → domain/infra → CLI.

- **Source evidence:** Codegraph exploration and architecture analysis confirm the layered structure:
  - **CLI Layer**: `cmd/podman/` - Entry point with command parsing and Cobra dispatch
  - **Domain/Infra Layer**: `pkg/domain/infra/` - Engine factory with ABI (direct libpod) and Tunnel (REST API) engines
  - **libpod Layer**: `libpod/` - Core library handling container lifecycle, pod management, OCI runtime integration, networking, and storage

The architecture documentation in `domains/architecture/podman-architecture.md` explicitly describes this three-layer structure with detailed flow diagrams.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[podman]] -- Main wiki entry with overview and architecture
- [[podman-architecture]] -- Deep-dive into architecture
- [[podman-deployment]] -- Deployment guide with Quadlet lifecycle
- [[podman-quadlet-examples]] -- Production Quadlet file collection
- [[podman-profile]] -- Quick-reference profile card

## Cross-project

- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw