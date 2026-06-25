---
name: goclaw-api
description: "GoClaw REST API — agent/tool management, webhook provisioning, SSE streaming"
tags: [ai-llm, cli, documentation, mcp, orchestration, plugin-sdk, rest-api, security, webhook]
---
# GoClaw REST API

**Source:** `/Users/admin1/Documents/knowledge/raw/goclaw/goclaw.xml`  
**Generated:** 2026-06-25

---

## Overview

GoClaw exposes a comprehensive REST API implemented via Go's standard `net/http.ServeMux`. All API handlers live in `internal/http/` and are wired in `cmd/gateway_http_handlers.go` and `cmd/gateway_http_wiring.go`. The API uses middleware for authentication and authorization (viewer/admin roles).

---

## 1. Architecture

### Handler Registration

In `cmd/gateway_http_handlers.go`, `wireHTTP()` creates all handler instances:

| Handler | Type | Responsibility |
|---------|------|----------------|
| `agentsH` | `*AgentsHandler` | Agent CRUD, workspace, prompts, export/import |
| `skillsH` | `*SkillsHandler` | Skills CRUD, evolution, versions, upload/download |
| `tracesH` | `*TracesHandler` | Run traces, timeline, session data |
| `mcpH` | `*MCPHandler` | MCP server CRUD, grants, OAuth, credentials |
| `channelInstancesH` | `*ChannelInstancesHandler` | Channel instances, contexts, capabilities |
| `providersH` | `*ProvidersHandler` | LLM provider CRUD, reconnect, model catalog |
| `builtinToolsH` | `*BuiltinToolsHandler` | Builtin tool settings, tenant overrides |
| `pendingMessagesH` | `*PendingMessagesHandler` | Pending message management |
| `teamEventsH` | `*TeamEventsHandler` | Team event webhooks |
| `secureCLIH` | `*SecureCLIHandler` | Secure CLI agent credentials, grants |
| `secureCLIGrantH` | `*SecureCLIGrantHandler` | Secure CLI grant management |
| `mcpUserCredsH` | `*MCPUserCredentialsHandler` | MCP user credentials |
| `mcpOAuthH` | `*MCPOAuthHandler` | MCP OAuth flow endpoints |

### Wiring

`wireHTTPHandlersOnServer()` in `cmd/gateway_http_wiring.go` registers all routes on an `http.ServeMux` and applies middleware.

### Auth Middleware

- `auth(next)` -- Requires valid session; returns user context
- `adminAuth(next)` -- Requires admin role (for mutating operations)
- Tenant-scoped: all queries filtered by `tenant_id` from auth context

---

## 2. Agent Management (`internal/http/agents.go`)

Handlers in `internal/http/agents.go`. `RegisterRoutes(prefix)` registers on the mux.

### Agents

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/agents` | `handleList` | List all agents (tenant-scoped) |
| POST | `/agents` | `handleCreate` | Create agent (with optional LLM summoning) |
| GET | `/agents/{key}` | `handleGet` | Get agent by ID or agent_key |
| PUT | `/agents/{key}` | `handleUpdate` | Update agent fields |
| DELETE | `/agents/{key}` | `handleDelete` | Delete agent |
| POST | `/agents/{key}/sync-workspace` | `handleSyncWorkspace` | Sync agent workspace |

Update validation:
- Request body capped at 64 KB (heap pressure protection)
- JSON update map whitelisted to known agent columns (column injection defense)
- `agent_key` changes enforce slug format
- Cache invalidation on update (Loop + bootstrap files)
- Status changes cascade to channel instances and cron jobs

### Agent Instances (`internal/http/agents_instances.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/agents/{key}/instances` | List agent instances |

### Agent Workspace (`internal/http/agents_workspace.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/agents/{key}/workspace` | Get agent workspace config |

### Agent Sharing (`internal/http/agents_sharing.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET/POST/PUT/DELETE | `/agents/{key}/sharing` | Tenant sharing management |

### Agent Export/Import

| Method | Route | File | Description |
|--------|-------|------|-------------|
| GET | `/agents/export` | `agents_export.go` | Export agent as archive |
| POST | `/agents/import` | `agents_import.go` | Import agent from archive |

### Agent Prompt Preview (`internal/http/agents_prompt_preview.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/agents/{key}/prompt-preview` | Generate system prompt preview |

---

## 3. Skills (`internal/http/skills.go`)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/skills` | `handleListSkills` | List skills |
| POST | `/skills` | `handleCreateSkill` | Create skill |
| GET | `/skills/{id}` | `handleGetSkill` | Get skill details |
| PUT | `/skills/{id}` | `handleUpdateSkill` | Update skill |
| DELETE | `/skills/{id}` | `handleDeleteSkill` | Delete skill |
| POST | `/skills/upload` | `handleUploadSkill` | Upload skill archive |
| GET | `/skills/{id}/export` | `handleExportSkill` | Export skill |
| POST | `/skills/{id}/grants` | `handleSetGrants` | Set skill grants |
| GET | `/skills/{id}/access` | `handleGetAccess` | Get effective access |

### Skills Evolution (`internal/http/skills_evolution.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/skills/{id}/evolution` | Get evolution settings |
| PATCH | `/skills/{id}/evolution` | Update evolution settings (enable, mode) |
| GET | `/skills/{id}/metrics` | Get skill usage metrics |
| GET | `/skills/{id}/activity` | Get skill activity log |
| GET | `/skills/{id}/suggestions` | List improvement suggestions |
| POST | `/skills/{id}/suggestions` | Create improvement suggestion |
| POST | `/skills/{id}/suggestions/{sg}/approve` | Approve suggestion |
| POST | `/skills/{id}/suggestions/{sg}/reject` | Reject suggestion |
| POST | `/skills/{id}/suggestions/{sg}/apply` | Apply suggestion patch |

### Skills Lifecycle (`internal/http/skills_lifecycle.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/skills/{id}/lifecycle` | Get lifecycle state |
| POST | `/skills/{id}/lifecycle/install` | Install skill |
| POST | `/skills/{id}/lifecycle/uninstall` | Uninstall skill |
| POST | `/skills/{id}/lifecycle/upgrade` | Upgrade skill version |

### Skills Versions (`internal/http/skills_versions.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/skills/{id}/versions` | List skill versions |
| GET | `/skills/{id}/versions/{v}` | Get specific version |

---

## 4. Providers (`internal/http/providers.go`)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/providers` | `handleListProviders` | List LLM providers |
| POST | `/providers` | `handleCreateProvider` | Add LLM provider |
| GET | `/providers/{name}` | `handleGetProvider` | Get provider details |
| PUT | `/providers/{name}` | `handleUpdateProvider` | Update provider |
| DELETE | `/providers/{name}` | `handleDeleteProvider` | Delete provider |
| POST | `/providers/{name}/reconnect` | `handleReconnectProvider` | Reconnect (test connection) |

Provider validation:
- URL validation (no SSRF -- only allowed localhost/internal for Ollama/ACP)
- API key masking in responses
- Ollama URL normalization (`/v1` suffix)
- Runtime registration status reported (`registered`, `disabled`, `skipped`, `missing_credential`, `invalid_config`)
- Cross-tenant owner super-admin support

### Provider Models (`internal/http/provider_models.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/providers/{name}/models` | List available models from provider |

- `fetchAnthropicModels()` -- Anthropic API models list
- `fetchGeminiModels()` -- Gemini API models list
- `fetchOpenAIModels()` -- OpenAI-compatible models list
- `fetchOllamaModels()` -- Ollama local models list

### Provider Embedding / Verification

| Method | Route | File | Description |
|--------|-------|------|-------------|
| POST | `/providers/{name}/verify` | `provider_verify.go` | Test provider connection |
| POST | `/providers/{name}/verify-embedding` | `provider_verify_embedding.go` | Test embedding capability |

---

## 5. MCP (`internal/http/mcp.go`)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/mcp/servers` | `handleListServers` | List MCP servers (with agent grant counts) |
| POST | `/mcp/servers` | `handleCreateServer` | Create MCP server config |
| GET | `/mcp/servers/{name}` | `handleGetServer` | Get MCP server details |
| PUT | `/mcp/servers/{name}` | `handleUpdateServer` | Update MCP server (OAuth fingerprint change purges tokens) |
| DELETE | `/mcp/servers/{name}` | `handleDeleteServer` | Delete MCP server |
| POST | `/mcp/servers/{name}/reconnect` | `handleReconnectServer` | Force reconnection |

Security validation: commands+args for stdio, URL for HTTP transports.

### MCP Grants (`internal/http/mcp_grants.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/mcp/servers/{name}/grants` | List agent grants for server |
| PUT | `/mcp/servers/{name}/grants` | Update grants (allow/deny tool lists per agent) |

### MCP OAuth (`internal/http/mcp_oauth.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/mcp/servers/{name}/oauth/start` | Start OAuth flow |
| GET | `/mcp/servers/{name}/oauth/callback` | OAuth callback |
| DELETE | `/mcp/servers/{name}/oauth/tokens` | Revoke OAuth tokens |

### MCP User Credentials (`internal/http/mcp_user_credentials.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/mcp/servers/{name}/user-credentials` | List user credentials |
| POST | `/mcp/servers/{name}/user-credentials` | Create user credential |
| PUT | `/mcp/servers/{name}/user-credentials/{id}` | Update user credential |
| DELETE | `/mcp/servers/{name}/user-credentials/{id}` | Delete user credential |

### MCP Tools (`internal/http/mcp_tools.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/mcp/servers/{name}/tools` | List tools exposed by server |

### MCP Export/Import

| Method | Route | File | Description |
|--------|-------|------|-------------|
| GET | `/mcp/export` | `mcp_export.go` | Export MCP server configurations |
| POST | `/mcp/import` | `mcp_import.go` | Import MCP server configurations |

---

## 6. Channel Instances (`internal/http/channel_instances.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/channel-instances` | List channel instances |
| POST | `/channel-instances` | Create channel instance |
| GET | `/channel-instances/{id}` | Get instance details |
| PUT | `/channel-instances/{id}` | Update instance |
| DELETE | `/channel-instances/{id}` | Delete instance |

### Channel Contexts (`internal/http/channel_instance_contexts.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/channel-instances/{id}/contexts` | List contexts |
| POST | `/channel-instances/{id}/contexts` | Create context |
| PUT | `/channel-instances/{id}/contexts/{ctx}` | Update context |
| DELETE | `/channel-instances/{id}/contexts/{ctx}` | Delete context |

### Channel Capabilities (`internal/http/channel_instance_capabilities.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/channel-instances/{id}/capabilities` | Get capabilities |

---

## 7. Sessions (`internal/http/sessions.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/sessions` | List sessions |
| GET | `/sessions/{id}` | Get session details |
| POST | `/sessions/{id}/branch` | Branch session |

### Session Branch Follow (`internal/http/sessions_branch_follow_test.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/sessions/{id}/branch/follow` | Follow branch to new session |

---

## 8. Webhooks (`internal/http/webhooks_*.go`)

| Method | Route | File | Description |
|--------|-------|------|-------------|
| POST | `/webhooks/message` | `webhooks_message.go` | Inbound message webhook |
| POST | `/webhooks/llm` | `webhooks_llm.go` | LLM webhook endpoint |
| POST | `/webhooks/admin` | `webhooks_admin.go` | Admin webhook |
| GET | `/webhooks/admin/calls` | `webhooks_admin_calls.go` | List admin webhook calls |

Webhook features:
- Authentication via configurable tokens
- Nonce validation
- Idempotency keys
- Rate limiting
- Media fetching from attachment URLs
- Context extraction

---

## 9. Auth & Security (`internal/http/auth.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/auth/login` | Login (API key, session token) |
| POST | `/auth/logout` | Logout |
| POST | `/auth/refresh` | Refresh session |

### API Keys (`internal/http/api_keys.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api-keys` | List API keys |
| POST | `/api-keys` | Create API key |
| DELETE | `/api-keys/{id}` | Revoke API key |

---

## 10. Knowledge Graph (`internal/http/knowledge_graph_handlers.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/knowledge-graph` | Query knowledge graph |
| POST | `/knowledge-graph` | Add to knowledge graph |

---

## 11. Memory (`internal/http/memory_handlers.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/memory` | Query episodic memory |
| POST | `/memory` | Store in episodic memory |
| DELETE | `/memory/{id}` | Delete memory entry |

---

## 12. Orchestration (`internal/http/orchestration_handlers.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/orchestration` | Get orchestration config |
| PUT | `/orchestration` | Update orchestration config |

---

## 13. Traces (`internal/http/traces.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/traces` | List run traces |
| GET | `/traces/{id}` | Get trace details |
| GET | `/traces/{id}/timeline` | Get run timeline |

### Trace Follow (`internal/http/traces_follow_test.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/traces/follow/{id}` | SSE stream for live trace updates |

---

## 14. Summoner (`internal/http/summoner.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/summon` | Summon agent by description (LLM-powered agent discovery) |
| POST | `/summon/{key}` | Summon specific agent by key |

### Summoner Prompts (`internal/http/summoner_prompts.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/summon/prompts` | List summoning prompts |
| POST | `/summon/prompts` | Create summoning prompt |

---

## 15. Chat (`internal/http/chat_completions.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/chat/completions` | OpenAI-compatible chat completions endpoint |
| POST | `/chat/completions/stream` | Streaming chat completions |

This route enables third-party tools to interact with GoClaw agents using the OpenAI chat completions API format.

---

## 16. Vault (`internal/http/vault_handlers.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/vault` | List vault entries |
| POST | `/vault` | Create vault entry |
| POST | `/vault/upload` | Upload to vault |
| GET | `/vault/tree` | Get vault tree structure |
| GET | `/vault/{path}` | Get vault file content |
| POST | `/vault/{path}/links` | Manage vault links |

---

## 17. Other Endpoints

| Method | Route | File | Description |
|--------|-------|------|-------------|
| GET | `/media/{token}` | `media_serve.go` | Serve uploaded media files |
| POST | `/media/upload` | `media_upload.go` | Upload media |
| GET | `/files/{path}` | `files.go` | Serve agent workspace files |
| POST | `/tts` | `tts.go` | Text-to-speech synthesis |
| GET | `/tts/config` | `tts_config.go` | TTS configuration |
| POST | `/tts/synthesize` | `tts_test.go` | Synthesize speech |
| GET | `/tts/capabilities` | `tts_capabilities.go` | TTS provider capabilities |
| POST | `/tts/test-connection` | `tts_test_connection.go` | Test TTS connection |
| POST | `/tools/invoke` | `tools_invoke.go` | Invoke a tool by name |
| POST | `/workspace/upload` | `workspace_upload.go` | Upload file to workspace |
| GET | `/backup/{name}` | `backup_handler.go` | Download backup |
| POST | `/backup` | `backup_handler.go` | Create backup |
| POST | `/restore` | `restore_handler.go` | Restore from backup |
| GET | `/tenants` | `tenants.go` | List tenants (system owner) |
| POST | `/tenants` | `tenants.go` | Create tenant |
| GET | `/users/search` | `user_search.go` | Search users |
| GET | `/browser-cookies` | `browser_cookies.go` | Get browser cookies |
| GET | `/voices` | `voices.go` | List available TTS voices |
| GET | `/evolve` | `evolution_handlers.go` | Evolution system status |
| GET | `/system-configs` | `system_configs.go` | System configuration |
| GET | `/edition` | `edition.go` | Get edition info |
| GET | `/wake` | `wake.go` | Health check/wake endpoint |
| GET | `/packages` | `packages.go` | List software packages |
| GET | `/not-found` | `api_not_found.go` | 404 catch-all handler |

---

## 18. OpenAPI Spec

An OpenAPI specification is available at `internal/http/openapi_spec.json` and served via `internal/http/openapi.go`.

---

## 19. Key Source Files

| File | Description |
|------|-------------|
| `internal/http/agents.go` | AgentsHandler with CRUD, RegisterRoutes, middleware |
| `internal/http/mcp.go` | MCPHandler with server CRUD, grants, OAuth |
| `internal/http/providers.go` | ProvidersHandler with provider CRUD, validation |
| `internal/http/skills.go` | SkillsHandler with CRUD, lifecycle, evolution |
| `internal/http/sessions.go` | Session management |
| `internal/http/auth.go` | Authentication and API keys |
| `internal/http/chat_completions.go` | OpenAI-compatible chat completions |
| `internal/http/response_helpers.go` | JSON response helpers |
| `internal/http/tenant_cache.go` | Tenant-scoped cache control |
| `cmd/gateway_http_handlers.go` | `wireHTTP()` for handler creation |
| `cmd/gateway_http_wiring.go` | `wireHTTPHandlersOnServer()` for route registration |
| `cmd/gateway_http_client.go` | HTTP client for backend services |
