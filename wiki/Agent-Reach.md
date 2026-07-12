---
name: Agent-Reach
tags: [agent-reach, agent, ai-agents, orchestration, multi-agent]
description: "Multi-agent orchestration and communication framework"
source: sources/Agent-Reach/
---

# Agent-Reach

| Field | Value |
|---|---|
| **Origin** | [Agent-Reach/Agent-Reach](https://github.com/Agent-Reach/Agent-Reach) |
| **Source** | `sources/Agent-Reach/` |
| **Repomix** | `raw/Agent-Reach/Agent-Reach.xml` |
| **Codegraph** | `graphs/Agent-Reach/` |

## Overview

Agent-Reach is a multi-agent orchestration and communication framework designed to enable structured interaction between multiple AI agents. It provides the communication primitives and coordination patterns needed for agents to discover each other, delegate tasks, share context, and collaborate on complex workflows.

## Key Features

- **Agent Discovery** — Mechanism for agents to discover peer agents and their capabilities within the network
- **Structured Communication** — Protocol for typed message passing between agents (requests, responses, errors, streaming)
- **Task Delegation** — Pattern for one agent to delegate sub-tasks to another with context propagation
- **Shared Context** — Capability for agents to share and synchronize working memory across the mesh
- **Pluggable Transport** — Abstract transport layer supporting multiple backends (WebSocket, gRPC, HTTP)
- **Failure Handling** — Timeout, retry, and fallback patterns for resilient multi-agent execution

## Architecture

Agent-Reach follows a hub-and-spoke or fully-meshed model depending on deployment. Each agent exposes a Reach endpoint; coordinators or intermediaries route messages between agents based on capability declarations.

## Related

- [[hermes-agent]] — Multi-platform agent gateway with delegation and subagent support
- [[openclaw]] — Personal AI assistant with channel bridge and agent workspace isolation
- [[nanobot]] — Agent orchestration framework
- [[materia]] — Agent framework with composable pipelines
