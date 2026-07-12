---
name: security-monitoring-stack
type: integration
tags: [security, monitoring, integration, deployment, ai, quadlet, podman, pentest, orchestration]
description: "Integration: hexstrike-ai + nyxstrike + SecuritySkills under Podman Quadlet — AI-powered security scanning pipeline with Prometheus monitoring"
---

# Integration: Security Monitoring Stack

**Source**: `sources/hexstrike-ai/`, `sources/nyxstrike/`, `sources/SecuritySkills/`

## Overview

Three AI-security tools under a single Podman Quadlet deployment: **hexstrike-ai** (MCP cybersecurity, 150+ tools, 12 agents), **nyxstrike** (offensive orchestration, 185+ tools, decision engine), and **SecuritySkills** (45 framework-grounded skills). Prometheus scrapes both engines for operational monitoring and alerting.

## Architecture

```
Pod: security-stack (ports 8000, 8888, 9090)
  ├── hexstrike-ai (MCP server, 150+ tools, 12 agents, /metrics)
  ├── nyxstrike (MCP server + dashboard, 185+ tools, /metrics)
  ├── prometheus (scrapes both engines)
  └── SecuritySkills (mounted volume — OWASP/NIST/MITRE/CIS)
```

## Configuration

```yaml
# security-stack.pod
[Pod]
PodName=security-stack
PublishPort=8000:8000 PublishPort=8888:8888 PublishPort=9090:9090

# hexstrike.container
[Container]
Image=ghcr.io/0x4m4/hexstrike-ai:latest
Pod=security-stack.pod
Environment=HEXSTRIKE_API_TOKEN=changeme PROMETHEUS_ENABLED=true
Volume=hexstrike_data:/data:U

# nyxstrike.container
[Container]
Image=ghcr.io/commonhuman-lab/nyxstrike:latest
Pod=security-stack.pod
Environment=NYXSTRIKE_API_TOKEN=changeme NYXSTRIKE_ENABLE_AI=true
Volume=nyxstrike_data:/data:U

# prometheus.container (scrape config targets hexstrike:8000, nyxstrike:8888)
[Container]
Image=docker.io/prom/prometheus:latest
Pod=security-stack.pod
Volume=./prometheus.yml:/etc/prometheus/prometheus.yml:Z
```

## Deployment

```bash
podman pod create --name security-stack --publish 8000:8000 --publish 8888:8888 --publish 9090:9090
podman run -d --pod security-stack --name hexstrike -e HEXSTRIKE_API_TOKEN=changeme ghcr.io/0x4m4/hexstrike-ai:latest
podman run -d --pod security-stack --name nyxstrike -e NYXSTRIKE_API_TOKEN=changeme ghcr.io/commonhuman-lab/nyxstrike:latest
curl http://localhost:8000/health && curl http://localhost:8888/api/v1/status
```

### Running a Scan

```bash
# hexstrike: network recon
curl -X POST http://localhost:8000/tools/recon -H "Authorization: Bearer $TOKEN" -d '{"target":"example.com","tools":["nmap","whatweb"]}'
# nyxstrike: full attack chain
curl -X POST http://localhost:8888/api/v1/scan -H "Authorization: Bearer $NYXSTRIKE_API_TOKEN" -d '{"target":"example.com","profile":"full-audit"}'
```

## Related

- [[hexstrike-ai]] — MCP cybersecurity automation with 150+ tools
- [[nyxstrike]] — AI offensive security orchestration engine
- [[SecuritySkills]] — Framework-grounded security skills for AI agents
- [[prometheus]] — Metrics and monitoring toolkit
