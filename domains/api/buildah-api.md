---
name: buildah-api
description: "Buildah API surface — REST API, CLI commands, Go bindings, image building operations"
source: sources/buildah/
tags: [buildah, api, container, oci]
---

# Buildah — API Reference

Buildah provides multiple API surfaces for building OCI-compliant container images: a CLI tool, Go library bindings, and a newer experimental REST API server. The primary interface is the CLI; the Go library is used by tools like Podman for image building.

## Key API Facts

| Feature | Detail |
|---------|--------|
| **Primary surface** | CLI (`buildah`) |
| **Go library** | `github.com/containers/buildah/pkg/cli`, `pkg/` modules |
| **REST API** | Experimental — `buildah api` (not yet equivalent to CLI) |
| **Image format** | OCI (default) + Docker v2s2 |
| **Build engine** | coreos/containers — uses containers/storage for layer caching |
| **Client library** | `github.com/containers/buildah` (Go module) |
| **Container runtime** | containers/common — runtime configuration via `containers.conf` |

## CLI Command Surface

Buildah's CLI is the primary API. All operations are available as subcommands:

| Command | Description |
|---------|-------------|
| `buildah add` | Add content from host/URL to image |
| `buildah bud` | Build-using-Dockerfile (Drop-in replacement for `docker build`) |
| `buildah commit` | Write working container to image |
| `buildah config` | Update image config (env, entrypoint, labels, etc.) |
| `buildah copy` | Copy files from host/URL into container |
| `buildah from` | Create working container from base image |
| `buildah inspect` | Inspect container or image configuration |
| `buildah login/logout` | Registry authentication |
| `buildah pull` | Pull image from registry |
| `buildah push` | Push image to registry |
| `buildah rm` | Remove working containers |
| `buildah rmi` | Remove images |
| `buildah run` | Run command in container during build |
| `buildah tag` | Tag an image |
| `buildah manifest` | Multi-architecture manifest list management |
| `buildah unshare` | Run command in user namespace |
| `buildah version` | Show version info |

## Go Library API

The `github.com/containers/buildah` module exports key types and functions:

| Package | Purpose |
|---------|---------|
| `buildah` | Core types: `Builder`, `BuildOptions`, `CommitOptions`, `PullOptions` |
| `pkg/cli` | CLI command wiring and flag parsing |
| `pkg/parse` | Parse image references, volumes, and build args |
| `pkg/util` | Utility helpers for build operations |

Key types:
- **`Builder`** — Represents a working container; methods: `Run()`, `Mount()`, `Commit()`, `Copy()`, `Add()`, `Config()`
- **`BuildOptions`** — Struct passed to `BuildDockerfiles()` / `Build()` with flags similar to `buildah bud`

## REST API (Experimental)

Buildah includes an experimental REST API server started via `buildah api`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1.0/ping` | GET | Health check |
| `/v1.0/images` | GET | List local images |
| `/v1.0/images/{name}` | GET | Inspect image |
| `/v1.0/images/{name}/push` | POST | Push image to registry |
| `/v1.0/containers` | GET | List working containers |
| `/v1.0/containers/{name}` | GET | Inspect container |
| `/v1.0/containers/{name}/commit` | POST | Commit container to image |

The REST API is limited compared to the CLI/Go library. Most automated usage integrates Buildah via the Go library or shelling out to the CLI.

## Authentication

- **Registry auth**: `buildah login` / `buildah logout` (stores credentials in `~/.config/containers/auth.json`)
- **Config files**: `~/.containers` or `${XDG_CONFIG_HOME}/containers/` — shared with Podman
- **CNCF distribution/auth**: Supports credential helpers (Docker-credential-*)

## Usage

```bash
# Build an image from a Dockerfile (drop-in for docker build)
buildah bud -t myapp:latest .

# Create a container and modify it layer by layer
buildah from alpine:latest
buildah run alpine-working-container -- apk add curl
buildah commit alpine-working-container myapp:latest
```

## Related

- [[buildah]] — Source repository and wiki
- [[podman-api]] — Compatible registry auth and image handling
- [[podlet]] — Quadlet generator (uses containers/image library)
- [[bootc]] — Bootable container images (uses Buildah for builds)
