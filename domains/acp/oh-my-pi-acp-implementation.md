---
name: oh-my-pi-acp-implementation
description: "oh-my-pi — no ACP implementation (coding agent, no agent communication protocol)"
source: sources/oh-my-pi/
tags: [acp, cli, coding-agent, oh-my-pi, rust, typescript]
---

# oh-my-pi ACP Implementation

The oh-my-pi project is a **Rust/TypeScript coding agent** that **does not implement ACP (Agent Communication Protocol)**.

## ACP Status

### Current State
- **No ACP Implementation**: The project lacks an actual ACP implementation
- **CLI-Only Design**: oh-my-pi operates as a command-line interface (CLI) tool
- **Agent Communication Limitation**: No standard agent-to-agent communication protocol

### What This Means
The absence of ACP means:

1. **No Message Bus**: There's no standardized message passing system between agents
2. **No Action Integration**: Agents cannot send standardized actions to each other
3. **No State Synchronization**: No built-in protocol for cross-agent state management
4. **No Workflow Orchestration**: Limited capabilities for orchestrating complex agent workflows

## Context and Design Decisions

### Coding Agent Focus
oh-my-pi is designed as a **specialized coding agent** rather than a general multi-agent system:

- **Primary Purpose**: Code analysis, refactoring, and development tasks
- **Tool Integration**: Works through its 30+ MCP tools for memory management
- **Architecture**: Single-agent focused with extensibility through tool ecosystem

### Why No ACP Needed
- **Scope Limitation**: Designed for specific coding tasks rather than general agent collaboration
- **Tool-Based Communication**: Uses MCP tools and memory systems instead of ACP
- **Simplification**: Avoiding ACP complexity for focused functionality

### Alternative Communication Channels
While no ACP implementation exists, communication is achieved through:

- **MCP Tools**: For structured tool calls and memory management
- **Memory Systems**: Via BeamMemory and episodic graph for state sharing
- **Filesystem Interaction**: For reading/writing project files and configurations

## Comparison with Other Implementations

### vs. Projects With ACP
- **Hermes**: Likely includes ACP implementation for agent communication
- **Standard MCP Servers**: May include ACP alongside MCP for comprehensive agent interactions
- **Multi-Agent Frameworks**: Systems built around agent collaboration inherently include ACP

### Architectural Implications
The decision not to implement ACP suggests:
- **Solo Agent Architecture**: Designed to be used as a single, self-contained agent
- **Extensibility through Tools**: Growth planned through MCP tool additions rather than protocol-level features
- **Performance Considerations**: Reduced overhead by avoiding ACP protocol layers

## Documentation References
- **Main Architecture**: Refer to the oh-my-pi architecture documentation
- **MCP Implementation**: See the MCP tool system details in the mcp-implementation documentation

## Conclusion
oh-my-it's deliberately **no-ACP approach** reflects its design as a focused, specialized coding agent. The project achieves agent communication through its comprehensive MCP tool system and memory management infrastructure, providing the core functionality needed for coding tasks without the complexity of full agent communication protocol support.

[[oh-my-pi-architecture]]
[[oh-my-pi-mcp-implementation]]