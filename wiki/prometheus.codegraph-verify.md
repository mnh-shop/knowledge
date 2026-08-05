---
name: prometheus-codegraph-verify
tags: [prometheus, codegraph-verify, monitoring, metrics]
description: "Codegraph Verification: Prometheus — validating wiki claims against indexed source code symbols"
source: sources/prometheus/
---

# Codegraph Verification: Prometheus

**Date:** 2026-07-12

## Claim 1: Pull-based architecture with HTTP scraping
- **Wiki says:** Prometheus operates on a pull model, scraping metrics from instrumented targets at configurable intervals. The main server binary in `cmd/prometheus/` handles HTTP-based metric collection.
- **Source evidence:**
  - `cmd/prometheus/main.go` is the server entry point with scrape manager, rule manager, and TSDB initialization
  - `scrape/` package implements target scraping with configurable intervals and HTTP endpoints
  - `config/config.go` defines `ScrapeConfig` with `ScrapeInterval`, `ScrapeTimeout`, and target specifications
  - Targets expose metrics via HTTP endpoints following the OpenMetrics format
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Local storage with TSDB at tsdb/
- **Wiki says:** Prometheus stores metrics locally in a custom TSDB format optimized for fast label-based querying and efficient compaction, located at the `tsdb/` package.
- **Source evidence:**
  - `tsdb/db.go` implements the core TSDB database with `Open()`, `Append()`, `Querier()`, and `Snapshot()` methods
  - `tsdb/block.go` handles block-level storage with block reader/writer
  - `tsdb/compact.go` handles compaction of multiple blocks
  - `tsdb/chunkenc/` provides chunk encoding for time-series data
  - `tsdb/chunks/` provides chunk reading and writing
  - `tsdb/agent/` provides a lightweight agent-mode TSDB for forwarding data via remote write
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: PromQL query language in promql/
- **Wiki says:** PromQL is a functional query language for real-time metric selection, aggregation, arithmetic, and transformation. It lives in the `promql/` package.
- **Source evidence:**
  - `promql/engine.go` contains the query engine with `Exec()` method for parsing and evaluating PromQL expressions
  - `promql/parser/` provides the PromQL parser and lexer
  - `promql/functions.go` defines built-in functions: `rate()`, `irate()`, `increase()`, `delta()`, `histogram_quantile()`, `predict_linear()`, `deriv()`, and more
  - `promql/bench_test.go` confirms query engine benchmarking
  - `promql/promqltest/` provides unit testing utilities for PromQL queries
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Multi-source service discovery at discovery/
- **Wiki says:** Prometheus supports automatic target discovery for Kubernetes, Consul, EC2, Azure, GCE, DNS, and other dynamic environments via the `discovery/` package.
- **Source evidence:**
  - `discovery/` contains 29 service discovery providers: `kubernetes/`, `consul/`, `aws/` (EC2), `azure/`, `gce/`, `dns/`, `file/`, `http/`, `docker/` (`moby/`), `eureka/`, `digitalocean/`, `hetzner/`, `ionos/`, `linode/`, `nomad/`, `openstack/`, `outscale/`, `ovhcloud/`, `puppetdb/`, `scaleway/`, `stackit/`, `triton/`, `uyuni/`, `vultr/`, `zookeeper/`, `xds/`, `marathon/`, `targetgroup/`, plus `install/`, `refresh/`, and metrics helpers
  - `discovery/discovery.go` defines the `Discoverer` and `Provider` interfaces
  - `discovery/manager.go` manages discoverer lifecycle and target updates
  - `plugins/` holds 27 optional build-tag plugin files (`//go:build !remove_all_sd || enable_<sd>_sd`), e.g. `plugin_kubernetes.go`, `plugin_aws.go`, `plugin_dns.go`; see `CHANGELOG.md:209`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Alertmanager integration at notifier/
- **Wiki says:** Alerting rules are evaluated on scraped data and trigger Alertmanager for notification dispatch. The notifier lives in the `notifier/` package.
- **Source evidence:**
  - `notifier/alertmanager.go` implements Alertmanager client communication
  - `notifier/manager.go` provides the notification manager with send loop and retry logic
  - `notifier/alert.go` defines alert data structures
  - `notifier/sendloop.go` implements the send loop for pushing alerts to Alertmanager
  - `notifier/metric.go` exposes notifier metrics for monitoring
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Dimensional data model at model/
- **Wiki says:** The multi-dimensional data model identifies time series by metric name and key/value label pairs. This lives in the `model/` and `labels/` packages.
- **Source evidence:**
  - `model/labels/` provides label matching, selection, and manipulation
  - `model/value/` defines value types including float, histogram, and exemplar
  - `model/histogram/` implements native histogram types
  - `model/textparse/` provides OpenMetrics text format parsing
  - `model/relabel/` provides relabeling functionality for target and metric manipulation
  - `model/metadata/` handles metric metadata
  - `model/exemplar/` provides exemplar support for trace-metric correlation
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: CLI tooling (promtool) and remote read/write (storage/remote)
- **Wiki says:** `cmd/promtool/` ships CLI tooling for config checking, rule validation, querying, and TSDB debugging; `storage/remote/` implements the remote read/write protocol for long-term storage and agent-mode forwarding.
- **Source evidence:**
  - `cmd/promtool/` contains the promtool CLI: `main.go`, `rules.go` (rule check/test), `config.go` (config check), `query.go` (server queries), `tsdb.go` (TSDB admin/debug commands)
  - `storage/remote/` implements remote read/write endpoints: `storage.go` (RemoteStorage with Write/ReadQueues), `write_handler.go` (`/api/v1/write`), `read_handler.go` (`/api/v1/read`), `queue_manager.go` (sharded write queue), `client.go` (remote client), `generic.go` (generic read/write with exemplars/histograms)
  - Agent-mode forwarding uses `storage/remote` + `tsdb/agent/`; agent mode flag at `cmd/prometheus/main.go:146` (`agentMode`), documented in `docs/prometheus_agent.md`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Web UI — react-app and mantine-ui (v3) in a pnpm workspace
- **Wiki says:** The web UI lives under `web/ui/` as a pnpm workspace with the established `react-app` and a `mantine-ui` v3 rewrite shipping alongside it.
- **Source evidence:**
  - `web/ui/` contains `react-app/`, `mantine-ui/`, `pnpm-workspace.yaml`, `package.json`, `pnpm-lock.yaml`, and `build_ui.sh` — confirming a pnpm workspace
  - `web/ui/react-app/` is the TypeScript/React UI (expression browser, targets, alerts pages) with `web/ui/react-app/src/`
  - `web/ui/mantine-ui/` is the v3 Mantine-based rewrite, embedded alongside react-app
  - `web/ui/ui.go` and `web/ui/assets_embed.go` embed the built UI into the Go binary
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the Prometheus wiki have been verified against the source code via directory exploration:
- ✅ Pull-based architecture: HTTP scraping via `scrape/`, `config/`, and `cmd/prometheus/` confirmed
- ✅ Local TSDB storage: `tsdb/` with block-based compaction and chunk encoding confirmed
- ✅ PromQL query language: `promql/` with parser, engine, and built-in functions confirmed
- ✅ Service discovery: 29 providers in `discovery/` with optional build-tag plugins confirmed
- ✅ Alertmanager integration: `notifier/` with alert dispatch and send loop confirmed
- ✅ Dimensional data model: `model/` and `labels/` packages confirmed
- ✅ CLI tooling (`cmd/promtool/`) and remote read/write (`storage/remote/`) confirmed
- ✅ Web UI: `react-app` + `mantine-ui` v3 in a pnpm workspace confirmed

## Related

- [[prometheus]] -- Main wiki entry
- [[prometheus-architecture]] -- Deep-dive into architecture
- [[prometheus-deployment]] -- Deployment guide

## Cross-project

- [[grafana.codegraph-verify]] -- Similar codegraph verification for Grafana
- [[netdata.codegraph-verify]] -- Similar codegraph verification for Netdata
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
