---
name: claw-code
tags: [claw-code, cli, developer-tools, openclaw, agent-gateway]
description: "Command-line tool for OpenClaw agent interaction and management"
source: sources/claw-code/
---

# Claw Code

| Field | Value |
|---|---|
| **Origin** | [openclaw/claw-code](https://github.com/openclaw/claw-code) |
| **Source** | `sources/claw-code/` |
| **Repomix** | `raw/claw-code/claw-code.xml` |
| **Codegraph** | `graphs/claw-code/` |

## Overview

Claw Code is a command-line interface tool for interacting with and managing the OpenClaw agent gateway. It provides a terminal-based entry point for sending messages to agents, managing sessions, inspecting agent state, and performing administrative operations without requiring the full OpenClaw desktop or web interface.

## Key Features

- **Agent Messaging** — Send messages to OpenClaw agents directly from the terminal
- **Session Management** — List, inspect, and manage agent conversation sessions
- **State Inspection** — View agent status, connected channels, and runtime configuration
- **Channel Control** — Enable or disable messaging channels from the CLI
- **Scriptable Interface** — Designed for use in shell scripts and automation pipelines
- **Lightweight Dependency** — Minimal footprint compared to the full OpenClaw suite

## Architecture

Claw Code communicates with the OpenClaw Gateway API over HTTP/WebSocket. It authenticates using gateway credentials and provides a structured command hierarchy for common operations. The tool is built to be composable with other CLI tools in the OpenClaw ecosystem.

## Related

- [[openclaw]] — The agent gateway that claw-code manages
- [[goclaw]] — Go-based alternative agent gateway
- [[clawpier]] — Desktop GUI for managing OpenClaw Docker containers
- [[hermes-agent]] — Alternative agent gateway with its own CLI
