# Integrations Sub-Index

This directory catalogs the **415 unique node types** (integrations) used across the 2,061 n8n workflow files.

Each integration is indexed in the master catalog at [[../INDEX|n8n Workflow Catalog INDEX]].

## Structure

The workflows are organized by **category directory** in `sources/n8n-workflows/workflows/`, where each directory name reflects the primary service or node type that the workflow demonstrates. Many workflows reference multiple integrations -- the category directory is the *organizational focus*, not an exhaustive list.

## Top Integrations by Workflow Count

These are the most frequently occurring node types (across all workflows):

| Node Type | Workflows Using It | Domain |
|---|---|---|
| stickyNote | 1,327 | Notes & Documentation |
| stopAndError | 1,083 | Data Flow Control |
| set | 1,069 | Data Transformation |
| noOp | 937 | Data Flow Control |
| manualTrigger | 927 | Trigger |
| httpRequest | 895 | Web & HTTP |
| if | 660 | Data Flow Control |
| code | 516 | Data Transformation |
| merge | 340 | Data Flow Control |
| webhook | 313 | Trigger |
| scheduleTrigger | 311 | Trigger |
| splitOut | 295 | Data Flow Control |
| googleSheets | 281 | Google Services |
| switch | 234 | Data Flow Control |
| splitInBatches | 224 | Data Flow Control |
| filter | 195 | Data Flow Control |
| executeWorkflowTrigger | 180 | Trigger |
| telegram | 176 | Messaging |
| aggregate | 173 | Data Flow Control |
| gmail | 168 | Email |

## Integration Domains

The 415 node types span these broad domains:

| Domain | Example Node Types | Approx Count |
|---|---|---|
| Data Flow & Transformation | `set`, `code`, `if`, `merge`, `filter`, `switch` | ~30 |
| Triggers | `manualTrigger`, `webhook`, `scheduleTrigger`, `formTrigger` | ~87 |
| Email | `gmail`, `emailSend`, `emailReadImap`, `mailchimp` | ~20 |
| Messaging | `telegram`, `slack`, `discord`, `mattermost`, `twilio` | ~15 |
| Google Services | `googleSheets`, `googleDrive`, `googleCalendar`, `googleDocs` | ~15 |
| Databases | `postgres`, `mysql`, `airtable`, `redis`, `mongodb`, `supabase` | ~25 |
| Storage & Files | `extractFromFile`, `convertToFile`, `readBinaryFile`, `s3` | ~15 |
| CRM | `hubspot`, `pipedrive`, `zendesk`, `salesforce` | ~15 |
| Social Media | `twitter`, `linkedIn`, `youtube`, `facebook` | ~10 |
| E-Commerce | `shopify`, `woocommerce`, `stripe`, `paypal` | ~10 |
| DevOps | `github`, `gitlab`, `netlify`, `posthog` | ~10 |
| AI / LLM | `openAi`, `n8n`, `summarize`, `langChain` | ~15 |
| AI Tools (MCP) | `gmailTool`, `googleCalendarTool`, `postgresTool` | ~15 |
| Infrastructure | `mqtt`, `amqp`, `redis`, `elasticsearch` | ~10 |
| Forms & Scheduling | `typeform`, `calendly`, `formTrigger` | ~10 |
| Content | `rssFeedRead`, `html`, `markdown`, `xml` | ~10 |
| Miscellaneous | `crypto`, `cron`, `bitly`, `coingecko`, `clockify` | ~100+ |

## Trigger Integrations

N8n workflows are event-driven. The trigger nodes that start them include:

- **Manual**: `manualTrigger` -- user-invoked, often used for testing
- **Webhook**: `webhook` -- receive HTTP POST from any service
- **Schedule**: `scheduleTrigger` -- cron-based intervals
- **Service-specific**: one trigger type per integration (e.g., `gmailTrigger`, `telegramTrigger`, `githubTrigger`, `shopifyTrigger`, `typeformTrigger`, `calendlyTrigger`, etc.)
- **Error**: `errorTrigger` -- fires when another workflow errors
- **Form**: `formTrigger` -- renders a form for user input
- **Workflow**: `executeWorkflowTrigger` -- called by another n8n workflow

For the complete list, see the [[../INDEX#Trigger-Type-Reference|Trigger Type Reference]] in the master index.

---

## About This Sub-Index

No per-integration files are generated due to the scale (415 integrations). Use the master INDEX.md for navigation. To trace a specific integration across workflows, search the JSON files in `sources/n8n-workflows/workflows/` for the node type string pattern (e.g., `n8n-nodes-base.gmail` or `@n8n/n8n-nodes-langchain.openAi`).
