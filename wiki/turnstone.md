---
name: turnstone
tags: [turnstone, ai-agents, agent-framework, autonomous, orchestration]
description: "Agent framework for building and deploying autonomous AI workers"
source: sources/turnstone/
---

# Turnstone

| Field | Value |
|---|---|
| **Origin** | [cf-toolsuite/turnstone](https://github.com/cf-toolsuite/turnstone) |
| **Source** | `sources/turnstone/` |
| **Repomix** | `raw/turnstone/turnstone.xml` |
| **Codegraph** | `graphs/turnstone/` |

## Overview

Turnstone is an agent framework for building and deploying autonomous AI workers. It provides the core abstractions — agents, tasks, tools, memory — needed to construct sophisticated AI worker systems, along with the runtime infrastructure to run them reliably. The framework emphasizes composability, allowing developers to assemble complex agent behaviors from simple, testable building blocks.

## Key Features

- **Agent Abstraction** — Core agent class with lifecycle hooks, tool registration, and state management
- **Task System** — Composable task definitions with dependency resolution and execution tracking
- **Tool Registry** — Pluggable tool system for extending agent capabilities
- **Memory Management** — Built-in memory stores (conversation, episodic, semantic)
- **Runtime Environment** — Execution sandbox with configurable resource limits
- **Observability** — Structured logging and telemetry for agent execution

## Architecture

Turnstone follows a modular architecture where agents are composed from collections of capabilities (tools, memory, skills). The framework provides base classes and dependency injection for assembling agents declaratively. Execution happens through a runtime that manages concurrency, error handling, and resource limits.

## Related

- [[hermes-agent]] — Production agent gateway with skill system and delegation
- [[nanobot]] — Agent framework for building autonomous workers (similar category)
- [[shannon]] — Agent runtime and orchestration platform
- [[materia]] — Agent framework with composable pipelines
