---
name: openclaw-skills
tags: [agent-gateway, cli, clawhub, markdown, openclaw, plugin-sdk, security, skills, typescript, workshop]
description: OpenClaw Skills
source: sources/openclaw/
---

# OpenClaw Skills
**Source:** `sources/openclaw/`

Skills are Markdown instruction files that teach the agent how and when to use tools. Each skill lives in a directory containing a `SKILL.md` file with YAML frontmatter and a markdown body. OpenClaw loads bundled skills plus local overrides, and filters them at load time based on environment, config, and binary presence. The operator-facing documentation is `docs/tools/skills.md`; the runtime lives in `src/skills/`.

## SKILL.md Format

Each skill directory contains a `SKILL.md` with:

- **YAML frontmatter** — `name` (used as the skill name and slash command), `description` (shown in the system-prompt skill list), plus additional metadata.
- **Markdown body** — instructions the agent reads on demand via the skill tooling; the model is expected to read the skill only when needed.

Skill roots support grouped layouts: OpenClaw discovers a skill whenever `SKILL.md` appears anywhere under a configured root, up to 6 levels deep. The folder path is for organization only; the skill's name comes from the `name` frontmatter field (or the directory name when `name` is missing).

## Loading Precedence (Six Tiers)

From `docs/tools/skills.md`, sources are loaded **highest precedence first**; when the same skill name appears in multiple places, the highest source wins:

| Priority | Source | Path |
|----------|--------|------|
| 1 — highest | Workspace skills | `<workspace>/skills` |
| 2 | Project agent skills | `<workspace>/.agents/skills` |
| 3 | Personal agent skills | `~/.agents/skills` (default state only) |
| 4 | Managed / local skills | `<state-dir>/skills` |
| 5 | Bundled skills | shipped with the install |
| 6 — lowest | Extra directories | `skills.load.extraDirs` + plugin skills |

Codex CLI's native `$CODEX_HOME/skills` is not an OpenClaw skill root — `openclaw migrate plan codex` inventories those skills and `openclaw migrate codex` copies them into the workspace. Connected headless nodes can publish their own skills, which appear while the node is connected and receive deterministic node-prefixed names on collision.

## Gating and Allowlists

Skill **location** (precedence) and skill **visibility** (which agent can use it) are separate controls. Per-agent allowlists are set in `agents.defaults.skills` (shared baseline) and `agents.entries.*.skills` (final set, replaces defaults entirely; `[]` exposes no skills). The effective allowlist applies across prompt building, slash-command discovery, sandbox sync, and skill snapshots. It is not a host-shell authorization boundary — constrain `exec` separately with sandboxing and OS-user isolation.

## ClawHub Marketplace

ClawHub (`docs/clawhub/`) is the marketplace for OpenClaw skills and plugins:

- `openclaw skills search "calendar"` — discover
- `openclaw skills install @owner/<slug>` — install into the active workspace `skills/` (add `--global` for the shared managed directory)
- `openclaw skills update @owner/<slug>` / `openclaw skills verify @owner/<slug> --card` — update and verify provenance/scan cards
- `skills-sh:<owner>/<repo>/<slug>` references route through ClawHub's resolver and install the commit-pinned GitHub source returned
- The standalone `clawhub` CLI handles publisher workflows: login, publish, sync, transfer

## Skill Workshop

Skill Workshop (`docs/tools/skill-workshop.md`, `src/skills/workshop/`) is OpenClaw's governed path for creating and updating **workspace** skills from chat, CLI, or Gateway:

- **Proposal first** — generated content is stored as `PROPOSAL.md`, never `SKILL.md`.
- **Apply is the only live write** — create/update/revise never change active skills; updates bind to the current target hash and go `stale` if the live skill changes.
- **Scanner gated** — apply reruns the security scanner before writing; only critical findings block apply.
- **Recoverable** — apply writes rollback metadata before touching live files.
- Consistent surfaces: chat, CLI, and Gateway all call the same service.

## Bundled Skills

~50 bundled skill directories ship under `skills/` (52 entries), covering: `1password`, `apple-notes`, `apple-reminders`, `bear-notes`, `blogwatcher`, `blucli`, `camsnap`, `clawhub`, `coding-agent`, `diagram-maker`, `eightctl`, `gemini`, `gh-issues`, `gifgrep`, `github`, `gog`, `goplaces`, `healthcheck`, `himalaya`, `mcporter`, `meme-maker`, `model-usage`, `nano-pdf`, `node-connect`, `node-inspect-debugger`, `notion`, `obsidian`, `openai-whisper`, `openhue`, `oracle`, `ordercli`, `peekaboo`, `python-debugpy`, `sag`, `session-logs`, `sherpa-onnx-tts`, `skill-creator`, `songsee`, `sonoscli`, `spike`, `spotify-player`, `summarize`, `taskflow`, `taskflow-inbox-triage`, `things-mac`, `tmux`, `trello`, `video-frames`, `weather`, `xurl`.

## Code Map

The skill runtime lives in `src/skills/`:

- `config/` — skill loading configuration (`skills.*` schema, gating)
- `discovery/` — skill root discovery and scan
- `lifecycle/` — skill lifecycle state
- `loading/` — loader, precedence resolution, environment/binary filtering
- `research/` — skill research/search across roots
- `runtime/` — runtime execution of skill commands
- `security/` — skill security scanning (scanner used by Workshop apply)
- `workshop/` — Skill Workshop service (proposal lifecycle, apply, rollback)
- `types.ts` — shared skill types

Related CLI and plugin surfaces: `skills-cli.ts` under `src/cli/`, `src/plugin-sdk/skill-commands-runtime.ts`, and `docs/tools/creating-skills.md` for authoring guidance.

## Key Source Files

| File | Purpose |
|------|---------|
| `docs/tools/skills.md` | Six-tier loading precedence, gating, allowlists |
| `docs/tools/skill-workshop.md` | Workshop proposal/apply lifecycle |
| `docs/tools/creating-skills.md` | Skill authoring guide |
| `docs/clawhub/cli.md` | ClawHub install/publish CLI |
| `src/skills/loading/` | Precedence-aware skill loading |
| `src/skills/workshop/` | Skill Workshop service |
| `src/skills/security/` | Skill security scanner |
| `skills/` | ~50 bundled skills |

## Related

- [[domains/architecture/openclaw-architecture.md]] — Overall system architecture
- [[domains/plugins/openclaw-plugins.md]] — Plugin system (skills are a plugin kind)
- [[wiki/openclaw.md]] — Wiki entry
