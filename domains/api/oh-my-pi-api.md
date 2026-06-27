---
name: oh-my-pi-api
description: "oh-my-pi — no REST API (CLI-only coding agent)"
source: sources/oh-my-pi/
tags: [api, cli, coding-agent, oh-my-pi, rust, typescript]
---

# oh-my-pi API Implementation Status

## Conclusion

oh-my-pi is a **Rust/TypeScript hybrid CLI coding agent** with **no REST API implementation**. It is fundamentally a command-line interface tool rather than a web service or API server that can be accessed over HTTP/S.

## What oh-my-pi Is Instead

oh-my-pi provides direct coding assistance through its **CLI surface** and includes the following core components:

- **@oh-my-pi/pi-coding-agent**: Interactive coding agent CLI for terminal-based development
  - Interactive editing, file operations (read/write/edit), bash command execution
  - Session management with branching and history
  - 40+ LLM provider integration via unified API
- **@oh-my-pi/pi-agent-core**: Runtime engine for tool calling and state management
- **@oh-my-pi/pi-ai**: Multi-provider LLM API client
- **@oh-my-pi/pi-tui**: Differential terminal UI library

oh-my-pi operates entirely within the terminal context, accepting commands through its CLI interface and providing direct output to the user, rather than exposing HTTP endpoints.

## CLI Surface

### Core Commands

**Interactive Mode:**
```bash
omp [messages...]           # Interactive coding session
omp --name "my task"        # Named session
omp -p "Summarize"          # Print mode (non-interactive)
omp --model "anthropic/claude-3-5-sonnet-20241022"  # Specify model
omp --tools read,edit,bash  # Allow specific tools
```

**Session Management:**
```bash
omp -c                      # Continue most recent session
omp -r                      # Browse and select from past sessions
omp --session <id>          # Use specific session
omp --fork <id>             # Fork a previous session
omp --no-session            # Ephemeral mode (no saving)
```

**Package Management:**
```bash
omp install npm:@foo/omp-tools    # Install packages
omp list                        # List installed packages
omp update                       # Update oh-my-pi and packages
omp config                       # Enable/disable package resources
```

**Provider & Model Management:**
```bash
/omp model                     # Model selector
/omp login                     # OAuth authentication
/omp scoped-models              # Enable/disable model cycling
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

- [[oh-my-pi-architecture]]

**Tags:** api, ai-llm, cli, coding-agent, oh-my-pi, rust, typescript