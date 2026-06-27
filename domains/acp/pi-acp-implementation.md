---
name: pi-acp-implementation
description: "Pi — no ACP implementation (CLI tool, no agent protocol)"
source: sources/pi/
tags: [acp, cli, pi, typescript]
---

# Pi - ACP Implementation Status

## Conclusion

Pi is a **pure TypeScript/Node.js CLI-only coding agent** with **no ACP (Agent Communication Protocol) implementation**. It is a standalone command-line tool rather than a protocol-based agent that communicates through ACP.

## What Pi Is Instead

Pi serves as a self-contained coding agent harness that runs directly in the terminal. It provides:

- **Interactive coding assistance** through its `@earendil-works/pi-coding-agent` package
- **State management and tool calling** via the `@earendil-works/pi-agent-core` runtime
- **Direct LLM integration** with 40+ providers through the `@earendil-works/pi-ai` multi-provider API
- **Rich terminal UI** with differential rendering capabilities via `@earendil-works/pi-tui`

The architecture is designed as a monolithic CLI tool that handles coding tasks end-to-end without requiring external protocol communication.

## Architecture Links

- [Pi Architecture](/architecture/pi/pi-architecture.md)

**Tags:** acp, ai-llm, cli, pi, typescript

## Related

- [[acp]]
- [[pi]]
