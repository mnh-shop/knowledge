---
name: zot-deployment
description: "Zot deployment patterns — single-static-binary deployment, Telegram bot daemon, container images, Go compose patterns with agentfield, goclaw"
tags: [deployment, zot, golang]
source: sources/zot/
---

# Zot Deployment

Zot is a **single static Go binary** with zero runtime dependencies — no database, no HTTP server, no Node.js, no interpreter. This makes it one of the lightest deployment targets in the vault.

## Build

```bash
# Standard build
go build -o zot ./cmd/zot

# Production build with ldflags
go build -ldflags "
  -X main.version=0.0.1
  -X main.commit=$(git rev-parse HEAD)
  -X main.date=$(date -u +%Y-%m-%dT%H:%M:%SZ)
" -o zot ./cmd/zot

# Cross-compile (static binary)
GOOS=linux GOARCH=amd64 go build -o zot-linux-amd64 ./cmd/zot
GOOS=linux GOARCH=arm64 go build -o zot-linux-arm64 ./cmd/zot
```

## Deployment Patterns

### 1. Interactive TUI (local workstation)

The simplest deployment — just run the binary:

```bash
./zot --provider anthropic --model claude-sonnet-4-6
```

No daemonization needed. The TUI handles session persistence automatically via `$ZOT_HOME/sessions/`.

### 2. Telegram Bot Daemon

Run zot as a long-lived Telegram bot:

```bash
export ZOT_TELEGRAM_TOKEN="your-bot-token"
export ANTHROPIC_API_KEY="sk-ant-..."

# Start (runs until killed)
zot telegram --provider anthropic --model claude-opus-4-8 --max-steps 30

# As a systemd service
```

**systemd unit** (`/etc/systemd/system/zot-telegram.service`):

```ini
[Unit]
Description=Zot Telegram Bot
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/zot telegram --provider anthropic --model claude-sonnet-4-6
Environment=ANTHROPIC_API_KEY=sk-ant-...
Environment=ZOT_TELEGRAM_TOKEN=...
Restart=on-failure
RestartSec=5
User=zot

[Install]
WantedBy=multi-user.target
```

### 3. RPC Mode Daemon (for integration)

Run zot as an RPC service, consumed by other tools (goclaw, agentfield, custom orchestrators):

```bash
# Start RPC listener (stdin/stdout, designed for pipe embedding)
export ZOTCORE_RPC_TOKEN="shared-secret"
coproc zot rpc --provider anthropic --model claude-sonnet-4-6

# Or via named pipes / subprocesses
mkfifo /tmp/zot-rpc-in /tmp/zot-rpc-out
zot rpc < /tmp/zot-rpc-in > /tmp/zot-rpc-out &
```

### 4. Container Image

Ultra-lightweight container (zot + nothing else):

```dockerfile
FROM alpine:latest AS base
RUN apk add --no-cache ca-certificates tzdata

FROM scratch
COPY --from=base /etc/ssl/certs /etc/ssl/certs
COPY zot /bin/zot
ENTRYPOINT ["/bin/zot"]
```

Build: `docker build -t zot:latest .`

**Podman Quadlet** (`zot-telegram.container`):

```ini
[Container]
Image=zot:latest
Exec=-zot telegram --provider anthropic --model claude-sonnet-4-6
Environment=ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
Environment=ZOT_TELEGRAM_TOKEN=${ZOT_TELEGRAM_TOKEN}
Volume=%h/.local/share/zot:/root/.local/share/zot:Z
Network=host
AutoUpdate=registry

[Service]
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

### 5. Composable Go Stack (with agentfield, goclaw)

Zot's Go SDK makes it embeddable alongside other Go services:

**Agentfield + Zot**: Agentfield spawns zot as a coding sub-agent inside a micro-VM sandbox. agentfield manages the sandbox lifecycle; zot provides the LLM coding capabilities.

**GoClaw + Zot**: GoClaw wires zot as an RPC tool bridge. GoClaw's tool management system discovers zot's capabilities and exposes them to its own orchestration layer.

```
┌──────────────────────────────────────────────────┐
│                  goclaw                          │
│  ┌──────────────────────────────────────────┐   │
│  │           Tool Bridge                     │   │
│  │  ├── read/write/edit/bash (built-in)      │   │
│  │  └── zot_rpc (via pipe → zot rpc)        │   │
│  └──────────────────────────────────────────┘   │
└──────────────────┬───────────────────────────────┘
                   │ stdin/stdout pipe
┌──────────────────┴───────────────────────────────┐
│                 zot rpc                          │
│  ├── provider: anthropic/openai/groq/xai/...     │
│  ├── tools: read, write, edit, bash              │
│  └── exts: user-defined extension binaries       │
└──────────────────────────────────────────────────┘
```

Or embedded directly in Go:

```go
import "github.com/patriceckhart/zot/packages/agent/sdk"

// agentfield/goclaw embeds zot for coding tasks
type ZotWorker struct {
    rt *sdk.Runtime
}

func NewZotWorker(apiKey string) (*ZotWorker, error) {
    rt, err := sdk.New(sdk.Config{
        Provider: "anthropic",
        Model:    "claude-sonnet-4-6",
        APIKey:   apiKey,
        Tools:    []string{"read", "write", "edit", "bash"},
    })
    return &ZotWorker{rt: rt}, err
}

func (w *ZotWorker) Code(ctx context.Context, task string) (string, error) {
    resp, err := w.rt.Chat(ctx, task)
    if err != nil {
        return "", err
    }
    return resp.Text, nil
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | For Anthropic | Anthropic Messages API key |
| `OPENAI_API_KEY` | For OpenAI | OpenAI API key |
| `ZOT_TELEGRAM_TOKEN` | For Telegram | Telegram Bot token |
| `ZOTCORE_RPC_TOKEN` | For RPC auth | Auth token for RPC mode |
| `ZOT_HOME` | Optional | Data directory (default `~/.local/share/zot`) |
| Provider-specific | Varies | Per-provider API key env vars |

## Resource Profile

- **Binary size**: ~20MB (static Go binary, no external runtime)
- **Memory**: ~50-200MB during inference (LLM response buffering)
- **Disk**: ~1-10MB for session transcripts (configurable)
- **CPU**: Minimal outside LLM API calls (no local inference)

## Extension Distribution

Extensions are discovered from `$ZOT_HOME/extensions/`:
- Each extension is its own binary
- Place in `$ZOT_HOME/extensions/<name>/` or install via `zot ext install <path>`
- Hot-reload with `/reload-ext` without restarting zot

## Related Documentation

- [[zot-architecture]] — Full architecture doc
- [[zot-mcp-implementation]] — Extension protocol details
- [[zot-api]] — Telegram bot and RPC API
- [[goclaw-api]] — GoClaw API (RPC consumer)
- [[agentfield-architecture]] — Agentfield sandbox (Go composition)
- [[quadlet-deployment-guide]] — Podman Quadlet patterns
- Source: `sources/zot/`
