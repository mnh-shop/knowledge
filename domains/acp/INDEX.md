---
name: acp-domain
description: "ACP (Agent Communication Protocol) implementation analysis across all repos in the vault"
tags: [acp, index, catalog]
---

# ACP Domain Docs

Analysis of ACP (Agent Communication Protocol) implementations across repositories. Each doc covers subagent orchestration, agent-to-agent delegation, JSON-RPC messaging, and identity/authorization models.

## By Repository

| Doc | Repo | Description |
|-----|------|-------------|
| [[agentfield-acp-implementation\|AgentField ACP]] | agentfield | Agent-to-agent routing, identity, authorization, and execution |
| [[alphaclaw-acp-implementation\|AlphaClaw ACP]] | alphaclaw | No ACP found; related multi-agent features |
| [[free-claude-code-acp-implementation\|Free Claude Code ACP]] | free-claude-code | ACP subagent delegation and communication |
| [[goclaw-acp-implementation\|GoClaw ACP]] | goclaw | External agent subprocess orchestration via JSON-RPC |
| [[hermes-acp-implementation\|Hermes ACP]] | hermes-agent | Server mode for ACP clients + client mode for external agents |
| [[n8n-acp-implementation\|n8n ACP]] | n8n | No ACP found; uses MCP and REST API instead |
| [[nanobot-acp-implementation\|Nanobot ACP]] | nanobot | Worker agents, task decomposition, subagent system |
| [[openclaw-acp-implementation\|OpenClaw ACP]] | openclaw | ACP server with session control plane, approval classifier, event ledger |
| [[podlet-acp-implementation\|Podlet ACP]] | podlet | No ACP found (Rust CLI tool, no agent protocol) |
| [[podman-acp-implementation\|Podman ACP]] | podman | No ACP found (REST API daemon, not agent protocol) |
| [[sablier-acp-implementation\|Sablier ACP]] | sablier | No ACP found (container scaling tool) |
| [[tank-os-acp-implementation\|Tank OS ACP]] | tank-os | No ACP found (container OS, runtime environment) |

## Key Patterns

- ACP is less standardized than MCP — implementations vary significantly
- Common pattern: JSON-RPC based subagent orchestration with tool-use delegation
- Several repos use ACP concepts without implementing the formal protocol
- Identity/authorization models range from shared API keys to DID-based keys
