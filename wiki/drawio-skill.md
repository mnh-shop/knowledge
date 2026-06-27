---
name: drawio-skill
title: drawio-skill
lastmod: 2026-06-25
description: A skill that turns natural-language descriptions into .drawio XML and exports to PNG/SVG/PDF/JPG via the native draw.io desktop CLI
source: sources/drawio-skill/
tags: [plugin, python]
icon: 📐
---

# drawio-skill — From Text to Professional Diagrams

**A skill that turns natural-language descriptions into `.drawio` XML and exports them to PNG / SVG / PDF / JPG via the native draw.io desktop CLI.** It can also turn an existing codebase (Python / JS-TS / Go / Rust) into an auto-laid-out structure diagram. 

## Key Features

- **6 diagram type presets** — ERD, UML Class, Sequence, Architecture, ML/Deep Learning, Flowchart
- **Visualize existing codebases** — extract and auto-lay-out the structure of Python / JS-TS / Go / Rust projects (import graphs) or a Python class hierarchy
- **Search 10,000+ official shapes** — resolve exact AWS / Azure / GCP / Cisco / Kubernetes / UML / BPMN icon styles instead of guessing
- **AI / LLM brand logos** — 321 logos (OpenAI, Claude, Gemini, Mistral, Llama, Ollama, LangChain...) for LLM-app architecture diagrams
- **Self-check + auto-fix** — reads PNG output and auto-fixes overlaps, clipped labels, stacked edges (up to 2 rounds)
- **Iterative feedback loop** — up to 5 rounds of targeted refinement
- **Style presets** — capture visual style from a `.drawio` file or image
- **Clean layout** — grid-aligned, spacing scales with diagram size, connectors routed clear of nodes
- **Multi-agent, zero-config** — runs from a single SKILL.md; no MCP server, no background daemon

## Quick Start

After installation, just describe what you want:

```
Draw a Transformer encoder-decoder for machine translation: 6-layer encoder with self-attention, 6-layer decoder with cross-attention, input embeddings (batch × 512 × 768), positional encoding, and a final output projection. Annotate tensor shapes between layers and color-code by layer type.
```

The skill plans the layout, generates the `.drawio` XML, exports to your chosen format, self-checks the result, and lets you iterate.

## When to Use

**Good fit:**
- Polished, precise diagrams — stakeholder decks, architecture, network topology, strict UML, ER diagrams
- Solid opaque fills, 10,000+ official shapes, branded icons (AWS / Azure / GCP / Cisco / Kubernetes + AI/LLM logos), swimlanes, and custom geometry
- Anything you'll export to PNG / SVG / PDF and keep editable

**Try a sibling skill instead when you need:**
- **A casual, hand-drawn / whiteboard look** → [excalidraw-skill](https://github.com/Agents365-ai/excalidraw-skill) or [tldraw-skill](https://github.com/Agents365-ai/tldraw-skill)
- **Diagrams-as-code that live in git and render in Markdown** → [mermaid-skill](https://github.com/Agents365-ai/mermaid-skill) (general) or [plantuml-skill](https://github.com/Agents365-ai/plantuml-skill) (UML)
- **Freeform infinite-canvas sketching / freehand strokes** → [tldraw-skill](https://github.com/Agents365-ai/tldraw-skill)

## Related

- [[skills]] — Agent skills platform
- [[hermes-agent]] — Compatible agent runtime for skills

## Related Skills

Part of the Agents365-ai diagram-skill family:

| Skill | Style | Best for |
|---|---|---|
| [excalidraw-skill](https://github.com/Agents365-ai/excalidraw-skill) | Hand-drawn / sketchy | Whiteboard mockups, informal diagrams |
| [mermaid-skill](https://github.com/Agents365-ai/mermaid-skill) | Text-based, auto-layout | README-embeddable, version-control friendly |
| [plantuml-skill](https://github.com/Agents365-ai/plantuml-skill) | UML-focused | Class / sequence diagrams in CI pipelines |
| [tldraw-skill](https://github.com/Agents365-ai/tldraw-skill) | Whiteboard collaboration | Casual sketches, FigJam-style boards |

## Installation

### 1. Install the draw.io desktop CLI

| Platform | Command |
|----------|---------|
| **macOS** | `brew install --cask drawio` |
| **Windows** | [Download installer](https://github.com/jgraph/drawio-desktop/releases) |
| **Linux** | `.deb`/`.rpm` from [releases](https://github.com/jgraph/drawio-desktop/releases); `sudo apt install xvfb` for headless |

Verify with `drawio --version`. On **WSL2** the CLI is the Windows desktop exe reached via `/mnt/c` — the skill detects this automatically.

### 2. Install the skill

```bash
npx skills add Agents365-ai/365-skills -g
```

Or clone manually:

```bash
git clone https://github.com/Agents365-ai/drawio-skill.git \
  ~/.claude/skills/drawio-skill
```

## Supported Diagram Types

| Category | Examples | Notable features |
|---|---|---|
| Architecture | microservices, cloud (AWS/GCP/Azure), network topology, deployment | Tier-based swimlanes, hub-center strategy |
| ML / Deep Learning | Transformer, CNN, LSTM, GRU | Tensor shape annotations, layer-type color coding |
| Flowcharts | business processes, workflows, decision trees, state machines | Semantic shapes (parallelogram I/O, diamond decisions) |
| UML | class diagrams, sequence diagrams | Inheritance / composition / aggregation arrows; lifelines + activation boxes |
| Data | ER diagrams, data flow diagrams (DFD) | Table containers, PK/FK notation |
| Other | org charts, mind maps, wireframes | — |

## Community

- **Discord:** https://discord.gg/Fpbkw7cAhp
- **WeChat:** Scan QR code for community group
- **GitHub:** https://github.com/Agents365-ai/drawio-skill

## License

[MIT](https://github.com/Agents365-ai/drawio-skill/blob/main/LICENSE)
