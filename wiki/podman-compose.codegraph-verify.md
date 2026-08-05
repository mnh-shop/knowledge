---
name: podman-compose-codegraph-verify
tags: [podman-compose, codegraph-verify, podman, compose]
description: "Codegraph Verification: podman-compose — validating wiki claims against indexed source code"
source: sources/podman-compose/
---

# Codegraph Verification: podman-compose

**Date:** 2026-07-12

## Claim 1: Compose Spec implementation with Podman backend — rootless, daemonless
- **Wiki says:** "podman-compose is an implementation of the Compose Spec with a Podman backend. It is rootless and daemonless — it directly executes podman commands rather than running a daemon."

- **Source evidence:**
  - `README.md:4-8` — "An implementation of [Compose Spec](https://compose-spec.io/) with [Podman](https://podman.io/) backend. This project focuses on: rootless, daemon-less process model, we directly execute podman, no running daemon."
  - `README.md:9-14` — "This project only depends on: `podman`, podman dnsname plugin, Python 3.9+, PyYAML, python-dotenv."
  - `README.md:22` — "formed as a single Python file script that you can drop into your PATH and run"
  - `podman_compose.py:1-8` — Docstring references docker-compose compose-file specs, confirms compatibility target
  - `podman_compose.py:2399` — `class PodmanCompose:` — Main class orchestrating the compose-to-podman translation
  - `podman_compose.py:3249` — `class PodmanComposeError(Exception):` — Custom error handling

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Single-file Python implementation (5514 lines) with direct podman command execution
- **Wiki says:** "The project is a single Python file (`podman_compose.py`, 5514 lines) that directly executes `podman` subprocesses."

- **Source evidence:**
  - `podman_compose.py` — file is 5514 lines (verified via `wc -l`); entry point at 5501-5514 (`async_main` / `main`)
  - `podman_compose.py:1` — `#!/usr/bin/env python3` — Single file executable
  - `README.md:22` — "formed as a single Python file script that you can drop into your PATH and run"
  - `podman_compose.py:1837` — `class Podman:` — Podman command wrapper class (async subprocess execution, concurrency-limited by `asyncio.Semaphore`)
  - `podman_compose.py:2400` — `class XPodmanSettingKey(Enum):` — Podman-specific configuration keys (`docker_compose_compat`, `default_net_name_compat`, `default_net_behavior_compat`, `name_separator_compat`, `in_pod`, `pod_args`); consumed from `PODMAN_COMPOSE_*` env vars at 2601-2613
  - `pyproject.toml:1-4` — Setuptools build system with single-file module

- **Verdict:** ✅ CORRECT (line count refreshed 5266 → 5514)
- **Fix needed:** Applied — section table line map refreshed in wiki (container_to_args 1339, Podman 1837, PodmanCompose 2399, decorators 3253-3296, commands 3297-4875, entry 5501-5514)

## Claim 3: YAML parsing with variable substitution, custom tags, and network name handling
- **Wiki says:** "podman-compose parses docker-compose YAML with full variable substitution (shell-style `${VAR}` and `${VAR:-default}`), custom YAML tags (`!override`, `!reset`), and automatic network/project name generation."

- **Source evidence:**
  - `podman_compose.py:44` — `import yaml` — PyYAML for compose file parsing
  - `podman_compose.py:45` — `from dotenv import dotenv_values` — `.env` file support
  - `podman_compose.py:275-470` — `var_interpolate`, `rec_subs`, `VarInterpolationOperators`, `Token`, `LiteralToken`, `VarToken`, `interpolate_str` — Full variable substitution implementation supporting `${VAR}`, `${VAR:-default}`, and nested resolution
  - `podman_compose.py:1756` — `class OverrideTag(yaml.YAMLObject):` — Custom `!override` YAML tag
  - `podman_compose.py:1785` — `class ResetTag(yaml.YAMLObject):` — Custom `!reset` YAML tag
  - `podman_compose.py:546-556` — `default_network_name_for_project` — Network name generation with `project_name` formatting and x-podman key support
  - `podman_compose.py:262-264` — Comments: "docker and docker-compose support subset of bash variable substitution"

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Volume, mount, secret, and ulimit translation from compose to podman CLI
- **Wiki says:** "podman-compose translates docker-compose volume definitions, mount specifications, secrets, and ulimit configuration into equivalent podman CLI arguments."

- **Source evidence:**
  - `podman_compose.py:577-620` — `assert_volume` function: creates/mounts volumes with `compose.project_name` and label `io.podman.compose.project`
  - `podman_compose.py:638-650` — `mount_desc_to_mount_args` — Converts mount descriptors to podman mount argument strings
  - `podman_compose.py:687-704` — `ulimit_to_ulimit_args` and `container_to_ulimit_args` — Translate ulimit configurations to `--ulimit` CLI args
  - `podman_compose.py:714-760` — `mount_desc_to_volume_args` — Volume binding with `srv_name` for service-specific volume handling
  - `podman_compose.py:764-795` — `get_mount_args` — Async mount argument generation with volume assertion
  - `podman_compose.py:797-830` — `get_secret_args` — Secret resolution for podman secret mounts
  - `podman_compose.py:162-224` — `parse_short_mount` — Short-syntax mount parsing (e.g. `./path:/container/path`)
  - `podman_compose.py:224-275` — `fix_mount_dict` — Normalizes mount dictionary format for compatibility

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Service dependency handling with condition states (service_started, service_healthy, service_completed_successfully)
- **Wiki says:** "podman-compose supports Compose Spec service dependencies with condition states: `service_started`, `service_healthy`, and `service_completed_successfully`. Dependencies can reference services across the compose project."

- **Source evidence:**
  - `podman_compose.py:1617` — `class ServiceDependencyCondition(Enum):` — Enum defining `service_started`, `service_healthy`, `service_completed_successfully`
  - `podman_compose.py:1653` — `class ServiceDependency:` — Dependency class with `condition`, `required`, and dependency resolution
  - `podman_compose.py:3763` — `class DependField(str, Enum):` — Alternative dependency field enumeration
  - `podman_compose.py:2399-2400` — `PodmanCompose` class orchestration includes dependency resolution in service startup ordering

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Pull policy management and image settings
- **Wiki says:** "podman-compose supports Docker Compose pull policies (`always`, `missing`, `never`, `newer`) and configurable image pull settings with progress display."

- **Source evidence:**
  - `podman_compose.py:3965` — `class PullImageSettings:` — Pull image settings container class
  - `podman_compose.py:5311` — `class PullPolicyAction(argparse.Action):` — CLI argument parser action for pull policy
  - `podman_compose.py:3965-4050` — Implements pull logic with policy selection and progress display
  - `README.md:80-131` — Installation and usage documentation covering pip, package repos, and running

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: 24 commands registered via cmd_run, including stats; systemd registers podman-compose@.service template unit
- **Wiki says:** podman-compose ships 24 commands; `systemd` generates unit files; `stats` displays CPU/memory/network/block I/O and PIDs.

- **Source evidence:**
  - `podman_compose.py:3297-4875` — all 24 `@cmd_run` registrations: `ls` (3297), `version` (3351), `wait` (3373), `systemd` (3384), `pull` (3489), `push` (3507), `build` (3684), `up` (4130), `down` (4417), `ps` (4502), `run` (4517), `cp` (4607), `exec` (4646), `start` (4713), `stop` (4721), `restart` (4726), `logs` (4731), `config` (4768), `port` (4779), `pause` (4790), `unpause` (4801), `kill` (4812), `stats` (4844), `images` (4875)
  - `podman_compose.py:4849` — `async def compose_stats(...)` — CPU, memory, network I/O, block I/O and PIDs (`podman stats` passthrough)
  - `podman_compose.py:3384-3408` — `compose_systemd` `register` action writes `~/.config/containers/compose/projects/<proj>.env` and instructs `systemctl --user start podman-compose@<PROJ>`
  - `podman_compose.py:3456-3488` — `create-unit` action writes the `podman-compose@.service` template unit (`/etc/systemd/user/podman-compose@.service`) with `ExecStartPre`/`ExecStop` pod commands and `WantedBy=default.target`

- **Verdict:** ✅ CORRECT (command count refreshed 22 → 24; stats row added to wiki table; systemd note expanded)
- **Fix needed:** Applied

## Claim 8: Unit tests — 26 test files in tests/unit/
- **Wiki says:** unit tests live in `tests/unit/` covering container-to-args translation, dependencies, parsing, interpolation, volumes, etc.

- **Source evidence:** `tests/unit/` contains 26 `test_*.py` files (plus `__init__.py`): `test_container_to_args.py`, `test_container_to_args_secrets.py`, `test_container_to_build_args.py`, `test_compose_up_args.py`, `test_get_net_args.py`, `test_get_network_create_args.py`, `test_build_deps.py`, `test_can_merge_build.py`, `test_compose_run_log_format.py`, `test_compose_cp_args.py`, `test_compose_exec_args.py`, `test_compose_run_update_container_from_args.py`, `test_depends_on.py`, `test_normalize_depends_on.py`, `test_normalize_final_build.py`, `test_normalize_service.py`, `test_parse_args.py`, `test_rec_merge_depends_on.py`, `test_rec_subs.py`, `test_service_dependency_condition.py`, `test_var_interpolate.py`, `test_pull_image.py`, `test_include.py`, `test_is_context_git_url.py`, `test_main.py`, `test_volumes.py`. Tests use `unittest.IsolatedAsyncioTestCase` and `parameterized.expand`.

- **Verdict:** ✅ CORRECT (table refreshed from 23 → 26 rows; wiki count updated)
- **Fix needed:** Applied

## Summary

All 8 key claims from the podman-compose wiki verified against the source code:
- ✅ **Compose Spec + Podman backend:** Rootless, daemonless design confirmed
- ✅ **Single-file Python:** 5514-line `podman_compose.py`; section map refreshed
- ✅ **YAML parsing:** Full variable substitution, custom tags, network naming confirmed
- ✅ **Volume/mount/secret translation:** Complete translation pipeline for compose storage directives
- ✅ **Service dependencies:** Three condition states with `ServiceDependencyCondition` enum
- ✅ **Pull policy management:** `PullPolicyAction`, `PullImageSettings` with `always`/`missing`/`never`/`newer`
- ✅ **Commands:** 24 `@cmd_run` registrations incl. `stats`; `systemd` writes `podman-compose@.service` template
- ✅ **Tests:** 26 unit test files in `tests/unit/`

## Related

- [[podman-compose]] -- Main wiki entry
- [[podman]] -- Container runtime backend
- [[podlet]] -- Quadlet file generation (alternative deployment)
- [[podman-quadlet]] -- Podman systemd integration

## Cross-project

- [[podman.codegraph-verify]] -- Container runtime foundation
- [[podlet.codegraph-verify]] -- Alternative deployment tooling
- [[buildah.codegraph-verify]] -- Image builder used in compose build steps
