---
name: podlet-api
description: "Podlet — no REST API (CLI-only tool)"
source: sources/podlet/
tags: [api, cli, container, podlet, podman, quadlet, rust]
---

# Podlet — API Reference

**Conclusion: Podlet does not expose a REST API or HTTP server.**

Podlet is a CLI-only Rust application. Its interface is the command line:

```bash
# Convert podman run to Quadlet
podlet podman run --name myapp nginx:latest

# Convert Docker Compose to Quadlet
podlet compose

# Generate from existing container
podlet generate my-container
```

## CLI Command Surface

| Command | Purpose |
|---------|---------|
| `podlet podman` | Convert `podman run/create` args to Quadlet |
| `podlet compose` | Convert Docker Compose to Quadlet files |
| `podlet generate` | Generate Quadlet from running container/pod |
| `podlet kube` | Convert Kubernetes YAML to Quadlet |
| `podlet network` | Generate Quadlet network files |
| `podlet volume` | Generate Quadlet volume files |
| `podlet build` | Generate Quadlet build files |
| `podlet image` | Generate Quadlet image files |
| `podlet artifact` | Generate Quadlet artifact files |

## Related

- [[podlet-architecture]] — Conversion pipeline architecture
- [[podlet-deployment]] — Installation and usage
