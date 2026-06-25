---
name: buildah-deployment
tags: [buildah, deployment, installation]
description: Buildah Deployment
---

# Buildah Deployment

## Installation

### Linux

Buildah is available in all major Linux distributions:

```bash
# Fedora / RHEL / CentOS
sudo dnf install buildah

# Debian / Ubuntu
sudo apt install buildah

# Arch Linux
sudo pacman -S buildah

# openSUSE
sudo zypper install buildah
```

#### Requirements Verification

```bash
# Verify installation
buildah info          # Shows version, storage driver, image format support
buildah version       # Shows Buildah and runc versions

# Check rootless readiness (Linux)
buildah unshare cat /proc/self/uid_map
# Should show: 0 <host_uid> 1
```

### macOS

Buildah on macOS uses a Podman-managed Linux VM (via `podman machine`) for building:

```bash
brew install buildah
```

The storage backend on macOS is limited — running containers natively requires the Podman VM. For local development, prefer `podman build` (which delegates to Buildah via the Podman machine).

### Containerized Buildah

```bash
# From Docker Hub
docker run --privileged docker.io/containers/buildah build --help

# From Quay.io
docker run --privileged quay.io/buildah/stable build --help

# Rootless containerized build
podman run --security-opt label=disable quay.io/buildah/stable build --help
```

Containerized Buildah requires `--privileged` or `--device /dev/fuse` for overlay storage. For rootless build inside containers, use Podman-in-Podman patterns.

### From Source

```bash
git clone https://github.com/containers/buildah
cd buildah
make buildah
sudo cp buildah /usr/local/bin/
```

## Rootless Configuration Requirements

For rootless image building (the default on most modern systems), the following must be configured:

### `/etc/subuid` and `/etc/subgid`

These files define the subordinate ID ranges for user namespaces:

```bash
# /etc/subuid — format: <username>:<start_uid>:<count>
myuser:100000:65536
```

```bash
# /etc/subgid — same format
myuser:100000:65536
```

Verify with:

```bash
buildah info | grep -A 5 "idMappings"
```

### Storage Driver

```bash
# Check current driver
buildah info | grep "graphDriverName"

# Override in ~/.config/containers/storage.conf
cat > ~/.config/containers/storage.conf << 'EOF'
[storage]
driver = "overlay"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
EOF
```

- **Native overlay** (kernel 5.11+): `driver = "overlay"` (no `mount_program`)
- **fuse-overlayfs** (earlier kernels): `driver = "overlay"` + `mount_program = "/usr/bin/fuse-overlayfs"`
- **VFS** (slowest, most compatible): `driver = "vfs"`

### Networking for Rootless Builds

Rootless builds that use `RUN` instructions requiring network need `pasta` or `slirp4netns`:

```bash
# Install pasta (from passt package)
sudo dnf install passt        # Fedora
sudo apt install passt        # Debian/Ubuntu

# OR install slirp4netns
sudo dnf install slirp4netns  # Fedora
sudo apt install slirp4netns  # Debian/Ubuntu
```

### Runtime for RUN Instructions

Buildah needs an OCI runtime for `RUN` instructions:

```bash
# Install crun (recommended — smaller, faster, rootless-friendly)
sudo dnf install crun

# OR install runc
sudo dnf install runc
```

## Building Images in CI/CD Pipelines

### GitHub Actions

```yaml
# .github/workflows/build-image.yml
name: Build Agent Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Buildah
        run: |
          sudo apt-get update
          sudo apt-get install -y buildah

      - name: Build image
        run: |
          buildah build \
            --label "org.opencontainers.image.source=${{ github.server_url }}/${{ github.repository }}" \
            --label "org.opencontainers.image.revision=${{ github.sha }}" \
            --label "org.opencontainers.image.created=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
            --label "io.agentfield.built-by=ci" \
            -t my-agent:latest .

      - name: Push to registry
        env:
          REGISTRY_PASSWORD: ${{ secrets.REGISTRY_PASSWORD }}
        run: |
          buildah login -u pushuser -p "$REGISTRY_PASSWORD" registry.example.com
          buildah push my-agent:latest docker://registry.example.com/agents/my-agent:latest
```

### GitLab CI

```yaml
# .gitlab-ci.yml
build-image:
  stage: build
  image: quay.io/buildah/stable:latest
  variables:
    STORAGE_DRIVER: vfs
    BUILDAH_FORMAT: oci
  script:
    - buildah build
        --label "org.opencontainers.image.source=${CI_PROJECT_URL}"
        --label "io.agentfield.built-by=gitlab-ci"
        -t ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA}
        -t ${CI_REGISTRY_IMAGE}:latest
        .
    - buildah push --tls-verify=false
        ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA}
        docker://${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA}
    - buildah push --tls-verify=false
        ${CI_REGISTRY_IMAGE}:latest
        docker://${CI_REGISTRY_IMAGE}:latest
  only:
    - main
```

### Building Behind a Corporate Proxy

```bash
# HTTP_PROXY is automatically picked up by Buildah's RUN instructions
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
export NO_PROXY=localhost,127.0.0.1,.example.com

# Use --build-arg to inject into Dockerfile
buildah build \
  --build-arg HTTP_PROXY=$HTTP_PROXY \
  --build-arg HTTPS_PROXY=$HTTPS_PROXY \
  --build-arg NO_PROXY=$NO_PROXY \
  -t my-agent .
```

## Integration with Podman for Local Testing

The standard local development workflow:

```bash
# 1. Build the image (using buildah directly)
buildah build -t my-agent:dev .

# 2. Test with Podman
podman run --rm my-agent:dev --version

# 3. Push for deployment
buildah push my-agent:dev docker://registry.example.com/agents/my-agent:dev

# 4. Deploy with Agentfield (which uses Podman/Quadlet under the hood)
agentfield deploy my-agent:dev --target production
```

When using Podman, `podman build` is equivalent to `buildah build` — Podman vendors Buildah's build API. You can use either command interchangeably for Dockerfile-based builds.

```bash
# These are functionally identical:
podman build -t my-agent .
buildah build -t my-agent .
```

## Security Considerations

### Image Building Security

1. **Never build as root**: Rootless builds constrain what the build process can do. If the Dockerfile has a malicious `RUN` instruction, rootless mode limits its blast radius.

2. **Use `scratch`-based final stages**: For minimal attack surface:
   ```dockerfile
   FROM golang:1.22 AS builder
   COPY . /src
   RUN go build -o /app/agent /src/

   FROM scratch
   COPY --from=builder /app/agent /agent
   ENTRYPOINT ["/agent"]
   ```

3. **Set `--cap-drop=ALL` during RUN**: Minimize capabilities available to build commands:
   ```bash
   buildah build --cap-drop ALL -t my-agent .
   ```

4. **Use `--security-opt` labels**: SELinux/AppArmor labels for build containers:
   ```bash
   buildah build --security-opt label=level:s0:c100,c200 -t my-agent .
   ```

### Supply Chain Security

1. **Sign images with GPG or sigstore**:
   ```bash
   buildah build --sign-by my@email.com -t my-agent .
   buildah push --sign-by my@email.com my-agent docker://registry.example.com/agents/my-agent
   ```

2. **Use SBOM scanning** (when building for critical environments):
   ```bash
   buildah build --sbom-scanner syft -t my-agent .
   ```

3. **Verify base image signatures**:
   ```bash
   # In containers registries configuration
   # ~/.config/containers/registries.d/default.yaml
   docker:
     registry.example.com:
       sigstore-staging: file:///etc/pki/containers/sigstore
   ```

### Storage Security

1. **Storage directory permissions**: Buildah stores images in `~/.local/share/containers/storage/`. Ensure this directory is only readable by your user: `chmod 700 ~/.local/share/containers/storage`
2. **Clean up build artifacts**: `buildah rmi --all` removes all cached images and layers
3. **Prune intermediate containers**: `buildah rm --all` removes all build containers

## Example: Building and Running Agent Containers

### Simple Agent Image

```dockerfile
# Dockerfile — minimal node agent
FROM node:22-alpine AS base

# Use distroless production image
FROM gcr.io/distroless/nodejs22-debian12

WORKDIR /app
COPY --from=base /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY package.json package-lock.json ./
COPY src/ ./src/
RUN npm ci --omit=dev
COPY .env.production ./.env

EXPOSE 3000
USER 1000:1000
ENTRYPOINT ["node", "src/index.js"]
```

Build and verify:

```bash
buildah build \
  --label "io.agentfield.agent=hermes" \
  --label "io.agentfield.version=1.0.0" \
  -t hermes-agent:latest .

buildah inspect hermes-agent:latest
buildah push hermes-agent:latest docker://registry.example.com/agents/hermes-agent:latest
```

### Multi-Architecture Build

```bash
# Build for multiple platforms
buildah build \
  --platform linux/amd64,linux/arm64 \
  --manifest hermes-agent:multiarch \
  .

# Push the manifest list
buildah manifest push \
  hermes-agent:multiarch \
  docker://registry.example.com/agents/hermes-agent:latest
```

### Scripted Build (no Dockerfile)

```bash
#!/usr/bin/env bash
set -euo pipefail

AGENT_NAME="${1:-default-agent}"

# Create from scratch
ctr=$(buildah from scratch)

# Add base filesystem
buildah copy "$ctr" rootfs/ /

# Configure agent
buildah config \
  --author "agent-deploy@example.com" \
  --created-by "scripted-build v1.0" \
  --label "io.agentfield.agent=${AGENT_NAME}" \
  --label "io.agentfield.built=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --entrypoint '["/agent/entrypoint.sh"]' \
  --workingdir /agent \
  --port 8080 \
  "$ctr"

# Commit
buildah commit --rm "$ctr" "agent/${AGENT_NAME}:latest"

echo "Built agent/${AGENT_NAME}:latest"
```

## Troubleshooting

### "overlay: is not supported over ..."

Rootless overlay requires specific kernel support:
```bash
# Enable FUSE overlayfs
sudo dnf install fuse-overlayfs
# Or configure VFS fallback
echo "driver = \"vfs\"" >> ~/.config/containers/storage.conf
```

### "cannot re-exec process"

The rootless re-exec mechanism requires a multi-threaded Go runtime:
```bash
# Ensure no conflicting seccomp profile
buildah unshare cat /proc/self/uid_map
# Should show mapped IDs, not an error
```

### "operation not permitted" during RUN

Usually a user namespace mapping issue:
```bash
# Check your subuid/subgid configuration
grep "$(whoami)" /etc/subuid /etc/subgid
# Ensure ranges are non-empty and don't overlap with other users
```

### Slow builds with VFS storage

VFS is the slowest storage driver. Switch to overlay:
```bash
# Install fuse-overlayfs
sudo dnf install fuse-overlayfs
cat > ~/.config/containers/storage.conf << 'EOF'
[storage]
driver = "overlay"
[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
EOF
```

## References

- [Buildah install.md](https://github.com/containers/buildah/blob/main/install.md)
- [Buildah troubleshooting.md](https://github.com/containers/buildah/blob/main/troubleshooting.md)
- [containers/storage configuration](https://github.com/containers/storage/blob/main/docs/containers-storage.conf.5.md)
- [Podman rootless tutorial](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)
- [OCI image format specification](https://github.com/opencontainers/image-spec)

## Related

- [[buildah]] — Wiki overview, feature comparison, relationship to Podman
- [[buildah-architecture]] — Four-layer architecture, image building pipeline, rootless mode
- [[buildah-profile]] — Agent profile, configuration reference, command cheatsheet
