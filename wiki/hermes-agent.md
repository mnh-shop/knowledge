---
name: hermes-agent
tags: [acp, hermes-agent, agent, agent-gateway, cli, container, dashboard, desktop, docker, git, lsp, mcp, messaging, multi-platform, observability, orchestration, quadlet, systemd, webhook, wiki, python, typescript, nix]
description: "Wiki entry for Hermes Agent: self-improving AI agent by Nous Research with multi-platform messaging (MIT, v0.19.0)"
source: sources/hermes-agent/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Hermes Agent

| Field | Value |
|---|---|
| **Origin** | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) |
| **License** | MIT |
| **Version** | 0.19.0 (`hermes_cli/__init__.py:17`) |
| **Source** | `sources/hermes-agent/` |
| **Repomix** | `raw/hermes-agent/hermes-agent.xml` (35MB) |
| **Codegraph** | `graphs/hermes-agent/` (3,726 files) |
| **Profile** | `sources/hermes-agent/AGENTS.md` |

## What is it?

A self-improving personal AI agent built by Nous Research. Runs the same
core across CLI, TUI, Electron desktop, and ~30 messaging platforms
(Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost, etc.).

It is simultaneously:

- An **agent runtime** — conversation loop, tool dispatch, memory,
  skills, delegation, cron, and self-improvement loops.
- A **multi-platform messaging gateway** — the same agent reachable from
  ~30 chat platforms through a unified adapter pattern.
- An **MCP hub** — MCP client (consumes external MCP servers), MCP
  server (10-tool messaging bridge), and a curated MCP catalog
  (`optional-mcps/`, 6 manifests) with one-click install.
- An **ACP server + client** — drives editor integrations (Zed, Claude
  Code, Cursor) and talks to Copilot over ACP.
- An **OpenAI-compatible REST API server** (port 8642) and a **dashboard
  web server** (port 9119).
- An **orchestration target** — 18 plugin directories, profiles /
  multi-instance, gateway relay, LSP integration, OTLP observability.

Key features:

- Multi-platform messaging gateway (21 plugin platforms + 9 core)
- Closed learning loop (memory, skills, curator, self-improvement)
- Scheduled automations (cron)
- Subagent delegation and parallelization (`delegate_task`, MoA)
- MCP client + server + curated catalog
- ACP server for editor integration (Zed, Claude Code, etc.)
- Seven terminal backends (local, Docker, SSH, Singularity, Modal,
  Daytona, Vercel Sandbox)
- OpenAI-compatible REST API (port 8642) and dashboard (port 9119)
- 75 registered core tools across 33 toolsets
- LSP integration, tool-search bridge, OTLP observability

---

## Where to find things

### Architecture & Design

| What | Where |
|---|---|
| Full architecture | [[hermes-agent-architecture]] (`domains/architecture/`) |
| Design principles | `sources/hermes-agent/AGENTS.md` |
| Source map | `domains/architecture/hermes-agent-architecture.md` (#key-source-map) |

### MCP

Hermes is an MCP client (consumes MCP servers), an MCP server (10-tool
messaging bridge), and ships a curated MCP catalog.

| What | Where |
|---|---|
| **MCP Server (bridge)** | [[hermes-mcp-serve]] (`assets/mcp-servers/`) |
| **MCP Server source** | `mcp_serve.py` → 10 tools (lines 557-925) |
| **MCP Client (consumer)** | `tools/mcp_tool.py` → `MCPServerTask` |
| MCP implementation patterns | [[hermes-mcp-implementation]] (`domains/mcp/`) |
| MCP OAuth | `tools/mcp_oauth_manager.py` |
| MCP catalog (curated) | `hermes_cli/mcp_catalog.py` + `optional-mcps/` (6 manifests) |
| Optional MCP manifests | `optional-mcps/` → blender, comfy-cloud, figma, linear, n8n, unreal-engine |
| MCP-as-tools server | `agent/transports/hermes_tools_mcp_server.py` (Hermes model tools exposed as MCP for Codex) |
| CLI | `hermes mcp` → subcommands `serve`, `catalog`, `install`, `picker`, `reauth`, `list`, `update`, `test` (`hermes_cli/subcommands/mcp.py`) |

**Important:** The primary MCP server (`mcp_serve.py`) is a *messaging
bridge*, not a generic tool exporter. It exposes exactly **10 tools** for
listing/sending conversations — `conversations_list`, `conversation_get`,
`messages_read`, `attachments_fetch`, `events_poll`, `events_wait`,
`messages_send`, `channels_list`, `permissions_list_open`,
`permissions_respond` — matching OpenClaw's 9-tool surface plus
Hermes-specific `channels_list`. The header says so explicitly
(`mcp_serve.py:9-11`): "Matches OpenClaw's 9-tool MCP channel bridge
surface."

**Second MCP server:** `agent/transports/hermes_tools_mcp_server.py`
exposes a curated subset of Hermes model tools (web_search, browser_*,
vision_analyze, image_generate, skill_view, text_to_speech, kanban_*) as a
stdio MCP server so spawned Codex subprocesses can reach Hermes
capabilities (`~/.codex/config.toml [mcp_servers.hermes-tools]`).

**MCP catalog:** `hermes mcp catalog` lists Nous-approved MCP servers;
`hermes mcp install <name>` installs one. Entries live under
`optional-mcps/<name>/manifest.yaml` and ship disabled
(`hermes_cli/mcp_catalog.py:1-15`, `hermes_cli/subcommands/mcp.py:110-128`).
The six curated manifests: **blender, comfy-cloud, figma, linear, n8n,
unreal-engine**.

### ACP

Hermes is an ACP server (driven by editors) and has an ACP client (talks
to Copilot). Since commit `d84e11af4` ("rip out brew + pip/PyPI wheel
support") the standalone `acp_registry/agent.json` was **removed** — there
is no ACP registry directory anymore.

| What | Where |
|---|---|
| **ACP Server** | [[hermes-acp-agent]] (`assets/acp-agents/`) |
| ACP implementation patterns | [[hermes-acp-implementation]] (`domains/acp/`) |
| ACP server source | `acp_adapter/server.py` → `HermesACPAgent` |
| ACP client (Copilot) | `agent/copilot_acp_client.py` |
| CLI | `hermes acp` — **the ACP server itself** (no `serve` subcommand) |

**`hermes acp` IS the server.** It runs the ACP protocol directly; flags are
`--version`, `--check`, `--setup`, `--setup-browser`, `--yes`
(`hermes_cli/subcommands/acp.py:16-49`). Capabilities advertised include
`load_session`, `prompt_capabilities.image`, and
`session_capabilities.fork/list/resume` (`acp_adapter/server.py`).

### Gateway (Messaging Platforms)

The gateway connects ~30 messaging platforms. Most are **plugin**
platforms (`plugins/platforms/`, 21 adapters); a smaller core set remains
in `gateway/platforms/` (9 adapters).

| What | Where |
|---|---|
| **Platform adapters** | [[hermes-gateway-platforms]] (`assets/api-clients/`) |
| Gateway API architecture | [[hermes-gateway-api]] (`domains/api/`) |
| Base adapter class | `gateway/platforms/base.py` → `BasePlatformAdapter` |
| Gateway bootstrap | `gateway/run.py` |
| Stream dispatch | `gateway/stream_dispatch.py` → `GatewayEventDispatcher` |
| Platform registry | `gateway/platform_registry.py` → `PlatformRegistry` (self-registering, incl. plugin adapters) |
| Webhook adapter | `gateway/platforms/webhook.py` → `WebhookAdapter` |
| Plugin platforms (21) | `plugins/platforms/` → buzz, dingtalk, discord, email, feishu, google_chat, homeassistant, irc, line, matrix, mattermost, ntfy, photon, raft, simplex, slack, sms, teams, telegram, wecom, whatsapp |
| Core platforms (9) | `gateway/platforms/` → api_server, signal, weixin, yuanbao, qqbot, bluebubbles, whatsapp_cloud, msgraph_webhook, webhook |
| Gateway Relay (experimental) | `gateway/relay/` + `docs/relay-connector-contract.md` |
| CLI | `hermes gateway` → `run`, `start`, `stop`, `restart`, `status`, `install`, `uninstall`, `setup`, `list`, `enroll`, `migrate-legacy` |

**Platform split:** the platform table in older wiki revisions is stale —
nearly every platform has moved to plugin form. The 21 plugin platforms
self-register into `PlatformRegistry` via `PluginContext.register_platform()`.
The 9 core adapters remaining in `gateway/platforms/` are api_server
(OpenAI-compatible REST), signal, weixin, yuanbao, qqbot, bluebubbles,
whatsapp_cloud, msgraph_webhook, and webhook.

**Gateway Relay (experimental):** `gateway/relay/adapter.py` implements a
single generic `RelayAdapter` that dials **out** to a Node/TypeScript
connector (`NousResearch/gateway-gateway`), receives a `CapabilityDescriptor`
at handshake, then exchanges normalized `MessageEvent`s over a per-turn
bidirectional WebSocket. The gateway never learns which concrete platform is
fronting it — the connector owns platform-specific socket/identity logic
(`docs/relay-connector-contract.md`, `gateway/relay/ws_transport.py`).

### Terminal Backends

Seven terminal backends for agent environment execution
(`tools/environments/`; README.md:29):

| Backend | Module |
|---|---|
| Local | `tools/environments/local.py` |
| Docker | `tools/environments/docker.py` |
| SSH | `tools/environments/ssh.py` |
| Singularity | `tools/environments/singularity.py` |
| Modal | `tools/environments/modal.py` |
| Managed Modal | `tools/environments/managed_modal.py` (managed variant of Modal) |
| Daytona | `tools/environments/daytona.py` |
| Vercel Sandbox | `tools/environments/vercel_sandbox.py` |

Daytona and Modal offer serverless persistence — the agent environment
hibernates when idle and wakes on demand. Shared helpers live in
`base.py`, `file_sync.py`, and `modal_utils.py`.

### Core Agent

| What | Source |
|---|---|
| Conversation loop | `agent/conversation_loop.py` → `AIAgent.run_conversation()` |
| Tool dispatch | `agent/tool_dispatch_helpers.py` |
| Tool executor | `agent/tool_executor.py` |
| Memory manager | `agent/memory_manager.py` |
| Context compressor | `agent/context_compressor.py` |
| System prompt | `agent/prompt_builder.py` |
| Prompt caching | `agent/prompt_caching.py` |
| Model adapters | `agent/anthropic_adapter.py`, `gemini_native_adapter.py`, `bedrock_adapter.py`, `vertex_adapter.py`, `codex_responses_adapter.py`, `azure_identity_adapter.py`, `lmstudio_reasoning.py` |
| Auxiliary model router | `agent/auxiliary_client.py` (side-task resolution chain) |
| Credential pool | `agent/credential_pool.py` (multi-credential failover per provider) |
| Iteration budget | `agent/iteration_budget.py` (parent 500 / subagent 50 default) |
| Goals | `hermes_cli/goals.py` → `GoalManager` (`/goal set|draft|show|status`) |
| Mixture of Agents | `agent/moa_loop.py`, `agent/moa_trace.py`, `hermes_cli/moa_cmd.py` |
| Tracks | `agent/trajectory.py` |
| Skill curator | `agent/curator.py`, `hermes_cli/curator.py` |

### Skills System

| What | Source |
|---|---|
| Skills hub (search) | `tools/skills_hub.py` — 9 source classes |
| Skills tool | `tools/skills_tool.py` |
| Skill manager | `tools/skill_manager_tool.py` |
| Skill bundles | `tools/skills_hub.py` → `SkillBundle` |
| Built-in skills | `skills/` → **14 categories, 70 SKILL.md files** |
| Optional skills | `optional-skills/` → **21 categories, 111 SKILL.md files** |

**Skills hub sources (`tools/skills_hub.py`):** GitHubSource (line 557),
WellKnownSkillSource (1196), UrlSource (1423), SkillsShSource (1609),
ClawHubSource (2185), LobeHubSource (2731), BrowseShSource (2891),
OptionalSkillSource (3065), HermesIndexSource (3793). What earlier wiki
revisions called "Claude Marketplace" is really **ClawHub + Anthropic
GitHub skills** — there is no separate marketplace source.

**Built-in skills (14 categories):** apple, autonomous-ai-agents, creative,
email, github, index-cache, media, mlops, note-taking, productivity,
research, smart-home, social-media, software-development — 70 SKILL.md files.

**Optional skills (21 categories):** autonomous-ai-agents, blockchain,
communication, creative, data-science, devops, dogfood, email, finance,
gaming, health, mcp, migration, mlops, payments, productivity, research,
security, software-development, web-development, yuanbao — 111 SKILL.md
files (plus a `DESCRIPTION.md`).

### Plugin System

18 plugin directories under `plugins/`:

| Plugin | Purpose |
|---|---|
| `browser/` | Browser automation backend |
| `context_engine/` | Context management |
| `cron_providers/` | Scheduled job providers |
| `dashboard_auth/` | Dashboard authentication providers |
| `disk-cleanup/` | Disk space maintenance |
| `google_meet/` | Google Meet integration |
| `hermes-achievements/` | Achievement system |
| `image_gen/` | Image generation |
| `kanban/` | Kanban board coordination |
| `memory/` | Memory backends (8 providers) |
| `model-providers/` | Model providers (33 packages) |
| `observability/` | Langfuse + Nemo relay OTLP traces |
| `platforms/` | 21 messaging platform adapters |
| `security-guidance/` | Security recommendations |
| `spotify/` | Spotify control |
| `teams_pipeline/` | Teams pipeline automation |
| `video_gen/` | Video generation |
| `web/` | Web platform tools |

**Memory providers (8):** honcho, mem0, supermemory, byterover, hindsight,
holographic, openviking, retaindb (`plugins/memory/`).

**Model providers (33 packages):** ai-gateway, alibaba, alibaba-coding-plan,
anthropic, arcee, azure-foundry, bedrock, copilot, copilot-acp, custom,
deepinfra, deepseek, fireworks, gemini, gmi, huggingface, kilocode,
kimi-coding, minimax, nous, novita, nvidia, ollama-cloud, openai-codex,
opencode-zen, openrouter, qwen-oauth, stepfun, upstage, vertex, xai,
xiaomi, zai (`plugins/model-providers/`).

**Observability plugins:** `plugins/observability/langfuse/` (Langfuse
traces for conversations/LLM calls/tools; env: `HERMES_LANGFUSE_PUBLIC_KEY`,
`HERMES_LANGFUSE_SECRET_KEY`) and `plugins/observability/nemo_relay/`
(Nous relay). Core OTLP scaffolding in `hermes_cli/observability/`
(shared_metrics, schemas, relay_runtime).

### Tools & Toolsets

**75 registered core tools** via `registry.register()` across `tools/**`
(55 always-loaded core tools in `_HERMES_CORE_TOOLS`, `toolsets.py:31-82`).
Tools are grouped into **33 toolsets** (`toolsets.py:97`): browser,
clarify, code_execution, coding, computer_use, context_engine, cronjob,
debugging, delegation, discord, discord_admin, feishu_doc, feishu_drive,
file, homeassistant, image_gen, kanban, memory, project, safe, search,
session_search, skills, spotify, terminal, todo, tts, video, video_gen,
vision, web, x_search, yuanbao.

Key tool sources:

| Tool | Source |
|---|---|
| Browser | `tools/browser_tool.py`, `tools/browser_cdp_tool.py`, `tools/browser_dialog_tool.py` |
| Code execution | `tools/code_execution_tool.py` |
| Computer use | `tools/computer_use/`, `tools/computer_use_tool.py` |
| Delegation | `tools/delegate_tool.py`, `tools/async_delegation.py` |
| File operations | `tools/file_tools.py`, `tools/file_operations.py` |
| MCP client | `tools/mcp_tool.py` |
| Memory | `tools/memory_tool.py` |
| Skills | `tools/skills_hub.py`, `tools/skills_tool.py`, `tools/skill_manager_tool.py` |
| Terminal | `tools/terminal_tool.py` |
| Vision | `tools/vision_tools.py` |
| Web search | `tools/web_tools.py` |
| X (Twitter) search | `tools/x_search_tool.py` — **X/Twitter only, via xAI** (no LinkedIn) |
| Cron | `tools/cronjob_tools.py` |
| Voice/TTS | `tools/transcription_tools.py`, `tools/tts_tool.py`, `tools/tts_streaming.py` |
| Image gen | `tools/image_generation_tool.py` |
| Video gen | `tools/video_generation_tool.py`, `tools/xai_video_tools.py` |
| Kanban | `tools/kanban_tools.py` |
| Home Assistant | `tools/homeassistant_tool.py` |
| Discord | `tools/discord_tool.py` |
| Feishu | `tools/feishu_doc_tool.py`, `tools/feishu_drive_tool.py` |
| Session search | `tools/session_search_tool.py` |
| Todo | `tools/todo_tool.py` |
| Project (desktop) | `tools/project_tools.py` |
| Desktop pane tools | `tools/read_terminal_tool.py`, `tools/close_terminal_tool.py`, `tools/open_preview_tool.py`, `tools/focus_pane_tool.py`, `tools/react_to_message_tool.py` |

**Tool search bridge (progressive disclosure):** when MCP/plugin tools are
present, `tools/tool_search.py` replaces them with three bridge tools —
`tool_search`, `tool_describe`, `tool_call` — surfaced on demand. Core
Hermes tools (`_HERMES_CORE_TOOLS`) are never deferred. Tiered disclosure:
Tier 0 pure passthrough, Tier 1 bridge + name/description listing, Tier 2
bare bridge + per-server summary (e.g. Cloudflare's ~3,300 flat API
tools).

### OpenAI-Compatible REST API Server

`gateway/platforms/api_server.py` — a full OpenAI-compatible HTTP gateway on
port **8642** (`DEFAULT_PORT = 8642`, api_server.py:124). Any OpenAI client
works by pointing at `http://localhost:8642/v1` (api_server.py:27).

| Endpoint | Description |
|---|---|
| `POST /v1/chat/completions` | OpenAI Chat Completions format (stateless; session continuity via `X-Hermes-Session-Id`, memory scoping via `X-Hermes-Session-Key`) |
| `POST /v1/responses` | OpenAI Responses API format (stateful via `previous_response_id`) |
| `GET/DELETE /v1/responses/{response_id}` | Retrieve/delete stored responses |
| `POST /v1/runs` | Start a run, returns `run_id` immediately (202) |
| `GET /v1/runs/{run_id}` | Run status |
| `GET /v1/runs/{run_id}/events` | SSE stream of lifecycle events |
| `POST /v1/runs/{run_id}/approval` | Resolve a pending run approval |
| `POST /v1/runs/{run_id}/stop` | Interrupt a running agent |
| `GET/POST /api/sessions` | List/create Hermes sessions |
| `GET/PATCH/DELETE /api/sessions/{id}` | Read/update/delete a session |
| `GET /api/sessions/{id}/messages` | Session message history |
| `POST /api/sessions/{id}/fork` | Branch a session via SessionDB lineage |
| `POST /api/sessions/{id}/chat[/stream]` | Chat with a persisted session |
| `GET /health`, `GET /health/detailed` | Health checks (detailed for cross-container dashboard probing) |

Per-profile mounts supported (`/p/<profile>/v1/...`, api_server.py:35).

### Dashboard Web Server

`hermes_cli/web_server.py` — dashboard web server on port **9119**
(`python -m hermes_cli.main dashboard`; start on `http://127.0.0.1:9119`,
web_server.py:8). **140+ routes** — `@app.get/post/put/delete` decorators
plus WebSocket endpoints — covering `/api/*` for chat, sessions, files
(read/download/upload/upload-stream/mkdir), media, images, settings,
plugins, MCP, models, and more (`/api/media` at web_server.py:1999,
`/api/chat/image-upload` at 2276, `/api/files*` at 2319+).

- Serves a built SPA from `web/` (compiled to `hermes_cli/web_dist/`).
- Auth-gated (`plugins/dashboard_auth/` providers register before a
  fail-closed gate check; `should_require_auth`).
- The desktop app's in-process `/api/ws` gateway builds agents via
  `tui_gateway/server.py`; background MCP discovery is spawned so desktop
  sessions see MCP tools.
- Web UI project in `web/` (React/TypeScript).

### LSP Integration

`agent/lsp/` — Language Server Protocol support: `client.py`, `manager.py`
(multi-server lifecycle), `servers.py` (server registry), `protocol.py`,
`install.py`, `range_shift.py`, `reporter.py`, `eventlog.py`, plus a CLI
entry (`cli.py`). `hermes lsp` subcommand in the CLI.

### Profiles & Multi-Instance

`hermes_cli/profiles.py` — profiles let you run multiple independent agent
configurations on one machine. `-p/--profile <name>` selects one
(`hermes_cli/_parser.py:21-22`). Subcommands: `hermes profile list|use|
create|delete|describe|show|alias`. Companion modules:
`profile_describer.py`, `profile_distribution.py`. Each profile has its own
gateway status (`hermes gateway list` shows per-profile status).

**Skin engine:** `hermes_cli/skin_engine.py` — the `/skin` slash command and
`hermes skin` subcommand list/switch/tweak UI skins.

### Desktop & UI

| What | Source |
|---|---|
| Electron desktop | `apps/desktop/` (+ `apps/shared/`, `apps/bootstrap-installer/`) |
| TUI | `ui-tui/` |
| Web dashboard UI | `web/` (React/TypeScript SPA) |
| Documentation website | `website/` |

---

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Python (agent/gateway/CLI), TypeScript (web UI), TypeScript/Node (connector, gateway-gateway) |
| MCP | stdio + HTTP (SSE/streamable) client; stdio server (10-tool bridge); catalog installs |
| ACP | Server (`acp_adapter/server.py`) + Copilot client |
| Terminal backends | local, docker, ssh, singularity, modal, managed_modal, daytona, vercel_sandbox |
| Model providers | 33 packages (Anthropic, OpenAI, Gemini, Bedrock, Vertex, xAI, DeepSeek, OpenRouter, Nous Portal, …) |
| Memory backends | 8 (honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb) |
| Observability | Langfuse + nemo_relay plugins, OTLP shared metrics |
| Database | SQLite (sessions, memory, kanban.db, etc.) |
| Packaging | uv/PyPI, Docker, Nix flake, quadlet |

---

## CLI reference

The CLI is the main entry point (`hermes_cli/main.py`, ~12k lines).
`_BUILTIN_SUBCOMMANDS` (main.py:10461-10473) enumerates the full surface.
The gateway subcommand has `run|start|stop|restart|status|install|
uninstall|setup|list|enroll|migrate-legacy` (hermes_cli/subcommands/gateway.py).

### Agent & session commands

| Command | What it does |
|---|---|
| `hermes` / `hermes chat` | Start chat (CLI or TUI) |
| `hermes model` | Switch models/providers |
| `hermes moa` | Configure Mixture of Agents provider/model slots (`list`, `configure`, `delete`) |
| `hermes fallback` | Manage fallback provider chain (`list`, `add`, `remove`, `clear`) |
| `hermes sessions` | Manage sessions |
| `hermes memory` | Manage memory |
| `hermes migrate` | Migration guide (OpenClaw → Hermes + Honcho) |
| `hermes import` / `hermes import-agent` | Import agents/configs |
| `hermes console` | Console commands |
| `hermes journey` | Learned skills + memories over time timeline |
| `hermes memory-graph` / `hermes learning` | Memory graph / learning views |

### Gateway & messaging

| Command | What it does |
|---|---|
| `hermes gateway run` | Run gateway in foreground |
| `hermes gateway start` / `stop` / `restart` / `status` | Gateway service lifecycle |
| `hermes gateway install` / `uninstall` | Install/uninstall gateway service |
| `hermes gateway setup` | Configure messaging platforms |
| `hermes gateway list` | List all profiles + gateway status |
| `hermes gateway enroll` | Enroll a profile |
| `hermes gateway migrate-legacy` | Migrate legacy gateway config |
| `hermes webhook` | Webhook management |
| `hermes whatsapp` / `hermes whatsapp-cloud` | WhatsApp / WhatsApp Cloud setup |
| `hermes slack` | Slack setup |
| `hermes pairing` | Device pairing |

### Platforms, tools & models

| Command | What it does |
|---|---|
| `hermes plugins` | Plugin management (`list`, `enable`, `disable`) |
| `hermes skills` | Install/browse skills |
| `hermes tools` | List/disable/enable/post-setup tools |
| `hermes mcp` | MCP management (`serve`, `catalog`, `install`, `picker`, `reauth`, `list`, `update`, `test`) |
| `hermes acp` | ACP server (`--version/--check/--setup/--setup-browser/--yes`) |
| `hermes skin` | List/switch/tweak UI skins |
| `hermes model` | Model switching |

### Security, secrets & config

| Command | What it does |
|---|---|
| `hermes secrets` | External secret managers: `bitwarden` (`bw`), `op` (1Password) |
| `hermes security` | Security settings (redact_secrets, approvals) |
| `hermes approvals` | Persistent dangerous-command approval mode |
| `hermes config` | Configuration |
| `hermes auth` / `hermes login` / `hermes logout` | Provider auth |
| `hermes setup` | First-time setup wizard |

### System, status & maintenance

| Command | What it does |
|---|---|
| `hermes status` | Status of all components |
| `hermes doctor` | Diagnostics |
| `hermes update` | Self-update |
| `hermes uninstall` | Uninstall |
| `hermes version` | Version |
| `hermes backup` | Backup |
| `hermes checkpoints` | Checkpoint management |
| `hermes bundles` | Skill bundles (aliases for multiple skills) |
| `hermes curator` | Background skill maintenance (`status`, `run`, `pause`, `pin`) |
| `hermes pets` | Petdex animated mascots (CLI/TUI/desktop) |
| `hermes computer-use` | Computer-use setup |
| `hermes hooks` | Hook management |
| `hermes insights` | Usage insights and analytics |
| `hermes monitoring` | Monitoring |
| `hermes logs` | Logs |
| `hermes dump` | Dump diagnostics |
| `hermes debug` | Debugging |
| `hermes completion` | Shell completion |
| `hermes egress` | Docker egress proxy status |

### Servers & utilities

| Command | What it does |
|---|---|
| `hermes dashboard` / `hermes serve` | Dashboard web server (port 9119) |
| `hermes desktop` / `hermes gui` | Desktop app (gui is a deprecated alias) |
| `hermes portal` | Nous Portal status + Tool Gateway routing |
| `hermes proxy` | Local OpenAI-compatible proxy to OAuth providers |
| `hermes send` | Send messages |
| `hermes kanban` | Multi-profile collaboration board |
| `hermes project` | Desktop Project tools |
| `hermes lsp` | LSP integration |
| `hermes migrate` | Migration tooling |
| `hermes honcho` | Honcho memory migration |
| `hermes claw` | OpenClaw migration (`migrate --dry-run`) |
| `hermes console` | Console |

### Slash commands (in-chat)

The chat interface registers **90 slash commands** in `COMMAND_REGISTRY`
(`hermes_cli/commands.py:101`). Full list: start, new topic, clear,
redraw, history, save, retry, prompt, undo, title, handoff, branch,
compress, rollback, snapshot, stop, approve, deny, background, agents,
journey, queue, steer, goal, moa, subgoal, status, egress, context,
whoami, profile, sethome, resume, sessions, config, model, codex-runtime,
personality, statusbar, battery, timestamps, diff, verbose, focus,
footer, yolo, approvals, reasoning, fast, skin, indicator, voice, wake,
busy, tools, toolsets, skills, memory, bundles, pet, hatch, learn, init,
cron, suggestions, blueprint, curator, kanban, reload, reload-mcp,
reload-skills, browser, plugins, commands, help, restart, usage,
subscription, topup, insights, platforms, platform, copy, paste, image,
update, version, debug, quit.

---

## Security & Safety

| Surface | Where |
|---|---|
| Approval system | `/approve`, `/deny`, `/approvals` slash commands; `hermes approvals` persistent mode; `/v1/runs/{id}/approval` API |
| Dangerous-command guardrails | `agent/tool_guardrails.py`, `tools/slash_confirm.py` |
| Prompt-injection hardening | `_HERMES_WEBHOOK_SAFE_TOOLS` (toolsets.py:86-91) — webhook events get an intentionally constrained toolset |
| Secret management | `hermes_cli/security.py` (redact_secrets), `agent/credential_pool.py`, `agent/credential_persistence.py`; external secret managers via `hermes secrets bitwarden|op` |
| Dashboard auth | `plugins/dashboard_auth/` — fail-closed gate; `should_require_auth()` in `hermes_cli/web_server.py` |
| OAuth | `tools/mcp_oauth_manager.py` (streaming OAuth for remote MCP), `hermes mcp reauth --all` |
| Terminal sandboxing | `tools/terminal_tool.py` with per-backend isolation (Docker/SSH/Singularity/Modal/Daytona/Vercel Sandbox) |
| Egress control | `/egress` slash command + `hermes egress` — Docker egress proxy status |

## Notable subsystems & entry points

| Subsystem | Entry point | Notes |
|---|---|---|
| `run_agent` | `run_agent.py` | Parent/subagent orchestration; re-exports `IterationBudget` |
| Subagent lifecycle | `agent/subagent_lifecycle.py` | Delegation + parallelization bookkeeping |
| Conversation compression | `agent/conversation_compression.py`, `agent/context_compressor.py` | Long-session management |
| Tool guardrails | `agent/tool_guardrails.py` | Safety checks on tool calls |
| Trajectory | `agent/trajectory.py` | Tracks (turn traces) |
| MoA loop | `agent/moa_loop.py`, `agent/moa_trace.py` | Mixture of Agents; `/moa` + `hermes moa` |
| Goals | `hermes_cli/goals.py` | `/goal set|draft|show|status|pause|resume|clear`; `GoalManager` |
| Curator | `agent/curator.py`, `hermes_cli/curator.py` | Auxiliary-model skill maintenance (pin/prune/archive) |
| Pets | `hermes pets` | Petdex animated mascots (CLI/TUI/desktop) |
| Skin engine | `hermes_cli/skin_engine.py` | `/skin`, `hermes skin` |
| Tool search bridge | `tools/tool_search.py` | `tool_search`/`tool_describe`/`tool_call` progressive disclosure |
| LSP | `agent/lsp/` | Client + multi-server manager; `hermes lsp` |
| Gateway relay | `gateway/relay/` | Experimental outbound connector adapter |
| Observability | `hermes_cli/observability/`, `plugins/observability/langfuse`, `plugins/observability/nemo_relay` | OTLP shared metrics, Langfuse traces |
| Background MCP discovery | `hermes_cli/mcp_startup.py` | `start_background_mcp_discovery` for dashboard/desktop sessions |
| Web dist | `web/` → `hermes_cli/web_dist/` | Built SPA served by dashboard |

---

## Deployment

| What | Where |
|---|---|
| Dockerfile | `sources/hermes-agent/Dockerfile` |
| Docker Compose | `sources/hermes-agent/docker-compose.yml` |
| Nix | `sources/hermes-agent/flake.nix` |
| Script | `sources/hermes-agent/setup-hermes.sh` |
| Install (end-user) | `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash` |
| **Deployment guide** | `domains/deployment/hermes-agent-deployment.md` |
| **Quadlet** | `assets/deployment/hermes-agent-quadlet.md` |

---

## Related

- [[hermes-profiles]] -- Agent profile / development guidelines
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-agent-deployment]] -- Deployment guide
- [[hermes-agent-docker]] -- Docker packaging
- [[hermes-agent-docker-deployment]] -- Docker deployment guide
- [[hermes-agent-quadlet]] -- Quadlet deployment
- [[hermes-acp-agent]] -- ACP agent configuration
- [[hermes-acp-implementation]] -- ACP implementation
- [[hermes-gateway-api]] -- Gateway API reference
- [[hermes-gateway-platforms]] -- Gateway platform adapters
- [[hermes-mcp-serve]] -- MCP messaging bridge
- [[hermes-mcp-implementation]] -- MCP implementation

## Related

| Repo | Relationship |
|---|---|
| [[openclaw]] | Another agent framework — MCP bridge surface is intentionally compatible |
| [[agentfield]] | ✅ MCP bridge | AgentField MCP bridge (`assets/mcp-servers/agentfield-mcp-server.md`) wraps AgentField REST API as MCP tools for Hermes. AgentField `app.harness()` could dispatch to Hermes for LLM execution |
| [[hermes-workspace]] | Hermes workspace environment (isolated dev/testing workspace) |
| [[hermes-startup-architect]] | Startup architect skill for Hermes |
| [[hermes-agent]] reference | `assets/agent-references/hermes-agent-reference.md` (dev guidelines from AGENTS.md) |

## Cross-project

- [[openclaw]] — Competing agent gateway (TypeScript, MIT)
- [[agentfield]] — Control plane that can orchestrate Hermes agents via MCP
- [[mission-control]] — Dashboard that can connect to Hermes gateway
- [[podman]] — Container runtime Hermes agents run inside
- [[n8n]] — Workflow engine callable from Hermes MCP tools
- [[hermzner]] — Deployment blueprint for Hermes on Hetzner
- [[tank-os]] — Bootc OS pattern applicable to Hermes deployment
- [[goclaw]] — Go-based agent gateway with compatible MCP surface
- [[clawpier]] — Desktop GUI for managing Hermes Docker containers
- [[buildah]] — Builds the container images Hermes agents run inside
- [[nix-podman-stacks]] — Declarative Nix-based container infrastructure
- [[sablier]] — Scale-to-zero for Hermes agent services
- [[gogs]] — Self-hosted Git backend for agent code repositories
