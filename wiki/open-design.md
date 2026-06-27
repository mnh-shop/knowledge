---
name: open-design
description: "Open Design system — build once, reuse everywhere: cross-agent design token and component framework"
source: sources/open-design/
tags: [acp, cli, design, desktop, documentation, mcp, design-system, typescript, nix]
type: wiki/overview
repo: https://github.com/nexu-io/open-design
---

# Open Design

An open-source, local-first alternative to Claude Design -- an agentic design workspace where coding agents (Claude Code, Codex, Cursor, Gemini CLI, and 18+ others) produce branded design artifacts directly on your machine. Instead of a cloud-only, model-locked service, Open Design treats any coding-agent CLI already on your `PATH` as the design engine.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 App Router + React 18 + TypeScript |
| Landing page | Astro (i18n, catalog pages) |
| Desktop shell | Electron + sidecar IPC (STATUS, EVAL, SCREENSHOT, CLICK, SHUTDOWN) |
| Daemon | Node 24, Express, SSE streaming, `better-sqlite3` |
| Package manager | pnpm 10.33.2 (monorepo) |
| Storage | SQLite (daemon-side) + filesystem under managed project directories |
| Preview | Sandboxed `srcdoc` iframe + streaming `<artifact>` parser |
| Export | HTML (inlined), PDF (browser print), PPTX (agent-driven), ZIP, Markdown, MP4 (HyperFrames) |
| MCP | stdio MCP server for read-only file access from agent context |

---

## Architecture

Open Design runs as a local daemon (Express + SQLite) that spawns a coding-agent CLI subprocess. The web UI communicates with the daemon over HTTP/SSE. The system supports three topologies:

1. **Fully local** -- browser talks to local daemon, which spawns agent CLIs.
2. **Web on Vercel + daemon on user machine** -- tunnel (cloudflared) bridges the two.
3. **Web on Vercel + direct API** -- no daemon; limited to BYOK proxy mode with IndexedDB storage.

```
┌────────────────── browser (Next.js 16) / Electron shell ──────────────┐
│  chat · file workspace · iframe preview · settings · import · MCP     │
└──────────────┬─────────────────────────────────────┬──────────────────┘
               │ /api/*                              │
               ▼                                     ▼
   ┌─────────────────────────────────┐   /api/proxy/{provider}/stream (SSE)
   │  local daemon (Express+SQLite)  │   ─→ any OpenAI-compatible BYOK,
   │                                  │       SSRF-guarded at the edge
   │  /api/skills    /api/plugins    │
   │  /api/design-systems            │
   │  /api/chat (SSE)   /api/proxy/* │
   │  /api/projects/:id/files/...    │
   │  /api/artifacts/{save,lint}     │
   │  /api/import/claude-design      │
   │  MCP stdio server                │
   └─────────┬───────────────────────┘
             │ spawn(cli, [...], { cwd: managed project cwd })
             ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │  claude · codex · cursor-agent · copilot · openclaw · gemini ·    │
   │  opencode · hermes (ACP) · kimi (ACP) · pi (RPC) · kiro · kilo · │
   │  vibe (ACP) · cline · trae · deepseek · qwen · qoder · antigravity│
   │  reads SKILL.md + DESIGN.md, writes artifacts to disk             │
   └──────────────────────────────────────────────────────────────────┘
```

---

## Key Components (packages and apps)

| Package / App | Path | Purpose |
|---|---|---|
| `@open-design/daemon` | `apps/daemon/` | Express server, CLI (`od`), all REST/SSE routes, runtime adapters, plugin/design-system/registry services |
| `@open-design/web` | `apps/web/` | Next.js 16 frontend with chat pane, file workspace, design system picker, plugin marketplace |
| `@open-design/desktop` | `apps/desktop/` | Electron shell with sidecar IPC |
| `@open-design/landing-page` | `apps/landing-page/` | Astro marketing site and design system catalog |
| `@open-design/packaged` | `apps/packaged/` | Thin packaged Electron runtime entry |
| `@open-design/contracts` | `packages/contracts/` | Pure TypeScript shared DTOs and types (web/daemon contract layer) |
| `@open-design/components` | `packages/components/` | Shared UI primitives |
| `@open-design/sidecar-proto` | `packages/sidecar-proto/` | Sidecar IPC protocol (app/mode/source constants, IPC schema) |
| `@open-design/sidecar` | `packages/sidecar/` | Generic sidecar bootstrap and IPC transport |
| `@open-design/platform` | `packages/platform/` | OS process stamp serialization and process primitives |
| `@open-design/tools-dev` | `tools/dev/` | Local development lifecycle control plane |
| `@open-design/tools-pack` | `tools/pack/` | Packaged build, installer identity, updater |
| `@open-design/tools-serve` | `tools/serve/` | Fixture-service control plane (e.g., updater metadata) |
| `@open-design/plugin-runtime` | `plugins/` | Plugin runtime and marketplace |
| `@open-design/registry-protocol` | `packages/registry-protocol/` | Registry/plugin protocol types |

---

## Design Systems

150 brand-grade `DESIGN.md` files ship with the repository. Each follows a 9-section schema (color, typography, spacing, layout, components, motion, voice, brand, anti-patterns). Systems are authored as plain Markdown in `design-systems/<brand>/DESIGN.md`.

Notable brands: Linear, Stripe, Vercel, Airbnb, Apple, Tesla, Notion, Anthropic, Cursor, Supabase, Figma, Spotify, Nike, Shopify, IBM, NVIDIA, and many more.

Also supports user-created systems (`user:` prefix) stored under a separate directory for editable/draft systems.

---

## Skills

100+ design skills in `skills/`. Each is a folder with a `SKILL.md` extended with Open Design frontmatter (`od:` namespace). Modes include: `prototype`, `deck`, `image`, `video`, `audio`, `template`, `design-system`, and `utility`. Scenario groups target roles: design, marketing, operation, engineering, product, finance, HR, sale, personal.

---

## Plugins

261 official plugins in `plugins/_official/` organized by category: scenarios (11), image templates (45), video templates (50), design systems (142), atoms (13), examples (140). Community plugins live in `plugins/community/`. Each plugin has a `SKILL.md` and an optional `open-design.json` manifest with marketplace metadata.

---

## Domain Model (from CONTEXT.md)

- **Project** -- top-level design workspace containing conversations and design files.
- **Normal Artifact** -- project design output represented by an entry file and manifest.
- **Live Artifact** -- refreshable project output stored with source data and preview state.
- **Artifact Entry File** -- primary file that opens/render a normal artifact.
- **Artifact Manifest** -- sidecar metadata identifying a file as a normal artifact.
- **Active Project** -- the most recently interacted project (used as MCP default).
- **Home Composer Media Surface** -- Home-only intent selectors (image, video, hyperframes, audio).
- **Chip Rail** -- row of intent chips below the Home prompt card.
- **AMR Cloud** / **AMR CLI** -- two faces of the official model router.

---

## Release Channels

| Channel | Identity | Use |
|---|---|---|
| `stable` | "Open Design" | Formal delivery |
| `beta` | "Open Design Beta" | Daily R&D/development validation |
| `prerelease` | "Open Design Prerelease" | Internal stable validation gate |
| `preview` | "Open Design Preview" | Early-access with stable-like rigor |

---

## Supporting Content

- `skills/` -- agent skill definitions (100+)
- `design-systems/` -- brand DESIGN.md files (150)
- `design-templates/` -- render templates (web-prototype, html-ppt, hyperframes, etc.)
- `plugins/` -- plugin marketplace (261 official, plus community)
- `mocks/` -- replay-based mock CLIs for testing
- `craft/` -- universal brand-agnostic craft rules
- `prompt-templates/` -- image and video prompts (93 image, 39 Seedance, 11 HyperFrames)
- `docs/` -- architecture, spec, protocols, i18n translations
- `e2e/` -- end-to-end tests (Playwright + Vitest harness)
- `scripts/` -- CI scripts, migration tools, validation guards
- `specs/` -- maintainability roadmap and cross-cutting specs

---

## Source

## Related

- [[mcp]] — MCP tool integration
- [[acp]] — Agent Communication Protocol
- [[hermes-agent]] — Design system consumers


Repository: `https://github.com/nexu-io/open-design`

Source checked out at: `/Users/admin1/Documents/knowledge/sources/open-design`

Primary language: TypeScript (with residual JavaScript in generated/compatibility paths)
