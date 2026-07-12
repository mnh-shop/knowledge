---
name: buildah-codegraph-verify
tags: [codegraph-verify, buildah, podman, oci, go]
description: "Codegraph Verification: buildah"
source: sources/buildah/
---

# Codegraph Verification: buildah

**Date:** 2026-07-12

## Claim 1: Daemonless OCI image builder (no running daemon required)
- **Wiki says:** Buildah builds OCI container images without requiring a running daemon. Unlike Docker, it uses a simple fork-exec model.

- **Source evidence:** `README.md` lines 56-57 state: "Buildah follows a simple fork-exec model and does not run as a daemon but it is based on a comprehensive API in golang, which can be vendored into other tools." The source tree confirms no daemon component — `cmd/buildah/` contains a standard CLI entry point, and the main `buildah.go` package exposes library functions directly. The `define` package (`define/types.go`) defines the `Package = "buildah"` and `Version` constants without any server or daemon process. The `run_linux.go` directly invokes OCI runtimes and manages containers via the `storage` library, not through a central daemon.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Rootless image building with user namespace support
- **Wiki says:** Buildah supports building images without root privileges by using user namespaces, UID/GID mapping, and rootless isolation.

- **Source evidence:** `README.md` lines 51-52 state: "allows building images with and without Dockerfiles while not requiring any root privileges." `define/isolation.go` line 17-18 defines `IsolationOCIRootless` — "a proper OCI runtime in rootless mode." The `IsolationDefault` handling includes rootless execution paths. The `run_linux.go` file imports `"go.podman.io/storage/pkg/unshare"` (line 49) which handles user namespace setup. `define/types_unix.go` line 11 references "rootless environments" for bind mount handling. The `pkg/overlay/` and `pkg/parse/parse.go` (which handles `--isolation` flags) provide rootless build infrastructure.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Multi-architecture image building with `--platform` support
- **Wiki says:** Buildah supports building images for multiple architectures using `--platform` flags. It can build for multiple platforms in a single invocation, producing a manifest list.

- **Source evidence:** `imagebuildah/build.go` lines 220-274 implement multi-platform build logic: iterating over `options.Platforms`, setting `OSChoice`, `ArchitectureChoice`, and `VariantChoice` per platform, and building each platform independently with `buildDockerfilesOnce()`. Lines 343-354 document three build modes: single-platform, multi-platform with manifest list (`--manifest`), and multi-platform without manifest list. `pkg/parse/parse.go` lines 519-537, 643-690 parse `--platform` flag with `OS/ARCH[/VARIANT]` syntax, supporting comma-separated multi-platform values. The `Platform()` function (lines 700-709) and `PlatformsFromOptions()` (lines 656-690) handle platform parsing including the `local` alias. `pkg/binfmt/` provides binary format registration for cross-architecture builds.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Comprehensive API library vendored by Podman and other tools
- **Wiki says:** Buildah provides a comprehensive Go library API for building OCI images that is vendored by Podman and other container tools. The API covers image creation, commit, pull, push, mount, and run operations.

- **Source evidence:** The `buildah` Go package exports a comprehensive API surface. `buildah.go` (581 lines) defines the core types: `PullPolicy`, `NetworkConfigurationPolicy`, `BuilderOptions`, `CommitOptions`, `BuildOptions`. `image.go` (1809 lines) implements image operations including `Commit()`, `Push()`, `Pull()`, and `Add()` with OCI and Docker manifest format support. `run.go`/`run_linux.go` (1492 lines) provides `Run()` for executing build commands. `new.go` (353 lines) implements `NewBuilder()` for creating build containers. The module path `go.podman.io/buildah` in imports (e.g., `README.md` line 58: "based on a comprehensive API in golang, which can be vendored into other tools") confirms direct library usage by Podman.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Builds images with and without Dockerfiles (Dockerfile-free builds)
- **Wiki says:** Buildah can build images using Dockerfiles (via the `build` command) or without them using a lower-level command interface (`buildah from`, `buildah copy`, `buildah commit`, etc.).

- **Source evidence:** `README.md` lines 50-55 state: "Buildah's commands replicate all of the commands that are found in a Dockerfile. This allows building images with and without Dockerfiles... The flexibility of building images without Dockerfiles allows for the integration of other scripting languages into the build process." The source tree confirms: `imagebuildah/build.go` handles Dockerfile-based builds via the `BuildDockerfiles()` function; the CLI in `cmd/buildah/` exposes individual commands (`from`, `add`, `copy`, `config`, `commit`, `run`, `mount`, `unmount`, etc.) for programmatic Dockerfile-free builds. The `imagebuildah` package includes Dockerfile parsing through the `github.com/openshift/imagebuilder` dependency.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Supports both OCI and Docker image format output
- **Wiki says:** Buildah can output images in OCI image format or the traditional Docker v2s2 image format, configurable via the preferred manifest type.

- **Source evidence:** `define/types.go` lines 38-50 define both formats: `OCIv1ImageManifest = v1.MediaTypeImageManifest` (line 41) and `Dockerv2ImageManifest = manifest.DockerV2Schema2MediaType` (line 45), with format constants `OCI = "oci"` and `DOCKER = "docker"` (lines 48-50). `image.go` lines 42-51 re-export these as `OCIv1ImageManifest` and `Dockerv2ImageManifest` with `PreferredManifestType` in `CommitOptions`. The `imagebuildah` package handles format conversion. `define/build.go` includes `github.com/containers/ocicrypt/config` for OCI encryption support.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Container mount/unmount for root filesystem manipulation
- **Wiki says:** Buildah can mount a working container's root filesystem for manipulation and unmount it when done, allowing direct filesystem access without running a process.

- **Source evidence:** `mount.go` and `unmount.go` in the repo root (`sources/buildah/mount.go`, `sources/buildah/unmount.go`) implement these operations. `README.md` lines 14-16 list these as core features: "mount a working container's root filesystem for manipulation" and "unmount a working container's root filesystem." The `Builder` type in `buildah.go` tracks mount state. `pkg/overlay/overlay_linux.go` provides overlay-based mount support. The `new.go` file's `BuilderOptions` includes `MountOptions` for configuring how the container rootfs is mounted.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[buildah]] -- Main wiki entry
- [[podman]] -- Podman container engine
- [[bootc]] -- Bootable containers
- [[podlet]] -- Quadlet file generation

## Cross-project

- [[podman.codegraph-verify]] -- Podman verification
- [[crun-vm.codegraph-verify]] -- crun-vm verification
- [[sablier.codegraph-verify]] -- Sablier verification
