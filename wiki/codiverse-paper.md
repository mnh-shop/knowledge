---
name: codiverse-paper
tags: [cordis, paper, spatiotemporal-composability, programming-paradigm, revertible-effects, reactive-coeffects]
description: "Wiki entry for cordiverse/paper — A Programming Paradigm for Spatiotemporal Composability"
source: sources/codiverse-paper/
verification_date: 2026-08-16
verified_by: codegraph-verify
---

# codiverse-paper

||| Field | Value |
|||---|---|
||| **Origin** | [cordiverse/paper](https://github.com/cordiverse/paper) |
||| **Version** | Draft of August 13, 2026 |
||| **Commit** | `948a07b` — `upload paper` |
||| **License** | See repo LICENSE |
||| **Source** | `sources/codiverse-paper/` |
||| **CBM index** | `Users-admin-repos-knowledge-sources-codiverse-paper` (7 nodes, 6 edges) |

## What is it?

The Cordis paper: _A Programming Paradigm for Spatiotemporal Composability_. A preprint under active revision describing the formal foundations of Cordis, the meta-framework that powers DeepSeek Harness.

## Abstract

Modern software — from plugin systems to self-evolving agent harnesses — increasingly requires **dynamic composition**, yet its formal foundations remain underdeveloped. The paper identifies two orthogonal dimensions:

- **Temporal composability** — the ability to completely revert a component's side effects upon removal
- **Spatial composability** — the ability to declare and reactively manage inter-component dependencies

The paper addresses both by lifting classical effect and coeffect concepts to runtime mechanisms:

1. **Revertible effects** — every context transformation carries an inverse that the runtime tracks
2. **Reactive coeffects** — each change of the context notifies a component against its coeffect specification
3. **Unified context type** — effect context and coeffect context combined into a single context type, constituting a programming paradigm
4. **Component calculus** — dynamic composition calculus whose metatheory carries spatiotemporal composability from a single component to a whole system of interleaved components

The paper also describes **Cordis**, a meta-framework implementing these ideas: a core library with effect tracking and coeffect resolution, plus a declarative component loader with configuration reconciliation and hot module replacement.

## Files

- `paper.pdf` — the paper (draft, August 13, 2026)
- `README.md` — abstract and citation info
- `.gitattributes` — git attributes

## Relationship to DeepSeek Harness

DeepSeek Harness is powered by Cordis. The paper is the formal specification behind the "everything is a plugin" architecture. See [[deepseek-harness]].

## CBM index

CBM index captures `master` at commit `948a07b`. Excludes `.git/` (1 dir). 7 nodes, 6 edges (paper PDF + README + .gitattributes).

## Verification

See [[codiverse-paper.codegraph-verify]] for evidence-backed claims.
