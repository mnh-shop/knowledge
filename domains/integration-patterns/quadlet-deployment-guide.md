---
name: quadlet-deployment-guide
description: "General guide for Quadlet-based container deployment in the ecosystem"
tags: [quadlet, podman, systemd, deployment, integration-patterns]
---

# Quadlet Deployment Guide

Quadlet files (`.container` units) define Podman containers as systemd services. In this ecosystem, all components (OpenClaw, n8n, Mission Control, Hermes) are deployed as Quadlets with explicit `After=` dependency chains.

See [[quadlet-patterns]] for general patterns and the stack-reference docs for specific configurations.
