---
name: nix.dev-architecture
tags: [nix.dev, architecture, nix, documentation]
description: "Official Nix documentation site — MyST+Sphinx build pipeline, Diataxis content framework, Nix-based reproducible builds, Netlify deployment"
source: sources/nix.dev/
verification_date: 2026-07-12
verified_by: source conf.py + wiki
---

# nix.dev — Architecture

**Source:** `sources/nix.dev/`

## Overview

nix.dev is the official documentation site for the Nix package manager and NixOS ecosystem, hosted at https://nix.dev and maintained by the NixOS Foundation documentation team. It is built with **Sphinx** using **MyST Markdown** (a superset of CommonMark that adds Sphinx directives), organized by the **Diataxis** content framework, and built with **Nix** itself for reproducible builds. Deployed via **Netlify** with GitHub Actions CI/CD. Content is CC-BY-SA-4.0 licensed; tooling is MIT.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Source Layer (source/)                     │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │tutorials/ │ │ guides/  │ │concepts/ │ │   reference/     │   │
│  │ (Diataxis │ │(How-to)  │ │(Explain) │ │  (Reference)    │   │
│  │ Tutorial) │ │          │ │          │ │                  │   │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────────────┤   │
│  │first-steps│ │ recipes/ │ │flakes.md │ │glossary.md      │   │
│  │nix-lang  │ │ ci-cd/   │ │store.md  │ │manual-index.md  │   │
│  │module-sys│ │ direnv/  │ │faq.md    │ │nixpkgs-pinning  │   │
│  │nixos/    │ │ python/  │ │          │ │                  │   │
│  │packaging │ │ best-    │ │          │ │                  │   │
│  │cross-comp│ │ practices│ │          │ │                  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
│  ┌──────────┐ ┌──────────┐                                       │
│  │contribut-│ │install-  │                                       │
│  │ing/      │ │nix.md    │                                       │
│  └──────────┘ └──────────┘                                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│                      Build Layer                                 │
│                                                                   │
│  conf.py (Sphinx config, 462 lines)                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Extensions:                                               │   │
│  │ myst_parser, intersphinx, sphinx_copybutton,             │   │
│  │ sphinx_design, sphinx_sitemap, notfound, extractable_code│   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ MyST Extensions: colon_fence, linkify, tasklist,         │   │
│  │ attrs_block                                               │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ Custom Extensions (source/_ext/):                        │   │
│  │ extractable_code_block — validates example code blocks   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  nix/build infrastructure:                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ nix/default.nix — Nix build derivation                   │   │
│  │ nix/overlay.nix — Custom Nixpkgs overlay                 │   │
│  │ nix/inputs.nix — Flake inputs for pinned deps            │   │
│  │ npins/ — Pinned source dependencies                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Makefile — Alternative non-Nix build path with virtualenv      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│                      CI/CD Layer                                 │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ build-and-   │  │    test.yml  │  │    vale.yml        │    │
│  │ deploy.yml   │  │  (link       │  │  (prose style      │    │
│  │ (Netlify     │  │   checking,  │  │   checking with    │    │
│  │  deploy)     │  │   build test)│  │   .vale.ini)       │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
│                                                                   │
│  ┌──────────────────────────────┐                                │
│  │ update-nix-releases.yml     │                                │
│  │ (auto-updates nix version   │                                │
│  │  references in source/)     │                                │
│  └──────────────────────────────┘                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
                    ┌─────────────┐
                    │  Netlify    │
                    │  (CDN)      │
                    │  nix.dev    │
                    └─────────────┘
```

### Diataxis Content Framework

Content is strictly organized by the Diataxis framework, which separates documentation into four modes:

| Directory | Diataxis Type | Purpose | Examples |
|-----------|--------------|---------|----------|
| `source/tutorials/` | Tutorials | Step-by-step learning | First steps, Nix language, module system, NixOS, packaging, cross-compilation |
| `source/guides/` | How-to Guides | Practical tasks | CI/CD with Cachix, direnv, Python envs, binary caches, best practices |
| `source/concepts/` | Explanations | Background and understanding | Flakes deep-dive (322 lines), Nix store model, FAQ |
| `source/reference/` | Reference | Technical descriptions | Glossary, manual index, nixpkgs pinning reference |

### Build Toolchain

The documentation is built using **Sphinx** with the **MyST parser** for Markdown support:

- **MyST Markdown** — Adds Sphinx directives (`{ref}`, `{term}`, `{need}`), roles, and admonitions to standard CommonMark. Configured with heading anchors (3 levels deep), colon fences for admonitions, linkify for auto-linking, and task lists.
- **Sphinx Extensions**: `intersphinx` for cross-linking to other docs, `sphinx_copybutton` for code copy buttons, `sphinx_design` for card grids, `sphinx_sitemap` for SEO, `notfound` for custom 404, and a custom `extractable_code_block` extension that validates code examples.
- **Nix Build**: The `nix/` directory contains the Nix derivation for building the site, with pinned dependencies via `npins/`. An overlay provides custom Nixpkgs overrides.
- **Makefile Fallback**: Non-Nix build path using Python virtualenv for contributors without Nix installed.

### Prose Quality Automation

**Vale** is integrated as a prose linter with a custom configuration (`.vale.ini`) that enforces the project's style guide. A custom Nix vocabulary list prevents false positives on Nix-specific terminology. Runs on every PR via the `vale.yml` GitHub Actions workflow.

## Key Components

### Source Structure

- `source/tutorials/first-steps/` — 5 tutorials: ad-hoc shells, declarative shells, reproducible scripts, pinning nixpkgs
- `source/tutorials/nix-language.md` — Complete 200+ line Nix language tutorial
- `source/tutorials/module-system/` — Module system tutorial series
- `source/tutorials/nixos/` — NixOS deployment tutorials (ISOs, Docker images, Raspberry Pi, integration testing)
- `source/guides/recipes/` — 8 recipe files covering CC, binary caches, dependency management, direnv, post-build hooks, Python envs, sharing deps
- `source/concepts/flakes.md` — 322-line deep dive on Nix flakes (inputs, outputs, flake.lock, references, CLI)
- `source/contributing/documentation/` — Style guide, Diataxis framework documentation, tutorial writing guide

### Maintenance Infrastructure

- `maintainers/` — Google Season of Docs 2024 info, responsibilities, technical writers guide
- npins-format `sources.json` with pinned nixpkgs, nix, python documentation tools
- `update-nix-releases.nix` — Automatically updates Nix version references in documentation
- `run_code_block_tests.sh` — Extracts and runs example code blocks for validation

## Related

- [[nix.dev]] — Wiki page with complete content inventory
- [[nix-podman-stacks]] — Uses Nix module system for declarative container stacks
- [[quadlet-nix]] — Nix-based Quadlet container management with NixOS integration
- [[podman]] — Container engine deployed via Nix for reproducible dev environments
- [[bootc]] — Bootable container system using Nix-compatible image building patterns
- [[nix]] — The Nix package manager and NixOS ecosystem
