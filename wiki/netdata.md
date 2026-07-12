---
name: netdata
tags: [netdata, monitoring, observability, infrastructure, real-time, metrics]
description: "Real-time infrastructure monitoring and troubleshooting platform"
source: sources/netdata/
---

# Netdata

| Field | Value |
|---|---|
| **Origin** | [netdata/netdata](https://github.com/netdata/netdata) |
| **License** | GPL-3.0 |
| **Stack** | C (agent), TypeScript/React (dashboard), Go (cloud) |
| **Source** | `sources/netdata/` |
| **Repomix** | `raw/netdata/netdata.xml` |
| **Codegraph** | `graphs/netdata/` |

## Overview

Netdata is a real-time infrastructure monitoring and troubleshooting platform that provides high-resolution metrics (down to 1-second granularity) for every component of a system — CPU, memory, disk, network, processes, containers, and applications. It combines a performance-optimized, zero-configuration monitoring agent with a rich, interactive dashboard and a cloud-based observability backend.

## Key Features

- **Zero-Configuration Monitoring** — Install and immediately see thousands of metrics with auto-detection of services (nginx, PostgreSQL, Redis, etc.)
- **High-Resolution Metrics** — 1-second granularity for real-time troubleshooting and forensic analysis
- **Interactive Dashboard** — Rich, responsive dashboard with charts, heatmaps, and topology views
- **Alerting Engine** — Customizable alarms with dynamic thresholds and multiple notification methods (email, Slack, PagerDuty, webhook)
- **Distributed Architecture** — Each node runs its own monitoring agent; Netdata Cloud provides centralized multi-node views
- **Anomaly Detection** — Machine learning-based anomaly detection on metric streams
- **Low Overhead** — ~1% CPU usage per core on a typical system, designed to run alongside production workloads

## Architecture

Netdata follows a distributed-agent model. Each monitored host runs the Netdata agent (written in C for performance), which collects metrics via plugins (procfs, eBPF, cgroups, service APIs). The agent serves metrics through an HTTP endpoint for the local dashboard or streams them to Netdata Cloud for centralized access. The cloud layer provides multi-node aggregation, long-term storage, team access controls, and cross-node dashboards.

## Related

- [[grafana]] — Alternative visualization platform (can also ingest Netdata metrics)
- [[prometheus]] — Metrics collection and alerting (pull-based, complementary approach)
- [[headroom]] — Auto-scaling decisions based on infrastructure metrics
- [[hermes-agent]] — Can report agent performance metrics through Netdata
