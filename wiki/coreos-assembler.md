---
name: coreos-assembler
tags: [coreos-assembler, fedora, bootc, image-builder, ostree, container-linux]
description: "Build pipeline and tooling for creating Fedora CoreOS images and derivatives"
source: sources/coreos-assembler/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# coreos-assembler

| Field | Value |
|---|---|
| **Origin** | [coreos/coreos-assembler](https://github.com/coreos/coreos-assembler) |
| **License** | Apache 2.0 |
| **Stack** | Go, bash, Python, ostree, rpm-ostree, QEMU, supermin |
| **Source** | `sources/coreos-assembler/` |
| **Repomix** | `raw/coreos-assembler/coreos-assembler.xml` |
| **Codegraph** | `graphs/coreos-assembler/` |

## Overview

coreos-assembler (also known as `cosa`) is the build pipeline and tooling used to create [Fedora CoreOS](https://coreos.fedoraproject.org) (FCOS) images and derivative operating systems. It orchestrates the full image build lifecycle — from package selection and composition through OSTree commit creation and final disk image generation. The tool runs inside a containerized build environment, ensuring reproducible and auditable OS image builds.

A high-level goal of the tool is to support two highly related use cases, and keep them as similar as possible:
- **Local development** ("test a kernel change" or experiment with OS configuration)
- **Production build system** orchestrated by an external tool (e.g., Jenkins, OpenShift Pipelines)

The container image itself is available on Quay.io at `quay.io/coreos-assembler/coreos-assembler` and includes all build dependencies bundled together — a self-contained OS build factory. See the [fedora-coreos-pipeline](https://github.com/coreos/fedora-coreos-pipeline) for an example production pipeline that uses COSA.

### Relationship to bootc

coreos-assembler is the established build pipeline for producing Fedora CoreOS and RHEL CoreOS images. The [bootc](../wiki/bootc.md) project represents the next-generation paradigm for transactional OS updates using standard OCI container images. COSA produces the OSTree commits and disk images that bootc-based systems consume, and the two projects are complementary — COSA is the factory, bootc is the delivery mechanism.

## Key Features

- **Containerized Build Environment** — Everything needed to build and test the OS comes encapsulated in one container image. The build pod runs with KVM device access for accelerating QEMU-based image operations and mounts host-level storage for build artifacts.
- **OSTree Commit Generation** — Composes package sets from RPM repositories into versioned, atomic OSTree commits using rpm-ostree. Builds are defined by a YAML manifest (`src/config/manifest.yaml`) specifying the package set and filesystem layout.
- **Disk Image Assembly** — Produces disk images for multiple target platforms including QCOW2 (QEMU), raw images (metal/bare-metal), ISO (live/installation), and cloud-specific images (AWS EC2, GCP, etc.).
- **Platform-Specific Image Building** — The `osbuild` command takes a bootable container and creates artifacts for specific platforms: `osbuild qemu`, `osbuild live`, `osbuild <platform>`. Supported platforms include all major cloud providers.
- **Live ISO Creation** — Builds live ISO images suitable for PXE boot, bare-metal provisioning, and rescue scenarios.
- **Comprehensive Testing** — Integration with `kola` for launching VM instances and running tests, and `kolet` as an agent that runs on test instances. This enables automated CI testing of OS images before release.
- **Cloud Provider Integration** — The `ore` tool provides interfaces for interacting with cloud providers for direct image upload and testing.
- **Update Stream Management** — Generates update metadata for over-the-air OS update delivery. The `plume` tool handles releasing Fedora CoreOS and Fedora Cloud updates.
- **CI Integration** — Designed for automated pipeline runs; used in Fedora CoreOS CI for continuous release builds. Runs inside OpenShift as an unprivileged pod on bare metal clusters with `/dev/kvm` mounted in.
- **Change Detection** — rpm-ostree has built-in intelligence: if RPM repositories haven't changed and the manifest is unmodified, running `cosa build` will not generate a new build. This is detectable via `readlink builds/latest`.

### Core CLI Tools

The COSA container bundles four primary CLI tools:

| Tool | Purpose |
|---|---|
| **`cosa`** | Entry point for the COSA container. Dispatches to sub-commands for init, build, osbuild, run, shell, fetch, clean, list, tag, sign, compress, and more. |
| **`kola`** | Test framework — launches VM instances and runs test suites against them. Supports QEMU-native and cloud-based test execution. |
| **`kolet`** | Test agent that runs on VM instances under kola's control, collecting test results and diagnostics. |
| **`ore`** | Cloud provider interface — manages images, instances, and networking across AWS, GCP, and other providers. |
| **`plume`** | Release tool — publishes Fedora CoreOS and Fedora Cloud updates, managing the update stream metadata. |

### cosa Sub-Commands

| Command | Description |
|---|---|
| `cosa init <git-url>` | Initialize a build directory, cloning the specified config repo into `src/config/` |
| `cosa build` | Build a bootable container (OSTree commit + base images) |
| `cosa osbuild <platform>` | Derive a bootable container into a platform-specific disk image |
| `cosa run` | Boot the built image in QEMU with root shell access |
| `cosa shell` | Get an interactive shell or run a command in the COSA container |
| `cosa fetch` | Fetch and import the latest packages from RPM repositories |
| `cosa clean` | Delete all build artifacts |
| `cosa list` | List builds available locally |
| `cosa kola` | Run tests with kola (VM-based integration tests) |
| `cosa tag` | Operate on tags in `builds.json` |
| `cosa sign` | Sign builds with RoboSignatory via fedora-messaging |
| `cosa compress` | Compress all images in a build |
| `cosa buildfetch` | Download a previous build from a remote source |
| `cosa buildupload` | Upload a build to S3-compatible storage |

### Operating System Concepts

The `kola` test framework also supports:
- `kola qemuexec` — Run a QEMU instance with custom Ignition config (for testing provisioning)
- `kola test` — Run automated test suites against a VM
- `kola spawn` — Launch test VMs in cloud environments

## Architecture

### Build Directory

coreos-assembler operates on a "build directory" (analogous to how git works on a repository). A build directory contains:

```
builds/                        ← Build artifacts organized by version
  ├── builds.json              ← Build manifest (list of builds, required because HTTP doesn't enumerate directories)
  ├── $version/                ← Individual build output
  │   ├── meta.json            ← Build metadata (OSTree commit, image info, version)
  │   ├── *.ostree.tar         ← OSTree commit archive
  │   └── *.qcow2 / *.raw / *.iso  ← Platform-specific disk images
src/
  ├── config/                  ← Cloned configuration repository
  │   ├── manifest.yaml        ← Package manifest (RPM selection)
  │   └── image.yaml           ← Image configuration (partition layout, filesystem)
  └── ...
tmp/                           ← Temporary build state
cache/                         ← Cached RPM and OSTree data
```

### Build Pipeline

1. **Init** — `cosa init <git-url>` clones a configuration repository into `src/config/`. The config repo contains `manifest.yaml` (defining the RPM package set) and `image.yaml` (defining disk image layout).
2. **Fetch** — `cosa fetch` downloads and imports the latest RPM packages based on the manifest.
3. **Build** — `cosa build` generates a new OSTree commit via rpm-ostree and produces a base disk image (QEMU by default). The output is structured under `builds/$version/` with `meta.json` capturing build metadata.
4. **Image customization** — `cosa osbuild <platform>` derives platform-specific images (QCOW2, raw, ISO, cloud images) from the bootable container.
5. **Testing** — `cosa run` boots the image in QEMU for manual testing; `cosa kola` runs automated test suites.
6. **Release** — Images are compressed, signed, and uploaded to distribution infrastructure using `plume`.

### Build Process Visualization

The build process follows a pipeline:

```
Manifest (YAML) → rpm-ostree compose → OSTree commit → supermin VM → Disk image
                          ↓
                   Change detection:
                   No changes → skip build
```

coreos-assembler ties together OSTree commits with disk images under a single build schema and version numbering. This is in contrast to rpm-ostree alone, which just generates OSTree commits without disk image management.

### Containerized Build Environment Setup

The COSA container requires:
- **`/dev/kvm`** — For QEMU-based image operations (nested virtualization)
- **`/dev/fuse`** — For FUSE filesystem operations (OSTree, composefs)
- **Privileged mode** — For loop device management and mounting (safe when run as non-root)
- **Persistent storage** — Build directory mounted at `/srv/` inside the container

The canonical `cosa` bash function wraps `podman run` with the necessary arguments, including user namespace mapping, device passthrough, and SELinux label disable.

### Supported Deployment Platforms

coreos-assembler can run on:
- **Local Linux** — With KVM access (bare metal or nested VM)
- **Bare metal cloud** — Packet, Hetzner, etc.
- **GCP nested virt** — Google Compute Platform with nested virtualization enabled
- **AWS** — `i3.metal` instances
- **IBM Bare Metal** — IBM Cloud bare metal servers
- **OpenShift/Kubernetes** — As an unprivileged pod on bare metal clusters with `/dev/kvm` mounted in (used by the Fedora CoreOS production pipeline)

### Custom OS Images

coreos-assembler can build custom operating system images derived from Fedora CoreOS. See the [Custom OS guide](https://github.com/coreos/coreos-assembler/blob/main/docs/custom.md) for documentation on forking the FCOS configuration and building custom variants.

## Usage Example

```bash
# Pull the COSA container
podman pull quay.io/coreos-assembler/coreos-assembler

# Create a build directory
mkdir fcos && cd fcos

# Define the cosa function (see docs/building-fcos.md for full definition)

# Initialize with Fedora CoreOS config
cosa init https://github.com/coreos/fedora-coreos-config

# Perform a build (generates OSTree commit + base images)
cosa build

# Build a platform-specific image
cosa osbuild qemu

# Run the resulting image in QEMU
cosa run

# Run automated tests
cosa kola run
```

## Related

- [[fedora-coreos-config]] — Configuration repository for Fedora CoreOS image definitions. This is the standard config repo used by `cosa init` and serves as the base for custom OS builds.
- [[bootc]] — Transactional OS updates using OCI container images (successor paradigm). COSA produces the images that bootc-based systems consume as updates.
- [[tank-os]] — Fedora bootc image for agent deployment. Built using COSA-derived tooling (bootc-image-builder) for creating bootc-based OS images.
- [[podman]] — Container runtime used to run coreos-assembler build pods. The `cosa` wrapper function invokes `podman run` with specific arguments for the build environment.
- [[coreos-assembler]] (this page) — Build pipeline for creating Fedora CoreOS and derivative images.
- [[tank-agent-os]] — Bootable agent OS image that follows the bootc/COSA pattern for immutable, atomically-updated deployment.
- [[secureblue]] — Hardened Fedora Atomic images built on coreos-adjacent tooling, providing security-focused OS variants.
- [[nix-podman-stacks]] — Alternative approach to OS image building using Nix, addressing similar goals as COSA for reproducibility.
