---
name: mcp-netbird-codegraph-verify
tags: [mcp, netbird, vpn, go, mcp-server, sse, stdio, wiki]
description: "Codegraph Verification: mcp-netbird — validating wiki claims against indexed source code symbols"
source: sources/mcp-netbird/
---

# Codegraph Verification: mcp-netbird

**Date:** 2026-07-30

## Claim 1: Origin is XNet-NGO/mcp-netbird, maintained by XNet Inc., derived from Grafana Labs
- **Wiki says:** Origin github.com/XNet-NGO/mcp-netbird, maintained by XNet Inc. (lead developer Joshua S. Doucette), derived from the MCP Server for Grafana by Grafana Labs.
- **Source evidence:**
  - `go.mod` line 1: `module github.com/XNet-NGO/mcp-netbird`; git remote `origin` points to `https://github.com/XNet-NGO/mcp-netbird`
  - `README.md` line 82: `git clone https://github.com/XNet-NGO/mcp-netbird`
  - `README.md` lines 5-6 and 812: "**Maintained by XNet Inc.**" / "**Copyright 2025-2026 XNet Inc.**"; line 823: "**Maintained by XNet Inc. | Lead Developer: Joshua S. Doucette**"
  - `README.md` line 23 and `cmd/mcp-netbird/main.go` line 16 (comment): "Originally derived from MCP Server for Grafana by Grafana Labs"
- **Verdict:** ✅ CORRECT (wiki previously misattributed origin to a different GitHub org — corrected)

## Claim 2: Licensed under Apache-2.0
- **Wiki says:** License Apache-2.0.
- **Source evidence:**
  - `LICENSE` file is the full "Apache License, Version 2.0, January 2004" text
  - `README.md` line 8: `[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)`; line 810: "This project is licensed under the [Apache License, Version 2.0](LICENSE)"
  - `cmd/mcp-netbird/main.go` lines 4-8: "Licensed under the Apache License, Version 2.0"
- **Verdict:** ✅ CORRECT (wiki previously said "Not specified" — corrected)

## Claim 3: Go 1.24 with mark3labs/mcp-go v0.18.0
- **Wiki says:** Written in Go 1.24 using mark3labs/mcp-go v0.18.0, a popular third-party MCP SDK (not the "official" Go SDK).
- **Source evidence:**
  - `go.mod` line 3: `go 1.24.0`
  - `go.mod` line 7: `github.com/mark3labs/mcp-go v0.18.0`
  - `cmd/mcp-netbird/main.go` line 27 imports `"github.com/mark3labs/mcp-go/server"`; line 34 creates the server: `s := server.NewMCPServer(...)`
  - `README.md` line 819: mark3labs/mcp-go referenced as the SDK dependency
- **Verdict:** ✅ CORRECT (wiki previously called it the "official Go MCP SDK" — softened to third-party)

## Claim 4: 50+ tools across 13 tool categories, plus policy helper tools
- **Wiki says:** 50+ MCP tools registered across 13 category functions, with policy helper tools `list_policies_by_group`, `replace_group_in_policies`, `get_policy_template`.
- **Source evidence:**
  - `README.md` line 3: "comprehensive MCP server for NetBird providing 50+ tools for complete VPN infrastructure management"; line 17 confirms "**50+ Management Tools**"
  - `cmd/mcp-netbird/main.go` lines 38-50 register exactly 13 categories: `AddNetbirdPeerTools`, `AddNetbirdGroupTools`, `AddNetbirdPolicyTools`, `AddNetbirdNetworkTools`, `AddNetbirdNetworkResourceTools`, `AddNetbirdNetworkRouterTools`, `AddNetbirdPostureCheckTools`, `AddNetbirdPortAllocationTools`, `AddNetbirdNameserverTools`, `AddNetbirdRouteTools`, `AddNetbirdSetupKeyTools`, `AddNetbirdUserTools`, `AddNetbirdAccountTools`
  - `README.md` lines 369-371: "**list_policies_by_group**: Find all policies referencing a specific group", "**replace_group_in_policies**: Bulk replace groups across all policies", "**get_policy_template**: Get example policy structures with documentation"
- **Verdict:** ✅ CORRECT

## Claim 5: STDIO and SSE transport modes
- **Wiki says:** Supports both STDIO (local) and SSE (remote) transport modes.
- **Source evidence:**
  - `cmd/mcp-netbird/main.go` line 54 defines `run(transport, addr string)` with transport routing
  - `cmd/mcp-netbird/main.go` lines 58-61 handle `"stdio"` case via `server.NewStdioServer(s)`
  - `cmd/mcp-netbird/main.go` lines 62-69 handle `"sse"` case via `server.NewSSEServer(s)`
  - `cmd/mcp-netbird/main.go` lines 72-73 validate: `"invalid transport type: %s. must be 'stdio' or 'sse'"`
- **Verdict:** ✅ CORRECT

## Claim 6: Env vars NETBIRD_API_TOKEN / NETBIRD_API_HOST and CLI flags --api-token / --api-host / --transport / --sse-address
- **Wiki says:** Environment configuration via `NETBIRD_API_TOKEN` and `NETBIRD_API_HOST`; CLI flags `--api-token`, `--api-host`, `--transport`, `--sse-address`.
- **Source evidence:**
  - `README.md` lines 39-40 and 125-126: `-e NETBIRD_API_TOKEN=your_token_here` / `-e NETBIRD_API_HOST=api.netbird.io` / `NETBIRD_API_TOKEN=nbp_your_token_here`
  - `cmd/mcp-netbird/main.go` lines 84-93: `flag.StringVar(&transport, "transport", "stdio", ...)`, `addr := flag.String("sse-address", "localhost:8001", ...)`, `flag.StringVar(&apiToken, "api-token", "", "Netbird API token")`, `flag.StringVar(&apiHost, "api-host", "", "Netbird API host (without protocol)")`
- **Verdict:** ✅ CORRECT (wiki previously listed wrong env var names and `-nb-*` flag names — corrected)

## Claim 7: Config priority CLI > HTTP headers > env vars
- **Wiki says:** Configuration loads with priority: CLI flags first, then HTTP headers (SSE mode), then environment variables.
- **Source evidence:**
  - `README.md` lines 296-310 (Configuration Priority section): "**CLI Arguments > HTTP Headers > Environment Variables**" with CLI-overrides-env example
  - `mcpnetbird.go` line 67: `func (cl *ConfigLoader) LoadConfig(httpToken, httpHost string)` — CLI token takes precedence (`cl.cliToken`), then HTTP header (`httpToken`), then env var (`os.Getenv(netbirdAPIEnvVar)`); same priority chain for API host (lines 80-91)
- **Verdict:** ✅ CORRECT

## Claim 8: Docker image xnetadmin/mcp-netbird:latest — plain two-stage Dockerfile, not multi-arch
- **Wiki says:** Docker Hub image `xnetadmin/mcp-netbird:latest`; the container image is NOT multi-arch (plain two-stage Dockerfile).
- **Source evidence:**
  - `README.md` line 33: `docker pull xnetadmin/mcp-netbird:latest`; lines 190, 239 reference `"xnetadmin/mcp-netbird:latest"`; line 11: Docker Hub badge `https://hub.docker.com/r/xnetadmin/mcp-netbird`
  - `Dockerfile`: two-stage build — `FROM golang:1.24-bullseye AS builder` then `FROM debian:bullseye-slim`, no `buildx`/platform matrix; multi-OS support comes from per-platform release binaries, not the image
- **Verdict:** ✅ CORRECT (wiki previously used a wrong ghcr.io image path and claimed multi-arch — corrected)

## Summary

All 8 key claims from the mcp-netbird wiki have been verified against the source:
- ✅ Origin XNet-NGO/mcp-netbird + XNet Inc. maintainer + Grafana Labs derivation
- ✅ Apache-2.0 license
- ✅ Go 1.24 + mark3labs/mcp-go v0.18.0 (third-party SDK)
- ✅ 50+ tools, 13 tool categories, policy helper tools
- ✅ STDIO + SSE transports
- ✅ NETBIRD_API_TOKEN/NETBIRD_API_HOST env vars + --api-token/--api-host/--transport/--sse-address flags
- ✅ Config priority CLI > HTTP headers > env
- ✅ Docker Hub image xnetadmin/mcp-netbird:latest, not multi-arch

## Related

- [[mcp-netbird]] -- Main wiki entry

## Cross-project

- [[netbird.codegraph-verify]] -- Similar codegraph verification for NetBird
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
