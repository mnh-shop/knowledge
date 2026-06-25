---
name: goclaw-acp
description: "GoClaw ACP agent communication protocol — subagent orchestration, agent teams, handoff"
tags: [acp, ai-llm, cli, documentation, mcp, orchestration, security]
---
# GoClaw ACP (Agent Communication Protocol) Implementation

**Source:** `/Users/admin1/Documents/knowledge/raw/goclaw/goclaw.xml`  
**Generated:** 2026-06-25

---

## Overview

GoClaw implements ACP (Agent Communication Protocol) -- a custom protocol for orchestrating external agents as subprocesses. ACP is similar in concept to MCP but designed for agent-to-agent communication rather than tool servers. It allows GoClaw to spawn and communicate with third-party AI agents (e.g., Gemini, Claude CLI) as child processes via JSON-RPC over stdin/stdout.

The implementation lives in `internal/providers/acp/` with the provider bridge in `internal/providers/acp_provider.go`.

---

## 1. Package Structure (`internal/providers/acp/`)

| File | Purpose |
|------|---------|
| `types.go` | All ACP protocol types (requests, responses, capabilities) |
| `jsonrpc.go` | JSON-RPC transport layer (`Conn`) -- read/write JSON-RPC messages over pipes |
| `session.go` | `ACPProcess` session management (Initialize, NewSession, Prompt, Cancel) |
| `process.go` | `ProcessPool` and `ACPProcess` -- subprocess lifecycle |
| `terminal.go` | Terminal sandbox (`Terminal`, `cappedBuffer`) for agent-created subprocesses |
| `tool_bridge.go` | `ToolBridge` -- handles tool requests from the ACP agent (FS, terminal, permissions) |
| `helpers.go` | `limitedWriter` utility |
| `sysproc_linux.go` | Linux-specific process attributes (setsid, Pdeathsig) |
| `sysproc_other.go` | Non-Linux process attributes |
| `acp_gemini_test.go` | Integration tests for Gemini agents via ACP |

---

## 2. ACP Protocol

### Transport

ACP uses **JSON-RPC 2.0** over stdin/stdout pipes to a child process. The `Conn` type in `jsonrpc.go` handles:

- Bidirectional JSON-RPC: both client-to-agent requests and agent-to-client requests/notifications
- Concurrent request dispatching via `sync.Map` for pending calls
- Notifications (fire-and-forget)
- Request handlers for agent-initiated calls

```go
type Conn struct {
    writer  io.Writer
    reader  io.Reader
    nextID  atomic.Int64
    pending sync.Map           // pending requests by ID
    handler RequestHandler     // handles agent-to-client requests
    notify  NotifyHandler      // handles agent-to-client notifications
    done    chan struct{}
}
```

### Protocol Phases

```
Client                          Agent
  |                               |
  |--- Initialize (request) ----->|  Protocol handshake
  |<--- Initialize (response) ----|  Capability negotiation
  |                               |
  |--- NewSession (request) ----->|  Create working session
  |<--- NewSession (response) ----|  Returns sessionID
  |                               |
  |--- Prompt (request) --------->|  Send prompt (streaming)
  |<--- SessionUpdate (notify) ---|  Mid-stream updates
  |<--- Prompt (response) ------->|  Final response
  |                               |
  |--- Cancel (notification) ---->|  Cancel active prompt
```

### Message Types

#### InitializeRequest / InitializeResponse (handshake)

```go
type InitializeRequest struct {
    ProtocolVersion int
    ClientInfo      ClientInfo      // name, version
    Capabilities    ClientCaps      // FS, Terminal capabilities
}

type InitializeResponse struct {
    AgentInfo    AgentInfo    // name, version
    Capabilities AgentCaps   // agent capabilities
}
```

Client capabilities:
- **FS**: `ReadTextFile`, `WriteTextFile` -- whether agent can read/write files through the bridge
- **Terminal**: `Enabled` -- whether agent can spawn terminal processes

Agent capabilities:
- **LoadSession**: Can reload existing sessions
- **PromptCapabilities**: `Audio`, `Image`, `EmbeddedContext`
- **SessionCapabilities**: Session management
- **MCPCapabilities**: `HTTP`, `SSE` -- agent can also use MCP

#### Session Management

```go
type NewSessionRequest struct {
    Cwd        string     // Working directory
    McpServers []string   // MCP servers to connect
}

type LoadSessionRequest struct {
    SessionID  string
    Cwd        string
    McpServers []string
}
```

#### Prompt

```go
type PromptRequest struct {
    SessionID string
    Prompt    []ContentBlock   // Multi-modal content
}

type ContentBlock struct {
    Type     string   // "text", "image", "audio"
    Text     string
    Data     string   // base64 for images/audio
    MimeType string
}

type PromptResponse struct {
    StopReason string   // "end_turn", "stop_sequence", etc.
}
```

#### Streaming Updates

During a prompt, the agent sends `SessionUpdate` notifications:

```go
type SessionUpdate struct {
    SessionID  string
    StopReason string
    Kind       string            // "message", "tool_call"
    Message    *MessageUpdate    // Text content delta
    ToolCall   *ToolCallUpdate   // Tool call with status
}
```

- `Kind: "message"` -- Streaming text content
- `Kind: "tool_call"` -- Tool call (with status: "in_progress" or "completed")
- Update entries for memory/log updates

#### Cancel

```go
type CancelNotification struct {
    SessionID string
}
```

Sent to cancel an in-progress prompt.

---

## 3. Process Management (`process.go`)

### ACPProcess

Represents a single ACP agent subprocess:

```go
type ACPProcess struct {
    cmd        *exec.Cmd
    conn       *Conn           // JSON-RPC connection
    agentCaps  AgentCaps       // Negotiated capabilities
    workDir    string
    lastActive time.Time
    inUse      atomic.Int32   // Active prompt count
    ctx        context.Context
    cancel     context.CancelFunc
    exited     chan struct{}
}
```

### ProcessPool

Manages a pool of ACP agent processes keyed by binary+args:

```go
type ProcessPool struct {
    processes   sync.Map       // map[string]*ACPProcess
    spawnMu     sync.Map       // Per-key spawn mutex
    agentBinary string
    agentArgs   []string
    workDir     string
    idleTTL     time.Duration  // Idle timeout for process reaping
    toolHandler RequestHandler  // Agent-initiated tool request handler
}
```

- `GetOrSpawn(ctx, poolKey)` -- Returns existing process or spawns a new one
- Spawns detect reaping: processes that have exited are respawned automatically
- `reapLoop()` -- Reaps processes idle beyond `idleTTL` (only when `inUse == 0`)
- `Close()` -- Gracefully shuts down all processes (5s timeout)

### Spawning

```go
func (pp *ProcessPool) spawn(ctx context.Context, poolKey string) (*ACPProcess, error)
```

1. Creates `exec.Cmd` with binary, args, and working directory
2. Sets process group attributes per platform (Linux: Pdeathsig, setsid)
3. Connects stdin/stdout pipes
4. Creates JSON-RPC `Conn` with the tool bridge as request handler
5. Sends `Initialize` and waits for `InitializeResponse`
6. Returns ready-to-use `*ACPProcess`

---

## 4. Session Lifecycle (`session.go`)

### Initialize

```go
func (p *ACPProcess) Initialize(ctx context.Context) error
```

- Sends `InitializeRequest` with version 1, client info, and client capabilities
- Receives `InitializeResponse` with agent info and capabilities
- Stores agent capabilities for later use

### NewSession

```go
func (p *ACPProcess) NewSession(ctx context.Context) (string, error)
```

- Sends `NewSessionRequest` with CWD
- Returns session ID from `NewSessionResponse`

### LoadSession

```go
func (p *ACPProcess) LoadSession(ctx context.Context, sessionID string) (string, error)
```

- Sends `LoadSessionRequest` with existing session ID
- Agent resumes the session
- Returns (possibly remapped) session ID

### Prompt

```go
func (p *ACPProcess) Prompt(ctx context.Context, sessionID string, content []ContentBlock, onUpdate func(SessionUpdate)) (*PromptResponse, error)
```

- Sends `PromptRequest` with session ID and content blocks
- Sets `inUse` flag (prevents reaping)
- Receives streaming `SessionUpdate` notifications and calls `onUpdate` for each
- Returns final `PromptResponse` with stop reason

### Cancel

```go
func (p *ACPProcess) Cancel(sessionID string) error
```

- Sends `CancelNotification` as JSON-RPC notification (fire-and-forget)

---

## 5. Tool Bridge (`tool_bridge.go`)

The `ToolBridge` handles agent-to-client requests -- when the ACP agent wants to use files, terminals, or request permissions.

```go
type ToolBridge struct {
    workspace      string                    // Sandboxed workspace path
    terminals      sync.Map                  // Active terminals
    denyPatterns   []*regexp.Regexp          // Shell deny patterns
    permMode       string                    // "approve_all", "deny_all", "approve_reads"
    nextTermID     atomic.Int64
    maxOutputBytes int                       // 1MB default
}
```

### Bridge Methods

| Method | Request | Response | Description |
|--------|---------|----------|-------------|
| `fs/readTextFile` | `ReadTextFileRequest` | `ReadTextFileResponse` | Read file (path-traversal checked) |
| `fs/writeTextFile` | `WriteTextFileRequest` | `WriteTextFileResponse` | Write file (creates subdirs) |
| `terminal/create` | `CreateTerminalRequest` | `CreateTerminalResponse` | Spawn terminal process |
| `terminal/output` | `TerminalOutputRequest` | `TerminalOutputResponse` | Read terminal output |
| `terminal/release` | `ReleaseTerminalRequest` | `ReleaseTerminalResponse` | Kill terminal process |
| `terminal/waitForExit` | `WaitForTerminalExitRequest` | `WaitForTerminalExitResponse` | Wait for terminal exit |
| `terminal/kill` | `KillTerminalRequest` | `KillTerminalResponse` | Force kill terminal |
| `permission/request` | `RequestPermissionRequest` | `RequestPermissionResponse` | Request permission for tool |

### Terminal Sandboxing

```go
var allowedTerminalBinaries = map[string]bool{
    "sh": true, "bash": true, "zsh": true, "fish": true,
    "node": true, "python": true, "python3": true, "ruby": true, "perl": true,
    "go": true, "cargo": true, "rustc": true, "gcc": true, "g++": true, "make": true,
    "git": true, "ls": true, "cat": true, "head": true, "tail": true,
    "grep": true, "rg": true, "find": true, "wc": true, "sort": true, "uniq": true,
    "diff": true, "patch": true, "mkdir": true, "cp": true, "mv": true, "touch": true,
    "echo": true, "printf": true, "env": true, "which": true, "whoami": true,
    "npm": true, "npx": true, "pnpm": true, "yarn": true, "bun": true,
    "pip": true, "pip3": true, "uv": true, "pipx": true,
    "docker": true, "kubectl": true,
    "curl": true, "wget": true, "jq": true, "yq": true,
    "tar": true, "gzip": true, "unzip": true,
    "sed": true, "awk": true, "xargs": true, "tee": true, "tr": true, "cut": true,
    "test": true, "true": true, "false": true,
}
```

Only binaries in this allowlist can be spawned as terminals through the bridge.

### Path Security

- `resolvePath()` -- Resolves and validates paths within workspace
- Path traversal attacks blocked (`../` escaping workspace)
- Absolute paths must be inside workspace
- Non-existent files allowed for write operations

### Permission Modes

| Mode | Behavior |
|------|----------|
| `approve_all` | All tool requests auto-approved |
| `deny_all` | All tool requests denied |
| `approve_reads` | Read operations approved, write/terminal denied |

---

## 6. Provider Integration (`internal/providers/acp_provider.go`)

### ACPProvider

Bridges ACP subprocess management with GoClaw's provider abstraction:

```go
type ACPProvider struct {
    name         string
    pool         *acp.ProcessPool
    bridge       *acp.ToolBridge
    defaultModel string
    permMode     string
    poolKey      string
    acpSessions  sync.Map        // goclawKey -> acpSessionEntry
    done         chan struct{}
}
```

### Creation

```go
func NewACPProvider(binary string, args []string, workDir string, idleTTL time.Duration, denyPatterns []*regexp.Regexp, opts ...ACPOption) *ACPProvider
```

- Creates `ProcessPool` and `ToolBridge` for the provider
- Configurable via `WithACPName`, `WithACPModel`, `WithACPPermMode`

### Session Lifecycle

- Sessions mapped by `goclawKey` = `agentID:runID`
- `resolveSession()` returns existing session or creates a new one
- `sessionReaper()` reaps sessions idle for >30 minutes

### Provider Interface

```go
func (p *ACPProvider) Chat(ctx context.Context, req ChatRequest) (*ChatResponse, error)
func (p *ACPProvider) ChatStream(ctx context.Context, req ChatRequest, onChunk func(StreamChunk)) (*ChatResponse, error)
```

- `extractACPContent()` converts GoClaw messages to `[]acp.ContentBlock`
- System prompts prepended to user messages
- `mapStopReason()` maps ACP stop reasons to GoClaw stop reasons

### Registration

Configured via config file or database:

```go
type ACPConfig struct {
    Binary    string   `json:"binary"`
    Args      []string `json:"args"`
    WorkDir   string   `json:"work_dir"`
    IdleTTL   string   `json:"idle_ttl"`
    PermMode  string   `json:"perm_mode"`
}
```

- `registerACPFromConfig()` -- Register from static config
- `registerACPFromDB()` -- Register from database provider records

---

## 7. Provider Type

ACP is registered as a provider type:

```go
ProviderACP = "acp"
```

Provider capabilities indicate runtime registration status:
```go
"acp": "ACP"
```

Supported provider types include `"acp"` alongside `"anthropic_native"`, `"openai_compat"`, `"gemini_native"`, etc.

---

## 8. UI Configuration

The admin UI includes an ACP configuration section at:
- `internal/http/providers.go` -- `provider-acp-section.tsx`
- Allows configuring binary path, arguments, work directory, permission mode

---

## 9. Related Files

- `cmd/gateway_providers.go` -- `registerACPFromConfig()`, `registerACPFromDB()`, `configuredShellDenyGroups()`, `configuredShellDenyPatterns()`
- `internal/providers/acp_provider.go` -- `ACPProvider`, session reaper, Chat/ChatStream implementation
- `internal/providers/adapter_anthropic.go` -- ACP lookup index migration
- `migrations/000023_agent_hard_delete_and_file_writer_merge.down.sql` -- ACP lookup index `idx_acp_lookup`
