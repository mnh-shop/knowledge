---
name: hermes-agent-observability
tags: [hermes-agent, langfuse, metrics, monitoring, nemo-relay, observability, otlp, telemetry, tracing]
description: "Hermes Agent observability: OTLP gateway health export, shared metrics relay, Langfuse and NeMo Relay plugins, monitoring/insights/billing CLIs"
source: sources/hermes-agent/
---

# Hermes Agent Observability

Hermes observability has three layers: (1) a **content-free gateway health &
diagnostics export** over OTLP (`hermes_cli/observability/` + `monitoring.*`
config), (2) **optional vendor plugins** for rich trace data
(`plugins/observability/` — Langfuse, NeMo Relay), and (3) **CLI surfaces**
for inspecting usage and billing (`hermes monitoring`, `hermes insights`,
`/usage`, `/subscription`).

A core design invariant: the built-in export is **content-free by
construction** — no prompts, messages, tool args/results, or usage analytics.
Anything richer is opt-in via plugins, and the repo policy forbids shipping
additional third-party-product plugins in-tree (they live in standalone plugin
repos installed into `~/.hermes/plugins/`).

## 1. Built-in OTLP Gateway Health Export

### Module Map (`hermes_cli/observability/`)

| File | Purpose |
|------|---------|
| `__init__.py` | `observe_lifecycle(hook_name, **kwargs)` — dispatches lifecycle events to built-in observability features (guarded by `_safe_observe`) |
| `relay_runtime.py` | Compatibility alias for the core Relay runtime (`agent.relay_runtime`) — kept so plugins/tests share one profile registry |
| `relay_shared_metrics.py` | Bridge: `observe_lifecycle()` → shared-metrics counters |
| `shared_metrics.py` | Durable SQLite aggregation + local export of Hermes shared metrics |
| `shared_metrics_contract.py` | Metric contract — `COUNTER_METRICS`, `MODEL_CALL_METRIC`, dimension validation |
| `shared_metrics_subscriber.py` | Subscriber side of the shared-metrics relay |
| `schemas/hermes.shared_metrics.v1.schema.json` | Versioned schema for the shared-metrics export |

`shared_metrics.py` stores counters in SQLite (`get_hermes_home()`), with a
30-day local history retention, and exports via the versioned contract.

### Configuration (`monitoring.*`)

Defined in `hermes_cli/config_defaults.py` (verified at line 2313):

```yaml
monitoring:
  install_id: ""          # stable install identifier on exported signals; empty = mint a UUID on first use; carries NO account identity
  gateway_health_export:
    enabled: false
    metrics_enabled: true
    diagnostic_events_enabled: true
    warning_error_events_enabled: true
    export_interval_seconds: 60
    logs_export_interval_seconds: 5
    resource_attributes:
      service.name: hermes-gateway
      deployment.environment.name: production
  export:
    otlp:
      enabled: false
      endpoint: ""          # OTLP collector endpoint
      headers_env: {}       # header name → ENVIRONMENT VARIABLE NAME (never secret values; read at export time)
```

Note the secret handling: `headers_env` maps header names to **env var names**,
not values, so credentials never land in `config.yaml`.

### CLI (`hermes monitoring`)

`hermes_cli/subcommands/monitoring.py` wires the tree; handler
`cmd_monitoring` lives in `hermes_cli/main.py` (line 10949):

```bash
hermes monitoring status
# Shows: export enabled/disabled, endpoint, redaction posture
```

The parser docstring states the contract: "service health metrics plus
redacted diagnostics, exported over OTLP to an operator-configured endpoint.
Content-free by construction — no prompts, messages, tool args/results, or
usage analytics. Configure under `monitoring.*` in config.yaml."

## 2. Optional Observability Plugins (`plugins/observability/`)

Both plugins are bundled but **opt-in** — they load only when explicitly
enabled, and they fail open (hooks no-op silently) when the SDK or
credentials are absent.

### Langfuse (`plugins/observability/langfuse/`)

Langfuse integration for LLM trace observability.

```bash
hermes tools                    # → Langfuse Observability (interactive)
# or manual:
pip install langfuse
hermes plugins enable observability/langfuse
```

Credentials (in `~/.hermes/.env`):

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or self-hosted
```

Files: `plugin.yaml`, `__init__.py`, `README.md`.

### NeMo Relay (`plugins/observability/nemo_relay/`)

NVIDIA NeMo Relay integration: configures exporters and maps Hermes
observer hooks to NeMo Relay marks and ATIF state. Hermes **core** owns Relay
session/turn/LLM/tool execution scopes; the plugin adds rich exporters and
observer marks for sessions, turns, approval prompts, and delegated subagents.

With the plugin enabled Hermes can:

- Export Relay scopes and LLM/tool lifecycles emitted by core.
- Add Hermes session, turn, approval, and subagent mark events.
- Export raw lifecycle events as **ATOF** (Agent Trajectory Observability
  Format) JSONL for debugging / offline inspection.
- Export **ATIF** (Agent Trajectory Interchange Format) trajectories for
  replay, evaluation, and harness analysis.
- Correlate parent sessions, delegated subagents, tool calls, and provider
  calls through shared session/turn/trajectory metadata.

Implementation: `plugins/observability/nemo_relay/__init__.py` maintains
per-runtime state (`_RUNTIMES`), registers a `_SESSION_INITIALIZER_NAME`
(`hermes.nemo_relay.rich_observability`) with `agent.relay_runtime`, and uses
`atexit` + a threading lock for clean shutdown. Files: `plugin.yaml`,
`__init__.py`, `README.md`.

## 3. CLI Usage & Billing Surfaces

### Insights (`hermes insights`)

`hermes_cli/subcommands/insights.py` wires `hermes insights` — "Show usage
insights and analytics". The handler (`cmd_insights`, `hermes_cli/main.py`
line 10935) analyzes session history to show token usage, costs, tool
patterns, and activity trends:

```bash
hermes insights                       # last 30 days
hermes insights --days 7              # shorter window
hermes insights --source telegram     # filter by platform
```

The `/insights` slash command is registered in `hermes_cli/commands.py`
(`CommandDef("insights", "Show usage insights and analytics", "Info")`).

### Usage / Subscription / Topup

Interactive CLI billing handlers live in `hermes_cli/cli_billing_mixin.py`
(billing mixin extracted from the CLI god-file). It prefers the shared dollar
usage model (`agent/billing_usage.py` → `build_usage_model()` +
`format_renews`) — a two-bar plan/top-up view, dollars-only, the source for
the `/usage` and `/subscription` slash commands:

```bash
/usage            # plan + renews + spendable balance (two-bar view)
/subscription     # plan details (free tier shows "Run /subscription to reach paid models")
/topup            # add spendable credit
```

Status lines show `plan_name`, `renews_display`, `has_topup`,
`total_spendable_usd`, and a free/low/paid status. The billing model is
account-login-gated; without a logged-in account the block degrades to a
prompt to log in.

## Docs

- `docs/observability/monitoring.md` — user-facing gateway monitoring guide.
- `docs/observability/relay-shared-metrics.md` — shared-metrics relay contract.
- `docs/observability/README.md` — observability docs index.

## Related

- [[hermes-agent-deployment]] -- `hermes monitoring status` + health checks in ops context
- [[hermes-agent-configuration]] -- `monitoring.*` config keys
- [[hermes-agent-cron]] -- Cron delivery/failure telemetry consumers
- [[hermes-agent-research-tools]] -- Trajectory formats (ATOF/ATIF) shared with data-gen tooling
