---
name: vault-assets-reorg-and-ideas-import
description: "Completed vault reorg (agent-profiles→profiles, agent-skills→skills) and workspace content imported into ideas/ as prototypes"
metadata:
  type: project
---

On 2026-06-27, reorganized the knowledge vault `assets/` directory and imported workspace prototypes into `ideas/`.

**Assets reorg:**
- `assets/agent-profiles/` → `assets/profiles/` (all 14 profile docs + roles/)
- `assets/agent-skills/` → `assets/skills/` (INDEX + 1 skill doc)
- Removed empty `assets/adapters/` and `assets/workflows/` directories
- Updated all wikilinks and path references in AGENTS.md, SCHEMA.md, README.md, MEMORY.md, wiki/, domains/, and assets/

**Workspace → ideas/ import:**
- `ideas/maxios-vision.md` — Full MaxiOS vision doc (1,652 lines)
- `ideas/security-boundary-pattern.md` — "Agents never on host OS" deployment rule
- `ideas/setup-factory/README.md` — Manifest-driven stack generator overview
- `ideas/setup-factory/v1-stack-architecture.md` — Security-boundary V1 stack
- `ideas/setup-factory/ROADMAP.md` — Build roadmap with phases 0-10
- `ideas/hermes-local-admin-setup.md` — Synthesized Hermes multi-profile setup guide (from 2,147-line .rtf)
- `ideas/hermes-profiles/` — 8 SOUL profile docs (local-admin, coder, planner, qa-tester, hermes-control, FCC-architect, KB-ingest, opencode-omo)
- `ideas/telegram-agent-control.md` — Deterministic Telegram-controlled stack (n8n + AgentField + Hermes)

**Why:** The vault already had a clean structure (sources/ for immutable truth, wiki/domains/ for reference). Workspace content is prototypes, not production-grade, so it went into `ideas/` per SCHEMA.md conventions. The assets reorg aligns directory names with the user's mental model ("tools/profiles/skills").

**How to apply:** All workspace-imported content has `source:` frontmatter pointing back to the original workspace files. Anything that becomes production-grade should be promoted to `domains/` or `wiki/` with verification against `sources/`.
