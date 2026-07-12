# Quadlets Deployment Assets Index

This directory contains deployable Quadlet files and bootc scripts from multiple source repositories for use in tank-os and tank-agent-os deployments.

## Per-Stack Architecture Descriptions

### AI Stack
The AI stack provides a complete self-hosted AI inference and interface pipeline. **Ollama** serves as the LLM inference engine (via pod `ollama.pod`), **Open WebUI** provides a ChatGPT-compatible interface, **Valkey** handles caching and session state for WebUI, **Edge TTS** enables text-to-speech, and **Tika** provides document parsing for RAG pipelines. The stack is designed to run as a cohesive unit — the `ollama.pod` groups Ollama and its network, with Open WebUI connecting to it as a dependent container.

### Bluesky PDS
The Bluesky Personal Data Server stack runs a full AT Protocol PDS behind a **Caddy** reverse proxy. Caddy terminates TLS and handles ACME certificate provisioning. The PDS container stores user data, repository, and account state. Three dedicated volumes separate Caddy configuration, SSL data, and access logs for clean management.

### Inlets Ghost
Inlets provides secure HTTP tunnels for exposing local services to the internet. The `.kube` file wraps a Kubernetes-style deployment that runs an inlets-ghost exit node. License and token templates (Jinja2) are provided for dynamic secret injection at deploy time.

### LocalStack
LocalStack emulates AWS cloud APIs (S3, DynamoDB, SQS, Lambda, etc.) locally for development and testing. A single container with a persistent volume stores emulated service state across restarts.

### MinIO & Prometheus
**MinIO** provides S3-compatible object storage for agent artifacts, backups, and media. **Prometheus** scrapes metrics from MinIO and other services. MinIO and Prometheus share a dedicated network for internal metric collection without exposing Prometheus externally.

### PostgreSQL
A standard PostgreSQL 16+ database container with template-based configuration. The `.container.j2` Jinja2 template allows customization of image tag, resource limits, and environment variables. The `.env` file provides default credentials and database name.

### Redpanda
Redpanda is a Kafka-compatible event streaming platform. Two containers run in parallel: **redpanda-server** (the broker) and **redpanda-console** (a Web UI for management). They share a network for internal communication. A persistent volume stores broker data.

### Splunk
Splunk provides log aggregation, search, and monitoring. A single container with a persistent volume stores all indexed data. Configured via environment variables for admin credentials and license.

### Syncthing
Syncthing provides peer-to-peer file synchronization across devices. A single container with bind mounts to host directories enables agent workspace synchronization across machines.

### ValKey
Standalone Valkey (a Redis-compatible key-value store) for caching and session state. A persistent volume ensures cache data survives restarts. Used by other stacks (AI stack, Open WebUI) as a shared dependency.

### Watchtower
Watchtower automatically monitors running containers and updates their images when new versions are published. It is a cross-stack utility that depends on the Docker/Podman socket being mounted.

### Zerotier One
Zerotier One provides software-defined networking, allowing containers to join a global virtual LAN. A persistent volume stores the node identity and configuration across restarts.

### Zot Registry
Zot is a lightweight OCI container registry for storing and distributing container images. A persistent volume holds the image layer storage. Useful for local image distribution in air-gapped or edge deployments.

## Dependency Ordering

Quadlet files within each stack have implicit and explicit startup ordering via systemd dependencies (`After=`, `BindsTo=`, `Requires=`). The general rules:

| Dependency Type | Directive | Behavior |
|-----------------|-----------|----------|
| Hard dependency | `BindsTo=%N.volume` | Container stops if volume unit fails |
| Network dependency | `Network=%N.network` | Container attaches to named network |
| Pod membership | `Pod=%N.pod` | Container joins systemd pod |
| Startup ordering | `After=network-online.target` | Container starts after network is available |

### Per-Stack Dependency Graph

| Stack | Dependency Order | Notes |
|-------|-----------------|-------|
| **AI Stack** | Volume(s) → Network → Pod → Containers → Dependent containers | `ollama.volume` → `ollama.network` → `ollama.pod` → `ollama.container`; `open-webui.container` depends on both `ollama` and `valkey` |
| **Bluesky PDS** | Volume(s) → Network → Containers | `pds_data.volume` + `pds_logs.volume` → `pds.network` → `pds.container`; `caddy_config.volume` + `caddy_data.volume` + `caddy_logs.volume` → `caddy.container` |
| **Redpanda** | Volume → Network → Containers | `redpanda.volume` → `redpanda.network` → `redpanda-server.container` + `redpanda-console.container` (parallel) |
| **MinIO & Prometheus** | Network → Containers (parallel) | `minio.network` → `minio.container` + `prometheus.container` (parallel) |
| **All single-container** | Volume (if any) → Container | e.g., `zot-registry.volume` → `zot-registry.container` |

### Cross-Stack Dependencies

| Consumer Stack | Depends On | Reason |
|----------------|-----------|--------|
| AI Stack (Open WebUI) | ValKey | Session caching |
| All HTTP stacks | Watchtower (optional) | Auto-updates |
| All exposed stacks | Zerotier One (optional) | Network connectivity |

## Port Mapping Reference

The following ports are used by Quadlet stacks. Stacks that bind to the same port cannot run simultaneously on the same host without modification.

| Port(s) | Stack | Service | Transport | Bind Address | Notes |
|---------|-------|---------|-----------|--------------|-------|
| 11434 | AI Stack | Ollama | TCP | `127.0.0.1` | LLM inference API |
| 8080 | AI Stack | Open WebUI | TCP | `127.0.0.1` | Web chat interface |
| 5002 | AI Stack | Edge TTS | TCP | `127.0.0.1` | Text-to-speech API |
| 9998 | AI Stack | Tika | TCP | `127.0.0.1` | Document parsing |
| 6379 | AI Stack / ValKey | Valkey | TCP | `127.0.0.1` | Key-value cache |
| 80, 443 | Bluesky PDS | Caddy | TCP | Host IP (public) | Reverse proxy (HTTP/HTTPS) |
| 3000 | Bluesky PDS | PDS | TCP | `127.0.0.1` | AT Protocol server |
| 9000 | MinIO | MinIO API | TCP | `127.0.0.1` | S3-compatible object storage |
| 9001 | MinIO | MinIO Console | TCP | `127.0.0.1` | Web management UI |
| 9090 | Prometheus | Prometheus | TCP | `127.0.0.1` | Metrics endpoint |
| 5432 | PostgreSQL | PostgreSQL | TCP | `127.0.0.1` | Database server |
| 8081 | Redpanda | Console | TCP | `127.0.0.1` | Kafka Web UI |
| 9092 | Redpanda | Broker (SASL) | TCP | `127.0.0.1` | Kafka message broker |
| 8008 | Redpanda | Broker (admin) | TCP | `127.0.0.1` | Admin REST API |
| 8089 | Splunk | Splunk Web | TCP | `127.0.0.1` | Log management UI |
| 22000 | Syncthing | Sync TCP | TCP | `127.0.0.1` | File sync data |
| 21027 | Syncthing | Discovery | UDP | `0.0.0.0` | LAN discovery |
| 4566 | LocalStack | LocalStack | TCP | `127.0.0.1` | AWS API emulation |
| 9999 | Zot Registry | Zot | TCP | `127.0.0.1` | OCI container registry |
| 9994 | Zerotier One | ZeroTier | TCP | `127.0.0.1` | Controller API |

## Volume Mount Conventions

All persistent storage follows these conventions for consistency across stacks.

### Volume Naming Convention

```
<stack-name>-<service-name>
```

Examples: `ollama`, `open-webui`, `pds_data`, `caddy_data`, `redpanda`, `zot-registry`.

### Volume Driver and Options

All volumes use the default `local` driver unless otherwise specified:

```ini
[Volume]
VolumeName=<name>
# Optional: Driver=local
# Optional: Label=app=<stack>
```

### Volume Mount Paths by Service

| Stack | Service | Volume Name | Container Mount Path | Purpose |
|-------|---------|-------------|---------------------|---------|
| AI Stack | Ollama | ollama | `/root/.ollama` | Model storage |
| AI Stack | Open WebUI | open-webui | `/app/backend/data` | User data, sessions |
| AI Stack | Valkey | valkey | `/data` | Cache persistence |
| Bluesky PDS | PDS | pds_data | `/pds` | User repos and data |
| Bluesky PDS | PDS | pds_logs | `/var/log/pds` | Access logs |
| Bluesky PDS | Caddy | caddy_config | `/config` | Caddy config |
| Bluesky PDS | Caddy | caddy_data | `/data` | SSL certs, OCSP |
| Bluesky PDS | Caddy | caddy_logs | `/var/log/caddy` | Access logs |
| LocalStack | LocalStack | localstack | `/var/lib/localstack` | Emulated service state |
| PostgreSQL | PostgreSQL | postgresql | `/var/lib/postgresql/data` | Database files |
| Redpanda | Redpanda | redpanda | `/var/lib/redpanda/data` | Kafka log data |
| Splunk | Splunk | splunk | `/opt/splunk/var` | Indexed data |
| ValKey | ValKey | valkey | `/data` | Cache persistence |
| Zerotier One | Zerotier One | zerotier-one | `/var/lib/zerotier-one` | Identity, config |
| Zot Registry | Zot | zot-registry | `/var/lib/zot` | Image layer storage |

### Best Practices

1. **Named volumes** are preferred over bind mounts for portability across storage backends.
2. **Volume labels** (`Label=`) can be applied for lifecycle management tools like Materia.
3. **Quadlet auto-creation**: Quadlet creates volumes with `[Volume]` sections automatically if they don't exist.
4. **Rootless Podman**: Volumes are stored under `~/.local/share/containers/storage/volumes/` by default.
5. **SELinux**: Use the `:Z` flag on bind mounts to auto-relabel for container access (e.g., `Volume=/host/path:/container/path:Z`).
6. **Backup**: Use `scripts/podman-volume-backup.sh` for volume backup automation.

## Overview

| Source Repository | Files Count | File Types | Purpose |
|------------------|-------------|------------|---------|
| appstore | 39+ | .container, .volume, .network, .pod, .kube | Application stack services |
| tank-os | 6 | .container, scripts | Upstream bootc image artifacts |
| tank-agent-os | 6 | .container, .network | Fork-specific bootc artifacts |

## File Catalog

### appstore Quadlets

#### AI Stack

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| ai-stack/edgetts.container | container | Edge TTS service | appstore/quadlet/ai-stack/edgetts.container |
| ai-stack/ollama.container | container | Ollama LLM service | appstore/quadlet/ai-stack/ollama.container |
| ai-stack/ollama.network | network | Ollama container network | appstore/quadlet/ai-stack/ollama.network |
| ai-stack/ollama.pod | pod | Ollama systemd pod | appstore/quadlet/ai-stack/ollama.pod |
| ai-stack/ollama.volume | volume | Ollama persistent storage | appstore/quadlet/ai-stack/ollama.volume |
| ai-stack/open-webui.container | container | Open WebUI interface | appstore/quadlet/ai-stack/open-webui.container |
| ai-stack/open-webui.volume | volume | Open WebUI persistent storage | appstore/quadlet/ai-stack/open-webui.volume |
| ai-stack/tika.container | container | Tika document processing | appstore/quadlet/ai-stack/tika.container |
| ai-stack/valkey.container | container | Valkey cache service | appstore/quadlet/ai-stack/valkey.container |
| ai-stack/valkey.volume | volume | Valkey persistent storage | appstore/quadlet/ai-stack/valkey.volume |

#### Bluesky PDS

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| bluesky_pds/caddy.container | container | Caddy reverse proxy | appstore/quadlet/bluesky_pds/caddy.container |
| bluesky_pds/caddy_config.volume | volume | Caddy config storage | appstore/quadlet/bluesky_pds/caddy_config.volume |
| bluesky_pds/caddy_data.volume | volume | Caddy data storage | appstore/quadlet/bluesky_pds/caddy_data.volume |
| bluesky_pds/caddy_logs.volume | volume | Caddy logs storage | appstore/quadlet/bluesky_pds/caddy_logs.volume |
| bluesky_pds/pds.container | container | Bluesky PDS service | appstore/quadlet/bluesky_pds/pds.container |
| bluesky_pds/pds.network | network | PDS container network | appstore/quadlet/bluesky_pds/pds.network |
| bluesky_pds/pds_data.volume | volume | PDS data storage | appstore/quadlet/bluesky_pds/pds_data.volume |
| bluesky_pds/pds_logs.volume | volume | PDS logs storage | appstore/quadlet/bluesky_pds/pds_logs.volume |

#### Inlets Ghost

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| inlets-ghost/inlets-ghost.kube | kube | Inlets Ghost Kubernetes config | appstore/quadlet/inlets-ghost/inlets-ghost.kube |
| inlets-ghost/inlets-ghost.yml.j2 | template | Inlets Ghost YAML template | appstore/quadlet/inlets-ghost/inlets-ghost.yml.j2 |
| inlets-ghost/inlets-license.yml.j2 | template | Inlets license template | appstore/quadlet/inlets-ghost/inlets-license.yml.j2 |
| inlets-ghost/inlets-token.yml.j2 | template | Inlets token template | appstore/quadlet/inlets-ghost/inlets-token.yml.j2 |

#### LocalStack

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| localstack/localstack.container | container | LocalStack AWS emulator | appstore/quadlet/localstack/localstack.container |
| localstack/localstack.volume | volume | LocalStack persistent storage | appstore/quadlet/localstack/localstack.volume |

#### MinIO & Prometheus

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| minio-prometheus/minio.container | container | MinIO object storage | appstore/quadlet/minio-prometheus/minio.container |
| minio-prometheus/minio.network | network | MinIO container network | appstore/quadlet/minio-prometheus/minio.network |
| minio-prometheus/prometheus.container | container | Prometheus monitoring | appstore/quadlet/minio-prometheus/prometheus.container |

#### PostgreSQL

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| postgresql/postgresql.container.j2 | template | PostgreSQL container template | appstore/quadlet/postgresql/postgresql.container.j2 |
| postgresql/postgresql.env | env | PostgreSQL environment config | appstore/quadlet/postgresql/postgresql.env |
| postgresql/postgresql.volume | volume | PostgreSQL persistent storage | appstore/quadlet/postgresql/postgresql.volume |

#### Redpanda

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| redpanda/redpanda-console.container | container | Redpanda console UI | appstore/quadlet/redpanda/redpanda-console.container |
| redpanda/redpanda-server.container | container | Redpanda message broker | appstore/quadlet/redpanda/redpanda-server.container |
| redpanda/redpanda.network | network | Redpanda container network | appstore/quadlet/redpanda/redpanda.network |
| redpanda/redpanda.volume | volume | Redpanda persistent storage | appstore/quadlet/redpanda/redpanda.volume |

#### Splunk

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| splunk/splunk.container | container | Splunk logging service | appstore/quadlet/splunk/splunk.container |
| splunk/splunk.volume | volume | Splunk persistent storage | appstore/quadlet/splunk/splunk.volume |

#### Syncthing

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| syncthing/syncthing.container | container | Syncthing file sync | appstore/quadlet/syncthing/syncthing.container |

#### Test OpenLDAP

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| test-openldap/test-openldap.container.j2 | template | OpenLDAP test container | appstore/quadlet/test-openldap/test-openldap.container.j2 |

#### ValKey

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| valkey/valkey.container | container | ValKey cache service | appstore/quadlet/valkey/valkey.container |
| valkey/valkey.volume | volume | ValKey persistent storage | appstore/quadlet/valkey/valkey.volume |

#### Watchtower

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| watchtower/watchtower.container | container | Container watcher | appstore/quadlet/watchtower/watchtower.container |

#### Zerotier One

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| zerotier-one/zerotier-one.container | container | Zerotier network | appstore/quadlet/zerotier-one/zerotier-one.container |
| zerotier-one/zerotier-one.volume | volume | Zerotier persistent storage | appstore/quadlet/zerotier-one/zerotier-one.volume |

#### Zot Registry

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| zot-registry/zot-registry.container | container | Zot container registry | appstore/quadlet/zot-registry/zot-registry.container |
| zot-registry/zot-registry.volume | volume | Zot persistent storage | appstore/quadlet/zot-registry/zot-registry.volume |

### Scripts

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| scripts/podman-volume-backup.sh | script | Podman volume backup utility | appstore/scripts/podman-volume-backup.sh |
| scripts/podman_ps/podman_ps.sh | script | Podman process status tool | appstore/scripts/podman_ps/podman_ps.sh |

### tank-os Bootc Artifacts

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| openclaw.container | container | OpenClaw service container | tank-os/bootc/rootfs/etc/containers/systemd/users/1000/openclaw.container |
| service-gator.container | container | Service Gator service container | tank-os/bootc/rootfs/etc/containers/systemd/users/1000/service-gator.container |
| Containerfile | containerfile | Bootc image definition | tank-os/bootc/Containerfile |
| bootstrap-openclaw | script | OpenClaw bootstrap script | tank-os/bootc/rootfs/usr/libexec/tank-os/bootstrap-openclaw |
| bootstrap-service-gator | script | Service Gator bootstrap script | tank-os/bootc/rootfs/usr/libexec/tank-os/bootstrap-service-gator |
| sync-podman-secrets | script | Podman secrets sync script | tank-os/bootc/rootfs/usr/libexec/tank-os/sync-podman-secrets |

### tank-agent-os Bootc Artifacts

| File | Type | Purpose | Source Path |
|------|------|---------|-------------|
| clawx.container | container | ClawX service container | tank-agent-os/bootc/rootfs/etc/containers/systemd/users/1000/clawx.container |
| docs-mcp.container | container | Docs MCP service container | tank-agent-os/bootc/rootfs/etc/containers/systemd/users/1000/docs-mcp.container |
| llm-wiki.container | container | LLM Wiki service container | tank-agent-os/bootc/rootfs/etc/containers/systemd/users/1000/llm-wiki.container |
| mcp-searxng.container | container | SearXNG MCP service container | tank-agent-os/bootc/rootfs/etc/containers/systemd/users/1000/mcp-searxng.container |
| searxng.container | container | SearXNG service container | tank-agent-os/bootc/rootfs/etc/containers/systemd/users/1000/searxng.container |
| service-gator.container | container | Service Gator service container | tank-agent-os/bootc/rootfs/etc/containers/systemd/users/1000/service-gator.container |
| clawx-isolated.network | network | ClawX isolated network | tank-agent-os/bootc/rootfs/etc/containers/systemd/users/1000/clawx-isolated.network |

## Usage Notes

- All files are preserved with their original directory structure from source repositories
- Container files (.container) define Podman Quadlet configurations
- Volume files (.volume) define persistent storage volumes
- Network files (.network) define container networking configurations
- Pod files (.pod) define systemd pod configurations
- Kube files (.kube) define Kubernetes configurations
- Script files (.sh) are executable bootstrap and utility scripts
- Template files (.j2) are Jinja2 templates for dynamic generation

## Verification

All files have been copied directly from source repositories without modification:
- appstore/quadlet/ - 39+ Quadlet files
- tank-os/bootc/ - 6 bootc artifacts
- tank-agent-os/bootc/ - 7 bootc artifacts (including 1 network file)

Total: 52 deployable assets copied to knowledge base.
