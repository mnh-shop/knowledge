---
name: free-claude-code-mcp
description: "MCP server implementation in free-claude-code tools, resources, and configuration"
tags: [cli, documentation, mcp, rest-api]
---

# free-claude-code MCP Implementation

## Overview

The "free-claude-code" project does NOT implement a standalone MCP (Model Context Protocol) server. Instead, it acts as an **Anthropic Messages API proxy gateway** with MCP-related behaviors:

1. **MCP server passthrough** -- the `mcp_servers` field on Anthropic Messages requests is accepted and forwarded (or stripped) depending on provider type.
2. **MCP tool namespace preservation** -- tools with `mcp__` prefixed names (e.g., `mcp__node_repl__js`) pass through the proxy including their namespace metadata for downstream OpenAI Responses API consumers.
3. **Anthropic server tools** (`web_search`, `web_fetch`) are intercepted and handled locally via SSE, not via the MCP protocol.

## Request Model: mcp_servers Field

The `MessagesRequest` model at `api/models/anthropic.py` includes an `mcp_servers` field:

```python
class MessagesRequest(BaseModel):
    mcp_servers: list[dict[str, Any]] | None = None
```

This field is accepted on ingress and **IS serialized** to provider bodies for all Anthropic-native providers via `_dump_request_fields` in `core/anthropic/native_messages_request.py`. The `_REQUEST_FIELDS` tuple lists `"mcp_servers"` as a recognized request field that gets dumped into native request bodies for providers such as OpenRouter, DeepSeek, Fireworks, Wafer, Kimi, Z.ai, and others.

However, some providers **reject** `mcp_servers` at the pre-flight stage (see DeepSeek below), so the proxy cannot blindly forward it to every Anthropic-native provider.

## MCP Server Rejection on DeepSeek

DeepSeek's native Anthropic Messages transport **explicitly rejects** `mcp_servers`:

File: `providers/deepseek/request.py` (function `_validate_deepseek_native_request_dict`)

```
mcp = data.get("mcp_servers")
if mcp:
    raise InvalidRequestError(
        "DeepSeek native does not support mcp_servers on requests."
    )
```

This is tested in `tests/providers/test_deepseek.py`:

```python
def test_preflight_rejects_mcp_servers():
    request = MessagesRequest(
        model="m",
        messages=[Message(role="user", content="x")],
        mcp_servers=[{"type": "url", "url": "https://x"}],
    )
    ...
    with pytest.raises(InvalidRequestError, match="mcp_servers"):
        provider.preflight_stream(request)
```

## MCP Tool Namespace Support

The OpenAI Responses API adapter preserves MCP tool namespace metadata. In `tests/core/openai_responses/test_conversion.py`:

- Tools named `mcp__node_repl` with function `mcp__node_repl__js` are recognized.
- The `namespace` field (e.g., `"namespace": "mcp__node_repl"`) is preserved in the adapter's conversion output.
- `tool_choice` with MCP-namespaced tool names (e.g., `mcp__node_repl__js`) is correctly mapped.

## Anthropic Server Tools (Not MCP)

The proxy implements local `web_search` and `web_fetch` handlers that produce Anthropic SSE content blocks, not MCP protocol messages. These are configured via:

- `ENABLE_WEB_SERVER_TOOLS=true` (default: on)
- `WEB_FETCH_ALLOWED_SCHEMES=http,https`
- `WEB_FETCH_ALLOW_PRIVATE_NETWORKS=false`

The SSE content block types used for server tools are defined in `core/anthropic/server_tool_sse.py`:

```python
SERVER_TOOL_USE: Final = "server_tool_use"
WEB_SEARCH_TOOL_RESULT: Final = "web_search_tool_result"
WEB_FETCH_TOOL_RESULT: Final = "web_fetch_tool_result"
WEB_SEARCH_TOOL_RESULT_ERROR: Final = "web_search_tool_result_error"
WEB_FETCH_TOOL_ERROR: Final = "web_fetch_tool_error"
```

## Empty MCP Config for Managed Sessions

When the smoke test matrix runs Claude Code CLI tests, it passes an **empty MCP config** to avoid the client trying to connect to MCP servers:

```python
_EMPTY_MCP_CONFIG = '{"mcpServers":{}}'
```

This is injected as `--mcp-config '{"mcpServers":{}}'` in the CLI invocation for NVIDIA NIM CLI matrix tests.

## Key Files

| File | Role |
|---|---|
| `api/models/anthropic.py` | `MessagesRequest` model with `mcp_servers` field |
| `core/anthropic/native_messages_request.py` | Request field serialization (includes `mcp_servers`) |
| `providers/deepseek/request.py` | DeepSeek MCP server rejection |
| `core/anthropic/server_tool_sse.py` | Server tool SSE block type constants |
| `api/web_tools/streaming.py` | Local web_search/web_fetch streaming handler |
| `smoke/lib/claude_cli_matrix.py` | Empty MCP config for smoke tests |

## Summary

free-claude-code does not host its own MCP tools or resources. It is a gateway that:

- Passes through client-side MCP configurations to compliant providers
- Rejects MCP configs on providers that do not support them (DeepSeek)
- Preserves MCP tool name namespacing for the OpenAI Responses adapter
- Does NOT implement any MCP server endpoints or tool/resource listings
