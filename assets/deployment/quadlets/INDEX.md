# Quadlets Deployment Assets Index

This directory contains deployable Quadlet files and bootc scripts from multiple source repositories for use in tank-os and tank-agent-os deployments.

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
