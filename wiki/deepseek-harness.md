---
name: deepseek-harness
tags: [agent-harness, plugin, cordis, typescript, node, deepseek, agent-os, web-ui, e2b, lsp, acp]
description: "Wiki entry for DeepSeek Harness (dsh) — open-source plugin-based agent harness by DeepSeek AI"
source: sources/deepseek-harness/
verification_date: 2026-08-16
verified_by: codegraph-verify
---

# deepseek-harness

||| Field | Value |
|||---|---|
||| **Origin** | [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) |
||| **Version** | `0.1.0-rc.5` (package.json, release commit abe560f8) |
||| **Commit** | `47f943859b` — `Merge pull request #2519 from deepseek-harness/feat/npm-public` |
||| **License** | MIT (DeepSeek, 2026) |
||| **Source** | `sources/deepseek-harness/` |
||| **Branches** | `master` |
||| **CBM index** | `Users-admin-repos-knowledge-sources-deepseek-harness` (~60K nodes, ~148K edges) |

## What is it?

DeepSeek Harness (`dsh`) is an open-source agent harness developed by DeepSeek AI. It uses a **everything-is-a-plugin** architecture powered by [Cordis](https://github.com/cordiverse/cordis), a meta-framework for spatiotemporal composability described in the [Cordis paper](https://github.com/cordiverse/paper).

Currently in **developer preview** — compatibility-breaking changes expected.

## Architecture

```
pnpm workspaces monorepo (@deepseek-ai/dsh-<pkg>)
├── packages/core/        product API spine: session, system-prompt, tools, agent, agent-loop
├── packages/api/         Remote BFF assembly and Typert RPC gateway
├── packages/typert/      type graph generator, loader, and runtime registry
├── packages/llm/         LLM capability: Service Definition/Consumer + DeepSeek providers
├── packages/e2b/         E2B POC: sandbox + FS/subprocess adapters
├── packages/shell/       bash capability
├── packages/subprocess/  subprocess capability
├── packages/terminal/    persistent sessions
├── packages/fs/          filesystem capability + policy
├── packages/lsp/         language-server capability
├── packages/skill/       skill provider registry + local impl + catalog/loader
├── packages/web/         web capability: search/fetch providers
├── packages/compaction/  compaction capability
├── packages/context/     request-context plugins
├── packages/subagent/    subagent capability
├── packages/workflow/    workflow capability
├── packages/acp/         automation-only Agent Client Protocol server
├── packages/sdk/         JSON-RPC protocol, server, and TypeScript client
├── packages/hooks/       Claude Code/Codex hook bridges
├── vendor/               Vendored Cordis source
├── python/               Python SDK and bundled runtime
├── native/               @deepseek-ai/node-addon-landlock-run
└── examples/             Runnable cordis.yml demo bundles
```

Key architectural principles:

- **ESM everywhere** (`"type": "module"`)
- **Registrations are effects** — every contribution goes through `ctx.effect()` / `ctx.on()`
- **Runtime invariants assert owned relationships**
- **Typed events use declaration merging**
- **Vendored Cordis** in `vendor/` with manifest + sync procedure

## Run

```sh
# From npm
npx @deepseek-ai/dsh web          # Web UI at http://127.0.0.1:3080

# From source
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

## Key files

- `README.md` — overview, run instructions, bilingual (EN/ZH)
- `AGENTS.md` — repo-level agent conventions, repository layout, commands
- `packages/AGENTS.md` — package invariant rules
- `vendor/README.md` — Cordis vendoring manifest + sync procedure
- `docs/architecture.md` — architecture docs
- `pnpm-workspace.yaml` — workspace definition
- `package.json` — root with 0.1.0-rc.5 version
- `LICENSE` — MIT
- `python/` — Python SDK and bundled runtime
- `native/` — landlock-run native addon

## Commands

```sh
pnpm install
pnpm run build          # tsc + tsdown
pnpm run test           # vitest unit tests
pnpm run test:e2e       # real-API tests (needs DEEPSEEK_API_KEY)
pnpm run test:snapshot  # keyless ACP/headless replay
pnpm run typecheck
pnpm run lint
pnpm run hygiene        # knip + publint + workspace constraints
pnpm run doc-sync       # documentation gates
pnpm run website:build  # VitePress build
pnpm dsh --profile headless "task"   # run one task (needs key)
```

## CBM index

CBM index captures `master` at commit `47f943859b`. Excludes `.claude/`, `.git/`, and `vendor/` (3 dirs). 60,855 nodes, 147,974 edges.

## Verification

See [[deepseek-harness.codegraph-verify]] for evidence-backed claims.
