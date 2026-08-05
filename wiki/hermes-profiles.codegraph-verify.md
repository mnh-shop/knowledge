---
title: hermes-profiles
subtitle: CodeGraph Verification
date: 2026-07-12
tags: [hermes-profiles, codegraph-verify, hermes-agent, profiles]
suffix: .codegraph-verify
source: sources/hermes-profiles/
related: [[hermes-profiles]], [[hermes-agent]], [[hermes-profiles]], [[hermzner]]
verified-by: codegraph-explore
---

# hermes-profiles — CodeGraph Verification

**Verification date:** 2026-07-12
**Verified by:** codegraph-explore
**Source reference:** `sources/hermes-profiles/`

## Claim-1: 39+ specialist agent profiles with four-file structure

The repository contains 39 profile directories under `profiles/`, each with `SOUL.md`, `profile.yaml`, `README.md`, and `AGENTS.md`.

**Source evidence:** Direct enumeration via `find profiles -maxdepth 2 -name "*.md" -o -name "*.yaml"`:
- 39 profile directories: `backend-engineer`, `brand-designer`, `ceo`, `cfo`, `chief-of-staff`, `chro`, `clo`, `cmo`, `coo`, `copy-editor`, `cpo`, `cto`, `curator`, `data-architect`, `data-engineer`, `data-scientist`, `debugger`, `editor`, `frontend-engineer`, `implementation-planner`, `kanban-strategist`, `ml-engineer`, `orchestrator`, `oss-contributor`, `platform-engineer`, `product-manager`, `qa-engineer`, `researcher`, `reviewer`, `security-engineer`, `seo-specialist`, `site-reliability-engineer`, `spec-driven-development`, `technical-architect`, `technical-writer`, `ux-designer`, `verifier`, `wonderer`, `writer`.

**Supporting detail:** `CONTRIBUTING.md` lines 7-14 define the four-file requirement:
```
| File | Purpose |
|---|---|
| `SOUL.md` | Identity document — first principles, output contract, methodology mandate |
| `profile.yaml` | Metadata — description, required skills, recommended skills |
| `README.md` | Usage guide — installation, quick start, skill reference |
| `AGENTS.md` | Agent guidance — trigger patterns, loading order, handoff protocol |
```
`scripts/validate_profiles.py` lines 157-161 enforce this check programmatically:
```python
for required_file in ("SOUL.md", "profile.yaml", "README.md", "AGENTS.md"):
    if not (profile_dir / required_file).is_file():
        errors.append(f"{rel}: missing {required_file}")
```

## Claim-2: Shared skill pool with 54 skill categories at root `skills/`

The root `skills/` directory contains 54 skill categories as the single canonical copy. Each profile's `skills/` directory contains relative symlinks back to this pool.

**Source evidence:** `skills/` directory listing shows 54 entries including `architecture/` (with adr-authoring, arc42-context, architect-pyramid, c4-diagramming), `artifact-pyramids/`, `backend-engineering/`, `research-methodology/`, `researcher-workflow/`, `financial-modeling/`, `security-audit-methodology/`, etc.

**Supporting detail:** `README.md` lines 125-127:
> "Profiles symlink to the shared `skills/` directory, so one copy of each skill serves every profile. Git tracks symlinks by reference, not by duplicating content."

`AGENTS.md` lines 41-44:
> "Profiles do NOT contain skill files directly. Each profile's `skills/` directory contains **relative symlinks** back to the shared `skills/` pool at the repo root."

`CONTRIBUTING.md` lines 18-28 document the symlink convention:
```
skills/                          ← Actual skill files (one copy)
└── some-skill/
    ├── SKILL.md
    └── references/
profiles/some-profile/skills/    ← Symlinks
    └── some-skill -> ../../../skills/some-skill
```

## Claim-3: Validate_profiles.py checks semantic correctness beyond YAML syntax

`scripts/validate_profiles.py` is a comprehensive validation tool that checks duplicate YAML keys, required files, declared skills matching the shared pool, reachable symlinks, skill frontmatter validity, and broken/absolute symlinks.

**Source evidence:** `scripts/validate_profiles.py` lines 1-211:
- Lines 23-37: `UniqueKeyLoader` rejects duplicate YAML mapping keys.
- Lines 54-72: `extract_frontmatter()` validates YAML frontmatter with `---` delimiters and non-empty body.
- Lines 108-120: `declared_skills()` extracts `required` and `recommended` skill lists from `profile.yaml`.
- Lines 123-127: `reachable_profile_skills()` resolves symlinks in each profile's `skills/` directory.
- Lines 140-155: Validates all shared skill `SKILL.md` files have non-empty `name` and `description` frontmatter.
- Lines 157-186: Per-profile checks: required files exist, declared skills exist in shared pool, declared skills reachable from profile symlinks.
- Lines 188-195: Validates all symlinks are relative (`os.path.isabs(target)` check) and unbroken.

## Claim-4: Nine C-suite executive profiles for swarm orchestration

The repository includes C-suite profiles (CEO, CTO, CFO, COO, CPO, CMO, chief-of-staff, CLO, CHRO) with comprehensive SOUL.md documents covering first principles, communication style, decision-making heuristics, and relationship maps.

**Source evidence:** Profile directories confirm existence:
- `profiles/ceo/` — CEO document at `SOUL.md` (83 lines): "I translate vision into strategy, allocate capital and talent toward the highest-leverage outcomes" (line 1).
- `profiles/cto/` — CTO document at `SOUL.md` (86 lines): "I own the technology strategy and architecture governance of the company" (line 1).
- `profiles/cfo/`, `profiles/coo/`, `profiles/cpo/`, `profiles/cmo/`, `profiles/chief-of-staff/`, `profiles/clo/`, `profiles/chro/` all exist with identical four-file structure.
- `profiles/cto/SOUL.md` lines 72-78 document cross-profile relationships: "CEO — receives decomposed technical strategy... CFO — coordinates on technology investment sizing... platform-engineer — receives architectural constraints."
- `git log` confirms C-suite addition in commit `839828e`: "feat: add C-suite executive profiles for agent swarm orchestration (#100)"

## Claim-5: CI/CD pipeline with automated profile validation and Factory Droid review

The repository has three GitHub Actions workflows for PR validation, automated tagging, and AI-driven code review with depth assessment.

**Source evidence:**
- `.github/workflows/profile-checks.yml` lines 1-39: Triggered on PRs touching `profiles/**` or `skills/**`. Runs `pip install pyyaml` then `python3 scripts/validate_profiles.py`, also verifies README.md profile count matches filesystem.
- `.github/workflows/droid.yml` lines 1-39: Factory Droid automation triggered on issue/PR comments with `@droid`, issue/PR creation, and review submissions.
- `.github/workflows/droid-review.yml` lines 1-56: Factory Droid auto-review on PR open, with depth assessment: shallow for non-sensitive files, deep for files matching `(auth|oauth|jwt|secret|credential|crypt|dockerfile|config\.|terraform|...)` patterns.
- `.github/workflows/droid-review.yml` lines 28-33: Security-sensitive path detection gates deep review with `security=true` output.

## Claim-6: Profile SOUL.md documents follow Hermes-native artifact-pyramid output contract

Each profile's SOUL.md specifies an artifact-pyramid output format — progressive disclosure with absolute path handoff — as the universal response contract.

**Source evidence:** 
- `profiles/researcher/SOUL.md` lines 13-15: "Everything I produce is an artifact pyramid... The caller receives a single absolute path to `00-index.md` at the pyramid root. Not a summary. Not a natural-language handoff. Not a conversation. A path."
- `profiles/backend-engineer/SOUL.md` lines 13-15: Identical artifact-pyramid output contract.
- `profiles/cto/SOUL.md` lines 51-70: Complete pyramid structure definition with layer breakdown (00-index, 01-summary, 02-analysis, 03-dossiers) and rules.
- `profiles/ceo/SOUL.md` refers to CEO output contract with strategic mandates as artifact pyramid.
- `CONTRIBUTING.md` line 42: "Be Hermes-native (artifact-pyramid output, skill-based methodology loading)"

## Claim-7: Profile → skills mapping declared in profile.yaml (required/recommended)

Every profile's `profile.yaml` declares `skills.required` and optionally `skills.recommended`, and all 39 profiles list `artifact-pyramids` first. Symlinks in `profiles/<name>/skills/` mirror the declared set.

**Source evidence:**
- `profiles/researcher/profile.yaml:2-6` — `required: [artifact-pyramids, research-methodology, researcher-workflow]`; `profiles/researcher/skills/` contains exactly those 3 relative symlinks → `../../../skills/<name>` (mode 120000)
- `profiles/technical-architect/profile.yaml` — `required: [artifact-pyramids, c4-diagramming, adr-authoring, arc42-context, architect-pyramid, mermaid-diagrams, software-architecture-analysis]`
- `profiles/ceo/profile.yaml` — `required: [artifact-pyramids, executive-methodology, strategy-frameworks]`, `recommended: [mermaid-diagrams]`
- The 9 C-suite profiles (ceo/cfo/coo/cpo/cmo/cto/clo/chro/chief-of-staff) all require `executive-methodology` (verified across profile.yaml files)
- `scripts/validate_profiles.py:108-120` — `declared_skills()` reads `required` + `recommended` buckets from profile.yaml; lines 123-127 `reachable_profile_skills()` cross-checks against resolved symlinks

## Claim-8: Unexplained `.hermes/plans/` directory at repo root

The repository root contains a `.hermes/plans/` directory that no README/CONTRIBUTING/AGENTS doc explains.

**Source evidence:**
- `ls -la .hermes/plans/` shows a single file: `2026-06-05_123300-platform-engineer-profile.md` (a dated plan document for the platform-engineer profile)
- No mention of `.hermes/` in `README.md`, `CONTRIBUTING.md`, or `AGENTS.md` (grep confirms zero hits)
- **Verdict:** ⚠️ FLAGGED as an upstream gap — wiki notes the directory exists but is undocumented

## Dependency Map

```
hermes-profiles
  └─► hermes-agent (consumes these profiles for role-based operation)
  └─► skills (cross-project Agent Skills Open Standard taxonomy)
  └─► hermes-suite (all-in-one Hermes deployment using these profiles)
  └─► agentfield (control plane that orchestrates agents with specific profiles)
  └─► mission-control (MCP audit server monitoring profile-switching behavior)
  └─► hermzner (Hetzner automations that pair with platform-engineer/SRE profiles)
  └─► abvx-agent-skills (alternative skill collection, compatible SKILL.md format)
```
