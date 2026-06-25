---
name: nix-podman-stacks-architecture
type: architecture
tags: [nix-podman-stacks, architecture, nix, home-manager, infrastructure-as-code, declarative, podman, self-hosted-stacks]
description: Architecture: nix-podman-stacks
---

# Architecture: nix-podman-stacks

**Source:** `sources/nix-podman-stacks/`
**Layer**: Container orchestration / deployment platform
**Paradigm**: Declarative Nix module system over rootless Podman Quadlets

## Overview

nix-podman-stacks is an architectural layer that translates declarative Nix configurations into running Podman containers managed by systemd --user (Quadlets). It sits between Home Manager (the Nix module system) and Podman (the container runtime), providing a cohesive abstraction for self-hosted service deployment.

The system is built on four architectural pillars:
1. **Nix Module Composition** -- how imports chain stack modules together
2. **Container Extension System** -- the `services.podman.containers` option extensions that enable integrations
3. **Cross-Stack Integration** -- how Traefik, Homepage, Monitoring, and Authelia auto-wire from stack enablement
4. **Secret Injection** -- how secrets flow from encrypted storage to container environments

---

## 1. Nix Module Composition

### Entry Point: `flake.nix`

The flake defines the project as a Nix module library:

```nix
outputs = { self, nixpkgs, home-manager, sops-nix, ... }: {
  homeModules = import ./modules/module_list.nix;
  # ...
};
```

The `homeModules` attribute contains:
- A flat map of every stack module keyed by name (`.traefik`, `.n8n`, etc.)
- A combined `nps` meta-module that imports all stack modules simultaneously

### Module Aggregation: `module_list.nix`

This file explicitly maps each stack name to its directory, then creates the `nps` meta-module:

```nix
modules = {
  settings = ./settings.nix;
  traefik = ./traefik;
  n8n = ./n8n;
  # ... 80+ more
};
nps = {
  imports = builtins.attrValues modules;
};
```

The `nps` module imports every single stack module. This means ALL stack options are available in the config namespace at all times, but only those with `enable = true` actually generate container configurations (via `lib.mkIf cfg.enable { ... }`).

### Module Chain

When a user imports `self.homeModules.nps`, the Nix module system evaluates this import chain:

```
settings.nix                          # Global nps.* options, base Podman config
  └─ imports: extension.nix           # Container option extensions
     └─ imports: (none)
traefik/default.nix                   # Traefik stack
  └─ imports: traefik/extension.nix   # Extends containers with traefik.* options
     └─ docker-socket-proxy/...
monitoring/default.nix               # Monitoring stack (Prometheus, Grafana, Loki, Alloy)
  └─ imports: monitoring/extension.nix # Extends containers with alloy.enable
     └─ docker-socket-proxy/...
homepage/default.nix                  # Homepage dashboard
  └─ imports: homepage/extension.nix  # Auto-populates services from containers
n8n/default.nix                       # n8n workflow engine
  └─ imports: mkAliases.nix           # Convenience aliases
# ... 80+ more modules
```

Each module's `imports` attaches extension modules that modify the `services.podman.containers` option type -- this is how the system maintains a single, extensible container config schema that every module can write to.

### Aliases via `mkAliases.nix`

The `mkAliases.nix` function creates two sets of convenience aliases for each stack:
- `nps.stacks.<name>.containers.<container>` -> `services.podman.containers.<container>`
- `nps.containers.<container>` -> `services.podman.containers.<container>`

These use Nix's `lib.doRename` to create transparent aliases that simplify user configuration.

---

## 2. The `nps.stacks` Configuration Namespace

Every stack module defines options under `nps.stacks.<name>`. The standard module pattern:

```nix
{ config, lib, ... }: let
  name = "mystack";
  cfg = config.nps.stacks.${name};
  storage = "${config.nps.storageBaseDir}/${name}";
in {
  imports = import ../mkAliases.nix config lib name [name];

  options.nps.stacks.${name} = {
    enable = lib.mkEnableOption name;
    # ... stack-specific options
  };

  config = lib.mkIf cfg.enable {
    services.podman.containers.${name} = {
      # ... Quadlet container config
    };
  };
};
```

### How Stack Modules Define Quadlet Files

Each stack module sets `services.podman.containers.<name>` to a Nix attribute set that Home Manager's podman module renders into a Quadlet `.container` file. The rendered file goes to `$HOME/.config/containers/systemd/<name>.container`, which systemd --user picks up.

Key container config attributes set by modules:

| Attribute | Quadlet Equivalent | Description |
|-----------|-------------------|-------------|
| `image` | `Image=` | Container image (pinned stable tags) |
| `volumeMap` | `Volume=` | Volume bind mounts (as attrset) |
| `environment` | `Environment=` | Env vars as native Nix types |
| `environmentFile` | `EnvironmentFile=` | File-based env vars |
| `ports` | `PublishPort=` | Port mappings |
| `network` | `Network=` | Podman network (created per-stack) |
| `exec` | `Exec=` | Container entrypoint |
| `user` | `User=` | Container user |
| `extraConfig` | raw Quadlet | Direct Quadlet key-value injection |
| `labels` | `Label=` | Docker labels (for Traefik/Homepage) |
| `autoUpdate` | `AutoUpdate=` | Registry-based auto-update |
| `socketActivation` | Socket unit | systemd socket activation |
| `traefik.*` | Label injection | Traefik Docker provider labels |
| `homepage.*` | Metadata | Homepage service registration |
| `alloy.*` | Label injection | Alloy log scraping label |

---

## 3. Cross-Stack Integration System

The most architecturally significant aspect of nix-podman-stacks is how enabling one stack automatically integrates with others through shared container option extensions and cross-module config writes.

### 3a. Traefik Integration

**Extension module**: `modules/traefik/extension.nix`

Every container in the system gains a `traefik` submodule option and a `port` option. When a container sets `traefik.name`:

1. **Router labels** are injected into the container's Docker labels:

```nix
"traefik.enable" = "true";
"traefik.http.routers.<name>.rule" = ''Host(`<subdomain>.<domain>`)'';
"traefik.http.routers.<name>.service" = "<name>";
"traefik.http.services.<name>.loadbalancer.server.port" = "<container-port>";
"traefik.http.routers.<name>.middlewares" = "private@file,public@file";
```

2. **Network attachment**: The container is added to Traefik's dedicated bridge network:

```nix
network = lib.mkIf enableTraefik [cfg.network.name];
```

3. **Service URL computation**: `traefik.serviceHost` and `traefik.serviceUrl` are read-only computed values that other modules can reference:

```nix
serviceUrl = "https://<subdomain>.<domain>"
```

The Traefik module itself (`modules/traefik/default.nix`) also performs cross-stack config writes:
- Writes to `nps.stacks.monitoring.prometheus.settings.scrape_configs` when `enablePrometheusExport` is set
- Writes to `nps.stacks.monitoring.grafana.dashboards` when Grafana dashboard options are enabled
- Configures `nps.stacks.crowdsec` for log collection and bouncer middleware
- Generates static config with Let's Encrypt, DNS challenge, geo-block plugin
- Generates dynamic config with `private` and `public` middleware chains

### 3b. Homepage Integration

**Extension module**: `modules/homepage/extension.nix`

Every container with a non-null `homepage.category` is automatically registered in the Homepage dashboard:

```nix
# In homepage/extension.nix:
mergedServices =
  builtins.foldl' (acc: c: let
    container = c.value;
    category = container.homepage.category;
    serviceName = container.homepage.name;
    serviceSettings = container.homepage.settings;
  in acc // { "${category}" = existingServices // {"${serviceName}" = serviceSettings}; };
  ) {} (lib.attrsToList homepageContainers);

config = {
  nps.stacks.homepage.services = mergedServices;
};
```

This means simply setting `homepage.category` on a container:
1. Populates the Homepage `services.yaml` configuration
2. Sets default `href` to the Traefik service URL
3. Sets default `server` and `container` for widget integration

The container's `homepage.settings` hash supports deep customization including widget configuration.

### 3c. Monitoring Integration

**Extension module**: `modules/monitoring/extension.nix`

Every container gains an `alloy.enable` option. When enabled, a Docker label `logging.alloy = "true"` is added, which Alloy's `discovery.docker` module uses to discover log sources.

The monitoring module also accepts contributions from other stacks via:

```nix
nps.stacks.monitoring = {
  prometheus.settings.scrape_configs = [ ... ];  # Stacks add scrape targets
  grafana.dashboards = [ ... ];                    # Stacks add dashboard JSONs
};
```

For example, the Blocky module:
```nix
nps.stacks.monitoring.prometheus.settings = lib.mkIf cfg.enablePrometheusExport {
  scrape_configs = [{
    job_name = "blocky";
    static_configs = [{targets = ["blocky:4000"];}];
  }];
};
nps.stacks.monitoring.grafana.dashboards = lib.mkIf cfg.enableGrafanaDashboard [
  ./grafana_dashboard.json
];
```

### 3d. Authelia / OIDC Integration

Several stacks support OIDC SSO through Authelia. The pattern:

1. Module defines `oidc.enable` and `oidc.clientSecretFile` / `oidc.clientSecretHash`
2. When enabled, the module writes to `nps.stacks.authelia.oidc.clients.<name>` to register the OIDC client
3. The module writes to `nps.stacks.lldap.bootstrap.groups.<name>` to create LDAP groups
4. Container env vars are set for OIDC discovery URL, client ID, roles

The `modules/authelia/options.nix` provides reusable option definitions for client secrets and hashes (supporting literals, `fromFile`, and auto-hashing via `toHash`).

---

## 4. Container Extension Options Detail

The core extension system (`modules/extension.nix`) adds these options to every `services.podman.containers.<name>`:

### `extraEnv` -- Flexible Environment Variables

Supports four value types:
- **Literal**: `KEY = "value"` -- direct string value
- **fromFile**: `KEY = { fromFile = "/path/secret"; }` -- reads file content at runtime
- **fromTemplate**: `KEY = { fromTemplate = "{{ env.GetEnv ... }}"; }` -- gomplate-rendered string
- **fromCommand**: `KEY = { fromCommand = "cat /secret"; }` -- command output captured at runtime

The system generates a PreStart systemd Exec script that:
1. Creates the appropriate environment files
2. Installs them with mode 600
3. For templates, loads all existing env vars before rendering with gomplate
4. For commands, evaluates them and captures output

### `volumeMap` -- Named Volume Attrset

Alternative to raw `volumes` list. Enables single-entry overrides:

```nix
# In module definition:
volumeMap.data = "${storage}/data:/data";
volumeMap.config = "${storage}/config:/config";

# User override in config:
nps.stacks.mystack.containers.mystack.volumeMap.data = "/custom/path:/data";
```

### `socketActivation` -- systemd Socket Activation

Creates systemd socket units that pass file descriptors to containers. Used by Traefik to listen on ports 80/443 directly (bypassing slirp4netns/pasta for real IP passthrough).

### `templateMount` -- Gomplate-Rendered Bind Mounts

Files are rendered from templates at container start via ExecStartPre, with optional `podman unshare chown`.

### `fileEnvMount` -- `_FILE` Pattern Automation

Combines a volume mount and env var into one declaration:

```nix
DB_PASSWORD_FILE = "/secrets/db-password.txt";
# Adds volume mount: /secrets/db-password.txt:/run/secrets/DB_PASSWORD_FILE
# Adds env var: DB_PASSWORD_FILE=/run/secrets/DB_PASSWORD_FILE
```

---

## 5. Secret Injection via sops-nix / agenix

Secrets flow through four layers:

```
sops-nix encrypted file
  -> Nix build: sops decrypts to /run/secrets/decrypted-path
    -> Container ExtraEnv: fromFile references the decrypted path
      -> Systemd ExecStartPre: reads file into environment file
        -> Quadlet EnvironmentFile: injected into container
```

The `ci_config.nix` contains all 80+ stacks enabled with dummy secrets for CI validation, serving as a comprehensive reference for every module's required options.

---

## 6. Flake Structure and Outputs

```nix
inputs = {
  nixpkgs.url = "github:nixos/nixpkgs/nixos-26.05";
  home-manager.url = "github:nix-community/home-manager/release-26.05";
  sops-nix.url = "github:Mic92/sops-nix";
  search.url = "github:NuschtOS/search";  # NixOS option search
};

outputs = {
  homeModules        # The nps meta-module and individual stack modules
  homeConfigurations.ci  # CI test configuration
  packages           # Documentation (mdbook) and option search index
  templates.default  # Starter template for new users
  formatter          # alejandra (Nix formatter)
};
```

---

## 7. Module Definition Patterns

### Simple Single-Container Stack

```nix
# modules/n8n/default.nix (simplified)
options.nps.stacks.n8n.enable = lib.mkEnableOption "n8n";
config = lib.mkIf cfg.enable {
  services.podman.containers.n8n = {
    image = "docker.n8n.io/n8nio/n8n:2.28.1";
    volumeMap.data = "${storage}/data:/home/node/.n8n:U";
    port = 5678;
    traefik.name = "n8n";
    homepage = { category = "General"; name = "n8n"; ... };
    glance = { ... };
  };
};
```

### Multi-Container Stack with Database

Each container in a stack shares the same `stack` attribute, which creates a shared Podman bridge network and systemd network unit:

```nix
# Pattern from streaming, paperless, and example modules
services.podman.containers = {
  app = {
    stack = "mystack";
    wantsContainer = ["db"];
    # ...
  };
  db = lib.mkIf (cfg.db.type == "postgres") {
    stack = "mystack";
    # ...
  };
};
```

### Integration-Contributing Stack

Stacks that support monitoring or OIDC write to cross-stack config namespaces:

```nix
config = lib.mkIf cfg.enable {
  services.podman.containers.app = { ... };

  # Cross-stack contributions:
  nps.stacks.monitoring.prometheus.settings.scrape_configs = [...];
  nps.stacks.monitoring.grafana.dashboards = [...];
  nps.stacks.authelia.oidc.clients.app = { ... };
  nps.stacks.lldap.bootstrap.groups = { app_admin = {}; ... };
};
```

---

## Summary: Architecture Diagram (Conceptual)

```
User Config (nps.stacks.*)
       │
       ▼
┌──────────────────────────────────────┐
│  nps Meta-Module (module_list.nix)   │
│  ┌── settings.nix (global options)  │
│  │    └── extension.nix (container  │
│  │         option extensions)       │
│  ├── traefik/                       │
│  │    └── extension.nix (traefik.*) │
│  ├── monitoring/                    │
│  │    └── extension.nix (alloy.*)   │
│  ├── homepage/                      │
│  │    └── extension.nix (homepage.*)│
│  ├── n8n, blocky, authelia, ...     │
│  └── 80+ more stack modules         │
└──────────┬───────────────────────────┘
           │
           ▼
services.podman.containers.<name>
           │
           ▼
Home Manager podman module
           │
           ▼
Quadlet files (~/.config/containers/systemd/*.container)
           │
           ▼
systemd --user services + sockets + networks
           │
           ▼
Rootless Podman containers
```

## Related

- [[nix-podman-stacks]] -- Project wiki overview and usage
- [[nix-podman-stacks-n8n]] -- n8n module integration details (key example stack)
