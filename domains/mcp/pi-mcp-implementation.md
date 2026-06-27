---
name: pi-mcp-implementation
description: "Pi — no MCP implementation (CLI tool, no protocol server)"
source: sources/pi/
tags: [cli, mcp, pi, typescript]
---

# Pi - MCP Implementation Status

## Conclusion

Pi is a **pure TypeScript/Node.js CLI-only coding agent** with **no MCP (Model Context Protocol) implementation**. Unlike other coding assistants, Pi does not run as a protocol server that can be accessed via MCP. It is a command-line tool for interactive code generation and assistance.

## What Pi Is Instead

Pi provides **40+ LLM providers via direct API access** through its unified multi-provider LLM API (`@earendil-works/pi-ai`). It includes four core packages:

- **[@earendil-works/pi-coding-agent](packages/coding-agent)**: Interactive coding agent CLI
- **[@earendil-works/pi-agent-core](packages/agent)**: Agent runtime with tool calling and state management  
- **[@earendil-works/pi-ai](packages/ai)**: Unified multi-provider LLM API (OpenAI, Anthropic, Google, etc.)
- **[@earendil-works/pi-tui](packages/tui)**: Terminal UI library with differential rendering

## MCP Alternative

If you need MCP capabilities with Pi, consider using **[oh-my-pi](https://github.com/earendil-works/oh-my-pi)** which provides MCP tools to expose Pi's functionality through the MCP protocol. This allows you to integrate Pi's coding agent capabilities into MCP-compatible environments and tools.

## Architecture Links

- [Pi Architecture](/architecture/pi/pi-architecture.md)
- [Oh-My-Pi Architecture](/architecture/pi/oh-my-pi-architecture.md)

**Tags:** ai-llm, cli, mcp, pi, typescript

## Related

- [[mcp]]
- [[pi]]
