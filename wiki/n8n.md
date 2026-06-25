---
name: n8n
tags: [automation, cli, docker, fair-code, git, integration, low-code, mcp, n8n, orchestration, storage, typescript, vue, webhook, wiki, workflow-automation]
description: n8n
source: sources/n8n/
---

# n8n

| Field | Value |
|---|---|
| **Origin** | [n8n-io/n8n](https://github.com/n8n-io/n8n) |
| **License** | Sustainable Use License (main branch, non-`.ee.` files) + Enterprise License (`.ee.` files) — **fair-code, not open source** |
| **Stack** | TypeScript monorepo — Vue 3 + Vite (frontend), Node.js + Express (backend), TypeORM (database) |
| **Source** | `sources/n8n/` |
| **Raw** | `raw/n8n/n8n.xml` (62MB) |
| **Codegraph** | `graphs/n8n/` (774MB DB — 16,057 files, 219+ symbols) |
| **Profile** | [[n8n-agent-profile]] |
| **Wanted** | n8n is a workflow automation platform — fair-code alternative to Zapier/Make |

## What it is

A workflow automation platform with 400+ integrations, AI-native workflow building, and self-hostable deployment. Nodes connect services (Slack, Notion, OpenAI, Discord, 300+ more) into automated workflows. The Instance AI agent provides natural language workflow creation.

## Where to find things

### Architecture & Design

| What | Where |
|---|---|
| Full architecture | [[n8n-architecture]] (`domains/architecture/`) |
| Instance AI architecture | [[n8n-instance-ai]] (`domains/architecture/`) |
| API architecture | [[n8n-api]] (`domains/api/`) |
| MCP integration | [[n8n-mcp]] (`domains/mcp/`) |
| Deployment guides | [[n8n-deployment]] (`domains/deployment/`) |
| Agent profile (standards) | [[n8n-agent-profile]] (`assets/agent-profiles/`) |
| AGENTS.md (agent instructions) | `sources/n8n/AGENTS.md` |
| README | `sources/n8n/README.md` |

### Core Engine

| What | Where |
|---|---|
| Workflow types & engine | `packages/workflow/src/` (Workflow class, expressions, graph traversal, cron, validation) |
| Execution engine | `packages/core/src/` (execution, binary data, credentials, encryption, node loader) |
| Engine (separate package) | `packages/@n8n/engine/` — isolated execution engine |
| Expression engine | `packages/workflow/src/expressions/` |
| Graph traversal utils | `packages/workflow/src/common/` — `getParentNodes()`, `getChildNodes()`, `mapConnectionsByDestination()` |

### Backend (Express Server)

| What | Where |
|---|---|
| Server entry | `packages/cli/src/server.ts` |
| Controllers | `packages/cli/src/controllers/` (~35 controllers) |
| Services | `packages/cli/src/services/` |
| Auth | `packages/cli/src/auth/` (JWT, cookies, MFA, SSO) |
| Webhooks | `packages/cli/src/webhooks/` (live webhooks, test webhooks, waiting forms, request handling) |
| Public API | `packages/cli/src/public-api/` (OpenAPI v3, v1) |
| Push (WebSocket/SSE) | `packages/cli/src/push/` |
| Event bus | `packages/cli/src/eventbus/` |
| Scaling | `packages/cli/src/scaling/` |
| Task runners | `packages/cli/src/task-runners/` |
| Feature modules | `packages/cli/src/modules/` (40+ modules) |
| CLI commands | `packages/cli/src/commands/` |

### Frontend (Vue 3)

| What | Where |
|---|---|
| Editor UI | `packages/frontend/editor-ui/src/` |
| Design system | `packages/frontend/@n8n/design-system/` |
| i18n | `packages/frontend/@n8n/i18n/` |
| Pinia stores | `packages/frontend/editor-ui/src/stores/` |
| Views (routes) | `packages/frontend/editor-ui/src/views/` |
| Router | `packages/frontend/editor-ui/src/router.ts` |
| Composables | `packages/frontend/editor-ui/src/composables/` |
| Shared stores | `packages/frontend/@n8n/stores/` |
| AGENTS.md | `packages/frontend/AGENTS.md` |

### Nodes & Integrations

| What | Where |
|---|---|
| Built-in nodes (307+) | `packages/nodes-base/nodes/` (one directory per integration) |
| Credentials | `packages/nodes-base/credentials/` (307+ credential types) |
| AI / LangChain nodes | `packages/@n8n/nodes-langchain/` |
| Node dev toolkit | `packages/node-dev/` |
| AGENTS.md | `packages/nodes-base/AGENTS.md` |

### Instance AI

| What | Where |
|---|---|
| Architecture | [[n8n-instance-ai]] (domain doc) |
| Docs | `packages/@n8n/instance-ai/docs/` (architecture, tools, streaming, memory, sandbox, filesystem, config) |
| Agent core | `packages/@n8n/instance-ai/src/agent/` |
| Tools | `packages/@n8n/instance-ai/src/tools/` (orchestration, workflows, executions, credentials, nodes, data-tables, workspace, web-research, filesystem) |
| Orchestration tools | `packages/@n8n/instance-ai/src/tools/orchestration/` |
| MCP client manager | `packages/@n8n/instance-ai/src/mcp/mcp-client-manager.ts` |
| Runtime | `packages/@n8n/instance-ai/src/runtime/` |
| Planned tasks | `packages/@n8n/instance-ai/src/planned-tasks/` |
| Workflow loop | `packages/@n8n/instance-ai/src/workflow-loop/` |
| Workspace/sandbox | `packages/@n8n/instance-ai/src/workspace/` |
| Memory | `packages/@n8n/instance-ai/src/memory/` |
| Storage | `packages/@n8n/instance-ai/src/storage/` |
| Backend adapter | `packages/cli/src/modules/instance-ai/` |
| CLAUDE.md | `packages/@n8n/instance-ai/CLAUDE.md` |

### MCP

| What | Where |
|---|---|
| MCP architecture | [[n8n-mcp]] (domain doc) |
| MCP Apps server | `packages/@n8n/mcp-apps/src/server/` |
| MCP Browser server | `packages/@n8n/mcp-browser/src/` (server.ts, cdp-relay.ts, browser-discovery.ts, tools/) |
| MCP Browser extension | `packages/@n8n/mcp-browser-extension/` |
| Native MCP server | `packages/cli/src/modules/mcp/` (tools, controller, service, config) |

### Database

| What | Where |
|---|---|
| Database migrations | `packages/cli/src/databases/` |
| TypeORM entities | `packages/@n8n/db/` |
| DB config | `packages/@n8n/config/` |

### Testing

| What | Where |
|---|---|
| Playwright E2E | `packages/testing/playwright/` |
| E2E AGENTS.md | `packages/testing/playwright/AGENTS.md` (Janitor, TCR, architecture rules) |
| Node tests | `packages/nodes-base/test/` |
| Jest config | Per-package `jest.config.ts` |
| Vitest config | `packages/@n8n/vitest-config/` |
| Containers | `packages/testing/` (docker-compose-based test environments) |

### Shared Packages (`packages/@n8n/`)

| Package | Where |
|---|---|
| api-types (FE/BE contract) | `packages/@n8n/api-types/` |
| config | `packages/@n8n/config/` |
| constants | `packages/@n8n/constants/` |
| di | `packages/@n8n/di/` |
| decorators | `packages/@n8n/decorators/` |
| errors | `packages/@n8n/errors/` |
| utils | `packages/@n8n/utils/` |
| permissions | `packages/@n8n/permissions/` |
| telemetry | `packages/@n8n/telemetry/` |
| crdt (collaboration) | `packages/@n8n/crdt/` |
| computer-use | `packages/@n8n/computer-use/` |
| local-gateway | `packages/@n8n/local-gateway/` |
| task-runner | `packages/@n8n/task-runner/` |
| task-runner-python | `packages/@n8n/task-runner-python/` |
| json-schema-to-zod | `packages/@n8n/json-schema-to-zod/` |
| chat-hub | `packages/@n8n/chat-hub/` |
| backend-common | `packages/@n8n/backend-common/` |
| backend-test-utils | `packages/@n8n/backend-test-utils/` |
| extension-sdk | `packages/@n8n/extension-sdk/` |

## Deployment

| What | Where |
|---|---|
| Deployment guide | [[n8n-deployment]] |
| Docker images | `docker/images/n8n/`, `docker/images/runners/` |
| Docker Compose | `docker-compose.yml` (root) |
| Helm charts | `charts/` |

## Fork Considerations

| Factor | Assessment |
|---|---|
| **License** | Fair-code (Sustainable Use + Enterprise) — cannot redistribute EE code |
| **Size** | Very large (62MB raw, 774MB codegraph, 16K files) |
| **Activity** | Very active — corporate backing (n8n GmbH), 50K+ GitHub stars |
| **Dependencies** | pnpm monorepo, deep dependency tree |
| **Fork cost** | Very high — full fork means either removing all EE code or requiring an n8n Enterprise License |
| **Fork target** | `packages/nodes-base/`, `packages/@n8n/instance-ai/`, `packages/@n8n/mcp-apps/`, `packages/@n8n/mcp-browser/` — individual packages could be extracted |
| **Unique value** | Autonomous agent (Instance AI), 400+ node integrations, MCP browser automation, fair-code licensing model, Vue 3 editor |
| **Zero-fork target** | Not designed for zero-fork — n8n is the upstream, not a consumer |

## Related

- [[n8n-architecture]] — Full architecture
- [[n8n-instance-ai]] — Autonomous agent architecture
- [[n8n-mcp]] — MCP integration
- [[n8n-api]] — REST and Public API
- [[n8n-deployment]] — Self-hosted deployment
- [[n8n-agent-profile]] — Engineering profile

## Cross-project

- [[hermes-agent]] -- MCP tool integration for workflow automation
- [[openclaw]] -- MCP tool integration for workflow automation
- [[agentfield]] -- Complementary AI decision orchestration
- [[mission-control]] -- Webhook panel integration
- [[podman]] -- Container runtime for n8n deployment
- [[nix-podman-stacks]] -- Nix deployment module for n8n
- [[gogs]] -- Webhook triggers from Git events
- [[buildah]] -- Custom n8n image building with pre-installed nodes
- [[sablier]] -- Scale-to-zero for n8n workflow services
