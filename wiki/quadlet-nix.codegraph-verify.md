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

## Claim-2: Full type coverage of all Quadlet options with typed escaping strategies

Every Quadlet property is exposed as a typed Nix option carrying the correct CLI flag, Quadlet property name, and encoder strategy. The encoder system (`utils.nix`) mirrors Podman's own `quadlet.go` parsing, supporting `scalar.legacy`, `scalar.raw`, `scalar.quotedEscaped` (via `builtins.toJSON`), and `scalar.quotedUnescaped` strategies — matching Podman's Lookup, LookupAllArgs, LookupAllStrv, and LookupAllKeyVal behavior.

**Source evidence:** `utils.nix:12-50` defines the four encoder types with the `makePassive` wrapper (`:15-22`), including the `scalar.raw` newline guard (`:29-37`) and the `scalar.quotedUnescaped` safety check (`:44-54`). `options.nix:7-33` defines `mkOption`, which captures `property`, `cli`, and `encoders` metadata per option. The NixOS module at `nixos-module.nix:38-42` writes out `/etc/containers/systemd/${p.ref}` with `text = p._configText`.

## Claim-3: Rootful (NixOS module) vs rootless (Home Manager) deployment

Rootful containers are deployed via the NixOS system module writing to `/etc/containers/systemd/`. Rootless containers are deployed via the Home Manager module with `xdg.configFile`, and the rootless pod/container modules work around the systemd restriction on unprivileged PID files by switching to `Type=simple` and polling for the infra conmon PID.

**Source evidence:** `nixos-module.nix:35-42` maps every object to `environment.etc."containers/systemd/${p.ref}"` with `text = p._configText`, `mode = "0600"`. `options.nix:216-230` adds `rootlessConfig.uid` via `applyRootlessOption` and `options.nix:236-254` (`applyRootlessConfig`) wires `serviceConfig.User`, `linger-users.service` Wants, and `user@<uid>.service` Requires/After. `pod.nix:244-269` implements the rootless hack: `Type=simple` (`:264`), an `ExecStart` that starts the pod and tails the `%t/%N.pid` file (`:265-267`), and `ExecStopPost` cleanup (`:268-272`). `container.nix:672-680` exposes `SubGIDMap`/`SubUIDMap` for rootless user/group mappings.

## Claim-4: Cross-referencing between resources using `.ref` syntax

Resources (containers, networks, pods, volumes, builds, images) can reference each other via a `.ref` attribute that produces the correct quadlet file name (e.g., `pods.foo.ref` → `foo.pod`). This enables Nix-level dependency tracking — cross-references resolve at config-generation time, producing valid quadlet `Network=`, `Pod=`, `Volume=` values.

**Source evidence:** `nixos-module.nix:37-41` generates `"containers/systemd/${p.ref}"` for each resource. `pod.nix:247` sets `ref = "${name}.pod"` (and `build.nix:285` sets `ref = "${name}.build"`). The NixOS module at `nixos-module.nix:45-52` creates a `linkFarm` of `etc/systemd/system/<svc>.service` symlinks so the NixOS activation process picks up generated services.

## Claim-5: Deep NixOS integration — change detection, systemd override, auto-update timer

Quadlet-nix integrates deeply with NixOS: it injects `X-QuadletNixConfigHash` to trigger restarts on config change, uses `overrideStrategy = "asDropin"` for systemd service overrides, sets `wantedBy` targets from `autoStart`, and provides a `virtualisation.quadlet.autoUpdate` option backed by a `podman-auto-update` systemd timer.

**Source evidence:** `nixos-module.nix:53-71` maps each object to a systemd service with `overrideStrategy = "asDropin"` (`:57`), `unitConfig.X-QuadletNixConfigHash = builtins.hashString "sha256" p._configText` (`:58`), and `wantedBy` derived from `_autoStart` (`:61-67`). Lines 73-80 configure `systemd.timers.podman-auto-update` with `OnCalendar` from `cfg.autoUpdate.calendar` (default `"*-*-* 00:00:00"` per `options.nix:187-191`). The drop-in services merge with `p._overrides`.

## Claim-6: Build submodule exposes a Containerfile path — no inline-text or git-context option

The build submodule (`build.nix`) supports building images from a Containerfile, but the Containerfile content must already exist on disk: the `buildConfig.file` option maps to the Quadlet `File=` property (a path), and `buildConfig.modules` maps to `ContainersConfModule`. There is no dedicated option for inlining Containerfile text, nor a dedicated git-context option — git-context builds (`git+https://...` or `https://...` URLs) only work by passing the repository URL through the `File=` passthrough.

**Source evidence:** `build.nix:100-106` defines `file` with `cli = "--file"`, `property = "File"`, `type = types.nullOr types.str`. `build.nix:57-63` defines `modules` with `property = "ContainersConfModule"`. The full option set in `build.nix:12-250` contains no `text`/`inline`/`context` option. Escape hatches: `podmanArgs` (`build.nix:170-177`, `PodmanArgs`) and `globalArgs` (`build.nix:115-122`, `GlobalArgs`). `build.nix:263` defaults the tag to `localhost/${name}` when unset.

## Claim-7: Build-time validation — autoEscape assertion and docker-archive FQDN requirement

Quadlet-nix validates configurations at build time: `autoEscape` defaults to true, and an assertion fails if any option value requires quoting while `autoEscape` is disabled. Images using the `docker-archive:` transport must specify the fully qualified name (FQDN) as a tag. Container/pod name uniqueness is also asserted.

**Source evidence:** `options.nix:174-176` sets `autoEscape` default `true`. The auto-escape assertion is at `options.nix:279-283` (`_autoEscapeRequired` is computed per-resource, e.g. `build.nix:284`). The docker-archive FQDN assertion is at `options.nix:265-289` (`nullImageArchiveTags` detection at `:262-267`, assertion at `:286-291`). The container/pod name-conflict assertion is at `options.nix:270-277`.

## Claim-8: Test suite — 13 configs plus two architecture directories

The `tests/` directory contains integration tests for every resource type plus escaping, overriding, raw config, health, and a `switch.nix` nixos-rebuild simulation, each evaluated on `aarch64-linux` and `x86_64-linux`.

**Source evidence:** `tests/` contains 13 test configs — `basic.nix`, `build.nix`, `container.nix`, `escaping.nix`, `health.nix`, `image.nix`, `kube.nix`, `network.nix`, `overriding.nix`, `pod.nix`, `raw.nix`, `switch.nix`, `volume.nix` — plus `flake.nix`, `README.md`, and architecture-specific `aarch64-linux/` and `x86_64-linux/` directories (each with its own `flake.nix`).
