---
name: nix.dev
tags: [developer-tools, documentation, git, python, nix, nix.dev]
description: "Official documentation for getting things done with Nix"
source: sources/nix.dev/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# nix.dev

**Source:** `sources/nix.dev/`

nix.dev is the official documentation site for the Nix package manager and NixOS. Hosted at https://nix.dev, it provides tutorials, guides, recipes, concepts, and reference material for learning and using Nix effectively. Maintained by the NixOS Foundation documentation team.

| Field | Value |
|---|---|
| **Origin** | [NixOS/nix.dev](https://github.com/NixOS/nix.dev) |
| **License** | CC-BY-SA-4.0 (documentation), MIT (tooling) |
| **Stack** | MyST Markdown, Sphinx, Nix |
| **Site** | https://nix.dev |
| **Source** | `sources/nix.dev/` |

## Overview

nix.dev is the home of official documentation for the Nix ecosystem — a documentation site built with Sphinx using MyST (Markedly Structured Text, a superset of CommonMark). Content is organized by the Diataxis framework (tutorials, how-to guides, explanations, reference) for structured learning. Built with Nix itself for reproducible builds and deployed via Netlify with automated GitHub Actions CI/CD. The site covers everything from installing Nix and first steps, through the Nix language and module system, to NixOS deployment, packaging, cross-compilation, and CI integration.

## Key Features

- **Tutorials:** Step-by-step learning paths covering first steps (ad-hoc shell environments with `nix shell`, declarative shell environments via `shell.nix` and `flake.nix`, reproducible scripts, pinning nixpkgs), the Nix language (full tutorial with syntax, functions, types, and idioms), the module system (options, imports, types, and NixOS module creation), NixOS (installation, building custom ISOs, Docker images, Raspberry Pi images, integration testing with virtual machines), packaging existing software, cross-compilation, and working with local files
- **Guides & Recipes:** Practical how-to guides covering continuous integration with GitHub Actions + Cachix binary caches, dependency management patterns, direnv integration for automatic shell activation, Python environment management, post-build hooks for deployment, sharing dependencies across projects, adding binary caches, best practices, FAQ, and troubleshooting
- **Concepts:** Deep dives into the Nix store model (immutable storage, content-addressing, garbage collection), Nix flakes (inputs/outputs system, `flake.nix` structure, `flake.lock` pinning, built-in output types, extensibility), and frequently asked conceptual questions about how Nix achieves reproducibility
- **Reference:** Glossary of Nix terminology, Nix manual index with links to official documentation, and nixpkgs pinning reference with version management guidance
- **Contributing Documentation:** Style guide, Diataxis framework documentation, writing tutorials guide, and contribution workflow; content in `source/contributing/` with `documentation/`, `how-to-contribute.md`, and `how-to-get-help.md`
- **Vale Integration:** Automated prose style checking with custom Nix vocabulary via `.vale.ini` configuration
- **Tooling:** Nix build infrastructure (`nix/` directory with `default.nix`, inputs, overlays, version data), `npins/` for pinned dependency sources, Sphinx extensions in `source/_ext/`, and `run_code_block_tests.sh` for validating example code blocks

## Architecture

The site is built with Sphinx using MyST Markdown (MyST is a superset of CommonMark that adds Sphinx-specific directives like `{ref}`, `{term}`, and `{need}`). Content is structured by the Diataxis framework:

| Directory | Diataxis Type | Purpose |
|---|---|---|
| `source/tutorials/` | Tutorials | First steps, Nix language, module system, NixOS, packaging, cross-compilation |
| `source/guides/` | How-to Guides | CI/CD, direnv, binary caches, Python environments, best practices, FAQ, troubleshooting |
| `source/concepts/` | Explanations | Flakes, Nix store model, FAQ |
| `source/reference/` | Reference | Glossary, manual index, nixpkgs pinning |

### Key Source Layout

- `source/tutorials/first-steps/` — 5 tutorials covering ad-hoc shells, declarative shells, reproducible scripts, and pinning nixpkgs
- `source/tutorials/nix-language.md` — Complete Nix language tutorial
- `source/tutorials/module-system/` — Module system tutorial
- `source/tutorials/nixos/` — NixOS deployment tutorials (ISOs, Docker, Raspberry Pi, integration testing)
- `source/guides/recipes/` — 8 recipe files: CC, binary cache, dependency management, direnv, post-build hook, Python environment, sharing dependencies
- `source/concepts/flakes.md` — 322-line deep dive on Nix flakes (inputs, outputs, flake.lock, references, CLI integration)
- `source/contributing/documentation/` — Style guide and Diataxis framework reference
- `nix/` — Build infrastructure with `default.nix`, overlays, and version data
- `maintainers/` — Project maintenance docs and Google Season of Docs 2024 information

## Usage

```bash
# Install Nix (from the site's guide)
# Then build the documentation site locally:
cd sources/nix.dev/
nix build   # or use make

# The site is published at https://nix.dev via Netlify
# GitHub Actions workflows: build-and-deploy.yml, test.yml, vale.yml, update-nix-releases.yml
```

Content contributions follow the MyST Markdown syntax and the Diataxis framework. The repo includes `CONTRIBUTING.md` with detailed guidance on content style, writing tutorials, and the documentation contribution workflow. Automated CI runs Vale prose checks and builds the site on every PR.

## Related

- [[nix-podman-stacks]] — Uses Nix module system for declarative container stacks and host configuration
- [[nix]] — The Nix package manager and NixOS ecosystem
- [[quadlet-nix]] — Nix-based Quadlet container management with NixOS integration
- [[podman]] — Container engine commonly deployed via Nix for reproducible development environments
- [[bootc]] — Bootable container system using Nix-compatible image building patterns
- [[fedora-coreos-config]] — Fedora CoreOS configuration that pairs with Nix-based deployment tooling
