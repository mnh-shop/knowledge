---
name: quadlet-nix
tags: [quadlet-nix, quadlet, nix, deployment, container, declarative]
description: "Nix-based generation and management of Podman Quadlet units"
source: sources/quadlet-nix/
---

# Quadlet Nix

| Field | Value |
|---|---|
| **Origin** | [towo/quadlet-nix](https://github.com/towo/quadlet-nix) |
| **Source** | `sources/quadlet-nix/` |
| **Repomix** | `raw/quadlet-nix/quadlet-nix.xml` |
| **Codegraph** | `graphs/quadlet-nix/` |

## Overview

Quadlet Nix provides Nix-based tooling for generating and managing Podman Quadlet units. It brings the declarative power of the Nix package manager and NixOS module system to Quadlet container management, allowing users to define their container infrastructure as Nix expressions that produce correct Quadlet files as build output.

## Key Features

- **Nix-Generated Quadlets** — Define Quadlet units declaratively in Nix and produce validated `.container`, `.volume`, `.network` files
- **Nix Flake Integration** — Packaged as a Nix flake for easy consumption and composition
- **Parameterized Templates** — Reusable Nix functions for common container patterns
- **Validation at Build Time** — Quadlet files are validated during the Nix build phase rather than at runtime
- **Composable Infrastructure** — Combine with other Nix modules for complete system configuration

## Architecture

Quadlet Nix defines Nix functions that take container parameters and produce valid Quadlet file contents. These are integrated into the Nix build process, so deploying a container stack is as simple as applying a Nix configuration. The generated files can be deployed via NixOS modules or copied to the systemd user directory.

## Related

- [[nix-podman-stacks]] — NixOS configurations for Podman container stacks
- [[podlet]] — CLI Quadlet generator (different approach, same goal)
- [[podman-quadlet]] — Official Quadlet reference
- [[podman]] — Container runtime for generated units
