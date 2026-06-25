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
| GET | `/v1/agents` | `handleList` | List all agents (tenant-scoped) |
| POST | `/v1/agents` | `handleCreate` | Create agent (with optional LLM summoning) |
| GET | `/v1/agents/{id}` | `handleGet` | Get agent by ID or agent_key |
| PUT | `/v1/agents/{id}` | `handleUpdate` | Update agent fields |
| DELETE | `/v1/agents/{id}` | `handleDelete` | Delete agent |
| POST | `/v1/agents/{id}/sync-workspace` | `handleSyncWorkspace` | Sync agent workspace |

Update validation:
- Request body capped at 64 KB (heap pressure protection)
- JSON update map whitelisted to known agent columns (column injection defense)
- `agent_key` changes enforce slug format
- Cache invalidation on update (Loop + bootstrap files)
- Status changes cascade to channel instances and cron jobs

### Agent Instances (`internal/http/agents_instances.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/agents/{id}/instances` | List agent instances |

### Agent Workspace (`internal/http/agents_workspace.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/agents/{id}/workspace` | Get agent workspace config |

### Agent Sharing (`internal/http/agents_sharing.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET/POST/PUT/DELETE | `/v1/agents/{id}/sharing` | Tenant sharing management |

### Agent Export/Import

| Method | Route | File | Description |
|--------|-------|------|-------------|
| GET | `/v1/agents/export` | `agents_export.go` | Export agent as archive |
| POST | `/v1/agents/import` | `agents_import.go` | Import agent from archive |

### Agent Prompt Preview (`internal/http/agents_prompt_preview.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/v1/agents/{id}/prompt-preview` | Generate system prompt preview |

---

## 3. Skills (`internal/http/skills.go`)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/v1/skills` | `handleListSkills` | List skills |
| POST | `/v1/skills` | `handleCreateSkill` | Create skill |
| GET | `/v1/skills/{id}` | `handleGetSkill` | Get skill details |
| PUT | `/v1/skills/{id}` | `handleUpdateSkill` | Update skill |
| DELETE | `/v1/skills/{id}` | `handleDeleteSkill` | Delete skill |
| POST | `/v1/skills/upload` | `handleUploadSkill` | Upload skill archive |
| GET | `/v1/skills/{id}/export` | `handleExportSkill` | Export skill |
| POST | `/v1/skills/{id}/grants` | `handleSetGrants` | Set skill grants |
| GET | `/v1/skills/{id}/access` | `handleGetAccess` | Get effective access |

### Skills Evolution (`internal/http/skills_evolution.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/skills/{id}/evolution` | Get evolution settings |
| PATCH | `/v1/skills/{id}/evolution` | Update evolution settings (enable, mode) |
| GET | `/v1/skills/{id}/metrics` | Get skill usage metrics |
| GET | `/v1/skills/{id}/activity` | Get skill activity log |
| GET | `/v1/skills/{id}/suggestions` | List improvement suggestions |
| POST | `/v1/skills/{id}/suggestions` | Create improvement suggestion |
| POST | `/v1/skills/{id}/suggestions/{sg}/approve` | Approve suggestion |
| POST | `/v1/skills/{id}/suggestions/{sg}/reject` | Reject suggestion |
| POST | `/v1/skills/{id}/suggestions/{sg}/apply` | Apply suggestion patch |

### Skills Lifecycle (`internal/http/skills_lifecycle.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/skills/{id}/lifecycle` | Get lifecycle state |
| POST | `/v1/skills/{id}/lifecycle/install` | Install skill |
| POST | `/v1/skills/{id}/lifecycle/uninstall` | Uninstall skill |
| POST | `/v1/skills/{id}/lifecycle/upgrade` | Upgrade skill version |

### Skills Versions (`internal/http/skills_versions.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/skills/{id}/versions` | List skill versions |
| GET | `/v1/skills/{id}/versions/{v}` | Get specific version |

---

## 4. Providers (`internal/http/providers.go`)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/v1/providers` | `handleListProviders` | List LLM providers |
| POST | `/v1/providers` | `handleCreateProvider` | Add LLM provider |
| GET | `/v1/providers/{name}` | `handleGetProvider` | Get provider details |
| PUT | `/v1/providers/{name}` | `handleUpdateProvider` | Update provider |
| DELETE | `/v1/providers/{name}` | `handleDeleteProvider` | Delete provider |
| POST | `/v1/providers/{name}/reconnect` | `handleReconnectProvider` | Reconnect (test connection) |

Provider validation:
- URL validation (no SSRF -- only allowed localhost/internal for Ollama/ACP)
- API key masking in responses
- Ollama URL normalization (`/v1` suffix)
- Runtime registration status reported (`registered`, `disabled`, `skipped`, `missing_credential`, `invalid_config`)
- Cross-tenant owner super-admin support

### Provider Models (`internal/http/provider_models.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/providers/{name}/models` | List available models from provider |

- `fetchAnthropicModels()` -- Anthropic API models list
- `fetchGeminiModels()` -- Gemini API models list
- `fetchOpenAIModels()` -- OpenAI-compatible models list
- `fetchOllamaModels()` -- Ollama local models list

### Provider Embedding / Verification

| Method | Route | File | Description |
|--------|-------|------|-------------|
| POST | `/v1/providers/{name}/verify` | `provider_verify.go` | Test provider connection |
| POST | `/v1/providers/{name}/verify-embedding` | `provider_verify_embedding.go` | Test embedding capability |

---

## 5. MCP (`internal/http/mcp.go`)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/v1/mcp/servers` | `handleListServers` | List MCP servers (with agent grant counts) |
| POST | `/v1/mcp/servers` | `handleCreateServer` | Create MCP server config |
| GET | `/v1/mcp/servers/{name}` | `handleGetServer` | Get MCP server details |
| PUT | `/v1/mcp/servers/{name}` | `handleUpdateServer` | Update MCP server (OAuth fingerprint change purges tokens) |
| DELETE | `/v1/mcp/servers/{name}` | `handleDeleteServer` | Delete MCP server |
| POST | `/v1/mcp/servers/{name}/reconnect` | `handleReconnectServer` | Force reconnection |

Security validation: commands+args for stdio, URL for HTTP transports.

### MCP Grants (`internal/http/mcp_grants.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/mcp/servers/{name}/grants` | List agent grants for server |
| PUT | `/v1/mcp/servers/{name}/grants` | Update grants (allow/deny tool lists per agent) |

### MCP OAuth (`internal/http/mcp_oauth.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/v1/mcp/servers/{name}/oauth/start` | Start OAuth flow |
| GET | `/v1/mcp/servers/{name}/oauth/callback` | OAuth callback |
| DELETE | `/v1/mcp/servers/{name}/oauth/tokens` | Revoke OAuth tokens |

### MCP User Credentials (`internal/http/mcp_user_credentials.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/mcp/servers/{name}/user-credentials` | List user credentials |
| POST | `/v1/mcp/servers/{name}/user-credentials` | Create user credential |
| PUT | `/v1/mcp/servers/{name}/user-credentials/{id}` | Update user credential |
| DELETE | `/v1/mcp/servers/{name}/user-credentials/{id}` | Delete user credential |

### MCP Tools (`internal/http/mcp_tools.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/mcp/servers/{name}/tools` | List tools exposed by server |

### MCP Export/Import

| Method | Route | File | Description |
|--------|-------|------|-------------|
| GET | `/v1/mcp/export` | `mcp_export.go` | Export MCP server configurations |
| POST | `/v1/mcp/import` | `mcp_import.go` | Import MCP server configurations |

---

## 6. Channel Instances (`internal/http/channel_instances.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/channel-instances` | List channel instances |
| POST | `/v1/channel-instances` | Create channel instance |
| GET | `/v1/channel-instances/{id}` | Get instance details |
| PUT | `/v1/channel-instances/{id}` | Update instance |
| DELETE | `/v1/channel-instances/{id}` | Delete instance |

### Channel Contexts (`internal/http/channel_instance_contexts.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/channel-instances/{id}/contexts` | List contexts |
| POST | `/v1/channel-instances/{id}/contexts` | Create context |
| PUT | `/v1/channel-instances/{id}/contexts/{ctx}` | Update context |
| DELETE | `/v1/channel-instances/{id}/contexts/{ctx}` | Delete context |

### Channel Capabilities (`internal/http/channel_instance_capabilities.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/channel-instances/{id}/capabilities` | Get capabilities |

---

## 7. Sessions (`internal/http/sessions.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/sessions` | List sessions |
| GET | `/v1/sessions/{id}` | Get session details |
| POST | `/v1/sessions/{id}/branch` | Branch session |

### Session Branch Follow (`internal/http/sessions_branch_follow_test.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/v1/sessions/{id}/branch/follow` | Follow branch to new session |

---

## 8. Webhooks (`internal/http/webhooks_*.go`)

| Method | Route | File | Description |
|--------|-------|------|-------------|
| POST | `/v1/webhooks/message` | `webhooks_message.go` | Inbound message webhook |
| POST | `/v1/webhooks/llm` | `webhooks_llm.go` | LLM webhook endpoint |
| POST | `/v1/webhooks/admin` | `webhooks_admin.go` | Admin webhook |
| GET | `/v1/webhooks/admin/calls` | `webhooks_admin_calls.go` | List admin webhook calls |

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
| POST | `/v1/auth/login` | Login (API key, session token) |
| POST | `/v1/auth/logout` | Logout |
| POST | `/v1/auth/refresh` | Refresh session |

### API Keys (`internal/http/api_keys.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/api-keys` | List API keys |
| POST | `/v1/api-keys` | Create API key |
| DELETE | `/v1/api-keys/{id}` | Revoke API key |

---

## 10. Knowledge Graph (`internal/http/knowledge_graph_handlers.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/knowledge-graph` | Query knowledge graph |
| POST | `/v1/knowledge-graph` | Add to knowledge graph |

---

## 11. Memory (`internal/http/memory_handlers.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/memory` | Query episodic memory |
| POST | `/v1/memory` | Store in episodic memory |
| DELETE | `/v1/memory/{id}` | Delete memory entry |

---

## 12. Orchestration (`internal/http/orchestration_handlers.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/orchestration` | Get orchestration config |
| PUT | `/v1/orchestration` | Update orchestration config |

---

## 13. Traces (`internal/http/traces.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/traces` | List run traces |
| GET | `/v1/traces/{id}` | Get trace details |
| GET | `/v1/traces/{id}/timeline` | Get run timeline |

### Trace Follow (`internal/http/traces_follow_test.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/traces/follow/{id}` | SSE stream for live trace updates |

---

## 14. Summoner (`internal/http/summoner.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/v1/summon` | Summon agent by description (LLM-powered agent discovery) |
| POST | `/v1/summon/{key}` | Summon specific agent by key |

### Summoner Prompts (`internal/http/summoner_prompts.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/summon/prompts` | List summoning prompts |
| POST | `/v1/summon/prompts` | Create summoning prompt |

---

## 15. Chat (`internal/http/chat_completions.go`)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/v1/chat/completions` | OpenAI-compatible chat completions endpoint |
| POST | `/v1/chat/completions/stream` | Streaming chat completions |

This route enables third-party tools to interact with GoClaw agents using the OpenAI chat completions API format.

---

## 16. Vault (`internal/http/vault_handlers.go`)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/v1/vault` | List vault entries |
| POST | `/v1/vault` | Create vault entry |
| POST | `/v1/vault/upload` | Upload to vault |
| GET | `/v1/vault/tree` | Get vault tree structure |
| GET | `/v1/vault/{path}` | Get vault file content |
| POST | `/v1/vault/{path}/links` | Manage vault links |

---

## 17. Other Endpoints

| Method | Route | File | Description |
|--------|-------|------|-------------|
| GET | `/v1/media/{token}` | `media_serve.go` | Serve uploaded media files |
| POST | `/v1/media/upload` | `media_upload.go` | Upload media |
| GET | `/v1/files/{path}` | `files.go` | Serve agent workspace files |
| POST | `/v1/tts` | `tts.go` | Text-to-speech synthesis |
| GET | `/v1/tts/config` | `tts_config.go` | TTS configuration |
| POST | `/v1/tts/synthesize` | `tts_test.go` | Synthesize speech |
| GET | `/v1/tts/capabilities` | `tts_capabilities.go` | TTS provider capabilities |
| POST | `/v1/tts/test-connection` | `tts_test_connection.go` | Test TTS connection |
| POST | `/v1/tools/invoke` | `tools_invoke.go` | Invoke a tool by name |
| POST | `/v1/workspace/upload` | `workspace_upload.go` | Upload file to workspace |
| GET | `/v1/backup/{name}` | `backup_handler.go` | Download backup |
| POST | `/v1/backup` | `backup_handler.go` | Create backup |
| POST | `/v1/restore` | `restore_handler.go` | Restore from backup |
| GET | `/v1/tenants` | `tenants.go` | List tenants (system owner) |
| POST | `/v1/tenants` | `tenants.go` | Create tenant |
| GET | `/v1/users/search` | `user_search.go` | Search users |
| GET | `/v1/browser-cookies` | `browser_cookies.go` | Get browser cookies |
| GET | `/v1/voices` | `voices.go` | List available TTS voices |
| GET | `/v1/evolve` | `evolution_handlers.go` | Evolution system status |
| GET | `/v1/system-configs` | `system_configs.go` | System configuration |
| GET | `/v1/edition` | `edition.go` | Get edition info |
| GET | `/v1/wake` | `wake.go` | Health check/wake endpoint |
| GET | `/v1/packages` | `packages.go` | List software packages |
| GET | `/v1/not-found` | `api_not_found.go` | 404 catch-all handler |

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
