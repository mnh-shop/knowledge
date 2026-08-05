---
name: openai-skills-codegraph-verify
tags: [openai-skills, codegraph-verify, openai, skills, codex, deprecated]
description: "Codegraph Verification: openai-skills — validating corrected wiki claims against indexed source code"
source: sources/openai-skills/
---

# Codegraph Verification: openai-skills

**Date:** 2026-07-12

## Claim 1: Repository is deprecated and points to the OpenAI Plugins repository
- **Wiki says:** The repository is deprecated; the README's very first lines redirect to the OpenAI Plugins repository (`openai/plugins`) and the "Build plugins" guide for skill-only plugins.
- **Source evidence:**
  - `README.md` line 1-2: "> [!IMPORTANT] > **This repository is deprecated.** For current Codex skill and plugin examples, use the [OpenAI Plugins repository](https://github.com/openai/plugins). If you want to add your own skills to Codex, follow the [Build plugins](https://developers.openai.com/codex/plugins/build) guide, which includes instructions for creating a skill-only plugin."
  - `README.md` line 6: "Agent Skills are folders of instructions, scripts, and resources that AI agents can discover and use to perform at specific tasks. Write once, use everywhere."
  - `README.md` line 8: "Codex uses skills to help package capabilities that teams and individuals can use to complete specific tasks in a repeatable way. This repository catalogs skills for use and distribution with Codex."
  - `README.md` line 10-13: Links to "Using skills in Codex", "Create custom skills in Codex", and the "Agent Skills open standard" at `https://agentskills.io`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Static catalog with no application code (no CLI, API, or installer)
- **Wiki says:** The repository contains no application code — no CLI, no REST API, no web UI, no installer implementation. The root contains only `README.md`, `contributing.md`, `.gitignore`, and `skills/`.
- **Source evidence:**
  - Repository root listing contains exactly: `.git/`, `.gitignore`, `README.md` (1840 bytes, 43 lines), `contributing.md` (527 bytes, 11 lines), `skills/`
  - No top-level `LICENSE`, no `package.json`, no `go.mod`, no `pyproject.toml`, no source/ or test/ trees — nothing executable
  - `README.md` line 15-39: the "Installing a skill" section describes consuming skills via the `$skill-installer` command **inside Codex**, not via any tool in this repo
  - `README.md` line 43: licensing is delegated per-skill, implying no repo-level packaging machinery
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Tier structure — 5 system + 39 curated skills; `.experimental/` documented but absent from snapshot
- **Wiki says:** `skills/.system/` holds exactly 5 skills (auto-installed), `skills/.curated/` holds exactly 39 skills (installable by name), and `.experimental/` is documented in the README (via `create-plan` examples) but absent from the checked-out snapshot.
- **Source evidence:**
  - `skills/.system/` contains exactly 5 directories: `imagegen/`, `openai-docs/`, `plugin-creator/`, `skill-creator/`, `skill-installer/`
  - `skills/.curated/` contains exactly 39 directories: `aspnet-core`, `chatgpt-apps`, `cli-creator`, `cloudflare-deploy`, `define-goal`, `figma`, `figma-code-connect-components`, `figma-create-design-system-rules`, `figma-create-new-file`, `figma-generate-design`, `figma-generate-library`, `figma-implement-design`, `figma-use`, `gh-address-comments`, `gh-fix-ci`, `hatch-pet`, `jupyter-notebook`, `linear`, `migrate-to-codex`, `netlify-deploy`, `notion-knowledge-capture`, `notion-meeting-intelligence`, `notion-research-documentation`, `notion-spec-to-implementation`, `openai-docs`, `pdf`, `playwright`, `playwright-interactive`, `render-deploy`, `screenshot`, `security-best-practices`, `security-ownership-map`, `security-threat-model`, `sentry`, `speech`, `transcribe`, `vercel-deploy`, `winui-app`, `yeet` (39 total, counted with `ls -d skills/.curated/*/`)
  - `skills/` top level contains only `.curated/` and `.system/` — no `.experimental/` directory on disk
  - `README.md` line 17: "Skills in [`.system`](skills/.system/) are automatically installed in the latest version of Codex."
  - `README.md` line 19: "To install [curated](skills/.curated/) or [experimental](skills/.experimental/) skills, you can use the `$skill-installer` inside Codex."
  - `README.md` line 30-31: "`$skill-installer install the create-plan skill from the .experimental folder`"
  - `README.md` line 36: "`$skill-installer install https://github.com/openai/skills/tree/main/skills/.experimental/create-plan`"
- **Verdict:** ✅ CORRECT (with the snapshot-accurate caveat that `.experimental/` content is not present locally)
- **Fix needed:** None

## Claim 4: Standard skill frontmatter — `name` + `description` (+ optional `metadata`)
- **Wiki says:** Each `SKILL.md` opens with YAML frontmatter containing `name` and `description`, optionally extended with a `metadata` block.
- **Source evidence:**
  - `skills/.curated/figma/SKILL.md` line 1-4: `---` / `name: figma` / `description: Use the Figma MCP server to fetch design context, screenshots, variables, and assets from Figma, ...` / `---`
  - `skills/.system/skill-creator/SKILL.md` line 1-6: `---` / `name: skill-creator` / `description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities ...` / `metadata:` / `  short-description: Create or update a skill` / `---`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: `skill-creator` is a 368-line authoring guide
- **Wiki says:** The `skill-creator` system skill is a comprehensive 368-line guide for creating effective Codex skills.
- **Source evidence:**
  - `skills/.system/skill-creator/SKILL.md` is 368 lines total (confirmed via file read: "Showing lines 1-15 of 368")
  - `skills/.system/skill-creator/SKILL.md` line 12-15: "Skills are modular, self-contained folders that extend Codex's capabilities by providing specialized knowledge, workflows, and tools. Think of them as 'onboarding guides' for specific..."
  - `skills/.system/skill-creator/` also contains `agents/`, `references/`, `scripts/`, `LICENSE.txt` — the full skill payload structure
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: `$skill-installer` mechanism — by name, by path, or by GitHub URL
- **Wiki says:** Codex provides `$skill-installer` to install curated skills by name (defaults to `skills/.curated`), experimental skills by folder path, and any skill by GitHub directory URL; Codex must be restarted afterward.
- **Source evidence:**
  - `README.md` line 21: "Curated skills can be installed by name (defaults to `skills/.curated`):"
  - `README.md` line 24: "`$skill-installer gh-address-comments`"
  - `README.md` line 30-31: "`$skill-installer install the create-plan skill from the .experimental folder`"
  - `README.md` line 36: "`$skill-installer install https://github.com/openai/skills/tree/main/skills/.experimental/create-plan`"
  - `README.md` line 39: "After installing a skill, restart Codex to pick up new skills."
  - `skills/.system/skill-installer/` exists with `agents/`, `assets/`, `scripts/` — the installer is itself shipped as a system skill
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Per-skill licensing — no top-level license, `LICENSE.txt` inside each skill directory
- **Wiki says:** There is no repository-level license; each individual skill carries its own `LICENSE.txt` inside its directory.
- **Source evidence:**
  - `README.md` line 41-43: "## License" / "The license of an individual skill can be found directly inside the skill's directory inside the `LICENSE.txt` file."
  - No `LICENSE` or `LICENSE.txt` at repository root (root listing shows only `.git/`, `.gitignore`, `README.md`, `contributing.md`, `skills/`)
  - `skills/.curated/figma/LICENSE.txt` exists
  - `skills/.system/skill-creator/LICENSE.txt` exists
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 7 key claims from the corrected openai-skills wiki have been verified against the source:
- ✅ Deprecation notice (README.md:1-2) redirecting to `openai/plugins` and the Build plugins guide
- ✅ Static catalog — repository root is only README.md, contributing.md, .gitignore, skills/; no application code
- ✅ 5 system + 39 curated skills confirmed by directory count; `.experimental/` documented in README but absent from snapshot
- ✅ Frontmatter convention: `name` + `description` (+ optional `metadata`) in SKILL.md
- ✅ `skill-creator` is a 368-line authoring guide with full skill payload
- ✅ `$skill-installer` supports name-based, path-based, and URL-based installation; restart required
- ✅ Per-skill `LICENSE.txt` with no repository-level license

## Related

- [[openai-skills]] — Main wiki entry
- [[skills]] — Agent skills platform and registry
- [[Anthropic-Cybersecurity-Skills]] — 817-skill cybersecurity library following the agentskills.io standard
- [[abvx-agent-skills]] — Auditable skillpack for coding agents

## Cross-project

- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
- [[abvx-agent-skills.codegraph-verify]] — Similar codegraph verification for ABVX Agent Skills
- [[drawio-skill.codegraph-verify]] — Similar codegraph verification for drawio-skill
- [[agentfield.codegraph-verify]] — Similar codegraph verification for AgentField
