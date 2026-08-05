---
name: superpowers-codegraph-verify
tags: [superpowers, skills, methodology, plugin, coding-agents, opencode, wiki]
description: "Codegraph Verification: superpowers — validating wiki claims against indexed source code symbols"
source: sources/superpowers/
---

# Codegraph Verification: superpowers

**Date:** 2026-07-30

## Claim 1: Origin is obra/superpowers, built by Jesse Vincent + Prime Radiant
- **Wiki says:** Origin is [obra/superpowers](https://github.com/obra/superpowers), built by Jesse Vincent and Prime Radiant.
- **Source evidence:**
  - Git remote: `git remote -v` → `origin https://github.com/obra/superpowers (fetch/push)`
  - `README.md` line 277: "Superpowers is built by [Jesse Vincent](https://blog.fsck.com) and the rest of the folks at [Prime Radiant](https://primeradiant.com)."
  - `README.md` line 24 references commercial support at `sales@primeradiant.com`.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously WRONG: wiki stated origin teknologist/superpowers)

## Claim 2: MIT license
- **Wiki says:** License is MIT (© 2025 Jesse Vincent).
- **Source evidence:**
  - `LICENSE` lines 1-3: "MIT License / Copyright (c) 2025 Jesse Vincent"
  - `README.md` line 269: "MIT License - see LICENSE file for details"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously WRONG: wiki stated "Not specified")

## Claim 3: 11 supported harnesses — Windsurf is NOT among them
- **Wiki says:** Works with 11 harnesses: Claude Code, Antigravity, Codex App, Codex CLI, Cursor, Factory Droid, Gemini CLI, GitHub Copilot CLI, Kimi Code, OpenCode, Pi.
- **Source evidence:**
  - `README.md` line 8 lists exactly 11 harness links: Claude Code, Antigravity, Codex App, Codex CLI, Cursor, Factory Droid, Gemini CLI, GitHub Copilot CLI, Kimi Code, OpenCode, Pi.
  - A full-repo grep for "Windsurf" (README.md, docs/, hooks/, skills/) returns no match — no Windsurf installation path exists.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously WRONG: wiki claimed "Claude Code, Cursor, Windsurf, and any agent with plugin support")

## Claim 4: Basic Workflow has 7 phases — there is NO documentation-generation phase
- **Wiki says:** The pipeline has 7 phases: brainstorming → using-git-worktrees → writing-plans → subagent-driven-development/executing-plans → test-driven-development → requesting-code-review → finishing-a-development-branch.
- **Source evidence:**
  - `README.md` lines 196-212 document "The Basic Workflow" with exactly 7 numbered phases: 1 brainstorming, 2 using-git-worktrees, 3 writing-plans, 4 subagent-driven-development or executing-plans, 5 test-driven-development, 6 requesting-code-review, 7 finishing-a-development-branch.
  - No documentation-generation skill exists among the 14 skills in `skills/` (brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously FABRICATED: wiki claimed a 5-phase table with a "Document — Auto-generate documentation" phase)

## Claim 5: Install commands use /plugin install + marketplace, not `claude plugins install superpowers`
- **Wiki says:** Install via `/plugin install superpowers@claude-plugins-official` or `/plugin marketplace add obra/superpowers-marketplace`.
- **Source evidence:**
  - `README.md` lines 36-40: official marketplace install is `/plugin install superpowers@claude-plugins-official`
  - `README.md` lines 46-56: alternate path is `/plugin marketplace add obra/superpowers-marketplace` then `/plugin install superpowers@superpowers-marketplace`
  - `README.md` line 32: Superpowers is available via the official Claude plugin marketplace (claude.com/plugins/superpowers)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously WRONG: wiki documented `claude plugins install superpowers`)

## Claim 6: Manual skill-file copying is not a real integration
- **Wiki says:** Manually copying skill files into a harness is not a real integration and is against maintainer policy; a real integration loads the `using-superpowers` bootstrap at session start.
- **Source evidence:**
  - `AGENTS.md` line 84: "**These are not real integrations and will be closed:**"
  - `AGENTS.md` line 86: "- Manually copying skill files into the harness"
  - `AGENTS.md` lines 87-89 list the other non-integrations (npx skills wrappers, per-session opt-in, anything where `brainstorming` does not auto-trigger on the acceptance test).
  - `AGENTS.md` line 82: "A real integration loads the `using-superpowers` bootstrap at session start. The bootstrap is what causes skills to auto-trigger at the right moments. Without it, the skills are dead weight — present on disk but never invoked."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously WRONG: wiki documented `git clone ... && cp -r skills/*` as a supported install path)

## Claim 7: Version 6.2.0 zero-dependency plugin with 94% PR rejection rate
- **Wiki says:** Superpowers is v6.2.0, zero-dependency by design, with a 94% PR rejection rate for AI contributions.
- **Source evidence:**
  - `package.json` line 3: `"version": "6.2.0"`; no `dependencies`/`devDependencies` sections
  - `AGENTS.md` line 38: "Superpowers is a zero-dependency plugin by design."
  - `AGENTS.md` line 7: "This repo has a 94% PR rejection rate."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Bootstrap injection via message transform + config hook, plus hooks/ and per-harness extensions
- **Wiki says:** The plugin bootstraps by injecting `using-superpowers` context via message transform and auto-registering the skills directory via config hook; harness hooks and per-harness extensions exist.
- **Source evidence:**
  - `.opencode/plugins/superpowers.js` lines 3-5: "Injects superpowers bootstrap context via message transform. Auto-registers skills directory via config hook (no symlinks needed)."
  - `.opencode/plugins/superpowers.js` line 124: `'experimental.chat.messages.transform'` hook injects the bootstrap into the first user message of each session.
  - `.opencode/plugins/superpowers.js` lines 107-113: the `config` hook pushes the skills directory into `config.skills.paths`.
  - `hooks/hooks.json` + `hooks/hooks-cursor.json` define `SessionStart`/`sessionStart` hooks running `hooks/run-hook.cmd session-start` (which executes `hooks/session-start`).
  - `.pi/extensions/superpowers.ts` exists and `package.json` `pi.extensions` lists `./.pi/extensions/superpowers.ts`; the extension injects the `using-superpowers` bootstrap at session startup and after compaction (README.md line 194).
  - `gemini-extension.json` + `GEMINI.md` provide the Gemini CLI extension, and `README.md` line 124: `gemini extensions install https://github.com/obra/superpowers`.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the superpowers wiki have been verified against the source:
- ✅ Origin obra/superpowers + Jesse Vincent / Prime Radiant: confirmed (git remote, README:277)
- ✅ MIT license: confirmed (LICENSE:1-3, README:269)
- ✅ 11 harnesses, no Windsurf: confirmed (README:8, no grep match)
- ✅ 7-phase Basic Workflow, no "Document" phase: confirmed (README:196-212, skills/ listing)
- ✅ /plugin install superpowers@claude-plugins-official: confirmed (README:36-56)
- ✅ Manual copy is a non-integration: confirmed (AGENTS.md:84-90)
- ✅ v6.2.0 zero-dependency + 94% PR rejection: confirmed (package.json, AGENTS.md:7,38)
- ✅ Bootstrap injection + hooks + per-harness extensions: confirmed (plugin code, hooks/, .pi/, gemini-extension.json)

## Related

- [[superpowers]] -- Main wiki entry

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[swe-cli-skills.codegraph-verify]] -- Similar codegraph verification for SWE CLI skills
