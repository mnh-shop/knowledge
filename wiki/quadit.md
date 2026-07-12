---
name: quadit
tags: [quadit, quadlet, cli, deployment, container, systemd]
description: "CLI toolkit for managing Podman Quadlet units"
source: sources/quadit/
---

# Quadit

| Field | Value |
|---|---|
| **Origin** | [towo/quadit](https://github.com/towo/quadit) |
| **Source** | `sources/quadit/` |
| **Repomix** | `raw/quadit/quadit.xml` |
| **Codegraph** | `graphs/quadit/` |

## Overview

Quadit is a command-line toolkit for managing Podman Quadlet units. It simplifies the creation, validation, deployment, and lifecycle management of Quadlet service files, providing a developer-friendly interface on top of the raw Quadlet file format. It fills the gap between manually editing Quadlet files and using Podman Desktop's GUI extension.

## Key Features

- **Unit Generation** — Scaffold Quadlet `.container`, `.volume`, `.network`, and `.pod` files from CLI arguments
- **Validation** — Lint and validate Quadlet files for correct syntax and directive usage
- **Deploy & Teardown** — Install Quadlet files to the systemd user directory and manage the service lifecycle
- **Status Reporting** — View the runtime status of deployed Quadlet units
- **Template Library** — Built-in templates for common container patterns (web services, databases, queues)
- **Dry-Run Mode** — Preview generated units without writing to disk

## Architecture

Quadit operates on Quadlet files in the user's `~/.config/containers/systemd/` directory. It can generate files from scratch, import from existing podman run commands, or modify existing units. The tool interacts with `systemctl --user` for lifecycle operations and may validate units against the Quadlet specification.

## Related

- [[podlet]] — Quadlet file generator (similar tool, different approach)
- [[podman-quadlet]] — Official Quadlet getting started and reference
- [[podman]] — Container runtime for Quadlet units
- [[extension-podman-quadlet]] — Desktop GUI for Quadlet management
