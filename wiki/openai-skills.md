---
name: openai-skills
tags: [openai-skills, openai, codex, agent, skill, deprecated, catalog]
description: "Deprecated static catalog of Agent Skills for Codex — 5 system + 39 curated SKILL.md folders installed via $skill-installer; superseded by the OpenAI Plugins repository"
source: sources/openai-skills/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# OpenAI Skills (Agent Skills catalog)

> [!IMPORTANT]
> **This repository is deprecated.** For current Codex skill and plugin examples, use the [OpenAI Plugins repository](https://github.com/openai/plugins). To add your own skills to Codex, follow the [Build plugins](https://developers.openai.com/codex/plugins/build) guide, which includes instructions for creating a skill-only plugin. (`README.md:1-2`)

## Metadata

| Field | Value |
|---|---|
| Repository | `openai/skills` |
| Status | **Deprecated** (superseded by `openai/plugins`) |
| Type | Static catalog of Agent Skills (Markdown + optional scripts/resources) |
| Content | 5 system skills, 39 curated skills (`.experimental/` tier documented but absent from snapshot) |
| Install mechanism | `$skill-installer` inside Codex (by name, by path, or by GitHub URL) |
| License | No top-level license — each skill ships its own `LICENSE.txt` |
| Language | No application code — plain Markdown/YAML content |
| Docs | [Using skills in Codex](https://developers.openai.com/codex/skills) · [Create custom skills](https://developers.openai.com/codex/skills/create-skill) · [Agent Skills open standard](https://agentskills.io) |

## What is it?

A deprecated, static catalog of **Agent Skills** for OpenAI Codex. Agent Skills are folders of instructions, scripts, and resources that AI agents can discover and use to perform specific tasks — "write once, use everywhere" (`README.md:4-6`). The repository contains **no application code**: no CLI, no REST API, no web UI, and no installer implementation of its own. It is purely a curated set of skill directories plus a 43-line README describing how Codex consumes them (`README.md:8`).

The repo is organized into three documented tiers, of which two are present in the checked-out snapshot:

| Tier | Directory | Contents in snapshot |
|---|---|---|
| System | `skills/.system/` | 5 skills, auto-installed in the latest Codex (`README.md:17`) |
| Curated | `skills/.curated/` | 39 skills, installable by name (`README.md:21-25`) |
| Experimental | `skills/.experimental/` | Documented in README (`README.md:19,27-31,36`) but **absent from the cloned snapshot** — referenced via the `create-plan` examples |

## Key features

- **Deprecation notice is the headline** — the very first lines redirect readers to the [OpenAI Plugins repository](https://github.com/openai/plugins) and the [Build plugins](https://developers.openai.com/codex/plugins/build) guide (`README.md:1-2`)
- **5 system skills** (`skills/.system/`): `imagegen`, `openai-docs`, `plugin-creator`, `skill-creator` (368-line authoring guide), `skill-installer` — bundled automatically with Codex
- **39 curated skills** (`skills/.curated/`) covering:
  - **Design/Figma (8):** `figma`, `figma-code-connect-components`, `figma-create-design-system-rules`, `figma-create-new-file`, `figma-generate-design`, `figma-generate-library`, `figma-implement-design`, `figma-use`
  - **Testing (2):** `playwright`, `playwright-interactive`
  - **Notion (4):** `notion-knowledge-capture`, `notion-meeting-intelligence`, `notion-research-documentation`, `notion-spec-to-implementation`
  - **Security (3):** `security-best-practices`, `security-ownership-map`, `security-threat-model`
  - **Deployment (4):** `cloudflare-deploy`, `netlify-deploy`, `render-deploy`, `vercel-deploy`
  - **GitHub (2):** `gh-address-comments`, `gh-fix-ci`
  - **Other (16):** `aspnet-core`, `chatgpt-apps`, `cli-creator`, `define-goal`, `hatch-pet`, `jupyter-notebook`, `linear`, `migrate-to-codex`, `openai-docs`, `pdf`, `screenshot`, `sentry`, `speech`, `transcribe`, `winui-app`, `yeet`
- **Standard skill frontmatter:** each `SKILL.md` opens with YAML `name` + `description` (optionally a `metadata` block) — e.g. `skills/.curated/figma/SKILL.md:1-4` and `skills/.system/skill-creator/SKILL.md:1-6`
- **`$skill-installer` command:** skills are installed from inside Codex by name, by folder path, or by GitHub directory URL
- **Per-skill licensing:** each skill directory carries its own `LICENSE.txt`; there is no repository-level license file (`README.md:41-43`)
- **Contributing values:** community norms (Contributor Covenant, kind and inclusive, teach & learn) and a security contact at `security@openai.com` (`contributing.md`)

## Tech stack

- **No application code.** Repository root contains only `README.md`, `contributing.md`, `.gitignore`, and `skills/`
- **Content format:** Markdown skill definitions (`SKILL.md`) with YAML frontmatter
- **Optional skill payloads:** per-skill subdirectories such as `agents/`, `assets/`, `references/`, `scripts/`, `evaluations/`, `examples/` (e.g. `cloudflare-deploy/references/` holds ~70 reference docs; `playwright/` includes `scripts/` and `NOTICE.txt`)
- **Standard:** follows the [Agent Skills open standard](https://agentskills.io) (`README.md:13`)
- **No API, no service, no build step** — skills are consumed directly by the Codex agent runtime

## Deployment / Usage

### System skills

Skills in `skills/.system/` are installed automatically in the latest version of Codex (`README.md:17`).

### Curated skills — install by name

Curated skills can be installed by name (defaults to `skills/.curated`) (`README.md:21-25`):

```
$skill-installer gh-address-comments
```

### Experimental skills — install by path

For experimental skills, specify the skill folder (`README.md:27-31`):

```
$skill-installer install the create-plan skill from the .experimental folder
```

### Any skill — install by GitHub URL

Or provide the GitHub directory URL (`README.md:33-37`):

```
$skill-installer install https://github.com/openai/skills/tree/main/skills/.experimental/create-plan
```

After installing a skill, **restart Codex** to pick up new skills (`README.md:39`).

## Notes

- The `.experimental/` tier and the `create-plan` skill are documented in the README's install examples but **do not exist in the checked-out snapshot** — only `skills/.system/` and `skills/.curated/` are present on disk.
- Because the repository is deprecated, new skill/plugin work should target [openai/plugins](https://github.com/openai/plugins) instead of this repo.

## Related

- [[skills]] — Agent skills platform and registry
- [[Anthropic-Cybersecurity-Skills]] — 817-skill cybersecurity library following the agentskills.io standard
- [[abvx-agent-skills]] — Auditable skillpack for coding agents
- [[claude-skills-journalism]] — Journalism-focused Claude Code skills
- [[ai-marketing-claude-code-skills]] — Marketing skills for Claude Code
