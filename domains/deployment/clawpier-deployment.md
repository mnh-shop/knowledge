---
name: clawpier-deployment
tags: [clawpier, deployment, tauri, desktop]
description: "ClawPier Deployment"
---
# ClawPier Deployment

| Field | Value |
|---|---|
| **Source** | `sources/clawpier/` |
| **Type** | Native desktop app (Tauri v2) |

## Installation

### macOS (Homebrew)

```bash
brew tap SebastianElvis/clawpier
brew install --cask clawpier
```

### Direct Download

Download the latest release from [GitHub Releases](https://github.com/SebastianElvis/clawpier/releases):

| Platform | Download |
|---|---|
| macOS (Apple Silicon) | `.dmg` (signed & notarized) |
| macOS (Intel) | `.dmg` (signed & notarized) |
| Linux (x86_64) | `.AppImage` or `.deb` |
| Windows (x86_64) | `.exe` installer or `.msi` |

### Prerequisites

- **Docker** must be installed and running (Docker Desktop on macOS/Windows, Docker Engine on Linux)
- Agent images pulled on first launch:
  - `ghcr.io/openclaw/openclaw:latest` (OpenClaw)
  - `nousresearch/hermes-agent:latest` (Hermes)

## Configuration

### Bot Profiles

Bot configurations are stored in `~/.clawpier/bots.json`. Each bot has:

```json
{
  "id": "uuid",
  "name": "My Bot",
  "agent_type": "OpenClaw",
  "image": "ghcr.io/openclaw/openclaw:latest",
  "network_enabled": false,
  "network_mode": "bridge",
  "port_mappings": [],
  "auto_start": false,
  "resource_limits": { "cpu_shares": 512, "memory_mb": 1024 },
  "env_vars": [{ "key": "OPENAI_API_KEY", "value": "..." }],
  "workspace_path": "/path/to/project",
  "health_check": { "enabled": true, "interval_secs": 30, "timeout_secs": 5 }
}
```

### Chat Sessions

Chat history is stored in `~/.clawpier/chat/` as JSON files, one per session.

### Import/Export

Bot configurations can be exported and imported as JSON or YAML from the GUI.

## Usage

### Creating a Bot

1. Click "New Bot"
2. Select agent type (OpenClaw or Hermes)
3. Configure name, image, resource limits
4. Set network mode (none by default)
5. Add environment variables (API keys, etc.)
6. Configure port mappings if network enabled
7. Save and start

### Resource Monitoring

Live CPU, memory, and network I/O per bot displayed in the dashboard.
Resource alerts trigger desktop notifications when limits are approached.

### ClawHub Skills

Browse, install, and manage OpenClaw community skills from the Skill Browser.
Requires an internet connection to connect to the ClawHub registry.

## Troubleshooting

### Docker Connection Issues

- Ensure Docker is running: `docker ps`
- Check Docker socket permissions: `ls -la /var/run/docker.sock`
- Restart ClawPier after starting Docker

### Bot Fails to Start

- Check Docker image is pulled: `docker images ghcr.io/openclaw/openclaw:latest`
- Verify API keys are set in bot env vars
- Check container logs: ClawPier LogViewer or `docker logs <container-id>`

### Permission Errors

- On Linux: ensure user is in `docker` group
- On macOS with Docker Desktop: ensure Docker Desktop is running
- Data directory: `~/.clawpier/` should be writable

## Security

### Default Sandbox

- All containers start with `--network none`
- Network access must be explicitly enabled per bot
- Port mappings only work when network is enabled

### Auto-start

Enable per-bot auto-start for persistent agents that should survive app restarts.

### Health Checks

Configure health checks with automatic restart on failure to recover from crashes.

## Related

- [[clawpier]] — Wiki entry
- [[clawpier-architecture]] — Architecture documentation
- [[clawpier-profile]] — Agent profile
- [[openclaw]] — Primary agent runtime
- [[hermes-agent]] — Secondary agent runtime
