---
name: openclaw-goclaw-mcp-bridge
type: integration-pattern
tag: [openclaw, goclaw, mcp, integration-patterns, gateway]
description: "Multi-gateway MCP bridge integration between OpenClaw TypeScript platform and GoClaw Go-based gateway"
---

# Integration Pattern: OpenClav ↔ GoClaw MCP Bridge

## Overview

This integration pattern enables **unified MCP (Model Context Protocol) connectivity** between OpenClaw's TypeScript-based agent gateway and GoClaw's Go-based AI agent gateway. The pattern leverages each platform's strengths:

- **OpenClaw**: Frontend-focused, React/Vite-based UI, JavaScript ecosystem
- **GoClaw**: Backend-optimized, Go native, performance-critical

The bridge pattern allows seamless tool sharing, workflow coordination, and agent orchestration across both platforms while maintaining platform-specific optimizations.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenClaw      │    │   MCP Broker    │    │   GoClaw        │
│   (TypeScript)  │    │   (Bridge)      │    │   (Go)         │
│                 │    │                 │    │                 │
│ MCP Client      │───▶│ MCP Bridge Server│───▶│ MCP Server     │
│ (Tool Consumer) │    │ (Bridge Component) │    │ (Tool Provider) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    OpenClaw APIs   MCP Protocol      GoClaw APIs\n    (TypeScript)         <─▶         (Go)\n         │                       │                       │\n    Orchestration     Workflow          Agent                     │\n     Coordination     Management        Lifecycle                 │\n```

## Pattern Purpose

### Primary Use Cases