---
name: agentfield-profile
description: AgentField is an Apache 2.0 control plane for AI agents — Go backend, 3 SDKs (Python/Go/TypeScript), DID/VC identity, harness orchestration
tags: [agent-profile, agentfield, ai-llm, control-plane, golang, harness, identity, orchestration, profile, quadlet, systemd]
metadata:
  type: reference
source: sources/agentfield/
---

# AgentField — Key Reference

**License:** Apache 2.0 (fully permissive — best for forking/redistribution)

**What it is:** An AI backend control plane. You write agent logic → it becomes production infrastructure (REST endpoints, cross-agent routing, memory, async execution, audit trails).

**Quick install:**
```bash
curl -fsSL https://agentfield.ai/install.sh | bash
# Then in Claude Code: /agentfield Build a claims processor...
```

**SDKs:** Python (main), Go, TypeScript — `@app.reasoner()` decorator → REST endpoint

**Key differentiators vs Hermes/n8n:**
- IAM for agents: W3C DID + Verifiable Credentials (tamper-proof execution receipts)
- Harness orchestration: `app.harness()` dispatches to Claude Code/Codex/Gemini CLI/OpenCode
- Canary deployments: traffic weight routing, A/B testing, blue-green
- Cross-agent mesh: `app.call()` with tracing, `app.discover()` for service discovery

**Deployment:** `af server` (SQLite, local dev) or Docker Compose with PostgreSQL (production)

**Related repos (built on AgentField):** SWE-AF, sec-af, af-deep-research, af-reactive-atlas-mongodb — all use same `app.reasoner()`/`app.ai()`/`app.skill()` SDK patterns.

**Why it matters for stack planning:** AgentField fills the "production infrastructure" gap that Hermes and n8n don't cover — identity, audit, canaries, cross-agent mesh. It's complementary to both, not a replacement.

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-mcp-server]] -- MCP bridge server
- [[agentfield.codegraph-verify]] -- codegraph verification
- [[SWE-AF]] -- autonomous engineering factory
- [[sec-af]] -- security auditor agent
- [[af-deep-research]] -- deep research engine
- [[af-reactive-atlas-mongodb]] -- reactive MongoDB intelligence
