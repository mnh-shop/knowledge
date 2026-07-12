---
name: podman-quadlet
tags: [podman-quadlet, podman, quadlet, deployment, systemd, container]
description: "Getting started guide and reference for Podman with Quadlet systemd integration"
source: sources/podman-quadlet/
---

# Podman Quadlet

| Field | Value |
|---|---|
| **Origin** | [containers/podman/tree/main/docs/quadlet](https://github.com/containers/podman/tree/main/docs/quadlet) |
| **Source** | `sources/podman-quadlet/` |
| **Repomix** | `raw/podman-quadlet/podman-quadlet.xml` |
| **Codegraph** | `graphs/podman-quadlet/` |

## Overview

Podman Quadlet is the official getting-started guide and reference documentation for running Podman containers with Quadlet — Podman's native integration with systemd. Quadlet allows users to define containers, volumes, networks, and pods as systemd unit files, giving them the full lifecycle management capabilities of systemd (dependency ordering, auto-restart, logging, resource control) while using the familiar container image paradigm.

## Key Features

- **Systemd-Native Containers** — Define containers as `.container` unit files managed by `systemd --user`
- **Quadlet File Types** — `.container`, `.volume`, `.network`, `.pod`, `.image`, `.kube` unit types
- **Automatic Generation** — systemd units are generated from Quadlet files on service start
- **Dependency Management** — `Requires=`, `After=`, `Before=` between containers and system services
- **Auto-Update Support** — Integration with Podman's auto-update mechanism
- **Rootless by Default** — Quadlet units run rootless under the user's systemd session

## Architecture

Quadlet files live in `~/.config/containers/systemd/` and are automatically picked up by `systemd --user`. When a user enables a service, Quadlet generates the corresponding systemd unit and podman arguments. The container lifecycle becomes a systemd service lifecycle — start, stop, restart, enable, disable, status.

## Related

- [[podman]] — Container runtime that executes Quadlet-managed containers
- [[podlet]] — CLI tool for generating Quadlet files from container run commands
- [[extension-podman-quadlet]] — Podman Desktop extension for GUI Quadlet management
- [[quadlet]] — Base wiki on the Quadlet format
