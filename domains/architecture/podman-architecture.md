---
name: podman-architecture
tags: [podman, container-engine, architecture]
description: "Podman Architecture"
---
# Podman Architecture
**Source:** `sources/podman/`

## Overview

Podman is a **daemonless container engine** structured around three architectural layers. Unlike Docker, there is no central daemon -- each `podman` invocation either links directly against the libpod library (ABI mode) or connects to `podman system service` via a Unix socket (Tunnel mode). Rootless execution is the default and is enforced by a C reexec mechanism that enters a user+mount namespace before Go `init()` runs.

```
┌──────────────────────────────────────────────┐
│                   CLI                         │
│            cmd/podman/ subcommands             │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│          Domain/Infra Engine Factory          │
│        pkg/domain/infra/                      │
│  ┌─────────────┐      ┌──────────────────┐   │
│  │ ABI Engine   │      │  Tunnel Engine   │   │
│  │ (direct      │      │  (REST API       │   │
│  │  libpod)     │      │   client)        │   │
│  └──────┬──────┘      └───────┬──────────┘   │
└─────────┼──────────────────────┼──────────────┘
          │                      │
          ▼                      ▼
┌──────────────────────────────────────────────┐
│                 libpod                         │
│   ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│   │container │ │   pod    │ │   volume     │  │
│   │lifecycle │ │management│ │  management  │  │
│   └────┬─────┘ └────┬─────┘ └──────┬──────┘  │
│        │            │              │          │
│   ┌────▼────┐ ┌────▼────┐ ┌───────▼──────┐   │
│   │  conmon │ │netavark │ │containers/   │   │
│   │+ crun   │ │+ aardvark│ │storage + img │   │
│   │(OCI)    │ │(network) │ │(layers+img)  │   │
│   └─────────┘ └─────────┘ └──────────────┘   │
│   ┌─────────┐ ┌─────────┐                    │
│   │ SQLite  │ │rootless │                    │
│   │ (state) │ │  reexec │                    │
│   └─────────┘ └─────────┘                    │
└──────────────────────────────────────────────┘
```

## Rootless Mechanism

Rootless Podman is not a setuid binary and has no special privileges. It works through a multi-stage namespace-joining mechanism implemented primarily in C (`pkg/rootless/rootless_linux.c`) with a Go wrapper (`pkg/rootless/rootless_linux.go`).

### Execution Flow

1. **C constructor test** -- Before Go `init()` completes, the C constructor (line 720 of `rootless_linux.c`) tests if the process is non-root. If so, it attempts a shortcut: opening namespace handles via `set_ns_handles()` from `/proc/self` or from `$XDG_RUNTIME_DIR/libpod/tmp/ns_handles` (line 842).

2. **Join existing namespace** -- If the shortcut fails (ENOENT/EOPNOTSUPP/ENOSYS/EPERM), it falls back to reading `$XDG_RUNTIME_DIR/libpod/tmp/pause.pid` (line 871), opening `/proc/<pid>/ns/user` and `/proc/<pid>/ns/mnt`, and calling `setns(2)` to join the existing user+mount namespace.

3. **Create new namespace** -- If joining fails (no existing namespace), the Go layer calls `BecomeRootInUserNS()` (`rootless_linux.go` line 421). This creates a socket pair for sync, then calls `C.reexec_in_user_namespace()` (line 282). The C function at line 1287 does `syscall_clone(CLONE_NEWUSER | CLONE_NEWNS | SIGCHLD)` to fork a child in a new user+mount namespace. The parent returns the child PID. The child sets itself as root (`setresgid(0,0,0)`, `setresuid(0,0,0)`), saves namespace handles, creates a pause process (catatonit) if nsfs handles are unavailable (line 1416-1427), then `execvp("/proc/self/exe")` to re-execute Podman.

4. **Pause process** -- The pause process (`do_pause` at line 513) runs `catatonit -P` or spins in `pause()` with ignored signals, keeping the user namespace alive.

### UID/GID Mapping

The UID/GID mapping (`rootless_linux.go` lines 288-343) uses `newuidmap`/`newgidmap` setuid helpers which read `/etc/subuid` and `/etc/subgid` to map a range of subordinate UIDs into the namespace.

- Without mappings, a single-entry mapping `0:<hostUID> 1` is written.
- With mappings, the format is `USERNAME:START_UID:RANGE` -- e.g., `alice:200000:65536`.
- Use `usermod --add-subuids 200000-201000 --add-subgids 200000-201000 $USER` to set up.
- On cgroups v2, the pause process gets moved into its own systemd scope via `MovePauseProcessToScope()`.

### Storage Path Redirection

Rootless redirects storage paths to avoid requiring `/var`:

| Path | Rootful | Rootless |
|------|---------|----------|
| graphroot | `/var/lib/containers/storage` | `$XDG_DATA_HOME/containers/storage` |
| runroot | `/run/containers/storage` | `$XDG_RUNTIME_DIR/containers` |

### Rootless Networking

The default rootless networking tool is **pasta** (from the passt project), replacing the removed slirp4netns (Podman 5.0+). Pasta copies the host's IP addresses into the container namespace without NAT.

### Rootless Constraints

- Cannot bind ports < 1024 (configurable via `net.ipv4.ip_unprivileged_port_start` sysctl).
- No cgroups v1 resource limits.
- NFS homedir incompatibility.
- Overlayfs requires kernel >= 5.12 or `fuse-overlayfs` fallback.
- No checkpoint/restore (CRIU requires root).
- No device node creation.

### Socket Activation Preservation

Socket activation is preserved across the user namespace reexec by saving/restoring `LISTEN_PID`, `LISTEN_FDS`, and `LISTEN_FDNAMES` in `rootless_linux.c` lines 792-810.

## Container Lifecycle Flow: `podman run` End-to-End

The lifecycle of a container illustrates how all three architectural layers interact. This section traces a `podman run -d --name myapp alpine sleep 3600` command through every component.

### Phase 1: CLI Parsing

1. `cmd/podman/main.go` dispatches to `cmd/podman/containers/run.go` via Cobra command routing.
2. Cobra flags are parsed against the `run` command definition, producing a `entities.ContainerRunOptions` struct.
3. PreRunE hooks call `NewContainerEngine()` in `cmd/podman/registry/registry.go`, which creates either an ABI or Tunnel engine.

### Phase 2: Engine Factory Decision

The infra layer (`pkg/domain/infra/`) makes a connection-mode decision:

- **ABI mode** (default on Linux, `connection=""`): `infra.NewContainerEngine()` calls `NewLibpodRuntime()` which calls `makeRuntime()` in `runtime_libpod.go`. This initializes the full libpod `Runtime` struct (`libpod/runtime.go`) -- storage, state (SQLite), networking (netavark), OCI runtime (crun), and conmon path. Before returning, `makeRuntime()` calls `BecomeRootInUserNS()` to re-exec into a user namespace if running rootless.

- **Tunnel mode** (`--connection=remote`): `infra.NewContainerEngine()` creates a tunnel engine that connects to `podman system service` via a Unix socket or SSH. The REST API server runs inside the service process, which uses the ABI engine on the server side.

### Phase 3: Container Creation via ABI Engine

`ABIContainerEngine.Run()` (`pkg/domain/infra/abi/containers_run.go`):

1. Calls `pkg/specgenutil/specgen.go` to build a `SpecGenerator` from CLI options -- image, command, env, volumes, port mappings, capabilities, etc.
2. Calls `pkg/specgen/generate/container.go:CreateContainer()`:
   a. Pulls or finds the image via the libimage runtime (`libpod/container_create.go:pullOrFindImage()`).
   b. Creates the rootfs from the image via `storageService.CreateContainer()`.
   c. Creates the OCI spec (`config.json`) via `libpod/container_internal_common.go:generateSpec()` -- mounts the rootfs, applies volumes, sets environment, configures capabilities/seccomp, generates resolv.conf/hosts.
   d. Generates the container's SELinux label via `libpod/labels.go`.
   e. Creates the container in the SQLite state database via `s.state.CreateContainer(ctr)`.
3. Returns an `*libpod.Container` with the new container object.

### Phase 4: Container Start via Conmon

`ABIContainerEngine.Start()` calls `Container.Start()`, which delegates to the OCI runtime through the ConmonOCIRuntime wrapper (`libpod/oci_conmon_common.go`):

1. `ConmonOCIRuntime.CreateContainer()` (`oci_conmon_common.go:182`) -- for rootless, calls `createRootlessContainer()`:
   - Creates a bundle directory at `$XDG_RUNTIME_DIR/libpod/tmp/`.
   - Writes the OCI config.json and a conmon configuration JSON (`config.json` in the bundle).
   - For rootless: may need to re-exec into the correct user namespace context.
   - Executes `conmon --bundle <path> --cid <cid> --cuuid <uuid> --runtime <crun path> --exit-dir <path> --log-level debug`.
2. Conmon creates a child process in a new cgroup via `fork()`. The child calls `crun create <cid>`.
3. `crun create` reads the bundle's `config.json`, sets up the rootfs, and creates the container's cgroups, namespaces, and mounts. It then pauses the container process.
4. Conmon monitors the container's I/O (stdin/stdout/stderr via pty or pipes), relays signals, and writes exit status to the exit-dir.

### Phase 5: Container Start (Running)

`Container.Start()` continues:

1. `ConmonOCIRuntime.StartContainer()` (line 194) calls `crun start <cid>`.
2. Crun applies any configured seccomp, drops capabilities to the specified set, and calls `execve()` for the container's `Entrypoint`/`Cmd`.
3. The container process begins running. Conmon waits for it and captures exit code.
4. The pause process (`pause.pid` read at line 360 of `rootless_linux.go`) holds the user namespace alive.
5. If `Notify=healthy` is set in Quadlet, the systemd unit waits for Podman's healthcheck system to signal `READY=1`.

### Phase 6: Networking Setup

If the container has networking (`CreateNetNS=true`):

1. `libpod/networking_linux.go:configureNetNS()` creates a new network namespace.
2. For rootless with pasta: `setupPasta()` (line 36) delegates to `pkg/network/pasta/pasta.go`, which forks a `pasta` process. Pasta copies the host's IP addresses and sets up forwarding via `pesto` binary if `pasta` is configured as the rootless port forwarder.
3. For bridge networking: Netavark (`libpod/networking_linux.go` line 131) creates a veth pair, sets IP addresses, applies firewall rules, and registers DNS records with aardvark-dns.
4. For rootless bridge with port forwarding: `startRootlessPortForwarding()` spawns the rootlessport process, which re-execs into a child network namespace for userspace port forwarding.

### Phase 7: Event Emission

The container lifecycle emits structured events through the libpod event system (`libpod/events.go`):

- `Init`, `Start`, `Stop`, `Died`, `HealthStatus` -- consumed by `podman events`, journald, or file-based eventers.
- Image events are forwarded from `libimage.Runtime` via `libimageEvents()` (`runtime.go:756`), which spawns a goroutine to translate libimage events to libpod events.

### Summary: Key Source Files in the Lifecycle

| Phase | File | Role |
|-------|------|------|
| CLI | `cmd/podman/containers/run.go` | Command parsing, flag handling |
| Engine | `pkg/domain/infra/abi/containers_run.go` | ABI engine run implementation |
| Create | `libpod/container_create.go` | Container creation (image, rootfs, spec) |
| Create | `libpod/container_internal_common.go` | OCI spec generation |
| State | `libpod/sqlite_state.go` | Persistent container state (SQLite) |
| OCI | `libpod/oci_conmon_common.go` | Conmon wrapper for OCI runtime |
| OCI | `conmon` (external) | Container monitor process |
| OCI | `crun` (external) | OCI runtime (namespace + cgroup setup) |
| Network | `libpod/networking_linux.go` | Rootless/bridge networking setup |
| Events | `libpod/events.go` | Event emission and forwarding |

## Quadlet Architecture

Quadlet is a **systemd generator** (documented in `podman-systemd.unit.5.md`) that translates Podman configuration files into systemd service units at boot or `daemon-reload` time.

### Supported File Types

Seven file types are supported, plus `.artifact`:

| File Type | Generated Service Type | Purpose |
|-----------|----------------------|---------|
| `.container` | `Type=notify` | `podman run` |
| `.kube` | `Type=notify` | `podman kube play` |
| `.pod` | `Type=forking` | `podman pod create` |
| `.volume` | `Type=oneshot` | `podman volume create` |
| `.network` | `Type=oneshot` | `podman network create` |
| `.build` | `Type=oneshot` | `podman build` |
| `.image` | `Type=oneshot` | `podman image pull` |

Each file type has a custom section (e.g., `[Container]`, `[Pod]`, `[Kube]`) that maps directly to podman CLI options.

### Search Paths

**Rootful (system):**
1. `/run/containers/systemd/` -- temporary/testing (highest precedence)
2. `/etc/containers/systemd/` -- system administrator
3. `/usr/share/containers/systemd/` -- distribution (lowest precedence)

**Rootless (user):**
1. `$XDG_RUNTIME_DIR/containers/systemd/`
2. `$XDG_CONFIG_HOME/containers/systemd/` or `~/.config/containers/systemd/`
3. `/etc/containers/systemd/users/${UID}/`
4. `/etc/containers/systemd/users/`
5. `/usr/share/containers/systemd/users/${UID}/`
6. `/usr/share/containers/systemd/users/`

### Drop-In Directories

Systemd drop-in directories are supported: `foo.container.d/*.conf` merge into `foo.container`, supporting hierarchical overrides. For example:

```
~/.config/containers/systemd/
  myapp.container
  myapp.container.d/
    10-secrets.conf        # Secret references (never committed)
    20-local-override.conf # Environment-specific overrides
```

### Generation and Dependencies

The generator binary is `/usr/lib/systemd/system-generators/podman-system-generator`. It reads all Quadlet files and creates `.service` files in the generator output directory.

Cross-unit dependencies are automatic:
- A `.container` referencing `foo.volume` gets `Wants` + `After` on `foo-volume.service`.
- A `.container` referencing `bar.network` gets `Wants` + `After` on `bar-network.service`.
- A `.container` using `Pod=baz.pod` gets dependencies on `baz-pod.service`.

### Template Units

Template files (`foo@.container`) become `foo@.service` systemd templates. Instantiate with `systemctl start foo@50.service`. The `DefaultInstance=` key in `[Install]` enables a default instance at boot.

### Install Section

The `[Install]` section supports `WantedBy`, `RequiredBy`, `Alias`, and `UpheldBy`. The generator applies the Install section itself at generation time -- `systemctl enable` will return `Unit is transient or generated`. Use `[Install] WantedBy=default.target` (rootless) or `[Install] WantedBy=multi-user.target` (rootful) to auto-start.

### Systemd Service Templates

The `contrib/systemd/` directory provides system and user templates for:
- `podman.service` / `podman.socket` -- Podman API service
- `podman-auto-update.timer` / `podman-auto-update.service` -- daily auto-update with `RandomizedDelaySec=900`

## Networking Architecture

Podman networking is built on multiple layers with distinct backends for rootful and rootless modes.

### Network Backend

The network backend (`libpod/runtime.go` line 556) uses **Netavark** (`github.com/containers/netavark`) -- a Rust-based network configuration tool that manages bridge creation, firewall rules, and NAT. DNS is handled by **aardvark-dns**, which registers each container under its name and aliases.

```
┌──────────────────────────────────────────────┐
│               Podman Container                │
├──────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌──────────┐     │
│  │ netavark │  │ aardvark│  │  pasta / │     │
│  │ (bridge  │  │  -dns   │  │ slirp4ns │     │
│  │ rootful) │  │         │  │ (rootless)│    │
│  └────┬────┘  └────┬────┘  └────┬─────┘     │
│       │            │            │            │
│       ▼            ▼            ▼            │
│  ┌────────────────────────────────────────┐  │
│  │       Linux Network Stack              │  │
│  │  veth / bridge / nat / firewall        │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### Rootful Networking

- Default bridge network named `podman` uses `10.88.0.0/16`.
- New networks pick subnets from `10.89.0.0/24` to `10.255.255.0/24`.
- Port forwarding uses iptables/nftables rules managed by netavark.
- Full IPv6 support.

### Rootless Networking

Two modes are available:

**Pasta (default since Podman 5.0):**
- Copies the host's IP addresses into the container namespace without NAT.
- Runs as a separate process.
- Supports full IPv6.
- Configuration is delegated to `common/libnetwork/pasta` via `libpod/networking_pasta_linux.go` line 14, which calls `pasta.Setup()`.

**Bridge networks via Netavark:**
- The container gets a veth pair into the bridge network.
- Port forwarding requires a userspace proxy because rootless users lack `CAP_NET_BIND_SERVICE` on the host.

### Port Forwarding for Rootless Bridge

Two methods exist:

| Method | Mechanism | Preserves Client IP? | Status |
|--------|-----------|---------------------|--------|
| rootlessport (legacy) | slirp4netns-based userspace proxy | No | Default for bridge |
| pesto via pasta | kernel-level forwarding via pesto binary | Yes | Requires `rootless_port_forwarder="pasta"` in `containers.conf` |

The `networking_linux.go` file (lines 21-78) orchestrates port forwarding: `configureNetNS()` checks if pasta mode is requested (line 36), calls `setupPasta()`, otherwise sets up bridge via netavark, then configures port forwarding based on the `rootless_port_forwarder` setting.

### Podman Machine Networking

For Podman Machine (macOS/Windows), ports are forwarded via **gvproxy**, which runs on the host and tunnels traffic to the VM via its HTTP API at `gateway.containers.internal` (`libpod/networking_machine.go` lines 22-156).

- `gvproxy` acts as a user-space network gateway.
- When a container publishes a port, `exposeMachinePorts()` (line 143) posts to gvproxy's `/services/forwarder/expose` endpoint.
- gvproxy binds the port on the macOS host and forwards connections to the VM.
- A Unix domain socket is used for rootlessport control signaling (`networking_rootlessport.go` line 48).

## Storage Architecture

Podman uses `containers/storage` for image and container storage.

### Storage Drivers

| Driver | Requirements | Notes |
|--------|-------------|-------|
| overlayfs | Kernel >= 5.11 (rootless), any (rootful) | Preferred; uses kernel overlay mount |
| fuse-overlayfs | fuse-overlayfs installed | Fallback for rootless on kernels < 5.12 |
| VFS | None | Slow, for testing only |

### Directory Layout

| Directory | Rootful | Rootless (default) |
|-----------|---------|-------------------|
| graphroot (images/layers) | `/var/lib/containers/storage` | `$XDG_DATA_HOME/containers/storage` |
| runroot (temp writable) | `/run/containers/storage` | `$XDG_RUNTIME_DIR/containers` |
| volumes | `$graphroot/volumes` | `$graphroot/volumes` |
| secrets | `$graphroot/secrets` | `$graphroot/secrets` |

### Initialization Flow

The `configureStore()` method (`libpod/runtime.go` lines 1004-1029):
1. Creates the `storage.Store` from `DefaultStoreOptions()`, mergeable with CLI flags.
2. Registers the store with the image transport.
3. Creates a `storageService` for rootfs creation from images.
4. Initializes `libimage.Runtime` from the same store.

### Volumes

Volumes are managed by `libpod/volume*.go` with support for:
- **local driver** -- default, stores data at `$graphroot/volumes`.
- **image driver** -- volume populated from image content.
- **Third-party volume plugins** -- looked up from `containers.conf` via `getVolumePlugin()` at `runtime.go` line 1157.

### Image Management

Images are managed via `containers/image` (`go.podman.io/image/v5`) through the `libimage` runtime (`libpod/runtime.go` line 1020). Image pulling, pushing, and layer management all go through this library.

## Security Model

Podman's security model is defense-in-depth built on Linux kernel primitives.

### Rootless as Primary Boundary

- Podman is **not a setuid binary** -- it has no special privileges.
- All containers run within a user namespace where UID 0 inside maps to the user's unprivileged UID outside.
- Containers inherit the user's limitations: cannot bind low ports, cannot create device nodes.

### Capabilities

By default, containers get a reduced set of capabilities (not full root). Configurable via:
- `DropCapability=all` -- remove all capabilities (most secure).
- `AddCapability=CAP_NET_BIND_SERVICE` -- add back only what is needed.
- In Quadlet: `[Container]` section keys.
- In CLI: `--cap-drop=all --cap-add=CAP_NET_BIND_SERVICE`.

### Seccomp

- Default seccomp profile blocks dangerous syscalls.
- Configurable via `SeccompProfile=` in Quadlet (line 414) or `--security-opt seccomp=<profile>`.

### NoNewPrivileges

- Can be set to prevent processes from gaining privileges via setuid binaries.
- In Quadlet: `NoNewPrivileges=true` in `[Container]` section.

### SELinux Support

SELinux is deeply integrated:

| Option | Purpose |
|--------|---------|
| SecurityLabelType | SELinux type for the container process |
| SecurityLabelLevel | SELinux level (MLS) |
| SecurityLabelFileType | SELinux type for container files |
| SecurityLabelDisable | Disable SELinux for this container |
| SecurityLabelNested | Allow SELinux labels inside the container |

The `:Z` flag on volume mounts relabels the host directory to match the container's SELinux context. The `:z` flag allows sharing between multiple containers. Example:

```
Volume=/host/path:/container/path:Z
```

### Secrets Encryption

Secrets are stored at `$graphroot/secrets` and managed by the `secrets.SecretsManager` (`libpod/runtime.go` line 1182). Secret drivers:
- **file** (default) -- stored as read-protected files on disk.
- **pass** -- GPG-encrypted files managed by the `pass` utility.
- **shell** -- custom scripts via `[secrets.opts]` in `containers.conf`.

### Read-Only Rootfs

- `ReadOnly=true` with `ReadOnlyTmpfs=true` makes the container rootfs immutable except for tmpfs mounts.
- `/tmp`, `/var/tmp`, and `/run` are mounted as tmpfs automatically.

## Service Mode (`podman system service`)

Podman operates in two modes: the **ephemeral CLI mode** (each command is a new process) and the **persistent service mode** (`podman system service`), which exposes the Podman REST API over a Unix or TCP socket.

### Architecture

The service mode runs the same libpod runtime but keeps it alive across requests:

1. `cmd/podman/system/service.go` starts a REST API server using the Go `net/http` package.
2. The server registers two API trees:
   - **Libpod API** (`pkg/api/handlers/libpod/`) -- Podman-specific endpoints (`/libpod/containers/json`, `/libpod/pods/create`, etc.)
   - **Compatible API** (`pkg/api/handlers/compat/`) -- Docker API-compatible endpoints (`/containers/json`, `/images/create`, etc.)
3. Each request handler converts HTTP parameters to `entities.ContainerEngine` method calls, executing against the same ABI engine used by the CLI.
4. The service uses the tunnel engine pattern in reverse: the REST API handlers call the ABI engine internally.

### Socket Activation

Podman supports systemd socket activation for the API service:

```
# contrib/systemd/podman.socket
[Socket]
ListenStream=%t/podman/podman.sock
SocketMode=0660

# contrib/systemd/podman.service
[Service]
ExecStart=/usr/bin/podman system service
Type=notify
```

With socket activation, `podman.socket` is the enabled unit. When a client connects to the socket, systemd starts `podman.service` on-demand. The service hands the socket's file descriptor to podman.

### Rootless Socket Path

- **Rootful**: `/run/podman/podman.sock` or `/run/podman/podman.sock`
- **Rootless**: `$XDG_RUNTIME_DIR/podman/podman.sock` (typically `/run/user/$UID/podman/podman.sock`)
- The rootless socket path is derived in `cmd/podman/registry/registry.go` line 99-107, which checks `rootless.IsRootless()` and sets the path accordingly.

### Connection Mode (Remote Client)

Podman can operate as a remote client connecting to a service running on a different host:

```bash
# On the server: enable the API service
systemctl --user enable --now podman.socket

# On the client: configure the connection
podman system connection add my-server \
  --identity ~/.ssh/id_ed25519 \
  ssh://user@server:22/run/user/1000/podman/podman.sock

# Use the remote connection
podman --connection my-server ps
```

The remote client uses the **tunnel engine** (`pkg/domain/infra/tunnel/`), which translates each API call to an HTTP request against the socket. The tunnel engine implements the same `ContainerEngine` and `ImageEngine` interfaces as the ABI engine, allowing the CLI to be connection-agnostic.

### Dual-Mode CLI Architecture

```
podman --connection=remote ps
  │
  ▼
cmd/podman/containers/ps.go (Cobra command)
  │
  ▼
registry.ContainerEngine() → infra.NewContainerEngine()
  │
  ├─ ABI mode (default):
  │    infra/tunnel/ is NOT compiled (build tag !remote)
  │    infra/abi/ containers_ps.go → libpod.Runtime
  │
  └─ Tunnel mode (--connection=remote or build tag remote):
       infra/tunnel/ containers_ps.go → HTTP GET /libpod/containers/json
       SSH transport or Unix socket
```

The build-tag separation (`//go:build !remote` vs `//go:build remote`) ensures the libpod library and its C dependencies are not compiled into the remote-only static binary.

## macOS Podman Machine

Podman Machine is a thin management layer that runs a Linux virtual machine on macOS or Windows to host the container runtime (containers are Linux-native).

### Architecture

```
┌─────────────────────────────────────────────────┐
│                 macOS Host                        │
│  ┌─────────────────────────┐  ┌──────────────┐  │
│  │   podman CLI (remote)   │  │   gvproxy    │  │
│  │   talks to VM via SSH   │  │ (port fwd)   │  │
│  └──────────┬──────────────┘  └──────┬───────┘  │
│             │                         │          │
└─────────────┼─────────────────────────┼──────────┘
              │ SSH tunnel              │ gvproxy tunnel
              ▼                         ▼
┌─────────────────────────────────────────────────┐
│           Linux VM (Fedora CoreOS)               │
│  ┌─────────────────────────────────────────┐    │
│  │         podman (rootful)                │    │
│  │  ┌─────┐ ┌─────┐ ┌──────┐ ┌──────┐   │    │
│  │  │ net │ │ dns │ │storage│ │conmon│   │    │
│  │  └─────┘ └─────┘ └──────┘ └──────┘   │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### VM Providers

| Provider | Technology | macOS? | Windows? |
|----------|-----------|--------|----------|
| libkrun | Lightweight KVM-based VM | Default | No |
| applehv | Apple Virtualization.framework | Alternative | No |
| qemu | Full system emulator | Yes | No |
| wsl | WSL 2 | No | Default |
| hyperv | Hyper-V | No | Alternative |

### Networking via gvproxy

`gvproxy` (`pkg/machine/gvproxy.go`) acts as a user-space network gateway:
- Runs on the macOS host.
- Accepts port-forwarding requests via JSON HTTP API at `gateway.containers.internal`.
- Binds host ports and forwards connections to the Linux VM.

### Filesystem Sharing

- macOS to Linux VM file sharing uses **virtiofs** (via `vfkit` on applehv).
- Default mount: `$HOME:$HOME` (configurable with `--volume` during `podman machine init`).

### VM Lifecycle

- VM boots from a Podman-provided Fedora-based disk image with a minimal OStree deployment.
- SSH access: `podman machine ssh`.
- Configuration stored under `$XDG_CONFIG_HOME/containers/podman/machine/`.
- Podman behaves identically on the VM side (fully rootful with full networking).

## Key Source Components

| Directory/File | Role |
|--------|------|
| `libpod/` | Core library: container lifecycle (`container*.go`), pod management (`pod*.go`), volume management (`volume*.go`), OCI runtime integration via conmon (`oci_conmon*.go`), SQLite state (`sqlite_state.go`), networking setup (`networking_linux.go`, `networking_pasta_linux.go`, `networking_rootlessport.go`), and the main Runtime struct (`runtime.go`, `runtime_*.go`) |
| `pkg/rootless/` | C (`rootless_linux.c`) and Go (`rootless_linux.go`) rootless user namespace implementation |
| `pkg/domain/infra/` | Engine factory: `runtime_abi.go` (libpod direct), `runtime_tunnel.go` (REST API client), `runtime_libpod.go` (runtime construction from CLI flags). Both produce ContainerEngine and ImageEngine implementations in `abi/` and `tunnel/` subdirectories |
| `pkg/machine/` | VM management for macOS and Windows: providers (`applehv/`, `libkrun/`, `qemu/`, `wsl/`, `hyperv/`), gvproxy integration (`gvproxy.go`), SSH (`ssh.go`), ignition-based VM provisioning |
| `contrib/systemd/` | Systemd service and socket templates for the Podman REST API, auto-update timer, kube@.service template, and clean-transient service |
| `cmd/podman/` | CLI entry point: command parsing, flag handling, dispatching to domain/infra engines |
| `pkg/specgen/` and `pkg/specgenutil/` | Container and pod spec generation: translates CLI flags into OCI-compatible container configurations |
| `libpod/define/` | Shared error types, constants, container states, info struct |
| `libpod/events/` | Event system: container lifecycle events, image events, artifact events, journald and file-backed eventers |
| `libpod/lock/` | Lock manager: SHM-based and file-based locking for container/pod/volume synchronization |
| `libpod/shutdown/` | Signal handler registry: graceful shutdown of storage on SIGTERM/SIGINT |

## Related

- [[podman]] -- Wiki entry with overview and installation
- [[podman-deployment]] -- Deployment guide with step-by-step instructions
- [[podman-quadlet-examples]] -- Production-ready Quadlet file collection
- [[podman-profile]] -- Quick-reference profile card
- [[podman.codegraph-verify]] -- Codegraph verification of architecture claims
