---
name: hermes-optimization-guide-api
description: "Hermes optimization guide configuration API, tuning parameters, benchmarking endpoints, performance metrics"
source: sources/hermes-optimization-guide/
tags: [hermes-optimization-guide, api, hermes-agent, configuration]
---

# Hermes Optimization Guide API

The guide documents the Hermes Agent's **configuration and tuning API surfaces** — `config.yaml` schema, environment variables, tuning knobs, and benchmark methodology.

## Overview

No HTTP server of its own. The guide prescribes how to interact with the Hermes Agent's built-in tuning API across 7 optimization dimensions: context, cost, latency, memory, security, caching, and routing. It ships 5 opinionated config templates and an interactive config wizard.

## API Surface

**Config Schema API** — The `config.yaml` sections consumed by Hermes Agent:
- `model_router` — cost tiers, fallback chains, capability routing
- `compression` — strategy (`conservative | adaptive | aggressive`), max tokens
- `context_window` — target size (`8000–128000`), strategy (`sliding | truncate | summarize`)
- `monitoring` — Langfuse, Helicone, OpenTelemetry backends

**Environment Variable API:**
| Variable | Default | Purpose |
|----------|---------|---------|
| `HERMES_CONFIG` | `~/.hermes/config.yaml` | Config path |
| `COMPRESSION_STRATEGY` | `adaptive` | Compression preset |
| `CONTEXT_WINDOW_TARGET` | `28000` | Target token threshold |
| `BENCHMARK_OUTPUT` | `stdout` | Results destination |

**Tuning Parameter API** — 7 dimensions with documented ranges and trade-offs, including model tier routing and caching TTL (0–3600s).

**Reference Architecture Presets:**
| Architecture | Budget | Context | Latency |
|-------------|--------|---------|---------|
| Homelab | $0 | 16K | 5s |
| Solo Dev | $25-70/mo | 32K | 2s |
| Agency | $200-500/mo | 64K | 1s |
| Road Warrior | $15-30/mo | 16K | 3s |

## Authentication

No dedicated auth — tuning parameters are set via `config.yaml` (file permissions) and environment variables. The guide recommends `0600` permissions on config files.

## Usage

```bash
# Apply a config template
cp assets/config-templates/cost-optimized.yaml ~/.hermes/config.yaml

# Override via env
COMPRESSION_STRATEGY=aggressive hermes gateway run

# Run benchmark
hermes chat --benchmark code-gen --model claude-sonnet-4

# Benchmark output format
BENCHMARK_OUTPUT=json hermes chat --benchmark tool-call --model gpt-4o
```

## Related

- [[domains/api/INDEX|api]]
- [[hermes-optimization-guide]] — Full guide documentation
- [[hermes-agent]] — Target agent being optimized
- [[llmtrim]] — Context compression integration
- [[hermes-startup-architect]] — Complementary architecture guide
