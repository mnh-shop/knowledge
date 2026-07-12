---
name: quadlet-nix
tags: [quadlet-nix, quadlet, nix, deployment, container, declarative]
description: "Nix-based generation and management of Podman Quadlet units"
source: sources/quadlet-nix/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Quadlet Nix

| Field | Value |
|---|---|
| **Origin** | [SEIAROTg/quadlet-nix](https://github.com/SEIAROTg/quadlet-nix) |
| **Source** | `sources/quadlet-nix/` |
| **Repomix** | `raw/quadlet-nix/quadlet-nix.xml` |
| **Codegraph** | `graphs/quadlet-nix/` |

## Overview

Quadlet Nix provides Nix-based tooling for generating and managing Podman Quadlet units declaratively via the NixOS module system and Home Manager. Started in August 2023 out of frustration with existing container management solutions, it offers a direct 1:1 mapping of Quadlet options into Nix language, allowing users to manage Podman containers, networks, pods, volumes, images, builds, and Kubernetes YAML units entirely within their Nix configuration — without acquiring domain knowledge in yet another tool. Prior knowledge of Podman and Quadlet continues to apply directly.

The project is designed to be simple, reliable, and comprehensive. It supports both rootful (via NixOS module) and rootless (via Home Manager module) configurations behind the same interface, with full Quadlet options support, typed and properly escaped. Generated Quadlet files are deployed to `/etc/containers/systemd/` on NixOS or `~/.config/containers/systemd/` under Home Manager, with systemd integration managed by the Nix activation process.

## Key Features

- **Full Quadlet Type Coverage** — Supports containers, networks, pods, volumes, images, builds (inlined Containerfile or git repository), and Kubernetes YAML (`.kube`) units
- **NixOS Module** — `virtualisation.quadlet` module with declarative options for all resource types, auto-enables Podman, integrates with systemd, and injects config-change detection hashes
- **Home Manager Module** — Same interface for rootless user-scoped containers with `xdg.configFile` deployment, systemd user service management, and Podman auto-update support
- **Cross-Resource References** — Type-safe `.ref` syntax for referencing other Quadlet resources (containers referencing networks, pods, volumes, images, builds) with automatic systemd dependency resolution
- **Build-Time Validation** — Assertions for container/pod name uniqueness, auto-escaping requirements, and docker-archive image tag completeness; warnings for configuration edge cases
- **Podman Auto-Update** — Built-in `autoUpdate` option with configurable calendar schedule, integrated as systemd timers (`podman-auto-update.timer`)
- **Rootless Under System Systemd** — Support for running rootless containers in system (not user) systemd via `rootlessConfig.uid`, with linger, subuid/subgid, and proper unit ordering
- **Raw Config Escape Hatch** — `rawConfig` option allows writing raw Quadlet text directly when Nix options are insufficient, while still benefiting from the rest of the module infrastructure (auto-start, refs)
- **Typed and Escaped Options** — Each Quadlet option is typed (string, bool, list, attrs) and properly escaped for the `.container` file format, with `autoEscape` (enabled by default) for correct quoting
- **Auto-Escaping** — Automatic enabling of appropriate quoting/escaping for Quadlet values that contain special characters, with build-time validation if disabled
- **Firewall Integration** — DNS-enabling helper recipes for Podman DNS on custom networks with `networking.firewall` rules
- **Debugging via Systemd** — Container logs accessible through `journalctl -u <service>` and status through `systemctl status <service>`, since Quadlet-managed containers are fully under systemd lifecycle management
- **`PodmanArgs`/`GlobalArgs` Escape Hatch** — Additional command-line arguments for options not yet covered by Quadlet, passed through to the underlying `podman run` / `podman network create` commands
- **`pkgs.dockerTools` Compatible** — Container images built with `pkgs.dockerTools` can be used via the `docker-archive:` transport

## Architecture

Quadlet Nix is structured as a set of composable Nix modules:

```
flake.nix              — Flake entry point exporting nixosModules and homeManagerModules
nixos-module.nix       — NixOS module: enables Podman, deploys Quadlet files to /etc/containers/systemd/
home-manager-module.nix — Home Manager module: deploys to ~/.config/containers/systemd/ (user services)
options.nix            — Core option definitions: mkOption, mkObjectOptions, mkTopLevelOptions, assertions
utils.nix              — Shared utilities: configToProperties, unitConfigToText, autoEscapeRequired, encoders
container.nix          — Container submodule with 70+ typed options (Image, Volume, Network, Pod, Environment, HealthCmd, etc.)
network.nix            — Network submodule with 20+ typed options (Driver, Subnet, Gateway, DNS, IPv6, Internal, etc.)
volume.nix             — Volume submodule
pod.nix                — Pod submodule
image.nix              — Image submodule (pull from registries or docker-archive)
build.nix              — Build submodule (Containerfile from text or git repo)
kube.nix               — Kubernetes YAML submodule
```

The module stack works as follows:

1. **Option Declaration** — `options.nix` defines `mkOption` that maps Nix attributes to Quadlet property names and CLI flags, plus `mkObjectOptions` for shared lifecycle options (autoStart, unitConfig, serviceConfig, rawConfig, ref)
2. **Submodule Definitions** — Each resource type (container.nix, network.nix, etc.) declares its typed options and generates Quadlet config text via `quadletUtils.unitConfigToText`
3. **Config Generation** — `utils.nix` converts Nix option values into Quadlet `.container`/`.network`/`.volume` file content with proper formatting and escaping
4. **Deployment** — The NixOS module writes files to the Nix store and symlinks them into `/etc/containers/systemd/`, while the Home Manager module uses `xdg.configFile` for user-level deployment
5. **Activation** — Systemd services are registered with `X-QuadletNixConfigHash` for change detection, and `wantedBy` targets determine start-on-boot behavior

### NixOS vs Home Manager

| Aspect | NixOS Module | Home Manager Module |
|---|---|---|
| Scope | System-wide (rootful) | User-level (rootless) |
| Config location | `/etc/containers/systemd/` | `~/.config/containers/systemd/` |
| Podman package | `config.virtualisation.podman.package` | `osConfig.virtualisation.podman.package` |
| Rootless support | Via `rootlessConfig.uid` | Default (user context) |
| Service target | `multi-user.target` | `default.target` |
| Auto-update timer | System-level timer | User-level timer |

## Usage

### Minimal NixOS Configuration

```nix
# flake.nix
{
  inputs.quadlet-nix.url = "github:SEIAROTg/quadlet-nix";
  outputs = { nixpkgs, quadlet-nix, ... }: {
    nixosConfigurations.machine = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        quadlet-nix.nixosModules.quadlet
      ];
    };
  };
}
```

```nix
# configuration.nix
{ config, ... }: {
  virtualisation.quadlet = let
    inherit (config.virtualisation.quadlet) volumes;
  in {
    containers.nginx = {
      containerConfig = {
        image = "docker.io/library/nginx:latest";
        publishPorts = [ "80:80" ];
        networks = [ "host" ];
        volumes = [ "${volumes.config.ref}:/etc/nginx" ];
      };
      serviceConfig.TimeoutStartSec = "60";
    };
    volumes.config.volumeConfig = {
      type = "bind";
      device = "/path/to/host/nginx-config";
    };
  };
}
```

### Resource Reference Syntax

Quadlet resources can cross-reference each other using the `.ref` attribute, producing correct Quadlet-native format names that systemd resolves into proper dependencies:

```nix
{ config, ... }: let
  inherit (config.virtualisation.quadlet) containers networks pods;
in {
  containers.app = {
    containerConfig = {
      image = "docker.io/myapp:latest";
      networks = [ networks.backend.ref ];
      pod = pods.app-pod.ref;
    };
    unitConfig = {
      Requires = [ containers.database.ref "network-online.target" ];
      After = [ containers.database.ref ];
    };
  };
};
```

## Related

- [[nix-podman-stacks]] — NixOS configurations for Podman container stacks
- [[podlet]] — CLI Quadlet generator (different approach, same goal)
- [[podman-quadlet]] — Official Quadlet reference
- [[podman]] — Container runtime for generated units
- [[quadlet-lsp]] — Language server for Quadlet files (complementary tooling)
