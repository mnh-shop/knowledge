---
title: n8n-workflows.codegraph-verify
date: 2026-07-12
tags: [n8n-workflows, codegraph-verify, n8n, workflows]
related: [[n8n-workflows]], [[n8n]], [[n8n-mcp]], [[n8n-skills]]
source: sources/n8n-workflows/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# n8n-workflows — CodeGraph Verification

## Claim-1: 2,061 workflow JSONs across 188 service-named category directories

The repository contains 2,061 n8n workflow JSON files organized into 188 top-level category directories under `workflows/`. The directories are service-named — they take the n8n node class name (`Activecampaign`, `Awsrekognition`, `Baserow`, `Clickup`, `Emailreadimap`, `Emailsend`, `Awss3`, `Gmail`, `Slack`) rather than curated topic folders. A handful of utility/flow dirs (`Aggregate`, `Code`, `Compression`, `Cron`, `Crypto`) accompany the service dirs.

**Source evidence:** `workflows/` directory listing — 188 top-level entries (measured: `ls workflows/ | wc -l` = 188; `find workflows/ -name '*.json' -type f | wc -l` = 2,061). `README.md` lines 46-49 ("By The Numbers": "4,343 Production-Ready Workflows", "365 Unique Integrations", "29,445 Total Nodes", "15 Organized Categories") are stale upstream claims — the filesystem holds 2,061 JSONs, and the wiki's count matches the filesystem, not the README.

## Claim-2: FastAPI backend with SQLite FTS5 full-text search (<100ms response)

The backend uses Python FastAPI with SQLite FTS5 for full-text search across workflow names, descriptions, and nodes. API endpoints include `/api/search`, `/api/stats`, `/api/workflow/{id}`, `/api/categories`, `/api/export` (6 endpoints). The server is launched via `run.py` and initialized with `workflow_db.py`.

**Source evidence:** `README.md` lines 55-60 (Performance: "< 100ms Search Response", "< 50MB Memory Usage"), lines 105-114 (API Endpoints table with 6 endpoints), lines 116-119 (Search Features). `api_server.py` lines 23-29 (FastAPI app init with title/description/version), line 34 (`MAX_REQUESTS_PER_MINUTE = 60`), lines 42-56 (CORS restricted to 5 origins, `allow_methods=["GET", "POST"]`, `allow_headers=["Content-Type", "Authorization"]`). `workflow_db.py` confirmed (WorkflowDatabase class, SQLite FTS5 trigger at lines 86-103).

## Claim-3: Computed collection statistics (nodes, complexity, triggers, services)

Computed across all 2,061 parsed workflow JSONs: **30,774 total nodes** (avg **14.93** nodes/workflow), **85 distinct trigger node types** (top: `manualTrigger` 927, `scheduleTrigger` 330, `executeWorkflowTrigger` 180, `formTrigger` 123), and **319 distinct non-utility `n8n-nodes-base.*` service integrations** (334 raw types including utility nodes `stickyNote`/`noOp`/`set`/`code`/`if`/`merge`/`splitOut`). The earlier wiki figures (8,923 nodes, 5.4 avg, 48 triggers, 282 services) and the README's "365+ integrations" (README.md:7) are all stale or incorrect.

**Source evidence:** Computed by parsing `workflows/**/*.json` (2,061 files): `total_nodes = 30,774`, `avg = 30,774/2,061 = 14.93`, 85 distinct types matching `*Trigger` in the `type` field, 319 distinct `n8n-nodes-base.*` types after removing utility/flow nodes. `docs/api/stats.json` is stale (total_workflows 4343, unique_integrations 268 — generated from the pre-trim dataset on 2025-11-03) and must not be used for current counts.

## Claim-4: Docker deployment with multi-platform builds and security scanning

Supports Docker deployment via `Dockerfile` and `docker-compose.yml` files (dev + prod variants). Multi-platform builds for linux/amd64 and linux/arm64. Docker images available via `zie619/n8n-workflows:latest` on Docker Hub. Security features include Trivy scanning, non-root container user, CORS protection, and input validation. Security scanning artifacts (`trivy.yaml`, `.trivyignore`) are committed in the repo.

**Source evidence:** `README.md` lines 21 (Latest Updates: "Multi-platform builds for linux/amd64 and linux/arm64"), 93-99 (Docker Installation: `docker run -p 8000:8000 zie619/n8n-workflows:latest`, local build instructions), 197-204 (Security Features: "Path traversal protection", "Input validation & sanitization", "CORS protection", "Rate limiting", "Docker security hardening", "Non-root container user", "Regular security scanning"). Files confirmed: `Dockerfile`, `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.prod.yml`, `trivy.yaml`, `.trivyignore`.

## Claim-5: GitHub Pages searchable web interface with dark/light mode

A modern web interface is hosted at `zie619.github.io/n8n-workflows` via GitHub Pages. Features include smart search, 15+ categories, mobile-responsive design, direct workflow JSON downloads, and dark/light mode. The `docs/` directory contains the GitHub Pages site assets (`index.html`, `_config.yml`, `api/search-index.json`).

**Source evidence:** `README.md` lines 22-24 (Latest Updates: "GitHub Pages: Live searchable interface at zie619.github.io/n8n-workflows", "Performance: 100x faster search with SQLite FTS5 integration", "Modern UI: Completely redesigned interface with dark/light mode"). Lines 31-35 (Quick Access: "Visit zie619.github.io/n8n-workflows for instant access to: Smart Search, 15+ Categories, Mobile Ready, Direct Downloads"). Files confirmed: `docs/index.html`, `docs/_config.yml`, `docs/api/search-index.json` (version 1.0, generated 2025-11-03).

## Claim-6: Security-first design with rate limiting, CORS, and input validation

The application implements multiple security layers: rate limiting (60 requests/minute per IP using `defaultdict(list)` storage), CORS with restricted origins (localhost, GitHub Pages, Render), allowed methods restricted to GET/POST, allowed headers restricted to Content-Type and Authorization, and GZip middleware for performance.

**Source evidence:** `api_server.py` lines 33-34 (rate limiting storage `defaultdict(list)` with `MAX_REQUESTS_PER_MINUTE = 60`), lines 42-56 (CORS middleware with `allow_origins` restricted to 5 origins: localhost:3000/8000/8080, `zie619.github.io`, Render community deployment; `allow_methods=["GET", "POST"]`, `allow_headers=["Content-Type", "Authorization"]`), line 37 (GZip middleware). `README.md` lines 197-204 (Security Features enumeration). `.trivyignore`, `test_security.sh` confirmed.

## Claim-7: Integrated AI-stack and medcards-ai components

Beyond workflow collection, the repository includes additional components: `ai-stack/` for AI stack integrations, `medcards-ai/` for medical cards AI functionality, `helm/` for Kubernetes Helm chart deployment, `k8s/` for Kubernetes manifests, `context/` for context management, `src/` for Python source code, `scripts/` for utility scripts. `DELIVERY-SUMMARY.md` documents the delivered AI automation stack (n8n + Agent Zero + ComfyUI).

**Source evidence:** Root directory listing shows `ai-stack/`, `medcards-ai/`, `helm/`, `k8s/`, `context/`, `src/`, `scripts/`, `DELIVERY-SUMMARY.md`, `DEPLOYMENT.md`. `DELIVERY-SUMMARY.md` header: "# AI Automation Stack - Delivery Summary" with "Core Stack Components" section. `scripts/` confirmed: `backup.sh`, `deploy.sh`, `generate_search_index.py`, `health-check.sh`, `update_github_pages.py`, `update_readme_stats.py`.
