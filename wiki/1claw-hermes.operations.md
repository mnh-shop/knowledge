---
name: 1claw-hermes.operations
description: "Operations companion for 1claw-hermes — Shroud sidecar process management (systemd/launchd/tmux/Docker), the two-process model with APIConnectionError troubleshooting, dotenv resolution order, scripts/ templates, and the corrected 23-format CMO catalog"
source: sources/1claw-hermes/
parent: 1claw-hermes
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [1claw-hermes, hermes-agent, shroud, sidecar, systemd, launchd, operations, cmo, dotenv]
---

# 1claw-hermes — Operations Companion

Companion to [[1claw-hermes]]. This is the operational playbook for keeping the 1Claw integration alive in production: running the Shroud sidecar as a supervised service, understanding the two-process failure mode, resolving `.env` paths, and the corrected CMO format catalog.

## The Two-Process Model

Hermes and the Shroud sidecar are **two different processes**.

- `pnpm setup` patches `~/.hermes/config.yaml` so Hermes uses `model.provider: custom` and `model.base_url: http://127.0.0.1:8080/v1`.
- **Hermes does not start or supervise the sidecar** (README:143-149). Restart Hermes or the machine and nothing listens on 8080 → chat fails with `APIConnectionError` / connection refused until the sidecar is up again.
- Quick fix after a restart: `pnpm shroud` (or `pnpm setup`) from the `1claw-hermes` package directory.
- Long-running setup: put the sidecar under a process manager (below).

**Also read:** Shroud does **not** turn on by itself (README:3). Either run the sidecar in front of Hermes or call `createShroudClient()` from TypeScript. `SHROUD_PROVIDER` only affects `createShroudClient()`; the Hermes+sidecar path uses `ONECLAW_DEFAULT_PROVIDER` on the **sidecar** process.

## Sidecar Process Management

Both Linux and macOS run the same `pnpm shroud` / `node dist/shroud/sidecar.js` stack — only the process manager differs (README:151-177):

| Approach | When to use | Key detail |
|----------|-------------|------------|
| **systemd (user)** | Linux server/desktop | Start on login/boot, restart on crash. Needs `loginctl enable-linger "$USER"` to boot without interactive login |
| **launchd** | macOS dev Mac | LaunchAgent with `RunAtLoad` + `KeepAlive` |
| **tmux / screen** | Either OS | Quick manual persistence, no system service |
| **Docker / compose** | Either OS | When services already run in containers |

### Linux (systemd user unit)

```bash
cd packages/1claw-hermes && pnpm install && pnpm build
cp scripts/shroud-sidecar.service.example ~/.config/systemd/user/1claw-shroud-sidecar.service
# edit WorkingDirectory=%h/path/to/1claw/packages/1claw-hermes,
#      ExecStart node path, Environment= lines (ONECLAW_DEFAULT_PROVIDER, ONECLAW_ENV_FILE)
systemctl --user daemon-reload
systemctl --user enable --now 1claw-shroud-sidecar.service
loginctl enable-linger "$USER"        # boot without interactive login
curl -s http://127.0.0.1:8080/healthz # expect ok
```

The unit runs `node dist/shroud/sidecar.js` (same as `pnpm shroud`): it loads `.env`, may append `ONECLAW_AGENT_ID`, then spawns the `shroud-sidecar` binary.

### macOS (launchd LaunchAgent)

```bash
cd packages/1claw-hermes && pnpm install && pnpm build
cp scripts/shroud-sidecar.launchd.plist.example ~/Library/LaunchAgents/com.1claw.shroud-sidecar.plist
# edit WorkingDirectory, ProgramArguments[0] (which node), ONECLAW_ENV_FILE;
# create log files: touch ~/Library/Logs/1claw-shroud-sidecar.{stdout,stderr}.log
launchctl load ~/Library/LaunchAgents/com.1claw.shroud-sidecar.plist
launchctl start com.1claw.shroud-sidecar
curl -s http://127.0.0.1:8080/healthz
```

## Dotenv Resolution Order

`pnpm setup` and `pnpm shroud` resolve credentials in this order (README:181-186):

1. **CLI flag:** `--env-path` (setup) or `--env-file` (shroud)
2. **Environment variable:** `ONECLAW_ENV_FILE=/absolute/path/.env`
3. **cwd walk:** walk the current working directory upward until a `.env` is found (so `cd ~/hermes/.../1claw-hermes && pnpm shroud` works with no flags)
4. **Package fallback:** `packages/1claw-hermes/.env` next to the package

**Gotcha:** the Go `shroud-sidecar` binary does **not** read `.env` files (README:188). Either run it via `pnpm shroud` (Node loads the file and passes env vars to the child) or `set -a; source /path/.env; set +a` before invoking `./shroud-sidecar` directly. `pnpm shroud` may auto-append `ONECLAW_AGENT_ID` to older `.env` files that only contain the `ocv_` key — required by the raw binary.

## Troubleshooting Matrix (README:238-248)

| Symptom | Cause | Fix |
|---------|-------|-----|
| `APIConnectionError` / "Connection error" to `http://localhost:8080/v1` | Sidecar not running, wrong port, or Hermes + sidecar on different hosts (VM/Docker without port publish) | Run `pnpm shroud` in another terminal, or `pnpm setup` to do everything |
| Putting `SHROUD_PROVIDER` under `mcp_servers.oneclaw.env` | That block configures **only the MCP subprocess** (secrets/tools) — not Hermes's model HTTP client | Set provider on the **sidecar process** (`ONECLAW_DEFAULT_PROVIDER`) or via `pnpm setup --provider` |
| MCP works, chat fails | Expected: two different processes — MCP has env from YAML; LLM uses `model.base_url` only | The sidecar must be running for LLM traffic |

**Docker note (README:246-248):** if Hermes runs inside a container, `localhost:8080` is inside that container. Run the sidecar in the same network namespace, publish `8080:8080`, or point `base_url` at `host.docker.internal:8080` (or the host IP).

## scripts/ Templates

- **`shroud-sidecar.service.example`** — systemd user unit: `Type=simple`, `WorkingDirectory=%h/.../1claw-hermes`, `ExecStart=/usr/bin/node dist/shroud/sidecar.js`, `Environment=ONECLAW_DEFAULT_PROVIDER=google` (+ optional `ONECLAW_ENV_FILE`), `Restart=always`, `RestartSec=5`, `WantedBy=default.target`. Header comments walk the 5-step install.
- **`shroud-sidecar.launchd.plist.example`** — LaunchAgent `com.1claw.shroud-sidecar`: `RunAtLoad` + `KeepAlive`, `ProgramArguments` = [`/usr/local/bin/node`, `dist/shroud/sidecar.js`], `EnvironmentVariables` (NODE_ENV, ONECLAW_DEFAULT_PROVIDER, ONECLAW_ENV_FILE), `StandardOutPath`/`StandardErrorPath` logs.

## CMO Format Catalog (corrected — 23 formats)

The `CmoPostFormat` union (`src/talents/cmo/draft-generator.ts:11-36`) has **23** members, not 26:

**gitlawb-style (13):** `newsdrop`, `stats`, `qt`, `qt-bigissue`, `milestone`, `release`, `dogfood`, `poll`, `shoutout`, `rally`, `thread`, `journal-cta`, `ugc-repost`

> `qt-bigissue` (3-paragraph claim → why → product-anchor QT) was the format missing from the earlier wiki count.

**1clawai / Bankr-ecosystem (9):** `holder-milestone`, `onchain-stats`, `listing-news`, `reference-demo`, `editorial-coverage`, `ecosystem-partner`, `essay`, `stack-diagram`, `bankr-amplified`

**Auto (1):** `auto` — model picks based on topic.

Campaign themes (`campaign.md`): **Week 1 (Days 1-7): Build the wedge artifact** — "ship the reference agent" (the 4-layer loop demo: DID via 1Claw HSM → push to GitLawb → LLM through Shroud → Bankr mint → Intents-signed swaps); Week 2 outreach + ecosystem; Week 3 distribution + volume; Week 4 manufactured inflection.

## Related

- [[1claw-hermes]] — Main wiki entry
- [[1claw-hermes.codegraph-verify]] — Source-verified claims
- [[hermes-agent]] — Parent project for secrets integration
- [[mcp]] — Model Context Protocol
- [[hermes-workspace]] — Hermes workspace tooling
