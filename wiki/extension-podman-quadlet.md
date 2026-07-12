---
name: extension-podman-quadlet
tags: [extension-podman-quadlet, podman, quadlet, plugin, desktop, container]
description: "Podman Desktop extension for Quadlet container management"
source: sources/extension-podman-quadlet/
---

# Extension Podman Quadlet

| Field | Value |
|---|---|
| **Origin** | [containers/podman-desktop-extension-podman-quadlet](https://github.com/containers/podman-desktop-extension-podman-quadlet) |
| **Source** | `sources/extension-podman-quadlet/` |
| **Repomix** | `raw/extension-podman-quadlet/extension-podman-quadlet.xml` |
| **Codegraph** | `graphs/extension-podman-quadlet/` |

## Overview

Extension Podman Quadlet is a Podman Desktop extension that provides a graphical interface for managing Quadlet container units. It bridges the gap between Podman Desktop's GUI and Quadlet's systemd-integrated container definitions, allowing users to create, edit, start, stop, and monitor Quadlet units without leaving the desktop environment.

## Key Features

- **Quadlet Unit Management** — Create, edit, and delete Quadlet `.container`, `.volume`, `.network`, and `.pod` files
- **Visual Editor** — Form-based editing of Quadlet unit directives with validation
- **Status Dashboard** — Real-time view of Quadlet unit states (active, inactive, failed)
- **Journal Integration** — View container logs through the desktop interface
- **Systemd Integration** — Start/stop/restart operations via systemd user services
- **Template Support** — Pre-configured Quadlet templates for common service patterns

## Architecture

The extension plugs into Podman Desktop's extension API, registering new pages and views within the existing dashboard. It interacts with the host system's podman socket and systemd user manager to manage Quadlet units, and reads/writes Quadlet files from the standard user quadlet directories.

## Related

- [[podman]] — Container engine that runs Quadlet units
- [[podlet]] — Quadlet file generator for container configurations
- [[podman-quadlet]] — Getting started guide for Podman with Quadlet
- [[quadlet]] — Base wiki for Quadlet unit format
