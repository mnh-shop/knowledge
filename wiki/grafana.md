---
name: grafana
tags: [grafana, monitoring, dashboard, observability, visualization, metrics, logs, alerting]
description: "Open-source observability and data visualization platform"
source: sources/grafana/
verification_date: 2026-07-12
verified_by: codegraph-verify
source_reference: sources/grafana/README.md, sources/grafana/AGENTS.md
---

# Grafana

| Field | Value |
|---|---|
| **Origin** | [grafana/grafana](https://github.com/grafana/grafana) |
| **License** | AGPL-3.0 (with Apache-2.0 exceptions) |
| **Stack** | Go (backend), TypeScript/React (frontend), CUE (schemas) |
| **Source** | `sources/grafana/` |
| **Repomix** | `raw/grafana/grafana.xml` |
| **Codegraph** | `graphs/grafana/` |

## Overview

Grafana is the leading open-source observability and data visualization platform. It provides a unified dashboarding interface for querying, visualizing, alerting on, and understanding metrics, logs, and traces regardless of where they are stored. With extensive plugin support for data sources, panels, and apps, Grafana serves as the central visualization layer in monitoring stacks across organizations of all sizes.

The project follows a plugin-based architecture with a core backend written in Go serving a TypeScript/React frontend in a monorepo using Yarn workspaces (frontend) and Go workspaces (backend). Data sources implement a common query interface, allowing any compatible backend to plug into the visualization layer. The alerting system operates as an independent evaluation engine that can route through Grafana's notification system or external Alertmanager instances.

Grafana is built for a data-driven culture: it allows users to create, explore, and share dashboards with their team. The platform supports template variables that appear as dropdowns for dynamic, reusable dashboards, and provides an Explore mode for ad-hoc querying and debugging without dashboard creation.

## Key Features

- **Unified Dashboarding** — Create, share, and manage interactive dashboards with drag-and-drop panel editing. Supports template variables for dynamic dashboards that adapt to different environments.
- **Multi-Data Source Support** — Native queries for Prometheus, InfluxDB, Elasticsearch, SQL databases (PostgreSQL, MySQL, SQLite), CloudWatch, Loki, Tempo, and 70+ other data sources through plugin architecture.
- **Alerting Engine** — Unified alerting with multi-dimensional evaluation, notification routing, silence management, and group notification. Visually define alert rules for important metrics with Slack, PagerDuty, VictorOps, and OpsGenie integrations.
- **Explore Mode** — Ad-hoc query interface for debugging and data exploration without dashboard creation. Split view compares different time ranges, queries, and data sources side by side.
- **Logs & Traces** — Seamless switching from metrics to logs with preserved label filters. Quick search through logs or streaming live. Native Tempo and Jaeger tracing support.
- **Mixed Data Sources** — Combine different data sources in the same graph on a per-query basis, enabling correlation across systems.
- **RBAC & Provisioning** — Role-based access control and dashboard-as-code provisioning via YAML/JSON configuration files.
- **Annotations** — Correlate events with metric data using event annotations from multiple sources.
- **Frontend** — Fast and flexible client-side graphs with a multitude of panel plugin options. Built with Emotion CSS-in-JS via `useStyles2`, Redux Toolkit, and React Testing Library.

## Architecture

Grafana uses a plugin-based architecture. The Go backend (structured under `pkg/`) handles the HTTP API, business logic (alerting, dashboards, auth), time-series database query backends, the plugin system, and configuration management. The TypeScript/React frontend (under `public/app/`) provides the UI layer with Redux Toolkit state management, RTK Query for data fetching, and shared packages (`@grafana/data`, `@grafana/ui`, `@grafana/runtime`, `@grafana/schema`).

| Backend Layer (`pkg/`) | Purpose |
|---|---|
| `pkg/api/` | HTTP API handlers and routes |
| `pkg/services/` | Business logic by domain (alerting, dashboards, auth) |
| `pkg/server/` | Server initialization and Wire DI setup |
| `pkg/tsdb/` | Time-series database query backends |
| `pkg/plugins/` | Plugin system and loader |
| `pkg/infra/` | Logging, metrics, database access |

The alerting system can operate independently and supports multi-dimensional rule evaluation, notification routing through Grafana's notification system or external Alertmanager instances. Schema definitions use CUE language (in `kinds/`) to generate both Go and TypeScript type definitions.

## Deployment & Configuration

Grafana can be deployed via Docker (`grafana/grafana`), Kubernetes Helm charts, bare-metal binary, or as a bootc container image. Default configuration uses embedded SQLite; production deployments typically use PostgreSQL. Configuration defaults live in `conf/defaults.ini` with overrides in `conf/custom.ini`. The Makefile provides targets for building backend (`make build-backend`), running with hot reload (`make run`), and building frontend (`yarn build`).

## Usage / Integration

Grafana integrates with the monitoring ecosystem at multiple levels:

- **As visualization layer** for [[prometheus]] — queries metrics via PromQL with full auto-completion and dashboard templates.
- **As dashboard frontend** for [[netdata]] — can ingest Netdata metrics via Prometheus scrape endpoint or directly through data source plugins.
- **With container runtimes** — deploy Grafana via [[podman]] or Docker with persistent storage for dashboards and configuration.
- **As edge monitoring** — run Grafana as a bootc container on [[bootc]]-based systems for local observability at remote sites.
- **With Cockpit** — manage Grafana containers through [[cockpit-podman]] web UI for container lifecycle management.

Grafana is also commonly paired with Loki for logs, Tempo for traces, and supports plugin-based data sources that can be provisioned declaratively. Built-in plugins include Loki, Jaeger, Pyroscope, Postgres, MySQL, and test data sources.

## Related

- [[prometheus]] — Primary metrics collection and alerting partner (PromQL support, native data source)
- [[netdata]] — Real-time infrastructure monitoring that can send metrics to Grafana via Prometheus endpoint
- [[podman]] — Container runtime for deploying Grafana instances in production
- [[bootc]] — Bootable OS images for running Grafana at the edge
- [[cockpit-podman]] — Web UI for managing Podman containers running Grafana
- [[mission-control]] — Observability management layer that coordinates with Grafana dashboards
- [[prometheus]] — Alertmanager integration for alert notification routing
- [[k3s]] — Lightweight Kubernetes for orchestrating Grafana at the edge
