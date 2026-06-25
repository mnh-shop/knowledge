---
name: agentfield-acp-implementation
tags: [acp, agent-communication, agentfield, ai-llm, cli, did-vc, plugin-sdk, webhook]
description: "AgentField's agent-to-agent communication system: routing, identity, authorization, and execution model"
---

# AgentField ACP Implementation

**Source:** `sources/agentfield/` (control-plane Go, SDK Python/Go/TypeScript)

AgentField does not implement an external ACP standard. It provides a **custom agent-to-agent communication system** built on DID-based cryptographic identity, tag-based access policies, Verifiable Credentials (VCs), and a centralized control plane for routing, observability, and workflow orchestration.

---

## 1. Communication Model

### Call Pattern

Agents call each other through the control plane. There is **never direct agent-to-agent HTTP**.

```python
# Python SDK
result = await app.call("other-agent.function_name", input={...})
```

```go
// Go SDK
result, err := agent.Call(ctx, "other-agent.function_name", input)
```

```typescript
// TypeScript SDK
const result = await agent.call("other-agent.function_name", { input });
```

### Target Format

- **Call format (dot-separated):** `agent_id.reasoner_name` or `agent_id.skill_name`
- **Discovery format (colon-separated):** `node_id:function_name` for reasoners, `node_id:skill:function_name` for skills
- SDK `_invocation_target_to_call_target()` converts colon-separated discovery targets to dot-separated call targets, replacing colons with double-underscores for LLM tool name compatibility

### Routing Flow

1. SDK sends `POST /api/v1/execute/{agent_id}.{function_name}` to the control plane
2. Control plane parses target via `parseTargetParam("agent_id.function_name")`
3. Permission middleware evaluates tag-based access policies
4. DID auth middleware verifies Ed25519 signature from caller
5. Control plane forward-proxies the execution request to the target agent's callback URL
6. Result propagates back through the control plane
7. Control plane records execution in the workflow DAG, injects metrics, propagates context headers

### Execution Modes

| Mode | Endpoint | Behavior |
|------|----------|----------|
| Sync | `POST /api/v1/execute/:target` | Blocks until completion (180s timeout, configurable) |
| Async | `POST /api/v1/execute/async/:target` | Returns `execution_id` immediately; poll via `GET /api/v1/executions/:id` |
| Async with webhook | Same as async + `webhook: {url: "..."}` | Control plane POSTs result to webhook URL |
| Batch | `POST /api/v1/executions/batch-status` | Poll multiple execution statuses at once |

### Execution Context Propagation

These HTTP headers are forwarded through the cross-agent call chain:

| Header | Purpose |
|--------|---------|
| `X-Run-ID` | Workflow run tracking |
| `X-Workflow-ID` | Workflow DAG identification |
| `X-Execution-ID` | Specific execution trace ID |
| `X-Parent-Execution-ID` | Parent-child call tree linkage |
| `X-Session-ID` | Multi-turn session tracking |
| `X-Actor-ID` | Actor identity |
| `X-Caller-DID` | DID of the calling agent |
| `X-Target-DID` | DID of the target agent |
| `X-Routed-Version` | Version traffic routing |
| `X-Caller-Agent-ID` | Agent node ID for memory access control |
| `X-Agent-Roles` | Agent roles for access control evaluation |
| `X-Team-ID` | Team ID for team-restricted memory access |

---

## 2. Cryptographic Identity (DID)

Every agent gets a W3C Decentralized Identifier (DID). Identity is opt-in per agent.

### DID Methods

| Method | Characteristics |
|--------|----------------|
| `did:web` (primary) | DID resolves to URL: `did:web:{domain}:agents:{agentID}`. Control plane hosts DID document. Real-time revocation (return 404 or revoked status). Verifiers fetch fresh public key on each verification. |
| `did:key` (supported) | DID derived from public key: `did:key:z6MkpTHR8VNs...`. Self-contained, no external resolution. Cannot be revoked -- only time-based expiry. |

### Key Hierarchy (3-Tier)

1. **Platform DID** -- The control plane itself (issuer DID for VCs)
2. **Node DID** -- Per registered agent (derived from master seed + BIP32)
3. **Function DID** -- Per reasoner/skill (derived from node DID)

### Key Generation

- Algorithm: Ed25519 + BIP32 derivation
- Keystore encryption: AES-256-GCM
- Master seed: `AGENTFIELD_AUTHORIZATION_MASTER_SEED` (must be stable across restarts)

### DID Registration

```
POST /api/v1/did/register
```
- Body: `{"agent_id": "...", "public_key_jwk": {...}}`
- Returns: `DIDIdentityPackage` with per-component keys
- Auto-registers DID document at Web resolution URLs
- Optionally generates Verifiable Credentials for agent tags

### DID Auth Headers (Cross-Agent Calls)

Every cross-agent call carries:

| Header | Description |
|--------|-------------|
| `X-Caller-DID` | The caller's W3C DID |
| `X-DID-Signature` | Ed25519 signature over `{timestamp}:{SHA256(body)}` |
| `X-DID-Timestamp` | Signing timestamp (300s window via `timestamp_window_seconds`) |
| `X-DID-Nonce` | Optional replay protection nonce (deduped in memory cache within window) |

---

## 3. Authorization System

### Tag-Based Access Policies

Access policies define tag-based authorization rules for cross-agent calls with function-level allow/deny lists and parameter constraints.

```yaml
# agentfield.yaml
features:
  did:
    authorization:
      access_policies:
        - name: finance_to_billing
          caller_tags: ["finance"]
          target_tags: ["billing"]
          allow_functions: ["charge_*", "refund_*", "get_*"]
          deny_functions: ["delete_*", "admin_*"]
          constraints:
            amount:
              operator: "<="
              value: 10000
          action: allow
          priority: 10

        - name: support_readonly
          caller_tags: ["support"]
          target_tags: ["customer-data"]
          allow_functions: ["get_*", "query_*"]
          action: allow
          priority: 5
```

### Policy Fields

| Field | Description |
|-------|-------------|
| `name` | Unique policy name |
| `caller_tags` | Tags the calling agent must have (empty = any) |
| `target_tags` | Tags the target agent must have (empty = any) |
| `allow_functions` | Whitelist of callable functions (supports wildcards) |
| `deny_functions` | Blacklist of functions (checked first, overrides allow) |
| `constraints` | Parameter-level constraints (e.g., `amount <= 10000`) |
| `action` | `"allow"` or `"deny"` -- the decision when all conditions match |
| `priority` | Higher priority policies evaluated first |
| `enabled` | Toggle without deletion |

### Evaluation Algorithm (First-Match-Wins)

1. Policies sorted by `priority DESC, id ASC` (deterministic ordering)
2. For each enabled policy:
   - Check caller tags match (empty policy tags = wildcard)
   - Check target tags match
   - Check deny functions -- if matched, **immediately deny**
   - Check allow functions -- if list exists but function not in it, skip policy
   - Evaluate constraints -- missing parameters or violations cause deny (fail-closed)
   - All checks pass -> return `Allowed = (action == "allow")`
3. No matching policy -> return `Matched: false` (request allowed for backward compatibility, or denied if `default_deny: true`)

### Constraint Operators

`<=`, `>=`, `<`, `>`, `==`, `!=`
- Numeric comparison for numeric values
- String comparison (`==`/`!=`) as fallback
- Missing parameters in input -> deny (fail-closed)

### Policy Evaluation Result

```go
type PolicyEvaluationResult struct {
    Allowed    bool   // Whether access is granted
    Matched    bool   // Whether any policy matched
    PolicyName string // Which policy matched
    PolicyID   int64
    Reason     string // Human-readable explanation
}
```

### Endpoints Protected by Permission Middleware

- `POST /api/v1/execute/:target` and `POST /api/v1/execute/async/:target`
- `POST /api/v1/reasoners/:reasoner_id`
- `POST /api/v1/skills/:skill_id`
- `POST /api/v1/session-targets/:target/start`

Memory endpoint authorization uses a separate `middleware.MemoryPermissionMiddleware()` with scope ownership enforcement.

---

## 4. Verifiable Credentials (VCs)

### AgentTagVC (Per-Agent)

Issued when admin approves an agent's tags. Certifies which tags an agent is authorized to hold. Signed with Ed25519 by the control plane issuer DID.

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiableCredential", "AgentTagCredential"],
  "id": "urn:agentfield:agent-tag-vc:550e8400-e29b-41d4-a716-446655440000",
  "issuer": "did:web:localhost%3A8080:agents:control-plane",
  "issuanceDate": "2026-02-08T10:30:00Z",
  "credentialSubject": {
    "id": "did:web:localhost%3A8080:agents:finance-bot",
    "agent_id": "finance-bot",
    "permissions": {
      "tags": ["finance", "payment"],
      "allowed_callees": ["*"]
    },
    "approved_by": "admin",
    "approved_at": "2026-02-08T10:30:00Z"
  },
  "proof": {
    "type": "Ed25519Signature2020",
    "created": "2026-02-08T10:30:00Z",
    "verificationMethod": "did:web:localhost%3A8080:agents:control-plane#key-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "s6mNf...XkMg=="
  }
}
```

**Key fields:**
- `credentialSubject.id` -- Agent's DID (cryptographic identity)
- `credentialSubject.permissions.tags` -- Approved tags (what the agent is authorized to claim)
- `proof` -- Ed25519 signature from control plane issuer; falls back to `UnsignedAuditRecord` if issuer DID unavailable

**Verification at call time (`TagVCVerifier`):**
1. Load VC record from storage
2. Check revocation (`revoked_at` timestamp)
3. Check expiration (`expires_at` timestamp)
4. Parse VC document from JSON
5. Verify Ed25519 signature against issuer public key
6. Validate subject binding (VC agent ID matches requested agent)

If VC verification succeeds, the permission middleware uses **VC-verified tags** (cryptographic proof). If VC exists but verification fails (revoked/expired/invalid), the middleware uses **empty tags** (fail-closed security).

### VC Configuration

```yaml
features:
  did:
    vc:
      require_vc_registration: true    # VC required for agent registration
      require_vc_execution: true       # VC required for all executions
      require_vc_cross_agent: true     # VC required for cross-agent calls
      store_input_output: false        # Store execution I/O in VC records
      hash_sensitive_data: true        # Hash sensitive data before storing
      persist_execution_vc: true       # Persist VCs to database
```

### Agent Tag Approval Flow

- Agents register with requested tags (e.g., `tags=["finance", "payment"]`)
- If `tag_approval_mode: admin`, the agent stays in `pending_approval` status
- `pending_approval` agents cannot be called -- permission middleware returns 503
- Admin approves/rejects tags via UI or API endpoints
- Tag VC is issued upon approval, agent transitions to `ready`
- Revoked tags force agent back to `pending_approval`

### VC Hierarchy (3 Tiers)

| Tier | Scope | Purpose |
|------|-------|---------|
| Platform VC | Control plane issuer | Root trust anchor |
| Node VC (AgentTagVC) | Per registered agent | Approved tags, allowed callees |
| Execution VC | Per execution run | Tamper-proof execution receipt |

---

## 5. Local (Offline) Verification

SDKs implement a `LocalVerifier` that caches policies and DID state from the control plane, enabling offline signature verification without round-tripping on every call.

### Cached Data (Refreshed Every 5 Minutes)

- **Access policies** -- fetched from `GET /api/v1/policies`
- **Revocation list** -- fetched from `GET /api/v1/revocations`
- **Registered DIDs** -- fetched from `GET /api/v1/registered-dids`
- **Admin public key** -- fetched from `GET /api/v1/admin/public-key`

### Local Verification Steps

1. Check caller DID not in revocation list
2. Validate timestamp within window (default 300 seconds)
3. Verify Ed25519 signature using cached admin public key
4. Evaluate policies locally using cached rules
5. Check parameter constraints

### Opt-Out Per Function

Functions marked with `require_realtime_validation=True` bypass local verification and forward to the control plane:

```python
@app.reasoner(require_realtime_validation=True)
async def high_security_operation(input_data):
    ...
```

### Fail-Closed Behavior

- No policies cached -> deny access
- VC verification fails -> empty tags used (no tag-based policies match)

---

## 6. Did Auth Error Responses

| HTTP | Error Code | Condition |
|------|-----------|-----------|
| 401 | `did_auth_required` | No `X-Caller-DID` header provided |
| 401 | `signature_required` | `X-Caller-DID` present but no `X-DID-Signature` |
| 401 | `signature_invalid` | Ed25519 signature verification failed |
| 403 | `did_revoked` | Caller's DID is on the revocation list |
| 403 | `did_not_registered` | DID not found in the control plane's registration set |
| 403 | `policy_denied` | No matching policy or denied by tag policy |

---

## 7. Execution Lifecycle

```
queued -> running -> completed|failed|paused|cancelled
```

| Endpoint | Action |
|----------|--------|
| `POST /api/v1/executions/:execution_id/status` | Status callback (agent to control plane) |
| `POST /api/v1/executions/:execution_id/cancel` | Cancel a running execution |
| `POST /api/v1/executions/:execution_id/pause` | Pause for human approval |
| `POST /api/v1/executions/:execution_id/resume` | Resume after human approval |
| `POST /api/v1/executions/:execution_id/restart` | Restart an execution |
| `POST /api/v1/executions/:execution_id/events` | SSE stream of execution events |
| `POST /api/v1/workflows/:workflowId/cancel-tree` | Cancel entire multi-hop DAG |

### Approval Flow (Human-in-the-Loop)

1. Agent calls `app.pause("Explain reasoning before proceeding")`
2. Control plane marks execution as `paused`
3. External system or human reviews via `POST /executions/:id/request-approval`
4. Resolution posted to `POST /api/v1/webhooks/approval-response`
5. Control plane resumes the execution

### Error Propagation

Agent-to-agent failures propagate with:
- Status code: 502 (Bad Gateway)
- Error details with `error_details` field
- Empty `caller_agent_id` fixed on re-approval
- Re-approval deadlock fix: only triggered for empty status, not revoked/rejected

---

## 8. SDK Implementations

### Python SDK

- Location: `sdk/python/agentfield/`
- Agent class extends `FastAPI`
- Auto-generates REST endpoints from decorators (`@app.reasoner()`, `@app.skill()`)
- `app.call()` routes through `AgentFieldClient.execute()`
- DID auth: `did_auth.py` (Ed25519 signing)
- Local verification: `verification.py` (async refresh)
- Serverless mode: `agent_serverless.py` (Lambda/Cloud Functions)

### Go SDK

- Location: `sdk/go/`
- Uses `http.ServeMux` internally
- Router API: `sdk/go/agent/router.go` with `IncludeRouter()` for nesting
- `agent.Call()` in `client/did_auth.go`
- DID/DID manager: `did/did_client.go`, `did/did_manager.go`
- Local verifier: `agent/verification.go`

### TypeScript SDK

- Location: `sdk/typescript/`
- `npm install @agentfield/sdk`
- Idempotent Node.js interface
- DID auth: `LocalVerifier.ts` (registered DID caching, nonce-aware verification)

---

## 9. Agent-to-Agent Direct Verification (CHANGELOG)

Added SDK `LocalVerifier` modules that cache policies, revocation lists, registered DIDs, and admin public key from the control plane. Enables offline signature verification without round-tripping. Added `/api/v1/registered-dids` endpoint. Supports nonce-based signatures and `did:key` public key resolution.

Key bugs fixed in the ACP interaction:
- Re-approval deadlock: Re-approval only triggered for empty status, not revoked/rejected
- Empty `caller_agent_id` and error propagation (200 -> 502 for agent-to-agent failures)
- Python SDK DID auth: pass pre-serialized JSON string to axios to ensure signed bytes match wire format

## 10. Related

- [[agentfield-api]] -- REST API reference including all ACP endpoints
- [[agentfield-architecture]] -- system architecture
- [[agentfield-mcp-implementation]] -- MCP integration (historical)
