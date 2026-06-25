---
name: alphaclaw-mcp
description: "AlphaClaw MCP configuration manager — writes mcp.servers blocks into openclaw.json"
tags: [documentation, mcp]
---
# AlphaClaw MCP Implementation

**Source repo:** `@chrysb/alphaclaw` (v0.9.18)
**File:** `lib/server/gateway.js`
**Role:** Setup UI, gateway manager, and onboarding wrapper for OpenClaw

## Overview

AlphaClaw does **not** run an MCP server itself. Instead, it acts as a **configuration manager** that writes an `mcp.servers.<name>` block into OpenClaw's `openclaw.json` on every gateway start when environment variables are provided. This enables the OpenClaw agent (running as a separate child process) to call back into an external MCP server.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `REMOTE_MCP_URL` | Optional | Upstream remote MCP server URL. Triggers config write to `openclaw.json` when set together with `REMOTE_MCP_API_TOKEN`. |
| `REMOTE_MCP_API_TOKEN` | Optional | Bearer token for the external MCP server. Persisted in `openclaw.json` as a `${REMOTE_MCP_API_TOKEN}` reference, never as plaintext. |
| `REMOTE_MCP_NAME` | Optional | Key under `mcp.servers.<name>`. Defaults to `remote`. Used to label the entry (e.g. `sure`, `notion`). |
| `REMOTE_MCP_PROXY_URL` | Optional | When set, OpenClaw connects here instead of `REMOTE_MCP_URL`. Intended for a same-host scanning proxy (e.g. Pipelock MCP reverse proxy). Implementation is proxy-agnostic. |

## Config Key Validation (`ensureGatewayProxyConfig`)

The config key that becomes `mcp.servers.<name>` is sanitized:

- Rejects names with prototype-pollution shapes, spaces, or path-like segments
- Falls back to `"remote"` with a warning if validation fails
- OpenClaw sanitizes names later for tool prefixes

## Generated `openclaw.json` Entry Shape

When `REMOTE_MCP_URL` + `REMOTE_MCP_API_TOKEN` are set, the following block is written to `openclaw.json`:

```json
{
  "mcp": {
    "servers": {
      "<REMOTE_MCP_NAME or 'remote'>": {
        "url": "<REMOTE_MCP_URL>",
        "headers": {
          "Authorization": "Bearer ${REMOTE_MCP_API_TOKEN}"
        }
      }
    }
  }
}
```

If `REMOTE_MCP_PROXY_URL` is also set, `url` uses the proxy value instead of `REMOTE_MCP_URL`.

## Proxy Support

- A same-host scanning proxy (e.g. `pipelock mcp proxy --listen <PROXY_URL> --upstream <REMOTE_MCP_URL>`) can be interposed
- Set `REMOTE_MCP_PROXY_URL` to route all callbacks through this proxy
- Implementation is proxy-agnostic -- any HTTP proxy works

## Gateway Lifecycle Integration

- The MCP config is written during `syncChannelConfig` / `ensureGatewayProxyConfig`, called on **every gateway start**
- Config is written into the shared `openclaw.json` that the OpenClaw child process consumes
- The token value is stored as an environment variable reference (`${REMOTE_MCP_API_TOKEN}`), not as plaintext
- Config is managed alongside channel configuration in a single `syncChannelConfig` call

## OpenClaw Integration

- AlphaClaw wraps OpenClaw (`openclaw: "2026.5.28"` npm dependency) as a child process
- The child process reads `openclaw.json` and connects to the configured MCP servers
- OpenClaw's `openclaw mcp` CLI commands read back the MCP server configuration

## Key Source Files

- `lib/server/gateway.js` -- MCP config write logic, env var resolution, key validation
- `lib/server/openclaw-config.js` -- `readOpenclawConfig` / `writeOpenclawConfig` helpers
