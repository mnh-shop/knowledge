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

Quadlet-lsp implements the Language Server Protocol (LSP 3.16) for `.container`, `.volume`, `.network`, `.pod`, `.image`, `.kube`, `.build`, and `.artifact` files used by Podman Quadlet. It uses the `glsp` framework (`github.com/tliron/glsp`) and communicates over stdio. The server delivers code completion, hover info, go-to-definition, find references, syntax diagnostics, semantic tokens, formatting, and the `pullAll`/`listJobs` workspace commands.

**Source evidence:** `main.go:33-34` starts the LSP via `lsp.Start()`. `internal/lsp/lsp.go:42-120` registers all LSP handlers: `TextDocumentCompletion`, `TextDocumentHover`, `TextDocumentDefinition`, `TextDocumentReferences`, `TextDocumentDidOpen`, `TextDocumentDidChange`, `TextDocumentDidSave`, `TextDocumentFormatting`, `TextDocumentSemanticTokensFull`. Capabilities are announced in `initialize()` at `lsp.go:179-197` including `CompletionProvider`, `HoverProvider`, `ExecuteCommandProvider` (registering `pullAll` and `listJobs` at `:181`), `DocumentFormattingProvider`, `SemanticTokensProvider`.

## Claim-2: Real-time completion against live Podman resources

The completion engine queries the actual Podman daemon for pulled images, defined secrets, created volumes, networks, pods, and exposed ports, providing dynamic completions based on the current system state — not just static keyword suggestions. Trigger characters include `=`, `[`, `]`, `.`, `:`, `,`, `%`.

**Source evidence:** `internal/completion/` contains `property_image.go`, `property_network.go`, `property_pod.go`, `property_secret.go`, `property_volume.go`, `property_port.go`, `property_userns.go` — each implementing dynamic completion against live Podman resources. `lsp.go:191-194` declares the completion trigger characters. `internal/completion/completion.go` delegates to the per-property engines with the parsed config.

## Claim-3: Comprehensive syntax checking with 26 QSR rules

The syntax checker enforces 26 Quadlet Syntax Rules (qsr001–qsr026), each in its own file with corresponding unit tests. Rules validate property names, value formats, section structure, and cross-file references. Rules can be disabled per-file via `# disable-qsr:` comments and per-directory via the `disable` list in `.quadletrc.json`. Diagnostics are published on document open, change, and save via `PublishDiagnostics` notifications.

**Source evidence:** `internal/syntax/syntax.go:39-64` registers the 26 checks `qsr001`→`qsr026`. `syntax.go:84` parses `# disable-qsr:` / `; disable-qsr:` header comments, and `pkg/parser/parse_quadlet.go:54` handles rule suspension in the parser. `lsp.go` DidOpen/DidChange/DidSave handlers instantiate `syntax.NewSyntaxChecker` and call `checker.RunAll(config)`, publishing diagnostics. Each rule has a `qsr0NN_test.go` file.

## Claim-4: Go-to-definition, references, and hover across quadlet files

The LSP supports cross-file navigation: go-to-definition resolves references to networks, pods, volumes, and images defined in other quadlet files. Find references locates all usages of a resource across the project. Hover provides inline documentation from Podman Quadlet's specification plus value previews for `Network=`, `Pod=`, and `Volume=` references.

**Source evidence:** `internal/lsp/go_definition.go` implements `textDefinition` which calls `findQuadlets()` → `ListQuadletFiles()` to locate resource definitions across files. `internal/lsp/go_references.go` implements `textReferences`. `internal/lsp/hover.go` implements `textHover` and uses the `internal/hover/value_*` preview helpers. `lsp.go:42-45` registers all three handlers.

## Claim-5: CLI exposes only help/version/check; pullAll/listJobs are LSP workspace commands

The binary operates in two modes: when invoked with arguments, it runs the CLI command router, which supports exactly `help`, `version`, and `check` — anything else is an error. When invoked without arguments, it starts the LSP server. The `pullAll` and `listJobs` commands are NOT CLI commands; they are workspace commands registered in the LSP `ExecuteCommandProvider`. A CLI error terminates with exit code 8.

**Source evidence:** `main.go:14-31` routes `len(args) >= 2` to `cli.CliCommand{Command: cmd, Parms: parms}` and calls `os.Exit(8)` on error (`main.go:26-28`). `internal/cli/cli.go:24-33` is the command switch: only `help`, `version`, `check` (default case returns `"invalid command, see 'quadlet-lsp help'"`). `internal/commands/commands.go:28-44` registers exactly `pullAll` and `listJobs` in the `EditorCommandExecutor` map. `lsp.go:180-182` advertises `Commands: []string{"pullAll", "listJobs"}` in `ExecuteCommandProvider`. No `QuadletPullAll`, `QuadletListJobs`, or `QuadletGenerate*` commands exist anywhere.

## Claim-6: Configuration-driven with `.quadletrc.json` and Podman version detection

The server reads a `.quadletrc.json` configuration from the workspace root for project-specific settings (disabled rules, `podmanVersion`, `project.rootDir`/`project.dirLevel`), and auto-detects the installed Podman version to adapt validation. A minimum Podman version of 5.4.0 is required for full support, falling back to 5.4.0 when detection fails. A file watcher monitors for config changes at runtime.

**Source evidence:** `internal/utils/config.go:12-24` defines the `QuadletConfig` schema (`disable`, `podmanVersion`, `project`) and `config.go:26-54` loads it from the workspace root, parsing the version with `ParseVersion` and falling back to `BuildPodmanVersion(5, 4, 0)` at `:50`. `lsp.go:150-167` calls `utils.LoadConfig`, checks `config.Podman.IsSupported()`, and warns if `< 5.4.0`. `lsp.go:171-176` starts the file watcher on `.quadletrc.json` (`internal/utils/watcher.go`).

## Claim-7: Formatting (80-char) and semantic tokens

Document formatting wraps lines at 80 characters with `\` continuations, and semantic tokens classify image owners, environment variable names, and other fields beyond generic keyword highlighting.

**Source evidence:** `internal/format/format.go:164-169` enforces the 80-character limit, wrapping long lines via `wrapLine`. `internal/semantic/` contains per-file-type token readers (`read_env_tokens.go`, `read_image_tokens.go`, `read_label_tokens.go`, `read_network_tokens.go`, `read_pod_tokens.go`, `read_secret_tokens.go`, `read_volume_tokens.go`) plus the legend/`TokenLegends` definitions used by the `SemanticTokensProvider` in `lsp.go:186-193`.

## Claim-8: Test coverage — 11 completion test files, 26 syntax test files; multi-platform packaging

The completion package contains exactly 11 `*_test.go` files, and each of the 26 syntax rules has its own test file. The project ships via Go install, Nix flake, Fedora COPR, Debian repository, GitHub releases (goreleaser), and Mise. The main branch is unstable; version-tagged releases provide stable code.

**Source evidence:** `internal/completion/` contains 11 test files: `new_property_test.go`, `property_image_test.go`, `property_network_test.go`, `property_pod_test.go`, `property_port_test.go`, `property_secret_test.go`, `property_test.go`, `property_userns_test.go`, `property_volume_test.go`, `sections_test.go`, `systemd_specifier_test.go`. `internal/syntax/` has 26 `qsr0NN_test.go` files. Packaging: `flake.nix` (pinned `v0.7.4`), `quadlet-lsp.spec` (COPR), `mise.toml`, `docs/install_and_plugins.md`, `.goreleaser.yaml`. `docs/development.md` documents the unstable-main-branch caveat.
