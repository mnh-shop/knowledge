---
name: quadlet-lsp-guide
type: developer-tools
tags: [developer-tools, editor-support, lsp, quadlet, quadlet-lsp, podman, container, language-server]
description: "Developer guide: Quadlet LSP — QSR catalog, CLI, editor setup, and configuration"
source: sources/quadlet-lsp/
---

# Quadlet LSP — Developer Guide

**Source:** `sources/quadlet-lsp/`
**Layer:** Editor tooling / language server
**Paradigm:** LSP 3.16 over stdio (glsp framework), Go single-binary

## Overview

Quadlet LSP brings IDE-grade editing to [Podman Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) unit files (`.container`, `.volume`, `.network`, `.pod`, `.image`, `.kube`, `.build`, `.artifact`). The binary is dual-mode: with no arguments it starts the LSP server over stdio; with an argument it runs one of three CLI subcommands (`help`, `version`, `check`). All editor-facing automation goes through LSP workspace commands (`pullAll`, `listJobs`) — never through the CLI.

---

## 1. QSR Catalog (26 rules)

The syntax checker implements 26 Quadlet Syntax Rules, registered in `internal/syntax/syntax.go:39-64` as `qsr001`→`qsr026`, each with its own source + test file. Full documentation ships in `docs/QSR0NN.md`.

| Rule | Diagnostic |
|---|---|
| qsr001 | Missing section header |
| qsr002 | Unfinished line |
| qsr003 | Invalid property |
| qsr004 | Image name is not fully qualified |
| qsr005 | Invalid value of AutoUpdate |
| qsr006 | Image file does not exist |
| qsr007 | Invalid format of Environment variable |
| qsr008 | Invalid format of Annotation |
| qsr009 | Invalid format of Label |
| qsr010 | Incorrect format of PublishPort |
| qsr011 | Port is not exposed in image |
| qsr012 | Invalid format of secret specification |
| qsr013 | Volume file does not exist |
| qsr014 | Network file does not exist |
| qsr015 | Invalid format of Volume specification |
| qsr016 | Invalid value of UserNS specification |
| qsr017 | Pod file does not exist |
| qsr018 | Container cannot publish port with pod |
| qsr019 | Container cannot have network with pod |
| qsr020 | Naming of unit is invalid |
| qsr021 | Unit points to not a systemd unit |
| qsr022 | `/` is before systemd directory specifier |
| qsr023 | Invalid systemd specifier is used |
| qsr024 | Not recommended property usage in Service section |
| qsr025 | Image is missing in container |
| qsr026 | Artifact is missing in artifact |

Rules span four families: **property validity** (qsr003, qsr007-009, qsr012, qsr015, qsr016, qsr020, qsr023-024), **required values** (qsr025, qsr026, qsr004), **cross-file reference resolution** (qsr006, qsr013, qsr014, qsr017, qsr021), and **structure** (qsr001, qsr002, qsr022). Cross-file rules resolve referenced `.image`/`.volume`/`.network`/`.pod` files through the parser's symbol table and validate them on the fly.

**Rule suspension** has two levels:
- Per-file: a `# disable-qsr:` (or `; disable-qsr:`) header comment lists rule names (`syntax.go:84`, `pkg/parser/parse_quadlet.go:54`)
- Per-directory: the `disable` array in `.quadletrc.json`

---

## 2. CLI

`main.go:14-31` routes any invocation with `>= 2` arguments to `internal/cli/cli.go`, whose switch (`cli.go:24-33`) accepts exactly:

| Command | Behavior |
|---|---|
| `quadlet-lsp help` | Prints usage (`cli.go:45-52`) |
| `quadlet-lsp version` | Prints `data.ProgramVersion` |
| `quadlet-lsp check <dir>` | Runs all enabled QSR rules over a directory |
| anything else | Error: `invalid command, see 'quadlet-lsp help'` |

**Exit code:** any CLI error (invalid command, unreadable config, missing/non-directory argument) terminates with `os.Exit(8)` (`main.go:26-28`).

### `check` in CI

`runCheckCLI` (`internal/cli/cmd_check.go`) walks the target directory via `parser.ParseQuadletDir`, then for every Quadlet file (and every drop-in under `foo.unit.d/` directories — `cmd_check.go:64-71`) instantiates `syntax.NewSyntaxChecker` and runs `RunAll(checkCfg)`. It respects the `disable` list from `.quadletrc.json` loaded from the current working directory, prints a `File, QSR number, Range, Message` table, and honors `project.dirLevel` for directory scanning depth. Diagnostics with `Information` severity are listed but do not fail the run.

---

## 3. Editor Setups

`docs/install_and_plugins.md` documents the supported editors:

- **VS Code** — [quadlet-lsp](https://marketplace.visualstudio.com/items?itemName=onlyati.quadlet-lsp) marketplace extension (ships the server).
- **Neovim** — [quadlet-lsp.nvim](https://github.com/onlyati/quadlet-lsp.nvim) plugin wrapping `vim.lsp.start`.
- **Zed** — [Quadlet extension](https://zed.dev/extensions/quadlet) (third-party).

Workspace commands (`pullAll`, `listJobs`) are advertised in the LSP `ExecuteCommandProvider` (`lsp.go:180-182`) and surface as editor palette actions. The server announces capabilities for completion, hover, definition, references, formatting, semantic tokens, and open/change/save diagnostics (`lsp.go:179-197`), so any LSP client (Helix, Emacs/eglot, etc.) works with a generic `quadlet-lsp` executable.

---

## 4. `.quadletrc.json` Schema

Loaded from the workspace root (`internal/utils/config.go:26-30`). `project.rootDir` re-bases the workspace root (`config.go:41-44`).

```jsonc
{
  // QSR rules to disable project-wide (e.g. ["qsr013", "qsr004"])
  "disable": ["qsr013"],
  // Podman version to validate against; "5.4.0" is the minimum supported.
  // When omitted or unparseable, the server runs `podman version` and
  // falls back to 5.4.0 (config.go:46-53).
  "podmanVersion": "5.4.0",
  "project": {
    // Directory depth to scan for Quadlet files (check + references)
    "dirLevel": 2,
    // Sub-directory that holds the Quadlet files
    "rootDir": "quadlets"
  }
}
```

The file is watched for changes and hot-reloaded mid-session (`lsp.go:171-176`, `internal/utils/watcher.go`).

---

## 5. Drop-in Handling

Drop-in files (`foo.container.d/10-ports.conf`) are parsed as part of the parent unit: the parser attaches them to `q.Dropins`, and both the LSP diagnostics path and `quadlet-lsp check` validate them with the same syntax checker (`cmd_check.go:64-71`). This mirrors systemd/Podman override semantics without modifying the original file.

---

## 6. LSP Workspace Commands

Registered in `internal/commands/commands.go:28-44` (map keys are the command names) and advertised at `lsp.go:181`:

- **`pullAll`** — pulls all images defined by `Image=` in the workspace directory (`commands/pull_all.go`), running asynchronously with progress messages.
- **`listJobs`** — lists running background tasks (`commands/list_jobs.go`).

The `EditorCommandExecutor` guards against concurrent/duplicate runs (`commands.go:59-82`) and reports failures to the client via a `MessengerError` window message (`commands.go:46-57`). There are no other commands — no documentation generation, no `Quadlet*`-prefixed names.

---

## Related

- [[quadlet-lsp]] — wiki summary
- [[quadlet-lsp.codegraph-verify]] — evidence-backed verification
- [[quadlet-nix]] — Nix-based Quadlet generation (alternative approach)
- [[quadlet-nix-architecture]] — Nix-side architecture
- [[podlet]] — Quadlet file generator CLI
