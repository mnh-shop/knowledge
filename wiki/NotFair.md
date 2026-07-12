---
name: NotFair
tags: [notfair, ai-agents, automation, workflow, intelligent-automation]
description: "AI-powered intelligent automation platform for business workflows"
source: sources/NotFair/
---

# NotFair

| Field | Value |
|---|---|
| **Origin** | [notfair-ai/NotFair](https://github.com/notfair-ai/NotFair) |
| **Source** | `sources/NotFair/` |
| **Repomix** | `raw/NotFair/NotFair.xml` |
| **Codegraph** | `graphs/NotFair/` |

## Overview

NotFair is an AI-powered intelligent automation platform designed to orchestrate and execute complex business workflows. Formerly known as Toprank, it provides a visual workflow builder backed by AI decision-making, enabling users to create sophisticated automation pipelines that combine traditional logic with LLM-powered reasoning. The platform focuses on making automation accessible to non-technical users while remaining extensible for developers.

## Key Features

- **Visual Workflow Builder** — Drag-and-drop interface for constructing automation pipelines with branching, loops, and conditional logic
- **AI Decision Nodes** — LLM-powered decision points within workflows for dynamic routing and content generation
- **Integration Library** — Pre-built connectors for common SaaS platforms, databases, and APIs
- **Execution Engine** — Reliable workflow execution with retry, error handling, and state persistence
- **Monitoring Dashboard** — Real-time visibility into workflow execution, logs, and performance metrics
- **Role-Based Access** — Multi-tenant architecture with granular permission controls

## Architecture

NotFair uses a directed acyclic graph (DAG) execution model where each workflow is composed of configurable nodes. The AI engine sits alongside the execution runtime, providing inference capabilities at decision points. Workflows can be triggered via API, webhooks, or schedule, and state is persisted to a backing database for durability and resume capability.

## Related

- [[openclaw]] — Personal AI agent platform with complementary workflow capabilities
- [[n8n]] — Open-source workflow automation platform (similar category)
- [[hermes-agent]] — Agent gateway with delegation and skill-based execution
- [[outreachmagic]] — AI-powered outreach automation
