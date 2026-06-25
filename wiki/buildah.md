# Buildah — OCI Image Builder

| Field | Value |
|---|---|
| **Origin** | [containers/buildah](https://github.com/containers/buildah) |
| **License** | Apache 2.0 |
| **Stack** | Go, containers/storage, containers/image, OCI runc/crun |
| **Source** | `sources/buildah/` |
| **Wanted** | Daemonless OCI image builder for agent deployment pipelines — the build-time counterpart to Podman's run-time |

## What it is

Buildah is a **daemonless, rootless OCI container image builder** from the `containers` project (same org as Podman, Skopeo, CRI-O). It builds images from Dockerfiles or from scratch using scriptable primitives (`buildah from`, `buildah copy`, `buildah run`, `buildah commit`). Unlike `docker build`, there is no daemon, no buildkit, and no long-running server — just a simple fork-exec model.

Key differentiating facts from the source code (`cmd/buildah/main.go`, `imagebuildah/build.go`):

- **Daemonless fork-exec model** — `main()` calls `buildah.InitReexec()` which wraps `reexec.Init()` from containers/storage. The Go binary re-executes itself inside namespaces for rootless operation. No background process.
- **Ephemeral "build containers"** — The `Builder` struct (`buildah.go:88`) represents a container whose sole purpose is accumulating content for a new image layer. It holds references to a `storage.Store`, image metadata (both OCIv1 and Docker v2 formats), mount points, and namespace settings. These are not long-lived containers.
- **Dockerfile OR scripted builds** — Two modes coexist. The `imagebuildah` package (`imagebuildah/build.go:73` - `BuildDockerfiles()`) parses Dockerfiles using the `openshift/imagebuilder` library. The lower-level `buildah` package exposes `Builder` methods (`Add()`, `Run()`, `Commit()`) for scripted builds.
- **Two image formats** — Both OCI and Docker v2s2 manifest formats are supported. The `define` package sets default manifest type to OCIv1.
- **Podman delegates `podman build`** — Podman links against Buildah's Go API (`imagebuildah.BuildDockerfiles()`) internally. You do NOT need Buildah installed separately if Podman is installed — Podman vendors Buildah's build logic.

## Architecture Overview (from source)

The codebase has four layers:

```
CLI (cmd/buildah/)
  └── Subcommands: build, from, commit, run, push, pull, config, etc.
       │
       ▼
imagebuildah/  (Dockerfile build pipeline)
  ├── build.go          — BuildDockerfiles() entry point
  ├── executor.go       — executor struct: coordinates multi-stage builds
  └── stage_executor.go — stageExecutor: per-stage execution (Parse → Execute → Commit)
       │
       ▼
buildah/  (core library — the Builder)
  ├── buildah.go      — Builder struct (88 fields), BuilderOptions
  ├── new.go          — NewBuilder() — creates build containers from images or scratch
  ├── commit.go       — Commit() — writes container content as new image layers
  ├── run_linux.go    — Run() — executes commands inside the build container
  ├── add.go / copy.go — Add() / Copy() — injects files into containers
  └── config.go       — Config() — sets image metadata (env, cmd, labels, etc.)
       │
       ▼
containers/storage  (layer/container/image management)
containers/image    (image pulling, pushing, format conversion)
```

## How it Builds Images (the flow)

### Dockerfile-based build

1. **Entry point**: `buildah build [CONTEXT]` → `cmd/buildah/build.go` → `buildCmd()` → `imagebuildah.BuildDockerfiles()` (`imagebuildah/build.go:73`)
2. **Dockerfile parsing**: Uses `openshift/imagebuilder` library (`imagebuilder.ParseDockerfile()`) to parse the Dockerfile(s) into an AST of `parser.Node` objects. Supports `.in` suffix Dockerfiles preprocessed with `cpp`.
3. **Executor creation**: `newExecutor()` (`imagebuildah/executor.go:210`) creates an `executor` struct holding all build options, caches, stages map, and semaphore for concurrent stage execution.
4. **Stage creation**: For each multi-stage target, `startStage()` creates a `stageExecutor` that wraps an `imagebuilder.Stage`.
5. **Per-stage execution**: `stageExecutor.execute()` (`imagebuildah/stage_executor.go:1286`) processes instructions sequentially:
   - `FROM` → `ib.From()` → pulls base image or references prior stage
   - `RUN` → `stageExecutor.Run()` → `b.Run()` → chroot/OCI runtime execution
   - `COPY/ADD` → content injection via the `copier` package
   - `commit()` → `b.Commit()` → creates layer in containers/storage
6. **Layer commit**: `Builder.Commit()` (`commit.go`) takes the mounted container rootfs, diffs it against the parent layer, compresses the diff, and writes it as a new image layer. The `commit()` method in `stage_executor.go` (`stage_executor.go:2576`) handles configuration (env, labels, cmd, ports, volumes, etc.) before committing.
7. **Output**: Returns image ID and optional canonical reference.

### Scripted build (lower-level)

```
buildah from scratch            # create empty build container
buildah copy $ctr src dest      # add files
buildah run $ctr -- dnf install ...  # run commands
buildah config --entrypoint ... $ctr  # set metadata
buildah commit $ctr my-image    # create final image
```

This mirrors exactly what a Dockerfile would do, but gives script-level control — useful for CI/CD pipelines that need conditional logic.

## Rootless Image Building

Buildah runs entirely without root privileges. The mechanism from the source:

1. **`InitReexec()`** (`util.go:26`) wraps `containers/storage`'s `reexec.Init()` which re-executes the buildah binary inside a new user namespace.
2. **User namespace mapping**: `/etc/subuid` and `/etc/subgid` supply subordinate ID ranges. Inside the namespace, the unprivileged user becomes UID 0.
3. **Storage backend**: Uses `containers/storage` with `fuse-overlayfs` (or native overlay on kernels 5.11+). The storage driver runs within the user namespace.
4. **Networking**: `pasta` (default) or `slirp4netns` for rootless network during `RUN` instructions.
5. **No setuid, no daemon**: The re-exec mechanism is the only privilege escalation — no binaries with setuid bits, no running daemon.

## Relationship to Podman (critical distinction)

This is the most common point of confusion. From the README and the source:

| Aspect | Buildah | Podman |
|---|---|---|
| Primary purpose | **Build** images | **Run** containers |
| Containers | Ephemeral build containers | Long-lived application containers |
| `buildah run` vs `podman run` | Emulates Dockerfile `RUN` | Emulates `docker run` |
| Storage separation | Separate container namespace | Separate container namespace |
| API relationship | Podman calls Buildah's `imagebuildah.\`Go API for `podman build` | Uses Buildah internally |
| Can you cross-see containers? | No | No |
| Daemon | No | No (but optional REST API) |

Key quote from the README: *"Podman specializes in all of the commands and functions that help you to maintain and modify OCI images... For building container images via Dockerfiles, Podman uses Buildah's golang API and can be installed independently from Buildah."*

In practice for this knowledge system: **Buildah is the build tool, Podman is the runtime.** Agent images will typically be built with Buildah (either via `podman build` which calls Buildah, or direct `buildah bud`) and run with Podman/Quadlet.

## Build Strategies

### Dockerfile-based
- Standard `buildah build` / `buildah bud` — works with any Dockerfile
- Multi-stage builds, build args, cache mounts
- `.in` file preprocessing with `cpp` for template-driven Dockerfiles

### Scripted (programmatic)
- Full shell scripts using `buildah from`, `buildah copy`, `buildah run`, `buildah commit`
- Useful when build logic needs conditionals, loops, or external data
- Native Go API for embedding (available as `go.podman.io/buildah`)

### From scratch
- `buildah from scratch` creates an empty container
- Everything is manual — useful for minimal, security-hardened images (distroless-style)

## Key Source Files and Their Roles

| File | Role |
|---|---|
| `cmd/buildah/main.go` | CLI entry point, cobra command registration |
| `cmd/buildah/build.go` | `buildah build` subcommand |
| `cmd/buildah/from.go` | `buildah from` subcommand (creates build containers) |
| `cmd/buildah/commit.go` | `buildah commit` subcommand |
| `cmd/buildah/run.go` | `buildah run` subcommand |
| `buildah.go` | `Builder` struct definition — the core type |
| `new.go` | `NewBuilder()` — factory for build containers |
| `commit.go` | Image layer creation and commit logic |
| `run_linux.go` | Command execution inside build containers (Linux) |
| `run_common.go` | Shared RUN implementation |
| `add.go` | File addition to containers |
| `define/types.go` | Core types, version, defaults |
| `define/build.go` | `BuildOptions` struct — all build configuration |
| `imagebuildah/build.go` | `BuildDockerfiles()` — main Dockerfile build entry point |
| `imagebuildah/executor.go` | `executor` struct — orchestrates multi-stage builds |
| `imagebuildah/stage_executor.go` | `stageExecutor` — per-stage instruction execution |
| `util.go` | `InitReexec()` for rootless re-exec, utilities |

## Compatibility with Core Systems

### Hermes
- Buildah builds the container images Hermes agents run inside
- Hermes agent deployment pipeline can use `buildah build` or `podman build` interchangeably

### OpenClaw
- Same — images for OpenClaw channels/plugins can be built with Buildah
- Scripted builds suit OpenClaw's modular plugin architecture

### Agentfield
- **Primary integration point.** Agentfield deploys agents into container images. Buildah is the image builder layer.
- CI/CD pipeline pattern: `buildah build` → `buildah push` → Agentfield pulls and deploys
- Buildah's scriptable mode allows injecting per-agent configuration at build time

### n8n
- n8n images can be custom-built with Buildah to include pre-installed nodes and credentials
- Multi-stage builds for optimized n8n workflow execution images

## Deployment

Buildah fits into the agent deployment stack as follows:

```
Agent source code
       │
       ▼
  ┌───────────┐
  │  Buildah  │  ← Builds the OCI image
  └─────┬─────┘
        │
        ▼
  ┌───────────┐
  │  Podman   │  ← Runs the image (via Quadlet)
  └───────────┘
        │
        ▼
  ┌──────────────────┐
  │  Agentfield      │  ← Manages the deployed agent
  └──────────────────┘
```

Buildah runs in CI/CD (GitHub Actions, GitLab CI) or as part of a local build workflow. The resulting images are pushed to a registry and pulled by Podman on the target nodes.

## Installation Methods

- **brew** (macOS): `brew install buildah`
- **Linux packages**: Available in all major distros (`dnf install buildah`, `apt install buildah`)
- **Containerized**: `docker.io/containers/buildah` or `quay.io/buildah/stable`
- **From source**: `make buildah` (uses Go modules)

See `install.md` in the repo for full details.

## Domain docs & assets

- [Architecture](domains/architecture/buildah-architecture.md) — 4-layer architecture, image building pipeline, rootless mode
- [Deployment](domains/deployment/buildah-deployment.md) — CI/CD pipelines, rootless config, agent image build examples
- [Agent Profile](assets/agent-profiles/buildah-profile.md) — Buildah as a build-time tool, configuration reference
