---
name: drawio-skill-codegraph-verify
tags: [drawio-skill, codegraph-verify, skill, diagram, drawio, visualization]
description: "Codegraph Verification: drawio-skill — validating wiki claims against indexed source code symbols"
source: sources/drawio-skill/
---

# Codegraph Verification: drawio-skill

**Date:** 2026-07-12 (counts refreshed against current repo state)

## Claim 1: Text-to-diagram pipeline with 11 diagram type presets
- **Wiki says:** The skill turns natural-language descriptions into `.drawio` XML and exports to PNG/SVG/PDF/JPG via the draw.io desktop CLI, with 11 diagram type presets.
- **Source evidence:**
  - `README.md:16`: "A skill that turns natural-language descriptions into `.drawio` XML and exports them to PNG / SVG / PDF / JPG via the native draw.io desktop CLI."
  - `README.md:24`: "**11 diagram type presets** — ERD, UML Class, Sequence, C4, Architecture, ML/Deep Learning, Flowchart, SysML (BDD / IBD / Requirement / Parametric), BPMN, Network Topology, Cross-Functional Swimlane"
  - `README.md:350`: comparison table still says "✅ 7 presets (ERD, UML, Seq, C4, Arch, ML, Flow)" — confirmed stale, noted in wiki
- **Verdict:** ✅ CORRECT (wiki fixed from "6 presets" to 11)
- **Fix needed:** None

## Claim 2: 13 extractors + scripts inventory for code / IaC / SQL / OpenAPI / CI
- **Wiki says:** 13 extractor scripts convert existing code (Python/JS/Go/Rust import graphs, Python class hierarchy), IaC (Terraform/K8s/docker-compose), SQL DDL, OpenAPI specs, CI pipelines, and live infrastructure into auto-laid-out diagrams.
- **Source evidence:**
  - `README.md:249`: "**13 extractors** | import graphs for **Python · JS/TS · Go · Rust**, **Python class inheritance**, **Terraform / Kubernetes / docker-compose** resource graphs (official cloud icons), **SQL DDL → ERD**, **OpenAPI / Swagger → API diagram** … **CI pipelines → DAG** (GitHub Actions `needs:` graphs + GitLab stages)… and **live** infra from `terraform show -json` / `docker inspect` / `kubectl get -o json`"
  - `skills/drawio-skill/scripts/` contains the Python tool suite (38 `.py` files by glob) including the wiki's listed 11: `c4.py`, `aiicons.py`, `timelapse.py`, `heatmap.py`, `tubemap.py`, `pyclasses.py`, `drawio2mermaid.py`, `shapesearch.py`, `tfstate.py`, `relabel.py`, `jsimports.py` (all verified present), plus `pyimports.py`, `goimports.py`, `rustimports.py`, `tfimports.py`, `k8simports.py`, `composeimports.py`, `sqlerd.py`, `openapiimports.py`, `ciimports.py`, `dockerimports.py`, `autolayout.py`, `validate.py`, `repair_png.py`, etc.
  - `README.md:169-230` — script usage examples for every extractor
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: 5 built-in style presets + style capture
- **Wiki says:** Five built-in style presets (default, corporate, handdrawn, colorblind-safe, dark) plus capture-your-own from a `.drawio` file or image.
- **Source evidence:**
  - `skills/drawio-skill/styles/built-in/` contains exactly 5 JSON files: `default.json`, `corporate.json`, `handdrawn.json`, `colorblind-safe.json`, `dark.json` (verified by directory listing) + `schema.json`
  - `README.md:322`: "Five presets are built in — `default`, `corporate`, `handdrawn`, `colorblind-safe` (Okabe-Ito palette), `dark` — and you can teach the skill your own style from a `.drawio` file or a flat image"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Self-check + auto-fix (2 rounds) with 5-round iterative feedback loop
- **Wiki says:** The skill reads its own PNG output and auto-fixes overlaps, clipped labels, stacked edges (up to 2 rounds), followed by a 5-round user feedback loop with targeted refinement.
- **Source evidence:**
  - `README.md:33`: "**Self-check + auto-fix** — reads its own PNG output and auto-fixes overlaps, clipped labels, stacked edges, and more (up to 2 rounds)"
  - `README.md:34`: "**Iterative feedback loop** — up to 5 rounds of targeted refinement"
  - `README.md:340`: "Behind the scenes: **check dependencies → plan layout → generate `.drawio` XML → export draft PNG → self-check + auto-fix** (up to 2 rounds) → **show to user → 5-round feedback loop** until approved → **final export**."
  - `skills/drawio-skill/scripts/repair_png.py` fixes draw.io's truncated IEND chunk issue
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: AI/LLM brand logo library — 321 logos + 18 data-store brands
- **Wiki says:** `aiicons.py` resolves a brand name to a draw.io image style for 321 AI/LLM logos from lobe-icons, plus 18 data-store brands from simple-icons.
- **Source evidence:**
  - `README.md:32`: "**AI / LLM brand logos** — 321 logos (OpenAI, Claude, Gemini, Mistral, Llama, Ollama, LangChain…) … plus **18 data-store brands** (Redis, Postgres, Qdrant, Milvus…) for LLM/RAG architecture diagrams"
  - `README.md:307`: "`aiicons.py` resolves a brand name to a draw.io image style for any of **321 logos** … from [lobe-icons](https://github.com/lobehub/lobe-icons) (MIT), plus **18 data-store brands** (Redis, Postgres, MongoDB, Qdrant, Milvus, Supabase…) via [simple-icons](https://simpleicons.org) (CC0)"
  - `skills/drawio-skill/scripts/aiicons.py` implements the resolution with CDN (`--json`) and `--embed` data-URI modes
- **Verdict:** ✅ CORRECT (wiki now includes the previously omitted 18 data-store brands)
- **Fix needed:** None

## Claim 6: Official draw.io shape search (10,000+ shapes)
- **Wiki says:** `shapesearch.py` searches 10,000+ official draw.io shapes for exact style strings covering AWS, Azure, GCP, Cisco, Kubernetes, UML, BPMN, ER, electrical, P&ID, and general shape sets.
- **Source evidence:**
  - `README.md:31`: "**Search 10,000+ official shapes** — resolve the exact AWS / Azure / GCP / Cisco / Kubernetes / UML / BPMN icon style instead of guessing"
  - `README.md:287`: "The skill searches **10,000+ official draw.io shapes** for the exact style string — so vendor icons render correctly"
  - `skills/drawio-skill/scripts/shapesearch.py` implements the search; `references/shapes.md` documents the style cheatsheet
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Repository layout — scripts / references / styles / docs
- **Wiki says:** `scripts/` (11 named tools), `references/` 13 docs, `styles/` 5 built-in + schema.json, `docs/` guides.
- **Source evidence:**
  - `skills/drawio-skill/references/` contains 13 docs (verified by directory listing): autolayout, derasterize, diagram-types, live-infra, mermaid-authoring, pr-bot, shapes, style-extraction, style-presets, toolbox, troubleshooting, tubemap, xml-authoring
  - `skills/drawio-skill/styles/` = `built-in/` (5 presets) + `schema.json` (verified by listing)
  - `docs/` = 12 markdown guides (INSTALL_CLI, INSTALL_SKILL, USAGE, STYLE_PRESETS, COMPARISON, CI — each EN + CN) + `index.html`/`zh.html` (verified by listing)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Zero-config single SKILL.md, WSL2 auto-detection, MIT license
- **Wiki says:** Runs from a single SKILL.md with no MCP server / daemon, auto-detects WSL2, MIT-licensed.
- **Source evidence:**
  - `README.md:37`: "**Multi-agent, zero-config** — runs from a single SKILL.md; no MCP server, no background daemon"
  - `README.md:383`: "…all from a single SKILL.md with no MCP server."
  - `README.md:105`: "On **WSL2** the CLI is the Windows desktop exe reached via `/mnt/c` — the skill detects this automatically"
  - `README.md:26`: "**Visualize a codebase** — extract and auto-lay-out the structure of a Python / JS-TS / Go / Rust project (import graphs) or a Python class hierarchy"
  - `LICENSE:1`: "MIT License"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the drawio-skill wiki verified against source:
- ✅ 11 diagram presets confirmed (`README.md:24`; comparison table "7 presets" at :350 flagged stale)
- ✅ 13 extractors + scripts inventory confirmed (README + `scripts/` listing)
- ✅ 5 built-in style presets confirmed (`styles/built-in/` + `README.md:322`)
- ✅ Self-check 2 rounds + 5-round feedback confirmed (`README.md:33,34,340`)
- ✅ 321 AI/LLM + 18 data-store logos confirmed (`README.md:32,307`)
- ✅ 10,000+ shape search confirmed (`README.md:31,287`)
- ✅ Repo layout confirmed (references 13, styles 5+schema, docs 12 guides)
- ✅ Zero-config / WSL2 / MIT confirmed

## Related

- [[drawio-skill]] — Main wiki entry
- [[skills]] — Agent skills overview
- [[open-design]] — Related design tools
- [[mermaid-diagrams]] — Related diagram-as-code approach

## Cross-project

- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
- [[abvx-agent-skills.codegraph-verify]] — Similar codegraph verification for ABVX Agent Skills
- [[ai-marketing-claude-code-skills.codegraph-verify]] — Similar codegraph verification for AI Marketing Skills
