---
name: AionUi-codegraph-verify
tags: [codegraph-verify, aionui, ui, desktop]
description: "Codegraph Verification: AionUi"
source: sources/AionUi/
date: 2026-07-12
---

# Codegraph Verification: AionUi

**Date:** 2026-07-12

## Claim 1: Desktop UI for AI agent management with cross-platform support
- **Wiki says:** AionUi is a cross-platform desktop application (macOS, Windows, Linux) that provides a UI for managing and interacting with AI agents, built with Electron.

- **Source evidence:** `README.md` badges show `platform-macOS%20%7C%20Windows%20%7C%20Linux`. `README.md` line 1 states "Cowork with AI Agents" with a banner image. Source structure confirms Electron architecture: `packages/desktop/` with `main` (Node.js) and `renderer` (React) process separation. `AGENTS.md` lines 56-63 document the dual-process architecture with IPC bridge. Build tools include `Makefile`, `Dockerfile`, and `entitlements.plist` for macOS code signing. `CHANGELOG.md` shows ongoing desktop releases (latest v2.1.44, 2026-07-30) with features like file browser, filename search, and chat-ref. `package.json:3` confirms `"version": "2.1.44"`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Multi-agent mode with auto-detection of CLI agents
- **Wiki says:** AionUi auto-detects installed CLI agents (Claude Code, Codex, Hermes Agent, OpenClaw, etc.) and provides a unified Cowork interface for all of them.

- **Source evidence:** `README.md` lines 142-148 document multi-agent mode: "AionUi auto-detects them and lets you Cowork with all of them." The list of supported agents includes "Built-in Agent (zero setup), Claude Code, Codex, Qwen Code, Goose AI, OpenClaw, Augment Code, CodeBuddy, Kimi CLI, OpenCode, Factory Droid, GitHub Copilot, Qoder CLI, Mistral Vibe, Nanobot, Aion CLI, Snow CLI, Hermes Agent, Cursor Agent and more." Lines 152-156 document auto-detection, unified interface, parallel sessions with independent context, MCP unified management, and YOLO Mode. The README shows a GIF (`multi-agent支持openclaw.gif`) demonstrating multi-agent Cowork.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Team Mode coordinated multi-agent orchestration
- **Wiki says:** AionUi provides Team Mode where a Leader agent receives instructions, breaks them into subtasks, and delegates to Teammate agents via ACP (Agent Communication Protocol) with parallel execution.

- **Source evidence:** `README.md` lines 158-177 document Team Mode in detail. The Leader delegates to Teammate agents via a "built-in Team MCP Server" with parallel execution and an "async mailbox." `README.md` line 166 states "Parallel multi-agent execution — Leader breaks tasks into subtasks and delegates to Teammate agents running in parallel; each Teammate uses its own model via ACP." Line 167 lists supported backends: "Claude Code, Codex, Hermes Agent, Gemini, Snow CLI, and Aion CLI." Line 175 documents "Dynamic scaling — add or remove Teammates while the team is running." Line 176: "Granular permissions — each agent has its own permission confirmation dialog". `package.json:78` confirms the ACP dependency: `"@agentclientprotocol/sdk": "^0.18.2"`. `CHANGELOG.md` confirms active Team Mode development (v2.1.27: "reconcile stale run state", v2.1.28: "lock team cron execution mode").

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Built-in agent engine with zero configuration
- **Wiki says:** AionUi ships with a built-in AI agent engine that works immediately after installation with just an API key — no CLI tools to install separately.

- **Source evidence:** `README.md` lines 74-81 document the built-in agent: "AionUi ships with a complete AI agent engine. Unlike tools that require you to install CLI agents separately, AionUi works the moment you install it." Key features: "No CLI tools to install, No complex setup, Full agent capabilities — file read/write, web search, image generation, MCP tools." Lines 82-84 list "21 built-in professional assistants" including PPT Creator, Word Creator, Excel Creator, Academic Paper Writer, and more. Lines 185-197 show the "Any API Key" model: "Your API Key → What You Get" table covering Gemini, OpenAI, Anthropic, AWS Bedrock, Ollama/LM Studio, and NewAPI Gateway.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Office assistant suite (PPT, Word, Excel) via OfficeCLI
- **Wiki says:** AionUi includes office assistant capabilities for generating PowerPoint, Word, and Excel documents via the OfficeCLI integration.

- **Source evidence:** `README.md` lines 87-138 document the office assistant suite: "PPT assistant" with Morph-animated `.pptx` output, "Word assistant" for `.docx` paper/thesis writing, and "Excel assistant" for `.xlsx/.xlsm/.csv` spreadsheets. All three reference "powered by [OfficeCLI](https://github.com/iOfficeAI/OfficeCLI)." The README includes embedded GIF demos for each assistant type: morph-ppt-balanced.gif, readme-demo-assistant-ppt.gif, readme-demo-generate-academic-paper.gif, readme-demo-assistant-write-paper.gif, readme-demo-generate-excel.gif, readme-demo-assistant-excel.gif. Line 89: "the `pptx` / `docx` / `xlsx` skills (see `assistant/` presets and `skills/` in the repo)."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Remote access via WebUI, Telegram, and other messaging platforms
- **Wiki says:** AionUi supports remote access from mobile devices via WebUI, Telegram, Lark, DingTalk, and WeChat.

- **Source evidence:** `README.md` line 63 documents remote access in the feature comparison table: "Remote access from phone — WebUI + Telegram / Lark / DingTalk / WeChat." Resource files confirm these integrations exist: `resources/remote-telegram.png`, `resources/remote.png`, `resources/webui-remote.png`, `resources/webui-remote-example.png`, `resources/remote-telegram copy.png`, `resources/webui%20banner.png`. The `docs/guides/webui.md` guide confirms a standalone web UI can operate alongside the desktop app.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: 13-locale i18n, AionCore integration, and 4-package Bun workspace
- **Wiki says:** AionUi ships 13 locales (adding de-DE, fr-FR, fa-IR beyond the original 10), pins the AionCore local backend via `aioncoreVersion`, and is a 4-package Bun workspace (`desktop/`, `web-host/`, `web-cli/`, `shared-scripts/`).

- **Source evidence:** `packages/desktop/src/common/config/i18n-config.json` `supportedLanguages` lists 13 entries: `zh-CN`, `en-US`, `ja-JP`, `zh-TW`, `ko-KR`, `tr-TR`, `ru-RU`, `uk-UA`, `pt-BR`, `de-DE`, `es-ES`, `fr-FR`, `fa-IR`. `packages/desktop/src/renderer/services/i18n/locales/` contains 13 locale directories matching that list. `package.json:258` pins `"aioncoreVersion": "v0.1.55"` and `package.json:11-13` defines workspaces `packages/*` (resolved to `desktop/`, `web-host/`, `web-cli/`, `shared-scripts/`, confirmed by `bun.lock`). `package.json:78` declares `"@agentclientprotocol/sdk": "^0.18.2"` for Team Mode / ACP.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[AionUi]] -- Main wiki entry
- [[clawpier]] -- Desktop GUI comparison
- [[hermes-workspace]] -- Hermes Workspace
- [[pi]] -- Pi agent harness

## Cross-project

- [[clawpier.codegraph-verify]] -- Clawpier verification
- [[materia.codegraph-verify]] -- Materia agent framework verification
