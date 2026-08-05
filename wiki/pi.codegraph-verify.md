---
title: pi.codegraph-verify
description: "Source-level verification of pi — TypeScript agent harness"
date: 2026-07-12
tags: [pi, codegraph-verify, agent, typescript, coding-agent]
verified_by: codegraph-explore
source: sources/pi/
---

# pi — CodeGraph Verification

**Claim-1: Pi is a TypeScript agent harness providing a multi-package monorepo under the `@earendil-works` npm scope — seven packages: coding-agent CLI, agent runtime, unified multi-provider LLM API, TUI, SQLite storage, server, and evals.**

- **Evidence:** `README.md` lines 13-19 state: "This is the home of the Pi agent harness project including our self extensible coding agent." Core packages listed are `@earendil-works/pi-coding-agent` (interactive coding agent CLI), `@earendil-works/pi-agent-core` (agent runtime with tool calling and state management), and `@earendil-works/pi-ai` (unified multi-provider LLM API). `package.json` workspaces confirm the full package set: `packages/agent/`, `packages/ai/`, `packages/coding-agent/`, `packages/tui/`, `packages/server/`, `packages/evals/`, and `packages/storage/*` (no `packages/orchestrator` exists). Per-package `package.json` files confirm the scope and names: `@earendil-works/pi-server`, `@earendil-works/pi-evals`, `@earendil-works/pi-storage-sqlite-node`. The root build script compiles tui → ai → agent → storage/sqlite-node → coding-agent → server in order. The project builds with TypeScript via esbuild and uses Biome for linting and formatting.
- **Source path:** `sources/pi/README.md`, `sources/pi/package.json`, `sources/pi/packages/{server,evals,storage/sqlite-node}/package.json`

**Claim-2: Pi's `@earendil-works/pi-ai` package provides a unified multi-provider LLM API supporting OpenAI, Anthropic, Google, and 40+ other provider files, with four transport modes.**

- **Evidence:** `README.md` line 19 explicitly states: "Unified multi-provider LLM API (OpenAI, Anthropic, Google, …)". The `packages/ai/src/providers/` directory contains 83 entries including `anthropic.ts`, `openai.ts`, `google.ts`, `amazon-bedrock.ts`, `deepseek.ts`, `nvidia.ts`, `kimi-coding.ts`, `xai.ts`, `openai-codex.ts`, `opencode.ts`, and more. `packages/ai/src/types.ts:103` defines the transport union: `export type Transport = "sse" | "websocket" | "websocket-cached" | "auto";`. The package table at `README.md` lines 28-34 repeats the description.
- **Source path:** `sources/pi/README.md`, `sources/pi/packages/ai/src/types.ts`, `sources/pi/packages/ai/src/providers/`

**Claim-3: Pi includes a Terminal UI (TUI) library with differential rendering in `@earendil-works/pi-tui`.**

- **Evidence:** `README.md` package table entry: "**@earendil-works/pi-tui** - Terminal UI library with differential rendering". The `packages/tui/` directory exists in the source. The build order in `package.json` confirms TUI is built first (`cd packages/tui && npm run build && cd ../ai && …`), indicating TUI is a foundational rendering layer for the agent CLI.
- **Source path:** `sources/pi/README.md`, `sources/pi/package.json`

**Claim-4: Pi implements supply-chain hardening with pinned dependencies, lockfile verification, shrinkwrap generation, and `--ignore-scripts` by default.**

- **Evidence:** `README.md` supply-chain section documents the practices: "Direct external dependencies are pinned to exact versions", "`.npmrc` sets `save-exact=true` and `min-release-age=2`", "Pre-commit blocks accidental lockfile commits unless `PI_ALLOW_LOCKFILE_CHANGE=1` is set", "CI installs with `npm ci --ignore-scripts`", and "a scheduled GitHub workflow runs `npm audit --omit=dev` plus `npm audit signatures --omit=dev`". The `AGENTS.md` "Dependency and Install Security" section expands on shrinkwrap generation with explicit allowlists for lifecycle scripts.
- **Source path:** `sources/pi/README.md`, `sources/pi/AGENTS.md`

**Claim-5: Pi supports three containerization/sandboxing patterns: Gondolin (Linux micro-VM), plain Docker, and OpenShell policy-controlled sandbox.**

- **Evidence:** `README.md` documents the permission model: "Pi does not include a built-in permission system for restricting filesystem, process, network, or credential access." Three isolation patterns are described: "**Gondolin extension**: keep `pi` and provider auth on the host while routing built-in tools and `!` commands into a local Linux micro-VM", "**Plain Docker**: run the whole `pi` process in a local container for simple isolation", and "**OpenShell**: run the whole `pi` process in a policy-controlled sandbox". The Gondolin extension example is referenced at `packages/coding-agent/examples/extensions/gondolin` and is a declared workspace.
- **Source path:** `sources/pi/README.md`, `sources/pi/package.json`

**Claim-6: Pi uses a lockstep versioning model with release automation — all packages share one version, releases include CHANGELOG updates, smoke testing, and tag-driven CI publishing.**

- **Evidence:** `AGENTS.md` "Releasing" section documents the full process: "**Lockstep versioning**: all packages share one version; every release updates all together." The smoke test procedure builds an unpublished release and tests it from outside the repo in both Node and Bun configurations. The release script (`scripts/release.mjs`) handles version bump, CHANGELOG finalization, commit, tag, and push. CI publishes npm packages when the tag is pushed via `.github/workflows/build-binaries.yml` using trusted publishing with OIDC. The `package.json` defines `release:patch`, `release:minor`, and `release:major` scripts.
- **Source path:** `sources/pi/AGENTS.md`, `sources/pi/package.json`

**Claim-7: Extensions are auto-discovered from `~/.pi/agent/extensions/` (global) and `.pi/extensions/` (project-local), not `~/.pi/extensions/`.**

- **Evidence:** `packages/coding-agent/docs/extensions.md:7`: "Put extensions in `~/.pi/agent/extensions/` (global) or `.pi/extensions/` (project-local) for auto-discovery." The "Extension Locations" table (lines 113-120) lists `~/.pi/agent/extensions/*.ts`, `~/.pi/agent/extensions/*/index.ts`, `.pi/extensions/*.ts`, and `.pi/extensions/*/index.ts`; project-local entries load only after the project is trusted. The Quick Start example (line 58) creates `~/.pi/agent/extensions/my-extension.ts`.
- **Source path:** `sources/pi/packages/coding-agent/docs/extensions.md`

**Claim-8: Pi ships a SQLite session storage backend and an experimental server package beyond the four core packages.**

- **Evidence:** `packages/storage/sqlite-node/README.md` describes `@earendil-works/pi-storage-sqlite-node`: "Node sqlite storage backend for `@earendil-works/pi-agent-core` sessions. Provides the `node:sqlite` adapter (`SqliteDatabase` implementation) and the SQLite session repo/storage implementation (`SqliteSessionRepo`, migrations, materialized views)." `packages/server/README.md` states: "Experimental. This package is under active development and may change or be removed without notice." and its `src/` contains `supervisor.ts`, `rpc-process.ts`, `radius.ts`, `ipc/`, and `storage.ts`. `packages/evals/README.md` describes "behavioral, model-backed checks for Pi workflows" run via `npm run eval`.
- **Source path:** `sources/pi/packages/storage/sqlite-node/README.md`, `sources/pi/packages/server/README.md`, `sources/pi/packages/evals/README.md`

**Related:** [[pi]], [[nanobot]], [[materia]]
