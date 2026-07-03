---
name: awesome-n8n-templates
description: "Curated collection of 280+ free ready-to-import n8n workflow templates across 18 categories"
source: sources/awesome-n8n-templates/
tags: [fair-code, git, integration, messaging, n8n, n8n-workflows, security, storage, templates, workflow-automation, reference, awesome-n8n-templates]
---

# awesome-n8n-templates

A curated collection of 280+ free, ready-to-import [[n8n]] workflow templates, maintained by [enescingoz](https://github.com/enescingoz/awesome-n8n-templates). This is the largest open-source repository of n8n automation templates on GitHub, continuously updated as of March 2026.

## Description

The repository serves as a comprehensive template library for the [[n8n]] workflow automation platform, providing pre-built solutions for common automation scenarios. Each template is a JSON file that can be directly imported into n8n, requiring only credential configuration for the connected services before activation. The collection spans 18 distinct categories covering email automation, messaging platforms, productivity tools, AI/LLM integrations, social media, DevOps, databases, and more.

## Key Features

- **280+ ready-to-import templates** across 18 categories of automation use cases
- **Multi-language support** with localized READMEs in 13 languages including English, Turkish, Chinese, German, French, Spanish, Japanese, Korean, Hindi, Arabic, Indonesian, Russian, and Italian
- **AI-native templates** featuring OpenAI, Anthropic Claude, Google Gemini, DeepSeek R1, Mistral AI, Ollama, LangChain, and Perplexity integrations
- **Production-ready workflows** for Gmail/Outlook email automation, Telegram/Discord/Slack bots, social media management, and data processing pipelines
- **Security-focused automations** including phishing detection, suspicious email analysis, and toxic language detection in messaging platforms
- **Database and vector store integrations** with PostgreSQL, MongoDB, Supabase, Pinecone, Qdrant, and Elasticsearch support
- **Human-in-the-loop workflows** enabling human review and approval before automated actions
- **Content creation and processing** for PDFs, documents, social media posts, and recipe delivery
- **Zero-cost starting point** - all templates work with n8n's free tier or self-hosted instances

## Categories

The repository organizes templates into the following categories:

- **Communication & Email**: Gmail, Outlook, IMAP automation with AI-powered labeling and categorization
- **Messaging**: Telegram, Slack, Discord, WhatsApp, LINE with chatbot and moderation capabilities
- **Office & Productivity**: Google Drive, Google Sheets, Notion, Obsidian, Todoist integration
- **Content Management**: WordPress, Confluence, Strapi publishing workflows
- **CRM & Sales**: Airtable, HubSpot, Pipedrive, Bitrix24 lead management
- **AI & LLMs**: OpenAI, Anthropic Claude, Gemini, DeepSeek R1, Mistral, Ollama, LangChain, Perplexity, Hugging Face
- **Databases & Vector Stores**: PostgreSQL, MongoDB, SQLite, Supabase, Pinecone, Qdrant, Elasticsearch
- **Social Media**: Instagram, Twitter/X, Reddit, YouTube, LinkedIn, Pinterest, TikTok
- **DevOps & Security**: SSH, Docker Compose, Qualys, SIEM enrichment, Venafi, phishing detection

## Usage

To use any template:

1. [[n8n]] instance (cloud or self-hosted)
2. Download the desired `.json` template file
3. In n8n, navigate to **Workflows → Import from File**
4. Select the downloaded JSON file
5. Configure credentials for each connected service
6. Activate the workflow and begin automation

## Statistics

- **280+ automation templates** across 18 categories
- **19,000+ GitHub stars** from the automation community
- **Platforms covered**: Gmail, Telegram, Google Drive, WordPress, Discord, Slack, Notion, Airtable, WhatsApp, Instagram, Twitter/X, and dozens more
- **Last commit**: Regularly updated with new templates and platform support

## Popular Use Cases

Email automation templates include AI-powered labeling and categorization of incoming Gmail messages, phishing detection with ChatGPT Vision analysis, automatic reply drafting for common queries, and inbox summarization delivered via Telegram. These are ideal for operations teams looking to reduce manual email triage and for security teams needing automated threat detection.

Messaging automations cover AI chatbots with long-term memory via Supabase, voice-to-text translation across 55 languages, PDF chat functionality where users can upload documents and ask questions, Spotify integration for music requests, and toxic language detection for content moderation. Telegram bots range from simple GPT wrappers to agentic assistants with dynamic tool routing.

Content and document processing templates enable chat-with-PDF functionality, automated WordPress posting, Google Sheets to email campaign workflows, recipe delivery bots, and social media post scheduling. Lead generation workflows combine Google Sheets lead lists with AI-powered cold email writing, while RAG pipelines connect vector stores with LLM providers for knowledge base queries.

## Source

- [[n8n-workflows]] — n8n workflow catalog and template collections
- [[n8n]] — Core n8n automation platform

- **Source path**: `/Users/admin1/Documents/knowledge/sources/awesome-n8n-templates`
- **Repository**: [enescingoz/awesome-n8n-templates](https://github.com/enescingoz/awesome-n8n-templates)
- **License**: CC BY 4.0