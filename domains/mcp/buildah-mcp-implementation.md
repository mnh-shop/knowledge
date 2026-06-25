---
name: buildah-mcp
description: "Buildah MCP implementation analysis — no MCP server found, container build tooling only"
tags: [cli, container, documentation, mcp]
---

# Buildah -- MCP Implementation Analysis

## Overview

**Buildah** is a Go-based CLI tool for building [Open Container Initiative (OCI)](https://www.opencontainers.org/) container images. It is part of the containers ecosystem (alongside Podman, Skopeo, etc.) and lives at `github.com/containers/buildah`. Buildah provides a comprehensive Golang API for building images programmatically, plus a CLI front-end.

## MCP Implementation Status: NOT PRESENT

This repository does **not** implement the Model Context Protocol (MCP). There are:

- No `@modelcontextprotocol` imports or dependencies
- No `FastMCP`, `ServerSession`, or MCP toolkit references
- No Python MCP server implementations (the only Python in the repo is a reference to Python's `http.server` in a demo script)
- No MCP tool, resource, or prompt definitions

## What Buildah Has Instead: A gRPC-Based RPC Server

Buildah provides a **hidden** `buildah rpc` subcommand that wraps a child command with a **gRPC** server (not MCP).

### RPC Architecture

| Component | Path | Description |
|---|---|---|
| CLI command | `cmd/buildah/rpc.go` | Hidden `buildah rpc` cobra command |
| Listener | `internal/rpc/listen/listen.go` | Creates a `net.Listener` from a Unix socket path |
| Noop service | `internal/rpc/noop/noop.go` | Registers a trivial gRPC `Noop` service |
| Protobuf | `internal/rpc/noop/pb/noop.proto` | `io.buildah.v1.Noop` service definition |
| Generated code | `internal/rpc/noop/pb/noop_grpc.pb.go`, `noop.pb.go` | gRPC generated stubs |
| Test client | `tests/rpc/noop/noop.go` | Test binary that invokes the RPC server |
| Integration test | `tests/rpc.bats` | BATS test for RPC functionality |
| Test HTTP server | `tests/serve/serve.go` | Separate HTTP/CGI test server (unrelated to RPC) |

### gRPC Proto Definition (noop.proto)

```protobuf
syntax = "proto3";
package io.buildah.v1;

service Noop {
  rpc Noop(NoopRequest) returns (NoopResponse);
}

message NoopRequest {
  string ignored = 1;
}
message NoopResponse {
  string ignored = 1;
}
```

### How `buildah rpc` Works

1. The command forks/execs the user's target command with `gRPC` reflection enabled
2. Exposes a Unix socket listener (via `--listen PATH`) for gRPC clients
3. Registers a `Noop` service on the gRPC server for health checks
4. Passes environment variables (`--env NAME`) to the spawned process
5. The `--env LISTENER` flag is a special sentinel that passes the socket path as the `LISTENER` environment variable to the child process

### Command Signature

```shell
buildah rpc [-e|--env NAME] [-l|--listen PATH] command ...
```

Example test:
```shell
buildah rpc -l /tmp/buildah.sock pwd
buildah rpc --env LISTENER /usr/bin/buildah-grpcnoop --env LISTENER first-arg second-arg
```

## Complete Buildah CLI Command Catalog

| Command | File | Description |
|---|---|---|
| `buildah` (root) | `main.go` | CLI entry point, `A tool that facilitates building OCI images` |
| `buildah add` | `addcopy.go` | Add content to a container |
| `buildah build` | `build.go` | Build an image from a Containerfile/Dockerfile |
| `buildah commit` | `commit.go` | Create an image from a working container |
| `buildah config` | `config.go` | Modify image configuration |
| `buildah containers` | `containers.go` | List working containers |
| `buildah copy` | `addcopy.go` | Copy content into a container |
| `buildah dumpbolt` | `dumpbolt.go` | Dump a bolt database (debug tool) |
| `buildah from` | `from.go` | Create a working container from an image |
| `buildah images` | `images.go` | List images in local storage |
| `buildah info` | `info.go` | Display system information |
| `buildah inspect` | `inspect.go` | Inspect a container or image |
| `buildah login` | `login.go` | Login to a container registry |
| `buildah logout` | `logout.go` | Logout from a container registry |
| `buildah manifest` | `manifest.go` | Manage manifest lists (create, add, annotate, inspect, push, remove) |
| `buildah mkcw` | `mkcw.go` | Convert an image for confidential workload (krun/SEV/SNP) |
| `buildah mount` | `mount.go` | Mount a working container's root filesystem |
| `buildah prune` | `prune.go` | Cleanup intermediate images and build/mount cache |
| `buildah pull` | `pull.go` | Pull an image from a registry |
| `buildah push` | `push.go` | Push an image to a registry |
| `buildah rename` | `rename.go` | Rename a local container |
| `buildah rm` | `rm.go` | Remove one or more working containers |
| `buildah rmi` | `rmi.go` | Remove one or more images |
| `buildah rpc` (hidden) | `rpc.go` | Run a command with a gRPC RPC server |
| `buildah run` | `run.go` | Run a command within a container |
| `buildah source` | `source.go` | Manage source containers (add, create, pull, push) |
| `buildah tag` | `tag.go` | Add an additional name to a local image |
| `buildah umount` | `umount.go` | Unmount a working container's root filesystem |
| `buildah unshare` | `unshare.go` | Run a command in a modified user namespace |
| `buildah version` | `version.go` | Display version information |

## Key Internal Packages

| Package | Path | Purpose |
|---|---|---|
| `buildah` (top-level library) | `buildah/` | Core image building API |
| `define` | `define/` | Shared types and constants |
| `pkg/cli` | `pkg/cli/` | CLI helper utilities |
| `pkg/parse` | `pkg/parse/` | Input parsing (volumes, mounts, etc.) |
| `internal/config` | `internal/config/` | Docker/OCI config conversion |
| `internal/rpc/listen` | `internal/rpc/listen/` | Unix socket listener |
| `internal/rpc/noop` | `internal/rpc/noop/` | gRPC Noop service |
| `internal/mkcw` | `internal/mkcw/` | Confidential workload support |
| `internal/sbom` | `internal/sbom/` | SBOM generation presets |
| `internal/source` | `internal/source/` | Source container operations |
| `copier` | `copier/` | File copy/extraction utilities |

## Conclusion

Buildah is a container image building tool. Its only server-like capability is a **gRPC-based RPC server** (hidden `buildah rpc` command), which is unrelated to MCP. The repository does not implement the Model Context Protocol in any form. If MCP-based container management is desired, it would need to be built as a separate adapter or tool wrapping Buildah's Go API.
