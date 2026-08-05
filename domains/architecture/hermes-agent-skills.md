---
name: hermes-agent-skills
tags: [architecture, hermes-agent, skills, plugin-sdk]
description: "Hermes Agent skills: 70 built-in + 111 optional SKILL.md files, 9 Skills Hub source adapters, skills tools (skills_list/skill_view/skill_manage), curator lifecycle, skill bundles"
source: sources/hermes-agent/
---

# Hermes Agent Skills

**Codegraph:** `graphs/hermes-agent`
**Source:** `sources/hermes-agent/skills/` · `sources/hermes-agent/optional-skills/` · `sources/hermes-agent/tools/skills_hub.py`

Skills are the **directory-based** extension mechanism for Hermes: each skill
is a folder containing a `SKILL.md` (frontmatter + markdown) plus optional
`references/`, `templates/`, and `scripts/`. The agent loads a skill's
content on demand through `skill_view` instead of having it in the system
prompt. This is the preferred way to add capability — priority one in the
hierarchy: extend existing → **CLI + skill** → gated tool → plugin → MCP
server → new core tool.

## Bundled skill sets

### `skills/` — 70 SKILL.md files across 14 categories

```
apple                autonomous-ai-agents   creative
email                github                 index-cache
media                mlops                  note-taking
productivity         research               smart-home
social-media         software-development
```

### `optional-skills/` — 111 SKILL.md files across 21 categories

```
autonomous-ai-agents   blockchain   communication   creative
data-science           devops       dogfood         email
finance                gaming       health          mcp
migration              mlops        payments        productivity
research               security     software-development   web-development
yuanbao
```

(22 top-level entries minus `DESCRIPTION.md` = 21 categories.) Optional
skills add: blockchain, data-science, devops, dogfood, finance, gaming,
health, mcp, payments, security, web-development, and yuanbao on top of the
built-in set.

## Skills Hub — `tools/skills_hub.py`

The hub fetches and installs skills from external sources via a `SkillSource`
ABC (skills_hub.py:474) with 9 concrete adapters:

| Adapter | Line | Source |
|---|---|---|
| `GitHubSource` | 557 | GitHub repos (skill directories or packed bundles) |
| `WellKnownSkillSource` | 1196 | Canonical well-known skills |
| `UrlSource` | 1423 | Arbitrary URLs |
| `SkillsShSource` | 1609 | skills.sh registry |
| `ClawHubSource` | 2185 | ClawHub registry |
| `LobeHubSource` | 2731 | LobeHub |
| `BrowseShSource` | 2891 | browse.sh |
| `OptionalSkillSource` | 3065 | The bundled `optional-skills/` set |
| `HermesIndexSource` | 3793 | The Hermes skills index |

## Skills tooling

### Agent tools (`tools/`)

- **`skills_tool.py`** — defines the `skills_list` tool (line 1753: "List
  available skills (name + description)") and `skill_view` (loads SKILL.md
  content plus a `linked_files` dict of references/templates/scripts; a
  second call with `file_path` returns a linked file). Plugin-provided
  skills use the qualified form `plugin:skill` (e.g. `superpowers:writing-plans`).
- **`skill_manager_tool.py`** — implements `skill_manage` (create/delete/
  update) with path-security hardening shared with `path_security.py`; it
  also drives the post-turn "should I save a memory / patch a skill"
  self-improvement review (skill_manager_tool.py:446).
- **`skill_usage.py`** — tracks skill usage/learning signal (feeds the
  curator and the learning graph).
- **`env_passthrough.py`** — when a skill is loaded via `skill_view`, its
  declared environment variables are passed through to the model.

### CLI — `hermes skills` (`hermes_cli/subcommands/skills.py`)

Subcommands: `browse`, `search`, `install`, `inspect`, `list`, `check`,
`update`, `audit`, `uninstall`, `reset`, `list-modified`, `diff`,
`opt-out`, `opt-in`.

### Slash commands (`hermes_cli/commands.py`)

- `/skills` — search, install, inspect, or manage skills
  (commands.py:245, gated by `skills.write_approval`).
- `/bundles` — list skill bundles (alias `/<name>` for multiple skills).
- `/curator` — background skill maintenance: status, run, pin, archive,
  list-archived.
- `/reload-skills` — re-scan `~/.hermes/skills/` for newly installed or
  removed skills (commands.py:288; sibling `/reload` aliases `reload_mcp`).

## Curator — skill lifecycle management

The curator maintains the installed skill set in the background:

- `agent/curator.py` — the agent-side curator logic (skill lifecycle,
  pinning, archiving).
- `hermes_cli/curator.py` — CLI-side state/status and maintenance commands
  (exposed via `hermes curator` and `/curator`).
- `tools/skill_usage.py` — usage telemetry the curator and learning graph
  consume.

### Skill bundles

`/bundles` lists named skill bundles — groups of skills addressable in one
command (`/bundles` then `/<name>` loads several skills at once). Bundle
resolution is pluggable via `skill_bundles_provider` (commands.py:1417,
`_iter_skill_bundles` at 1443).

## Related

- [[hermes-agent-architecture]] -- Overall architecture; skills as the directory-based edge subsystem
- [[hermes-agent-cli]] -- `hermes skills` CLI + `/skills`, `/reload-skills`, `/bundles`, `/curator`
- [[hermes-agent-plugins]] -- Plugins can also provide skills (`plugin:skill` qualified names)
- [[hermes-agent-memory]] -- Curator/skill-usage feed the learning graph alongside memory chunks

## Links

- Built-in: `sources/hermes-agent/skills/`
- Optional: `sources/hermes-agent/optional-skills/`
- Hub: `sources/hermes-agent/tools/skills_hub.py`
- Agent tools: `sources/hermes-agent/tools/skills_tool.py`, `skill_manager_tool.py`, `skill_usage.py`
- Curator: `sources/hermes-agent/agent/curator.py`, `hermes_cli/curator.py`
- CLI: `sources/hermes-agent/hermes_cli/subcommands/skills.py`
