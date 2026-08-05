---
name: hermes-workspace-security
tags: [agent-gateway, audit, dashboard, desktop, hermes-agent, mcp, security, typescript]
description: "Hermes Workspace security model: auth-middleware, rate limiting, SSRF guard, path-traversal guard, fail-closed remote bind, cookie flags"
source: sources/hermes-workspace/
---

# Hermes Workspace — Security Model

**Source:** `sources/hermes-workspace/`
**Codegraph:** `graphs/hermes-workspace/`

Hermes Workspace is a loopback-first web control plane for Hermes Agent.
Its security posture is **fail-closed by default**: auth middleware on every
route, rate limiting, path-traversal prevention, an SSRF guard in the MCP
Hub, and a startup guard that refuses to bind non-loopback interfaces
without a password. See README.md:672-696 for the canonical summary.

## Built-in safeguards (README.md:680-683)

- Auth middleware on every API route
- CSP headers via meta tags
- Path-traversal prevention on file/memory routes (real-path boundary check,
  not string prefix)
- Rate limiting on endpoints
- Fail-closed startup guard: refuses to bind non-loopback without
  `HERMES_PASSWORD`
- Session cookies: `HttpOnly` + `SameSite=Strict` + `Secure` (in production)
- Optional password protection for the web UI

## Auth middleware — `src/server/auth-middleware.ts`

Single module (9,101 bytes) implementing the whole session/auth layer:

| Function | Role |
|---|---|
| `generateSessionToken` / `storeSessionToken` / `revokeSessionToken` | Token lifecycle; persistent store at `~/.hermes/workspace-sessions.json` (30-day TTL, in-memory + JSON persistence) |
| `isValidSessionToken` | Timing-safe session validation |
| `getConfiguredPassword` / `verifyPassword` | `HERMES_PASSWORD` (legacy `CLAUDE_PASSWORD` honored) using `timingSafeEqual` |
| `isPasswordProtectionEnabled` | Password gate on/off |
| `getRequestIp` / `isTrustedProxyEnabled` | IP classification; `TRUST_PROXY=1` trusts `x-forwarded-for`/`x-real-ip` (only behind a sanitizing proxy) |
| `isLocalRequest` / `requireLocalOrAuth` | Loopback allowlist (`127.0.0.1`, `::1`, `localhost`, `::ffff:127.0.0.1`) — local requests pass, remote requests must authenticate |
| `createSessionCookie` / `shouldSetSecureCookie` | Cookie flags |

**Cookie flags** (auth-middleware.ts:297-306): `HttpOnly` (blocks JS access,
mitigates XSS session theft) + `Secure` (HTTPS only, production default) +
`SameSite=Strict` (CSRF protection) + `Path=/` + 30-day `Max-Age`.

**Fail-safe behavior:** falls back to loopback-only when no auth is
available (auth-middleware.ts:230) — fails *safe*, never open.

## Fail-closed remote bind

The workspace refuses to bind non-loopback interfaces unless a password is
set (README.md:682). Env vars:

- `HERMES_PASSWORD` — required whenever `HOST ≠ 127.0.0.1`
- `HERMES_ALLOW_INSECURE_REMOTE=1` — bypass the fail-closed guard (not
  recommended, README.md:694)
- `COOKIE_SECURE=0` — disable `Secure` flag for plain-HTTP LAN deployments
  (`HOST=0.0.0.0` without HTTPS); without it browsers silently drop session
  cookies (#149)

The conservative loopback check also appears in
`src/server/gateway-capabilities.ts:542-556` — capability gating only trusts
loopback-resolved gateway URLs.

## Rate limiting — `src/server/rate-limit.ts`

Zero-dependency in-memory sliding-window limiter (`rateLimit(key,
maxRequests, windowMs)`), 2-minute janitor sweep, per-key timestamp store.
Covered by `src/server/rate-limit.test.ts`.

## SSRF guard — `src/server/mcp-hub/lib/ssrf-guard.ts`

Protects the MCP Hub `generic-json` adapter (the one that fetches
user-defined source URLs):

- Resolves **all A/AAAA records** for a hostname before fetching
  (`node:dns/promises`)
- Rejects any URL resolving to **private, loopback, or link-local** ranges
- Stateless (no cross-process locking needed); tested in
  `ssrf-guard.test.ts`

## Path-traversal guard — `src/routes/api/files.ts`

Real-path boundary check rather than string-prefix matching
(README.md:680):

- `path.resolve(raw)` / `path.resolve(workspaceRoot, raw)` (files.ts:51-52)
- Rejects when `relative.startsWith('..')` (files.ts:57)
- `src/routes/api/preview-file.ts` additionally scopes reads to allowed
  roots (`~/.hermes`, `dispatch/`, `projects/`).

## Env var surface for remote / Docker (README.md:686-694)

| Var | Effect |
|---|---|
| `HERMES_PASSWORD` | Required when `HOST ≠ 127.0.0.1` (legacy `CLAUDE_PASSWORD` fallback) |
| `COOKIE_SECURE=1` | Force `Secure` cookie flag when terminating HTTPS at a proxy |
| `COOKIE_SECURE=0` | Drop `Secure` for plain-HTTP LAN |
| `TRUST_PROXY=1` | Trust `x-forwarded-for` / `x-real-ip` (sanitizing proxy only) |
| `HERMES_DASHBOARD_TOKEN` | Explicit bearer for dashboard API (preferred over legacy HTML-scrape fallback) |
| `HERMES_API_TOKEN` | Bearer for Hermes Agent gateway started with `API_SERVER_KEY` (legacy `CLAUDE_API_TOKEN` honored) |
| `HERMES_ALLOW_INSECURE_REMOTE=1` | Bypass fail-closed guard (not recommended) |

## Threat model notes

- **Remote binding** is opt-in and gated on a password; loopback is the
  default posture.
- **MCP Hub** is the primary SSRF attack surface (user-supplied source URLs)
  — mitigated by the DNS-level guard in `ssrf-guard.ts`.
- **Session theft** mitigated by `HttpOnly` + `SameSite=Strict` + rotating
  30-day tokens; multi-worker deployments should swap the JSON session store
  for Redis/DB (auth-middleware.ts header note).
- Credits: security audit by [@kiosvantra](https://github.com/kiosvantra)
  surfaced #121-#125 (README.md:696).

## Related

- [[hermes-workspace]] -- Wiki entry
- [[hermes-workspace-architecture]] -- System architecture
- [[hermes-workspace-features]] -- Feature inventory
- [[hermes-workspace-api]] -- REST API reference
- [[hermes-workspace-mcp-hub]] -- MCP hub implementation
- [[hermes-workspace-deployment]] -- Deployment guide
- [[openclaw-security]] -- Comparable security model for OpenClaw
