---
name: netdata
tags: [netdata, monitoring, observability, infrastructure, real-time, metrics, ml, kubernetes]
description: "Real-time infrastructure monitoring and troubleshooting platform with per-second metrics and ML-powered anomaly detection"
source: sources/netdata/
verification_date: 2026-07-12
verified_by: codegraph-verify
source_reference: sources/netdata/README.md, sources/netdata/AGENTS.md
---

# Netdata

| Field | Value |
|---|---|
| **Origin** | [netdata/netdata](https://github.com/netdata/netdata) |
| **License** | GPL-3.0 (agent), NCUL1 (UI), proprietary (Cloud) |
| **Stack** | C (agent), TypeScript/React (dashboard), Go (cloud), Python (plugins) |
| **Source** | `sources/netdata/` |
| **Repomix** | `raw/netdata/netdata.xml` |
| **Codegraph** | `graphs/netdata/` |

## Overview

Netdata is an open-source, real-time infrastructure monitoring platform that provides high-resolution metrics (down to 1-second granularity) for every component of a system — CPU, memory, disk, network, processes, containers, and applications. It combines a performance-optimized, zero-configuration monitoring agent written in C with a rich, interactive dashboard, ML-powered anomaly detection, and a cloud-based observability backend.

According to a University of Amsterdam study, Netdata is the most energy-efficient tool for monitoring Docker-based systems, excelling in CPU usage, RAM usage, and execution time compared to other monitoring solutions. With under 1% CPU usage per core and ~100MiB RAM (measured with ML and alerts disabled and using ephemeral storage — README.md:310), it is designed to run alongside production workloads with minimal overhead.

Netdata provides **instant insights** with per-second metrics and visualizations, **zero configuration** deployment, **ML-powered anomaly detection** that trains multiple models per metric at the edge, and a **distributed** architecture where each node runs its own monitoring agent and data is never centralized unless explicitly streamed to Netdata Cloud.

## Key Features

- **Zero-Configuration Monitoring** — Install and immediately see thousands of metrics with auto-detection of services (nginx, PostgreSQL, Redis, MongoDB, Apache, and hundreds more).
- **High-Resolution Metrics** — 1-second granularity for real-time troubleshooting and forensic analysis. ~0.5 bytes per sample with tiered storage for long-term retention.
- **Interactive Dashboard** — Rich, responsive dashboard with charts, heatmaps, and topology views. Slice and dice data without a query language.
- **Alerting Engine** — Customizable alarms with dynamic thresholds and multiple notification methods (email, Slack, PagerDuty, webhook). Per-second alert evaluation.
- **ML-Powered Anomaly Detection** — Unsupervised anomaly detection using multiple ML models trained per metric at the edge. Detects anomalies, predicts issues, and automates analysis.
- **Distributed Architecture** — Each node runs its own monitoring agent; Netdata Cloud provides centralized multi-node views without centralizing metric storage. Parent-Child centralization supports multi-million samples per second.
- **Comprehensive Visibility** — From infrastructure (CPU, memory, disk, network, hardware sensors) to applications (nginx, Apache, postgres, redis, mongodb, and hundreds more).
- **Container & Kubernetes Monitoring** — Native support for Docker, containerd, LXC/LXD, and Kubernetes (via cgroups, kubelet, and Prometheus endpoints).
- **Extreme Scalability** — Native horizontal scaling via parent-child streaming architecture supporting millions of samples per second.
- **Low Overhead** — <1% CPU per core and ~100MiB RAM when ML and alerts are disabled and ephemeral storage is used (README.md:310), designed for production deployment alongside workloads.
- **Logs Monitoring** — systemd-journal, Windows Event Log, and ETW log collection and visualization.
- **Cloud Provider Support** — AWS, GCP, Azure, and more infrastructure monitoring.
- **Synthetic Checks** — Test APIs, TCP ports, Ping, Certificates, and more.
- **Custom Applications** — OpenMetrics and StatsD support for custom application instrumentation.
- **OpenTelemetry (Rust)** — Native OTLP ingestion via the `src/crates/` Rust workspace: `otel-ingestor` (OTLP intake) and `otel-ledger` (ledger processing), alongside `sfsq`, `netipc`, and supporting `opentelemetry` crates.

## Architecture

Netdata follows a distributed-agent model. Each monitored host runs the Netdata agent (written in C for performance), which collects metrics via multiple plugin interfaces: 27 internal plugins in this checkout (C, Python, and shell), Go plugins via `go.d.plugin` — a separate repository (netdata/go.d.plugin) referenced here rather than vendored — and external plugins via the PLUGINSD protocol. The agent collects data from procfs, eBPF, cgroups, systemd-journal, and service APIs.

**Three-component ecosystem:**

| Component | Description | License |
|---|---|---|
| **Netdata Agent** | Core monitoring engine on each node. Handles collection, storage, ML training, alert evaluation, and data export. Runs on Linux, macOS, FreeBSD, and Windows. | GPL v3+ |
| **Netdata Cloud** | Enterprise features: user management, RBAC, horizontal scaling, centralized alert management, multi-node dashboards. Free community tier available. No metric storage centralization — data stays on nodes. | Proprietary |
| **Netdata UI** | Dashboards and visualizations included in standard packages. Latest version delivered via CDN. Rich interactive charts without query language. | NCUL1 |

The agent serves metrics through an HTTP endpoint for the local dashboard or streams them to Netdata Cloud for centralized access. The tiered storage engine archives older data at lower resolution (~0.5 bytes per sample) for long-term retention while keeping recent data at full 1-second resolution.

A Rust workspace under `src/crates/` adds native components to the agent: `otel-ingestor` and `otel-ledger` implement OpenTelemetry ingestion and ledger processing, supported by `sfsq`, `netipc`, and the `opentelemetry`/`otel-*` crates — giving the agent native OTLP intake alongside its collector plugins.

## What Can Be Monitored

Netdata provides comprehensive monitoring coverage across all major platforms:

- **System Resources** — CPU (per-core, frequency, throttling), memory (RAM, swap, huge pages, KSM, NUMA), shared resources
- **Storage** — Disks, mount points, filesystems, RAID arrays, I/O operations and latency, S.M.A.R.T., NVMe
- **Network** — Network interfaces, protocols (TCP, UDP, ICMP), firewall, DNS queries, network connections per PID
- **Hardware & Sensors** — Fans, temperatures, voltages, power supplies, GPUs (Intel, AMD, Nvidia), PCI AER, RAM EDAC, IPMI, Intel RAPL
- **Containers** — Docker/containerd, LXC/LXD, Kubernetes cgroups and kubelet metrics
- **VMs** — KVM, qemu, libvirt, Proxmox, Hyper-V
- **Applications** — nginx, Apache, PostgreSQL, Redis, MongoDB, and hundreds more through auto-detection
- **Logs** — systemd-journal (Linux), Windows Event Log, ETW (Windows)
- **Synthetic Checks** — API endpoints, TCP ports, ping, TLS certificate expiry
- **Cloud Infrastructure** — AWS, GCP, Azure resource utilization. The cloud provider collectors ship in the external `go.d.plugin` repo (integrations/categories.yaml `data-collection.cloud-and-devops`), not in this checkout.

## Usage / Integration

- **As Prometheus metrics source** — Netdata nodes expose metrics in Prometheus-compatible format for [[prometheus]] scraping, combining high-resolution data with Prometheus's pull model.
- **Visualized via Grafana** — Netdata metrics can be ingested into [[grafana]] through the Prometheus data source or the Netdata data source plugin.
- **Kubernetes monitoring** — Deploy Netdata on [[k3s]] clusters for per-node, per-pod, and per-container metrics with 1-second granularity.
- **Container deployment** — Run Netdata via [[podman]] or Docker with minimal overhead alongside workloads.
- **Edge observability** — Deploy on [[bootc]]-based immutable OS images for per-second monitoring at remote edge locations.
- **With [[mission-control]]** — Integrate Netdata metrics into centralized observability management for cross-system visibility.
- **With [[headroom]]** — Feed real-time utilization metrics from Netdata into AI context compression agents for token-optimized observability.

## Related

- [[grafana]] — Alternative/companion visualization platform for Netdata metrics
- [[prometheus]] — Metrics collection and alerting (pull-based, complementary approach)
- [[k3s]] — Lightweight Kubernetes distribution compatible with Netdata monitoring
- [[headroom]] — AI context compression for agent-based monitoring workflows
- [[podman]] — Container runtime for deploying Netdata alongside workloads
- [[bootc]] — Bootable OS for edge deployments instrumented with Netdata
- [[mission-control]] — Centralized observability management layer
