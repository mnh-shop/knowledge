---
name: hermes-profiles-catalog
description: "All 39 Hermes Agent specialization profiles — role identity (SOUL.md), skill dependencies, and configuration each deployable as a hermz agent"
tags: [hermes-profiles, catalog, agent-profile, hermes-agent]
metadata:
  type: catalog
---

# Hermes Profiles Catalog

39 specialization profiles for Hermes Agent. Each profile packages a role identity (SOUL.md), skill dependencies, and configuration that can be deployed as a hermz agent. These are the actual runtime profiles — see `sources/hermes-profiles/profiles/` for the source of truth.

## Foundational Roles

| Profile | Description |
|---------|-------------|
| **orchestrator** | Decompose/sequence/synthesize pattern — breaks work into phases, assigns subagents, verifies outputs |
| **spec-driven-development** | Formal spec pipeline — writes specs before code, validates against them, prevents scope creep |
| **implementation-planner** | Work breakdown structure + critical path — plans multi-step implementations with dependency ordering |
| **verifier** | Verification gatekeeper — checks outputs against acceptance criteria before delivery |

## Technical Roles

| Profile | Description |
|---------|-------------|
| **backend-engineer** | API-boundary discipline, business-logic isolation, service-oriented development |
| **frontend-engineer** | Component composition, co-located state, UI architecture |
| **data-engineer** | Pipeline design, data integrity, operational databases |
| **data-scientist** | Causal inference, reproducibility, statistical analysis |
| **data-architect** | Data modeling, schema design, storage strategy |
| **ml-engineer** | Model training, optimization, reproducible ML pipelines |
| **platform-engineer** | Infrastructure design, platform architecture, deployment systems |
| **site-reliability-engineer** | Production reliability, incident management, SLO/SLI frameworks |
| **technical-architect** | Systems architecture, technology decisions, cross-system integration |
| **security-engineer** | Threat modeling, defense-in-depth, security review methodology |
| **qa-engineer** | Test strategy, quality gates, automation-first testing |
| **debugger** | Root-cause analysis, reproduction-first debugging, systematic diagnosis |

## Product & Management Roles

| Profile | Description |
|---------|-------------|
| **product-manager** | PRD writing, roadmap planning, stakeholder communication |
| **cpo** | Chief Product Officer — product strategy, portfolio decisions |
| **cto** | Technical strategy, architecture governance, engineering leadership |
| **ceo** | Executive decision-making, strategy, organizational direction |
| **cfo** | Financial planning, budgeting, resource allocation |
| **coo** | Operations management, process optimization |
| **chro** | Human resources, team development, organizational culture |
| **clo** | Legal compliance, risk management, regulatory oversight |
| **cmo** | Marketing strategy, brand positioning, go-to-market |
| **chief-of-staff** | Leadership amplifier — cross-domain execution, prioritization |

## Creative & Content Roles

| Profile | Description |
|---------|-------------|
| **writer** | Structure-first prose, voice discipline, long-form content |
| **editor** | Content refinement, structure critique, narrative coherence |
| **copy-editor** | Grammar, punctuation, consistency — final polish before publication |
| **technical-writer** | Interface-level documentation, user-centered technical docs |
| **brand-designer** | Visual identity systems, brand language, cross-surface consistency |
| **ux-designer** | User-centered design, accessibility-first, interaction patterns |
| **curator** | Atomic notes, knowledge graph building, connection-driven information management |

## Review & Specialized Roles

| Profile | Description |
|---------|-------------|
| **researcher** | Question-first methodology, evidence hierarchy, deep-dive investigation |
| **reviewer** | Intent-aware code review, constructive criticism, quality gates |
| **wonderer** | Lateral exploration, adjacent possibilities, expanding questions |
| **kanban-strategist** | Flow optimization, WIP limits, bottleneck analysis |
| **seo-specialist** | Content discoverability, search optimization, structured metadata |
| **oss-contributor** | Open source contribution lifecycle, project conventions, release management |

## Related

- [[hermes-agent]] — Hermes Agent wiki (the runtime these profiles target)
- [[hermes-profiles]] — Wiki page for the hermes-profiles source repo
- [[agent-references]] — Agent system reference cards (distinct from runtime profiles)
- [[skills-catalog]] — Skills used by these profiles