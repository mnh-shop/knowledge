---
name: podlet
tags: [cli, container, docker, podlet, podman, quadlet, security, systemd, wiki, rust]
description: "Generate Podman Quadlet files from container images"
source: sources/podlet/
---

# Podlet

| Field | Value |
|-------|-------|
| Origin | <https://github.com/containers/podlet> |
| License | Apache 2.0 |
| Stack | Rust |
| Source | `sources/podlet/` |
| Wanted | Critical dev tool for converting ad-hoc container commands to persistent systemd-managed Quadlet services |

## Overview

Podlet generates Podman Quadlet files (systemd-like `.container`, `.pod`, `.kube`, `.volume`, `.network`, `.build`, `.image`, `.artifact` unit files) from a `podman run` command, a Docker Compose file, or an existing running container/pod/network/volume/image. It is the bridge between ad-hoc container invocations and the declarative, systemd-integrated world of Quadlet.

For our agent deployment stack, Podlet is the primary tool for converting development `podman run` invocations into production-ready Quadlet unit files that live in `/etc/containers/systemd/` or `~/.config/containers/systemd/`. Every service in our architecture that currently runs via manual `podman run` commands should be converted through Podlet into Quadlet files.

## Supported Inputs and Quadlet Output Types

| Input | Output Quadlet Type(s) |
|-------|----------------------|
| `podman run ...` | `.container` + optional `.volume`, `.network`, `.build`, `.image`, `.kube` |
| `podlet podman pod create ...` | `.pod` (+ contained containers as `.container`) |
| `podlet podman kube play ...` | `.kube` |
| `podlet podman network create ...` | `.network` |
| `podlet podman volume create ...` | `.volume` |
| `podlet podman build ...` | `.build` |
| `podlet podman image pull ...` | `.image` |
| `podlet podman artifact pull ...` | `.artifact` |
| `podlet compose file.yaml` | Generated `.container`, `.pod`, `.kube`, `.volume`, `.network` files per compose service/network/volume |
| `podlet compose --kube file.yaml` | `.kube` + Kubernetes YAML for a single pod |
| `podlet compose --pod file.yaml` | `.pod` + `.container` per service linked into a pod |
| `podlet generate container <name>` | `.container` (from `podman container inspect`) |
| `podlet generate pod <name>` | `.pod` + `.container` per non-infra container (from `podman pod inspect`) |
| `podlet generate network <name>` | `.network` (from `podman network inspect`) |
| `podlet generate volume <name>` | `.volume` (from `podman volume inspect`) |
| `podlet generate image <name>` | `.image` (from `podman image inspect`) |

## Output Modes

1. **stdout** (default): Prints the combined `.quadlets` format to stdout. Best for quick inspection.
2. **`--file [path]`**: Writes individual Quadlet files to the given directory (or cwd if no path). Each resource type gets its own extension (`.container`, `.volume`, etc.).
3. **`--unit-directory`** (`-u`): Writes directly to the Podman Quadlet unit directory:
   - Root: `/etc/containers/systemd/`
   - User: `$XDG_CONFIG_HOME/containers/systemd/` (typically `~/.config/containers/systemd/`)
4. **`--quadlets-file <name>`**: Writes a single `.quadlets` file containing all sections concatenated into one file. Useful for distributing complete stacks.

## Key Features

- **CLI-to-Quadlet mapping**: Every `podman run` flag is mapped to the corresponding Quadlet key. Flags without a direct Quadlet equivalent are placed into `PodmanArgs=` for passthrough.
- **Compose file conversion**: Full support for converting Docker Compose files into multiple Quadlet files. Supports `--pod` (creates a `.pod` unit linking all containers) and `--kube` (creates a Kubernetes YAML + `.kube` unit) variants.
- **Generate from existing objects**: Reverse-engineers running containers, pods, networks, volumes, and images back into Quadlet definitions via `podman {resource} inspect`.
- **Version downgrade**: `--podman-version` flag allows generating Quadlet files compatible with older Podman versions, downgrading features that were added later.
- **Service conflict detection**: On Unix, checks systemd DBus for existing unit files that would conflict with generated files.
- **Option joining**: By default, multi-value Quadlet options (like `Environment=`, `Label=`) are joined into single lines. `-s` / `--split-options` controls which options to split onto separate lines.
- **Host path resolution**: `--absolute-host-paths` resolves relative host paths relative to a specified directory.

## Architecture

Podlet follows a linear conversion pipeline:

```
Input (CLI args / compose file / existing object)
    -> Parse (clap-based arg parser or compose_spec deserialization)
    -> Map (map parsed fields to Quadlet struct fields)
    -> Serialize (custom serde serializer to Quadlet INI format)
    -> Output (stdout / file / unit-directory / .quadlets file)
```

**Key insight**: The mapping phase is the core of the tool. Podlet's CLI structs (`src/cli/container/quadlet.rs`) define every Quadlet key as a clap argument with a doc comment documenting the exact Quadlet key it maps to. The `From` trait implementations in `src/cli/container.rs` then convert these CLI structs into Quadlet domain structs (`src/quadlet/container.rs`). Flags without native Quadlet keys are accumulated into `PodmanArgs=` via `podman_args_push_str`.

## Source Files and Roles

| File | Role |
|------|------|
| `src/main.rs` | Entry point: calls `Cli::parse().print_or_write_files()` |
| `src/cli.rs` | Main CLI struct (`Cli`), output modes, file writing, service conflict check |
| `src/cli/container.rs` | Container-specific CLI struct, `TryFrom<compose_spec::Service>`, `From` for `quadlet::Container` |
| `src/cli/container/quadlet.rs` | All Quadlet container key definitions as clap args (~80+ options) |
| `src/cli/container/podman.rs` | Podman passthrough args converted to `PodmanArgs=` |
| `src/cli/container/compose.rs` | Compose service extraction: supported/unsupported option tracking |
| `src/cli/container/security_opt.rs` | Security option parsing (maps `--security-opt` to Quadlet keys or PodmanArgs) |
| `src/cli/compose.rs` | Compose file reading, validation, conversion into File vectors |
| `src/cli/generate.rs` | `podlet generate` subcommand: inspect running objects, parse create commands |
| `src/cli/k8s.rs` | Kubernetes YAML generation from compose files (Pod + PVCs) |
| `src/cli/k8s/service.rs` | Compose service to Kubernetes container/volume mapping |
| `src/cli/kube.rs` | `podlet kube play` CLI args |
| `src/cli/network.rs` | `podlet network create` CLI args |
| `src/cli/volume.rs` | `podlet volume create` CLI args |
| `src/cli/pod.rs` | `podlet pod create` CLI args |
| `src/cli/build.rs` | `podlet build` CLI args |
| `src/cli/image.rs` | `podlet image pull` CLI args |
| `src/cli/artifact.rs` | `podlet artifact pull` CLI args |
| `src/quadlet.rs` | Core Quadlet types: `File`, `Resource` enum (8 variants), `JoinOption` |
| `src/quadlet/container.rs` | `[Container]` section struct, downgrade logic for all Podman versions |
| `src/quadlet/container/mount.rs` | Mount type parsing (bind, volume, tmpfs, devpts, image, ramfs, glob, artifact) |
| `src/quadlet/container/volume.rs` | Volume type in `--volume` flag (source, container_path, options) |
| `src/quadlet/container/device.rs` | Device type for `--device` flag |
| `src/quadlet/container/rootfs.rs` | Rootfs type for `--rootfs` flag |
| `src/quadlet/pod.rs` | `[Pod]` section struct |
| `src/quadlet/kube.rs` | `[Kube]` section struct |
| `src/quadlet/network.rs` | `[Network]` section struct |
| `src/quadlet/volume.rs` | `[Volume]` section struct |
| `src/quadlet/build.rs` | `[Build]` section struct |
| `src/quadlet/image.rs` | `[Image]` section struct |
| `src/quadlet/artifact.rs` | `[Artifact]` section struct |
| `src/quadlet/unit.rs` | `[Unit]` section (Description, Documentation, Wants, etc.) |
| `src/quadlet/service.rs` | `[Service]` section (Restart policy) |
| `src/quadlet/install.rs` | `[Install]` section (WantedBy) |
| `src/quadlet/globals.rs` | Global Podman options (event logger, root, etc.) |
| `src/serde/quadlet.rs` | Custom serde serializer that writes Quadlet INI format (`Section\nKey=Value`) |
| `src/serde/args.rs` | Serializer for Podman CLI args (`--key value` format) |
| `src/escape.rs` | Shell escaping utilities for joining command parts into `Exec=` |

## Compatibility with Our Stack

Podlet is a critical development tool for our agent deployment workflow. Every Quadlet file in our architecture (OpenClaw ACP services, Hermes agent services, Hermes workspace, etc.) should be generated or refined using Podlet. The typical workflow:

1. Prototype with `podman run` commands
2. Pipe through `podlet podman run <args>` to see Quadlet output
3. Write to `--unit-directory` for immediate systemd integration
4. Add systemd drop-ins, secrets, and environment overrides alongside generated files

The `podlet compose` command is particularly valuable for converting our Compose-based multi-container stacks (e.g., Hermes + database + backup sidecars) into persistent Quadlet units with proper dependencies.

## Cargo.toml Key Dependencies

- **clap**: Argument parsing (derive-based, with custom value parsers)
- **compose_spec**: Docker Compose file deserialization (from the podlet-compose fork)
- **serde** / **serde_yaml**: Serialization framework and YAML output
- **k8s-openapi**: Kubernetes Pod and PersistentVolumeClaim types
- **zbus**: D-Bus communication with systemd for service conflict detection
- **color-eyre**: Error handling and reporting

## Related

- [Architecture](domains/architecture/podlet-architecture.md) — Conversion pipeline, 27+ flag-to-Quadlet key mappings, compose conversion, serde serializer
- [Deployment](domains/deployment/podlet-deployment.md) — Installation, 6 usage patterns, best practices
- [Quadlet Examples](assets/deployment/podlet-quadlet-examples.md) — 5 concrete conversion examples (OpenClaw, Hermes stack, generate from objects)

## Related

- [[podlet-architecture]] -- Conversion pipeline and flag-to-Quadlet mapping
- [[podlet-deployment]] -- Installation, usage patterns, and best practices
- [[podlet-quadlet-examples]] -- Concrete conversion examples for OpenClaw and Hermes stacks

## Cross-project

- [[podman]] -- Podman Quadlet files Podlet generates
- [[tank-os]] -- Quadlet files for bootc OS deployment
- [[hermes-agent]] -- Quadlet files for Hermes agent deployment
- [[openclaw]] -- Quadlet files for OpenClaw agent deployment
- [[agentfield]] -- Quadlet files for AgentField control plane
- [[nix-podman-stacks]] -- Alternative Nix approach to Quadlet management
