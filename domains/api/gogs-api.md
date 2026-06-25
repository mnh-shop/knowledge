---
name: gogs-api
description: Gogs API
source: sources/gogs/
tags: [api, git, gogs, golang, rest-api, self-hosted, ssh, version-control, webhook]
---

# Gogs API

| Field | Value |
|---|---|
| **Source** | `sources/gogs/` |
| **Type** | REST API (experimental) |

## Overview

Gogs provides an experimental REST API for repository, user, organization, and issue management. Full documentation at https://gogs.io/api-reference.

## Authentication

API authentication via:
- **Token-based:** `Authorization: token <your_token>` header
- **Basic auth:** `Authorization: Basic <base64>` header
- Generated from user settings → Applications → Generate Access Token

## Key Endpoints

### Repositories

```
GET   /api/v1/repos/search       — Search repositories
GET   /api/v1/repos/:owner/:repo — Get repository details
POST  /api/v1/repos/migrate      — Migrate repository from external source
POST  /api/v1/user/repos         — Create repository
DELETE /api/v1/repos/:owner/:repo — Delete repository
GET   /api/v1/repos/:owner/:repo/raw/:filepath — Get raw file content
```

### Issues & Pull Requests

```
GET    /api/v1/repos/:owner/:repo/issues        — List issues
POST   /api/v1/repos/:owner/:repo/issues        — Create issue
GET    /api/v1/repos/:owner/:repo/issues/:index — Get issue
PATCH  /api/v1/repos/:owner/:repo/issues/:index — Edit issue
GET    /api/v1/repos/:owner/:repo/pulls         — List pull requests
```

### Webhooks

```
GET   /api/v1/repos/:owner/:repo/hooks       — List webhooks
POST  /api/v1/repos/:owner/:repo/hooks       — Create webhook
PATCH /api/v1/repos/:owner/:repo/hooks/:id   — Edit webhook
DELETE /api/v1/repos/:owner/:repo/hooks/:id  — Delete webhook
```

### Users & Organizations

```
GET  /api/v1/users/:username           — Get user profile
GET  /api/v1/users/:username/repos     — List user repos
GET  /api/v1/orgs/:orgname             — Get organization
GET  /api/v1/orgs/:orgname/repos       — List org repos
GET  /api/v1/orgs/:orgname/members     — List org members
```

### Admin

```
POST /api/v1/admin/users     — Create user (admin only)
PATCH /api/v1/admin/users/:username  — Edit user (admin only)
```

## API Versioning

The API is experimental and uses `/api/v1/` prefix. Endpoints and response schemas may change across Gogs releases.

## Integration

Gogs webhooks can be configured to fire on:
- Push events
- Issue creation/editing
- Pull request creation/merge
- Repository creation/deletion

Webhooks support JSON payload format and can target any HTTP endpoint (e.g., n8n webhook nodes).

## Related

- [[gogs]] — Wiki entry
- [[gogs-architecture]] — Architecture and component design
- [[gogs-deployment]] — Deployment options and configuration
