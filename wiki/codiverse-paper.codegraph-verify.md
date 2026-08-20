---
name: codiverse-paper-codegraph-verify
tags: [codiverse-paper, codegraph-verify, cordis, paper, spatiotemporal-composability]
description: "Codegraph Verification: codiverse-paper — validating wiki claims against indexed source code symbols"
source: sources/codiverse-paper/
---

# Codegraph Verification: codiverse-paper

**Date:** 2026-08-16

**Version checked:** `948a07b` (master, `upload paper`)

**CBM project:** `Users-admin-repos-knowledge-sources-codiverse-paper` (7 nodes, 6 edges)

## Claim 1: This is a standalone clone of cordiverse/paper

- **Wiki says:** `sources/codiverse-paper/` is a clone of the cordiverse/paper repository.
- **Source evidence:**
  - `sources/codiverse-paper/.git/` — standard git directory
  - `git remote -v` — `origin https://github.com/cordiverse/paper.git`
  - `git branch -vv` — `master` tracking `origin/master`
- **Verdict:** ✅ CORRECT — standalone clone with correct remote

## Claim 2: Paper is "A Programming Paradigm for Spatiotemporal Composability"

- **Wiki says:** The paper title is _A Programming Paradigm for Spatiotemporal Composability_.
- **Source evidence:**
  - `README.md` — `# A Programming Paradigm for Spatiotemporal Composability`
  - `README.md` — `[Read the paper (PDF)](paper.pdf) · Draft of August 13, 2026`
- **Verdict:** ✅ CORRECT — title matches README

## Claim 3: Draft date is August 13, 2026

- **Wiki says:** Draft of August 13, 2026.
- **Source evidence:**
  - `README.md` — `Draft of August 13, 2026`
  - `git log --oneline -1` — `948a07b upload paper` (same date as wiki verification)
- **Verdict:** ✅ CORRECT — date confirmed in README

## Claim 4: paper.pdf exists

- **Wiki says:** The paper PDF is at `paper.pdf`.
- **Source evidence:**
  - `find . -type f` — `./paper.pdf` present
  - `README.md` — `[Read the paper (PDF)](paper.pdf)`
- **Verdict:** ✅ CORRECT — PDF file present

## Claim 5: Paper describes revertible effects + reactive coeffects

- **Wiki says:** Paper formalizes revertible effects (context transformations with inverses) and reactive coeffects (context changes notify components against coeffect specs).
- **Source evidence:**
  - `README.md` abstract — "we formalize _revertible effects_, in which every context transformation carries an inverse that the runtime tracks. We formalize _reactive coeffects_, in which each change of the context notifies a component against its coeffect specification."
- **Verdict:** ✅ CORRECT — abstract confirms both concepts

## Claim 6: Cordis is the implementation

- **Wiki says:** Paper describes Cordis as a meta-framework implementing these ideas.
- **Source evidence:**
  - `README.md` — "We implement these ideas in _Cordis_, a meta-framework of spatiotemporal composability that provides a core library with effect tracking and coeffect resolution, as well as a declarative component loader with configuration reconciliation and hot module replacement."
- **Verdict:** ✅ CORRECT — Cordis described in abstract

## Claim 7: CBM index is minimal (7 nodes, 6 edges)

- **Wiki says:** 7 nodes, 6 edges (paper PDF + README + .gitattributes).
- **Source evidence:**
  - CBM output: `"nodes":7,"edges":6`
  - Files on disk: `paper.pdf`, `README.md`, `.gitattributes` (3 files)
  - CBM DB: 1.7M on disk (tiny)
- **Verdict:** ✅ CORRECT — stats match file count

## Claim 8: Only 2 commits on master

- **Wiki says:** 2 commits: initial commit + upload paper.
- **Source evidence:**
  - `git log --oneline` — `948a07b upload paper`, `17a0f0 initial commit`
- **Verdict:** ✅ CORRECT — 2 commits confirmed

## Claim 9: Index excludes .git/

- **Wiki says:** CBM index excludes `.git/` directory.
- **Source evidence:**
  - CBM output: `"excluded":{"dirs":[".git"],"count":1,"truncated":false}`
- **Verdict:** ✅ CORRECT — exclusion confirmed in CBM output
