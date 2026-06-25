# AionUi

**Source repo:** `/Users/admin1/Documents/knowledge/sources/AionUi`
**License:** Apache-2.0
**Current version:** 2.1.24

## Overview

AionUi is a free, open-source "Cowork" desktop application that transforms command-line AI agents into a modern graphical chat interface. Users interact with AI agents that operate directly on their computer -- reading files, writing code, browsing the web, and automating tasks -- through a built-in agent engine and a unified UI. The desktop app is backed by a standalone web runtime (no Electron required) for remote access.

## Tech Stack

- **Language:** TypeScript (strict mode, path aliases: `@/*`, `@process/*`, `@renderer/*`)
- **Desktop shell:** Electron, built with **electron-vite**
- **UI framework:** React (functional components + hooks)
- **Component library:** `@arco-design/web-react`
- **Icons:** `@icon-park/react`
- **Styling:** UnoCSS utility classes + CSS Modules; semantic color tokens; no hardcoded color values
- **Linting/Formatting:** oxlint + oxfmt
- **Package manager:** Bun (`bun.lock`)
- **Testing:** Vitest (target >=80% coverage), Playwright (E2E)
- **Build system:** electron-vite for desktop builds; `scripts/build-with-builder.js` for dist artifacts (macOS, Windows, Linux)
- **Internationalization:** i18next-based with code-generated TypeScript types

## Repository Structure

The project is a **Bun workspace monorepo** with four packages under `packages/`:

| Package | Path | Purpose |
|---------|------|---------|
| `@aionui/desktop` | `packages/desktop/` | Main Electron desktop application |
| `@aionui/web-host` | `packages/web-host/` | Standalone web server -- spawns backend, reverse-proxies, serves static files |
| `@aionui/web-cli` | `packages/web-cli/` | CLI wrapper (`aionui-web`) for the web-host runtime |
| `@aionui/shared-scripts` | `packages/shared-scripts/` | Scripts shared across packages |

### Desktop Application Architecture (`packages/desktop/`)

The Electron app follows a strict two-process model:

| Process | Path | Restriction |
|---------|------|-------------|
| **Main** | `packages/desktop/src/process/` | No DOM APIs |
| **Renderer** | `packages/desktop/src/renderer/` | No Node.js APIs |

Communication between processes goes through a **preload bridge** at `packages/desktop/src/preload/`.

Key sub-directories under `src/`:
- `common/` -- shared configuration, i18n config, types
- `renderer/` -- React UI, pages, hooks, components
- `process/` -- Electron main process: services, database drivers, startup logic
- `preload/` -- IPC bridge definitions

## Key Features (from readme & codebase analysis)

1. **Built-in AI agent engine** -- no external CLI agent required; ships with 21 pre-built professional assistants (Cowork, PPT Creator, Word Creator, Excel Creator, Morph PPT, Pitch Deck Creator, Academic Paper Writer, Financial Model Creator, and more)
2. **Multi-agent support** -- auto-detects and integrates with Claude Code, Codex, Qwen Code, Hermes Agent, Snow CLI, Cursor Agent, and 13+ external agents under a unified interface
3. **Full file system access** -- file read/write, workspace file diffing/staging/unstaging via a built-in file change list UI (git-aware)
4. **WebUI mode** -- `bun run webui` starts a standalone web server (no Electron) accessible from a browser; supports remote access and mobile devices
5. **Scheduled automation** -- cron-based 24/7 unattended task execution
6. **Office document generation** -- integrates with [OfficeCLI](https://github.com/iOfficeAI/OfficeCLI) for PPT (Morph), Word (`.docx`), and Excel (`.xlsx/.xlsm/.csv`) creation
7. **Remote channels** -- accessible via Telegram, Lark, DingTalk, WeChat
8. **Internationalization** -- full i18n support with English, Simplified Chinese, Traditional Chinese, Japanese, Korean, Spanish, Portuguese, Turkish, Russian, and Ukrainian translations
9. **MCP (Model Context Protocol)** support -- extensible tool system for AI agents

## Notable Code Symbols (surface area from CodeGraph analysis)

- **React hooks:** `useConversationListSync`, `useModelProviderList`, `useAssistantList`, `useUploadState`, `useWorkspaceEvents`, `useWorkspaceFileOps`
- **Components:** `FileChangeList`, `WorkspaceTabBar`, `ChatWorkspace`, `ModalWrapper`, `StepsWrapper`, `ComponentsShowcase`, `FileChangeItem`, `CronJobSiderItem`
- **Main process services:** `BetterSqlite3Driver` (database driver implementing `ISqliteDriver` contract), startup architecture compatibility checks (`assertStartupArchitectureCompatible`)
- **Scripts:** `webui.ts` (standalone web host launcher), `resetpass.ts` (admin password reset), `run-benchmarks.ts`
- **Startup:** Rosetta/architecture mismatch detection on macOS (`detectStartupArchitectureMismatch`)

## Coding Conventions (from `AGENTS.md`)

- **Directory size limit:** max 10 direct children per directory; split when approaching the limit
- **Naming:** PascalCase for components, camelCase for utilities/hooks/types/constants, kebab-case for CSS modules, `use` prefix for hooks
- **UI:** Only `@arco-design/web-react` components -- no raw `<button>` or `<input>`
- **CSS:** UnoCSS utility classes preferred; complex styles use CSS Modules with semantic color tokens
- **TypeScript:** strict mode, no `any`, no implicit returns; `type` over `interface` (per oxlint config)
- **No hardcoded user-facing strings** -- all text goes through i18n keys
- **Commit format:** Conventional Commits (`<type>(<scope>): <subject>`)
- **CI:** `just push` enforces lint, format, typecheck, and tests before every push; `prek` replicates the full CI pipeline

## Build & Run

```bash
bun install              # install dependencies (Bun workspace)
bun run dev              # start Electron dev mode
bun run webui            # start standalone web UI (no Electron)
bun run package          # build for production
bun run test             # run all vitest tests
bun run lint             # run oxlint
bun run format           # run oxfmt
```
