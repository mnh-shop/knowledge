---
name: nix-podman-stacks-n8n
type: integration
tags: [nix-podman-stacks, integration, nix, home-manager, infrastructure-as-code, declarative, podman, self-hosted-stacks]
description: "Integration: nix-podman-stacks n8n Module"
---

# Integration: nix-podman-stacks n8n Module

**Source**: `sources/nix-podman-stacks/modules/n8n/default.nix`

## Overview

nix-podman-stacks ships a dedicated **n8n module** (`modules/n8n/`) that provides declarative deployment of the n8n workflow automation engine using rootless Podman Quadlets managed through Home Manager. This module integrates n8n into the full nix-podman-stacks ecosystem: Traefik reverse proxy, Homepage dashboard, Grafana monitoring, Authelia OIDC, and Alloy log collection -- all activated by setting a single option.

## Module Definition

**File**: `sources/nix-podman-stacks/modules/n8n/default.nix`

The module is minimal (48 lines), reflecting n8n's simple deployment model (single container, SQLite database, env-var configuration):

```nix
{ config, lib, ... }: let
  name = "n8n";
  storage = "${config.nps.storageBaseDir}/${name}";
  cfg = config.nps.stacks.${name};

  category = "General";
  description = "Workflow Automation";
  displayName = "n8n";
in {
  imports = import ../mkAliases.nix config lib name [name];

  options.nps.stacks.${name}.enable = lib.mkEnableOption name;

  config = lib.mkIf cfg.enable {
    services.podman.containers.${name} = {
      image = "docker.n8n.io/n8nio/n8n:2.28.1";
      volumeMap.data = "${storage}/data:/home/node/.n8n:U";
      environment = {
        DB_TYPE = "sqlite";
        GENERIC_TIMEZONE = config.nps.defaultTz;
        N8N_EDITOR_BASE_URL = cfg.containers.${name}.traefik.serviceUrl;
        N8N_DIAGNOSTICS_ENABLED = false;
      };
      port = 5678;
      traefik.name = name;
      homepage = {
        inherit category;
        name = displayName;
        settings = { inherit description; icon = "n8n"; };
      };
      glance = {
        inherit category description;
        name = displayName;
        id = name;
        icon = "di:n8n";
      };
    };
  };
};
```

## Configuration Options

The n8n module exposes a single option:

| Option | Type | Description |
|--------|------|-------------|
| `nps.stacks.n8n.enable` | bool | Enable the n8n stack |

That's it -- everything else is derived automatically from the nix-podman-stacks integration system.

### Derived (Implicit) Configuration

Because of the framework's cross-module extensions, enabling n8n automatically configures:

**Traefik integration** (via `modules/traefik/extension.nix`):
- Docker labels are injected onto the n8n container: `traefik.enable=true`, `traefik.http.routers.n8n.rule=Host(`n8n.<domain>`)`, etc.
- n8n is added to Traefik's `traefik-proxy` Podman bridge network
- `N8N_EDITOR_BASE_URL` is automatically set to the Traefik URL (`https://n8n.<domain>`)
- The `private` middleware chain is applied (internal IPs only by default; set `expose = true` to allow public access)

**Homepage integration** (via `modules/homepage/extension.nix`):
- n8n appears in the "General" category on the Homepage dashboard
- Service name: "n8n" (displayName)
- Description: "Workflow Automation"
- Icon: "n8n" (from dashboard-icons)
- Default `href`: Traefik service URL

**Glance integration**:
- n8n appears in the Glance dashboard if enabled
- Same metadata as Homepage

**Alloy log collection** (via `modules/monitoring/extension.nix`):
- By default, n8n does NOT set `alloy.enable = true`. To enable log shipping to Loki, a user would need to add `alloy.enable = true` to the n8n container config via `services.podman.containers.n8n.alloy.enable = true;` or through the alias `nps.stacks.n8n.containers.n8n.alloy.enable = true;`

**Monitoring**:
- No Prometheus metrics export is configured by default (n8n doesn't expose /metrics natively)
- No Grafana dashboards are auto-provisioned

## How It Configures the n8n Container

### Container Image
- `docker.n8n.io/n8nio/n8n:2.28.1` (pinned stable tag; Renovate keeps it updated)
- Official n8n registry, not Docker Hub

### Volume Configuration
```nix
volumeMap.data = "${storage}/data:/home/node/.n8n:U";
```
- Persistent storage at `$STORAGE_BASE_DIR/n8n/data/` mapped to `/home/node/.n8n`
- The `:U` suffix tells Podman to chown the host directory to the container's UID (1000) automatically
- This is necessary because n8n runs as UID/GID 1000 inside the container

### Environment Variables
```nix
environment = {
  DB_TYPE = "sqlite";
  GENERIC_TIMEZONE = config.nps.defaultTz;
  N8N_EDITOR_BASE_URL = cfg.containers.${name}.traefik.serviceUrl;
  N8N_DIAGNOSTICS_ENABLED = false;
};
```

| Variable | Value | Purpose |
|----------|-------|---------|
| `DB_TYPE` | `sqlite` | n8n stores workflow data in SQLite (default; no external DB) |
| `GENERIC_TIMEZONE` | from `nps.defaultTz` | Timezone for n8n scheduler |
| `N8N_EDITOR_BASE_URL` | `https://n8n.<domain>` | Required for webhook URL generation and CORS |
| `N8N_DIAGNOSTICS_ENABLED` | `false` | Opt-out of n8n telemetry |

Notably absent: no `N8N_ENCRYPTION_KEY`, no database credentials, no external PostgreSQL configuration. The module uses the simplest possible n8n configuration.

### Port
- Internal port `5678` (n8n's default HTTP port)

### Traefik Service Host
- Automatically computed as `n8n.<traefik-domain>` (e.g., `n8n.example.com`)

## How to Enable

### Minimal Configuration
```nix
{ ... }: {
  nps.stacks.n8n.enable = true;
}
```

### With Public Exposure (External Access)
```nix
{ ... }: {
  nps.stacks = {
    n8n.enable = true;
    # If n8n needs to be accessible from the internet:
    nps.stacks.n8n.containers.n8n.expose = true;
  };
}
```

### Full Config with Traefik and Monitoring
```nix
{ config, ... }: {
  nps = {
    hostIP4Address = "192.168.1.100";
    storageBaseDir = "${config.home.homeDirectory}/stacks";
    externalStorageBaseDir = "/mnt/data";
    defaultTz = "America/New_York";

    stacks = {
      traefik = {
        enable = true;
        domain = "example.com";
      };
      n8n.enable = true;
      homepage.enable = true;
      monitoring = {
        enable = true;
        grafana.enable = true;
      };
      # Also enable log shipping for n8n
    };
  };
  # Optionally enable log shipping for n8n
  services.podman.containers.n8n.alloy.enable = true;
}
```

## How This Fits with the Monitoring Stack

By default, n8n does not export Prometheus metrics or have a Grafana dashboard. However:

- **Log shipping**: Adding `alloy.enable = true` to the n8n container enables Alloy to scrape its Docker logs and ship them to Loki for log exploration in Grafana
- **Manual metrics**: If n8n exposes metrics (e.g., via an external metrics exporter sidecar), you can add Prometheus scrape configs via `nps.stacks.monitoring.prometheus.settings.scrape_configs`

## Gaps and Overlaps with Our Existing n8n Knowledge

### This Module Provides
- Declarative, reproducible n8n deployment via Nix
- Automatic Traefik reverse proxy with Let's Encrypt TLS
- Automatic Homepage dashboard registration
- Standardized storage paths and volume management
- Auto-update via Podman's registry watcher (`autoUpdate = "registry"`)

### This Module Does NOT Provide (Gaps)
- **No external PostgreSQL support** -- hardcoded to SQLite. Our existing n8n knowledge for production deployments recommends PostgreSQL. To add PostgreSQL: set `N8N_DB_TYPE=postgresdb`, `N8N_DB_HOST`, `N8N_DB_PORT`, `N8N_DB_DATABASE`, `N8N_DB_USER`, `N8N_DB_PASSWORD` in `extraEnv`.
- **No encryption key** -- `N8N_ENCRYPTION_KEY` is not set. For production, an encryption key should be injected via `extraEnv` or `services.podman.containers.n8n.extraEnv.N8N_ENCRYPTION_KEY.fromFile = <path>;`.
- **No OIDC/SSO** -- unlike many other stacks in nix-podman-stacks, the n8n module does not have built-in OIDC support. Our existing n8n setup uses Authelia for SSO; this would need to be added manually.
- **No multi-instance** -- single container only. No support for queue mode (Redis + multiple workers).
- **No webhook tunnel** -- `N8N_WEBHOOK_TUNNEL_URL` is not configured.
- **No custom nodes** -- modules are not installed; the container runs the base image only.

### How to Bridge the Gaps

For a production n8n deployment that matches our existing knowledge, extend the module config:

```nix
services.podman.containers.n8n = {
  # Add PostgreSQL support
  extraEnv = {
    DB_TYPE = "postgresdb";
    DB_POSTGRESDB_HOST = "n8n-db";
    DB_POSTGRESDB_PORT = 5432;
    DB_POSTGRESDB_DATABASE = "n8n";
    DB_POSTGRESDB_USER = "n8n";
    DB_POSTGRESDB_PASSWORD.fromFile = config.sops.secrets."n8n/db_password".path;
    N8N_ENCRYPTION_KEY.fromFile = config.sops.secrets."n8n/encryption_key".path;
  };
  wantsContainer = ["n8n-db"];

  # Enable log shipping
  alloy.enable = true;
};

# Postgres sidecar
services.podman.containers."n8n-db" = {
  image = "docker.io/postgres:18";
  stack = "n8n";
  volumeMap.data = "${config.nps.storageBaseDir}/n8n/postgres:/var/lib/postgresql/data";
  extraEnv = {
    POSTGRES_DB = "n8n";
    POSTGRES_USER = "n8n";
    POSTGRES_PASSWORD.fromFile = config.sops.secrets."n8n/db_password".path;
  };
};
```

## Summary

The nix-podman-stacks n8n module provides a quick-start, single-flag deployment path for n8n with automatic Traefik, Homepage, and Glance integration. It is best suited for non-production or development use cases. For production n8n deployments, the module serves as a foundation that should be extended with PostgreSQL, encryption keys, and optionally OIDC and custom nodes -- following the same patterns used by more complex modules like `paperless`, `immich`, or `mealie` in the same repository.

## Related

- [[nix-podman-stacks]] -- Project wiki overview
- [[nix-podman-stacks-architecture]] -- Nix module system and cross-stack integration architecture
