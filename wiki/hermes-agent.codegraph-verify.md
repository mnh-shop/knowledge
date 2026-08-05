---
name: hermes-agent-codegraph-verify
tags: [acp, hermes-agent, agent, agent-gateway, cli, mcp, messaging, multi-platform, orchestration, python, wiki]
description: "Codegraph Verification: hermes-agent — validating wiki claims against indexed source code symbols"
source: sources/hermes-agent/
---

# Codegraph Verification: hermes-agent

**Date:** 2026-07-30

**Version checked:** 0.19.0 (`hermes_cli/__init__.py:17`)

## Claim 1: MCP hub — 10-tool messaging bridge + curated catalog
- **Wiki says:** Hermes is an MCP client (`tools/mcp_tool.py`), an MCP server (`mcp_serve.py`) exposing exactly 10 tools, and ships a curated MCP catalog (`optional-mcps/`, 6 manifests) installable via `hermes mcp catalog/install`. A second MCP server (`agent/transports/hermes_tools_mcp_server.py`) exposes Hermes model tools to Codex. The bridge header explicitly says "Matches OpenClaw's 9-tool MCP channel bridge surface".
- **Source evidence:**
  - `mcp_serve.py:9-11` — header: "Matches OpenClaw's 9-tool MCP channel bridge surface" listing the 9 tools
  - `mcp_serve.py:557-925` — exactly 10 `@mcp.tool()` registrations: `conversations_list` (557), `conversation_get` (614), `messages_read` (647), `attachments_fetch` (704), `events_poll` (756), `events_wait` (785), `messages_send` (819), `channels_list` (855), `permissions_list_open` (909), `permissions_respond` (925)
  - `tools/mcp_tool.py` — `MCPServerTask` with `_run_stdio()` / `_run_http()` transports and `_discover_tools()`
  - `hermes_cli/mcp_catalog.py:1-15` — curated catalog; entries live under `optional-mcps/<name>/manifest.yaml`
  - `hermes_cli/subcommands/mcp.py:110-128` — `catalog` / `install` / `picker` subparsers
  - `optional-mcps/` — six manifests: blender, comfy-cloud, figma, linear, n8n, unreal-engine
  - `agent/transports/hermes_tools_mcp_server.py:1-40` — Hermes-tools-as-MCP stdio server for the codex_app_server runtime
- **Verdict:** ✅ CORRECT (10-tool bridge confirmed, not a generic tool exporter; 6 curated MCP manifests confirmed)
- **Fix needed:** None (replaces earlier claim of 3 optional-mcps)

## Claim 2: 75 registered core tools across 33 toolsets
- **Wiki says:** 75 registered core tools via `registry.register()` across `tools/**`, of which 55 are the always-loaded core set (`_HERMES_CORE_TOOLS`); tools grouped into 33 toolsets.
- **Source evidence:**
  - `toolsets.py:31-82` — `_HERMES_CORE_TOOLS = [...]` with 55 entries (web, terminal, file, vision, skills, browser, tts, todo, memory, session_search, clarify, execute_code, delegate_task, cronjob, ha_*, kanban_*, computer_use, …)
  - `toolsets.py:97` — `TOOLSETS = {...}` with 33 toolset keys: browser, clarify, code_execution, coding, computer_use, context_engine, cronjob, debugging, delegation, discord, discord_admin, feishu_doc, feishu_drive, file, homeassistant, image_gen, kanban, memory, project, safe, search, session_search, skills, spotify, terminal, todo, tts, video, video_gen, vision, web, x_search, yuanbao
  - `tools/registry.py:3` — "Each tool file calls `registry.register()` at module level"
  - `registry.register()` call sites across `tools/*.py` (browser_tool, kanban_tools, file_tools, web_tools, vision_tools, homeassistant_tool, mcp_tool, delegate_tool, computer_use_tool, x_search_tool, …) — 77 call sites incl. helper files
- **Verdict:** ✅ CORRECT (75+ tool registrations; 55 core; 33 toolsets — replaces the stale "90+ model tools" claim)
- **Fix needed:** None

## Claim 3: Skills — 14 built-in + 21 optional categories
- **Wiki says:** Built-in skills are 14 categories (70 SKILL.md files); optional skills are 21 categories (111 SKILL.md files). Skills hub has 9 source classes.
- **Source evidence:**
  - `skills/` — 14 category dirs: apple, autonomous-ai-agents, creative, email, github, index-cache, media, mlops, note-taking, productivity, research, smart-home, social-media, software-development
  - `find skills -name SKILL.md` → 70 files
  - `optional-skills/` — 22 entries minus `DESCRIPTION.md` = 21 categories (autonomous-ai-agents, blockchain, communication, creative, data-science, devops, dogfood, email, finance, gaming, health, mcp, migration, mlops, payments, productivity, research, security, software-development, web-development, yuanbao)
  - `find optional-skills -name SKILL.md` → 111 files
  - `tools/skills_hub.py` — `SkillSource` subclasses: GitHubSource (557), WellKnownSkillSource (1196), UrlSource (1423), SkillsShSource (1609), ClawHubSource (2185), LobeHubSource (2731), BrowseShSource (2891), OptionalSkillSource (3065), HermesIndexSource (3793)
- **Verdict:** ✅ CORRECT (replaces stale "18 built-in / 19 optional categories" claim)
- **Fix needed:** None

## Claim 4: ACP — server is `hermes acp` itself; no registry, no `serve` subcommand
- **Wiki says:** `acp_registry/agent.json` was removed (commit d84e11af4 "rip out brew + pip/PyPI wheel support"); `hermes acp` IS the ACP server with flags `--version/--check/--setup/--setup-browser/--yes`; no `serve` subcommand.
- **Source evidence:**
  - `acp_registry/` directory does not exist in the working tree
  - `git log` confirms commit `d84e11af4` "rip out brew + pip/PyPI wheel support (#68217)"
  - `hermes_cli/subcommands/acp.py:16-49` — parser adds only `--version`, `--check`, `--setup`, `--setup-browser`, `--yes` flags; no subparsers
  - `acp_adapter/server.py` — `HermesACPAgent` extending `acp.Agent`; `SessionManager` for session CRUD
  - `agent/copilot_acp_client.py` — ACP client for Copilot
- **Verdict:** ✅ CORRECT (replaces stale claims about `hermes acp serve` and `acp_registry/agent.json`)
- **Fix needed:** None

## Claim 5: Terminal backends — seven, incl. Vercel Sandbox
- **Wiki says:** Seven terminal backends: local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox (with managed_modal as a Modal variant).
- **Source evidence:**
  - `README.md:29` — "Seven terminal backends — local, Docker, SSH, Singularity, Modal, Daytona, and Vercel Sandbox"
  - `tools/environments/` — backend modules: local.py, docker.py, ssh.py, singularity.py, modal.py, managed_modal.py, daytona.py, vercel_sandbox.py (plus shared base.py, file_sync.py, modal_utils.py)
- **Verdict:** ✅ CORRECT (replaces stale "six terminal backends" claim)
- **Fix needed:** None

## Claim 6: Gateway — 21 plugin platforms + 9 core adapters
- **Wiki says:** Most platforms moved to plugin form: 21 adapters in `plugins/platforms/` and 9 core adapters remain in `gateway/platforms/`. A single generic RelayAdapter (experimental) fronts external connectors.
- **Source evidence:**
  - `plugins/platforms/` — 21 adapters: buzz, dingtalk, discord, email, feishu, google_chat, homeassistant, irc, line, matrix, mattermost, ntfy, photon, raft, simplex, slack, sms, teams, telegram, wecom, whatsapp
  - `gateway/platforms/` — 9 core adapters: api_server, signal, weixin, yuanbao, qqbot, bluebubbles, whatsapp_cloud, msgraph_webhook, webhook (+ base.py)
  - `gateway/platform_registry.py:4-8` — self-registration for built-in and plugin adapters via `PluginContext.register_platform()`
  - `gateway/platforms/base.py` — `BasePlatformAdapter`; `gateway/stream_dispatch.py` — `GatewayEventDispatcher`
  - `gateway/relay/adapter.py:1-30` — single `RelayAdapter` dialing out to a connector; `docs/relay-connector-contract.md` defines the wire contract
  - `gateway/platforms/api_server.py:124` — `DEFAULT_PORT = 8642` (OpenAI-compatible REST gateway)
- **Verdict:** ✅ CORRECT (replaces stale platform table that predated the plugin split)
- **Fix needed:** None

## Claim 7: OpenAI-compatible API server + dashboard web server
- **Wiki says:** Hermes ships an OpenAI-compatible REST API server (port 8642, `/v1/chat/completions`, `/v1/responses`, `/v1/runs` + SSE, `/api/sessions` CRUD, `/health`) and a dashboard web server (port 9119, 140+ routes + websockets).
- **Source evidence:**
  - `gateway/platforms/api_server.py:1-35` — route inventory: `/v1/chat/completions`, `/v1/responses`, `/v1/runs` (+ `/events` SSE, `/approval`, `/stop`), `/api/sessions` CRUD + `/fork` + `/messages`, `/health`, `/health/detailed`, per-profile `/p/<profile>/v1/...`
  - `gateway/platforms/api_server.py:124` — `DEFAULT_PORT = 8642`
  - `hermes_cli/web_server.py:8` — "Start on http://127.0.0.1:9119"
  - `hermes_cli/web_server.py` — 141 `@app.*` route decorators incl. `/api/media` (1999), `/api/chat/image-upload` (2276), `/api/files*` (2319-2521), plus websocket endpoints; `start_server` invoked from `hermes_cli/main.py` dashboard path
  - `hermes_cli/main.py:10348` — `from hermes_cli.web_server import start_server`
- **Verdict:** ✅ CORRECT (major capability previously missing from wiki)
- **Fix needed:** None

## Claim 8: 90 slash commands, plugins surface, agent internals
- **Wiki says:** 90 slash commands in `COMMAND_REGISTRY`; 18 plugin directories (incl. image_gen, video_gen, kanban, spotify, web, disk-cleanup, google_meet, hermes-achievements, teams_pipeline); 8 memory providers; 33 model-provider packages; agent internals include credential pool, auxiliary_client, iteration budget, goals, MoA; LSP integration; tool-search bridge; OTLP observability.
- **Source evidence:**
  - `hermes_cli/commands.py:101` — `COMMAND_REGISTRY: list[CommandDef]` with 90 entries (start, goal, moa, egress, approvals, bundles, curator, kanban, insights, pets, journey, …)
  - `plugins/` — 18 dirs: browser, context_engine, cron_providers, dashboard_auth, disk-cleanup, google_meet, hermes-achievements, image_gen, kanban, memory, model-providers, observability, platforms, security-guidance, spotify, teams_pipeline, video_gen, web
  - `plugins/memory/` — 8 providers: honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb
  - `plugins/model-providers/` — 33 package dirs (anthropic, openai-codex, gemini, bedrock, vertex, xai, deepseek, openrouter, nous, …)
  - `agent/credential_pool.py` — multi-credential failover; `agent/auxiliary_client.py` — side-task resolution chain; `agent/iteration_budget.py` — parent 500 / subagent 50; `hermes_cli/goals.py:1079` — `GoalManager`; `agent/moa_loop.py` + `agent/moa_trace.py`
  - `agent/lsp/` — client.py, manager.py, servers.py, protocol.py; `tools/tool_search.py` — tool_search/tool_describe/tool_call bridge; `hermes_cli/observability/` + `plugins/observability/langfuse/` + `plugins/observability/nemo_relay/`
  - `tools/x_search_tool.py:1-8` — X (Twitter) search via xAI's `x_search` Responses API tool; **no LinkedIn**
- **Verdict:** ✅ CORRECT (adds previously missing plugin/internals coverage; confirms X-only search, no LinkedIn)
- **Fix needed:** None

## Summary

All 8 key claims from the Hermes Agent wiki verified against source
(v0.19.0). This revision replaces several stale counts from the previous
verify pass:

- ✅ MCP: 10-tool bridge + 6 optional-mcps + catalog install (was: 3 optional-mcps, "90+ tools")
- ✅ Tools: 75 registered / 55 core / 33 toolsets (was: "90+ model tools")
- ✅ Skills: 14 built-in / 21 optional categories (was: 18 / 19)
- ✅ ACP: `hermes acp` is the server; registry + `serve` subcommand removed
- ✅ Terminal backends: seven incl. Vercel Sandbox (was: six)
- ✅ Gateway: 21 plugin platforms + 9 core (was: stale 20+ table)
- ✅ API server (8642) + dashboard (9119) now documented
- ✅ 90 slash commands, plugins, internals, LSP, tool-search, observability

## Related

- [[hermes-agent]] -- Main wiki entry
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-mcp-implementation]] -- MCP implementation details
- [[hermes-acp-implementation]] -- ACP implementation details
- [[hermes-gateway-api]] -- Gateway API reference
- [[hermes-gateway-platforms]] -- Gateway platform adapters
- [[hermes-plugins-architecture]] -- Plugin architecture

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
