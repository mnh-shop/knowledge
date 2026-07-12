---
name: hermes-profiles-index
description: "Catalog of 38 Hermes Agent role profiles — specialist personas with isolated configurations, skills, and SOUL documents"
tags: [agent-profile, harness, hermes-agent, profile, python, typescript, agent]
metadata:
  type: catalog
source: sources/hermes-profiles/
---

# Hermes Agent Profiles Catalog

Role-based specialist profiles for Hermes Agent. Each profile is a fully isolated instance with its own configuration, skills, and SOUL document defining first principles.

**Source:** `sources/hermes-profiles/profiles/` (38 profiles)

---

## Executive & Strategy

| Profile | Description | Core Skills |
|---|---|---|
| [[backend-engineer-profile]] | Implements API endpoints, database access, integration code | artifact-pyramids, backend-engineering |
| [[brand-designer-profile]] | Brand identity specialist — strategy, visual identity, guidelines | artifact-pyramids, brand-designer |
| [[ceo-profile]] | Vision to strategy translation, strategic trade-offs | artifact-pyramids, executive-methodology |
| [[cfo-profile]] | Financial strategy, capital discipline, fundraising | artifact-pyramids, financial-modeling |
| [[chro-profile]] | Organizational design, talent strategy, culture | artifact-pyramids, org-design |
| [[clo-profile]] | Legal strategy, regulatory risk, IP protection | artifact-pyramids, legal-strategy |
| [[cmo-profile]] | Go-to-market, brand, customer acquisition | artifact-pyramids, go-to-market |
| [[coo-profile]] | Operational design, execution infrastructure | artifact-pyramids, operational-design |
| [[cpo-profile]] | Product strategy, market fit, feature prioritization | artifact-pyramids, executive-methodology, product-strategy |
| [[cto-profile]] | Technology strategy, engineering standards, tech radar | artifact-pyramids, technology-radar |
| [[curator-profile]] | Knowledge management, cross-linking, ingestion | artifact-pyramids, curation-methodology |

## Engineering Roles

| Profile | Description | Core Skills |
|---|---|---|
| [[data-architect-profile]] | Data modeling, pipeline architecture, storage strategy | artifact-pyramids, data-architect |
| [[data-engineer-profile]] | ETL/ELT, analytical SQL, schema migrations | artifact-pyramids, data-engineering |
| [[data-scientist-profile]] | Statistical modeling, causal inference, ML research | artifact-pyramids, data-scientist |
| [[debugger-profile]] | Systematic debugging, root cause analysis | artifact-pyramids, debugging-methodology |
| [[frontend-engineer-profile]] | UI components, responsive layouts, client performance | artifact-pyramids, frontend-engineering |
| [[ml-engineer-profile]] | Model training, fine-tuning, inference serving | artifact-pyramids, ml-engineering |
| [[platform-engineer-profile]] | CI/CD, IaC, k8s, service networking | artifact-pyramids, platform-engineering |
| [[security-engineer-profile]] | Threat modeling, vulnerability assessment, pentesting | artifact-pyramids, security-audit-methodology |
| [[site-reliability-engineer-profile]] | SLO/SLI frameworks, observability, incident command | artifact-pyramids, site-reliability-engineering |
| [[technical-architect-profile]] | Service boundaries, API contracts, deployment topology | artifact-pyramids, software-architecture-analysis |

## Product & Planning

| Profile | Description | Core Skills |
|---|---|---|
| [[implementation-planner-profile]] | Work breakdown, dependency chains, milestone planning | artifact-pyramids, implementation-planning |
| [[kanban-strategist-profile]] | Flow optimization, WIP limits, board design | artifact-pyramids, kanban-guru |
| [[product-manager-profile]] | Specs, roadmaps, stakeholder alignment | artifact-pyramids, product-methodology |

## Quality & Research

| Profile | Description | Core Skills |
|---|---|---|
| [[qa-engineer-profile]] | Test strategy, automation, quality gates | artifact-pyramids, qa-methodology |
| [[researcher-profile]] | Deep-dive research, evidence gathering, synthesis | artifact-pyramids, research-methodology |
| [[reviewer-profile]] | Code review, quality gates, standards verification | artifact-pyramids, review-methodology |
| [[verifier-profile]] | Pass/fail verification against criteria | artifact-pyramids, verification-methodology |
| [[wonderer-profile]] | Lateral exploration, adjacent domains | artifact-pyramids, wonderer-methodology |

## Content & Documentation

| Profile | Description | Core Skills |
|---|---|---|
| [[copy-editor-profile]] | Grammar, punctuation, style guide enforcement | artifact-pyramids, copy-editor-methodology |
| [[editor-profile]] | Structural editing, argument coherence, voice | artifact-pyramids, editor-methodology |
| [[technical-writer-profile]] | API docs, READMEs, CLI help text, developer guides | artifact-pyramids, technical-documentation |
| [[writer-profile]] | Articles, blog posts, long-form content, narrative flow | artifact-pyramids, editorial-methodology |
| [[ux-designer-profile]] | User journeys, interaction flows, accessibility | artifact-pyramids, ux-methodology |

## Development Process

| Profile | Description | Core Skills |
|---|---|---|
| [[oss-contributor-profile]] | CONTRIBUTING.md-first, cross-fork PRs, releases | artifact-pyramids, opensource-contributions |
| [[spec-driven-development-profile]] | Formal specs, task plans, CLAUDE.md generation, phase gates | artifact-pyramids, sdd-authoring |

## Orchestration

| Profile | Description | Core Skills |
|---|---|---|
| [[orchestrator-profile]] | Decomposes questions, routes to specialists, synthesizes outputs | artifact-pyramids, orchestration-methodology |

---

## Shared Skills Pool

All profiles use symlinks to the shared skills pool at `sources/hermes-profiles/skills/`:

| Skill | Category |
|---|---|
| artifact-pyramids | Core output format |
| backend-engineering | Backend implementation |
| brand-designer | Brand strategy |
| contribution-pipeline | OSS workflow |
| copy-editor-methodology | Editing style guide |
| curation-methodology | Knowledge curation |
| data-architect | Data modeling |
| data-engineering | ETL/ELT pipelines |
| data-scientist | Statistics/ML |
| debugging-methodology | Systematic debugging |
| docker-management | Container ops |
| editor-methodology | Structural editing |
| editor-review-methodology | Review process |
| editorial-methodology | Content editing |
| executive-methodology | Decision frameworks |
| financial-modeling | Financial analysis |
| frontend-engineering | UI/UX implementation |
| go-to-market | Launch strategy |
| implementation-planning | Project planning |
| kanban-guru | Kanban optimization |
| legal-strategy | Legal/compliance |
| mermaid-diagrams | Diagramming |
| ml-engineering | ML pipelines |
| opensource-contributions | OSS etiquette |
| operational-design | Ops workflows |
| orchestration-methodology | Multi-agent orchestration |
| org-design | Organizational structure |
| platform-engineering | Platform ops |
| product-methodology | Product execution |
| product-strategy | Product vision |
| qa-methodology | Quality assurance |
| research-methodology | Research methods |
| researcher-workflow | Research process |
| review-methodology | Review process |
| sdd-authoring | Specification writing |
| sdd-review | Spec review |
| sdd-verification | Spec validation |
| sdd-work-decomposition | Task breakdown |
| security-audit-methodology | Security review |
| seo-audit | SEO analysis |
| seo-content-optimization | Content SEO |
| site-reliability-engineering | SRE practices |
| software-architecture-analysis | Architecture review |
| strategy-frameworks | Strategic planning |
| systematic-debugging | Debugging frameworks |
| tailscale | Tailscale config |
| technical-documentation | Docs craft |
| technology-radar | Tech assessment |
| traefik | Traefik config |
| ux-methodology | UX research |
| verification-methodology | Verification gates |
| wonderer-methodology | Lateral thinking |

---

## Usage

Hermes profiles provide **multi-instance isolation**:

```bash
hermes --profile backend-engineer   # Isolated instance with backend skills
hermes --profile cpo                 # Isolated instance with product strategy skills
hermes --profile orchestrator        # Multi-agent workflow coordinator
```

Each profile has its own:
- Configuration directory (`~/.hermes/profiles/<name>/`)
- API keys and credentials
- Memory and session state
- Skills symlinked from shared pool

---

## Related

- [[hermes-agent]] -- Main Hermes Agent wiki
- [[hermes-agent-profile]] -- Agent development guide
- [[hermes-workspace]] -- Swarm orchestration
- [[hermes-profiles]] -- Source repository wiki (if exists)