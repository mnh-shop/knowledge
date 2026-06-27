---
name: podman-compose
description: "Podman-compose — docker-compose compatible orchestration for Podman, daemon-less rootless containers"
source: sources/podman-compose/
tags: [cli, container, docker, git, orchestration, podman, python]
---

# podman-compose

**Repository:** containers/podman-compose -- <https://github.com/containers/podman-compose>

An implementation of the [Compose Spec](https://compose-spec.io/) with the [Podman](https://podman.io/) backend. Provides a `docker-compose`-like experience without requiring a daemon -- podman is invoked directly as a subprocess.

---

## Philosophy

- **Rootless by default:** containers run without root privileges.
- **Daemon-less process model:** directly execs `podman` subprocesses; no persistent daemon.
- **Single-file deployment:** everything lives in one Python script (`podman_compose.py`, 5266 lines) that can be dropped into `PATH`.
- **Minimal dependencies:** requires only `podman`, `python-dotenv`, and `PyYAML`.

---

## Architecture

### Single-file design

The entire implementation is a single Python module (`podman_compose.py`) broken into logical sections:

| Lines | Content |
|---|---|
| 1-57 | Imports, version (`__version__ = "1.6.0"`), constants |
| 58-695 | Helper functions (`is_list`, `filteri`, `norm_as_list`, `ulimit_to_ulimit_args`, `mount_desc_to_volume_args`, etc.) |
| 696-1305 | Container-to-args translation helpers (`get_net_args`, `get_volumes_args`, `container_to_res_args`, etc.) |
| 1306-1716 | **`container_to_args()`** -- the central function that converts a compose service definition into `podman run` CLI arguments |
| 1717-1794 | YAML tags (`!override`, `!reset`) |
| 1795-2333 | **`Podman` class** -- async wrapper around the podman CLI |
| 2334-3130 | **`PodmanCompose` class** -- the main orchestrator |
| 3131-3176 | Command registration decorators (`cmd_run`, `cmd_parse`) |
| 3177-5251 | **Command implementations** (22 commands) |
| 5252-5266 | Entry point (`async_main` / `main`) |

### `container_to_args()` (line 1306)

This is the heart of the system. It takes a parsed compose service dictionary and produces a flat list of CLI arguments for `podman run` (or `podman create`). It handles:

- Networking (`--network`, `--pod`, `--dns`, etc.)
- Volumes (`--volume`, `--mount`)
- Environment variables (`-e`), env files (`--env-file`)
- Ports (`-p`), expose
- Capabilities (`--cap-add`, `--cap-drop`)
- Security options, sysctls, ulimits
- Resource limits (`--cpus`, `--memory`, etc.)
- Podman-specific `x-podman.*` extensions (uidmaps, gidmaps, rootfs, no_hosts)
- IPC modes, PID modes, cgroup parents
- Labels, annotations, devices, group additions

### `Podman` class (line 1795)

Wraps the `podman` binary via asyncio subprocess:

```python
class Podman:
    def __init__(self, compose, podman_path="podman", dry_run=False, semaphore=...)
```

Key methods:
- **`output()`** -- runs podman and returns stdout bytes; raises `CalledProcessError` on non-zero exit.
- **`run()`** -- runs podman and streams stdout/stderr with optional log formatting (for `podman logs -f`).
- **`exec()`** -- replaces the current process with podman (for interactive `exec` and `cp` commands).
- **`volume_ls()`** / **`network_ls()`** -- lists volumes/networks filtered by compose project labels.

All methods are async and concurrency-limited by an `asyncio.Semaphore` (default: `--parallel` CLI arg).

### `PodmanCompose` class (line 2334)

The main orchestrator. Holds all compose state:

- **`run(argv)`** -- entry point: parses args, detects podman version, reads compose file, dispatches to the registered command.
- **`get_podman_args(cmd)`** -- assembles global podman args and command-specific `--podman-run-args`.
- **`resolve_pod_name()`** -- determines whether containers run in a pod, and the pod name (priority: CLI `--in-pod` > `x-podman.in_pod` > default `True`).
- **`join_name_parts()`** / **`format_name()`** -- name generation with `_` (default) or `-` (docker-compat) separator.

### Command registration

Commands are registered via the `cmd_run` decorator:

```python
@cmd_run(podman_compose, "up", "Create and start the entire stack or some of its services")
async def compose_up(compose: PodmanCompose, args: argparse.Namespace) -> None:
```

A companion `cmd_parse` decorator attaches CLI argument parsers to any registered command.

---

## Commands

| Command | Description |
|---|---|
| `up` | Create and start the entire stack or some of its services |
| `down` | Tear down entire stack (stops containers, removes networks, volumes, and images on request) |
| `run` | Create and run a one-off container based on a service definition |
| `build` | Build stack images |
| `pull` | Pull stack images |
| `push` | Push stack images |
| `start` | Start specific services |
| `stop` | Stop specific services |
| `restart` | Restart specific services |
| `ps` | Show status of containers |
| `logs` | Show logs from services |
| `exec` | Execute a command in a running container |
| `cp` | Copy files/folders between a service container and the local filesystem |
| `port` | Print the public port for a port binding |
| `kill` | Kill one or more running containers with a specific signal |
| `pause` | Pause all running containers |
| `unpause` | Unpause all running containers |
| `images` | List images used by the created containers |
| `ls` | List running compose projects |
| `config` | Display the compose file |
| `version` | Show version |
| `wait` | Wait for running containers to stop |
| `systemd` | Generate systemd unit files |
| `config --services` | List configured services |

---

## Podman-specific Extensions (`x-podman.*`)

Podman-compose supports several extensions beyond the standard Compose spec, documented in `/Users/admin1/Documents/knowledge/sources/podman-compose/docs/Extensions.md`.

### Container-level extensions

| Key | Description |
|---|---|
| `x-podman.uidmaps` | UID mapping for user namespaces (e.g., `["1000:1000:1"]`) |
| `x-podman.gidmaps` | GID mapping for user namespaces |
| `x-podman.rootfs` | Run container with externally-managed rootfs (no image required) |
| `x-podman.no_hosts` | Skip `/etc/hosts` creation |

### Secrets-level extensions

| Key | Description |
|---|---|
| `x-podman.relabel` | SELinux relabeling (e.g., `Z` for private, unshared mount) |

### Network-level extensions

| Key | Description |
|---|---|
| `x-podman.disable_dns` | Disable the DNS plugin when set to `true` |
| `x-podman.dns` | List of nameservers for the network |
| `x-podman.routes` | Additional routes (corresponds to `--route` in `podman network create`) |
| `x-podman.mac_address` | Per-network MAC address (backward-compat; `mac_address` is now standard in compose spec) |
| `x-podman.interface_name` | Custom interface name inside the container |

### Podman-specific network modes

In addition to standard `bridge`, `host`, `none`, `service`, and `container`:

- `slirp4netns[:options,...]`
- `ns:options`
- `pasta[:options,...]`
- `private`

### Podman-specific mount type

- `glob` -- in addition to standard `volume`, `bind`, `tmpfs`

### Global `x-podman` settings (top-level)

```yaml
x-podman:
    in_pod: true                # Run containers in a pod
    pod_args: ["--infra=false", "--share="]  # Pod creation args
    docker_compose_compat: false  # Enable all compat settings
    name_separator_compat: false  # Use `-` instead of `_`
    default_net_name_compat: false  # Match docker-compose network naming
    default_net_behavior_compat: false  # Match docker-compose default net behavior
```

All settings can also be set via environment variables (`PODMAN_COMPOSE_IN_POD`, `PODMAN_COMPOSE_POD_ARGS`, `PODMAN_COMPOSE_DOCKER_COMPOSE_COMPAT`, etc.).

### YAML extension tags

- **`!override`** -- merges values when combining multiple compose files (similar to YAML merge).
- **`!reset`** -- resets a key to its empty state when overriding.

---

## Docker-compose Compatibility

Podman-compose supports several compatibility modes to match docker-compose behavior:

| Setting | Effect |
|---|---|
| `name_separator_compat` | Use `-` separator (like docker-compose) instead of `_` |
| `default_net_name_compat` | Match docker-compose default network naming (removes dashes from project name) |
| `default_net_behavior_compat` | Match docker-compose behavior when no networks are defined |
| `docker_compose_compat` | Enable all three compat settings at once |

---

## Lifecycle

### `up` flow

1. Check for existing podman installation and version.
2. Parse compose YAML file(s) and normalize all service definitions.
3. Resolve include/extends directives.
4. Create networks (or validate external networks exist).
5. Create pods (if `x-podman.in_pod` is enabled).
6. Pull/build images as needed.
7. For each container in dependency order:
   - Remove existing container if `--force-recreate`.
   - Create container via `podman create`.
   - Start container via `podman start`.
8. Optionally wait for containers to be running/healthy.

### `down` flow

1. Stop containers (with `stop_grace_period` respecting service deps).
2. Remove containers.
3. Optionally remove orphaned containers/images, volumes (`--volumes`), images (`--rmi`).
4. Remove pods and networks.

### `run` flow

1. Create pods if needed.
2. Start dependency services.
3. Build the service image if needed.
4. Override container config with CLI flags (entrypoint, user, workdir, env, ports, volumes, command).
5. Run a one-off container and stream output.

---

## Project Structure

```
sources/podman-compose/
  podman_compose.py          # 5266 lines -- the whole implementation
  pyproject.toml             # Project metadata, dependencies, tool config
  README.md                  # User-facing documentation
  LICENSE                    # GPL-2.0-only
  Dockerfile                 # Binary build container
  CONTRIBUTING.md
  RELEASING.md
  SECURITY.md
  CODE-OF-CONDUCT.md
  requirements.txt
  test-requirements.txt
  setup.cfg
  docs/
    Extensions.md            # Podman-specific compose extensions
    Mappings.md              # Podman-compose CLI mapping details
    Changelog-*.md           # Per-version changelogs
  tests/
    unit/                    # 25 unit test files (async tests via IsolatedAsyncioTestCase)
    integration/             # Integration tests
  examples/
    hello-python/            # Python app with Redis
    hello-app/               # Simple web app example
    wordpress/               # WordPress stack
    busybox/                 # Minimal busybox example
    awx3/, awx17/            # AWX (Ansible Tower) examples
    azure-vote/              # Azure Vote sample
    docker-inline/           # Inline Dockerfile example
    echo/                    # Echo service
    hello-app-redis/         # App with Redis
    nodeproj/                # Node.js project
    nvidia-smi/              # GPU passthrough example
  completion/bash/           # Bash completion script
  scripts/                   # Build/release utilities
  newsfragments/             # Towncrier changelog fragments
  .github/                   # CI/CD workflows
```

---

## Unit Tests

Unit tests are located in `tests/unit/` with 25 test files covering:

| Test file | Coverage |
|---|---|
| `test_container_to_args.py` | Core `container_to_args()` function (38807 bytes) |
| `test_container_to_args_secrets.py` | Secret handling in `container_to_args()` |
| `test_container_to_build_args.py` | Build argument generation |
| `test_get_net_args.py` | Network argument generation |
| `test_get_network_create_args.py` | Network creation arguments |
| `test_build_deps.py` | Build dependency resolution |
| `test_can_merge_build.py` | Build config merging |
| `test_compose_run_log_format.py` | Log formatting |
| `test_compose_cp_args.py` | Copy command arguments |
| `test_compose_exec_args.py` | Exec command arguments |
| `test_compose_run_update_container_from_args.py` | One-off run argument updates |
| `test_depends_on.py` | depends_on resolution |
| `test_normalize_depends_on.py` | depends_on normalization |
| `test_normalize_final_build.py` | Final build normalization |
| `test_normalize_service.py` | Service definition normalization |
| `test_rec_merge_depends_on.py` | Recursive depends_on merging |
| `test_rec_subs.py` | Recursive substitution |
| `test_var_interpolate.py` | Variable interpolation |
| `test_pull_image.py` | Image pull logic |
| `test_include.py` | Include directive handling |
| `test_is_context_git_url.py` | Git URL context detection |
| `test_main.py` | Main entry point error handling |
| `test_volumes.py` | Volume handling |

Tests use `unittest.IsolatedAsyncioTestCase` for async test methods and `parameterized.expand` for data-driven test cases.

---

## Dependencies

**Runtime:**
- `podman` (CLI tool, any modern version >=3.4 recommended)
- `python-dotenv` -- env file parsing
- `PyYAML` -- YAML parsing

**Development:**
- `coverage`, `parameterized`, `pre-commit`, `ruff`

---

## Installation

```bash
pip3 install podman-compose           # PyPI
pip3 install https://github.com/containers/podman-compose/archive/main.tar.gz  # Dev
sudo apt install podman-compose       # Debian
sudo dnf install podman-compose       # Fedora
brew install podman-compose           # Homebrew
```

Or download the single script directly:
```bash
curl -o /usr/local/bin/podman-compose https://raw.githubusercontent.com/containers/podman-compose/main/podman_compose.py
chmod +x /usr/local/bin/podman-compose
```

---

## Source file

## Related

- [[podman]] — Core Podman platform
- [[docker]] — Docker-compose compatibility
- [[orchestration]] — Container orchestration


`/Users/admin1/Documents/knowledge/sources/podman-compose/podman_compose.py`

**Type:** LLM wiki page
