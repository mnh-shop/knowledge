---
name: hermes-agent-profile
tags: [hermes, profile, typescript, agent-gateway, messaging, multi-platform, ai-llm, automation, orchestration, acp, agent-profile, cli, mcp, plugin-sdk]
description: "Agent profile for Hermes Agent: development guide for AI coding assistants and contributors to the Hermes Agent project"
---

# Agent Profile: hermes-agent

**Source:** `sources/hermes-agent/AGENTS.md`
**Purpose:** Development guide for AI coding assistants and contributors

## Design Principles

1. **Prompt caching is sacred.** Long-lived conversations reuse a cached
   prefix every turn. Mid-conversation mutations that invalidate the cache
   (mutating past context, swapping toolsets, rebuilding system prompt) are
   avoided.

2. **Core is a narrow waist; capability lives at the edges.** Every model
   tool ships on every API call. New core tools are high-bar. Most new
   capability arrives as CLI commands, skills, plugins, or MCP servers.

3. **Expansive at the edges, conservative at the waist.** New platform
   adapters, channels, providers, models are welcome. New core tools are
   the last resort.

## Footprint Ladder (preference for new capabilities)

1. Extend existing code
2. CLI command + skill
3. Service-gated tool (`check_fn`)
4. Plugin
5. MCP server in the catalog
6. New core tool (last resort)

## What gets merged

| Category | Policy |
|---|---|
| Bug fixes | ✅ Always wanted — reproduce on `main`, fix whole class, not just the reported site |
| Platform adapters | ✅ Welcome — integrate with existing setup/config UX |
| Refactor god-files | ✅ Wanted — extracting from `cli.py`, `run_agent.py`, `gateway/run.py` |
| New core tools | ❌ Last resort — every tool ships on every API call |
| Duplicate functionality | ❌ Extend, don't duplicate |
| Taste-based "out of scope" closes | ❌ Not automated — stays with human maintainer |

## Architecture principles

- **Smallest footprint governs how a capability is wired into the core**,
  NOT whether the product is allowed to grow.
- **Behavior contracts over snapshots** — test how two pieces of code
  interact, not what their intermediate state is.

## Related

- [[hermes-agent]] -- Wiki entry for Hermes Agent
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-gateway-platforms]] -- Gateway platform adapters
- [[hermes-acp-agent]] -- ACP agent configuration
- [[hermes-mcp-serve]] -- MCP messaging bridge
- [[hermes-agent-deployment]] -- Deployment and operations guide

## Links

- Full wiki: [[hermes-agent]]
- Architecture: [[hermes-agent-architecture]]
