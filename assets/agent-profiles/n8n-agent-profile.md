---
name: n8n-agent-profile
description: Engineering profile for the n8n monorepo — standards, patterns, architecture rules
tags: [agent-profile, ai-llm, fair-code, integration, low-code, mcp, n8n, profile, security, typescript, vue, workflow-automation]
metadata:
  type: reference
source: sources/n8n/
---

# n8n — Agent Profile

## Overview

n8n is a large TypeScript monorepo (16K files, 60MB+ raw) using pnpm workspaces and Turbo build. The development culture emphasizes type safety, clean interfaces, and testable architecture.

## Engineering Standards

### TypeScript Rules (strict)

- **No `any`** — use proper types or `unknown`
- **No `as` casts** — use type guards, type predicates, `satisfies` (except in test code)
- **Zod schemas as source of truth** — infer with `z.infer<>`, derive types from schemas
- **Define shared types in `@n8n/api-types`** — event types, API shapes, enums
- **Lazy-load heavy modules** — use `await import()` for conditionally-used modules

### Architecture Rules

- **Layer boundaries**: Tool → Service interface → Adapter → n8n internals. No business logic in tools.
- **Dependency injection**: Services registered with `@Service()` decorator, injected via constructor
- **Controllers are thin**: Controllers parse input, call service, return response. Business logic in services.
- **Module system**: `@BackendModule` decorator for feature modules with lifecycle hooks

### Testing Standards

- **Test behavior, not implementation** — test contracts, edge cases, observable outcomes
- **Node testing**: Jest for backend/node testing, `nock` for HTTP mocking
- **Frontend testing**: Vitest
- **E2E testing**: Playwright (see `packages/testing/playwright/AGENTS.md`)
- **Mock types**: Prefer reusable hoisted `mock<T>(...)` fixtures over `as unknown as T`
- **Vitest + decorators**: Use `createVitestConfigWithDecorators` for packages using `@n8n/di`
- **Schema integration tests**: Validate API request/response shapes against Zod schemas

### Code Quality

- Formatting: Biome
- Linting: ESLint
- Git hooks: lefthook
- Package specific: Run `pnpm lint` + `pnpm typecheck` from within package directory
- Full repo: Only before final PR

## Key Design Principles

1. **Security must not degrade the building experience** — security should be invisible in the common case
2. **Security Fix Hygiene** — never expose vulnerability details in public artifacts (branch names, commit messages, test descriptions)
3. **Core is a narrow waist** — `packages/workflow` provides interfaces/types; capability lives in specialized packages
4. **Clean interface boundary** — agent core (`@n8n/instance-ai`) has no dependency on n8n internals

## Development Workflow

- Always use `pnpm` (not npm/yarn)
- Use Linear for ticket tracking
- Branch from fresh master with Linear-suggested name (unless security fix)
- Draft PRs via `gh pr create --draft`

## Project Structure

For full structure see [[n8n-architecture]]. Key packages:

### Frontend
- `packages/frontend/editor-ui/` — Vue 3 + TypeScript + Vite + Pinia
- `packages/frontend/@n8n/design-system/` — Component library with CSS tokens
- `packages/frontend/@n8n/i18n/` — Translation strings
- All UI text through i18n
- `data-testid` values must be single words (no spaces)

### Backend
- `packages/cli/` — Express server, controllers, services, TypeORM
- `packages/core/` — Execution engine, credentials, binary data
- `packages/workflow/` — Core types, graph traversal, expression engine
- `packages/nodes-base/` — 307+ node implementations

### AI / Extensions
- `packages/@n8n/instance-ai/` — Autonomous agent (framework-agnostic core)
- `packages/@n8n/mcp-apps/` — MCP server for n8n app features
- `packages/@n8n/mcp-browser/` — Browser automation MCP server
- `packages/@n8n/nodes-langchain/` — AI/LangChain node types

## Related

- n8n Architecture: [[n8n-architecture]]
- n8n Instance AI: [[n8n-instance-ai]]
- n8n MCP: [[n8n-mcp]]
- n8n API: [[n8n-api]]
- n8n Deployment: [[n8n-deployment]] -- Deployment models, Docker images, and scaling
- Wiki entry: [[n8n]]
