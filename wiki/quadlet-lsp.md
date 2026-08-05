---
name: quadlet-lsp
tags: [quadlet-lsp, quadlet, lsp, developer-tools, editor-support, container]
description: "Language server protocol implementation for Podman Quadlet files"
source: sources/quadlet-lsp/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Quadlet LSP

| Field | Value |
|---|---|
| **Origin** | [onlyati/quadlet-lsp](https://github.com/onlyati/quadlet-lsp) |
| **Source** | `sources/quadlet-lsp/` |
| **Repomix** | `raw/quadlet-lsp/quadlet-lsp.xml` |
| **Codegraph** | `graphs/quadlet-lsp/` |

## Overview

Quadlet LSP is a Language Server Protocol (LSP) implementation for [Podman Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) files, written in Go. It provides IDE-grade editing support — syntax checking, autocompletion, hover documentation, go-to-definition, reference finding, file formatting, semantic highlighting, and diagnostics — for all Quadlet unit file types (`.container`, `.volume`, `.network`, `.pod`, `.image`, `.kube`, `.build`, `.artifact`) in any LSP-compatible editor (VS Code, Neovim, Emacs, Helix, Zed). The project follows a semantic versioning release cycle with prebuilt binaries for multiple platforms and is packaged via Go, Nix, Fedora COPR, Debian repositories, GitHub releases, and the Mise version manager. The main branch is considered unstable; version-tagged releases provide stable code.

## Key Features

- **Code Completion** — Static completion based on the Podman Quadlet documentation plus dynamic completion querying real configuration: pulled images and `*.image` files at `Image=`, defined secrets at `Secret=`, created volumes and `*.volume` files at `Volume=`, `*.pod` files at `Pod=`, networks and `*.network` files at `Network=`, systemd specifiers at `%`, UID/GID from images at `UserNS=keep-id:`, and exposed ports from images for `PublishPort`.
- **Syntax Checking** — 26 Quadlet Syntax Rules (QSR001–QSR026) covering invalid properties, missing required fields, deprecated directives, type validation, value range checks, and cross-file reference validation. Per-file and per-directory rule suspension via `# disable-qsr:` comments and `.quadletrc.json` configuration.
- **Hover Documentation** — Inline documentation for Quadlet directives (including `UserNS`, `Volume`, `Secret` value explanations), systemd specifier descriptions, and peek-into-Quadlet file previews for `Network=`, `Pod=`, and `Volume=` values.
- **Go Definition / References** — Jump to referenced Quadlet files (e.g., clicking `Pod=nc.pod` opens the `.pod` file). Find all files referencing a Quadlet resource from its `[Unit]` section.
- **Formatting** — Document formatting with 80-character line width, `\` continuation for long lines, comment filtering, property grouping by topic, and alphabetical ordering within groups.
- **Semantic Tokens** — Syntax highlighting via semantic tokens that distinguish image owners, environment variable names, and other important fields beyond generic keyword highlighting.
- **LSP Workspace Commands** — Editor-triggerable commands registered in the LSP `ExecuteCommandProvider`: `pullAll` (pull all images defined in the directory) and `listJobs` (list running background tasks). These are workspace commands, not CLI commands — no other built-in commands exist.
- **CLI Syntax Checker** — The binary can be used standalone as a CLI syntax checker (`quadlet-lsp check .`) for CI/CD pipelines, returning exit code 8 when the CLI reports an error (invalid command, unreadable config, missing directory).
- **Drop-in Directory Support** — Understands Quadlet drop-in files (`foo.container.d/10-ports.conf`) for overriding settings without modifying the original file.
- **Configurable** — `.quadletrc.json` configuration for disabling specific QSR rules, specifying `podmanVersion` for cross-version validation, and `project.rootDir`/`project.dirLevel` for multi-project workspaces.
- **File Watcher** — Watches `.quadletrc.json` for changes and hot-reloads the configuration during the session.

## Architecture

The language server is structured as a Go application with a layered architecture:

- **Entry Point** (`main.go`) — Routes between CLI mode (only `help`, `version`, `check`) and LSP server mode based on argument count
- **LSP Core** (`internal/lsp/`) — Implements the GLSP protocol handler with registered capabilities for completion, hover, definition, references, formatting, semantic tokens, diagnostics (on open/change/save), and workspace commands. Uses the `tliron/glsp` library for protocol 3.16.
- **Syntax Checker** (`internal/syntax/`) — 26 independent rule modules (qsr001–qsr026), each with its own test file. Rules check for invalid properties, deprecated options, missing `Image=` fields, port range validity, volume path integrity, secret name formats, and cross-file reference consistency.
- **Parser** (`pkg/parser/`) — Quadlet file parsing logic that builds an AST and symbol table
- **Completion Engine** (`internal/completion/`) — Context-aware suggestions based on cursor position, file type, and runtime state (pulled images, defined secrets, etc.)
- **Semantic Module** (`internal/semantic/`) — Token classification for semantic highlighting (types, modifiers, legends)
- **Data Layer** (`internal/data/`) — Version information and program constants
- **Format Module** (`internal/format/`) — Document formatting with line width constraints and property organization
- **Hover Module** (`internal/hover/`) — Directive documentation, value explanations, and cross-file peek previews
- **Command Executor** (`internal/commands/`) — Background task management for the `pullAll` and `listJobs` LSP workspace commands
- **Utilities** (`internal/utils/`) — File watching, document tracking, configuration loading, and OS command execution
- **CLI** (`internal/cli/`) — Command-line argument processing for non-LSP modes

The LSP server communicates over stdio (standard JSON-RPC transport) and maintains an in-memory document store for tracking file changes. Configuration is loaded from `.quadletrc.json` in the workspace root, with Podman version auto-detection via `podman version` fallback.

## Usage

### Installation Methods

```bash
# Go install
go install github.com/onlyati/quadlet-lsp@latest

# Nix flake
nix profile install github:onlyati/quadlet-lsp

# Fedora / RHEL
sudo dnf copr enable onlyati/quadlet-lsp
sudo dnf install quadlet-lsp

# Debian / Ubuntu (trixie)
curl -o /etc/apt/keyrings/gitea-pandora.asc \
  https://git.thinkaboutit.tech/api/packages/pandora/debian/repository.key
# Add apt source from repo, then:
sudo apt install quadlet-lsp

# Mise
mise use -g github:onlyati/quadlet-lsp
```

### Editor Integration

- **VS Code** — Install [quadlet-lsp](https://marketplace.visualstudio.com/items?itemName=onlyati.quadlet-lsp) from the marketplace
- **Neovim** — Use the [quadlet-lsp.nvim](https://github.com/onlyati/quadlet-lsp.nvim) plugin
- **Zed** — Install the [Quadlet extension](https://zed.dev/extensions/quadlet) (third-party)

### CLI Syntax Check

```bash
# Check all Quadlet files in a directory
quadlet-lsp check .

# With custom configuration, create .quadletrc.json:
# { "disable": ["qsr013", "qsr004"], "podmanVersion": "5.4.0" }
```

### Per-File Rule Suspension

```ini
# disable-qsr: qsr004 qsr021

[Container]
Image=library/postgres:17
```

## Related

- [[podlet]] — Quadlet file generator CLI
- [[podman-quadlet]] — Official Quadlet documentation reference
- [[podman]] — Container runtime for Quadlet units
- [[quadit]] — CLI GitOps toolkit for managing Quadlet units
- [[quadlet-nix]] — Nix-based Quadlet generation (alternative approach)
- [[podman]] — Podman container engine that runs Quadlet units
