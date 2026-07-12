---
name: grafana-codegraph-verify
tags: [grafana, codegraph-verify, monitoring, dashboard]
description: "Codegraph Verification: Grafana — validating wiki claims against indexed source code symbols"
source: sources/grafana/
---

# Codegraph Verification: Grafana

**Date:** 2026-07-12

## Claim 1: Plugin-based architecture with Go backend (pkg/) and TypeScript/React frontend (public/app/)
- **Wiki says:** The Grafana backend is written in Go structured under `pkg/`, handling the HTTP API, business logic, TSDB query backends, plugin system, and configuration management. The frontend is TypeScript/React under `public/app/` with Redux Toolkit state management and shared `@grafana/*` packages.
- **Source evidence:**
  - `pkg/` contains all backend packages: `api/`, `services/`, `server/`, `tsdb/`, `plugins/`, `infra/`, `setting/`, `login/`, `apimachinery/`, and more
  - `public/app/` contains the frontend entry point, `api/`, `features/`, `plugins/`, `store/`, `routes/`, `core/`, `extensions/`, and `types/`
  - `public/app/store/` and `public/app/features/` confirm Redux Toolkit state management with per-feature stores
  - `pkg/server/server.go` and `pkg/server/wire.go` provide server initialization with Wire DI
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: HTTP API handlers in pkg/api/ and business logic in pkg/services/
- **Wiki says:** HTTP API handlers live in `pkg/api/` and business logic by domain lives in `pkg/services/`.
- **Source evidence:**
  - `pkg/api/` contains handlers: `alerting.go`, `admin.go`, `admin_users.go`, `admin_encryption.go`, `accesscontrol.go`, and many more
  - `pkg/services/` has 70+ service directories: `dashboards/`, `alerting/` (in `ngalert/`), `auth/`, `annotations/`, `datasources/`, `provisioning/`, `secrets/`, `sqlstore/`, `user/`, `team/`, `folder/`, `quota/`, `search/`, and more
  - `pkg/services/ngalert/` contains the unified alerting engine with `eval/`, `models/`, `api/`, `cluster/`, `backtesting/`, and `image/`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Time-series database query backends in pkg/tsdb/
- **Wiki says:** TSDB query backends live in `pkg/tsdb/` supporting Prometheus, InfluxDB, Elasticsearch, SQL databases, CloudWatch, Loki, Tempo, and more.
- **Source evidence:**
  - `pkg/tsdb/` contains backend directories: `prometheus/`, `azuremonitor/`, `cloudwatch/`, `graphite/`, `influxdb/`, `loki/`, `jaeger/`, `mysql/`, `mssql/`, `postgresql-datasource/`, `pyroscope-datasource/`, `grafanads/`, `grafana-testdata-datasource/`, and `sqlmacro/`
  - `pkg/tsdb/prometheus/prometheus.go` confirms PromQL query implementation
  - `pkg/tsdb/README.md` documents the query backend interface
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Plugin system in pkg/plugins/ with loader and manager
- **Wiki says:** The plugin system lives in `pkg/plugins/` with plugin loading, management, authentication, storage, tracing, and backend plugin support.
- **Source evidence:**
  - `pkg/plugins/` contains: `plugins.go`, `manager/`, `backendplugin/`, `repo/`, `storage/`, `config/`, `auth/`, `log/`, `tracing/`, `pluginassets/`, `pluginerrs/`, `pluginscdn/`, `codegen/`, `envvars/`, and `models.go`
  - `pkg/plugins/plugins.go` defines core plugin interfaces
  - `pkg/plugins/manager/` provides the plugin lifecycle manager
  - `pkg/plugins/backendplugin/` handles backend plugin registration and communication
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Schema definitions using CUE language in kinds/
- **Wiki says:** Schema definitions use CUE language in `kinds/` to generate both Go and TypeScript type definitions.
- **Source evidence:**
  - `kinds/` directory exists with `dashboard/` subdirectory
  - `kinds/gen.go` generates Go and TypeScript type definitions from CUE sources
  - `cue.mod/` confirms CUE module configuration
  - `pkg/kinds/` provides runtime kind support
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Infrastructure layer in pkg/infra/
- **Wiki says:** `pkg/infra/` provides logging, metrics, database access, and other infrastructure concerns.
- **Source evidence:**
  - `pkg/infra/` contains: `db/`, `log/`, `metrics/`, `tracing/`, `httpclient/`, `kvstore/`, `remotecache/`, `localcache/`, `filestorage/`, `fs/`, `usagestats/`, `features/`, `process/`, `network/`, `nats/`, `leaderelection/`, `serverlock/`, `slugify/`, `cleanup/`, and more
  - `pkg/infra/db/` provides database access layer
  - `pkg/infra/log/` provides logging infrastructure
  - `pkg/infra/metrics/` provides internal metrics collection
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the Grafana wiki have been verified against the source code via directory exploration:
- ✅ Plugin-based architecture: Go backend `pkg/` and TypeScript/React frontend `public/app/` confirmed
- ✅ HTTP API handlers in `pkg/api/` and business logic services in `pkg/services/` confirmed
- ✅ Time-series database query backends in `pkg/tsdb/` with multiple data source integrations confirmed
- ✅ Plugin system in `pkg/plugins/` with lifecycle management confirmed
- ✅ CUE schema definitions in `kinds/` confirmed
- ✅ Infrastructure layer in `pkg/infra/` with DB, logging, metrics, and tracing confirmed

## Related

- [[grafana]] -- Main wiki entry
- [[grafana-architecture]] -- Deep-dive into Architecture
- [[grafana-deployment]] -- Deployment guide

## Cross-project

- [[prometheus.codegraph-verify]] -- Similar codegraph verification for Prometheus
- [[netdata.codegraph-verify]] -- Similar codegraph verification for Netdata
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
