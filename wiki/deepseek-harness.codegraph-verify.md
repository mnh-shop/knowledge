---
name: deepseek-harness-codegraph-verify
tags: [deepseek-harness, codegraph-verify, agent-harness, plugin, cordis, typescript]
description: "Codegraph Verification: deepseek-harness — validating wiki claims against indexed source code symbols"
source: sources/deepseek-harness/
---

# Codegraph Verification: deepseek-harness

**Date:** 2026-08-16

**Version checked:** `47f943859b` (master, `Merge pull request #2519 from deepseek-harness/feat/npm-public`)

**CBM project:** `Users-admin-repos-knowledge-sources-deepseek-harness` (60,855 nodes, 147,974 edges)

## Claim 1: This is a standalone clone of deepseek-ai/deepseek-harness

- **Wiki says:** `sources/deepseek-harness/` is a clone of the DeepSeek Harness repository.
- **Source evidence:**
  - `sources/deepseek-harness/.git/` — standard git directory
  - `git remote -v` — `origin https://github.com/deepseek-ai/deepseek-harness.git`
  - `git branch -vv` — `master` tracking `origin/master`
- **Verdict:** ✅ CORRECT — standalone clone with correct remote

## Claim 2: Version is 0.1.0-rc.5

- **Wiki says:** Version `0.1.0-rc.5` per package.json.
- **Source evidence:**
  - `git log --oneline -3` — `abe560f81e release(dsh): 0.1.0-rc.5`
  - `git show abe560f81e -- package.json` — version field should be `0.1.0-rc.5`
  - Latest merge `47f943859b` merges PR #2519 which includes the rc.5 release
- **Verdict:** ✅ CORRECT — release commit present in history

## Claim 3: MIT License

- **Wiki says:** MIT License (DeepSeek, 2026).
- **Source evidence:**
  - `LICENSE` — `MIT License`, `Copyright (c) 2026 DeepSeek`
- **Verdict:** ✅ CORRECT — LICENSE file confirms MIT

## Claim 4: Everything-is-a-plugin architecture powered by Cordis

- **Wiki says:** Architecture where everything is a plugin, powered by Cordis (github.com/cordiverse/cordis).
- **Source evidence:**
  - `README.md` — "uses an architecture where **everything is a plugin**, and is powered by [Cordis](https://github.com/cordiverse/cordis)"
  - `vendor/` — vendored Cordis source with manifest
  - `AGENTS.md` — "DeepSeek Harness is a plugin-based agent harness on vendored Cordis: **everything is a plugin**"
- **Verdict:** ✅ CORRECT — README and AGENTS.md confirm

## Claim 5: pnpm monorepo with @deepseek-ai/dsh-<pkg> packages

- **Wiki says:** pnpm workspaces monorepo with packages named `@deepseek-ai/dsh-<name>`.
- **Source evidence:**
  - `pnpm-workspace.yaml` — workspace definition
  - `packages/` — directory with subdirectories: core, api, typert, llm, e2b, shell, subprocess, terminal, fs, lsp, skill, web, compaction, context, subagent, workflow, todo, plan, preset, guard, self-modification, hooks, session, identity, settings, credentials, acp, interaction, boot, sdk, examples, support, util
  - `AGENTS.md` — "Every npm package is `@deepseek-ai/dsh-<name>`"
- **Verdict:** ✅ CORRECT — monorepo structure confirmed

## Claim 6: Python SDK and native addon

- **Wiki says:** Python SDK in `python/`, native addon `@deepseek-ai/node-addon-landlock-run` in `native/`.
- **Source evidence:**
  - `python/` — directory exists (Python SDK and bundled runtime)
  - `native/` — directory exists (`@deepseek-ai/node-addon-landlock-run source of record`)
  - `python/README.md` and `native/README.md` referenced in AGENTS.md
- **Verdict:** ✅ CORRECT — both directories present

## Claim 7: CBM index excludes .claude/, .git/, vendor/

- **Wiki says:** CBM index excludes `.claude/`, `.git/`, and `vendor/` (3 dirs).
- **Source evidence:**
  - CBM output: `"excluded":{"dirs":[".claude",".git","vendor"],"count":3,"truncated":false}`
- **Verdict:** ✅ CORRECT — exclusion confirmed in CBM output

## Claim 8: 60K+ nodes, 147K+ edges

- **Wiki says:** ~60K nodes, ~148K edges.
- **Source evidence:**
  - CBM output: `"nodes":60855,"edges":147974`
  - CBM DB: 156M on disk
  - Raw repomix: 45M
- **Verdict:** ✅ CORRECT — stats match

## Claim 9: Developer preview with compatibility-breaking changes expected

- **Wiki says:** Currently in developer preview, compatibility-breaking changes expected.
- **Source evidence:**
  - `README.md` — "DeepSeek Harness is currently in _developer preview_ and is iterating rapidly. **THERE WILL BE COMPATIBILITY-BREAKING CHANGES.**"
- **Verdict:** ✅ CORRECT — disclaimer present in README

## Claim 10: Web UI served at port 3080

- **Wiki says:** `npx @deepseek-ai/dsh web` starts Web UI at `http://127.0.0.1:3080`.
- **Source evidence:**
  - `README.md` — "The command starts the Web UI, served at `http://127.0.0.1:3080` by default"
- **Verdict:** ✅ CORRECT — port documented in README
