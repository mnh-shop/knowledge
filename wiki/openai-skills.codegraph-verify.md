---
name: openai-skills-codegraph-verify
tags: [openai-skills, codegraph-verify, openai, skills, codex]
description: "Codegraph Verification: openai-skills — validating wiki claims against indexed source code symbols"
source: sources/openai-skills/
---

# Codegraph Verification: openai-skills

**Date:** 2026-07-12

## Claim 1: Official OpenAI repository for Codex agent skills (now deprecated)
- **Wiki says:** `openai/skills` is the official OpenAI repository for Codex agent skills, containing system, curated, and experimental skill tiers. Now deprecated in favor of the OpenAI Plugins repository at `openai/plugins`.
- **Source evidence:**
  - `README.md` line 1-3: "> **This repository is deprecated.** For current Codex skill and plugin examples, use the [OpenAI Plugins repository](https://github.com/openai/plugins)."
  - `README.md` line 8: "Agent Skills are folders of instructions, scripts, and resources that AI agents can discover and use"
  - `README.md` line 9: "Codex uses skills to help package capabilities that teams and individuals can use to complete specific tasks in a repeatable way. This repository catalogs skills for use and distribution with Codex."
  - `README.md` line 12-13: References to official Codex documentation: "Using skills in Codex" and "Create custom skills in Codex"
  - `README.md` line 14: "Agent Skills open standard" at `https://agentskills.io`
  - `README.md` line 43: "The license of an individual skill can be found directly inside the skill's directory inside the `LICENSE.txt` file."
  - Repository structure is `openai/skills` on GitHub
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 39 curated + 5 system skills across skill tiers
- **Wiki says:** Skills are organized into three tiers: `.system/` (5 auto-installed skills), `.curated/` (39 community-curated skills installable by name), and `.experimental/` (skills in development). Curated skills cover Figma, Playwright, Linear, Sentry, GitHub, security, deployment, Notion, and more.
- **Source evidence:**
  - `skills/.system/` contains exactly 5 directories: `imagegen/`, `openai-docs/`, `plugin-creator/`, `skill-creator/`, `skill-installer/`
  - `skills/.curated/` contains exactly 39 directories:
    - Design/Figma: `figma/`, `figma-code-connect-components/`, `figma-create-design-system-rules/`, `figma-create-new-file/`, `figma-generate-design/`, `figma-generate-library/`, `figma-implement-design/`, `figma-use/`
    - Testing: `playwright/`, `playwright-interactive/`
    - Project management: `linear/`, `notion-knowledge-capture/`, `notion-meeting-intelligence/`, `notion-research-documentation/`, `notion-spec-to-implementation/`
    - Security: `security-best-practices/`, `security-ownership-map/`, `security-threat-model/`
    - GitHub: `gh-address-comments/`, `gh-fix-ci/`
    - Deployment: `cloudflare-deploy/`, `netlify-deploy/`, `render-deploy/`, `vercel-deploy/`
    - Monitoring: `sentry/`
    - Other: `aspnet-core/`, `chatgpt-apps/`, `cli-creator/`, `define-goal/`, `hatch-pet/`, `jupyter-notebook/`, `migrate-to-codex/`, `openai-docs/`, `pdf/`, `screenshot/`, `speech/`, `transcribe/`, `winui-app/`, `yeet/`
  - `README.md` line 17: "Skills in `.system/` are automatically installed in the latest version of Codex."
  - `README.md` line 19: "To install curated or experimental skills, you can use the `$skill-installer` inside Codex."
  - `README.md` line 21: "Curated skills can be installed by name (defaults to `skills/.curated`)"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Skill Creator system skill with structured 368-line authoring guide
- **Wiki says:** The `skill-creator` system skill provides comprehensive guidance for creating effective Codex skills. Covers core principles (concise context, appropriate freedom degrees), skill structure, tool integrations, bundled resources, and domain expertise patterns. Used as the canonical reference for writing Codex skills.
- **Source evidence:**
  - `skills/.system/skill-creator/SKILL.md` is 368 lines of authoring guidance
  - `skills/.system/skill-creator/SKILL.md` line 1-6: YAML frontmatter: `name: skill-creator`, `description: "Guide for creating effective skills"`
  - `skills/.system/skill-creator/SKILL.md` line 12-25: "About Skills" section explaining the purpose of skills as "onboarding guides"
  - `skills/.system/skill-creator/SKILL.md` line 26-35: "Core Principles": "Concise is Key", "Default assumption: Codex is already very smart"
  - `skills/.system/skill-creator/SKILL.md` line 36-40+: "Set Appropriate Degrees of Freedom" with high/medium/low levels
  - `skills/.system/skill-creator/SKILL.md` line 19-24: Lists 4 things skills provide: specialized workflows, tool integrations, domain expertise, bundled resources
  - `skills/.system/skill-creator/agents/`, `LICENSE.txt`, `references/`, `scripts/` confirm the full skill structure
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Image generation skill with dual-mode (built-in image_gen tool + CLI fallback)
- **Wiki says:** The `imagegen` system skill provides exactly two modes: the default built-in `image_gen` tool (preferred, no API key needed) and an explicit CLI fallback via `scripts/image_gen.py` (requires `OPENAI_API_KEY`). The CLI exposes three subcommands: `generate`, `edit`, `generate-batch`. Save-path policy with three-tier precedence.
- **Source evidence:**
  - `skills/.system/imagegen/SKILL.md` line 12-16: "Exactly two top-level modes": built-in `image_gen` tool and CLI fallback
  - `skills/.system/imagegen/SKILL.md` line 14: "Default built-in tool mode (preferred): built-in `image_gen` tool for normal image generation and editing. Does not require `OPENAI_API_KEY`."
  - `skills/.system/imagegen/SKILL.md` line 15: "Fallback CLI mode (explicit-only): `scripts/image_gen.py` CLI. Use only when the user explicitly asks for the CLI path. Requires `OPENAI_API_KEY`."
  - `skills/.system/imagegen/SKILL.md` line 17-21: CLI exposes three subcommands: `generate`, `edit`, `generate-batch`
  - `skills/.system/imagegen/SKILL.md` line 30-38: Save-path policy with three-tier precedence
  - `skills/.system/imagegen/scripts/`, `agents/`, `references/`, `assets/` directories confirm full skill infrastructure
  - `skills/.system/imagegen/LICENSE.txt` provides the license
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Diverse curated skills across domains (Figma, Playwright, Security, Linear, Sentry)
- **Wiki says:** The curated collection covers major development tool integrations: Figma design-to-code with 8 Figma variants, Playwright E2E testing (regular and interactive), security best practices and threat modeling, Linear issue tracking, Sentry error monitoring, Notion knowledge management, and deployment targets (Cloudflare, Netlify, Render, Vercel).
- **Source evidence:**
  - `skills/.curated/figma/SKILL.md` exists with `agents/`, `references/` for Figma integration
  - `skills/.curated/figma-code-connect-components/SKILL.md`, `figma-create-design-system-rules/`, `figma-create-new-file/`, `figma-generate-design/`, `figma-generate-library/`, `figma-implement-design/`, `figma-use/` — 8 Figma variants total
  - `skills/.curated/playwright/SKILL.md` exists with `agents/`, `assets/`, `NOTICE.txt`, `references/`, `scripts/` — full testing skill
  - `skills/.curated/playwright-interactive/SKILL.md` exists with `agents/`, `assets/`
  - `skills/.curated/security-best-practices/SKILL.md` exists with `agents/`, `references/`
  - `skills/.curated/security-threat-model/SKILL.md` exists with `agents/`, `references/`
  - `skills/.curated/security-ownership-map/SKILL.md` exists
  - `skills/.curated/linear/SKILL.md` exists with `agents/`, `assets/`
  - `skills/.curated/sentry/SKILL.md` exists with `agents/`, `assets/`
  - `skills/.curated/pdf/SKILL.md` exists with `agents/`, `assets/`
  - `skills/.curated/notion-knowledge-capture/SKILL.md` with `agents/`, `evaluations/`, `examples/`, `reference/`
  - Deployment skills: `cloudflare-deploy/`, `netlify-deploy/`, `render-deploy/`, `vercel-deploy/` all exist
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Skill installation via `$skill-installer` system command
- **Wiki says:** Codex provides `$skill-installer` as a built-in system command for installing skills. Curated skills can be installed by name (`$skill-installer gh-address-comments`). Experimental skills require the explicit folder path. Skills can also be installed from GitHub directory URLs.
- **Source evidence:**
  - `skills/.system/skill-installer/SKILL.md` implements the installer skill
  - `skills/.system/skill-installer/agents/`, `assets/`, `scripts/` confirm full infrastructure
  - `README.md` line 17: "Skills in `.system/` are automatically installed in the latest version of Codex."
  - `README.md` line 24: Curated skill install by name: `$skill-installer gh-address-comments`
  - `README.md` line 30-31: Experimental skill install with folder path
  - `README.md` line 35-37: GitHub URL-based installation: `$skill-installer install https://github.com/openai/skills/tree/main/skills/.experimental/create-plan`
  - `README.md` line 39: "After installing a skill, restart Codex to pick up new skills."
  - `skills/.system/openai-docs/SKILL.md` provides Codex documentation knowledge
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the openai-skills wiki have been verified against source code:
- ✅ Official OpenAI Codex skills repository confirmed; deprecation notice present
- ✅ 39 curated + 5 system skills confirmed from `skills/.curated/` (39 dirs) and `skills/.system/` (5 dirs)
- ✅ Skill Creator system skill confirmed with 368-line SKILL.md authoring guide
- ✅ Image generation dual-mode confirmed: built-in tool + CLI fallback with 3 subcommands
- ✅ Diverse curated skills confirmed: 8 Figma, Playwright, Security, Linear, Sentry, Notion, deployment
- ✅ `$skill-installer` system command confirmed with name-based, path-based, and URL-based installation

## Related

- [[openai-skills]] — Main wiki entry
- [[ai-marketing-claude-code-skills]] — Marketing skills for Claude Code
- [[claude-ai-music-skills]] — Creative AI skills
- [[pydantic-ai-skills]] — Python skills for AI agents

## Cross-project

- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
- [[abvx-agent-skills.codegraph-verify]] — Similar codegraph verification for ABVX Agent Skills
- [[drawio-skill.codegraph-verify]] — Similar codegraph verification for drawio-skill
- [[agentfield.codegraph-verify]] — Similar codegraph verification for AgentField
