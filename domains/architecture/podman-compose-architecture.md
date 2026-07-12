---
name: podman-compose-architecture
tags: [podman-compose, architecture, podman, compose, container, orchestration]
description: "Compose Spec implementation for Podman — single-file Python design, rootless daemon-less orchestration, variable substitution, volume/secret translation"
source: sources/podman-compose/
verification_date: 2026-07-12
verified_by: fixer
---

# podman-compose — Architecture

**Source:** `sources/podman-compose/`

## Overview

podman-compose is an implementation of the [Compose Spec](https://compose-spec.io/) with the Podman backend. It provides a `docker-compose`-like experience without requiring a daemon — podman is invoked directly as a subprocess via the `podman` CLI. The entire implementation is a single Python script (`podman_compose.py`, 5,266 lines) that can be dropped into `PATH`. Rootless by default, daemon-less process model, minimal dependencies (only `podman`, `python-dotenv`, `PyYAML`).

## Architecture

The architecture follows a **single-file modular design** where a central `container_to_args()` function translates Compose service definitions into `podman run` CLI arguments, orchestrated by an async `PodmanCompose` class that wraps `podman` invocations through an asyncio subprocess layer.

```
┌──────────────────────────────────────────────────────────┐
│                     CLI / Entry Point                      │
│     async_main() · main() · argparse · 22 commands         │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│                 PodmanCompose (Orchestrator)               │
│  run() · get_podman_args() · resolve_pod_name()            │
│  join_name_parts() · format_name()                         │
│  Command registration: @cmd_run · @cmd_parse                │
└──────┬──────────────────────────────────┬─────────────────┘
       │                                  │
┌──────▼──────────┐           ┌───────────▼─────────────────┐
│  container_to_args() │        │     Podman (Async CLI Wrapper) │
│  Compose → podman run │        │  output() · run() · exec()    │
│  55+ argument types   │        │  volume_ls() · network_ls()   │
│  x-podman.* extensions  │        │  asyncio.Semaphore concurrency│
└─────────────────────┘        └─────────────────────────────┘
```

### Single-File Module Layout

| Lines | Section | Role |
|-------|---------|------|
| 1–57 | Imports, version, constants | `__version__ = "1.6.0"` |
| 58–695 | Helper functions | `is_list`, `norm_as_list`, `mount_desc_to_volume_args`, etc. |
| 696–1305 | Compose-to-args translation helpers | `get_net_args`, `get_volumes_args`, `container_to_res_args` |
| 1306–1716 | **`container_to_args()`** | The central translation function — Compose service dict → `podman run` CLI |
| 1717–1794 | YAML tags | `!override`, `!reset` for compose file merging |
| 1795–2333 | **`Podman` class** | Async subprocess wrapper around the `podman` binary |
| 2334–3130 | **`PodmanCompose` class** | Main orchestrator — state, lifecycle, command dispatch |
| 3131–3176 | Command decorators | `@cmd_run`, `@cmd_parse` |
| 3177–5251 | Command implementations | 22 commands (`up`, `down`, `run`, `build`, `pull`, `ps`, `logs`, `exec`, `cp`, `config`, etc.) |
| 5252–5266 | Entry point | `async_main()` / `main()` |

### Podman-Specific Extensions (`x-podman.*`)

Beyond standard Compose Spec, podman-compose adds extensions for Podman-native features: UID/GID mapping (`x-podman.uidmaps`, `x-podman.gidmaps`), rootfs containers, SELinux relabeling, custom DNS/routes per network, interface names, `slirp4netns`/`pasta` network modes, and `glob` mount type. Global `x-podman` settings control pod behavior, naming separators, and docker-compose compatibility.

### Docker-Compose Compatibility Modes

| Setting | Effect |
|---------|--------|
| `name_separator_compat` | Use `-` separator (docker-compose) instead of `_` |
| `default_net_name_compat` | Match docker-compose default network naming |
| `default_net_behavior_compat` | Match docker-compose default net behavior |
| `docker_compose_compat` | Enable all three at once |

### Variable Substitution

Variable interpolation (`${VAR}`, `${VAR:-default}`, `${VAR:?error}`) is handled through `test_rec_subs.py` and `test_var_interpolate.py` unit tests, supporting `.env` files via `python-dotenv`.

## Key Components

| Component | Location | Role |
|-----------|----------|------|
| **`container_to_args()`** | Line 1306 | Central Compose→Podman translation (networking, volumes, env, ports, capabilities, resource limits, x-podman) |
| **`Podman` class** | Line 1795 | Async subprocess wrapper — `output()`, `run()`, `exec()`, `volume_ls()`, `network_ls()` |
| **`PodmanCompose` class** | Line 2334 | State holder, lifecycle manager, command dispatch, name generation |
| **Unit tests** | `tests/unit/` (25 files) | `test_container_to_args.py`, `test_var_interpolate.py`, `test_depends_on.py`, etc. |
| **Examples** | `examples/` | 10+ compose stacks (wordpress, hello-python, AWX, nvidia-smi) |

## Related

- [[podman-compose]] — Wiki entry with full command reference
- [[podman]] — Core Podman container engine
- [[podlet]] — Podman Quadlet generator for systemd integration
- [[podman-quadlet]] — Native Quadlet support in Podman
- [[podman-architecture]] — Podman internals deep-dive
