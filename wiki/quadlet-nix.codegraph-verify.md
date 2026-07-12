---
title: "quadlet-nix — CodeGraph Verification"
tags: [quadlet-nix, codegraph-verify, quadlet, nix]
related: [[quadlet-nix]], [[nix-podman-stacks]], [[podlet]], [[quadlet]]
verification_date: 2026-07-12
verified_by: CodeGraph & manual source audit
source_ref: sources/quadlet-nix/
graph_ref: graphs/quadlet-nix/
---

# quadlet-nix — CodeGraph Verification

## Claim-1: NixOS + Home Manager module for declaring Podman Quadlets in Nix

Quadlet-nix provides both a NixOS module (`nixosModules.quadlet`) and a Home Manager module (`homeManagerModules.quadlet`) that allow users to declare Podman containers, networks, pods, volumes, builds, images, and kube resources using Nix option types instead of writing raw quadlet files. Configuration goes under `virtualisation.quadlet`.

**Source evidence:** `flake.nix:7-8` exports `nixosModules.quadlet = ./nixos-module.nix` and `homeManagerModules.quadlet = ./home-manager-module.nix`. `nixos-module.nix:23` sets `options.virtualisation.quadlet = quadletOptions.mkTopLevelOptions {}`. `home-manager-module.nix` mirrors the interface. Container and pod options are typed Nix options in `container.nix` (812 lines) and `pod.nix` (300 lines).

## Claim-2: Full type coverage of all Quadlet options with proper escaping

Every Quadlet property is exposed as a typed Nix option with the correct CLI flag, Quadlet property name, and encoder strategy. The encoder system (`utils.nix`) mirrors Podman's own `quadlet.go` parsing, supporting `scalar.legacy`, `scalar.raw`, `scalar.quotedEscaped` (via `builtins.toJSON`), and `scalar.quotedUnescaped` strategies — matching Podman's Lookup, LookupAllArgs, LookupAllStrv, and LookupAllKeyVal behavior.

**Source evidence:** `utils.nix:12-50` defines encoder types with `makePassive` wrapper. `container.nix` uses these across 812 lines for all container options. `pod.nix` uses them for pod options. `options.nix:7-33` defines `mkOption` that captures `property`, `cli`, and `encoders` metadata for each option. The NixOS module at `nixos-module.nix:38-42` writes out `/etc/containers/systemd/${p.ref}` with `text = p._configText`.

## Claim-3: Supports both rootful (NixOS module) and rootless (Home Manager) deployment

Rootful containers are deployed via the NixOS system module writing to `/etc/containers/systemd/`. Rootless containers are deployed via the Home Manager module with automatic `PIDFile` management — the rootless pod/container modules work around systemd restriction on PID files by switching to `Type=simple` and polling for the infra conmon PID.

**Source evidence:** `container.nix` and `pod.nix` both use `applyRootlessOption` from `options.nix` to add `rootlessConfig`. `pod.nix:244-269` implements the rootless hack: `Type=simple`, `ExecStart` polls for `%t/%N.pid`, and `ExecStopPost` cleans up. `home-manager-module.nix` provides the rootless path. `nixos-module.nix` handles rootful via `environment.etc`. The README shows both rootful (flake.nix with `nixosModules.quadlet`) and rootless (with `home-manager` and `homeManagerModules.quadlet`) examples.

## Claim-4: Cross-referencing between resources using `.ref` syntax

Resources (containers, networks, pods, volumes, builds, images) can reference each other via a `.ref` attribute that produces the correct quadlet file path (e.g., `networks.internal.ref` → `internal.network`). This enables Nix-level dependency tracking — cross-references are resolved at config-generation time, ensuring valid quadlet `Network=`, `Pod=`, `Volume=` values.

**Source evidence:** `nixos-module.nix:37-41` generates `"containers/systemd/${p.ref}"` for each resource. The README shows `networks.internal.ref` and `pods.foo.ref` in `nginx.containerConfig`. `pod.nix:247` sets `ref = "${name}.pod"`. `options.nix` provides `mkTopLevelOptions` which generates `.ref` for each resource type. The NixOS module at line 46-52 creates `linkFarm` symlinks so systemd can find generated services.

## Claim-5: NixOS integration with change detection, systemd override, and auto-update

Quadlet-nix integrates deeply with NixOS: it writes configs to `/etc/containers/systemd/`, creates symlinks via `systemd.packages` for activation script detection, injects `X-QuadletNixConfigHash` to trigger restarts on config change, supports `overrideStrategy = "asDropin"` for systemd service overrides, and provides a `virtualisation.quadlet.autoUpdate` option with a systemd timer for Podman auto-update.

**Source evidence:** `nixos-module.nix:53-71` maps each object to a systemd service with `overrideStrategy = "asDropin"`, `X-QuadletNixConfigHash` (line 58), and `wantedBy`. Lines 73-80 configure `systemd.timers.podman-auto-update` with configurable `OnCalendar`. Line 45-52 creates `systemd.packages` with `linkFarm` for symlinks. The README documents `autoUpdate.enable` and `autoUpdate.calendar`.

## Claim-6: Comprehensive test suite covering all resource types

The `tests/` directory contains integration tests for containers, networks, pods, volumes, builds, images, kube, healthchecks, escaping, overriding, raw config, basic operations, and `switch.nix` (nixos-rebuild simulation). Tests suggest Nix build-level validation for every resource type, ensuring option types and config generation produce valid quadlet files.

**Source evidence:** `tests/` contains: `basic.nix`, `container.nix`, `network.nix`, `pod.nix`, `volume.nix`, `build.nix`, `image.nix`, `kube.nix`, `health.nix`, `escaping.nix`, `overriding.nix`, `raw.nix`, `switch.nix`, `flake.nix`, and architecture-specific `aarch64-linux/` and `x86_64-linux/` directories. The `README.md` at tests/ would contain test documentation.
