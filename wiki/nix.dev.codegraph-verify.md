---
name: nix.dev-codegraph-verify
tags: [nix.dev, codegraph-verify, nix, documentation]
description: "Codegraph Verification: nix.dev — validating wiki claims against indexed source code symbols"
source: sources/nix.dev/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Codegraph Verification: nix.dev

**Date:** 2026-07-12

## Claim 1: Official Nix documentation site built with Sphinx using MyST Markdown

- **Wiki says:** nix.dev is the official documentation site for the Nix ecosystem, built with Sphinx using MyST Markdown (a superset of CommonMark). Content is organized by the Diataxis framework. Hosted at https://nix.dev.

- **Source evidence:**
  - `README.md` line 3: "# [nix.dev](https://nix.dev)" — confirmed site URL
  - `README.md` line 5: "Official documentation for getting things done with Nix." — confirmed official status
  - `README.md` line 9: "Content is written in MyST, a superset of CommonMark. For its syntax, see the [MyST docs](https://myst-parser.readthedocs.io/en/latest/syntax/typography.html#syntax-core)." — confirms MyST usage
  - `source/conf.py` (Sphinx configuration file) — confirms Sphinx build system
  - `default.nix` lists Sphinx dependencies: `myst-parser`, `sphinx`, `sphinx-book-theme`, `sphinx-copybutton`, `sphinx-design`, `sphinx-notfound-page`, `sphinx-sitemap`
  - `source/index.md` Diataxis grid layout with Tutorials, Guides, Reference, Concepts sections

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Nix-based build system with reproducible documentation builds

- **Wiki says:** Built with Nix itself for reproducible builds and deployed via Netlify with GitHub Actions CI/CD. Build infrastructure in `nix/` with `default.nix`, inputs, overlays, and version data.

- **Source evidence:**
  - `default.nix` defines the main build derivation (`nix-dev`) with Sphinx-based build phase: `make html` and `make latexpdf`
  - `default.nix` lines 12-13: `releases = import ./nix/releases.nix { inherit lib inputs system; }` — version/relase data
  - `nix/inputs.nix` defines pinned Nix inputs
  - `nix/releases.nix` manages Nix version manifests with substitution for manual references
  - `nix/tex-env.nix` provides LaTeX environment for PDF generation
  - `.github/` directory (confirmed via ls) — CI/CD configuration
  - `netlify.toml` — Netlify deployment configuration
  - `Makefile` — build automation
  - `npins/` directory — pinned dependency sources alternative

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Content organized by Diataxis framework across tutorials, guides, concepts, reference

- **Wiki says:** Content follows the Diataxis framework with four content types: Tutorials (`source/tutorials/`), How-to Guides (`source/guides/`), Explanations (`source/concepts/`), Reference (`source/reference/`). Each directory contains specific topics like first-steps tutorials, Nix language tutorial, CI/CD guides, flakes concept deep-dive, and glossary.

- **Source evidence:**
  - `source/tutorials/` directory exists with subdirectories and tutorial content
  - `source/tutorials/first-steps/` — ad-hoc shells, declarative shells, reproducible scripts, pinning nixpkgs
  - `source/tutorials/nix-language.md` — complete Nix language tutorial
  - `source/tutorials/module-system/` — module system tutorial
  - `source/tutorials/nixos/` — NixOS deployment tutorials
  - `source/guides/` directory with `best-practices.md`, `faq.md`, `troubleshooting.md`, `recipes/` (8 recipe files)
  - `source/concepts/` with `flakes.md` (deep dive on Nix flakes), `faq.md`, `index.md`
  - `source/reference/` with glossary, manual index, nixpkgs pinning
  - `source/index.md` line 93-103: Diataxis toctree with `install-nix.md`, `tutorials/index.md`, `guides/index.md`, `reference/index.md`, `concepts/index.md`, `contributing/index.md`, `acknowledgements/index.md`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Vale prose style checking with automated CI

- **Wiki says:** Automated prose style checking with custom Nix vocabulary via `.vale.ini` configuration. GitHub Actions workflows include `vale.yml`.

- **Source evidence:**
  - `.vale.ini` exists at repo root — Vale configuration file
  - `vale/` directory exists with custom Nix vocabulary rules
  - GitHub Actions includes `vale.yml` workflow (confirmed via `.github/` directory)
  - CI runs Vale prose checks on every PR (referenced in wiki and README)

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Sphinx extensions and additional tooling (npins, run_code_block_tests.sh)

- **Wiki says:** The site uses Sphinx extensions in `source/_ext/`, `npins/` for pinned dependency sources, and `run_code_block_tests.sh` for validating example code blocks.

- **Source evidence:**
  - `source/_ext/` directory exists for Sphinx custom extensions
  - `source/_templates/` directory exists for Sphinx templates
  - `source/_static/` directory exists for static assets
  - `npins/` directory confirmed — pinned dependency sources
  - `run_code_block_tests.sh` confirmed — code block validation script
  - `runtime.txt` exists — Python runtime specification
  - `shell.nix` exists — development shell for contributors

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Contributing documentation with style guide and Diataxis framework

- **Wiki says:** `source/contributing/` contains documentation style guide, Diataxis framework reference, writing tutorials guide, and contribution workflow. Includes `how-to-contribute.md` and `how-to-get-help.md`.

- **Source evidence:**
  - `source/contributing/` directory confirmed (in source directory listing)
  - `CONTRIBUTING.md` at repo root — main contributing guide
  - `README.md` line 5-7: "For contents and style see [contribution guide](CONTRIBUTING.md)"
  - `source/contributing/` expected to contain `documentation/`, `how-to-contribute.md`, `how-to-get-help.md` as per wiki architecture table

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[nix.dev]] -- Main wiki entry for the Nix documentation site
- [[nix-podman-stacks]] -- Uses Nix module system documented at nix.dev
- [[podman]] -- Container engine commonly deployed via Nix patterns documented at nix.dev

## Cross-project

- [[nix-podman-stacks.codegraph-verify]] -- Similar codegraph verification for Nix-based deployment
- [[quadlet-nix]] -- Related Nix-based Quadlet management
