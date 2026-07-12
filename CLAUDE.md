# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **knowledge vault** for AI agent infrastructure — curated documentation of 115 open-source repos covering MCP, ACP, agent frameworks, deployment patterns, and system integrations. It follows a **3-layer architecture**:

- **Layer 1** (`sources/`, `raw/`): Git clones / archived source repos (immutable)
- **Layer 2** (`wiki/`, `domains/`, `graphs/`): Derived documentation (editable)
- **Layer 3** (`assets/`, `SCHEMA.md`, `MEMORY.md`): Reference templates and conventions (editable)

The focus is **Hermes, OpenClaw, AgentField, Podman, n8n, and surrounding ecosystem** — 115 source repositories (cloned and indexed) across 6 functional layers.

## Key Tools and Access Patterns

### CodeGraph Verification (Recommended First Step)

**Always use CodeGraph to verify claims against source repos first:**

```bash
# From the sources directory
codegraph explore "function_name" -p "sources/<repo-name>"

# Or from graphs directory (faster indexes)
codegraph explore "function_name" -p "graphs/<repo-name>"
```

**MCP tool equivalent:**
```json
{
  "tool": "codegraph_explore",
  "projectPath": "sources/<repo-name>",
  "query": "find_function_or_class_or_route"
}
```

**Rule:** Read the wiki page first, then use CodeGraph for specifics. The source code in `sources/` is always authoritative.

### Validation Commands

These commands help maintain vault integrity:

```bash
# Validate all wikilinks resolve to existing files
bash tests/validate-wikilinks.sh

# Validate markdown quality (frontmatter, fences, file sizes)
bash tests/validate-markdown.sh
```

### Project Skills

The vault includes specialized skills for different areas:

- `graphify` - Any input to knowledge graph (use when user requests `/graphify`)
- `codebase-design` - Deep module interface design
- `codebase-memory` - Query knowledge graph for code structure
- `domain-modeling` - Build/verification domain models
- `repo-wiki` - Build wiki from repositories
- `tdd` - Test-driven development
- `verify` - End-to-end verification of changes
- `code-review` - Review current diff for bugs and improvements
- `claude-api` - Claude API reference (use for LLM questions)

## Architecture Guidelines

### Layered Structure Navigation

**To understand system architecture:**

1. **Start with the wiki** (`wiki/<repo>.md`) for high-level overviews
2. **Check source** (`sources/<repo>/`) for actual code 
3. **Use CodeGraph** to trace call chains and dependencies
4. **Consult domains/** for deep-dive analysis (architecture, APIs, deployment, etc.)
5. **Review assets/** for reusable templates and patterns

### Integration Patterns

When documenting connections between systems:

1. **Identify interfaces** — MCP, REST API, CLI, webhooks, event bus
2. **Check compatibility** with core platforms:
   - Hermes (agent platform)
   - OpenClaw (Rust agent platform)  
   - AgentField (firecracker VMs)
   - n8n (workflow automation)
3. **Seed `domains/integration-patterns/`** with cross-references

## File Conventions

### Wiki Pages (`wiki/`)<file_path>
- One page per source repo (matched by `source:` field in frontmatter)
- Must include: `name`, `tags`, `description`, `source`
- Tag taxonomy: ecosystem (repo name), language, classification
- Include at least 2 outbound wikilinks to related pages
- Max ~200 lines — split into domains docs if longer

### Domain Docs (`domains/`)<file_path>
- Deep-dive on specific dimension: `architecture`, `api`, `mcp`, `acp`, `deployment`, `integration-patterns`
- File format: `<entity>-<dimension>.md`
- No `source:` field — include repo name as tag instead
- One INDEX.md per directory mapping

### Naming Conventions
- File names: `lowercase-hyphenated.md`
- Page name matches repo name: `hermes-agent.md` describes `hermes-agent` repo
- Domain docs follow `<name>-<dimension>.md`: `n8n-deployment.md`, `openclaw-mcp-implementation.md`

## Development Workflow

### Common Commands and Tasks

#### 1. Understanding a Repository

```bash
# Get quick overview of a repo's architecture
read knowledge/wiki/<repo-name>.md

# Deep dive into specific components using CodeGraph
codegraph explore "class_name" -p "sources/<repo-name>"

# Find callers/callees for key functions
codegraph trace "function_name" -p "sources/<repo-name>"
```

#### 2. Making Changes

**Wiki/Entry Updates:**
- Edit wiki pages with insights from source code
- Always verify claims against source using CodeGraph
- Ensure proper wikilinks to related pages
- Run validation: `bash tests/validate-wikilinks.sh`

**Domain Docs:**
- Add deep-dive analysis for APIs, architectures, deployment
- Cross-reference between wiki and domain docs
- Use INDEX.md files for discovery

#### 3. Repository Analysis

```bash
# Extract skills and capabilities
python3 tests/add-capability-tags.py --dry-run

# Build/rebuild wiki from sources (if needed)
<command to generate wiki from sources>
```

#### 4. Integration Documentation

```bash
# Find how systems interconnect
codegraph explore "mcp_server" -p "sources/hermes-agent"
codegraph explore "handler" -p "sources/openclaw"
```

Create `domains/integration-patterns/<name>-integration.md` for each new pattern.

### Validation Before Edits

Always verify:
1. Source repo exists in `sources/` before referencing it
2. Tags are in `SCHEMA.md` taxonomy
3. Wikilinks resolve (`bash tests/validate-wikilinks.sh`)
4. Frontmatter has `name` and `description`

## Default Permissions

The project has configured permissions for common vault operations:

- Reading markdown files and sources
- Running validation scripts
- Using CodeGraph tools
- Writing to vault directories (`wiki/`, `domains/`, etc.)

All changes should respect the Layer rules — never modify `sources/` or `raw/` directly.

## References

### Primary Documents

- **`AGENTS.md`** — Agent principles and structure rules
- **`SCHEMA.md`** — Complete file conventions, tag taxonomy, update policies
- **`MEMORY.md`** — Repository index, coverage status, compatibility matrix

### Validation Scripts

- **`tests/validate-wikilinks.sh`** — Check all [[wikilinks]] resolve
- **`tests/validate-markdown.sh`** — Check fences, sizes, frontmatter completeness
- **`tests/add-capability-tags.py`** — Preview skill/capability tags

## Content Types in the Vault

The knowledge vault includes:

| Type | Location | Purpose |
|------|----------|---------|
| **Repository wikis** | `wiki/` | 98 wiki entries for 115 source repos |
| **Domain knowledge** | `domains/` | Cross-repo concept docs (6 dimensions) |
| **Integration patterns** | `domains/integration-patterns/` | How systems connect |
| **Reusable assets** | `assets/` | Skills, workflows, profiles, deployment configs |
| **Deployment configs** | `assets/deployment/` | Quadlet configs, infra templates |
| **Reference docs** | `assets/mcp-servers/`, etc. | API clients, agent profiles |
| **Temporary work** | `memory/` | Session memory system |
| **Brainstorming** | `ideas/` | When requested |

The vault is designed for **AI agent infrastructure** — understanding, modifying, and extending this ecosystem of autonomous agents.