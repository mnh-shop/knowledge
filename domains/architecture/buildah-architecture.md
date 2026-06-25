---
name: buildah-architecture
tags: [architecture, buildah, cli, container, daemonless, docker, git, golang, image-builder, oci, podman, storage]
description: Buildah Architecture
---

# Buildah Architecture

**Source:** `sources/buildah/`
**Raw:** `raw/buildah/buildah.xml` (3.0M)
**Codegraph:** `graphs/buildah/` (9.7M)

## Overview

Buildah is a **daemonless, rootless OCI image builder** written in Go. Unlike Docker build which requires a daemon or BuildKit daemon, Buildah uses a simple fork-exec model where each invocation re-executes itself inside a user namespace for rootless operation. The codebase lives at `github.com/containers/buildah` and vendors the `containers/storage` and `containers/image` libraries for storage and image handling.

```
┌──────────────────────────────────────────────────────────┐
│                    CLI (cmd/buildah/)                     │
│  build │ from │ commit │ run │ push │ pull │ config ...  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│              imagebuildah/ (Dockerfile pipeline)           │
│  build.go → executor.go → stage_executor.go               │
│  (BuildDockerfiles → newExecutor → buildStage → execute)  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│              buildah/ (Core Builder Library)               │
│  Builder struct, NewBuilder, Commit, Run, Add, Copy       │
│  Image config management, rootless re-exec                │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│  containers/storage  │  containers/image  │  OCI runtimes  │
│  (layer/container    │  (pull/push/manifest│  (runc/crun)   │
│   management)         │   format support)  │                 │
└──────────────────────────────────────────────────────────┘
```

## CLI Entry Point (`cmd/buildah/`)

The CLI is built on `cobra` + `pflag`. The `main()` function in `cmd/buildah/main.go`:

1. Calls `buildah.InitReexec()` — if true the binary has re-executed in a user namespace and must return immediately.
2. Calls `mainInit()` for shared initialization logic.
3. Calls individual `*Init()` functions that register subcommands as cobra commands: `buildInit()`, `fromInit()`, `commitInit()`, `runInit()`, etc.
4. Executes `rootCmd.Execute()`.

Each `*Init()` function:
- Creates a `*cobra.Command` with `Use`, `Short`, `Long`, `RunE`
- Adds flags (layer flags, build flags, from/bud flags, user namespace flags, network flags)
- Registers with `rootCmd.AddCommand()`

## The Core Builder Library (`buildah/`)

### `Builder` struct (`buildah.go:88`)

The central type. A Builder represents a build container — an ephemeral container whose root filesystem is being accumulated into image layers. Key fields:

```go
type Builder struct {
    store            storage.Store        // containers/storage handle
    Type             string               // "buildah" — container type identifier
    FromImage        string               // Base image name
    FromImageID      string               // Base image ID
    Config           []byte              // Source image config
    Manifest         []byte              // Source image manifest
    Container        string              // Build container name
    ContainerID      string              // Build container ID
    MountPoint       string              // Mounted rootfs location
    OCIv1            v1.Image           // OCI image config
    Docker           docker.V2Image     // Docker image config
    ImageAnnotations map[string]string  // Image annotations
    Isolation        define.Isolation   // CHROOT, OCI, or ROOTLESS
    NamespaceOptions define.NamespaceOptions
    Capabilities     []string           // For RUN commands
    Format           string             // OCI or Docker format
    ContentDigester  CompositeDigester  // Tracks added content digests
    TopLayer         string             // Current top layer ID
    // ... plus PrependedEmptyLayers, AppendedEmptyLayers, LinkedLayers
}
```

### Builder lifecycle

1. **`NewBuilder()`** (`new.go`) — creates a Builder from an image reference or "scratch". Pulls the base image, creates a container in containers/storage, mounts the rootfs.
2. **Content operations** — `Add()`, `Copy()`, `Run()`, `Config()` modify the container's rootfs and metadata.
3. **`Commit()`** (`commit.go`) — Creates an image from the Builder's current state. Diffs the current rootfs against the parent layer, compresses, and stores as a new layer in containers/storage.

### Rootless re-execution (`util.go`, `run_linux.go`)

The `InitReexec()` function wraps `containers/storage/pkg/reexec.Init()`. On Linux:

1. If not already in a user namespace, the binary re-executes itself with `CLONE_NEWUSER` flags.
2. Maps host UID/GID to root inside the namespace using `/etc/subuid` and `/etc/subgid`.
3. Inside the namespace, the process has full root capability for storage and runtime operations.
4. `Run()` (`run_linux.go:67+`) uses either `chroot` (fast path for RUN instructions) or an OCI runtime (runc/crun) for full isolation.

## The Dockerfile Build Pipeline (`imagebuildah/`)

### Entry Point: `BuildDockerfiles()` (`imagebuildah/build.go:73`)

```
BuildDockerfiles(ctx, store, options, containerFiles...)
    → parse Dockerfiles (supports URLs, .in preprocessing)
    → for each target platform (--platform / --all-platforms):
        → buildDockerfilesOnce()
            → imagebuilder.ParseDockerfile() — parse to AST
            → newExecutor() — create executor with all options
            → imagebuilder.NewBuilder() — create imagebuilder builder
            → imagebuilder.NewStages() — create multi-stage stages
            → exec.Build(ctx, stages) — execute all stages
    → if manifest list: aggregate instances into manifest
    → return image ID and canonical reference
```

### Executor (`imagebuildah/executor.go:77`)

The `executor` struct is the central coordinator. It holds:

- Build-wide settings (compression, output format, caching, pull policy)
- Maps for `stages`, `imageMap`, `containerMap`, `baseMap`
- A semaphore for controlled concurrent stage execution
- Cache configuration (`cacheFrom`, `cacheTo`, `cacheTTL`)
- Platform-specific settings (architecture, OS, variant)

`executor.Build()` (`imagebuildah/executor.go`) iterates through stages:
- Calls `buildStage()` for each stage
- Handles `--after` dependencies (wait for prior stages)
- Manages cleanup of intermediate containers
- Tracks stage image IDs for multi-stage references

### Stage Executor (`imagebuildah/stage_executor.go`)

The `stageExecutor` handles one build stage. Its `execute()` method processes each Dockerfile instruction sequentially:

1. **`FROM`** — Pulls base image, runs `ib.From()` which calls `NewBuilder()` to create a Builder.
2. **`RUN`** — Calls `stageExecutor.Run()` → `b.Run()` → either chroot-based or OCI-runtime execution.
3. **`COPY/ADD`** — Calls `b.Add()` / `b.Copy()` to inject files via the `copier` package.
4. **`ENV`, `LABEL`, `CMD`, `ENTRYPOINT`, etc.** — Calls corresponding `b.Set*()` / `b.Config()` methods.
5. **`commit()`** — Calls `b.Commit()` to create a layer from the current state.

### `commit()` method (`stage_executor.go:2576`)

This is the most important function for understanding how layers are created:

1. Resolves output name to an image reference.
2. Transfers all config from the `imagebuilder.Builder` to the `buildah.Builder`:
   - Author, created-by, hostname, domainname
   - Architecture, OS, OS version, OS features
   - User, ports, env, cmd, volumes, onbuild, workdir, entrypoint, shell, stop-signal
   - Healthcheck, labels (including identity label and layer labels)
   - Annotations (for final instructions)
3. Builds `buildah.CommitOptions` with compression, signing, history, timestamp settings.
4. Calls `b.Commit(ctx, imageRef, options)` which does the actual layer creation.

## Storage and Caching

### containers/storage integration

Buildah uses `containers/storage` as its backing store for:
- **Images**: Stored as layers with metadata (manifest + config).
- **Containers**: Each Builder maps to one container in storage with a mounted rootfs.
- **Layers**: Copy-on-write filesystem layers using overlayfs (native) or fuse-overlayfs (rootless).

Key storage operations from the source:
- `getStore(cmd)` in `cmd/buildah/common.go` — initializes the storage.Store from config
- `store.Shutdown(false)` — cleanly shuts down the store on exit
- Layer creation happens inside `Builder.Commit()` → `store.CreateLayer()` / `store.CreateImage()`

### Build Caching

Buildah supports layer caching via `--cache-from` and `--cache-to`:
- `CacheFrom []reference.Named` — external repositories to check for cached layers
- `CacheTo []reference.Named` — external repositories to push cached layers
- `CacheTTL time.Duration` — cache entry expiry
- Internal cache: `imageInfoCache` map stores image type, history, and diff IDs for cache lookups

Caching works by comparing layer digests and history entries. When `--layers` is enabled, Buildah checks if each instruction's result matches a previously built layer.

### Multi-stage Builds

Multi-stage builds are handled through the stages map in the executor:
```go
type executor struct {
    stages    map[string]*stageExecutor   // all stages
    imageMap  map[string]string           // stage name → image ID
    baseMap   map[string]struct{}         // base image names
}
```

Stage `i` can reference stage `j`'s image as its base via `COPY --from=stage_j`. The executor tracks which stages depend on others and runs independent stages concurrently via a semaphore.

## Rootless Mode Specifics

From the source code analysis:

1. **User namespace re-execution**: `InitReexec()` (`util.go:26`) → `reexec.Init()` → `BecomeRootInUserNS()` in containers/storage. The process re-executes itself, entering a new user+mount namespace.

2. **ID mapping**: `IDMappingOptions` field in both `Builder` and `BuilderOptions` controls UID/GID mapping. The `define.IDMappingOptions` struct (`define/types.go:97`) has:
   ```go
   type IDMappingOptions struct {
       HostUIDMapping bool
       HostGIDMapping bool
       UIDMap         []specs.LinuxIDMapping
       GIDMap         []specs.LinuxIDMapping
   }
   ```

3. **Storage driver**: Rootless mode uses `fuse-overlayfs` on kernels before 5.11, or native overlay on 5.11+. The storage configuration comes from `containers/storage`'s `storage.conf`.

4. **Networking for RUN**: `pasta` (default) or `slirp4netns` provides network access inside the build container during `RUN` instructions. The `executor.configureNetwork` field controls network policy.

5. **Runtime for RUN**: Buildah supports multiple isolation modes:
   - `define.IsolationDefault` — auto-select
   - `define.IsolationOCI` — uses OCI runtime (runc/crun)
   - `define.IsolationChroot` — direct chroot (fast, no runtime overhead)
   - `define.IsolationRootless` — chroot in a user namespace

## Image Format Support

Buildah produces images in two formats, controlled by `Builder.Format`:

| Format | Manifest MIME | Default? |
|---|---|---|
| **OCI** (`define.OCI`) | `application/vnd.oci.image.manifest.v1+json` | Yes |
| **Docker** (`define.DOCKER`) | `application/vnd.docker.distribution.manifest.v2+json` | No |

The `Builder` struct stores **both** formats simultaneously:
- `Builder.OCIv1 v1.Image` — OCI image config
- `Builder.Docker docker.V2Image` — Docker v2 image config

At commit time, `Builder.Format` determines which gets used for the final image. The `PreferredManifestType` in `CommitOptions` can override this.

## The Buildah API that Podman Consumes

Podman's `podman build` command calls `imagebuildah.BuildDockerfiles()` directly via the vendored Go API. Key insight from the source:

- The entire `imagebuildah` package, the `buildah.Builder` type, and all `buildah.*` functions are importable as `go.podman.io/buildah` (the Go module path).
- Podman imports this as a dependency — no subprocess or RPC boundary.
- This means any fixes or features in Buildah automatically flow into Podman when Podman updates its vendored dependency.

## Comparison: Buildah vs Alternatives

| Aspect | Buildah | Docker build | Kaniko | img |
|---|---|---|---|---|
| **Daemon** | None (fork-exec) | Docker daemon | None | None |
| **Rootless** | Native via user namespaces | Via rootless Docker | -- | Yes |
| **Dockerfile support** | Full (via openshift/imagebuilder) | Full (buildkit) | Full | Partial |
| **Scripted builds** | Native (buildah CLI primitives) | No | No | No |
| **Multi-arch build** | Yes (--platform, --all-platforms) | Yes (buildx) | -- | No |
| **OCI format** | Yes (default) | Yes | Yes | Yes |
| **Build caching** | Layer-based + external cache repos | BuildKit cache | Cache registry | -- |
| **Podman integration** | Vendored API | No | No | No |
| **Performance** | Fast (chroot for RUN) | Moderate (buildkit DAG) | Moderate (in-cluster) | Fast |

## Key Dependencies

From `go.mod`:
- `go.podman.io/storage` — container/image/container storage backend
- `go.podman.io/image/v5` — image handling (pull, push, manifest, format conversion)
- `go.podman.io/common` — shared libnetwork, libimage, config
- `github.com/openshift/imagebuilder` — Dockerfile parsing and instruction processing
- `github.com/opencontainers/image-spec` — OCI image spec types
- `github.com/spf13/cobra` — CLI framework

## Related

- [[buildah]] — Wiki overview, feature comparison, relationship to Podman
- [[buildah-deployment]] — Installation, CI/CD pipelines, rootless configuration
- [[buildah-profile]] — Agent profile, configuration reference, command cheatsheet
