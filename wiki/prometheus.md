---
name: prometheus
tags: [prometheus, monitoring, metrics, observability, alerting, time-series, cncf, promql]
description: "CNCF-graduated open-source systems monitoring and alerting toolkit with a dimensional data model"
source: sources/prometheus/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Prometheus

| Field | Value |
|---|---|
| **Origin** | [prometheus/prometheus](https://github.com/prometheus/prometheus) |
| **License** | Apache-2.0 |
| **Stack** | Go (core), TypeScript/React (UI), Go (exporters ecosystem) |
| **Source** | `sources/prometheus/` |
| **Repomix** | `raw/prometheus/prometheus.xml` |
| **Codegraph** | `graphs/prometheus/` |

## Overview

Prometheus is a CNCF-graduated open-source systems monitoring and alerting toolkit originally built at SoundCloud. It collects and stores metrics as time-series data with a powerful dimensional data model, enabling flexible querying through its PromQL query language. Prometheus operates on a pull model, scraping metrics from instrumented targets at configurable intervals, and supports service discovery for dynamic environments like Kubernetes.

Prometheus is distinguished from other monitoring systems by its **multi-dimensional data model** (time series defined by metric name and set of key/value label pairs), **PromQL** — a powerful and flexible functional query language that leverages dimensionality, **no dependency on distributed storage** (single server nodes are autonomous), an **HTTP pull model** for time-series collection, **service discovery** for dynamic target management, and support for **hierarchical and horizontal federation**. Pushing time series is supported via an intermediary gateway for batch jobs.

The project is a [Cloud Native Computing Foundation](https://cncf.io/) graduated project and follows strict governance with maintainer-reviewed contributions, DCO sign-off requirements, and semantic release versioning.

## Key Features

- **Dimensional Data Model** — Metrics identified by metric name and key/value label pairs for flexible aggregation. Time series are uniquely identified by their metric name and optional label pairs.
- **PromQL Query Language** — Rich functional query language for real-time metric selection, aggregation, arithmetic, and transformation. Supports range vectors, instant vectors, subqueries, and built-in functions for rate, histogram quantization, and more.
- **Pull-Based Scraping** — Server-initiated metric collection with configurable scrape intervals and targets. Targets expose metrics via HTTP endpoints following the OpenMetrics format.
- **Service Discovery** — Automatic target discovery for Kubernetes, Consul, EC2, Azure, GCE, DNS, and other dynamic environments. Supports static configuration, file-based service discovery, and HTTP-based discovery. Service discovery plugins are bundled as optional build-time components using Go build tags.
- **Alertmanager Integration** — Configurable alerting with grouping, silencing, inhibition, and routing. Alerting rules are evaluated on scraped data and trigger Alertmanager for notification dispatch.
- **Local Storage** — Efficient on-disk time-series storage with configurable retention and compaction. Custom storage format optimized for fast label-based querying.
- **Federation** — Hierarchical federation allows one Prometheus server to scrape selected time series from another Prometheus server, enabling multi-level aggregation and global views.
- **Graphing & Dashboarding** — Built-in expression browser and multiple dashboarding options through integration with [[grafana]] and other visualization tools.
- **Push Gateway** — Standalone intermediary service that accepts pushed metrics from batch jobs and short-lived processes, making them available for Prometheus scraping.

## Architecture

Prometheus follows a pull-based architecture. The Prometheus server scrapes metrics from instrumented targets (exporters, applications, and other services) over HTTP. Data is stored locally as time series in a custom, highly optimized format designed for fast label-based querying and efficient compaction.

```
Prometheus Server ──scrape──> Targets (exporters, applications)
       │
       ├──> Local Storage (TSDB with configurable retention)
       ├──> Recording/Alerting Rules ──> Alertmanager
       ├──> PromQL Queries (expression browser / Grafana)
       └──> Federation (remote read/write, hierarchical)
```

Alerting rules evaluated on scraped data trigger Alertmanager for notification routing through email, Slack, PagerDuty, OpsGenie, webhook, and custom receivers. Long-term storage or horizontal scaling can be achieved via Thanos or Cortex, which extend Prometheus with global query views, durable object storage, and cross-cluster aggregation.

The server binary includes an optional agent mode that reduces the footprint by omitting querying, alerting, and local storage — forwarding scraped data via remote write instead. Service discovery plugins are modular and controllable via Go build tags (`remove_all_sd`, `enable_kubernetes_sd`, etc.).

## PromQL Query Language

PromQL is the functional query language at the heart of Prometheus. It supports:

- **Instant vectors** — query a single point in time: `http_requests_total{job="api"}`
- **Range vectors** — query a time window: `http_requests_total[5m]`
- **Aggregation operators** — `sum()`, `avg()`, `min()`, `max()`, `count()`, `quantile()`, `topk()`, `bottomk()`
- **Rate & delta functions** — `rate()`, `irate()`, `increase()`, `delta()`, `deriv()`, `predict_linear()`
- **Histogram operations** — `histogram_quantile()`, bucket trimming, and native histogram support
- **Binary & comparison operators** — arithmetic, boolean filtering, vector matching

PromQL is used both in ad-hoc queries (Grafana dashboards, expression browser) and within recording and alerting rules.

## Usage / Integration

Prometheus serves as the foundational metrics layer in the monitoring stack:

- **Visualized via [[grafana]]** — Grafana provides full PromQL support with query auto-completion, template variables, and dashboard annotations for Prometheus metrics.
- **Monitored with [[netdata]]** — Netdata nodes can expose metrics in Prometheus-compatible format for Prometheus scraping, combining real-time per-second metrics with Prometheus's pull model.
- **Kubernetes monitoring** — Deploy Prometheus on [[k3s]] for lightweight edge Kubernetes monitoring or on full K8s clusters via the Prometheus Operator helm chart.
- **Auto-scaling input** — [[headroom]] consumption optimization tools can use Prometheus metrics as input for scaling decisions.
- **Container deployment** — Run Prometheus via [[podman]] using the official `prom/prometheus` image for lightweight monitoring deployments.
- **Edge deployments** — Prometheus agent mode pairs with [[bootc]]-based edge devices for low-footprint metric collection with remote write to central storage.

Standard exporters include `node_exporter` (system metrics), `blackbox_exporter` (network probes), `process_exporter`, and application-level exporters for databases, message queues, and web servers.

## Related

- [[grafana]] — Primary visualization and dashboarding layer for Prometheus metrics
- [[netdata]] — Real-time node monitoring that can expose Prometheus-compatible metrics
- [[headroom]] — AI context compression layer that integrates with Prometheus-backed agents
- [[k3s]] — Lightweight Kubernetes distribution commonly instrumented with Prometheus
- [[podman]] — Container runtime for deploying Prometheus instances
- [[bootc]] — Bootable container OS for running Prometheus at the edge
- [[mission-control]] — Centralized observability management coordinating Prometheus-based monitoring
