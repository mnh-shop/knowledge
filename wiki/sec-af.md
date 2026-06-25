---
name: sec-af
tags: [adversarial, ai-llm, auditor, docker, git, orchestration, python, sec-af, security, wiki]
description: Wiki entry for SEC-AF — AI-native security auditor that confirms exploitability, not just pattern detection (Apache 2.0)
---

# SEC-AF

| Field | Value |
|---|---|
| **Origin** | [Agent-Field/sec-af](https://github.com/Agent-Field/sec-af) |
| **License** | Apache 2.0 |
| **Stack** | Python + FastAPI + AgentField SDK |
| **Source** | `sources/sec-af/` |
| **Wanted** | AI-native security auditor — confirms exploitability, not just patterns |

## What it is

Adversarial security analysis that proves exploitability. Uses a multi-reasoner DAG with HUNT vs PROVE adversarial tension — 106 raw findings filtered to 28 confirmed via adversarial verification (94% noise reduction).

Built on [[agentfield]] — same multi-reasoner architecture as SWE-AF, applied to security.

## Architecture

- **Composite intelligence**: Multi-reasoner DAG with 4-agent verification chain (Tracer → Sanitization Analyzer → Exploit Hypothesizer → Verdict Agent)
- **Signal cascade**: Raw findings → deduplication → adversarial verification
- **Dynamic AI gates**: Runtime routing based on technology stack detection
- **SARIF 2.1.0 native output**: GitHub Code Scanning integration
- **Integration**: 4 core systems (HARMONIZE, BRAHM, SKYHOOK, TEMPEST compatible)
- **AgentField relationship**: SEC-AF is a sub-repo of the AgentField platform, designed for adversarial security analysis rather than standalone operation

## Performance (DVGA benchmark)

- 106 raw findings → 28 confirmed after adversarial verification
- Cost: $0.18–$0.90 per 30 findings
- Agent calls: ~166–255, 82 DAG edges
- Verdict model: `confirmed` / `likely` / `inconclusive` / `not_exploitable`

## Deployment

Requires AgentField control plane, Python 3.11+, OpenRouter API key. Air-gapped capable with local LLMs.

**Deployment via Docker Compose / Railway**:
- Railway: One-click deployment at `https://railway.com/deploy/sec-af`
- Local: `docker compose up --build` after adding OpenRouter API key to `.env`
- Supports integration with AgentField's distributed orchestration

## Key Source Files and Roles

- `src/sec_af/app.py` — FastAPI entry point with AgentField integration and audit pipeline
- `src/sec_af/reasoners/` — Multi-reasoner DAG nodes for coordinated agent orchestration
- `src/sec_af/agents/*/` — Specialized agent implementations:
  - **Hunt phase**: 10+ strategy hunters (injection, auth, crypto, etc.)
  - **ReI gather**: Architecture, dependencies, config analysis
  - **Prove verification**: 4-agent adversarial chain (tracer → sanitizer → exploit → verdict)
- `src/sec_af/orchestrator.py` — SEC-AF orchestrator managing the full audit pipeline
- `prompts/` — Strategy-specific prompts for each agent type
- `examples/` — Sample usage and integration patterns

## Related

- [[sec-af-architecture]] -- architecture documentation
- [[sec-af-profile]] -- agent profile
- [[agentfield]] -- core AgentField platform
- [[agentfield-profile]] -- AgentField platform profile
- [[agentfield-deployment]] -- deployment guide
- [[swe-af-profile]] -- sibling SWE-AF profile

## Cross-project

- [[SWE-AF]] -- Sibling autonomous engineering factory on AgentField
- [[af-deep-research]] -- Sibling research engine on AgentField
- [[af-reactive-atlas-mongodb]] -- Sibling MongoDB intelligence on AgentField
- [[hermes-agent]] -- Can audit Hermes agent applications
- [[openclaw]] -- Can audit OpenClaw agent applications
- [[n8n]] -- Can audit n8n workflow configurations
- [[gogs]] -- Can audit Git repositories for security issues
