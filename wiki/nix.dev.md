---
name: nix.dev
tags: [developer-tools, documentation, git, nix]
description: "Official documentation for getting things done with Nix"
---

# nix.dev

**Source:** `sources/nix.dev/`

nix.dev is the official documentation site for the Nix package manager and NixOS. Hosted at https://nix.dev, it provides tutorials, guides, recipes, concepts, and reference material for learning and using Nix effectively. Maintained by the NixOS Foundation.

| Field | Value |
|---|---|
| **Origin** | [NixOS/nix.dev](https://github.com/NixOS/nix.dev) |
| **License** | CC-BY-SA-4.0 (documentation), MIT (tooling) |
| **Stack** | MyST Markdown, Sphinx, Nix |
| **Site** | https://nix.dev |
| **Source** | `sources/nix.dev/` |

## Key Features

- **Tutorials:** Step-by-step learning paths covering first steps (ad-hoc shell environments, declarative shells, reproducible scripts, pinning nixpkgs), Nix language, module system, NixOS (installation, building ISOs, Docker images, Raspberry Pi, integration testing), packaging, cross-compilation, and more.
- **Guides & Recipes:** Practical guides with troubleshooting, best practices, FAQ, and use-case recipes including CI/CD (GitHub Actions), direnv integration, dependency management, binary caches, Python environments, and post-build hooks.
- **Concepts:** Deep dives into Nix flakes, the Nix store model, and frequently asked conceptual questions.
- **Reference:** Glossary, Nix manual index, and nixpkgs pinning reference.
- **Contributing Documentation:** Style guide, Diataxis framework for documentation types, writing tutorials guide, and how to contribute.
- **Vale Integration:** Automated prose style checking with custom Nix vocabulary.
- **Published via Netlify** with automated builds from the main branch.

## Architecture

Sphinx-based documentation site using MyST (Markedly Structured Text, a superset of CommonMark). Content organized by the Diataxis framework (tutorials, how-to guides, explanations, reference). Built with Nix for reproducible builds, deployed via Netlify.

### Key Source Directories

| Directory | Purpose |
|---|---|
| `source/tutorials/` | Tutorials (first steps, Nix language, module system, NixOS, packaging, cross-compilation) |
| `source/guides/` | How-to guides, recipes (CI, direnv, binary caches, Python), best practices, FAQ, troubleshooting |
| `source/concepts/` | Conceptual explanations (flakes, FAQ) |
| `source/reference/` | Glossary, manual index, nixpkgs pinning |
| `source/contributing/` | Contributor documentation, style guide, Diataxis framework |
| `source/_ext/` | Sphinx extensions |
| `source/_templates/` | Sphinx templates |
| `maintainers/` | Project maintenance docs, documentation survey, Google Season of Docs 2024 info |
| `nix/` | Nix build infrastructure (`default.nix`, inputs, overlays, version data) |
| `npins/` | Pinned dependency sources |

## Interfaces

- **Web:** Published at https://nix.dev
- **Nix Build:** Buildable via `nix build` using the `nix/` build infrastructure
- **CI:** GitHub Actions (`build-and-deploy.yml`, `test.yml`, `vale.yml`, `update-nix-releases.yml`)
- **Vale:** Automated prose style checking

## Related

- [[nix-podman-stacks]] -- Uses Nix module system for declarative container stacks
- [[podman]] -- Container engine commonly deployed via Nix
