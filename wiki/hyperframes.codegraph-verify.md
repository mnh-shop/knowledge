---
name: hyperframes-codegraph-verify
tags: [hyperframes, codegraph-verify, video-rendering, heygen]
description: "Codegraph Verification: hyperframes — validating wiki claims against indexed source code symbols"
source: sources/hyperframes/
---

# Codegraph Verification: hyperframes

**Date:** 2026-07-12

## Claim 1: Monorepo with 14 packages including cli, core, engine, player, producer, studio
- **Wiki says:** "14 packages under `packages/`: cli, core, engine, player, producer, shader-transitions, studio, aws-lambda, gcp-cloud-run, lint, parsers, sdk, sdk-playground, studio-server"
- **Source evidence:**
  - `packages/` directory listing confirms 14 subdirectories: `aws-lambda/`, `cli/`, `core/`, `engine/`, `gcp-cloud-run/`, `lint/`, `parsers/`, `player/`, `producer/`, `sdk/`, `sdk-playground/`, `shader-transitions/`, `studio/`, `studio-server/`
  - `package.json:2` — `"name": "hyperframes-monorepo"`
  - `package.json:8-10` — Workspaces declaration: `"workspaces": ["packages/*"]`
  - `package.json:11` — `"type": "module"` confirming ESM monorepo structure
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: CLI commands — hyperframes init, preview, lint, check, render, snapshot, doctor, publish
- **Wiki says:** "CLI commands for the full production loop: init, preview, lint, check, render, snapshot, doctor, publish, catalog, add, capture, lambda, cloudrun, figma, compositions, compare, keyframes, tts, transcribe, upgrade"
- **Source evidence:**
  - `packages/cli/src/commands/` — 45+ command modules including: `init.ts`, `preview.ts`, `lint.ts`, `check.ts`, `render.ts`, `snapshot.ts`, `doctor.ts`, `publish.ts`, `catalog.ts`, `add.ts`, `capture.ts`, `lambda.ts`, `cloudrun.ts`, `figma.ts`, `compare.ts`, `keyframes.ts`, `tts.ts`, `transcribe.ts`, `upgrade.ts`, `compositions.ts`, `batchRender.ts`, `browser.ts`, `beats.ts`, `benchmark.ts`, `present.ts`, `remove-background.ts`, `skills.ts`, `validate.ts`, `docs.ts`, `feedback.ts`, `events.ts`, `info.ts`, `inspect.ts`, `layout.ts`, `play.ts`, `grade-compare.ts`, `auth.ts`, `telemetry.ts`, `contrast-bg.ts`, `contrast-fg.ts`, `contrast-sample.ts`, `motionShot.ts`, `motionShotLayout.ts`, `deprecationTestHarness.ts`, `coreSkillContent.ts`
  - `packages/cli/src/cli.ts` — CLI entry point that imports and dispatches commands
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: 20 AI agent skills in skills/ directory
- **Wiki says:** "20 AI agent skills via vercel-labs/skills: router (/hyperframes), creation workflows (product-launch-video, website-to-video, faceless-explainer, embedded-captions, talking-head-recut, pr-to-video, motion-graphics, music-to-video, slideshow, general-video, remotion-to-hyperframes), domain skills (hyperframes-core, hyperframes-animation, hyperframes-keyframes, hyperframes-creative, media-use, hyperframes-cli, hyperframes-registry, figma)"
- **Source evidence:**
  - `skills/` directory — 20 skill subdirectories confirmed: `embedded-captions/`, `faceless-explainer/`, `figma/`, `general-video/`, `hyperframes/`, `hyperframes-animation/`, `hyperframes-cli/`, `hyperframes-core/`, `hyperframes-creative/`, `hyperframes-keyframes/`, `hyperframes-registry/`, `media-use/`, `motion-graphics/`, `music-to-video/`, `pr-to-video/`, `product-launch-video/`, `remotion-to-hyperframes/`, `slideshow/`, `talking-head-recut/`, `website-to-video/`
  - `skills-manifest.json` — 20 entries with hashes and file counts (confirms exactly 20 skills)
  - `README.md:54` — "HyperFrames ships 20 skills agents load on demand"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: GSAP frame adapter — seekable animation via FrameAdapter pattern
- **Wiki says:** "GSAP is the primary adapter. The `createGSAPFrameAdapter()` function wraps a GSAP timeline into a `FrameAdapter`. At each capture frame, the engine calls `seekFrame(n)`, which delegates to `timeline.seek(n / fps, false)`"
- **Source evidence:**
  - `packages/core/src/adapters/types.ts:9-15` — `FrameAdapter` interface: `id`, `init?`, `getDurationFrames()`, `seekFrame()`, `destroy?`
  - `packages/core/src/adapters/gsap.ts:1-44` — `createGSAPFrameAdapter()` implementation: wraps GSAP timeline `duration()`, `seek(timeInSeconds, suppressEvents)`, `pause()` into FrameAdapter
  - `packages/core/src/adapters/gsap.ts:37-41` — `seekFrame`: `timeline.seek(targetSeconds, false)` with clamped frame-to-seconds conversion
  - `packages/core/src/adapters/index.ts` — Exports `FrameAdapter`, `FrameAdapterContext`, `createGSAPFrameAdapter`
  - `packages/core/src/adapters/gsap.ts:12-16` — `CreateGSAPFrameAdapterOptions` with `id?`, `fps`, `timeline`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Engine — Puppeteer-based HTML capture via Chrome BeginFrame API
- **Wiki says:** "Engine packages/engine: Puppeteer browser manager, frame capture via BeginFrame API, screenshot service, parallel coordination, chunk encoder (FFmpeg)"
- **Source evidence:**
  - `packages/engine/src/services/browserManager.ts:1-7` — JSDoc: "Manages Puppeteer browser lifecycle: Chrome executable resolution, launch args, pooled browser acquisition/release." Imports `Browser`, `PuppeteerNode` from `puppeteer-core` (line 8)
  - `packages/engine/src/services/frameCapture.ts:1-9` — JSDoc: "Uses Puppeteer to capture frames from any web page implementing the window.__hf seek protocol. Navigates to a file server URL, waits for the page to expose window.__hf, then captures frames deterministically via Chrome's BeginFrame API or Page.captureScreenshot fallback."
  - `packages/engine/src/services/screenshotService.ts` — `beginFrameCapture`, `pageScreenshotCapture`, `captureAlphaPng`
  - `packages/engine/src/services/chunkEncoder.ts:1-7` — JSDoc: "Encodes captured frames into video using FFmpeg. Supports CPU (libx264) and GPU encoding."
  - `packages/engine/src/services/parallelCoordinator.ts` — `calculateOptimalWorkers`, `distributeFrames`, `executeParallelCapture`, `mergeWorkerFrames`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Producer — Full rendering pipeline with FFmpeg encoding, audio mixing, and render orchestration
- **Wiki says:** "Producer packages/producer: HTML compiler, render orchestrator, audio mixer, font inliner, deterministic fonts, shader worker pool, regression harness, distributed rendering"
- **Source evidence:**
  - `packages/producer/src/services/renderOrchestrator.ts` — Render orchestrator for coordinating the full pipeline
  - `packages/producer/src/services/htmlCompiler.ts:1-11` — JSDoc: "Two-phase compilation that guarantees every media element has data-end. Also handles sub-compositions referenced via data-composition-src." 2,327 lines implementing compilation pipeline
  - `packages/producer/src/services/audioMixer.ts` — Audio mixing for composition audio tracks
  - `packages/producer/src/services/deterministicFonts.ts` — Font inlining for deterministic rendering
  - `packages/producer/src/services/shaderTransitionWorkerPool.ts` — WebGL shader transition worker pool
  - `packages/producer/src/services/regression-harness.ts` — Regression testing harness
  - `packages/producer/src/services/distributed/` — Distributed rendering support
  - `packages/engine/src/services/audioMixer.ts` — Audio element parsing and processing (`parseAudioElements`, `processCompositionAudio`)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Player — `<hyperframes-player>` web component in packages/player/
- **Wiki says:** "The `<hyperframes-player>` custom element (packages/player/src/hyperframes-player.ts) provides embeddable video playback in the browser"
- **Source evidence:**
  - `packages/player/src/hyperframes-player.ts:53` — `class HyperframesPlayer extends HTMLElement` — defines the web component
  - `packages/player/src/hyperframes-player.ts:54-66` — `static get observedAttributes()` — `src`, `srcdoc`, `width`, `height`, `controls` and more
  - `packages/player/src/composition-probe.ts` — `CompositionProbe` class for probing composition metadata
  - `packages/player/src/controls.ts` — Player controls implementation
  - `packages/player/src/controls-setup.ts` — Controls setup utilities
  - `packages/player/src/direct-timeline-clock.ts` — `DirectTimelineClock` for timeline synchronization
  - `packages/player/src/runtime-message-handler.ts` — Cross-iframe runtime message handling
  - `packages/player/src/timeline-adapters.ts` — Timeline adapter types
  - `packages/player/src/styles.ts` — Player styles injection
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Registry — 50+ blocks, 25 components, 13 examples
- **Wiki says:** "109 installable blocks, 25 components, 13 example projects" and "109 blocks, 25 components, 13 examples"
- **Source evidence:**
  - `registry/blocks/` — 109 block directories confirmed, including: data-chart, 34+ code-snippet themes, transitions (3D, blur, cover, destruction, dissolve, distortion, grid, light, mechanical, push, radial, scale), visual effects (liquid-glass, magnetic, portal, shatter), map visualizations (world-map, us-map, spain-map), UI elements (macos-notification, spotify-card, reddit-post), video effects (glitch, cross-warp-morph, whip-pan, light-leak), and more
  - `registry/components/` — 25 component directories confirmed: caption-blend-difference, caption-clip-wipe, caption-editorial-emphasis, caption-emoji-pop, caption-glitch-rgb, caption-gradient-fill, caption-highlight, caption-kinetic-slam, caption-matrix-decode, caption-neon-accent, caption-neon-glow, caption-parallax-layers, caption-particle-burst, caption-pill-karaoke, caption-texture, caption-weight-shift, grain-overlay, grid-pixelate-wipe, morph-text, motion-blur, parallax-unzoom, parallax-zoom, shimmer-sweep, texture-mask-text, vignette
  - `registry/examples/` — 13 example directories: airbnb-deck, decision-tree, kinetic-type, motion-blur, nyt-graph, play-mode, product-promo, slideshow-demo, startup-pitch, swiss-grid, vignelli, vscode-theme-visualizer, warm-grain
  - `registry/registry.json:1-575` — Registry manifest file with all items listed
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the HyperFrames wiki have been verified against the source code:

- ✅ **Monorepo structure:** 14 packages confirmed in `packages/` with workspace declaration in `package.json`
- ✅ **CLI commands:** 45+ command modules in `packages/cli/src/commands/` verified
- ✅ **20 AI agent skills:** 20 skill directories in `skills/` + 20 entries in `skills-manifest.json` confirmed
- ✅ **GSAP frame adapter:** `packages/core/src/adapters/gsap.ts` with `createGSAPFrameAdapter()` and `FrameAdapter` interface verified
- ✅ **Puppeteer-based engine:** `frameCapture.ts` and `browserManager.ts` confirmed Puppeteer + BeginFrame API usage
- ✅ **Producer pipeline:** `renderOrchestrator.ts`, `htmlCompiler.ts`, `audioMixer.ts` confirmed full rendering pipeline
- ✅ **Player web component:** `HyperframesPlayer extends HTMLElement` in `hyperframes-player.ts` confirmed
- ✅ **Registry count:** 109 blocks + 25 components + 13 examples confirmed by directory listing

## Related

- [[hyperframes]] — Main wiki entry

## Cross-project

- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
- [[hermes-agent.codegraph-verify]] — Similar codegraph verification for Hermes Agent
- [[turnstone.codegraph-verify]] — Similar codegraph verification for Turnstone
