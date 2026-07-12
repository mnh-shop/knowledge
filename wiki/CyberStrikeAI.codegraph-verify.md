---
title: "CyberStrikeAI"
subtitle: "CodeGraph Verification Companion"
suffix: ".codegraph-verify"
date: 2026-07-12
verified_by: "codegraph-explore"
source: "sources/CyberStrikeAI/"
tags: [cyberstrikeai, codegraph-verify, security, ai]
related:
  - "[[CyberStrikeAI]]"
  - "[[hexstrike-ai]]"
  - "[[Hexstrike-redteam]]"
  - "[[nyxstrike]]"
---

# CyberStrikeAI — CodeGraph Verification

**Verification date:** 2026-07-12  
**Verified by:** codegraph-explore (source tree analysis)  
**Source reference:** `sources/CyberStrikeAI/`  
**Companion to:** [[CyberStrikeAI]]

---

## Claim-1: AI-native security testing platform written in Go with 100+ integrated tools

CyberStrikeAI is an **AI-native security testing platform** built in Go (Go 1.24+, module `cyberstrike-ai`). It integrates **100+ security tools** via YAML recipe files covering the full kill chain:

- **Network scanners:** nmap, masscan, rustscan, arp-scan, nbtscan
- **Web scanners:** sqlmap, nikto, dirb, gobuster, feroxbuster, ffuf, httpx
- **Vulnerability scanners:** nuclei, wpscan, wafw00f, dalfox, xsser
- **Cloud security:** prowler, scout-suite, cloudmapper, pacu, terrascan, checkov
- **Exploitation:** metasploit, msfvenom, pwntools, ropper
- **Post-exploitation:** linpeas, winpeas, mimikatz, bloodhound, impacket, responder

The `tools/` directory on disk contains **92 YAML tool recipe files** (`tools/*.yaml`).

**Source evidence:** `sources/CyberStrikeAI/README.md` lines 149–166 (Tool Overview), `tools/` directory listing (92 `.yaml` files), `go.mod` line 1 (`module cyberstrike-ai`).

---

## Claim-2: Built-in C2 framework with listeners, encrypted beacons, sessions, and MCP tool integration

The platform includes a **first-party, AI-native C2 stack** with:

- **Listener types:** TCP reverse, HTTP/HTTPS beacon, WebSocket
- **Encrypted beacon channel** with per-listener crypto keys
- **Session and task queues** persisted in SQLite
- **SSE live events** for real-time status
- **REST API** under `/api/c2/*`
- **MCP tool family:** `c2_listener`, `c2_session`, `c2_task`, `c2_task_manage`, `c2_payload`, `c2_event`, `c2_profile`, `c2_file`
- **HITL integration** for approving sensitive C2 operations
- **OPSEC controls** including command deny rules

Listeners can be **restored after restart** when marked running in the database. Authorized testing only.

**Source evidence:** `sources/CyberStrikeAI/README.md` lines 351–355 (Built-in C2 section), line 137 (C2 highlights with tool family details), `internal/c2/` (implementation directory).

---

## Claim-3: Multi-agent AI orchestration via CloudWeGo Eino (Deep, Plan-Execute, Supervisor)

The platform implements three multi-agent orchestration patterns on CloudWeGo **Eino** (`github.com/cloudwego/eino v0.8.13`):

| Mode | Architecture | Config |
|------|-------------|--------|
| **deep** | Coordinator + `task` sub-agents | `orchestrator.md` |
| **plan_execute** | Planner / executor / replanner | `orchestrator-plan-execute.md` |
| **supervisor** | Orchestrator with `transfer`/`exit` | `orchestrator-supervisor.md` |

Features include:
- Markdown-defined agents under `agents/` directory
- ADK summarization with transcript persistence
- Checkpoint directory for process crash recovery
- Skills loaded via Eino ADK `skill` tool (progressive disclosure)
- Streaming SSE output via `/api/multi-agent/stream`

The `go.mod` confirms `github.com/cloudwego/eino v0.8.13` and `github.com/cloudwego/eino-ext` components for embeddings, document loaders, and model backends.

**Source evidence:** `sources/CyberStrikeAI/README.md` lines 301–311 (Multi-Agent Mode), `go.mod` lines 12–13 (Eino dependencies), `agents/` directory (Markdown agent definitions).

---

## Claim-4: Native MCP protocol support with HTTP/stdio/SSE transports and external MCP federation

CyberStrikeAI implements the **Model Context Protocol** natively with:

- **HTTP MCP server** (separate port, default 8081) with header-based auth
- **stdio MCP mode** via `cmd/mcp-stdio/main.go` for Cursor/CLI integration
- **SSE mode** for real-time streaming communication
- **External MCP federation** — register third-party MCP servers (HTTP, stdio, or SSE) from the UI, toggle per engagement, monitor health/call volume
- **MCP tool family** bridging C2 operations as MCP tools
- **Optional MCP servers** in `mcp-servers/` directory (e.g., reverse shell)

The MCP client library dependency is `github.com/modelcontextprotocol/go-sdk v1.2.0`.

**Source evidence:** `sources/CyberStrikeAI/README.md` lines 357–460 (MCP Everywhere section), `go.mod` line 27 (MCP SDK), `cmd/mcp-stdio/main.go` (MCP stdio entrypoint), `mcp-servers/` directory.

---

## Claim-5: RAG knowledge base with MultiQuery, HTTP rerank, and Eino Compose indexing pipeline

The platform includes a complete RAG pipeline:

- **MultiQuery** — LLM-driven query rewrite (configurable `max_queries: 4`)
- **Vector retrieval** — cosine similarity with configurable threshold
- **HTTP rerank** — supports DashScope `gte-rerank` or Cohere-compatible `/v1/rerank`
- **Post-processing** — normalized deduplication, char/token budget, final top_k
- **Auto-indexing** — scans `knowledge_base/` directory for Markdown files, chunking via Eino (Markdown header split + recursive chunking)
- **Web management** — CRUD for knowledge items, category-based organization, retrieval logs

Rerank failures degrade to fusion order without breaking search. Pipeline configurable in `config.yaml` under `knowledge:` section.

**Source evidence:** `sources/CyberStrikeAI/README.md` lines 469–511 (Knowledge Base section), `config.yaml` lines 551–572 (knowledge configuration block), `go.mod` lines 14–15 (Eino document loader/splitter components).

---

## Claim-6: Role-based testing with 15 predefined security roles and YAML-based extension

The platform ships **15 predefined security testing roles** in `roles/` directory:

| Role | Focus |
|------|-------|
| Penetration Testing | Full pentest with nmap, sqlmap, nuclei, metasploit |
| Web App Scanning | Web application vulnerability scanning |
| CTF | Capture-the-flag utilities |
| API Security Testing | API-focused testing |
| Binary Analysis | Reverse engineering tools |
| Cloud Security Audit | Cloud posture assessment |
| Container Security | Container/K8s audit |
| Digital Forensics | Forensic analysis |
| Post-Exploitation | Lateral movement and escalation |

Each role is a YAML file defining `name`, `description`, `user_prompt`, `icon`, `tools` (allowlist), and `enabled`. Custom roles can be created by adding YAML files. Tool restrictions allow focused testing scenarios.

**Source evidence:** `sources/CyberStrikeAI/README.md` lines 278–299 (Role-Based Testing), `roles/` directory (15 `.yaml` files), `config.yaml` line 573 (`roles_dir: "roles"`).

---

## Related Pages

- [[CyberStrikeAI]] — Main wiki entry for this repository
- [[hexstrike-ai]] — AI-powered security framework
- [[Hexstrike-redteam]] — Red team automation
- [[nyxstrike]] — Security orchestration platform
