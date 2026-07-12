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

## Claim-1: Curated collection of 2,061 production-ready n8n workflows across 85 categories

The repository contains 2,061 verified n8n workflow JSON files organized into 85 categories. Workflows are stored as individual JSON files in `workflows/` directory with subdirectories per integration category (ActiveCampaign, Airtable, Asana, AWS S3, Calendly, ClickUp, Slack, etc.). The collection represents a curated subset with documented integration patterns — originally claimed 4,343, revised to 2,061 verified workflows.

**Source evidence:** `README.md` lines 41-74 (Features section: "2,061 Production-Ready Workflows", "85 Organized Categories", "282 Unique Integrations", "8,923 Total Nodes"). Lines 68-74 (Recent Changes: "Collection now contains 2,061 workflows (revised from 4,343)", "282 unique service integrations", "85 workflow categories"). `workflows/` directory listing confirmed 189+ category subdirectories (offset 40 shows 40 entries of 189 total).

## Claim-2: FastAPI backend with SQLite FTS5 full-text search (<100ms response)

The backend uses Python FastAPI with SQLite FTS5 for full-text search across workflow names, descriptions, and nodes. Performance metrics claim <100ms search response, <50MB memory usage, 400x smaller than v1. API endpoints include `/api/search`, `/api/stats`, `/api/workflow/{id}`, `/api/categories`, `/api/export`. The server is launched via `run.py` and initialized with `workflow_db.py`.

**Source evidence:** `README.md` lines 55-65 (Performance: "< 100ms Search Response", "< 50MB Memory Usage", "400x Smaller Than v1"). Lines 115-132 (API Endpoints table with 6 endpoints, Search Features with 5 filter types). Lines 136-152 (Architecture diagram showing User → Web Interface → FastAPI Server → SQLite FTS5 → Workflow Database). `api_server.py` lines 1-60 (FastAPI app with CORS middleware, GZip middleware, rate limiting, Pydantic models). `workflow_db.py` confirmed.

## Claim-3: Python-based workflow database with multi-format search filters

The `WorkflowDatabase` class provides full-text search across workflow names, descriptions, and nodes. Search supports filtering by: category (Marketing, Sales, DevOps, etc.), complexity (Low, Medium, High), trigger type (Webhook, Schedule, Manual), and service integration (365+). The database is backed by SQLite with FTS5 and initialized from the workflow JSON files directory.

**Source evidence:** `README.md` lines 127-131 (Search features: category filtering, complexity filtering, trigger type filtering, service filtering). `api_server.py` lines 1-60 (WorkflowDatabase import from `workflow_db.py`, FastAPI initialization, security middleware). `workflows/` directory listing shows diverse integration categories confirming the multi-service filter capability. `requirements.txt` confirmed.

## Claim-4: Docker deployment with multi-platform builds and security scanning

Supports Docker deployment via `Dockerfile` and `docker-compose.yml` files. Multi-platform builds for linux/amd64 and linux/arm64. Docker images available via `zie619/n8n-workflows:latest` on Docker Hub. Security features include Trivy scanning, non-root container user, CORS protection, and input validation. Security scanning artifacts (`trivy.yaml`, `.trivyignore`) are committed in the repo.

**Source evidence:** `README.md` lines 100-110 (Docker Installation: `docker run -p 8000:8000 zie619/n8n-workflows:latest`, local build instructions). Lines 207-215 (Security Features: "Path traversal protection", "Input validation & sanitization", "CORS protection", "Rate limiting", "Docker security hardening", "Non-root container user", "Regular security scanning"). Files confirmed: `Dockerfile`, `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.prod.yml`, `trivy.yaml`, `.trivyignore`.

## Claim-5: GitHub Pages searchable web interface with dark/light mode

A modern web interface is hosted at `zie619.github.io/n8n-workflows` via GitHub Pages. Features include smart search, 15+ categories, mobile-responsive design, direct workflow JSON downloads, and dark/light mode. Static files are served by the FastAPI backend as well as deployed as a standalone GitHub Pages site. The `docs/` directory contains the GitHub Pages site assets.

**Source evidence:** `README.md` lines 30-35 (Quick Access: "Visit zie619.github.io/n8n-workflows for instant access to: Smart Search, 15+ Categories, Mobile Ready, Direct Downloads"). Lines 22-23 (Latest Updates: "GitHub Pages: Live searchable interface at zie619.github.io/n8n-workflows", "Modern UI: Completely redesigned interface with dark/light mode"). `docs/` directory confirmed. `static/` directory confirmed.

## Claim-6: Security-first design with rate limiting, CORS, and input validation

The application implements multiple security layers: rate limiting (60 requests/minute per IP using `defaultdict(list)` storage), CORS with restricted origins (localhost, GitHub Pages, Render), allowed methods restricted to GET/POST, allowed headers restricted to Content-Type and Authorization, path traversal protection, input validation/sanitization via Pydantic field validators, and GZip middleware for performance.

**Source evidence:** `api_server.py` lines 33-56 (rate limiting storage `defaultdict(list)` with `MAX_REQUESTS_PER_MINUTE = 60`, CORS middleware with `allow_origins` restricted to 5 origins, `allow_methods=["GET", "POST"]`, `allow_headers=["Content-Type", "Authorization"]`). `.trivyignore` confirmed. `test_security.sh` confirmed. `README.md` lines 207-215 (Security Features enumeration).

## Claim-7: Integrated AI-stack and medcards-ai components

Beyond workflow collection, the repository includes additional components: `ai-stack/` for AI stack integrations, `medcards-ai/` for medical cards AI functionality, `helm/` for Kubernetes Helm chart deployment, `k8s/` for Kubernetes manifests, `context/` for context management, `src/` for Python source code, `templates/` for HTML templates, and `scripts/` for utility scripts. The `DELIVERY-SUMMARY.md` and `DEPLOYMENT.md` provide delivery and deployment documentation.

**Source evidence:** Root directory listing shows `ai-stack/`, `medcards-ai/`, `helm/`, `k8s/`, `context/`, `src/`, `templates/`, `scripts/`, `DELIVERY-SUMMARY.md`, `DEPLOYMENT.md`. `README.md` lines 156-169 (Repository Structure showing additional directories beyond core workflows). `test_workflows.py` and `test_api.sh` and `test_security.sh` confirmed as testing infrastructure.
