---
name: n8n-api
tags: [n8n, api, typescript, vue, workflow-automation, low-code, integration, fair-code]
description: n8n — API Architecture
---

# n8n — API Architecture

**Source:** `sources/n8n/packages/cli/src/`

## Overview

n8n has three API surfaces: the internal REST API (used by the frontend), the Public API (for programmatic access), and the Push API (WebSocket/SSE for real-time frontend updates). All backed by Express on the same server process.

## Internal REST API

Controllers under `packages/cli/src/controllers/` handle the frontend-facing API (~30 controllers):

| Controller | Endpoint Prefix | Purpose |
|------------|----------------|---------|
| `auth.controller.ts` | `/auth` | Login, signup, password reset |
| `users.controller.ts` | `/users` | User CRUD, settings |
| `me.controller.ts` | `/me` | Current user profile, theme, API key |
| `workflows.controller.ts` | `/workflows` | Workflow CRUD, activation, tags |
| `active-workflows.controller.ts` | `/active-workflows` | Active workflow management |
| `executions.controller.ts` | `/executions` | Execution history, delete |
| `credentials.controller.ts` | `/credentials` | Credential CRUD, sharing |
| `credentials-types.controller.ts` | `/credentials-types` | Credential type metadata |
| `nodes.controller.ts` | `/node-types` | Node type metadata |
| `tags.controller.ts` | `/tags` | Tag CRUD |
| `project.controller.ts` | `/projects` | Project CRUD, sharing |
| `folder.controller.ts` | `/folders` | Folder CRUD |
| `role.controller.ts` | `/roles` | Role management |
| `invitation.controller.ts` | `/invitations` | User invitations |
| `mfa.controller.ts` | `/mfa` | Multi-factor auth |
| `owner.controller.ts` | `/owner` | Owner management |
| `password-reset.controller.ts` | `/password-reset` | Password reset flow |
| `api-keys.controller.ts` | `/api-keys` | API key management |
| `auth.controller.ts` | `/oauth` | OAuth credential flow |
| `user-settings.controller.ts` | `/user-settings` | User preferences |
| `security-settings.controller.ts` | `/security-settings` | Security settings |
| `binary-data.controller.ts` | `/binary-data` | Binary data upload/download |
| `debug.controller.ts` | `/debug` | Debug endpoints |
| `node-types.controller.ts` | `/node-types` | Node type catalog |
| `telemetry.controller.ts` | `/telemetry` | Telemetry data |
| `posthog.controller.ts` | `/posthog` | Feature flags |
| `orchestration.controller.ts` | `/orchestration` | Multi-main orchestration |
| `workflow-statistics.controller.ts` | `/workflow-stats` | Workflow statistics |
| `cta.controller.ts` | `/cta` | Call-to-action tracking |
| `dynamic-node-parameters.controller.ts` | `/dynamic-node-params` | Dynamic node parameter loading |
| `dynamic-templates.controller.ts` | `/dynamic-templates` | Workflow templates |
| `e2e.controller.ts` | `/e2e` | E2E test helpers |
| `translation.controller.ts` | `/translations` | Translation strings |
| `third-party-licenses.controller.ts` | `/third-party-licenses` | License display |
| `module-settings.controller.ts` | `/module-settings` | Feature module settings |
| `survey-answers.controller.ts` | `/survey-answers` | User survey responses |
| `annotation-tags.controller.ee.ts` | `/annotation-tags` | Execution annotation tags (EE) |
| `ai.controller.ts` | `/instance-ai` | Instance AI endpoints |
| `webhooks.controller.ts` | `(webhook paths)` | Webhook trigger endpoints |
| `test-webhooks.controller.ts` | `/test-webhook` | Test webhook endpoints |

### Shared Patterns

- **`@n8n/di`**: Services injected via constructor with `@Service()` decorator
- **TypeORM repositories**: Data access via typed repositories
- **RBAC**: Permission checks via `userHasScopes()` middleware
- **Validation**: Zod schemas for input validation (migrating from class-validator)
- **Error handling**: Global error middleware, typed error classes

## Public API (`packages/cli/src/public-api/`)

RESTful API for programmatic access (integrations, external tools):

- **Version 1** (`v1/`): Current stable version
- **Format**: OpenAPI 3.0 (`openapi.yml`) with Swagger UI
- **Handlers**: Organized by resource in `handlers/`
- **Shared**: Pagination, filtering, error responses
- **API keys**: Authenticated via API keys managed through `/api-keys`

The Public API provides programmatic access to workflows, executions, credentials, users, tags, and more. Used by CI/CD pipelines, external automation, and CLI tools.

## Instance AI API

Subset of the REST API specifically for the AI assistant:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/instance-ai/chat/:threadId` | POST | Send a message (returns runId) |
| `/instance-ai/events/:threadId` | GET (SSE) | Subscribe to agent events |
| `/instance-ai/chat/:threadId/confirm` | POST | Submit HITL confirmation |
| `/instance-ai/chat/:threadId/cancel` | POST | Cancel active run |
| `/instance-ai/threads/:threadId` | GET | Thread info + messages |
| `/instance-ai/credits` | GET | Credit balance |
| `/instance-ai/gateway` | GET | Filesystem gateway state |
| `/instance-ai/chat/:threadId/tasks/:taskId/cancel` | POST | Cancel background task |
| `/instance-ai/settings` | GET/PUT | User/admin AI settings |

## Push API

Real-time updates from server to frontend:

| Transport | Implementation | Use |
|-----------|---------------|-----|
| WebSocket | `websocket.push.ts` | Production — persistent connection |
| SSE | `sse.push.ts` | Fallback — Server-Sent Events |

Push events carry workflow execution status, active workflow changes, credential updates, and Instance AI agent events.

## Event Bus (`packages/cli/src/eventbus/`)

Two-tier event system:

- **In-process** (`EventEmitter`): Single instance mode — events handled in the same Node.js process
- **Redis Pub/Sub** (queue mode): Events distributed across processes via Redis channels
- **`MessageEventBus`**: Structured event messages with `event-message-classes/` for typed event payloads
- **`MessageEventBusWriter`**: Event persistence/logging

Events flow through the bus for: execution lifecycle, webhook triggers, workflow activation, errors, and Instance AI events.

## Auth System (`packages/cli/src/auth/`)

| Method | Implementation |
|--------|---------------|
| JWT | Access + refresh tokens |
| Cookie-based | Session cookies (web UI) |
| MFA | TOTP-based (authenticator app) |
| SSO | OIDC and SAML (Enterprise Edition) |
| API Keys | Static keys for programmatic access |
| OAuth | For credential authentication (OAuth2) |

## Module System

Feature modules are registered via `@BackendModule` decorator:
- Controllers auto-registered from module
- Settings exposed via `settings()` method
- Lifecycle management (init, shutdown)
- Can be disabled via environment variable
- Type-specific (main instance only, or worker)

## License Management

Enterprise features (`.ee.` files) are gated by license checks:
- License key stored in DB
- Features enabled/disabled based on license tier
- Metering tracks usage for consumption-based pricing

## Related

- n8n Architecture: [[n8n-architecture]]
- n8n Instance AI: [[n8n-instance-ai]]
- n8n MCP: [[n8n-mcp]]
- n8n Deployment: [[n8n-deployment]] -- Deployment models, Docker images, and scaling
- n8n Agent Profile: [[n8n-agent-profile]] -- Engineering standards and development patterns
- Wiki entry: [[n8n]]
