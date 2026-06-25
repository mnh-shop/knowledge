---
name: buildah-profile
description: Buildah is a daemonless, rootless OCI image builder — the build-time layer for agent deployment pipelines
tags: [buildah, oci, image-builder, profile]
metadata:
  type: reference
source: sources/buildah/
---

# Buildah — Agent Profile

**License:** Apache 2.0

**What it is:** An OCI container image builder that runs without a daemon and without root. Specializes in building images from Dockerfiles OR from scratch using scriptable primitives. From the `containers` project, same organization as Podman.

**Quick install (Linux):**
```bash
sudo dnf install buildah    # Fedora/RHEL
sudo apt install buildah    # Debian/Ubuntu
```

**Containerized:**
```bash
podman run quay.io/buildah/stable build --help
```

**Language:** Go (module: `go.podman.io/buildah`)

**Integrates with:** Podman (vendored API), containers/storage, containers/image, OCI runtimes (crun/runc)

---

## What a "Buildah Agent" Is

A Buildah agent is not a running service — it is a **build-time tool** used in agent deployment pipelines. Specifically, a Buildah agent:

1. **Receives build instructions** (Dockerfile or build script + context directory).
2. **Builds an OCI image** containing the agent software.
3. **Pushes the image** to a container registry.
4. **Optionally signs and scans** the image for supply chain security.

In the agent deployment stack, Buildah is the **image builder** — the step between "source code is ready" and "image is available for Podman to run."

## When to Use Buildah vs Podman Build

| Scenario | Buildah | `podman build` |
|---|---|---|
| Dockerfile build | `buildah build` | `podman build` (delegates to Buildah) |
| Scripted/programmatic build | Native (`buildah from`, `buildah copy`, etc.) | Not directly supported |
| Embedding in Go applications | Import `go.podman.io/buildah` | Import `go.podman.io/podman/pkg/buildah` (wrapper) |
| Need lower-level control | Yes (each instruction is separate) | No (Dockerfile-only) |
| `podman build` is already available | Not needed separately | Use it directly |

**Rule of thumb:** If you're building from a Dockerfile, `podman build` and `buildah build` are interchangeable because Podman vendors Buildah's build API. If you need scripted builds, CI/CD integration at a lower level, or are embedding image building in a Go application, use Buildah directly.

## Configuration Reference

### Storage Configuration (`~/.config/containers/storage.conf`)

```ini
[storage]
driver = "overlay"
runroot = "/run/user/$UID/containers"
graphroot = "/home/$USER/.local/share/containers/storage"

[storage.options]
size = ""
# fuse-overlayfs for rootless on kernels < 5.11
mount_program = "/usr/bin/fuse-overlayfs"
mountopt = "nodev,metacopy=on"

# For better performance with many layers
[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
```

### Registries Configuration (`/etc/containers/registries.conf` or `~/.config/containers/registries.conf`)

```toml
unqualified-search-registries = ["docker.io", "quay.io"]

[[registry]]
prefix = "docker.io"
location = "docker.io"

[[registry.mirror]]
location = "mirror.gcr.io"

[[registry]]
prefix = "localhost"
location = "localhost:5000"
insecure = true
```

### Policy Configuration (`/etc/containers/policy.json` or `~/.config/containers/policy.json`)

```json
{
  "default": [
    {
      "type": "reject"
    }
  ],
  "transports": {
    "docker": {
      "registry.example.com": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/containers/example.pub"
        }
      ]
    },
    "docker-daemon": {
      "": [
        {
          "type": "insecureAcceptAnything"
        }
      ]
    }
  }
}
```

## Skill/Tool Descriptions

### Image Building

| Command | Description | Example |
|---|---|---|
| `buildah build` | Build from Dockerfile/Containerfile | `buildah build -t my-agent .` |
| `buildah bud` | Alias for `buildah build` | `buildah bud -f Dockerfile .` |
| `buildah from` | Create a new build container | `buildah from alpine` |
| `buildah commit` | Commit container to image | `buildah commit $ctr my-image` |
| `buildah config` | Set image config (labels, cmd, ports) | `buildah config --label "x=y" $ctr` |

### Content Management

| Command | Description | Example |
|---|---|---|
| `buildah add` | Add files (with URL/tar extraction) | `buildah add $ctr https://example.com/tar.gz /` |
| `buildah copy` | Copy files into container | `buildah copy $ctr ./src /app/src` |
| `buildah run` | Run command in build container | `buildah run $ctr -- dnf install -y nginx` |
| `buildah mount` | Mount container rootfs | `buildah mount $ctr` |
| `buildah unmount` | Unmount container rootfs | `buildah umount $ctr` |

### Image Management

| Command | Description | Example |
|---|---|---|
| `buildah images` | List local images | `buildah images` |
| `buildah pull` | Pull image from registry | `buildah pull alpine:latest` |
| `buildah push` | Push image to registry | `buildah push my-agent docker://registry...` |
| `buildah rmi` | Remove image | `buildah rmi my-agent` |
| `buildah tag` | Tag an image | `buildah tag my-agent my-agent:1.0` |
| `buildah inspect` | Inspect image config | `buildah inspect my-agent` |
| `buildah manifest` | Manage manifest lists | `buildah manifest push my-list docker://...` |

### Advanced

| Command | Description | Example |
|---|---|---|
| `buildah unshare` | Run in user namespace | `buildah unshare` (opens shell) |
| `buildah version` | Show version info | `buildah version` |
| `buildah info` | Show system info | `buildah info` |
| `buildah login` | Login to registry | `buildah login registry.example.com` |
| `buildah logout` | Logout from registry | `buildah logout registry.example.com` |

## Common Integration Patterns

### CI/CD Pipeline Embedding

```bash
#!/usr/bin/env bash
# ci-build.sh — build and push agent image in CI

set -euo pipefail

REGISTRY="${CI_REGISTRY:-registry.example.com}"
IMAGE_TAG="${CI_COMMIT_SHORT_SHA:-latest}"
LABELS="--label io.agentfield.build-id=${CI_JOB_ID:-local}"

buildah build \
  $LABELS \
  --label "io.agentfield.agent=${AGENT_NAME}" \
  --label "io.agentfield.commit=${CI_COMMIT_SHA:-dev}" \
  --label "io.agentfield.built=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -t "${REGISTRY}/agents/${AGENT_NAME}:${IMAGE_TAG}" \
  .

buildah push \
  "${REGISTRY}/agents/${AGENT_NAME}:${IMAGE_TAG}" \
  docker://"${REGISTRY}/agents/${AGENT_NAME}:${IMAGE_TAG}"

# Also tag as latest for dev environments
buildah tag "${REGISTRY}/agents/${AGENT_NAME}:${IMAGE_TAG}" "${REGISTRY}/agents/${AGENT_NAME}:latest"
buildah push "${REGISTRY}/agents/${AGENT_NAME}:latest" docker://"${REGISTRY}/agents/${AGENT_NAME}:latest"
```

### Go Library Embedding

```go
package main

import (
    "context"
    "fmt"
    "go.podman.io/buildah"
    "go.podman.io/buildah/define"
    "go.podman.io/buildah/imagebuildah"
    "go.podman.io/storage"
)

func buildImage(ctx context.Context, dockerfile, contextDir, output string) error {
    store, err := storage.GetStore(storage.StoreOptions{})
    if err != nil {
        return fmt.Errorf("getting store: %w", err)
    }
    defer store.Shutdown(false)

    options := define.BuildOptions{
        ContextDirectory: contextDir,
        Output:           output,
        PullPolicy:       define.PullIfMissing,
    }

    id, ref, err := imagebuildah.BuildDockerfiles(ctx, store, options, dockerfile)
    if err != nil {
        return fmt.Errorf("build failed: %w", err)
    }

    fmt.Printf("Built image: %s (%s)\n", id, ref.String())
    return nil
}
```

### Rootless Agent Deployment Pipeline

```
Developer pushes code
       │
       ▼
  GitHub Actions / GitLab CI
       │
       ├── buildah build --platform linux/amd64,linux/arm64
       ├── buildah push to registry
       ├── (optional) cosign sign
       │
       ▼
  Registry (e.g., quay.io/example/agent)
       │
       ▼
  Agentfield deploy agent@registry...:tag
       │
       ▼
  Podman (Quadlet) runs the agent container
```

## Related

- [[buildah]] -- Wiki overview, feature comparison, relationship to Podman
- [[buildah-architecture]] -- Four-layer architecture, image building pipeline, rootless mode
- [[buildah-deployment]] -- Installation, CI/CD pipelines, rootless configuration
- [[podman]] — Runtime counterpart (runs what Buildah builds)
- [[podman-deployment]] — Runtime deployment, Quadlet, rootless config
- [[agentfield]] — Manages deployed agents
- [[tank-os]] — Immutable OS that runs Podman containers
- [[openclaw]] — Can build OpenClaw images with Buildah
