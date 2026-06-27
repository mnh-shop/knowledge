---
name: schema
description: "Vault conventions, tag taxonomy, directory structure, and update policies for the knowledge base"
tags: [index, reference]
---

# Vault Schema

> Codified conventions for the AI agent infrastructure knowledge base.
> Agents MUST read this before creating or modifying any page in the vault.

## Domain

This vault covers **AI agent infrastructure** — the software stack for building, deploying, and orchestrating autonomous AI agents. It tracks 70+ open-source repos (sources), 77 wiki entries, 125 domain deep-dive docs, and reference deployment stacks.

It is a **curated, evidence-grounded reference** — not a general note vault, not a scratchpad. All claims should be traceable to source repos or verified documentation.

## Directory Structure

```
knowledge/
├── SCHEMA.md              # ← THIS FILE — structure, conventions, taxonomy
├── AGENTS.md              # Agent instructions for working with the vault
├── MEMORY.md              # Index, coverage status, cross-repo compatibility
├── sources/               # Layer 1: Git clones / archived source repos (immutable)
│   ├── hermes-agent/      #   One directory per repo
│   ├── n8n/
│   └── ...                #   70 source repos total
├── wiki/                  # Layer 2: Wiki entry per repo (one markdown page each)
│   ├── hermes-agent.md
│   ├── n8n.md
│   └── ...                #   77 wiki pages
├── domains/               # Layer 2: Deep-dive docs by dimension
│   ├── architecture/      #   System design, component relationships, data flow
│   ├── api/               #   REST / HTTP API references
│   ├── mcp/               #   MCP server implementations
│   ├── acp/               #   Agent Communication Protocol implementations
│   ├── deployment/        #   Deployment and operations guides
│   └── integration-patterns/  # Cross-system integration stacks
├── graphs/                # Layer 2: AgentField code graph run data
├── raw/                   # Layer 1: AgentField AG metadata XML (immutable)
├── assets/                # Layer 3: Reference templates and artifacts
│   ├── profiles/
│   ├── skills/
│   ├── mcp-servers/
│   ├── acp-agents/
│   ├── api-clients/
│   └── deployment/
├── integrations/          # (reserved)
└── ideas/                 # Brainstorming space — NOT source truth
    └── (ignored by default — read/write only when user asks for idea work)
```

### Layer roles

| Layer | What | Who modifies | Source of truth |
|---|---|---|---|
| **Layer 1** | `sources/`, `raw/` | Git pull / ingestion only | Immutable — the actual code/config |
| **Layer 2** | `wiki/`, `domains/`, `graphs/` | Agent maintains | Derived from Layer 1 |
| **Layer 3** | `assets/`, `SCHEMA.md`, `MEMORY.md` | Curated by user + agent | Reference templates and conventions |

## Conventions

### File naming
- Lowercase, hyphens, no spaces: `agentfield-architecture.md`, `hermes-mcp-implementation.md`
- Page name matches repo name where possible: `hermes-agent.md` describes the `hermes-agent` repo
- Domain docs follow `<entity>-<dimension>.md`: `n8n-deployment.md`, `openclaw-mcp-implementation.md`

### Frontmatter (every page)
Every wiki and domain document MUST start with YAML frontmatter:

```yaml
---
name: page-slug           # lowercase-hyphenated, matches filename without .md
tags: [tag1, tag2]        # only tags from the taxonomy below; repo-name tag always included
description: "One-line summary"  # short enough for INDEX listings
source: sources/repo-name/       # wiki entries only — points to the source repo directory
---
```

For domain docs, omit `source:` — instead include the repo name as a tag and link to the corresponding wiki entry.

### Wikilinks
- Use `[[page-name]]` to link between wiki entries and domain docs
- Every page should have at least 2 outbound wikilinks to related pages
- Cross-reference from wiki entries to domain docs and vice versa

### Provenance
- Every wiki entry has a `source:` field pointing to the relevant `sources/<repo>/` directory
- Source code in `sources/` is authoritative — if a wiki page contradicts the source code, the source wins
- Claims about architecture, APIs, and configuration should be verifiable against the source
- For pages synthesizing 3+ sources, provenance markers `^[sources/repo/file]` may be appended at the paragraph level

## Tag Taxonomy

Tags fall into three categories: **ecosystem** (repo names), **language**, and **classification**.

### Ecosystem tags (repo / project names)

Every source repo directory name is a valid ecosystem tag. Always include the repo's own name tag on its pages.

```
1claw-hermes, AionUi, ECC, Hermes-caduceus, Mnemosyne, OpenViking,
SWE-AF, abvx-agent-skills, af-deep-research, af-reactive-atlas-mongodb,
agent-rules-books, agentfield, agentfield.codegraph-verify, alphaclaw,
awesome-n8n-templates, awesome-openclaw-skills, awesome-openclaw-usecases,
bootc, buildah, camofox-browser, clawpier, cockpit, cockpit-podman,
crun-vm, drawio-skill, ecc, fedora-coreos-config, free-claude-code, goclaw,
gogs, graphify, hermes-agent, hermes-agent-acp-skill, hermes-agent-docker,
hermes-agent-template, hermes-autonomous-server, hermes-bus,
hermes-incident-commander, hermes-optimization-guide, hermes-plugins,
hermes-startup-architect, hermes-suite, hermes-workspace, hermzner, llmtrim,
materia, mission-control, n8n, n8n-mcp, n8n-nodes, n8n-skills,
n8n-workflow-catalog, n8n-workflows, nanobot, nix-podman-stacks, nix.dev,
obsidian-skills, oh-my-hermes, oh-my-openagent, oh-my-opencode-slim, oh-my-pi,
open-design, openclaw, openclaw-container, openclaw-plugin-claude-code,
openclaw.codegraph-verify, opencode, opencode-hermes-multiagent, openviking,
outreachmagic, pi, podlet, podman, podman-compose, podman.codegraph-verify,
pydantic-ai-skills, quadlet, sablier, sec-af, skills, tank-os, zot
```

## Domain-dimension tags

Used on domain docs and INDEX files to indicate which dimension of analysis:

- `acp` — Agent Communication Protocol docs
- `api` — REST/HTTP API docs
- `architecture` — System design docs
- `deployment` — Deployment guides
- `integration-patterns` — Cross-system integration docs
- `mcp` — Model Context Protocol docs
- `catalog` — INDEX files and catalogs
- `index` — INDEX files and listings

### Language tags

Based on actual file counts. Include only languages that make up a meaningful portion of the codebase (>20 files or >10% of code):

- `python` — Python repos
- `typescript` — TypeScript repos (includes TS/JS for Obsidian)
- `golang` — Go repos
- `rust` — Rust repos
- `javascript` — JavaScript repos
- `nix` — Nix / NixOS repos

### Classification tags

General purpose — describe what the project IS or DOES:

`agent`, `agent-gateway`, `agent-manager`, `agent-profile`, `agent-runtime`,
`ai-agents`, `ai-llm`, `ansible`, `anthropic`, `auditor`, `automation`, `bootc`,
`browser-automation`, `cli`, `claude-code`, `code-assistant`, `coding-agent`,
`container`, `control-plane`, `dashboard`, `daemonless`, `declarative`, `deep-research`,
`deployment`, `desktop`, `design`, `design-system`, `developer-tools`, `docker`,
`documentation`, `electron`, `engineering-factory`, `event-bus`, `fair-code`, `gateway`,
`fedora`, `git`, `gui`, `harness`, `hetzner`, `home-manager`, `identity`,
`image-builder`, `image-based`, `immutable-os`, `infrastructure-as-code`,
`integration`, `landscape`, `linux`, `live-canvas`, `low-code`, `mcp`,
`messaging`, `monitoring`, `multi-agent`, `multi-platform`, `multi-provider`,
`nextjs`, `notifications`, `oci`, `oci-runtime`, `open-source`, `optimization`,
`orchestration`, `packaging`, `personal-assistant`, `planning`, `plugin`,
`plugin-sdk`, `profile`, `protocol`, `proxy`, `qemu`, `quadlet`, `react`,
`recursive-agents`, `reference`, `research`, `rest-api`, `reverse-proxy`,
`rootless`, `scaling`, `scale-to-zero`, `security`, `self-hosted`,
`self-hosted-stacks`, `shared`, `skill`, `skills-platform`, `sqlite`, `ssh`,
`storage`, `systemd`, `tauri`, `telegram`, `templates`, `terraform`,
`tool-calling`, `ui`, `version-control`, `virtualization`, `vm`, `vps`, `vue`,
`webhook`, `wiki`, `workflow-automation`, `workflows`

### Tag rules
1. Every page MUST include its own repo name as a tag (e.g., `podman` on podman.md)
2. Ecosystem tags are preferred over classification tags where both fit
3. Do NOT add redundant per-repo tags (e.g., `agentfield-architecture`) — use the standard ecosystem tag
4. Do NOT add single-use, overly specific tags like `cron`, `loom`, `atlas-triggers` — prefer broader classification
5. When in doubt, fewer tags is better than more

## Page Thresholds

### When to create a wiki page
- One wiki page per source repo (matched by `source:` field)
- Exception: auxiliary collections (awesome-* lists, template repos) may share a page or be grouped under their primary ecosystem
- Do NOT create standalone pages for one-off concepts — use a domain doc or fold into an existing wiki entry

### When to create a domain doc
- The repo has architecture worth a deep dive (beyond what fits in the wiki entry)
- The repo exposes an API, MCP server, or ACP agent
- The repo has deployment instructions with enough nuance to warrant a dedicated guide
- Not every repo needs all 6 domain dimensions — only fill what's useful

### When to update vs split
- **Update** an existing page when new information extends it
- **Split** when any page exceeds ~200 lines — break the domain dimension into `domains/<dimension>/<name>-<dimension>.md`
- **Archive** when a repo is deprecated or fully superseded — move to `_archive/` and remove from INDEX

## Update Policy

1. **Source code wins.** If a wiki page contradicts what's in `sources/<repo>/`, correct the wiki to match the source.
2. **Date-stamp changes.** Update `updated` date (if frontmatter has one) or note the change in log.md.
3. **Cross-reference.** Every update should check for broken or missing `[[wikilinks]]` and add them where the topic relates to other pages.
4. **Update MEMORY.md.** If a repo is added or removed, update the wiki entries list and cross-repo compatibility table in MEMORY.md.
5. **Tag hygiene.** When updating, check that tags still reflect the repo — remove stale tags, add new ones from the taxonomy, prune noise.

## Linting

On request ("audit", "health check", "lint the vault"):

1. Check every wiki page has a valid `source:` field
2. Check every tag is in the taxonomy above
3. Find wiki pages with no `[[wikilinks]]` to other pages
4. Find domain docs with missing INDEX.md entries
5. Surface `confidence: low` and `contested: true` pages for review
6. Check for broken source paths (`sources/<name>/` directories that don't exist)

## Related

- [MEMORY.md](MEMORY.md) — Current index, coverage status, cross-repo compatibility
- [AGENTS.md](AGENTS.md) — Agent-level instructions for working with this vault
- [Obsidian graph](.obsidian/graph.json) — Visual tag groups and colors
