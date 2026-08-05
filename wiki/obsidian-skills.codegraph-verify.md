---
name: obsidian-skills-codegraph-verify
tags: [obsidian-skills, codegraph-verify, obsidian, note-taking]
description: "Codegraph Verification: obsidian-skills — validating wiki claims against indexed source code symbols"
source: sources/obsidian-skills/
---

# Codegraph Verification: obsidian-skills

**Date:** 2026-07-12

## Claim 1: Agent Skills for Obsidian following the Agent Skills specification
- **Wiki says:** Agent Skills for use with Obsidian that follow the [Agent Skills specification](https://agentskills.io/specification). Compatible with Claude Code, Codex, and OpenCode.
- **Source evidence:**
  - `README.md` line 1: "Agent Skills for use with Obsidian."
  - `README.md` line 3: "These skills follow the [Agent Skills specification](https://agentskills.io/specification) so they can be used by any skills-compatible agent, including Claude Code, Codex, and Open Code."
  - Each skill directory contains a `SKILL.md` file with YAML frontmatter (name, description) — matching the Agent Skills specification format
  - `README.md` lines 7-46 document installation methods for all three platforms
  - `README.md` lines 28-46: Specific installation instructions for Claude Code, Codex, and OpenCode
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 5 skills covering Obsidian-specific operations
- **Wiki says:** Ships 5 skills: obsidian-markdown (Obsidian Flavored Markdown), obsidian-bases (.base database-like views), json-canvas (.canvas files), obsidian-cli (Obsidian CLI/plugin dev), defuddle (web page → clean markdown extraction).
- **Source evidence:**
  - `README.md` lines 50-56: Table listing all 5 skills with descriptions
  - `skills/obsidian-markdown/SKILL.md` exists — covers wikilinks, embeds, callouts, properties, tags, comments, math (LaTeX), diagrams (Mermaid)
  - `skills/obsidian-markdown/SKILL.md` line 3 (description): mentions tags in the activation triggers; lines 103 (tags syntax), 105 (## Comments), 121 (## Math (LaTeX)), 132 (## Diagrams (Mermaid)) document the additional syntax coverage
  - `skills/obsidian-bases/SKILL.md` exists — covers .base files with views, filters, formulas, summaries
  - `skills/json-canvas/SKILL.md` exists — covers JSON Canvas files with nodes, edges, groups, connections
  - `skills/obsidian-cli/SKILL.md` exists — covers Obsidian CLI for plugin/theme development
  - `skills/defuddle/SKILL.md` exists — covers clean markdown extraction from web pages using Defuddle
  - `skills/obsidian-cli/SKILL.md` explicitly covers "plugin and theme development"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Multi-platform installation (marketplace, npx skills, manual)
- **Wiki says:** Available via marketplace (`/plugin marketplace add kepano/obsidian-skills`), npx skills, or manual clone. OpenCode auto-discovers skills without config changes.
- **Source evidence:**
  - `README.md` lines 7-13: Marketplace install via `/plugin marketplace add kepano/obsidian-skills` and `/plugin install obsidian@obsidian-skills`
  - `README.md` lines 15-24: npx skills install via `npx skills add git@github.com:kepano/obsidian-skills.git` (ssh) or `npx skills add https://github.com/kepano/obsidian-skills` (https)
  - `README.md` lines 27-46: Manual install for Claude Code (`.claude` folder), Codex (`~/.codex/skills`), OpenCode (`~/.opencode/skills/obsidian-skills`)
  - `README.md` lines 44-46: "OpenCode auto-discovers all SKILL.md files under ~/.opencode/skills/. No changes to opencode.json or any config file are needed."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Skills include detailed reference documentation
- **Wiki says:** Skills include reference files for callouts, properties, embeds, and functions that provide complete syntax coverage beyond the SKILL.md itself.
- **Source evidence:**
  - `skills/obsidian-markdown/references/CALLOUTS.md` exists
  - `skills/obsidian-markdown/references/PROPERTIES.md` exists
  - `skills/obsidian-markdown/references/EMBEDS.md` exists
  - `skills/obsidian-bases/references/FUNCTIONS_REFERENCE.md` exists
  - `skills/json-canvas/references/EXAMPLES.md` exists
  - `skills/obsidian-bases/SKILL.md` references external documentation: `README.md` lines 493-498: "References" section links to official Obsidian help for Bases Syntax, Functions, Views, Formulas
  - `skills/obsidian-markdown/SKILL.md` lines 192-196: References section links to official Obsidian docs for flavored markdown, links, embeds, callouts, properties
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Created by kepano (Obsidian CEO)
- **Wiki says:** Repository is maintained by kepano.
- **Source evidence:**
  - `README.md` line 11: `/plugin marketplace add kepano/obsidian-skills` — references kepano's GitHub
  - Repository URL: `https://github.com/kepano/obsidian-skills` (kepano is the GitHub handle of the Obsidian CEO)
  - `skills/defuddle/SKILL.md` references Defuddle at `https://github.com/kepano/defuddle` — same author
  - `README.md` describes the skill set as "Agent Skills for use with Obsidian" — aligned with Obsidian's official ecosystem
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 5 key claims from the obsidian-skills wiki have been verified against the source code:
- ✅ Agent Skills spec format: SKILL.md with YAML frontmatter confirmed for all skills
- ✅ 5 skills: obsidian-markdown, obsidian-bases, json-canvas, obsidian-cli, defuddle all present
- ✅ Multi-platform install: Marketplace, npx, and manual methods documented for all 3 platforms
- ✅ Reference documentation: Callouts, properties, embeds, functions reference files present
- ✅ Created by kepano: GitHub handle confirmed as repository owner and Obsidian CEO

## Related

- [[obsidian-skills]] -- Main wiki entry
- [[skills]] -- Agent skills catalog
- [[hermes-agent]] -- Hermes agent platform
- [[openclaw]] -- OpenClaw agent platform

## Cross-project

- [[skills.codegraph-verify]] -- Skills catalog codegraph verification
- [[hermes-agent.codegraph-verify]] -- Hermes agent codegraph verification
- [[openclaw.codegraph-verify]] -- OpenClaw codegraph verification
