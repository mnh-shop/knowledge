---
name: tank-os-mcp-implementation
description: "Tank OS — deploys service-gator MCP server as a sidecar (no native MCP implementation)"
source: sources/tank-os/
tags: [container-os, deployment, mcp, quadlet, tank-os]
---

# Tank OS — MCP Implementation

**Conclusion: Tank OS does not natively implement MCP, but it deploys the `service-gator` MCP server as a sidecar Quadlet.**

Tank OS is a bootc-based container OS. It runs `service-gator` as a second rootless Podman Quadlet owned by the `openclaw` user:

```
/etc/containers/systemd/users/1000/service-gator.container
```

## service-gator MCP Server

| Detail | Value |
|--------|-------|
| **Purpose** | Scoped access to external services (GitHub, GitLab, Forgejo, JIRA) |
| **Transport** | HTTP with MCP protocol |
| **Endpoint** | `http://127.0.0.1:8080/mcp` |
| **Runtime** | Rootless Podman Quadlet (separate from OpenClaw gateway) |
| **Auth** | No raw PATs exposed to OpenClaw agents |

The MCP server runs outside the gateway container so OpenClaw agents can consume its tools without receiving provider credentials directly.

### Configuration

Scopes are configured at `~/.config/service-gator/scopes.json`:

```json
{
  "scopes": {
    "gh": {
      "repos": {
        "myorg/myrepo": {
          "read": true,
          "push-new-branch": true
        }
      }
    }
  }
}
```

The scope file is watched for changes and can be reloaded without restarting.

## Related

- [[tank-os-architecture]] — Container OS architecture
- [[tank-os-deployment]] — Deployment guide
- [[quadlet-patterns]] — Quadlet deployment patterns
