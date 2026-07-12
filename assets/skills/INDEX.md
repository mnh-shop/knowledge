---
name: skills-catalog
description: "Cross-harness skills catalog organized by use case — 99 skill files across 66 categories with sub-catalog references to 1000+ skills from source repositories"
tags: [skills, catalog, index, cybersecurity, swe, mcp]
metadata:
  type: catalog
---

# Skills Catalog

Skills organized by **use case** with cross-harness compatibility. Skills are usable patterns that can run across multiple agentic harnesses (Hermes Agent, OpenClaw, GoClaw, AgentField, n8n, ECC, opencode, pydantic-ai).

**Total categories:** 66 (65 directories + 1 standalone skill file)
**Total skill files on disk:** 99
**Total sub-catalog references:** 1000+ (from indexed source repositories)

---

## How to Use This Catalog

Each category links to its directory containing SKILL.md files. Categories with sub-catalogs (INDEX.md) aggregate skills from source repositories into browsable lists.

**To load a skill:** Use your harness's skill loading mechanism (e.g., `skill_view(name='category-name')` in Hermes Agent, or reference the SKILL.md frontmatter directly).

**To find harness-compatible skills:** Check the "Compatible Harnesses" column. Skills without harness restrictions work across all platforms via MCP hooks.

---

## Use Case Categories

| Category | Skills | Description | Compatible Harnesses |
|----------|--------|-------------|---------------------|
| [Architecture](architecture/) | 4 | System design and architecture skills — C4 diagramming, ADR authoring, arc42 context, architect pyramid | hermes-agent, ECC, open-design |
| [Artifact Pyramids](artifact-pyramids/) | 1 | Progressive disclosure for AI agent outputs — Summary, Analysis Collection, Detailed Dossiers, with full SOURCES navigation | hermes-agent, ECC, openclaw |
| [Backend Engineering](backend-engineering/) | 1 | API patterns (REST, gRPC, GraphQL), service architecture (clean/hexagonal/layered), database access, error handling, testing | hermes-agent, ECC, goclaw, agentfield |
| [Brand Designer](brand-designer/) | 1 | Comprehensive brand identity documentation — strategy, visual identity, voice and tone, governance, asset inventory | openclaw, hermes-agent, ECC, open-design |
| [Chief of Staff Methodology](chief-of-staff-methodology/) | 1 | Gatekeeping, force multiplication, executive briefing, organizational sensing, institutional memory, meeting triage | hermes-agent, ECC |
| [Content Creation](content-creation/) | 95+ | [Sub-catalog](content-creation/) — copywriting, design, animation, media generation, 3D graphics, creative workflows | openclaw, hermes-agent, ECC, open-design |
| [Contribution Pipeline](contribution-pipeline/) | 1 | Issue-to-PR lifecycle with 5-phase gated pipeline — security-gated, tested, documented, clean-room verified | hermes-agent, ECC, opencode |
| [Copy Editor Methodology](copy-editor-methodology/) | 1 | Style guide enforcement, grammar and punctuation, consistency checking, proofreading protocols | hermes-agent, ECC, openclaw |
| [Curation Methodology](curation-methodology/) | 1 | Knowledge vault curation — atomic note principles, cross-linking heuristics, graph health diagnostics, curation cycle | hermes-agent, ECC |
| [Cybersecurity](cybersecurity/) | 900+ | [4 sub-catalogs](cybersecurity/) — AI & AppSec, Cloud & Infrastructure, Offensive Security, Governance & Compliance | hermes-agent, openclaw, goclaw, ECC, agentfield |
| [Data Architect](data-architect/) | 1 | Virtual data architect — data pipeline design, data modeling, platform evaluation, cost optimization, governance | hermes-agent, ECC, agentfield |
| [Data Engineering](data-engineering/) | 1 | Database operations (vector, relational, graph, time-series), ETL/ELT pipelines, SQL analytics, data quality, schema migration | hermes-agent, ECC, goclaw |
| [Data Scientist](data-scientist/) | 1 | PhD-level statistical analysis, experimental design, causal inference, advanced modeling, research methodology | hermes-agent, ECC, pydantic-ai |
| [Debugging Methodology](debugging-methodology/) | 1 | Systematic debugging — root cause analysis, error reproduction, isolation techniques, verification protocols | hermes-agent, ECC, opencode |
| [Docker Management](docker-management/) | 1 | Container lifecycle — Dockerfiles, multi-stage builds, Compose stacks, registries, networking, production patterns | ECC, hermes-agent, agentfield |
| [Editor Methodology](editor-methodology/) | 1 | Professional editorial process — argument coherence, structural editing, engagement quality, voice consistency | hermes-agent, ECC, openclaw |
| [Editor Review Methodology](editor-review-methodology/) | 1 | Editorial review — fact-checking, voice audit, engagement review, source integrity assessment | hermes-agent, ECC, openclaw |
| [Editorial Methodology](editorial-methodology/) | 1 | Voice discipline, article structure patterns, source hygiene, revision protocols for content creation | hermes-agent, ECC, openclaw |
| [Executive Methodology](executive-methodology/) | 1 | C-suite decision frameworks (RAPID, DACI), strategic thinking (inversion, first principles), governance, stakeholder communication | hermes-agent, ECC, open-design |
| [Financial Modeling](financial-modeling/) | 1 | CFO methodology — unit economics, pricing strategy, fundraising, budget frameworks, SaaS metrics, cap tables | hermes-agent, ECC |
| [Frontend Engineering](frontend-engineering/) | 1 | Component architecture, state management, API integration, responsive layout, performance, frontend testing | hermes-agent, ECC, goclaw, agentfield |
| [Go-to-Market](go-to-market/) | 1 | CMO methodology — positioning and messaging, customer acquisition strategy, brand architecture, market entry, growth modeling | hermes-agent, ECC, open-design |
| [Implementation Planning](implementation-planning/) | 1 | Work breakdown, dependency analysis, critical path identification, risk assessment, rollback planning | hermes-agent, ECC, opencode |
| [Infrastructure](infrastructure/) | 35+ | [Sub-catalog](infrastructure/) — deployment, homelab, networking, Kubernetes, system operations | ECC, hermes-agent, agentfield, goclaw |
| [Kanban Guru](kanban-guru/) | 1 | Flow diagnosis, board configuration, WIP limits, service level expectations, Scrum-to-Kanban transitions | hermes-agent, ECC, open-design |
| [Legal Strategy](legal-strategy/) | 1 | CLO methodology — regulatory landscape (GDPR, CCPA, AI Act), IP strategy, contract risk, data privacy, corporate governance | hermes-agent, ECC |
| [Mermaid Diagrams](mermaid-diagrams/) | 1 | Platform-agnostic diagramming — flowcharts, sequence diagrams, C4, class/state/ER/Gantt, renders via mmdc CLI or CDN | hermes-agent, ECC, opencode, all MCP |
| [ML Engineering](ml-engineering/) | 1 | Model training, fine-tuning (LoRA/QLoRA), evaluation, quantization, deployment, MLOps pipeline design | hermes-agent, ECC, agentfield |
| [n8n Workflows](n8n-workflows/) | 188 | [Sub-catalog](n8n-workflows/) — 90+ workflow automation categories via n8n-mcp skills integration | n8n (native), all (via MCP) |
| [OpenClaw](openclaw/) | — | OpenClaw skills README — curated agent skills and capabilities defined in AGENTS.md format | openclaw, goclaw |
| [OpenClaw Extensions](openclaw-extensions/) | 42 | [Sub-catalog](openclaw-extensions/) — extensions and platform-specific skills for OpenClaw | openclaw, goclaw |
| [Open Source Contributions](opensource-contributions/) | 1 | Good open source citizenship — CONTRIBUTING.md norms, bug reports, feature requests, pull requests | hermes-agent, ECC, opencode |
| [Operational Design](operational-design/) | 1 | COO methodology — process design, scaling, operational metrics, compliance, vendor management, team topology | hermes-agent, ECC, open-design |
| [Orchestration](orchestration/) | 54+ | [Sub-catalog](orchestration/) — workflow orchestration skills for planning, coordination, multi-agent systems | hermes-agent, n8n, agentfield, ECC, open-design |
| [Orchestration Methodology](orchestration-methodology/) | 1 | Task decomposition, specialist routing, synthesis patterns, multi-agent workflow design | hermes-agent, ECC, agentfield |
| [Org Design](org-design/) | 1 | CHRO methodology — team topologies, talent strategy, compensation frameworks, culture architecture, health metrics | hermes-agent, ECC, open-design |
| [Platform Engineering](platform-engineering/) | 1 | Infrastructure as code, CI/CD, container orchestration, service networking, internal developer platforms | ECC, hermes-agent, agentfield, goclaw |
| [Product Management](product-management/) | 45+ | [Sub-catalog](product-management/) — PRD, roadmap planning, capability mapping, stakeholder workflows | hermes-agent, ECC, open-design |
| [Product Methodology](product-methodology/) | 1 | RICE, MoSCoW, Opportunity Solution Trees, customer interviews, spec templates, decision logs | hermes-agent, ECC, open-design |
| [Product Strategy](product-strategy/) | 1 | CPO methodology — product vision, competitive analysis, roadmap prioritization, PMF, market sizing, platform strategy | hermes-agent, ECC, open-design |
| [QA Methodology](qa-methodology/) | 1 | Test strategy, test automation, regression testing, CI quality gates, test data management, quality metrics | hermes-agent, ECC, opencode |
| [Research](research/) | 45+ | [Sub-catalog](research/) — literature review, web search, evidence gathering, continuous learning, knowledge synthesis | hermes-agent, openclaw, pydantic-ai, af-deep-research, ECC |
| [Research Methodology](research-methodology/) | 1 | Professional research — journalistic investigation, industry analysis, technical verification, academic-style systematic research | hermes-agent, ECC, pydantic-ai |
| [Researcher Workflow](researcher-workflow/) | 1 | Non-interactive deep research pipeline for specialist subagents — receive mission, gather, evaluate gaps, build pyramid, deliver | hermes-agent, ECC, agentfield |
| [Review Methodology](review-methodology/) | 1 | Code review, security audit, architectural review, kanban swarm verification — Google standards, OWASP | hermes-agent, ECC, opencode |
| [SDD Authoring](sdd-authoring/) | 1 | Specification authoring — Gherkin, user stories, acceptance criteria, spec quality gates, artifact-pyramid compliance | hermes-agent, ECC, open-design |
| [SDD Review](sdd-review/) | 1 | SDD phase-gate review — enforces gated structure, reviews artifacts before next phase, produces gate decision reports | hermes-agent, ECC, open-design |
| [SDD Verification](sdd-verification/) | 1 | Acceptance criteria verification — maps specs to tests, validates implementation, produces VERIFICATION.md reports | hermes-agent, ECC, opencode |
| [SDD Work Decomposition](sdd-work-decomposition/) | 1 | Translates specs into dependency-aware task plans with per-task acceptance criteria, produces TASK-PLAN.md | hermes-agent, ECC, open-design |
| [Security Audit Methodology](security-audit-methodology/) | 1 | Threat modeling, vulnerability classification, defense-in-depth, dependency analysis, OWASP/CWE/STRIDE/LINDDUN | hermes-agent, openclaw, goclaw, ECC |
| [SEO Audit](seo-audit/) | 1 | Full-spectrum SEO + AEO — technical crawl, on-page optimization, JSON-LD/Schema.org, Ghost CMS, content strategy gap | hermes-agent, ECC, openclaw |
| [SEO Content Optimization](seo-content-optimization/) | 1 | Page title audits, schema injection, meta description rewrites, URL hygiene, local landing pages, measurement | hermes-agent, ECC, openclaw |
| [Site Reliability Engineering](site-reliability-engineering/) | 1 | SLOs, incident command, observability, error budgets, operational excellence — production reliability patterns | ECC, hermes-agent, agentfield |
| [Software Architecture Analysis](software-architecture-analysis/) | 1 | Reverse-engineer codebases — architecture, data flow, privacy posture, feature surface; produce clean-room design docs | hermes-agent, ECC, opencode |
| [Software Engineering](software-engineering/) | 235+ | [Sub-catalog](software-engineering/) — coding, debugging, architecture, testing, domain-specific healthcare patterns | hermes-agent, openclaw, ECC, goclaw, agentfield |
| [Strategy Frameworks](strategy-frameworks/) | 1 | CEO methodology — OKRs, mission/vision/values, competitive moat analysis, growth frameworks, capital allocation, M&A | hermes-agent, ECC, open-design |
| [Systematic Debugging](systematic-debugging/) | 1 | 4-phase root cause debugging — for ANY technical issue, especially under time pressure or after failed fix attempts | hermes-agent, ECC, opencode |
| [Tailscale](tailscale/) | 1 | WireGuard overlay networking — mesh VPN, ACL policies, subnet routing, exit nodes, Headscale self-hosted | ECC, hermes-agent, agentfield |
| [Technical Documentation](technical-documentation/) | 1 | API reference, README authorship, CLI help text, agent-facing docs (AGENTS.md), developer guides, info architecture | hermes-agent, ECC, opencode |
| [Technology Radar](technology-radar/) | 1 | CTO methodology — technology evaluation, build-vs-buy, engineering metrics, technical debt, innovation pipeline | hermes-agent, ECC, open-design |
| [Token Efficiency](token-efficiency/) | 10+ | [Sub-catalog](token-efficiency/) — LLM token usage optimization, budget management, cost-aware development | hermes-agent, ECC, agentfield |
| [Traefik](traefik/) | 1 | Reverse proxy, load balancer, ingress controller — dynamic routing, TLS, middleware, Docker/Kubernetes integration | ECC, hermes-agent, agentfield |
| [UX Methodology](ux-methodology/) | 1 | User research, interaction design, accessibility standards, usability evaluation | hermes-agent, ECC, open-design |
| [Verification Methodology](verification-methodology/) | 1 | Criteria-driven gatekeeping, evidence assessment, completion verification | hermes-agent, ECC, opencode |
| [Wonderer Methodology](wonderer-methodology/) | 1 | Exploring adjacent ideas, overlooked angles, lateral research paths without collapsing to a single answer | hermes-agent, ECC, pydantic-ai |

**Standalone file:** [hermes-startup-architect-skill.md](hermes-startup-architect-skill.md) — transforms raw startup ideas into comprehensive research-backed startup kits

---

## Groups

Skills grouped by broader domain for easier navigation.

| Group | Categories | Skills Count | Primary Harnesses |
|-------|-----------|-------------|------------------|
| **🏗️ Architecture & System Design** | Architecture, Artifact Pyramids, Software Architecture Analysis, Software Engineering, Backend Engineering, Frontend Engineering, Platform Engineering, Technology Radar, Mermaid Diagrams | 12 | hermes-agent, ECC, open-design |
| **🔒 Security & Compliance** | Cybersecurity, Security Audit Methodology, Legal Strategy, Data Architect | 900+ | hermes-agent, openclaw, goclaw, ECC |
| **📊 Data & ML** | Data Engineering, Data Scientist, ML Engineering | 3 | hermes-agent, ECC, agentfield, pydantic-ai |
| **🧪 Research & Analysis** | Research, Research Methodology, Researcher Workflow, Wonderer Methodology, Curation Methodology | 48+ | hermes-agent, ECC, pydantic-ai, af-deep-research |
| **🎯 Product & Strategy** | Product Management, Product Methodology, Product Strategy, Strategy Frameworks, Go-to-Market, Brand Designer, Kanban Guru, UX Methodology | 52+ | hermes-agent, ECC, open-design |
| **📝 Content & Editorial** | Content Creation, Copy Editor Methodology, Editor Methodology, Editor Review Methodology, Editorial Methodology, SEO Audit, SEO Content Optimization, Technical Documentation | 101+ | openclaw, hermes-agent, ECC, open-design |
| **⚙️ Development Workflow** | Contribution Pipeline, Implementation Planning, QA Methodology, Review Methodology, Systematic Debugging, Debugging Methodology, Verification Methodology, Open Source Contributions | 8 | hermes-agent, ECC, opencode |
| **📋 SDD Pipeline** | SDD Authoring, SDD Review, SDD Verification, SDD Work Decomposition | 4 | hermes-agent, ECC, open-design |
| **🚀 Orchestration & Automation** | Orchestration, Orchestration Methodology, n8n Workflows, Token Efficiency | 65+ | hermes-agent, n8n, agentfield, ECC |
| **👔 Executive & Operations** | Executive Methodology, Chief of Staff Methodology, Financial Modeling, Operational Design, Org Design | 5 | hermes-agent, ECC, open-design |
| **🖥️ Infrastructure & Ops** | Infrastructure, Docker Management, Tailscale, Traefik, Site Reliability Engineering, Platform Engineering | 40+ | ECC, hermes-agent, agentfield, goclaw |
| **🔌 OpenClaw Ecosystem** | OpenClaw, OpenClaw Extensions | 42 | openclaw, goclaw |

---

## Skill Loading Quick Reference

How to load skills in each harness:

| Harness | Load Command / Method | Example |
|---------|----------------------|---------|
| **Hermes Agent** | `skill_view(name='category/skill-name')` | `skill_view(name='architecture/c4-diagramming')` |
| **OpenClaw** | Symlink to `skills/` directory | `ln -s category/skills/* ~/.claw/skills/` |
| **GoClaw** | Place in `skills/` directory | `cp -r category ~/.goclaw/skills/` |
| **AgentField** | Reference in skill graph | Skill subdirectory in agent config |
| **ECC** | `skill_view(name='category')` or hook | `skill_view(name='systematic-debugging')` |
| **opencode** | Skills directory reference | OpenCode automatically loads from `.opencode/skills/` |
| **n8n** | MCP tool invocation | Call via n8n-mcp server node |
| **pydantic-ai** | Tool decorator import | `@agent.tool` wrapping skill logic |

---

## Harness Compatibility Matrix

| Harness | Native Skills Format | Can Use | Notes |
|---------|-------------------|---------|-------|
| **Hermes Agent** | SKILL.md with frontmatter | abvx, ECC (hooks), Hermes-caduceus, open-design | Progressive disclosure, symlinked skills |
| **OpenClaw** | skills/ directories | hermes-profiles (via symlink), extensions | ClawHub registry integration |
| **GoClaw** | skills/ directories | Native skills, skill-creator pattern | Document processing focus |
| **AgentField** | skill/ subdirectories | ECC (hooks), n8n-mcp | Harness orchestration support |
| **n8n** | MCP tools via n8n-mcp | All skills (via hooks/MCP) | Workflow automation platform |
| **ECC** | .claude/skills/ with hooks | All skills (aggressive hooks) | 273 native skills + hook ecosystem |
| **opencode** | skills/ directories | open-design, n8n, pydantic-ai | Native skill format |
| **pydantic-ai** | tool-calling approach | pydantic-ai skills, can wrap others | Tool-calling based |

---

## Skill Structure

Each skill directory follows one of two patterns:

**Standalone SKILL.md (65 categories):** A single SKILL.md file with YAML frontmatter (name, description, version, compatibility, tags) and markdown body containing procedural instructions, reference links, and output templates. These are methodology or profile skills designed to be loaded as a complete workflow.

**Sub-catalog with INDEX.md (9 categories):** An INDEX.md that aggregates skills from multiple source repositories into organized listings. These categories (cybersecurity, software-engineering, research, orchestration, infrastructure, content-creation, product-management, token-efficiency, n8n-workflows) reference 1000+ skills from the source repositories listed below.

**Extension catalog (1 category):** The OpenClaw Extensions directory contains 42 SKILL.md files organized into `extensions/` and `skills/` subdirectories, providing platform-specific skills for the OpenClaw harness.

---

## Source Repositories

Skills come from these primary sources, indexed as full repo clones under `sources/`:

- `sources/Anthropic-Cybersecurity-Skills/` — 817 security testing skills
- `sources/SecuritySkills/` — 45 framework-grounded AI security skills
- `sources/awesome-openclaw-skills/skills/` — ~20 security + audit skills
- `sources/reverse-skill/skills/` — 15 reverse engineering skills
- `sources/CyberStrikeAI/skills/` — Security testing skills
- `sources/abvx-agent-skills/` — 55+ general agent skills (Matt Pocock)
- `sources/ECC/` — 285+ ECC skills + hooks ecosystem
- `sources/hermes-agent/skills/` — 72 Hermes skills in 18 categories
- `sources/hermes-profiles/skills/` — 40 shared methodology skills
- `sources/openclaw/extensions/` — Platform-specific extension skills
- `sources/open-design/skills/` — 160+ design/creative skills
- `sources/n8n-skills/` — 14 n8n workflow skills
- `sources/pydantic-ai-skills/` — Pydantic AI skills framework
- `sources/af-deep-research/` — Deep research agent skills
- `sources/oh-my-hermes/` — OMH plugin ecosystem skills
- `sources/hexstrike-ai/` — Security framework skills
- `sources/oh-my-openagent/` — OpenAgent plugin system skills
- `sources/nanobot/` — Nanobot agent skills and patterns
- `sources/materia/` — Materia agent framework skills
- `sources/skills/` — General-purpose skill collection
- `sources/ai-marketing-claude-code-skills/` — AI marketing skills
- `sources/claude-ai-music-skills/` — AI music creation skills
- `sources/openai-skills/` — OpenAI integration skills

---

*To add a new category: create a directory under `assets/skills/`, add a `SKILL.md` with YAML frontmatter and markdown body, then update this INDEX.md. For sub-catalog categories, create an `INDEX.md` that references source repo skills with descriptions and compatibility info.*
