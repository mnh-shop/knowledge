---
name: podman-pod-stack
description: "Podman pod-based deployment stacks for colocated multi-container services"
tags: [podman, container, deployment, integration-patterns]
---

# Podman Pod Stack

Podman pods colocate multiple containers that share a network namespace. In this ecosystem, pods can be used to group related services (e.g., OpenClaw + n8n) with shared network configuration and simplified dependency management.

See [[stack-reference-mission-control]] and [[stack-reference-openclaw-n8n]] for Quadlet-based deployment patterns.
