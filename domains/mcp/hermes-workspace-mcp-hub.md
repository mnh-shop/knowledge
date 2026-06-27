---
name: hermes-workspace-mcp-hub
tags: [agent-gateway, hermes-agent, mcp, messaging, multi-platform, typescript]
description: "Hermes Workspace MCP Hub: centralized MCP server management for Hermes workspace agents"
source: sources/hermes-workspace/
---

# Hermes Workspace — MCP Hub

**Source:** `sources/hermes-workspace/src/server/mcp-hub/`

## What it is

The MCP Hub is the Workspace's server-side MCP catalog and marketplace
aggregator. It searches multiple MCP server sources in parallel, deduplicates
results, marks installed servers, and presents a unified catalog UI.

## How it works

```typescript
src/server/mcp-hub/
├── index.ts              — Unified search: fans out to all sources, deduplicates
├── types.ts              — HubMcpEntry, HubSource, HubTrust types
├── cache.ts              — Caching layer
├── trust.ts              — Trust/security checks
├── lib/                  — Shared utilities
└── sources/
    ├── local-file.ts     — Local JSON/MCP config files
    ├── mcp-get.ts        — `mcp-get` package registry
    └── generic-json.ts   — Generic JSON source (user-defined)

// Support files elsewhere:
src/server/mcp-hub-sources-store.ts     — User-defined source configs
src/server/mcp-presets-store.ts         — MCP preset/configuration store
src/server/mcp-normalize.ts             — Server config normalization
src/server/mcp-input-validate.ts        — User input validation
src/server/mcp-tools-cache.ts           — Tool definition cache
src/server/mcp-cli-bridge.ts            — CLI command bridge for MCP
```

### Search flow

1. `unifiedSearch()` reads all configured sources
2. Fans out to all sources in parallel via `Promise.allSettled` (8s timeout
   per source)
3. Deduplicates by `${source}:${name}`
4. Marks installed entries by comparing against `config.yaml` `mcp_servers`
5. Falls back to local-file only when all remote sources fail

### Sources

| Source Type | Description |
|---|---|
| `local-file` | Local JSON/MCP config files on disk |
| `mcp-get` | The `mcp-get` package registry |
| `generic-json` | User-defined JSON sources (Phase 3.2) |
| `user-defined` | Loaded from `readHubSources()` at runtime |

### Integration with UI

The MCP Hub feeds the `/mcp` screen, which shows:
- Catalog browsing with search
- Marketplace aggregation
- Install/uninstall/config UI
- Fallback to local config CRUD when remote sources are unavailable

## Related

- [[hermes-workspace]] -- Wiki entry
- [[hermes-workspace-architecture]] -- System architecture
- [[hermes-workspace-api]] -- REST API reference
- [[hermes-workspace-deployment]] -- Deployment guide
- [[hermes-mcp-implementation]] -- Hermes MCP implementation patterns
