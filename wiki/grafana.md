---
name: grafana
tags: [grafana, monitoring, dashboard, observability, visualization, metrics]
description: "Open-source observability and data visualization platform"
source: sources/grafana/
---

# Grafana

| Field | Value |
|---|---|
| **Origin** | [grafana/grafana](https://github.com/grafana/grafana) |
| **Source** | `sources/grafana/` |
| **Repomix** | `raw/grafana/grafana.xml` |
| **Codegraph** | `graphs/grafana/` |

## Overview

Grafana is the leading open-source observability and data visualization platform. It provides a unified dashboarding interface for querying, visualizing, alerting on, and understanding metrics, logs, and traces regardless of where they are stored. With extensive plugin support for data sources, panels, and apps, Grafana serves as the central visualization layer in monitoring stacks across organizations of all sizes.

## Key Features

- **Unified Dashboarding** — Create, share, and manage interactive dashboards with drag-and-drop panel editing
- **Multi-Data Source Support** — Native queries for Prometheus, InfluxDB, Elasticsearch, SQL databases, CloudWatch, and 70+ other data sources
- **Alerting Engine** — Unified alerting with multi-dimensional evaluation, notification routing, and silence management
- **Explore Mode** — Ad-hoc query interface for debugging and data exploration without dashboard creation
- **Annotations** — Correlate events with metric data using event annotations from multiple sources
- **RBAC & Provisioning** — Role-based access control and dashboard-as-code provisioning via YAML/JSON

## Architecture

Grafana follows a plugin-based architecture with a core backend (Go) serving the frontend (React/TypeScript). Data sources implement a common query interface, allowing any compatible backend to plug into the visualization layer. The alerting system operates as an independent evaluation engine that can route through Grafana's notification system or external Alertmanager instances.

## Related

- [[prometheus]] — Primary metrics collection and alerting partner (PromQL support)
- [[netdata]] — Real-time infrastructure monitoring (can feed metrics to Grafana)
- [[podman]] — Container runtime for deploying Grafana instances
- [[bootc]] — Bootable OS images for running Grafana at the edge
- [[cockpit-podman]] — Web UI for managing Podman containers running Grafana
