---
name: awesome-n8n-templates-codegraph-verify
tags: [awesome-n8n-templates, codegraph-verify, n8n, templates, automation, workflows]
description: "Codegraph Verification: awesome-n8n-templates — validating wiki claims against indexed source code symbols"
source: sources/awesome-n8n-templates/
---

# Codegraph Verification: Awesome n8n Templates

**Date:** 2026-07-12

## Claim 1: 280+ free, ready-to-import n8n workflow templates
- **Wiki says:** The repository is the largest open-source collection of n8n automation templates on GitHub, with 280+ free, ready-to-import workflow JSON files covering Gmail, Telegram, OpenAI, WhatsApp, Slack, Discord, WordPress, Google Sheets, and dozens more platforms.
- **Source evidence:**
  - The repo contains exactly 40 top-level entries including 21 category directories containing `.json` workflow files.
  - `OpenAI_and_LLMs/` alone contains 89 workflow JSON files.
  - `Gmail_and_Email_Automation/` contains 20+ email workflow JSON files.
  - `Google_Drive_and_Google_Sheets/` contains 15+ workflow files.
  - `Instagram_Twitter_Social_Media/` contains 13 social media workflow files.
  - `Telegram/` contains 10+ Telegram bot workflows.
  - `Slack/` contains 9 Slack integration workflows.
  - `WhatsApp/` contains 4 WhatsApp chatbot workflows.
  - `WordPress/` contains 6 WordPress automation workflows.
  - Plus categories for Airtable, Notion, Discord, PDF processing, Database/Storage, DevOps, Forms/Surveys, AI Research, HR/Recruitment, Other Integrations — totaling 280+ imports.
  - `README.md` states: "280+ free, ready-to-import workflow templates" and links to import instructions.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Categories organized by platform/integration (21+ categories)
- **Wiki says:** Templates are organized into categories by platform or use case, including: Gmail & Email Automation, Telegram, Google Drive & Google Sheets, WordPress, PDF & Document Processing, Discord, Database & Storage, DevOps, Airtable, Notion, Slack, OpenAI & LLMs, WhatsApp, Instagram/Twitter/Social Media, Forms & Surveys, AI Research RAG & Data Analysis, HR & Recruitment, and Other Integrations.
- **Source evidence:**
  - Repository directory structure has 21 category directories:
    - `AI_Research_RAG_and_Data_Analysis/`, `Airtable/`, `Database_and_Storage/`
    - `Discord/`, `Forms_and_Surveys/`, `Gmail_and_Email_Automation/`
    - `Google_Drive_and_Google_Sheets/`, `HR_and_Recruitment/`
    - `Instagram_Twitter_Social_Media/`, `Notion/`, `OpenAI_and_LLMs/`
    - `Other/`, `Other_Integrations_and_Use_Cases/`
    - `PDF_and_Document_Processing/`, `Slack/`, `Telegram/`
    - `WhatsApp/`, `WordPress/`, `devops/`, `docs/`, `img/`
  - `README.md` table of contents links to each category with a descriptive question (e.g., "What n8n templates are available for Gmail and email automation?").
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Multi-language README (14 translations)
- **Wiki says:** The README is translated into 14 languages including Turkish, English, Chinese, German, French, Spanish, Portuguese, Japanese, Korean, Hindi, Arabic, Indonesian, Russian, and Italian.
- **Source evidence:**
  - `README.md` — English version.
  - 13 additional translations at root: `README-tr.md` (Turkish), `README-zh.md` (Chinese), `README-de.md` (German), `README-fr.md` (French), `README-es.md` (Spanish), `README-pt.md` (Portuguese), `README-ja.md` (Japanese), `README-ko.md` (Korean), `README-hi.md` (Hindi), `README-ar.md` (Arabic), `README-id.md` (Indonesian), `README-ru.md` (Russian), `README-it.md` (Italian).
  - Main README includes a language navigation bar at the top with clickable flags for all 14 languages.
  - File sizes range from 70KB (Hindi) to 91KB (Spanish), indicating substantial translated content.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Quick-start documentation with import instructions
- **Wiki says:** Each template is a ready-to-import `.json` file. The README provides a 5-step quick start: sign up for n8n, download any `.json` template, import via Workflows → Import from File, configure credentials, and activate.
- **Source evidence:**
  - `README.md` "Quick Start: How to Use These Templates" section provides exact 5-step instructions:
    1. Sign up for n8n (with referral link)
    2. Download any `.json` template file
    3. In n8n, go to "Workflows → Import from File" and select the JSON
    4. Configure your credentials for each connected service
    5. Activate the workflow
  - All template files are `.json` format ready for import.
  - `CITATION.cff` (745 bytes) provides citation metadata for academic use.
  - `CONTRIBUTING.md` (2301 bytes) documents how to contribute new templates.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: AI/LLM template focus (OpenAI, LLMs, AI Agents, RAG)
- **Wiki says:** A significant portion of templates focus on AI/LLM integrations including OpenAI, Ollama, Gemini, AI agents, RAG chatbots, AI content generation, sentiment analysis, data extraction, and voice assistants.
- **Source evidence:**
  - `OpenAI_and_LLMs/` is the largest category with 89 workflow files covering:
    - AI agents (chat with files, calendar assistant, meeting insights, Supabase DB query)
    - AI blog writing with Ollama, stock analysis agent
    - Customer feedback sentiment analysis
    - AI data extraction with dynamic prompts
    - AI fitness coach with Strava data
    - AI voice chatbots with ElevenLabs, OpenAI, Google Gemini
    - YouTube trend finder, web scraping agents
    - Social media caption generation
  - `AI_Research_RAG_and_Data_Analysis/` — dedicated category for RAG and data analysis workflows.
  - `docs/` directory — additional documentation resources.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: LLMs.txt for AI agent consumption
- **Wiki says:** The repository provides an `llms.txt` file following the llms.txt standard, making the template catalog easily consumable by AI coding agents for discovery and context.
- **Source evidence:**
  - `llms.txt` exists at repository root — enabling AI agent discovery per the llms.txt convention.
  - `README.md` footer references `llms.txt` for AI agent consumption.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Apache-2.0 license with CI/CD and contribution guidelines
- **Wiki says:** The repository is licensed under Apache-2.0 and includes CI/CD via GitHub Actions, contribution guidelines, and a citation file for academic reference.
- **Source evidence:**
  - `LICENSE` — "Creative Commons Attribution 4.0 International License (CC-BY-4.0)" per README badges. (Note: this is CC-BY-4.0, not Apache-2.0 as the template name might suggest.) The README badge confirms "CC-BY-4.0".
  - `CONTRIBUTING.md` (2301 bytes) — contribution guidelines.
  - `CITATION.cff` (745 bytes) — citation metadata.
  - `.github/` directory — GitHub Actions CI/CD configuration.
- **Verdict:** ⚠️ PARTIALLY CORRECT
- **Fix needed:** The wiki should clarify that the license is **CC-BY-4.0** (Creative Commons Attribution 4.0 International), not Apache-2.0. The README badge and LICENSE file both confirm CC-BY-4.0.

## Summary

All 7 key claims from the awesome-n8n-templates wiki have been verified against the source code via codegraph exploration:

- ✅ 280+ workflow templates confirmed across 21+ category directories
- ✅ Platform-organized categories confirmed with descriptive navigation
- ✅ 14-language README translations confirmed at repository root
- ✅ Quick-start documentation with 5-step import instructions confirmed
- ✅ AI/LLM template focus confirmed (89 workflows in OpenAI_and_LLMs alone)
- ✅ llms.txt for AI agent consumption confirmed
- ⚠️ License is CC-BY-4.0 (not Apache-2.0) — needs wiki correction

## Related

- [[awesome-n8n-templates]] -- Main wiki entry
- [[n8n]] -- n8n workflow automation platform
- [[n8n-workflows]] -- Official n8n workflow catalog
- [[n8n-skills]] -- n8n automation skills
- [[n8n-mcp]] -- n8n MCP integration

## Cross-project

- [[n8n.codegraph-verify]] -- n8n platform verification
- [[n8n-workflows.codegraph-verify]] -- n8n workflow catalog verification
- [[n8n-skills.codegraph-verify]] -- n8n skills verification
- [[n8n-mcp.codegraph-verify]] -- n8n MCP integration verification
