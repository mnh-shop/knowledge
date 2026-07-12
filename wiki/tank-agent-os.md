---
name: tank-agent-os
tags: [tank-agent-os, bootc, agent, immutable-os, container, fedora]
description: "Bootable container OS image for running AI agents in production"
source: sources/tank-agent-os/
---

# Tank Agent OS

| Field | Value |
|---|---|
| **Origin** | [tank-OS/tank-agent-os](https://github.com/tank-OS/tank-agent-os) |
| **Source** | `sources/tank-agent-os/` |
| **Repomix** | `raw/tank-agent-os/tank-agent-os.xml` |
| **Codegraph** | `graphs/tank-agent-os/` |

## Overview

Tank Agent OS is a bootable container OS image designed specifically for running AI agents in production. Built on Fedora bootc, it provides a minimal, immutable, self-updating operating system that boots directly into an agent runtime environment — eliminating the gap between containerized agent deployments and the host OS that runs them.

## Key Features

- **Bootc-Based Image** — Built with Fedora bootc for atomic, image-based OS updates
- **Agent Runtime Included** — Pre-installed agent runtimes (OpenClaw, Hermes, or custom)
- **Immutable Root Filesystem** — Read-only root with transactional updates
- **Automatic Updates** — Continuous delivery of OS and agent runtime updates via OCI image registry
- **Minimal Attack Surface** — Only packages needed for agent operation are included
- **Rootless Podman** — Pre-configured rootless Podman for running additional workloads

## Architecture

Tank Agent OS is defined as a Containerfile that layers agent runtime binaries and configuration on top of a bootc base image. The resulting OCI image is signed and published to a container registry. Systems boot from this image using bootc's update mechanism, pulling new versions atomically.

## Related

- [[tank-os]] — Fedora bootc image for general deployment (parent project)
- [[bootc]] — Bootable container technology underlying Tank
- [[openclaw]] — Personal AI assistant deployable on Tank Agent OS
- [[secureblue]] — Hardened Fedora Atomic images (security-focused)
