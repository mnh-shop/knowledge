---
name: quadlet
description: "Quadlet — systemd-native container management for Podman"
source: sources/podman/
tags: [container, podman, quadlet, systemd, deployment]
---

# Quadlet

**Quadlet** is a Podman feature that allows running containers and pods as systemd services using declarative unit files (`.container`, `.pod`, `.volume`, `.network`, `.kube` files). Quadlet files are placed in standard systemd directories and are translated into systemd service units automatically.

Quadlet provides:
- Systemd-native container lifecycle management (start on boot, restart policies, dependency ordering)
- Rootless containers managed per-user via `systemd --user`
- Integration with `systemctl` for status, logs, and journald

## In This Vault

- `domains/deployment/quadlet-patterns.md` — detailed deployment patterns
- [[cockpit-podman]] — Cockpit UI for managing quadlets
- [[podman]] — Container engine that powers quadlets
