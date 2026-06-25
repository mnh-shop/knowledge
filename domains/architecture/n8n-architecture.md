---
name: n8n-architecture
tags: [n8n, architecture, workflow]
description: n8n — Architecture
---

# n8n — Architecture

**Source:** `/Users/admin1/Documents/knowledge/sources/n8n/`
**Raw:** `raw/n8n/n8n.xml` (62MB)
**Codegraph:** `graphs/n8n/` (774MB DB — 16,057 files, 219+ symbols indexed)

## Licensing

n8n uses **fair-code licensing** — not open source, not closed:

- **Sustainable Use License** (main branch, non-`.ee.` files): Free for internal business/personal use. May not be offered as a competing service. Source available.
- **Enterprise License** (`.ee.` files): Requires a paid n8n Enterprise License.
- **Third-party components** retain their original licenses.

This is critical for fork analysis — Enterprise Edition features cannot be redistributed without a license.

## What it is

n8n is a **workflow automation platform** — a fair-code alternative to Zapier/Make, built with a programmable edge: users can write custom nodes and extend any part of the system. 400+ integrations, AI-native workflow building, self-hostable.

## Monorepo Structure

Managed by **pnpm workspaces** with **Turbo** build orchestration.

### Top-level packages (`packages/`)

| Package | Role |
|---------|------|
| `packages/workflow` | Core workflow engine — types, interfaces, expression engine, graph traversal, node validation, cron, data tables |
| `packages/core` | Workflow execution engine — binary data, credentials, execution engine, node loader, encryption |
| `packages/cli` | Express server, REST API, CLI commands, auth, controllers, webhooks, task runners, public API, scaling, event bus, MCP server |
| `packages/frontend/editor-ui` | Vue 3 frontend application (editor UI) |
| `packages/frontend/@n8n/` | Frontend shared packages (design-system, i18n, stores, chat, composables, rest-api-client, storybook) |
| `packages/nodes-base` | 307+ built-in node types (integrations) in `nodes/`, credentials in `credentials/` |
| `packages/testing` | Playwright E2E tests, test containers |
| `packages/node-dev` | Node development toolkit |
| `packages/extensions/insights` | Insights extension (analytics) |

### Middleware packages (`packages/@n8n/` — 40+ packages)

| Package | Role |
|---------|------|
| `instance-ai` | Autonomous agent — orchestrator + sub-agents, planning, tools, memory, MCP client, sandbox. **Framework-agnostic core** |
| `mcp-apps` | MCP server for n8n app automation (apps, components, composables, telemetry) |
| `mcp-browser` | MCP server for browser automation (CDP relay, tabs, navigation, credentials, inspection) |
| `mcp-browser-extension` | Browser extension for MCP |
| `engine` | Workflow execution engine |
| `ai-workflow-builder.ee` | AI workflow builder (Enterprise Edition) |
| `nodes-langchain` | AI/LangChain node types |
| `api-types` | Shared TypeScript interfaces between frontend and backend |
| `config` | Centralized configuration management |
| `design-system` | Vue 3 component library for UI consistency |
| `i18n` | Internationalization for UI text |
| `di` | Dependency injection container (`@n8n/di`) |
| `db` | Database entities and repositories |
| `crdt` | CRDT-based real-time collaboration |
| `chat-hub` | Chat hub for multi-tenant chat |
| `computer-use` | Computer Use automation |
| `task-runner` | Task runner for distributed execution |
| `task-runner-python` | Python task runner |
| `permissions` | Authorization/permissions |
| `constants` | Shared constants |
| `errors` | Error types |
| `utils` | Shared utilities |
| `telemetry` | Telemetry collection |
| `decorators` | TypeScript decorators |
| `local-gateway` | Local gateway for filesystem access |
| `json-schema-to-zod` | JSON Schema → Zod schema conversion |
| `extension-sdk` | Extension SDK |
| `node-cli` | Node CLI tooling |
| `vitest-config` | Vitest configuration presets |
| `typescript-config` | TypeScript configuration presets |

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                       │
│  editor-ui  ·  design-system  ·  i18n  ·  stores  ·  chat │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP + SSE
                         ▼
┌─────────────────────────────────────────────────────────┐
│               Backend (Express + TypeORM)                 │
│  Controllers  ·  Services  ·  Middleware  ·  Auth  ·  API  │
│  Public API  ·  Webhooks  ·  Push  ·  Event Bus          │
│  Module System  ·  RBAC  ·  License                      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│               Workflow Engine                             │
│  packages/workflow  ·  packages/core  ·  packages/engine  │
│  Expression Engine  ·  Node Loader  ·  Execution Engine   │
│  Graph Traversal  ·  Data Flow  ·  Error Handling         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                Integration Layer                          │
│  nodes-base (307+ nodes)  ·  credentials  ·  triggers     │
│  webhooks  ·  polling  ·  LangChain / AI nodes            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Extensions                             │
│  Instance AI  ·  MCP Servers  ·  Insights  ·  CRDT       │
│  Source Control  ·  SSO  ·  External Secrets              │
│  Task Runners (Node.js + Python)  ·  Queue Mode           │
└─────────────────────────────────────────────────────────┘
```

### Key Architectural Patterns

1. **Dependency Injection**: Uses `@n8n/di` for IoC container — all services registered via `@Service()` decorator
2. **Controller-Service-Repository**: Backend follows MVC-like pattern. TypeORM entities → Repositories → Services → Controllers
3. **Module System**: `@BackendModule` decorator for feature modules (Instance AI, MCP, Source Control, SSO, etc.). Each module has lifecycle management, settings, and shutdown hooks
4. **Event-Driven**: Internal event bus (`EventBus` / `MessageEventBus`) for decoupled communication. Supports in-process EventEmitter and Redis Pub/Sub (queue mode)
5. **Context-Based Execution**: Different execution contexts for different node types (main, trigger, webhook, polling)
6. **State Management**: Frontend uses Pinia stores with TypeScript
7. **Design System**: Reusable Vue 3 components in `@n8n/design-system` with CSS tokens

## CLI Package (`packages/cli/src/`)

The primary backend — Express HTTP server with 40+ module directories:

| Directory / Module | Purpose |
|---|---|
| `controllers/` | REST API controllers (workflows, credentials, executions, users, auth, settings, etc.) |
| `services/` | Business logic services |
| `modules/` | Feature modules (40+ modules) — see below |
| `databases/` | Database migrations, TypeORM setup |
| `auth/` | Authentication (JWT, cookies, MFA, SSO) |
| `webhooks/` | Webhook handling infrastructure |
| `task-runners/` | Distributed task execution (Node.js + Python) |
| `public-api/` | Public REST API for programmatic access |
| `eventbus/` | Event bus (in-process + Redis Pub/Sub) |
| `executions/` | Execution lifecycle management |
| `workflows/` | Workflow CRUD and lifecycle |
| `credentials/` | Credential management |
| `user-management/` | User CRUD, roles, invites |
| `scaling/` | Multi-main scaling coordination |
| `push/` | WebSocket push notifications to frontend |
| `license/` | License management (Enterprise features) |
| `metrics/` | Prometheus metrics |
| `middlewares/` | Express middlewares (auth, error handling, etc.) |
| `commands/` | CLI commands (`n8n start`, `n8n worker`, `n8n export`, etc.) |

### CLI Feature Modules (`modules/` — 40+ modules)

| Module | Type | Description |
|--------|------|-------------|
| `instance-ai` | Core | AI assistant backend — orchestrator, tools, memory, MCP client |
| `mcp` | Core | MCP server for n8n (native MCP protocol support) |
| `mcp-registry` | Core | MCP tool registry |
| `agents` | Core | Agent system (n8n-native agents) |
| `chat-hub` | Core | Multi-tenant chat hub |
| `workflow-builder` | Core | Workflow builder |
| `workflow-index` | Core | Workflow search indexing |
| `data-table` | Core | Data table CRUD |
| `source-control.ee` | EE | Git-based workflow source control |
| `sso-oidc` | EE | OIDC single sign-on |
| `sso-saml` | EE | SAML single sign-on |
| `ldap.ee` | EE | LDAP directory sync |
| `external-secrets.ee` | EE | External secrets management |
| `provisioning.ee` | EE | User/workflow provisioning |
| `log-streaming.ee` | EE | Log streaming to external services |
| `dynamic-credentials.ee` | EE | Dynamic OAuth credentials |
| `insights` | Core | Analytics and dashboards |
| `otel` | Core | OpenTelemetry integration |
| `community-packages` | Core | Community node package management |
| `favorites` | Core | Favorites/bookmarks |
| `encryption-key-manager` | Core | Encryption key lifecycle |
| `n8n-packages` | Core | n8n package management |
| `quick-connect` | Core | Quick connect to services |
| `redaction` | Core | Data redaction |
| `runtime-credentials` | Core | Runtime credential injection |
| `token-exchange` | Core | Token exchange API |
| `node-catalog` | Core | Node type catalog |
| `oauth` | Core | OAuth helper |
| `oauth-jwe` | Core | OAuth JWE encryption |
| `oauth-server` | Core | OAuth authorization server |
| `breaking-changes` | Core | Breaking change notifications |
| `instance-registry` | Core | Instance registration |
| `instance-version-history` | Core | Instance version tracking |
| `evaluation.ee` | EE | Workflow evaluation |

## Workflow Engine (`packages/workflow/`)

The workflow engine provides:

- **`Workflow` class**: Nodes, connections, settings, expression evaluation
- **Graph traversal**: `getParentNodes()`, `getChildNodes()`, `mapConnectionsByDestination()` — indexed by source node, invert via `mapConnectionsByDestination()`
- **Expression engine**: `WorkflowExpression`, `ExpressionEvaluatorProxy`, `ExpressionSandboxing`
- **Node validation**: `NodeValidation`, `NodeParameters`, `TypeValidation`
- **Cron/Schedule**: `Cron` parsing and next-run calculation
- **Data tables**: `DataTable` types for structured data operations
- **Tool helpers**: `ToolHelpers` for tool-based node interactions
- **Workflow diff**: `WorkflowDiff` for version comparison
- **Error types**: Hierarchical error classes in `errors/`

## Core Engine (`packages/core/src/`)

The core execution engine:

- **Execution engine** (`execution-engine/`): Runs workflows — manages node execution order, error propagation, data flow
- **Binary data** (`binary-data/`): Binary file storage manager
- **Credentials**: `credential-types.ts`, `credentials-helper.ts`, `credentials-overwrites.ts`
- **Node loader**: `nodes-loader/` — discovers and loads node types
- **Encryption**: `encryption/` — credential encryption
- **Observability**: `observability/` — metrics and tracing
- **HTML sandbox**: `html-sandbox.ts` — sandboxed HTML rendering

## Frontend (`packages/frontend/editor-ui/src/`)

Vue 3 application with:

| Area | Description |
|------|-------------|
| `views/` | Route-level page components |
| `components/` | Shared Vue 3 components |
| `stores/` | Pinia state management stores |
| `router.ts` | Vue Router configuration |
| `api/` | API client modules |
| `composables/` | Vue composables |
| `models/` | Data models |
| `plugins/` | Vue plugins |
| `utils/` | Utility functions |
| `types/` | TypeScript type definitions |
| `css/` | Global styles |
| `constants/` | Application constants (debounce times, etc.) |
| `workers/` | Web workers |
| `event-bus/` | Client-side event bus |
| `push-connection/` | WebSocket push client |
| `layouts/` | Layout components |
| `experiments/` | Feature experiments |
| `features/` | Feature flags |

### Frontend Shared Packages (`packages/frontend/@n8n/`)

| Package | Description |
|---------|-------------|
| `design-system` | Vue 3 component library with CSS tokens and primitives |
| `i18n` | Internationalization (translation strings) |
| `stores` | Shared Pinia stores |
| `rest-api-client` | REST API client for backend communication |
| `chat` | Chat UI components |
| `composables` | Shared Vue composables |
| `storybook` | Storybook configuration for design system |

## Nodes (`packages/nodes-base/nodes/`)

307+ node implementations organized by integration name (Airtable, Asana, AWS, Discord, Google, HubSpot, Notion, OpenAI, Slack, etc.):

**Node types:**
- **Programmatic nodes**: Custom `execute()` function with business logic
- **Declarative nodes**: `requestDefaults` + routing config (no `execute()`)
- **Trigger nodes**: Polling (`poll()`), Webhook (`webhook()` + `webhookMethods()`), or Generic (`trigger()`)

**Node versioning:**
- Light: Version arrays in description (`version: [3, 3.1, 3.2]`)
- Full: `VersionedNodeType` class with separate version implementations

**Credentials** (`credentials/`): 307+ credential types matching nodes. Each implements `ICredentialType` with `authenticate` config and optional `test` request.

**Testing**: Vitest + nock for HTTP mocking + vitest-mock-extended for interface mocking.

## Event Bus

Two-tier system:

1. **In-process EventEmitter** (single instance mode): Events handled within the same Node.js process
2. **Redis Pub/Sub** (queue mode): Events distributed across multiple processes (workers, webhooks, main)

The `MessageEventBus` handles structured event messages with logging and persistence.

## Execution Architecture

Workflows can execute in multiple modes:
- **Main mode**: In-process on the main server
- **Worker mode**: Offloaded to dedicated worker processes (scaling)
- **Trigger mode**: Run as daemon (webhook, polling, or event-triggered)
- **Queue mode**: Managed via Redis/bull

The `ActiveWorkflowManager` manages active (running) workflow lifecycle.

## Task Runners

Distributed task execution for long-running or resource-intensive operations:

- **`packages/@n8n/task-runner`**: Node.js task runner — receives tasks, executes, returns results
- **`packages/@n8n/task-runner-python`**: Python task runner — Pyodide-based or native Python
- **CLI module** (`task-runners/`): Server-side management of task runner connections

## Multi-Main Scaling

Multiple main instances can run for high availability. The `scaling/` module coordinates:
- Leader election
- Workflow distribution
- State synchronization via Redis
- Webhook routing across instances

## Related

- Instance AI architecture: [[n8n-instance-ai]]
- n8n API: [[n8n-api]]
- n8n MCP: [[n8n-mcp]]
- n8n Deployment: [[n8n-deployment]]
- Wiki entry: [[n8n]]
- Agent profile: [[n8n-agent-profile]]
