---
name: openclaw-memory
tags: [agent-gateway, dreaming, embeddings, memory, openclaw, plugin-sdk, qmd, sqlite, typescript]
description: OpenClaw Memory Architecture
source: sources/openclaw/
---

# OpenClaw Memory Architecture
**Source:** `sources/openclaw/`

OpenClaw memory is a set of plain Markdown files plus a SQLite index, organized into five tiers with different trust levels, write rules, and injection behavior. The end-to-end design is documented in `docs/concepts/memory-architecture.md`; implementation lives in the `memory-core` extension and the memory host SDK in `src/memory-host-sdk/`.

## The Five-Tier Model

The tier model from `docs/concepts/memory-architecture.md`:

| Tier | Surface | Written by | Injected |
|------|---------|-----------|----------|
| Instructions | `AGENTS.md` and workspace instruction files | Human only | Always, at session start |
| Curated core | `MEMORY.md`, `USER.md` | Dreaming consolidation; direct user request | Always, at session start, budgeted |
| Episodic | `memory/YYYY-MM-DD.md` daily notes, session transcripts | Agent during work; memory flush; transcript capture | Never; searchable on demand |
| Prospective | Standing intents (SQLite) and cron jobs | `intent` tool; scheduled tasks | Only when a trigger fires |
| Review | `DREAMS.md`, dreaming reports | Dreaming phases | Never; for human reading |

The boundary that matters most is between **curated core** and **episodic**: curated files are small, always in context, and written only through gated consolidation; episodic files are large, append-friendly, and reachable only through explicit search tools or the escalation lane. Nothing crosses from episodic to curated without passing promotion gates.

## Write-Path Provenance

Provenance is recorded at write time in SQLite columns the model cannot write through prose (per `docs/concepts/memory-architecture.md`):

- **Origin class** — closed set: `owner`, `agent`, `untrusted` (derived from web pages, tool output, or non-owner group participants), and `system` (heartbeat prompts, cron preambles).
- **Session kind** — interactive, cron, heartbeat, or sub-agent.
- **Observed timestamp and supersession key** — date each fact and let newer observations supersede older ones.

Two hygiene rules use this metadata: **session-kind gating** (cron, heartbeat, and sub-agent sessions produce no durable memory candidates) and **recall-loop prevention** (content injected from memory is structurally marked and never re-extracted). Content whose provenance cannot be determined defaults to `untrusted`/`system`, never `owner`.

## Dreaming Consolidation

Dreaming is the background consolidation system in `extensions/memory-core`, enabled by default (`plugins.entries.memory-core.config.dreaming.enabled`). It runs three cooperative phases per sweep — **light, REM, deep** — documented in `docs/concepts/dreaming.md`:

1. **Light and REM** stage and reflect: dedupe recent signals, stage candidates, build theme reflections, record reinforcement — without touching long-term memory.
2. **Deep** promotes through two gates in sequence:
   - **Deterministic gate** — candidates ranked by weighted signals (retrieval relevance, recall frequency, query diversity, recency, multi-day recurrence, conceptual richness); `untrusted`/`system` origin excluded structurally before any prompt is built.
   - **Consolidation step** — a model turn produces a revised `MEMORY.md`: duplicates merged, superseded entries retired via supersession keys, source references preserved as daily-note anchors. Output accepted only if it passes structural validation and stays within the bootstrap budget.

**Write safety** uses optimistic concurrency: the content hash captured when consolidation input was built is re-checked immediately before an atomic rename; on conflict the rewrite aborts for that sweep and an append fallback runs. The pre-image of every accepted rewrite is stored and a human-readable summary is appended to `DREAMS.md`.

## Recall: Two Lanes

- **Lane 1 (always on, zero model calls):** bootstrap injection of `MEMORY.md`/`USER.md` at session start; ranked `memory_search` scoring hybrid relevance by exponential recency decay (30-day half-life) and an importance multiplier; trigger injection where writer-attached trigger phrases (trailing `<!-- trigger: ... -->` and `<!-- importance: N -->` comments) run a lexical/vector prefilter and inject at most three matching entries per turn. Auto-injection is restricted to the curated tier.
- **Lane 2 (escalation):** the blocking recall sub-agent from `extensions/active-memory` — a real agent turn that searches conversation history, running only when the message shows recall intent and Lane 1 produced no strong hit (configurable `mode: "always"` / `"off"`).

## QMD Engine and Embeddings

- **Builtin engine** — default in-memory/SQLite hybrid search (BM25 + vectors) managed by `extensions/memory-core/src/memory/` (manager, hybrid, mmr, tokenize, embeddings, project-ranking, temporal-decay).
- **QMD** (`docs/concepts/memory-qmd.md`) — local-first search sidecar combining BM25, vectors, and reranking with query expansion; can index extra directories and session transcripts; runs with the llama.cpp provider plugin and auto-downloads GGUF models. Enabled via `memory.backend: "qmd"`; falls back to the builtin engine automatically if unavailable. Host-side engine wiring lives in `src/memory-host-sdk/engine-qmd.ts` and `engine-storage.ts`.
- Embedding providers are pluggable; see `memory-embedding-provider-runtime.ts` / `memory-embedding-providers.ts` in `src/plugins/` and `memory-core-host-embedding-registry.ts` in `src/plugin-sdk/`.

## Code Map

- `extensions/memory-core/` — the memory-core plugin (142 non-test `.ts` files): `dreaming-*.ts` (phases, consolidation, narrative, markdown, dreams-file, repair, state), `rem-*.ts` (REM evidence/harness), `cli-*.ts` (dreaming/REM/status/index CLI), `memory-tool-manager` + `tools.ts`/`tools.runtime.ts`/`tools.citations.ts` (memory tools), `qmd-*.ts` + `src/memory/qmd-*.ts` (QMD manager/collection), `short-term-promotion-*.ts` (episodic-to-curated promotion), `standing-intents.ts` (prospective tier), `session-backfill-*.ts`, `memory-budget.ts`, `flush-plan.ts`.
- `src/memory-host-sdk/` — host-side SDK: `dreaming.ts`, `engine-qmd.ts`, `engine-storage.ts`, `query.ts`, `events.ts` (plus `event-store.ts`, `event-types.ts`, `event-export.ts`, `status.ts`, `multimodal.ts`).
- `extensions/active-memory/` — escalation lane: `recall.ts`, `recall-run.ts`, `recall-state.ts`, `transcript.ts`, `transcript-watch.ts`, `escalation.ts`, `session-policy.ts`, `trigger-recall.ts`.
- `extensions/memory-lancedb/` — LanceDB vector backend (`docs/plugins/memory-lancedb.md`).
- `extensions/memory-wiki/` — wiki-based memory surface (`docs/plugins/memory-wiki.md`).

## Surfaces

- **`MEMORY.md`** — curated core facts, always injected (budgeted), consolidated by dreaming, project-scoped via trailing `<!-- project: origin-remote -->` annotations.
- **`USER.md`** — the user model: imperative directives ("Always"/"Never"/"Prefer") with date + active/superseded status; updates supersede in place. Never project-scoped.
- **`DREAMS.md`** — the Dream Diary: review surface listing every consolidation's summary and pre-image trail; phase reports optionally under `memory/dreaming/<phase>/YYYY-MM-DD.md`. Machine state lives in `memory/.dreams/`.

## Security Model

Memory poisoning is defended structurally, not by content scanning (per `docs/concepts/memory-architecture.md`): unforgeable provenance (SQLite columns written by classification code), quarantine by tier (untrusted content barred from curated core and auto-injection), taint propagation through consolidation (gates check candidate provenance, not just scores), and review surfaces (`DREAMS.md` + Dreams UI expose phase state, staged candidates, and promoted entries).

## Key Source Files

| File | Purpose |
|------|---------|
| `docs/concepts/memory-architecture.md` | End-to-end memory architecture (tiers, provenance, dreaming, recall, security) |
| `docs/concepts/dreaming.md` | Dreaming phases (light/REM/deep), machine state, write safety |
| `docs/concepts/memory-qmd.md` | QMD engine setup and capabilities |
| `docs/concepts/active-memory.md` | Escalation lane and cross-conversation recall |
| `extensions/memory-core/src/dreaming.ts` | Dreaming orchestration |
| `extensions/memory-core/src/standing-intents.ts` | Prospective memory (`intent` tool) |
| `src/memory-host-sdk/dreaming.ts` | Host-side dreaming integration |
| `src/memory-host-sdk/engine-qmd.ts` | QMD host engine |
| `src/memory-host-sdk/query.ts` | Host memory query surface |
| `extensions/active-memory/src/recall.ts` | Escalation recall lane |

## Related

- [[domains/architecture/openclaw-architecture.md]] — Overall gateway architecture
- [[domains/plugins/openclaw-plugins.md]] — Plugin system hosting memory-core
- [[wiki/openclaw.md]] — Wiki entry
