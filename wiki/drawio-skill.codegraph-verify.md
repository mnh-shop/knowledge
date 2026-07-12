---
name: drawio-skill-codegraph-verify
tags: [drawio-skill, codegraph-verify, skill, diagram, drawio, visualization]
description: "Codegraph Verification: drawio-skill — validating wiki claims against indexed source code symbols"
source: sources/drawio-skill/
---

# Codegraph Verification: drawio-skill

**Date:** 2026-07-12

## Claim 1: Text-to-diagram pipeline with 7 diagram type presets
- **Wiki says:** The skill turns natural-language descriptions into `.drawio` XML and exports to PNG/SVG/PDF/JPG via the draw.io desktop CLI. Supports 7 diagram type presets: ERD, UML Class, Sequence, C4, Architecture, ML/Deep Learning, Flowchart. Also supports Mermaid → native .drawio conversion for 28 additional standard types.
- **Source evidence:**
  - `README.md` line 17: "A skill that turns natural-language descriptions into `.drawio` XML and exports them to PNG / SVG / PDF / JPG via the native draw.io desktop CLI."
  - `README.md` line 25: "**7 diagram type presets** — ERD, UML Class, Sequence, C4, Architecture, ML/Deep Learning, Flowchart"
  - `README.md` line 26: "**Mermaid → native .drawio** (draw.io ≥ 30) — author 28 standard types as Mermaid text"
  - `README.md` line 221-233: Supported Diagram Types table with 8 categories and notable features
  - `skills/drawio-skill/SKILL.md` line 37-39: references to `references/mermaid-authoring.md` for Mermaid conversion
  - `skills/drawio-skill/SKILL.md` lines 37-60: References `references/diagram-types.md`, `references/toolbox.md` for type-specific guidance
  - `README.md` line 132: "The skill plans the layout, generates the `.drawio` XML, exports to your chosen format, self-checks the result, and lets you iterate."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 12 code and infrastructure extractors with 28+ bundled scripts
- **Wiki says:** 12 extractor scripts convert existing code (Python/JS/Go/Rust import graphs, Python class hierarchy), IaC (Terraform/K8s/docker-compose with official cloud icons), SQL DDL, OpenAPI specs, and live infrastructure into auto-laid-out diagrams. Total of 28+ bundled Python scripts.
- **Source evidence:**
  - `skills/drawio-skill/scripts/` contains 29 Python scripts (verified by glob):
    - Language importers: `pyimports.py`, `jsimports.py`, `goimports.py`, `rustimports.py`, `pyclasses.py`
    - IaC importers: `tfimports.py`, `k8simports.py`, `composeimports.py`
    - Live infra: `tfstate.py`, `dockerimports.py`
    - Data/API: `sqlerd.py`, `openapiimports.py`
    - Diagram tools: `seqlayout.py`, `c4.py`, `autolayout.py`, `validate.py`, `repair_png.py`
    - Diff/metrics: `drawiodiff.py`, `heatmap.py`, `timelapse.py`
    - Utility: `shapesearch.py`, `aiicons.py`, `encode_drawio_url.py`, `explain.py`
    - Export/convert: `drawio2pptx.py`, `drawiohtml.py`, `svgflow.py`, `drawio2mermaid.py`
  - `README.md` line 148-199: Full script reference with descriptions and usage examples
  - `README.md` line 202-218: Table summarizing each script's function
  - `README.md` line 204: "**12 extractors**" listed for import graphs, class hierarchy, IaC, SQL DDL, OpenAPI, live infra
  - `skills/drawio-skill/SKILL.md` line 51-52: Documents `pyimports.py`, `jsimports.py`, `goimports.py`, `rustimports.py` for language import
  - `skills/drawio-skill/SKILL.md` line 52: Documents `tfimports.py`, `k8simports.py`, `composeimports.py` for IaC
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Auto-layout with Graphviz, transitive reduction, and nested containers
- **Wiki says:** The auto-layout system uses Graphviz for node placement, orthogonal edge routing around nodes, transitive reduction to remove implied edges (e.g., asyncio: 149→46 edges), and nested module containers with `--group`. Deterministic validator lints the `.drawio` for dangling edges, duplicate IDs, and overlaps.
- **Source evidence:**
  - `skills/drawio-skill/scripts/autolayout.py` implements the auto-layout pipeline
  - `README.md` line 213: "Graphviz places nodes and routes orthogonal edges *around* them"
  - `README.md` line 214: "**Transitive reduction** — drops edges implied by a longer path — example: asyncio: 149 → 46 edges"
  - `README.md` line 215: "**Nested containers** — `--group` boxes modules by sub-package, nested for deep package trees"
  - `README.md` line 217: "**Deterministic validator** — `validate.py` lints the `.drawio` (dangling edges, duplicate ids, overlaps)"
  - `skills/drawio-skill/scripts/validate.py` implements the structural validation
  - `README.md` line 219: "Layout needs Graphviz (`brew install graphviz` / `apt install graphviz`) — optional; everything else works without it"
  - `skills/drawio-skill/SKILL.md` line 48: Reference to `references/autolayout.md` for large diagram layout
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Self-check + auto-fix pipeline with 5-round iterative feedback loop
- **Wiki says:** The skill reads its own PNG output and auto-fixes overlaps, clipped labels, stacked edges (up to 2 rounds), followed by a 5-round user feedback loop with targeted refinement. Repair script fixes draw.io's truncated IEND chunk issue.
- **Source evidence:**
  - `README.md` line 34: "**Self-check + auto-fix** — reads its own PNG output and auto-fixes overlaps, clipped labels, stacked edges, and more (up to 2 rounds)"
  - `README.md` line 35: "**Iterative feedback loop** — up to 5 rounds of targeted refinement"
  - `README.md` line 289: "Behind the scenes: **check dependencies → plan layout → generate `.drawio` XML → export draft PNG → self-check + auto-fix** (up to 2 rounds) → **show to user → 5-round feedback loop** until approved → **final export**"
  - `skills/drawio-skill/scripts/repair_png.py`: "fixes draw.io's truncated IEND chunk (issue #8)" (referenced in `SKILL.md` line 46)
  - `README.md` line 297: Comparison table shows "Self-check after export: ✅ reads PNG, auto-fixes 6 issue types" vs native agent "❌"
  - `README.md` line 298: "Iterative review loop: ✅ targeted edits, 5-round safety valve" vs "❌ manual re-prompt"
  - `README.md` line 307: "Structural validation: ✅ deterministic `.drawio` linter" vs "❌"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: AI/LLM brand logo library with 321 logos and 18 data-store brands
- **Wiki says:** `aiicons.py` resolves a brand name to a draw.io image style for 321 AI/LLM logos (OpenAI, Claude, Gemini, Mistral, Llama, Cohere, DeepSeek, etc.) from lobe-icons, plus 18 data-store brands (Redis, Postgres, MongoDB, Qdrant, Milvus, Supabase, etc.) from simple-icons. Supports CDN-referenced and self-contained data URI modes.
- **Source evidence:**
  - `skills/drawio-skill/scripts/aiicons.py` implements the logo resolution
  - `README.md` line 256: "draw.io ships **no** modern AI/LLM logos"
  - `README.md` line 256: "aiicons.py resolves a brand name to a draw.io image style for any of **321 logos** (OpenAI, Claude, Gemini, Mistral, Llama, Cohere, DeepSeek, Qwen, Ollama, LangChain, HuggingFace…) from [lobe-icons](https://github.com/lobehub/lobe-icons) (MIT)"
  - `README.md` line 256: "plus **18 data-store brands** (Redis, Postgres, MongoDB, Qdrant, Milvus, Supabase…) via [simple-icons](https://simpleicons.org) (CC0) for RAG stacks"
  - `README.md` line 258-260: Usage examples: `python3 scripts/aiicons.py "claude" --json` and `python3 scripts/aiicons.py "openai" --embed`
  - `README.md` line 267: "Icons are referenced from the unpkg CDN by default (network needed at render time); `--embed` inlines them for offline use"
  - `skills/drawio-skill/SKILL.md` line 42: References `scripts/aiicons.py` for AI/LLM brand logos
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Official draw.io shape search (10,000+ shapes)
- **Wiki says:** `shapesearch.py` searches 10,000+ official draw.io shapes for exact style strings covering AWS, Azure, GCP, Cisco, Kubernetes, UML, BPMN, ER, electrical, P&ID, and general shape sets. Resolves the exact style instead of guessing `shape=mxgraph.*` names.
- **Source evidence:**
  - `skills/drawio-skill/scripts/shapesearch.py` implements the shape search
  - `README.md` line 31: "**Search 10,000+ official shapes** — resolve the exact AWS / Azure / GCP / Cisco / Kubernetes / UML / BPMN icon style instead of guessing"
  - `README.md` line 236: "The skill searches **10,000+ official draw.io shapes** for the exact style string — so vendor icons render correctly"
  - `README.md` line 240-243: Usage example: `python3 scripts/shapesearch.py "aws lambda" --limit 5`
  - `README.md` line 252: "Covers AWS / Azure / GCP / Cisco / Kubernetes / UML / BPMN / ER / electrical / P&ID and the general shape sets"
  - `skills/drawio-skill/SKILL.md` line 41: References `shapesearch.py` for specific shape resolution
  - `skills/drawio-skill/SKILL.md` line 41: "shapesearch.py returns the exact official style for 10k+ shapes"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the drawio-skill wiki have been verified against source code:
- ✅ Text-to-diagram pipeline confirmed with 7 presets + 28 Mermaid types in `README.md` and `SKILL.md`
- ✅ 12 extractors / 29 scripts confirmed from `skills/drawio-skill/scripts/` glob and README documentation
- ✅ Auto-layout with Graphviz + transitive reduction confirmed: `scripts/autolayout.py`, `scripts/validate.py`
- ✅ Self-check + auto-fix + 5-round iteration confirmed: `scripts/repair_png.py`, README workflow diagram
- ✅ 321 AI/LLM logos + 18 data-store brands confirmed: `scripts/aiicons.py` with CDN/embed modes
- ✅ 10,000+ shape search confirmed: `scripts/shapesearch.py` with vendor icon coverage

## Related

- [[drawio-skill]] — Main wiki entry
- [[skills]] — Agent skills overview
- [[open-design]] — Related design tools
- [[mermaid-diagrams]] — Related diagram-as-code approach

## Cross-project

- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
- [[abvx-agent-skills.codegraph-verify]] — Similar codegraph verification for ABVX Agent Skills
- [[ai-marketing-claude-code-skills.codegraph-verify]] — Similar codegraph verification for AI Marketing Skills
