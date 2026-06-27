---
name: pi-api
description: "Pi — no REST API (CLI-only tool)"
source: sources/pi/
tags: [api, cli, pi, typescript]
---

# Pi - API Implementation Status

## Conclusion

Pi is a **pure TypeScript/Node.js CLI-only coding agent** with **no REST API implementation**. It is fundamentally a command-line interface tool rather than a web service or API server that can be accessed over HTTP/S.

## What Pi Is Instead

Pi provides direct coding assistance through its **CLI surface** and includes the following core components:

- **[@earendil-works/pi-coding-agent](packages/coding-agent)**: Interactive coding agent CLI for terminal-based development
  - Interactive editing, file operations (read/write/edit), bash command execution
  - Session management with branching and history
  - 40+ LLM provider integration via unified API
- **[@earendil-works/pi-agent-core](packages/agent)**: Runtime engine for tool calling and state management
- **[@earendil-works/pi-ai](packages/ai)**: Multi-provider LLM API client
- **[@earendil-works/pi-tui](packages/tui)**: Differential terminal UI library

Pi operates entirely within the terminal context, accepting commands through its CLI interface and providing direct output to the user, rather than exposing HTTP endpoints.

## CLI Surface

### Core Commands

**Interactive Mode:**
```bash
pi [messages...]           # Interactive coding session
pi --name "my task"        # Named session
pi -p "Summarize"          # Print mode (non-interactive)
pi --model "anthropic/claude-3-5-sonnet-20241022"  # Specify model
pi --tools read,edit,bash  # Allow specific tools
```

**Session Management:**
```bash
pi -c                      # Continue most recent session
pi -r                      # Browse and select from past sessions
pi --session <id>          # Use specific session
pi --fork <id>             # Fork a previous session
pi --no-session            # Ephemeral mode (no saving)
```

**Package Management:**
```bash
pi install npm:@foo/pi-tools    # Install packages
pi list                        # List installed packages
pi update                       # Update pi and packages
pi config                       # Enable/disable package resources
```

**Provider & Model Management:**
```bash
/pi model                     # Model selector
/pi login                     # OAuth authentication
/pi scoped-models              # Enable/disable model cycling
```

### Built-in Tools

- `read` - Read file contents
- `write` - Write/create files
- `edit` - Edit files with AI assistance
- `bash` - Execute shell commands
- `grep` - Search files
- `find` - Find files
- `ls` - List directories

## Architecture Links

- [Pi Architecture](/architecture/pi/pi-architecture.md)

**Tags:** api, ai-llm, cli, pi, typescript

## Related

- [[api]]
- [[pi]]
