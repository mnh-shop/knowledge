---
name: appstore-codegraph-verify
tags: [appstore, codegraph-verify, mcp, marketplace]
description: "Codegraph Verification: appstore — validating wiki claims against indexed source code"
source: sources/appstore/
date: 2026-07-12
---

# Codegraph Verification: appstore

**Date:** 2026-07-12

## Claim 1: MCP server marketplace and discovery platform
- **Wiki says:** "AppStore (originally named `mcp-marketplace`) is an MCP server marketplace and discovery platform that catalogs available MCP servers for AI agents. It provides a browsable registry where agents and their operators can find, evaluate, and connect to MCP-compatible tools and services."

- **Source evidence:**
  - GitHub origin is `nicholasgriffintn/mcp-marketplace` — confirming the original name "mcp-marketplace" from the wiki.
  - `README.md` title is "appstore" with description "Example directory of Kubernetes YAML and Quadlets tested with Podman."
  - The repo does not contain a web application, database, or API for MCP discovery. It is primarily a deployment examples repo, not a functional marketplace platform. No database schemas, API endpoints, or search interface exist.
  - The wiki overstates the scope: the repo is a reference collection of deployment examples, not a running marketplace service.

- **Verdict:** ❌ INCORRECT — The repo is a static collection of deployment examples (Kubernetes YAML + Quadlets), not a functional MCP server marketplace or discovery platform. No search interface, registry API, or dynamic catalog exists in the source.

- **Fix needed:** Update wiki to match actual repo content: "AppStore is a reference collection of Kubernetes YAML manifests and Podman Quadlet files tested in production with Podman. Originally named mcp-marketplace, it serves as a deployment pattern library rather than a functional marketplace platform."

## Claim 2: Kubernetes deployment reference for Podman
- **Wiki says:** "Tested Kubernetes YAML examples for Podman-native container orchestration, including comprehensive configurations for various service types."

- **Source evidence:**
  - `kubernetes/` directory exists with a `README.md` file.
  - No `.yaml` or `.yml` files found directly in `kubernetes/` — only the README.
  - The Kubernetes examples appear minimal or placeholder-level.

- **Verdict:** ⚠️ PARTIAL — The `kubernetes/` directory exists but contains only a README with no actual Kubernetes YAML manifests found at the time of verification. The claim of "comprehensive configurations" is not substantiated by the source tree.

- **Fix needed:** Add actual Kubernetes YAML examples or update wiki to reflect the minimal Kubernetes content.

## Claim 3: 15+ Quadlet deployment collections covering AI stack, databases, monitoring, networking, and more
- **Wiki says:** "15+ tested Quadlet file sets for Podman systemd-native container management, covering AI stack infrastructure, databases (PostgreSQL, Redpanda, Valkey), monitoring (MinIO with Prometheus), storage sync (Syncthing), networking (ZeroTier-One), reverse proxy (inlets-ghost), development (LocalStack), directory services (test OpenLDAP), logging (Splunk), and registry management (zot-registry with Watchtower)."

- **Source evidence:**
  - `quadlet/` directory contains 15 subdirectories: `ai-stack/`, `bluesky_pds/`, `inlets-ghost/`, `localstack/`, `minio-prometheus/`, `postgresql/`, `redpanda/`, `splunk/`, `syncthing/`, `test-openldap/`, `valkey/`, `watchtower/`, `zerotier-one/`, `zot-registry/`, plus `README.md`.
  - `quadlet/ai-stack/` contains 11 files: `edgetts.container`, `ollama.container`, `ollama.network`, `ollama.pod`, `ollama.service.d/`, `ollama.volume`, `open-webui.container`, `open-webui.service.d/`, `open-webui.volume`, `tika.container`, `valkey.container`, `valkey.volume`, `README.md` — confirming full AI stack quadlet files.
  - `quadlet/postgresql/`, `quadlet/redpanda/`, `quadlet/valkey/`, `quadlet/minio-prometheus/`, `quadlet/syncthing/`, `quadlet/zerotier-one/`, `quadlet/inlets-ghost/`, `quadlet/localstack/`, `quadlet/test-openldap/`, `quadlet/splunk/`, `quadlet/zot-registry/`, `quadlet/watchtower/`, `quadlet/bluesky_pds/` — all present with `.container`, `.volume`, `.network`, `.pod`, and `.service.d/` files as appropriate.
  - README.md line 2: "Podman supported example quadlet file examples sub-directories."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Structured metadata for MCP server listings
- **Wiki says:** "Structured metadata for each MCP server listing including tools exposed, resources available, authentication requirements, and transport protocols (stdio, SSE, WebSocket)."

- **Source evidence:**
  - No files in the repo contain MCP server metadata, tool definitions, resource descriptions, or transport protocol specifications. No JSON/YAML schemas for MCP listings exist.
  - The repo contains no MCP-related content beyond the GitHub project's original name (`mcp-marketplace`).

- **Verdict:** ❌ INCORRECT — No MCP server metadata, structured or otherwise, exists in the repository. The claim applies to the original upstream concept, not the checked-out source.

- **Fix needed:** Remove the MCP metadata curation claim or mark the repo as a deployment reference only, not a functioning marketplace.

## Claim 5: Community contribution mechanism for MCP listings
- **Wiki says:** "Mechanism for publishing and updating MCP server listings, enabling a community-driven ecosystem of agent tools."

- **Source evidence:**
  - No issue templates, pull request templates, submission forms, or contribution workflows specific to MCP listings exist in the repo.
  - Standard `.github/` directory is present but no contribution automation for MCP metadata.
  - No database, registry, or content management system for community submissions exists.

- **Verdict:** ❌ INCORRECT — No community contribution mechanism for MCP server listings exists in this repo. The repo is a static collection of Quadlet and Kubernetes deployment examples.

- **Fix needed:** Remove the community marketplace claim. If the wiki intends to describe the original GitHub project concept, add a disclaimer distinguishing the upstream vision from the actual repository contents.

## Summary

The appstore wiki significantly overstates the repository's scope. The actual source is a **deployment reference collection** — primarily Podman Quadlet examples (15 directories, confirmed) with minimal Kubernetes YAML. The wiki's MCP marketplace, metadata curation, search/discovery, and community contribution claims are **not supported** by the source code. The Quadlet collection claim (Claim 3) is accurate and well-supported.

## Related

- [[appstore]] -- Main wiki entry
- [[mcp]] -- Model Context Protocol standard
- [[hermes-agent]] -- MCP client
- [[openclaw]] -- MCP server surface

## Cross-project

- [[podman-quadlet.codegraph-verify]] -- Podman Quadlet reference
- [[hermes-agent.codegraph-verify]] -- Hermes Agent verification
- [[openclaw.codegraph-verify]] -- OpenClaw verification
