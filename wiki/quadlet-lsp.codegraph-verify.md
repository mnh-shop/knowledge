---
title: "quadlet-lsp — CodeGraph Verification"
tags: [quadlet-lsp, codegraph-verify, quadlet, lsp]
related: [[quadlet-lsp]], [[podlet]], [[podman]], [[quadlet-nix]]
verification_date: 2026-07-12
verified_by: CodeGraph & manual source audit
source_ref: sources/quadlet-lsp/
graph_ref: graphs/quadlet-lsp/
---

# quadlet-lsp — CodeGraph Verification

## Claim-1: Language server for Podman Quadlet files with full LSP protocol support

Quadlet-lsp implements the Language Server Protocol (LSP 3.16) for `.container`, `.volume`, `.network`, `.pod`, `.kube`, and `.image` files used by Podman Quadlet. It uses the `glsp` framework (`github.com/tliron/glsp`) and communicates over stdio. The server delivers code completion, hover info, go-to-definition, find references, syntax diagnostics, semantic tokens, formatting, and custom commands.

**Source evidence:** `main.go:33-34` starts the LSP via `lsp.Start()`. `internal/lsp/lsp.go:34-129` registers all LSP handlers: `TextDocumentCompletion`, `TextDocumentHover`, `TextDocumentDefinition`, `TextDocumentReferences`, `TextDocumentDidOpen`, `TextDocumentDidChange`, `TextDocumentDidSave`, `TextDocumentFormatting`, `TextDocumentSemanticTokensFull`. Capabilities are announced in `initialize()` at line 179-197 including `CompletionProvider`, `HoverProvider`, `ExecuteCommandProvider`, `DocumentFormattingProvider`, `SemanticTokensProvider`.

## Claim-2: Real-time completion against live Podman resources

The completion engine queries the actual Podman daemon for running images, volumes, networks, pods, and secrets, providing dynamic completions based on the current system state — not just static keyword suggestions. Trigger characters include `=`, `[`, `]`, `.`, `:`, `,`, `%`.

**Source evidence:** `internal/completion/` contains `property_image.go`, `property_network.go`, `property_pod.go`, `property_secret.go`, `property_volume.go`, `property_port.go`, `property_userns.go` — each implementing dynamic completion against live Podman resources. `internal/lsp/completion.go` delegates to `completion.NewCompletion().RunCompletion(config)`. The completion capabilities at `lsp.go:195-197` declare trigger characters. `internal/data/package` likely holds static completion data from Quadlet documentation.

## Claim-3: Comprehensive syntax checking with 26 QSR rules

The syntax checker enforces 26 Quadlet Syntax Rules (QSR001-QSR026), each in its own file with corresponding unit tests. Rules validate property names, value formats, section structure, and cross-file references. Diagnostics are published on document open, change, and save via `PublishDiagnostics` notifications.

**Source evidence:** `internal/syntax/` contains `qsr001.go` through `qsr026.go` plus `common.go`, `syntax.go`, and 26 `*_test.go` files. `lsp.go:55-70` (DidOpen) and `lsp.go:87-102` (DidChange) instantiate `syntax.NewSyntaxChecker` and call `checker.RunAll(config)`, publishing diagnostics. `lsp.go:111` registers `SyntaxCheckOnSave` for DidSave.

## Claim-4: Go-to-definition, references, and hover across quadlet files

The LSP supports cross-file navigation: go-to-definition resolves references to networks, pods, volumes, and images defined in other quadlet files. Find references locates all usages of a resource across the project. Hover provides inline documentation from Podman Quadlet's specification.

**Source evidence:** `internal/lsp/go_definition.go` implements `textDefinition` which calls `findQuadlets()` → `ListQuadletFiles()` to locate resource definitions across files. `internal/lsp/go_references.go` implements `textReferences`. `internal/lsp/hover.go` implements `textHover`. `internal/lsp/utils.go` provides shared helpers. `lsp.go:42-45` registers all three handlers.

## Claim-5: Dual-mode architecture — LSP server and CLI commands

The binary operates in two modes: when invoked with arguments, it runs CLI commands (currently `pullAll` and `listJobs`). When invoked without arguments, it starts the LSP server. The CLI commands are executed against the Podman system, with errors surfaced via exit codes.

**Source evidence:** `main.go:12-31` checks `len(args) >= 2` and routes to `cli.CliCommand{Command: cmd, Parms: parms}`. `internal/cli/` contains the CLI command infrastructure. `internal/commands/` has `commands.go`, `pull_all.go`, `list_jobs.go`, and `pull_all_test.go`. `lsp.go:181-182` registers `pullAll` and `listJobs` as workspace commands in `ExecuteCommandProvider`.

## Claim-6: Configuration-driven with `.quadletrc.json` and Podman version detection

The server reads a `.quadletrc.json` configuration from the workspace root for project-specific settings, and auto-detects the installed Podman version to adapt completion and validation to available features. A minimum Podman version of 5.4.0 is required for full support. A file watcher monitors for config changes at runtime.

**Source evidence:** `internal/utils/config.go` handles `.quadletrc.json` loading. `internal/utils/podman_version.go` detects Podman version. `lsp.go:150-167` calls `utils.LoadConfig(workspaceDir, ...)`, checks `config.Podman.IsSupported()`, and warns if `< 5.4.0`. `lsp.go:171-176` starts a file watcher on `.quadletrc.json`. `internal/utils/podman_version_test.go` provides version parsing tests.

## Claim-7: Rich test coverage across completion, syntax, and core logic

The project has extensive test coverage: 12 completion property test files, 26 syntax rule test files, config tests, Podman version tests, quadlet scan tests, general utility tests, and a pull_all test. Tests cover edge cases like empty values, special characters, cross-file references, and Podman version parsing.

**Source evidence:** Files: `property_image_test.go`, `property_network_test.go`, `property_pod_test.go`, `property_secret_test.go`, `property_volume_test.go`, `property_port_test.go`, `property_userns_test.go`, `sections_test.go`, `systemd_specifier_test.go`, `property_test.go` (11 completion test files). `qsr001_test.go` through `qsr026_test.go` (26 syntax test files). `config_test.go`, `podman_version_test.go`, `quadlet_scan_test.go`, `general_test.go`, `pull_all_test.go`.
