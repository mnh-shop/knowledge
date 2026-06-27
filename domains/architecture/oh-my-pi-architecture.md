---
name: oh-my-pi-architecture
description: "omp.sh — Rust/TypeScript hybrid coding agent with 40+ LLM providers, MCP tools, and IDE integration"
source: sources/oh-my-pi/
tags: [architecture, cli, rust, typescript, mcp, coding-agent]
---

# oh-my-pi-architecture

## Overview

oh-my-pi is a feature-rich fork of Pi by can1357, offering a powerful 703MB repository for Rust/TypeScript hybrid coding agent development. It provides 40+ LLM providers, 32 built-in tools, and comprehensive IDE integration. The project can be installed easily via `curl -fsSL https://omp.sh/install | sh` or through Homebrew.

## Architecture

### Core
- **Rust-based**: Uses Cargo package management (`Cargo.toml`, `Cargo.lock`) for performance-critical paths
- **Hybrid Model**: Combines Rust's performance with TypeScript's flexibility for different use cases

### UI/Agent
- **TypeScript-based CLI tooling**: Built on TypeScript for enhanced developer experience
- **Multi-package Structure**: Inherited from Pi with the following main packages:
  - `pi-ai`: Core AI provider implementations
  - `pi-agent-core`: Agent core functionality
  - `pi-coding-agent`: Coding agent specific tools and logic

### Docker Support
- **Standard Docker Image**: `Dockerfile` for containerized deployment
- **Robomp Image**: `Dockerfile.robomp` for specialized configurations

## MCP Implementation

The `packages/mnemopi/` package defines a comprehensive MCP tool system with 30+ tools, implementing sophisticated memory management and graph-based reasoning capabilities.

### Key Files and Components

#### `packages/mnemopi/src/mcp-tools.ts`
This file contains the core tool definitions with a `ToolDefinition` interface that includes:
- `name`: Tool identifier
- `description`: Human-readable description
- `inputSchema`: JSON schema for tool arguments

#### Core Tool Types
Tools include:
- **Memory Management**: `remember`/`recall` for durable memories, `shared_remember`/`shared_recall` for compact cross-agent surface memory
- **Graph Operations**: `graph_query` (findRelatedMemories), `graph_link` (addEdge)
- **Memory Banks**: Support for multiple memory banks with persistence
- **Utilities**: `stats`, `sleep` (consolidation), `diagnose` (PII-safe diagnostics)

#### Beam Memory System
- Uses `BeamMemory` for shared state management
- Implements episodic graph with beam-based memory consolidation
- Supports dynamic fact extraction and dense recall capabilities

### Key Tools Defined:
- `handleSharedRemember`: Shared surface memory storage
- `handleGraphQuery`: Traverse memory graphs from seed memories
- `handleGraphLink`: Declare semantic edges between memories
- `handleSleep`: Run consolidation sleep cycles
- `handleStats`: Return memory statistics and database paths

## GitHub Tool System

Full GitHub integration implemented in `packages/coding-agent/src/tools/gh.ts`:

### `GithubTool` Class
- Implements `AgentTool` interface
- Provides comprehensive GitHub API access through the coding agent

### Capabilities
- **Repository Search**: Search through repos, issues, code, and commits using GitHub API
- **PR Operations**: Create, update, and manage pull requests
- **Issue Management**: Create, query, and manage issues
- **Rate Limiting**: Built-in support for GitHub API rate limits
- **Pagination**: Comprehensive pagination handling for large datasets

## LLM Provider System

Built on Pi's multi-provider architecture with significant enhancements:

### Key Components
- **Model Registry**: `packages/coding-agent/src/config/model-registry.ts` for centralized model discovery
- **AI Package**: `@oh-my-pi/pi-ai` handles provider streaming and model communication
- **Catalog Package**: `@oh-my-pi/pi-catalog` provides model discovery and selection
- **API Key Resolver**: Implements retry/rotation patterns for secure key management

### Provider Features
- 40+ LLM provider support
- API key rotation and retry mechanisms
- Model optimization and selection

## No REST API or ACP

oh-my-pi is strictly a CLI-based tool with:
- **No HTTP server**: Does not expose REST APIs
- **No ACP protocol**: Does not implement the Agent Control Protocol (ACP)
- **MCP as Tool Consumer**: Uses MCP tools as a consumer, not as a protocol server

This design maintains a clean, focused CLI experience without server-side complexity.

## Key Files

### Primary Entry Points
- **Main Entry**: `packages/coding-agent/src/index.ts` (TypeScript CLI), Rust binary alternative
- **MCP Tools**: `packages/mnemopi/src/mcp-tools.ts` (30+ tool definitions)
- **GitHub Tool**: `packages/coding-agent/src/tools/gh.ts` (full GitHub integration)
- **Model Registry**: `packages/coding-agent/src/config/model-registry.ts` (centralized model management)
- **AI Types**: `packages/ai/src/types.ts` (AI-specific type definitions)

### Supporting Files
- **Configuration**: `Cargo.toml` and `Cargo.lock` for Rust components
- **Docker**: `Dockerfile` and `Dockerfile.robomp` for containerization
- **Documentation**: `README.md` for comprehensive project documentation

## Related

- [[pi-architecture]]
- [[hermes-agent-architecture]]
- [[openclaw-architecture]]