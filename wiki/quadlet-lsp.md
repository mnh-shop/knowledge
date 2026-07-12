---
name: quadlet-lsp
tags: [quadlet-lsp, quadlet, lsp, developer-tools, editor-support, container]
description: "Language server protocol implementation for Podman Quadlet files"
source: sources/quadlet-lsp/
---

# Quadlet LSP

| Field | Value |
|---|---|
| **Origin** | [towo/quadlet-lsp](https://github.com/towo/quadlet-lsp) |
| **Source** | `sources/quadlet-lsp/` |
| **Repomix** | `raw/quadlet-lsp/quadlet-lsp.xml` |
| **Codegraph** | `graphs/quadlet-lsp/` |

## Overview

Quadlet LSP is a Language Server Protocol (LSP) implementation for Podman Quadlet files. It provides IDE-grade editing support — syntax highlighting, autocompletion, validation, hover documentation, and diagnostics — for `.container`, `.volume`, `.network`, `.pod`, `.image`, and `.kube` Quadlet unit files in any LSP-compatible editor.

## Key Features

- **Syntax Validation** — Real-time validation of Quadlet directives and values against the spec
- **Autocompletion** — Context-aware suggestions for directive names and valid values
- **Hover Documentation** — Inline documentation for Quadlet directives
- **Diagnostics** — Error and warning reporting for invalid configurations
- **Multi-File Support** — Understands references between Quadlet files (e.g., network and container)
- **Editor Agnostic** — Works with VS Code, Neovim, Emacs, Helix, and any LSP-compatible editor

## Architecture

The LSP server parses Quadlet files according to the Podman Quadlet specification, building a symbol table of directives and their values. It provides standard LSP capabilities (textDocument/completion, textDocument/hover, textDocument/diagnostic) by walking the parsed AST and resolving references between related unit files.

## Related

- [[podlet]] — Quadlet file generator CLI
- [[podman-quadlet]] — Official Quadlet documentation
- [[podman]] — Container runtime
- [[quadit]] — CLI toolkit for managing Quadlet units
