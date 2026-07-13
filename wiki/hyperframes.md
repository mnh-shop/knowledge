---
name: hyperframes
tags: [hyperframes, video-rendering, html-to-video, heygen, gsap, ffmpeg, puppeteer, open-source]
description: "Open-source framework for turning HTML, CSS, media, and seekable animations into deterministic MP4 videos"
source: sources/hyperframes/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Hyperframes

| Field | Value |
|---|---|
| **Origin** | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) |
| **Source** | `sources/hyperframes/` |
| **Repomix** | `raw/hyperframes/hyperframes.xml` |
| **Codegraph** | `graphs/hyperframes/` |
| **License** | Apache 2.0 |
| **Package Manager** | bun |
| **Language** | TypeScript (monorepo) |

## Overview

HyperFrames is an open-source framework for turning HTML, CSS, media, and seekable animations into deterministic MP4 videos. Built by [HeyGen](https://www.heygen.com/), it enables AI coding agents to write HTML compositions that render frame-accurate video output.

The core workflow is simple: **write HTML, render video**. Compositions use `data-*` attributes for timing, tracks, and composition metadata. Animation runtimes (GSAP, Lottie, Three.js, CSS, WAAPI, Anime.js, and others) plug in via the seek-by-frame adapter pattern. The rendering pipeline captures frames headlessly via Puppeteer (Chrome's BeginFrame API) and encodes them with FFmpeg.

The framework ships 20 AI agent skills (via `vercel-labs/skills`) that guide agents through the production loop: plan → design → layout → animate → validate → render.

## Key Features

- **Write HTML, Render Video** — Compositions are authored as HTML with `data-*` timing attributes. No proprietary tooling required
- **Deterministic Rendering** — Frame-accurate output via Chrome's BeginFrame API. No `Date.now()`, no unseeded `Math.random()`, no render-time network fetches in the animation pipeline
- **Seekable Animations** — GSAP is the primary animation runtime with a dedicated `createGSAPFrameAdapter()`. Lottie, Three.js, CSS animations, Anime.js, WAAPI, and TypeGPU also supported via the frame adapter pattern
- **20 AI Agent Skills** — Router skill (`/hyperframes`) dispatches to creation workflows: product-launch-video, website-to-video, faceless-explainer, pr-to-video, motion-graphics, music-to-video, slideshow, embedded-captions, talking-head-recut, general-video, plus remotion-to-hyperframes for porting
- **Registry** — 109 installable blocks (sub-composition scenes), 25 components (effects and snippets), 13 example projects
- **Player Web Component** — `<hyperframes-player>` custom element for embedding and playback
- **Studio** — Browser-based composition editor with live preview
- **Parallel Rendering** — Distributed frame capture with smart worker distribution across CPU cores
- **HDR & Transparent Background Support** — HDR10 capture pipeline, alpha PNG capture, WebGL shader transitions
- **Cross-Platform** — CLI, AWS Lambda, GCP Cloud Run deployment targets

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HyperFrames Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌───────────┐   ┌───────────┐   │
│  │   CLI     │   │  Studio  │   │   SDK     │   │  Player   │   │
│  │ (packages │   │ (browser │   │ (packages │   │ (web      │   │
│  │  /cli)    │   │  editor) │   │  /sdk)    │   │ component)│   │
│  └────┬─────┘   └────┬─────┘   └─────┬─────┘   └─────┬─────┘   │
│       │              │               │               │         │
│  ┌────▼──────────────▼───────────────▼───────────────▼─────┐   │
│  │                     Core (packages/core)                  │   │
│  │  Types · Parsers · Generators · Linter · Compiler        │   │
│  │  Runtime · Frame Adapters · Registry Client              │   │
│  │  Timeline Engine · Media Pipeline                         │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │              Engine (packages/engine)                      │   │
│  │  Browser Manager (Puppeteer) · Frame Capture (BeginFrame) │   │
│  │  Screenshot Service · Parallel Coordinator                │   │
│  │  Chunk Encoder (FFmpeg) · HDR Capture                    │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │             Producer (packages/producer)                   │   │
│  │  Render Orchestrator · HTML Compiler · Audio Mixer        │   │
│  │  Font Inliner · Deterministic Fonts · Shader Workers      │   │
│  │  Regression Harness · Lambda/GCP Adapters                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Registry (registry/)                           │   │
│  │  109 Blocks · 25 Components · 13 Examples                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Skills (skills/)                               │   │
│  │  20 AI Agent Skills · Skills Manifest                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Additional packages:                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐          │
│  │Shader    │ │Parsers   │ │AWS Lambda / GCP  │          │
│  │Transitions│ │(packages │ │(packages/aws-    │          │
│  │(packages │ │ /parsers)│ │lambda, gcp-cloud-│          │
│  │/shader-  │ │          │ │run)              │          │
│  │transitions│ │          │ │                  │          │
│  └──────────┘ └──────────┘ └──────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Package Structure

The monorepo (bun workspaces) is organized into 14 packages under `packages/`:

| Package | Description |
|---|---|
| **cli** | `hyperframes` CLI — `init`, `preview`, `lint`, `check`, `render`, `snapshot`, `doctor`, `publish`, `compositions`, `lambda`, `cloudrun`, `figma`, `capture`, and more |
| **core** | Types, parsers, generators, linter, compiler, runtime engine, timeline, frame adapters, media handling, GSAP integration, registry client, slideshow support, color grading |
| **engine** | Seekable page-to-video capture engine — Puppeteer browser manager, frame capture via BeginFrame API, screenshot service, parallel coordination, chunk encoder (FFmpeg), HDR capture, shader transitions |
| **producer** | Full rendering pipeline — HTML compiler, render orchestrator, audio mixer, font inliner, deterministic fonts, shader worker pool, regression harness, distributed rendering |
| **player** | `<hyperframes-player>` embeddable web component with composition probe, controls, timeline clock, runtime message handling, shader loader |
| **studio** | Browser-based composition editor UI (React + Vite + Tailwind) |
| **studio-server** | Studio backend server |
| **shader-transitions** | WebGL shader transition library for compositions |
| **parsers** | Composition parsing utilities (sub-composition validity, etc.) |
| **lint** | Composition linting utilities |
| **sdk** | Programmatic SDK for HyperFrames |
| **sdk-playground** | SDK playground environment |
| **aws-lambda** | AWS Lambda deployment adapter for cloud rendering |
| **gcp-cloud-run** | Google Cloud Run deployment adapter |

## AI Agent Skills

HyperFrames ships **20 AI agent skills** via [vercel-labs/skills](https://github.com/vercel-labs/skills). Skills are installable via `npx skills add heygen-com/hyperframes`.

### Router

| Skill | Purpose |
|---|---|
| `/hyperframes` | **Read first.** Capability map and intent router. Dispatches "make me a..." requests to the correct creation workflow. |

### Creation Workflows

| Skill | Input → Output |
|---|---|
| `/product-launch-video` | Product URL / brief → product launch promo video (~30-90s) |
| `/website-to-video` | General website URL → site tour / showcase video |
| `/faceless-explainer` | Arbitrary text → faceless explainer video (~30-90s), LLM-invented visuals |
| `/pr-to-video` | GitHub PR URL → code-change explainer video |
| `/embedded-captions` | Talking-head MP4 → same footage with styled captions |
| `/talking-head-recut` | Talking-head MP4 → footage with graphic overlays (lower-thirds, kinetic titles, callouts) |
| `/motion-graphics` | Design brief → short motion graphic MP4 / transparent overlay (~under 10s) |
| `/music-to-video` | Audio file → beat-synced music video (lyric / slideshow / kinetic) |
| `/slideshow` | Content → navigable deck (not rendered video; discrete slides, branching, hotspots) |
| `/general-video` | Any input → any video (fallback for unspecified or complex compositions) |
| `/remotion-to-hyperframes` | Existing Remotion (React) composition → ported HyperFrames HTML |

### Domain Skills (Atomic Capabilities)

| Skill | Covers |
|---|---|
| `/hyperframes-core` | Composition contract, `data-*` attributes, `class="clip"`, tracks, sub-compositions, determinism rules |
| `/hyperframes-animation` | All animation knowledge — GSAP, Lottie, Three.js, Anime.js, CSS, WAAPI, TypeGPU adapters |
| `/hyperframes-keyframes` | Seek-safe keyframe authoring — GSAP timelines, CSS keyframes, SVG morph/draw, 3D depth |
| `/hyperframes-creative` | Creative direction — frame.md, design.md, palettes, typography, beat planning |
| `/media-use` | Media OS — BGM, SFX, TTS, transcription, background removal, asset reuse |
| `/hyperframes-cli` | CLI dev loop — `init`, `lint`, `check`, `snapshot`, `preview`, `render`, `publish`, `doctor`, `lambda` |
| `/hyperframes-registry` | Registry block/component installation and authoring |
| `/figma` | Figma import — tokens, components, storyboard → composition |

## GSAP Seekable Animation & Frame Adapter Pattern

Animation runtimes plug into HyperFrames via the **frame adapter** pattern — a lightweight interface that normalizes any animation runtime to seek-by-frame:

```typescript
interface FrameAdapter {
  id: string;
  init?: (ctx: FrameAdapterContext) => Promise<void> | void;
  getDurationFrames: () => number;
  seekFrame: (frame: number) => Promise<void> | void;
  destroy?: () => Promise<void> | void;
}
```

**GSAP** is the primary adapter. The `createGSAPFrameAdapter()` function wraps a GSAP timeline (`duration()`, `seek()`, `pause()`) into a `FrameAdapter`. At each capture frame, the engine calls `seekFrame(n)`, which delegates to `timeline.seek(n / fps, false)` — pausing the timeline at the exact frame requested. This enables frame-accurate seekable animation without re-rendering the full animation.

Other supported runtimes include Lottie, Three.js, CSS Animations, Anime.js, WAAPI, and TypeGPU.

## Deterministic Rendering

HyperFrames guarantees frame-accurate, reproducible video output:

- **No `Date.now()` in the animation pipeline** — the runtime uses `performance.now()` and the `TransportClock` class for timekeeping; `Date.now()` is only used for event instrumentation timestamps (picker events, load telemetry)
- **No unseeded `Math.random()`** — compositions must not rely on non-deterministic RNG for visual output
- **No render-time network fetches** — all media must be resolved before rendering begins
- **Chrome BeginFrame API** — captures frames at precise time positions rather than real-time playback
- **FPGA encoding** — frames are encoded to video via FFmpeg with consistent parameters per render

## Registry

Located at `registry/`, the registry contains reusable composition assets:

- **109 blocks** (`registry/blocks/`) — installable sub-composition scenes including data-chart, code-snippet themes, transitions (3D, blur, cover, destruction, dissolve, distortion, grid, light, mechanical, push, radial, scale), visual effects (liquid-glass, magnetic, portal, shatter), map visualizations (world-map, us-map, spain-map), UI elements (macos-notification, spotify-card, reddit-post), and more
- **25 components** (`registry/components/`) — reusable effects including caption animations (blend-difference, clip-wipe, emoji-pop, glitch-rgb, gradient-fill, kinetic-slam, matrix-decode, neon-accent, parallax-layers, particle-burst, etc.), grain-overlay, morph-text, motion-blur, vignette, and more
- **13 examples** (`registry/examples/`) — starter projects: warm-grain, play-mode, swiss-grid, vignelli, decision-tree, kinetic-type, product-promo, nyt-graph, airbnb-deck, motion-blur, startup-pitch, slideshow-demo, vscode-theme-visualizer

## Player Web Component

The `<hyperframes-player>` custom element (`packages/player/src/hyperframes-player.ts`) provides embeddable video playback in the browser. It handles:

- Composition probing and loading (via `CompositionProbe`)
- Controls UI with play/pause, seek, and playback rate control (clamped to 0.1×–5×)
- Runtime message handling between the iframe composition and the player host
- Shader loading and WebGL capture for transparent-background compositions
- Timeline clock synchronization (`DirectTimelineClock`)
- Parent media element management (`ParentMediaManager`)

## CLI Commands

The `hyperframes` CLI (`packages/cli/src/cli.ts`) exposes commands for the full production loop:

| Command | Description |
|---|---|
| `init` | Scaffold a new composition project |
| `preview` | Launch browser preview with live reload |
| `lint` | Static HTML structure check |
| `check` | Browser gate — headless Chrome runtime errors, layout, motion, WCAG contrast |
| `render` | Full render to MP4 |
| `snapshot` | Capture a single frame screenshot |
| `doctor` | System diagnostics (Chrome, FFmpeg, GPU) |
| `publish` | Publish composition to registry |
| `catalog` | Browse registry catalog |
| `add` | Install registry blocks/components |
| `capture` | Frame capture utilities |
| `lambda` / `cloudrun` | Cloud rendering deploy/render/progress |
| `figma` | Figma import workflows |
| `compositions` | Composition management |
| `compare` | Visual comparison between renders |
| `keyframes` | Motion diagnostics |
| `tts` | Text-to-speech generation |
| `transcribe` | Audio transcription |
| `upgrade` | Upgrade project to latest HyperFrames version |

## Cross-References

- **[[Puppeteer]]** — `packages/engine/src/services/browserManager.ts` manages Chrome via Puppeteer for headless frame capture
- **[[FFmpeg]]** — `packages/engine/src/services/chunkEncoder.ts` and `packages/producer/src/services/renderOrchestrator.ts` use FFmpeg for video encoding and audio mixing
- **[[GSAP]]** — `packages/core/src/adapters/gsap.ts` provides the primary frame adapter for GSAP seekable animations
- **[[Lottie]]** — `packages/core/src/lottieReadiness.ts` provides Lottie animation support
- **[[Three.js]]** — `packages/engine/src/services/threeDProjection.ts` handles Three.js 3D scene capture

## Commands Reference

```bash
bun install           # Install dependencies
bun run build         # Build all packages
bun run test          # Run all unit tests
bun run lint          # Lint with oxlint
bun run format        # Format with oxfmt
```

## Source

- [README.md](https://github.com/heygen-com/hyperframes) — Project overview and quick start
- [AGENTS.md](https://github.com/heygen-com/hyperframes/AGENTS.md) — Agent skill documentation
- [DESIGN.md](https://github.com/heygen-com/hyperframes/DESIGN.md) — Design system and style guide
- [CLAUDE.md](https://github.com/heygen-com/hyperframes/CLAUDE.md) — Agent configuration
- [packages/](https://github.com/heygen-com/hyperframes/packages) — Monorepo packages
- [skills/](https://github.com/heygen-com/hyperframes/skills) — 20 AI agent skills
- [registry/](https://github.com/heygen-com/hyperframes/registry) — Blocks, components, examples
- [registry/registry.json](https://github.com/heygen-com/hyperframes/registry/registry.json) — Registry manifest
- [skills-manifest.json](https://github.com/heygen-com/hyperframes/skills-manifest.json) — Skills manifest with file counts and hashes
