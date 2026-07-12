---
name: prometheus
tags: [prometheus, monitoring, metrics, observability, alerting, time-series]
description: "Open-source systems monitoring and alerting toolkit with a dimensional data model"
source: sources/prometheus/
---

# Prometheus

| Field | Value |
|---|---|
| **Origin** | [prometheus/prometheus](https://github.com/prometheus/prometheus) |
| **Source** | `sources/prometheus/` |
| **Repomix** | `raw/prometheus/prometheus.xml` |
| **Codegraph** | `graphs/prometheus/` |

## Overview

Prometheus is a CNCF-graduated open-source systems monitoring and alerting toolkit originally built at SoundCloud. It collects and stores metrics as time-series data with a powerful dimensional data model, enabling flexible querying through its PromQL query language. Prometheus operates on a pull model, scraping metrics from instrumented targets at configurable intervals, and supports service discovery for dynamic environments like Kubernetes.

## Key Features

- **Dimensional Data Model** — Metrics identified by metric name and key/value label pairs for flexible aggregation
- **PromQL Query Language** — Rich functional query language for real-time metric selection, aggregation, and arithmetic
- **Pull-Based Scraping** — Server-initiated metric collection with configurable scrape intervals and targets
- **Service Discovery** — Automatic target discovery for Kubernetes, Consul, EC2, and other dynamic environments
- **Alertmanager Integration** — Configurable alerting with grouping, silencing, inhibition, and routing
- **Local Storage** — Efficient on-disk time-series storage with configurable retention and compaction

## Architecture

Prometheus follows a pull-based architecture where the Prometheus server scrapes metrics from instrumented targets (exporters, applications, and other services). Data is stored locally as time-series in a custom format optimized for fast label-based querying. Alerting rules evaluated on scraped data trigger Alertmanager for notification routing. Long-term storage or horizontal scaling can be achieved via Thanos or Cortex, which extend Prometheus with global query views and durable object storage.

## Related

- [[grafana]] — Primary visualization and dashboarding layer for Prometheus metrics
- [[netdata]] — Real-time node monitoring that can expose metrics for Prometheus scraping
- [[headroom]] — Kubernetes auto-scaling tool that uses Prometheus metrics as input
- [[k3s]] — Lightweight Kubernetes distribution commonly instrumented with Prometheus
- [[podman]] — Container runtime for deploying Prometheus instances
