---
name: openclaw-plugins
tags: [agent-gateway, cli, clawhub, hooks, mcp, npm, openclaw, plugin-sdk, providers, typescript]
description: OpenClaw Plugins
source: sources/openclaw/
---

# OpenClaw Plugins
**Source:** `sources/openclaw/`

OpenClaw's plugin system is one of the most complex subsystems. It supports bundled plugins shipped in `extensions/` and third-party/community plugins installed via ClawHub, npm, or git. The public contract between plugins and core is the Plugin SDK (`src/plugin-sdk/`); the loader, manifest, install, registry, and hooks machinery lives in `src/plugins/`.

## Plugin SDK

The Plugin SDK (`src/plugin-sdk/`) is the public contract between plugins and core, exposed through narrow subpaths (plugins import from `openclaw/plugin-sdk/*`, never from core internals). `scripts/lib/plugin-sdk-entrypoints.json` declares **321 SDK entrypoints**. Major families:

- **Channel contract** — `channel-entry-contract.ts`, `channel-core.ts`, `channel-plugin-common.ts`, `channel-pairing.ts`, `channel-setup.ts`, `channel-streaming.ts`, `channel-targets.ts`, `channel-message.ts`, `channel-inbound.ts`, `channel-outbound.ts`, `channel-reply-pipeline.ts`, `channel-lifecycle.ts`, `channel-status.ts`, `channel-dm-policy.ts`, `channel-mention-gating.ts`
- **Provider contract** — `provider-entry.ts`, `provider-auth.ts`, `provider-oauth-runtime.ts`, `provider-setup.ts`, `provider-stream.ts`, `provider-tools.ts`, `provider-catalog-runtime.ts`, `provider-model-types.ts`, `provider-transport-runtime.ts`
- **Approval** — `approval-runtime.ts`, `approval-approvers.ts`, `approval-renderers.ts`, `approval-reply-runtime.ts`, `approval-gateway-runtime.ts`, `approval-reaction-runtime.ts`, `exec-approvals-runtime.ts`
- **Session** — `session-store-runtime.ts`, `session-key-runtime.ts`, `session-visibility.ts`, `session-catalog-runtime.ts`, `session-transcript-runtime.ts`, `session-binding-runtime.ts`, `model-session-runtime.ts`
- **Memory host** — `memory-core-host-runtime-*.ts`, `memory-core-host-engine-*.ts`, `memory-host-search.ts`, `memory-host-events.ts`, `memory-host-markdown.ts`
- **Standalone modules** — `sandbox.ts`, `agent-harness.ts`, `agent-harness-runtime.ts`, `acp-runtime.ts`, `acp-binding-runtime.ts`, `browser-*.ts`, `media-*.ts`, `skill-commands-runtime.ts`, `plugin-entry.ts`, `tool-plugin.ts`, `webhook-ingress.ts`, `cron-store-runtime.ts`

`src/plugin-sdk/core.ts` and `src/plugin-sdk/plugin-entry.ts` define the core entry pattern: `definePluginEntry({ id, name, description, configSchema, register(api) })` with a typed `OpenClawPluginApi`.

## Manifest Contract and Loader Lifecycle

- **Manifest** — `manifest.json5` validated by `src/plugins/manifest.ts` and `manifest-types.ts` with `id`, `version`, `capabilities`, `hooks`, `tools`, `entrypoints`, and `min-host-version` compatibility enforcement (`min-host-version.ts`).
- **Loader** — `src/plugins/loader*.ts` (loader.ts, loader-discovery.ts, loader-runtime-*.ts, loader-records.ts, loader-provenance.ts, loader-cache.ts) implements discovery (bundled dirs, npm packages, git repos, local paths), manifest validation, dependency order planning, and runtime tracking.
- **Activation** — `activation-planner.ts` resolves activation dependency order; `activation-context.ts` builds per-plugin activation state.
- **Runtime tracking** — `src/plugins/runtime.ts` tracks active plugins, HTTP routes, session extensions, gateway methods, and channel registrations; `active-runtime-registry.ts`, `plugin-registry.ts`, `plugin-registry-snapshot.ts` maintain the registry state.
- **Canonical Install Record** — `canonical-record.ts` stores install provenance (source, version, install date) for update detection and migration; `installed-plugin-index-*.ts` maintains the durable installed-plugin index.

## Install Provenance

Install flows in `src/plugins/install*.ts` support three provenances:

- **npm** — `install-npm.ts`, `install-npm-resolution.ts`, `install-npm-pack.ts`, `install-npm-metadata.ts`, `install-managed-npm.ts` with security scanning (`install-security-scan.ts`)
- **git** — `git-install.ts`
- **ClawHub** — `clawhub.ts`, `marketplace.ts`, `clawhub-install-records.ts`, `clawhub-error-codes.ts` (plugins require the explicit `clawhub:` prefix to force ClawHub resolution over npm/git/local paths)

Plus `install-paths.ts`, `install-provenance.ts`, `install-persistence.ts`, `install-overrides.ts`, `install-policy-context.ts`, and `install-installed-package.ts`. Updates/uninstall live in `update.ts`, `update-installed.ts`, `update-channel.ts`, `update-claw-lifecycle.ts`, and `uninstall.ts`.

## Registry and Slots

- **Registry** — `src/plugins/registry*.ts` (registry, registry-runtime, registry-registrars-*.ts split by capability kind: channels, providers, tools-hooks, memory, network, operations) plus `registry-api.ts`, `registry-state.ts`, `registry-refresh.ts`, `catalog-search.ts`.
- **Slots** — `slots.ts` and `slot-selection.ts` implement exclusive plugin slots (e.g. the memory backend / context engine), selected via `plugins.slots.*` config. Core stays plugin-agnostic; exclusive-slot decisions are the plugin's manifest/capability contract.

## Hooks System

Plugin hooks (`src/plugins/hooks.ts`, `docs/plugins/hooks.md`) are in-process extension points registered with `api.on(name, handler, opts?)`. Handlers run sequentially in descending `priority`; observation-only handlers run in parallel. Key hook kinds:

- **Phase hooks** — `before_tool_call`, `after_tool_call`, `before_agent_reply`, `before_agent_start`, `before_agent_finalize`, `before_dispatch`, `before_install`, `before_prompt_build`, compaction, message routing, decision, correlation
- **Options** — `matcher` (canonical tool ids for before/after_tool_call), `timeoutMs` per-hook budget, `eligibleTriggers` (`cron`/`heartbeat`/`user`) for `before_agent_reply`
- Operator config: `plugins.entries.<id>.hooks.timeoutMs` / `hooks.timeouts.<hookName>` override plugin-authored budgets
- Internal `HOOK.md` scripts are a separate, operator-installed surface (`docs/automation/hooks.md`)

Wiring files: `hook-agent-context.ts`, `hook-channel-context.types.ts`, `hook-before-tool-call-result.ts`, `hook-decision-types.ts`, `hook-skill.types.ts`, `hook-registry.types.ts`, `hooks.before-*.test.ts`.

## Providers

Provider plugins are a first-class kind with a dedicated runtime surface in `src/plugins/providers*.ts`:

- **Runtime** — `provider-runtime.ts` (+ `.types.ts`, `provider-runtime.runtime.ts`), `provider-discovery.ts`, `provider-validation.ts`, `provider-catalog.ts`, `provider-model-*.ts` (routes, primary, compat, helpers), `provider-thinking.ts`
- **Auth** — `provider-api-key-auth.ts`, `provider-oauth-flow.ts`, `provider-auth-choice.ts`, `provider-auth-token.ts`, `provider-auth-mode.ts`, `provider-auth-types.ts`, `provider-openai-chatgpt-oauth.ts`, `provider-openai-chatgpt-auth.ts`, `provider-external-auth.types.ts`
- **Wizard/setup** — `provider-wizard.ts`, `provider-setup.ts`, `provider-self-hosted-setup.ts`, `provider-onboard.ts`
- **Contract registries** — `doctor-contract-registry.ts`, `setup-registry.ts` (+ `setup-registry.runtime.ts`), `provider-install-catalog.ts`, `provider-public-artifacts.ts`

## Bundled vs External Lifecycle

- `extensions/` holds the bundled plugin catalog: 161 top-level package directories, 151 with `openclaw.plugin.json` manifests (core-dist bundled plugins, external official plugins, and test-support scaffolding). Provider extensions include `anthropic`, `openai`, `google`, `xai`, `openrouter`, `ollama`, `lmstudio`, `vllm`, `llama-cpp`, `sglang`, `litellm`, `microsoft`, `amazon-bedrock`, and many more.
- Official external plugins own their package/deps and are excluded from core dist; internal bundled plugins ship in core dist with a facade loader.
- **Migration extensions** — `extensions/migrate-claude/` (Claude Code → OpenClaw: `plan.ts`, `apply.ts`, `skills.ts`, `memory.ts`, `provider.ts`) and `extensions/migrate-hermes/` (Hermes → OpenClaw: config, auth, secrets, skills, memory mapping) provide cross-platform onboarding.
- Plugin management CLI: `openclaw plugins install/search/update/uninstall`; docs in `docs/plugins/manage-plugins.md`, `docs/plugins/building-plugins.md`, `docs/plugins/manifest.md`, `docs/plugins/hooks.md`, `docs/plugins/sdk-*.md`.

## Key Source Files

| File | Purpose |
|------|---------|
| `src/plugin-sdk/plugin-entry.ts` | Plugin entry point contract |
| `src/plugin-sdk/tool-plugin.ts` | Tool plugin pattern with TypeBox schemas |
| `scripts/lib/plugin-sdk-entrypoints.json` | 321 declared SDK subpaths |
| `src/plugins/loader.ts` | Plugin discovery and loading |
| `src/plugins/manifest.ts`, `manifest-types.ts` | Manifest validation |
| `src/plugins/activation-planner.ts` | Activation dependency planning |
| `src/plugins/install-npm.ts`, `git-install.ts`, `clawhub.ts` | Install provenance (npm/git/ClawHub) |
| `src/plugins/registry.ts`, `slots.ts` | Plugin registry and exclusive slots |
| `src/plugins/hooks.ts` | Plugin lifecycle hook system |
| `src/plugins/providers.ts`, `provider-runtime.ts` | Provider plugin runtime |
| `src/plugins/canonical-record.ts` | Canonical Install Record system |
| `extensions/` | 151 manifest-bearing bundled plugin packages |

## Related

- [[domains/architecture/openclaw-architecture.md]] — Overall system architecture
- [[domains/channels/openclaw-channels.md]] — Channel plugins (a plugin kind)
- [[domains/skills/openclaw-skills.md]] — Skill plugins and loading
- [[domains/memory/openclaw-memory.md]] — memory-core plugin deep dive
- [[wiki/openclaw.md]] — Wiki entry
