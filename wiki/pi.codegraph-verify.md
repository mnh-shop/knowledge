---
title: pi.codegraph-verify
description: "Source-level verification of pi — TypeScript agent harness"
date: 2026-07-12
tags: [pi, codegraph-verify, agent, typescript, coding-agent]
verified_by: codegraph-explore
source: sources/pi/
---

# pi — CodeGraph Verification

**Claim-1: Pi is a TypeScript agent harness providing a multi-package ecosystem including an interactive coding agent CLI, agent runtime, and unified multi-provider LLM API.**

- **Evidence:** `README.md` lines 13-19 state: "This is the home of the Pi agent harness project including our self extensible coding agent." Three core packages are listed: `@earendil-works/pi-coding-agent` (interactive coding agent CLI), `@earendil-works/pi-agent-core` (agent runtime with tool calling and state management), and `@earendil-works/pi-ai` (unified multi-provider LLM API). `package.json` confirms the workspace structure with packages at `packages/agent/`, `packages/ai/`, `packages/coding-agent/`, `packages/orchestrator/`, and `packages/tui/`. The project builds with TypeScript via esbuild and uses Biome for linting and formatting.
- **Source path:** `sources/pi/README.md`, `sources/pi/package.json`

**Claim-2: Pi's `@earendil-works/pi-ai` package provides a unified multi-provider LLM API supporting OpenAI, Anthropic, Google, and other providers.**

- **Evidence:** `README.md` line 19 explicitly states: "Unified multi-provider LLM API (OpenAI, Anthropic, Google, …)". The package table at lines 28-34 repeats this description. The `packages/ai/` directory contains scripts for model generation (`scripts/generate-models.ts`) and a `models.generated.ts` output, indicating a structured model catalog. The `packages/ai/` directory is listed as workspace package in `package.json`.
- **Source path:** `sources/pi/README.md`, `sources/pi/package.json`

**Claim-3: Pi includes a Terminal UI (TUI) library with differential rendering in `@earendil-works/pi-tui`.**

- **Evidence:** `README.md` package table entry: "**@earendil-works/pi-tui** - Terminal UI library with differential rendering". The `packages/tui/` directory exists in the source. The build order in `package.json` line 15 confirms TUI is built first: `"build": "cd packages/tui && npm run build && cd ../ai && npm run build && cd ../agent && npm run build && cd ../coding-agent && npm run build"`, indicating TUI is a foundational rendering layer for the agent CLI.
- **Source path:** `sources/pi/README.md`, `sources/pi/package.json`

**Claim-4: Pi implements supply-chain hardening with pinned dependencies, lockfile verification, shrinkwrap generation, and `--ignore-scripts` by default.**

- **Evidence:** `README.md` lines 62-72 document the supply-chain practices: "Direct external dependencies are pinned to exact versions" (line 66), "`.npmrc` sets `save-exact=true` and `min-release-age=2`" (line 67), "Pre-commit blocks accidental lockfile commits unless `PI_ALLOW_LOCKFILE_CHANGE=1` is set" (line 68), "CI installs with `npm ci --ignore-scripts`" (line 72), and "a scheduled GitHub workflow runs `npm audit --omit=dev` plus `npm audit signatures --omit=dev`" (line 72). The `AGENTS.md` "Dependency and Install Security" section expands on shrinkwrap generation with explicit allowlists for lifecycle scripts.
- **Source path:** `sources/pi/README.md`, `sources/pi/AGENTS.md`

**Claim-5: Pi supports three containerization/sandboxing patterns: Gondolin (Linux micro-VM), plain Docker, and OpenShell policy-controlled sandbox.**

- **Evidence:** `README.md` lines 38-46 document the permission model: "Pi does not include a built-in permission system for restricting filesystem, process, network, or credential access." Three isolation patterns are described: "**Gondolin extension**: keep `pi` and provider auth on the host while routing built-in tools and `!` commands into a local Linux micro-VM" (line 44), "**Plain Docker**: run the whole `pi` process in a local container for simple isolation" (line 45), and "**OpenShell**: run the whole `pi` process in a policy-controlled sandbox" (line 46). The Gondolin extension example is referenced in the workspace at `packages/coding-agent/examples/extensions/gondolin`.
- **Source path:** `sources/pi/README.md`, `sources/pi/package.json`

**Claim-6: Pi uses a lockstep versioning model with release automation — all packages share one version, releases include CHANGELOG updates, smoke testing, and tag-driven CI publishing.**

- **Evidence:** `AGENTS.md` "Releasing" section (lines ~249-284) documents the full process: "**Lockstep versioning**: all packages share one version; every release updates all together." The smoke test procedure builds an unpublished release and tests it from outside the repo in both Node and Bun configurations. The release script (`scripts/release.mjs`) handles version bump, CHANGELOG finalization, commit, tag, and push. CI publishes npm packages when the tag is pushed via `.github/workflows/build-binaries.yml` using trusted publishing with OIDC. The `package.json` defines `release:patch`, `release:minor`, and `release:major` scripts.
- **Source path:** `sources/pi/AGENTS.md`, `sources/pi/package.json`

**Related:** [[pi]], [[oh-my-pi]], [[nanobot]], [[materia]]
