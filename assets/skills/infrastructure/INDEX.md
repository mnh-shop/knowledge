---
name: infrastructure-skills
description: "35+ infrastructure skills for deployment, homelab, networking, Kubernetes, and system operations"
tags: [infrastructure, skills, mcp, automation]
metadata:
  type: catalog
---

# Infrastructure Skills

Skills for deployment patterns, homelab setup, Kubernetes, networking, and system operations.

**Total skills:** 35+ across 8 repos

---

## Skill Sources

| Repo | Count | Harness Support |
|------|-------|-----------------|
| `sources/ECC/skills/` | 10 skills | ECC, hermes-agent |
| `sources/hermes-profiles/skills/` | 8 skills | hermes-agent |
| `sources/hermes-agent/skills/` | 11 skills | hermes-agent |
| `sources/open-design/skills/` | 4 skills | open-design |
| `sources/abvx-agent-skills/skills/` | 4 skills | All skills-harnesses |

---

## Skill Catalog

### Deployment Patterns

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| deployment-patterns | ECC | ECC, hermes-agent | Production deployment workflows |
| docker-patterns | ECC | ECC | Docker best practices |
| kubernetes-patterns | ECC | ECC | Kubernetes deployment patterns |
| autonomous-agent-harness | ECC | ECC | Deploy autonomous agent infrastructure |
| uncloud | ECC | ECC | Infrastructure decommissioning and migration |

### Homelab

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| homelab-network-readiness | ECC | ECC | Homelab network prep |
| homelab-network-setup | ECC | ECC | Network configuration |
| homelab-pihole-dns | ECC | ECC | Pi-hole deployment |
| homelab-vlan-segmentation | ECC | ECC | VLAN configuration |
| homelab-wireguard-vpn | ECC | ECC | VPN setup for homelab |

### Networking & Systems

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| network-bgp-diagnostics | ECC | ECC | BGP troubleshooting |
| network-config-validation | ECC | ECC | Config validation |
| network-interface-health | ECC | ECC | Interface monitoring |
| rtk-assisted-shell | abvx-agent-skills | All | Shell command assistance with RTK |

### Platform Engineering

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| platform-engineer | hermes-profiles | hermes-agent | Platform design workflows |
| site-reliability-engineer | hermes-profiles | hermes-agent | SRE practices |
| data-engineer | hermes-profiles | hermes-agent | Data pipeline engineering |
| platform-design | open-design | open-design | Infrastructure design |

### MLOps & AI Infrastructure

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| huggingface-hub | hermes-agent | hermes-agent | HuggingFace Hub model and dataset management |
| llama-cpp | hermes-agent | hermes-agent | Llama.cpp inference optimization |
| vllm | hermes-agent | hermes-agent | vLLM inference server integration |
| lm-evaluation-harness | hermes-agent | hermes-agent | LM evaluation harness for benchmarking |
| segment-anything | hermes-agent | hermes-agent | Segment Anything model integration |
| weights-and-biases | hermes-agent | hermes-agent | Weights & Biases experiment tracking |

### Smart Home & Automation

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| openhue | hermes-agent | hermes-agent | OpenHue smart home lighting control |
| dogfood | hermes-agent | hermes-agent | Dogfood testing automation |
| yuanbao | hermes-agent | hermes-agent | Yuanbao integration |

### Computer Automation

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| computer-use | hermes-agent | hermes-agent | Computer use and desktop automation |

---

## Harness Compatibility

- **ECC** — Aggressive hook integration
- **Hermes Agent** — Progressive disclosure
- **open-design** — Design for infra systems
- **opencode** — Native skills format

---

## Related

- [[skills-catalog]] — Main catalog
- [[quadlet]] — Container deployment
- [[bootc]] — Image-based OS
- [[nix-podman-stacks]] — Nix declarative infrastructure