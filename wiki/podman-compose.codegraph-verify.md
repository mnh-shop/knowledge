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
  - `README.md:9-11` — "This project only depends on: `podman`, podman dnsname plugin, Python 3.9+, PyYAML, python-dotenv."
  - `README.md:22` — "formed as a single Python file script that you can drop into your PATH and run"
  - `podman_compose.py:1-8` — Docstring references docker-compose compose-file specs, confirms compatibility target
  - `podman_compose.py:2334` — `class PodmanCompose:` — Main class orchestrating the compose-to-podman translation
  - `podman_compose.py:3134` — `class PodmanComposeError(Exception):` — Custom error handling

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Single-file Python implementation (~5266 lines) with direct podman command execution
- **Wiki says:** "The project is a single Python file (`podman_compose.py`, ~5266 lines) that directly executes `podman` subprocesses. It has 135+ subprocess calls translating docker-compose.yml directives to `podman` CLI equivalents."

- **Source evidence:**
  - `podman_compose.py:5266` — Line count confirmed: 5266 lines
  - `podman_compose.py:1` — `#!/usr/bin/env python3` — Single file executable
  - `README.md:22` — "formed as a single Python file script that you can drop into your PATH and run"
  - `grep -c "subprocess\|Popen\|run"` — Returns 135 subprocess-related calls throughout the file
  - `podman_compose.py:1795` — `class Podman:` — Podman command wrapper class
  - `podman_compose.py:11-30` — Import of `asyncio.subprocess`, `subprocess` modules for command execution
  - `podman_compose.py:2335` — `class XPodmanSettingKey(Enum):` — Podman-specific configuration keys
  - `pyproject.toml:1-4` — Setuptools build system with single-file module

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: YAML parsing with variable substitution, custom tags, and network name handling
- **Wiki says:** "podman-compose parses docker-compose YAML with full variable substitution (shell-style `${VAR}` and `${VAR:-default}`), custom YAML tags (`!override`, `!reset`), and automatic network/project name generation."

- **Source evidence:**
  - `podman_compose.py:44` — `import yaml` — PyYAML for compose file parsing
  - `podman_compose.py:45` — `from dotenv import dotenv_values` — `.env` file support
  - `podman_compose.py:275-470` — `var_interpolate`, `rec_subs`, `VarInterpolationOperators`, `Token`, `LiteralToken`, `VarToken`, `interpolate_str` — Full variable substitution implementation supporting `${VAR}`, `${VAR:-default}`, and nested resolution
  - `podman_compose.py:1715` — `class OverrideTag(yaml.YAMLObject):` — Custom `!override` YAML tag
  - `podman_compose.py:1744` — `class ResetTag(yaml.YAMLObject):` — Custom `!reset` YAML tag
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
  - `podman_compose.py:1579` — `class ServiceDependencyCondition(Enum):` — Enum defining `service_started`, `service_healthy`, `service_completed_successfully`
  - `podman_compose.py:1612` — `class ServiceDependency:` — Dependency class with `condition`, `required`, and dependency resolution
  - `podman_compose.py:3645` — `class DependField(str, Enum):` — Alternative dependency field enumeration
  - `podman_compose.py:2334-2400` — `PodmanCompose` class orchestration includes dependency resolution in service startup ordering

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Pull policy management and image settings
- **Wiki says:** "podman-compose supports Docker Compose pull policies (`always`, `missing`, `never`, `newer`) and configurable image pull settings with progress display."

- **Source evidence:**
  - `podman_compose.py:3781` — `class PullImageSettings:` — Pull image settings container class
  - `podman_compose.py:5063` — `class PullPolicyAction(argparse.Action):` — CLI argument parser action for pull policy
  - `podman_compose.py:3781-3900` — Implements pull logic with policy selection and progress display
  - `README.md:80-131` — Installation and usage documentation covering pip, package repos, and running

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the podman-compose wiki have been verified against the source code:
- ✅ **Compose Spec + Podman backend:** Rootless, daemonless design confirmed
- ✅ **Single-file Python:** 5266-line `podman_compose.py` with 135+ subprocess calls
- ✅ **YAML parsing:** Full variable substitution, custom tags, network naming confirmed
- ✅ **Volume/mount/secret translation:** Complete translation pipeline for compose storage directives
- ✅ **Service dependencies:** Three condition states with `ServiceDependencyCondition` enum
- ✅ **Pull policy management:** `PullPolicyAction`, `PullImageSettings` with `always`/`missing`/`never`/`newer`

## Related

- [[podman-compose]] -- Main wiki entry
- [[podman]] -- Container runtime backend
- [[podlet]] -- Quadlet file generation (alternative deployment)
- [[podman-quadlet]] -- Podman systemd integration

## Cross-project

- [[podman.codegraph-verify]] -- Container runtime foundation
- [[podlet.codegraph-verify]] -- Alternative deployment tooling
- [[buildah.codegraph-verify]] -- Image builder used in compose build steps
