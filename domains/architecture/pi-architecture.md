---
name: pi-architecture
description: "Pi Agent Harness — TypeScript/Node.js multi-provider LLM agent coding framework"
source: sources/pi/
tags: [architecture, cli, javascript, typescript]
---

# Pi Agent Harness Architecture

## Overview

The **Pi Agent Harness** is a TypeScript/Node.js monorepo multi-provider LLM agent framework. It is a CLI-based coding agent with no HTTP server, no MCP implementation, no ACP, and no REST API. The monorepo contains 4 core packages:

- `pi-ai`: Multi-provider LLM API abstraction
- `pi-agent-core`: Agent runtime with tool calling, state management, context window, and thinking support
- `pi-coding-agent`: Interactive CLI with auth storage, model registry, and keybinding system
- `pi-tui`: Terminal UI library with differential rendering

The framework supports 40+ LLM providers through a unified interface and provides a complete coding agent experience.

## Package Architecture

### `@earendil-works/pi-ai` (packages/ai/)

The `pi-ai` package provides a multi-provider LLM API abstraction layer. It includes:

- **Unified Model Interface**: Single `Model<TApi>` interface for all providers
- **KnownApi Types**: Specialized interfaces for different provider types:
  - `openai-completions`
  - `anthropic-messages`
  - `google-generative-ai`
  - `bedrock-converse-stream`
  - `azure-openai-responses`
  - And 35+ more provider implementations
- **Provider Streaming**: Implemented via `ProviderStreams.stream()` and `streamSimple()` methods
- **Auth System**: Complete credential management with `CredentialStore` (api_key + OAuth), `ApiKeyAuth`, and `OAuthAuth` patterns

**Key Features**:
- Environment variable support
- Stored credentials management
- OAuth refresh capabilities
- Provider-specific streaming optimizations

### `@earendil-works/pi-agent-core` (packages/agent/)

The `pi-agent-core` package provides the agent runtime engine with essential capabilities:

- **Tool Calling Framework**: Extensible tool system with proper typing
- **State Management**: Sophisticated agent state tracking
- **Context Window**: Intelligent context management
- **Thinking Support**: Built-in reasoning and thought tracking capabilities

This package forms the core processing engine that agents use to interact with LLM providers and execute tasks.

### `@earendil-works/pi-coding-agent` (packages/coding-agent/)

The `pi-coding-agent` package provides the interactive CLI interface:

- **Interactive CLI**: Command-line interface for agent interaction
- **Auth Storage**: Secure credential storage and management
- **Model Registry**: Dynamic model discovery and registration
- **Keybinding System**: Customizable keyboard shortcuts for CLI navigation

**Key Files**:
- Entry point: `packages/coding-agent/src/index.ts`
- Auth storage: `packages/coding-agent/src/core/auth-storage.ts`

### `@earendil-works/pi-tui` (packages/tui/)

The `pi-tui` package provides the terminal UI library:

- **Terminal UI Library**: Rich terminal user interface components
- **Differential Rendering**: Efficient terminal rendering engine
- **Component System**: Reusable UI elements for agent interfaces

This package enables advanced terminal-based interactions with the agent framework.

## LLM Provider Integration

The Pi Agent Harness uses a unified architecture for integrating with multiple LLM providers:

### Model Interface
All providers implement the `Model<TApi>` interface, providing consistent access patterns across different LLM services.

### Provider Streaming
Provider-to-client communication happens through:
- `ProviderStreams.stream()` - Standard streaming interface
- `streamSimple()` - Simplified streaming for common use cases

### Authentication System
The auth system centralizes credential management:
- **CredentialStore**: Central repository for all authentication credentials
- **ApiKeyAuth**: Simple API key authentication
- **OAuthAuth**: OAuth 2.0 authentication with refresh capabilities
- **Environment Variables**: Support for environment-based credential configuration

**Flow**:
1. User provides credentials (API key or OAuth tokens)
2. Credentials stored in CredentialStore
3. Providers automatically use stored credentials when making requests
4. OAuth tokens automatically refreshed when expired

## No MCP/ACP/API

This is a **pure CLI tool** with no HTTP endpoints:

- **No HTTP Server**: No web server component
- **No REST API**: No API surface for external consumption
- **No MCP Protocol**: No Model Context Protocol implementation
- **No ACP Agent Protocol**: No Agent Communication Protocol support

The agent operates entirely within the terminal, making it ideal for:
- Local development workflows
- CI/CD pipeline integration
- Automated task execution
- Command-line productivity enhancement

## Key Files

### Entry Points
- **Main Entry**: `packages/coding-agent/src/index.ts`
- **AI Package**: `packages/ai/src/api/*.ts` (all provider implementations)

### Type Definitions
- **Agent Types**: `packages/agent/src/types.ts`
- **Auth Types**: `packages/ai/src/auth/types.ts`

### Core Components
- **Auth Storage**: `packages/coding-agent/src/core/auth-storage.ts`
- **Provider Abstractions**: `packages/ai/src/providers/*.ts`

## Related

[[hermes-agent-architecture]]
[[oh-my-pi-architecture]]

## Summary

The Pi Agent Harness provides a comprehensive, unified framework for building LLM agents in TypeScript. Its monorepo structure separates concerns cleanly across four core packages, supports over 40 LLM providers, and maintains a CLI-first approach. The framework is designed for developers who want to build custom LLM agents without the overhead of web server infrastructure.