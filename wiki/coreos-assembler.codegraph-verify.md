---
name: coreos-assembler-codegraph-verify
tags: [coreos-assembler, codegraph-verify, fedora, coreos]
description: "Codegraph Verification: coreos-assembler — validating wiki claims against indexed source code"
source: sources/coreos-assembler/
---

# Codegraph Verification: coreos-assembler

**Date:** 2026-07-12

## Claim 1: COSA is a containerized build environment for Fedora CoreOS and RHEL CoreOS
- **Wiki says:** "The CoreOS Assembler (COSA) is a collection of tools packaged in a container used to build Fedora CoreOS and RHEL CoreOS systems. Everything needed to build and test the OS comes in one container image available at `quay.io/coreos-assembler/coreos-assembler`."

- **Source evidence:**
  - `README.md:1-7` — "The CoreOS Assembler (often abbreviated COSA) build environment. It is a collection of various tools used to build [Fedora CoreOS][fcos] style systems, including RHEL CoreOS. The goal is that everything needed to build and test the OS comes encapsulated in one (admittedly large) container."
  - `README.md:16-18` — "The container itself is available on [Quay.io](https://quay.io) at `quay.io/coreos-assembler/coreos-assembler`."
  - `Dockerfile` — Present in repo root confirming containerized build environment
  - `src/coreos-assembler.go` — Main entrypoint for the COSA tool
  - `go.mod:1` — `module github.com/coreos/coreos-assembler` — Go module declaration

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Tool suite includes cosa, kola, kolet, ore, and plume
- **Wiki says:** "COSA bundles multiple tools: `cosa` (entrypoint/dispatcher), `kola` (test harness), `kolet` (kola test agent), `ore` (cloud provider interface), and `plume` (release publishing)."

- **Source evidence:**
  - `README.md:19-31` — Lists: "`cosa`: entrypoint for the COSA container and dispatcher to other commands", "`kola`: for launching instances and running tests on them", "`kolet`: an agent for kola that runs on instances", "`ore`: for interfacing with cloud providers", "`plume`: for releasing Fedora CoreOS and Fedora Cloud"
  - `docs/cosa.md` — Full `cosa` command reference documenting `build`, `fetch`, `init`, `kola`, `list`, `osbuild`, `run`, `shell`, `virt-install`, and more
  - `docs/kola.md:1-14` — "Kola is a framework for testing software integration in CoreOS systems across multiple platforms." Lists supported platforms: QEMU, GCP, AWS, VMware VSphere, Packet, OpenStack.
  - `src/cmd-kola` — Kola test runner entrypoint
  - `docs/mantle/` — Mantle tool documentation directory (ore, plume)

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Build produces OSTree commits and disk images via `cosa build` and `cosa osbuild`
- **Wiki says:** "The `cosa build` command generates a new OSTree commit and optionally a QEMU image. The `cosa osbuild` command derives bootable disk images for specific platforms from the bootable container. The build directory contains multiple versioned builds with `meta.json` metadata."

- **Source evidence:**
  - `docs/design.md:14-24` — "coreos-assembler operates on a 'build directory', which can contain multiple builds. A build is a pairing of an OSTree commit (stored as `*-ostree.tar`) as well as an optional set of disk images."
  - `docs/design.md:26-27` — "The default for `cosa build` is to generate a new OSTree commit and a `qemu` image."
  - `docs/design.md:32-35` — "Physically, a coreos-assembler build is represented primarily by a new subdirectory in `builds/$version`, and inside that directory there's a `meta.json`."
  - `docs/cosa.md:29-31` — "By default, the `build` command will build an OS Bootable Container. The `osbuild` command will take the bootable container and create artifacts/images for various platforms."
  - `src/cmd-build:1-10` — Entrypoint: `Build bootable container (ostree) and image base artifacts using the container runtime (buildah).`
  - `src/cmd-osbuild` — OSBuild command implementation for platform-specific artifacts
  - `src/cmd-buildextend-metal` — Example of 20+ `buildextend-*` commands for platform-specific disk images
  - `docs/design.md:40-42` — "After a build is generated there are a variety of `buildextend-$x` commands, for example `buildextend-ec2` which can upload to AWS, and `buildextend-metal` which generates a bare metal disk image."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Multi-cloud platform support with 20+ `buildextend-*` commands
- **Wiki says:** "COSA supports building images for 20+ cloud and virtualization platforms including AWS, Azure, GCP, VMware, Hyper-V, QEMU, Metal, OpenStack, and others via `buildextend-*` and `osbuild` commands."

- **Source evidence:**
  - `src/cmd-buildextend-metal:1-20` — Declares `SUPPORTED_PLATFORMS` associative array with 24 platform entries: aliyun, applehv, aws, azure, azurestack, digitalocean, exoscale, gcp, hetzner, hyperv, ibmcloud, kubevirt, metal4k, metal, nutanix, nvidiabluefield, openstack, oraclecloud, proxmoxve, qemu, qemu-secex, vultr, live
  - Each platform has a corresponding `cmd-buildextend-<platform>` file in `src/` — confirmed for: aliyun, applehv, aws, azure, azurestack, digitalocean, exoscale, gcp, hetzner, hyperv, ibmcloud, kubevirt, metal, metal4k, nutanix, nvidiabluefield, openstack, oraclecloud, powervs, proxmoxve, qemu, qemu-secex, secex, virtualbox, vmware, vultr
  - `src/cmd-buildextend-metal:55-60` — `postprocess_artifact` function stores artifact metadata (path, sha256, size) in `meta.json`
  - `src/cmd-buildextend-metal:95-105` — `postprocess_qemu_secex` for IBM Z secure execution
  - `src/cmd-imageupload-aws`, `src/cmd-imageupload-azure`, `src/cmd-imageupload-gcp`, `src/cmd-imageupload-aliyun`, `src/cmd-imageupload-powervs` — Cloud upload commands for each supported platform

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Supermin-based QEMU virtual machine for disk image generation
- **Wiki says:** "COSA uses `supermin` to run a virtual machine that writes the ostree content along with the filesystem layout into a disk image, for cases where container-based image generation is insufficient."

- **Source evidence:**
  - `docs/design.md:61-63` — "However, coreos-assembler builds on top of rpm-ostree and also generates disk images. It uses supermin to run a virtual machine that runs code to write the ostree content along with the filesystem layout into a disk image."
  - `docs/design.md:66-67` — "If you want to force a build, use `coreos-assembler build --force`. A common reason to do this is when something changes in the tooling itself."
  - `src/cmd-build:12-14` — Direct build option: `--direct` flag: "Run buildah directly rather than within supermin." (implies supermin is the default)
  - `src/supermin-init-prelude.sh` — Supermin init script
  - `src/supermin-run` — Supermin runner for VM execution
  - `src/supermin-shell` — Supermin interactive shell for debugging
  - `src/libguestfish.sh` — libguestfish helper for disk image manipulation

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: RPM-based build with YAML manifest and dependency management
- **Wiki says:** "COSA builds are defined by a configuration manifest (`manifest.yaml`) specifying RPM packages, with dependency files for each architecture (`deps-x86_64.txt`, `deps-aarch64.txt`, etc.), and lockfiles for reproducible builds."

- **Source evidence:**
  - `docs/design.md:29-30` — "The OSTree commit data is generated via rpm-ostree, using `src/config/manifest.yaml`. Image configuration uses `src/config/image.yaml`."
  - `src/deps-x86_64.txt` — x86_64 build dependencies
  - `src/deps-aarch64.txt` — aarch64 build dependencies
  - `src/deps-ppc64le.txt` — ppc64le build dependencies
  - `src/deps-s390x.txt` — s390x build dependencies
  - `src/vmdeps-x86_64.txt`, `src/vmdeps-aarch64.txt`, `src/vmdeps-ppc64le.txt`, `src/vmdeps-s390x.txt` — VM-specific dependencies per architecture
  - `src/deps.txt` — Common cross-architecture dependencies
  - `src/vmdeps.txt` — Common VM dependencies
  - `src/build-deps.txt` — Build-time dependencies
  - `src/kola-container-image-deps.txt` — Kola test container image dependencies
  - `src/konflux-rpm-lockfile` — Konflux RPM lockfile for reproducible builds
  - `rpms.in.yaml`, `rpms.lock.yaml` — RPM lockfile inputs and locked outputs

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the CoreOS Assembler wiki have been verified against the source code:
- ✅ **Containerized build environment:** `quay.io/coreos-assembler/coreos-assembler` confirmed
- ✅ **Tool suite:** cosa, kola, kolet, ore, plume all confirmed with dedicated docs
- ✅ **Build pipeline:** OSTree commits + disk images via `cosa build` and `cosa osbuild`
- ✅ **Multi-cloud support:** 24 platform targets confirmed in `SUPPORTED_PLATFORMS`
- ✅ **Supermin virtualization:** Default VM-based disk image generation confirmed
- ✅ **RPM dependency management:** Architecture-specific and common dependency files confirmed

## Related

- [[coreos-assembler]] -- Main wiki entry
- [[fedora-coreos-config]] -- Fedora CoreOS configuration
- [[bootc]] -- Bootable container technology successor
- [[tank-os]] -- Fedora bootc appliance

## Cross-project

- [[bootc.codegraph-verify]] -- Bootable container technology that succeeds ostree
- [[podman.codegraph-verify]] -- Container runtime used by COSA builds
- [[fedora-coreos-config.codegraph-verify]] -- FCOS configuration consumed by COSA
