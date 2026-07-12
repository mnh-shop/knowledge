---
name: appstore
tags: [appstore, mcp, developer-tools, marketplace, agent-tools]
description: "MCP server marketplace and discovery platform for AI agent tools"
source: sources/appstore/
---

# AppStore

| Field | Value |
|---|---|
| **Origin** | [nicholasgriffintn/mcp-marketplace](https://github.com/nicholasgriffintn/mcp-marketplace) |
| **Source** | `sources/appstore/` |
| **Repomix** | `raw/appstore/appstore.xml` |
| **Codegraph** | `graphs/appstore/` |

## Overview

AppStore (originally named `mcp-marketplace`) is an MCP server marketplace and discovery platform that catalogs available MCP servers for AI agents. It provides a browsable registry where agents and their operators can find, evaluate, and connect to MCP-compatible tools and services, reducing the friction of discovering new capabilities.

The repository also doubles as a reference collection of Kubernetes YAML manifests and Podman Quadlet files tested in production with Podman. These deployment examples cover a wide range of services including AI stacks, messaging infrastructure (NATS, Redpanda), database systems (PostgreSQL, Valkey), monitoring stacks (Prometheus with MinIO), storage (Syncthing), networking (ZeroTier-One), reverse proxies (inlets-ghost), development tools (LocalStack, test OpenLDAP), logging (Splunk), and registry management (zot-registry with Watchtower). This dual purpose — marketplace frontend and deployment reference — makes the AppStore repo a practical resource for both MCP discovery and container-native infrastructure.

## Key Features

- **MCP Server Registry** — Catalog of available MCP servers with descriptions, capabilities, and configuration details. Agents browse to discover new tool surfaces.
- **Search & Discovery** — Search and filter interface for finding MCP servers by category, protocol, or capability. Enables rapid evaluation of available agent tooling.
- **Agent Integration** — Simplified workflow for connecting discovered MCP servers to agent runtimes. Standardized metadata facilitates plug-and-play agent connectivity.
- **Metadata Curation** — Structured metadata for each MCP server listing including tools exposed, resources available, authentication requirements, and transport protocols (stdio, SSE, WebSocket).
- **Community Contributions** — Mechanism for publishing and updating MCP server listings, enabling a community-driven ecosystem of agent tools.
- **Kubernetes Deployment Reference** — Tested Kubernetes YAML examples for Podman-native container orchestration, including comprehensive configurations for various service types.
- **Quadlet Deployment Collection** — 15+ tested Quadlet file sets for Podman systemd-native container management, covering AI stack infrastructure, databases (PostgreSQL, Redpanda, Valkey), monitoring (MinIO with Prometheus), storage sync (Syncthing), networking (ZeroTier-One), reverse proxy (inlets-ghost), development (LocalStack), directory services (test OpenLDAP), logging (Splunk), and registry management (zot-registry with Watchtower).

## Architecture

The platform aggregates MCP server metadata from community submissions and automated discovery, presenting it through a web interface and optionally through an API that agent runtimes can query programmatically. Each MCP server entry includes structured metadata about available tools, resources, prompts, authentication requirements, and transport protocols.

The deployment reference side of the repo is organized as:

```
appstore/
├── kubernetes/          # Podman-supported K8s YAML examples
│   └── README.md
└── quadlet/             # Podman Quadlet file examples
    ├── README.md
    ├── ai-stack/        # AI infrastructure stack
    ├── postgresql/      # PostgreSQL database
    ├── redpanda/        # Redpanda event streaming
    ├── valkey/          # Valkey key-value store
    ├── minio-prometheus/ # Monitoring stack
    ├── syncthing/       # File synchronization
    ├── zerotier-one/    # ZeroTier networking
    ├── inlets-ghost/    # Reverse proxy
    ├── localstack/      # AWS local emulation
    ├── test-openldap/   # LDAP directory services
    ├── splunk/          # Logging infrastructure
    ├── zot-registry/    # OCI registry with Watchtower
    ├── bluesky_pds/     # AT Protocol PDS
    └── watchtower/      # Container update management
```

## Quadlet Deployment Examples

The Quadlet collection provides systemd-native Podman configurations for running containerized services. Key example stacks include:

- **AI Stack** (`quadlet/ai-stack/`) — Complete AI infrastructure with model serving, vector stores, and agent runtime containers
- **Redpanda** — Kafka-compatible event streaming platform for building real-time data pipelines
- **MinIO + Prometheus** — S3-compatible object storage paired with monitoring and alerting
- **PostgreSQL** — Database with persistent storage, backup configurations, and connection pooling
- **Syncthing** — Peer-to-peer file synchronization across devices
- **ZeroTier-One** — Software-defined networking for secure multi-node communication
- **zot-registry + Watchtower** — OCI-compliant container image registry with automatic updates

## Usage

### MCP Discovery

Browse the registry to find MCP servers by category (AI, databases, analytics, messaging, storage, networking). Each listing provides:
- Server name and description
- Available tools and resources
- Transport protocol and connection details
- Authentication requirements
- Configuration examples for common agent runtimes

### Deploying Quadlet Examples

```bash
# Copy the desired Quadlet to the systemd user directory
cp -r quadlet/postgresql/* ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user start postgresql
```

### Kubernetes Examples

```bash
# Deploy Podman-compatible Kubernetes YAML
podman play kube kubernetes/example.yaml
```

## Related

- [[hermes-agent]] — MCP client that can consume servers from the marketplace
- [[openclaw]] — MCP server surface that could be listed in the marketplace
- [[mcp]] — Model Context Protocol standard that underpins the marketplace
- [[mission-control]] — MCP audit server for monitoring and verifying MCP connections
- [[n8n-mcp]] — MCP servers for n8n workflow automation
- [[podman-quadlet]] — Podman Quadlet reference for container deployment patterns
