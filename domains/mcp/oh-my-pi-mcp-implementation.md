---
name: oh-my-pi-mcp-implementation
description: "oh-my-pi — MCP tool system via mnemopi package (30+ tools for memory management)"
source: sources/oh-my-pi/
tags: [acp, cli, coding-agent, mcp, oh-my-pi, rust, typescript]
---

# oh-my-pi MCP Tool Implementation

The oh-my-pi project implements a set of MCP (Model Control Protocol) tools via the `mnemopi` package, providing 30+ memory management tools for the coding agent system.

## Tool Architecture

### ToolDefinition Interface
The MCP tool system uses a structured `ToolDefinition` interface:

```typescript
interface ToolDefinition {
  readonly name: string;
  readonly description: string;
  readonly inputSchema: {
    readonly type: "object";
    readonly properties: Record<string, unknown>;
    readonly required?: readonly string[];
  };
}
```

This interface ensures all MCP tools follow a consistent pattern with type safety and schema validation.

### Handler Pattern
Tools are implemented as individual handler functions that follow the async `ToolArguments` → `ToolResult` pattern:

```typescript
type Handler = (args: ToolArguments) => ToolResult | Promise<ToolResult>;
```

The `TOOL_HANDLERS` record maps tool names to their corresponding handler functions, which are then invoked through the `handleToolCall(name: string, args: ToolArguments = {})` interface.

### Core MCP Tools

#### 1. `handleSharedRemember` (beam memory)
- **Description**: Stores compact cross-agent surface memory
- **Key Features**: Handles surface memory (meta, preference, correction, identity kinds)
- **Storage**: Uses BeamMemory for shared state management
- **Schema**: `SHARED_REMEMBER_SCHEMA` with content, kind, importance, and metadata

#### 2. `handleGraphQuery` (episodic graph findRelatedMemories)
- **Description**: Traverses the memory graph from a seed memory
- **Key Features**: Uses episodic graph for relationship tracking
- **Functions**: Calls `graph.findRelatedMemories()` to find related memories by ID
- **Parameters**: seed_memory_id, max_hops (default 2), edge_type, min_weight (default 0.0)

#### 3. `handleGraphLink` (addEdge)
- **Description**: Declares a semantic edge between two memories
- **Key Features**: Manages graph relationships in episodic graph
- **Functionality**: Calls `graph.addEdge()` to establish connections
- **Parameters**: source_id, target_id, relationship, weight (default 0.5)

### Other Key Tools
The TOOL array includes approximately 30 tools covering:

- **Memory Storage**: `mnemopi_remember`, `mnemopi_shared_remember`
- **Memory Retrieval**: `mnemopi_recall`, `mnemopi_shared_recall`
- **Memory Management**: `mnemopi_forget`, `mnemopi_update`, `mnemopi_invalidate`
- **Memory Validation**: `mnemopi_validate`, `mnemopi_diagnose`
- **Graph Operations**: `mnemopi_graph_query`, `mnemopi_graph_link`
- **Statistical Operations**: `mnemopi_stats`, `mnemopi_shared_stats`
- **Data Export/Import**: `mnemopi_export`, `mnemopi_import`
- **Scratchpad Operations**: `mnemopi_scratchpad_write`, `mnemopi_scratchpad_read`, `mnemopi_scratchpad_clear`
- **Temporal Triples**: `mnemopi_triple_add`, `mnemopi_triple_query`
- **Sleep/Consolidation**: `mnemopi_sleep`

## Architecture Comparison

### oh-my-pi MCP vs. Full MCP Servers

This implementation differs from full MCP servers like **OpenClaw** in several key ways:

**oh-my-pi**:
- Implements **30+ individual tools** rather than protocol endpoints
- Uses a **tool-based pattern** rather than a protocol server/client architecture
- Integrates with `BeamMemory` for memory management
- Provides a subset of memory management functionality
- Optimized as an **extension to the coding agent** rather than a standalone MCP server

**OpenClaw**:
- Exposes actual **protocol endpoints** via MCP protocol
- Full implementation of MCP specification with request/response patterns
- More comprehensive memory management capabilities
- Designed as a complete MCP server rather than agent extension

**Hermes MCP Implementation**:
- Similar tool-based approach but with different use cases and architecture
- Likely complementary implementations in the ecosystem

## System Components

- **BeamMemory**: Central memory management component providing persistent storage
- **Episodic Graph**: Manages memory relationships and semantic connections
- **BankManager**: Handles different memory bank isolation
- **Triples System**: Temporal fact storage and querying

## Implementation Pattern

The MCP tool system in oh-my-pi follows a **hosted tool model** where:

1. **Tool Definitions** are exported statically (`TOOLS` array)
2. **Handler Functions** manage the business logic
3. **Integration Layer** (`handleToolCall`) routes calls to appropriate handlers
4. **State Management** uses `BeamMemory` for persistence
5. **Error Handling** returns structured error responses in ToolResult format

## Key Insights

The oh-my-pi MCP implementation represents a **practical tool-based approach** to MCP integration, focusing on memory management utilities for the coding agent ecosystem. It demonstrates how MCP concepts can be adapted for specific use cases within a larger system.

[[oh-my-pi-architecture]]
[[pi-architecture]]
[[hermes-mcp-implementation]]
[[openclaw-mcp-implementation]]