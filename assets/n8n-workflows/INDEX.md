# n8n Workflow Catalog

Tags: [n8n, workflow-patterns, automation]

## Overview

[n8n](https://n8n.io/) is a fair-code, extensible workflow automation tool that connects services via a visual node-based interface. This catalog indexes **2,061 workflow JSON definitions** drawn from the [n8n-workflows community collection](https://github.com/zie619/n8n-workflows), organized into 188 category subdirectories.

The workflows are stored at `sources/n8n-workflows/workflows/` in this repo. Each JSON file captures a complete automation graph: trigger nodes, action nodes (integrations), data-transformation nodes, and error-handling patterns.

### Why this matters for knowledge

These workflows are a dense corpus of "how people wire services together" -- integration patterns, trigger setups, data-flow topologies, and error-handling strategies across hundreds of real-world services. They serve as:

- A reference for common integration patterns (webhook -> transform -> store, schedule -> fetch -> notify, etc.)
- A training corpus for understanding service interconnection schemas
- A catalog of node-type usage frequency across the n8n ecosystem

---

## Stats

| Metric | Value |
|---|---|
| Total workflows | **2,061** |
| Category directories | **188** |
| Unique integrations (node types) | **415** |
| Unique trigger types | **87** |
| Average nodes per workflow | **14.9** |
| Top node: stickynote | 1,327 workflows |
| Top trigger: manualTrigger | 927 workflows |
| Top webhook trigger: webhook | 313 workflows |

---

## Top Categories by Workflow Count

The 188 category directories span trigger types, core n8n nodes, and external service integrations. Below are the largest groups, organized by domain.

### Trigger & Flow Control (751 workflows)

Directories focused on how workflows start, respond, and route:

| Category | Workflows | Primary Triggers |
|---|---|---|
| [[Manual]] | 391 | manualTrigger, scheduleTrigger, webhook |
| [[Http]] | 176 | manualTrigger, webhook, scheduleTrigger, many integration-specific triggers |
| [[Webhook]] | 65 | webhook, respondToWebhook, scheduleTrigger |
| [[Schedule]] | 52 | scheduleTrigger, manualTrigger |
| [[Respondtowebhook]] | 26 | respondToWebhook, webhook |
| [[Form]] | 23 | formTrigger, respondToWebhook |
| [[Error]] | 17 | errorTrigger, scheduleTrigger, manualTrigger |
| [[Cron]] | 1 | cron |

### Core n8n Nodes: Data Flow (683 workflows)

Workflows demonstrating n8n's built-in processing nodes:

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Splitout]] | 194 | splitOut, aggregate, if, merge, code |
| [[Code]] | 183 | code, function, if, merge, httpRequest |
| [[Wait]] | 104 | wait, scheduleTrigger, if, merge |
| [[Stickynote]] | 57 | stickyNote, code, gmail, webhook |
| [[Noop]] | 24 | noop, function, httpRequest, webhook |
| [[Stopanderror]] | 24 | stopAndError, if, set, code |
| [[Filter]] | 23 | filter, if, merge, httpRequest |
| [[Limit]] | 22 | limit, merge, code, if |
| [[Datetime]] | 18 | dateTime, cron, if, merge |
| [[Aggregate]] | 16 | aggregate, if, merge, httpRequest |
| [[Functionitem]] | 13 | functionItem, function, httpRequest |
| [[Comparedatasets]] | 1 | compareDatasets |
| [[Removeduplicates]] | 1 | removeDuplicates |
| [[Splitinbatches]] | 1 | splitInBatches |

### Messaging & Communication (170 workflows)

| Category | Workflows | Primary Triggers |
|---|---|---|
| [[Telegram]] | 119 | telegramTrigger, manualTrigger, scheduleTrigger |
| [[Mattermost]] | 24 | webhook, typeFormTrigger, manualTrigger |
| [[Slack]] | 18 | webhook, slackTrigger, manualTrigger |
| [[Twilio]] | 4 | twilioTrigger, typeFormTrigger |
| [[Discord]] | 2 | formTrigger |
| [[Whatsapp]] | 2 | whatsappTrigger, webhook, respondToWebhook |
| [[Matrix]] | 1 | cron |

### Google Services (55 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Googlesheets]] | 26 | googleSheets, code, webhook, gmail |
| [[Googlecalendar]] | 8 | googleCalendar, gmail, webhook |
| [[Googledocs]] | 6 | googleDocs, googleDrive, gmail |
| [[Googleanalytics]] | 4 | googleAnalytics, code |
| [[Googledrive]] | 3 | googleDrive, googleDocs |
| [[Googleslides]] | 3 | googleSlides, hubSpot |
| [[Googletasks]] | 2 | googleTasks, gmail |
| [[Googlebigquery]] | 1 | googleBigQuery |
| [[Googlecontacts]] | 1 | googleContacts |
| [[Googletranslate]] | 1 | googleTranslate |

### File Processing (41 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Extractfromfile]] | 21 | extractFromFile, code, gmail, formTrigger |
| [[Localfile]] | 6 | localFileTrigger, code |
| [[Readbinaryfile]] | 5 | readBinaryFile, postgres |
| [[Converttofile]] | 3 | convertToFile, gmail |
| [[Compression]]| 2 | compression, httpRequest |
| [[Editimage]] | 2 | editImage, googleDrive |
| [[Writebinaryfile]] | 2 | writeBinaryFile |

### Email (36 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Emailreadimap]] | 8 | emailReadImap, gmail, httpRequest |
| [[Gmail]] | 8 | gmail, googleSheets, googleDrive |
| [[Send]] | 3 | mcpClientTool |
| [[Emailsend]] | 2 | emailSend, hubspot |
| [[Mailchimp]] | 2 | mailchimp |
| [[Mailjet]] | 2 | mailjet |
| [[Autopilot]] | 2 | autopilot |
| [[Activecampaign]] | 1 | activeCampaign |
| [[Convertkit]]| 1 | convertKit |
| [[Customerio]] | 1 | customerIo |
| [[Getresponse]] | 1 | getResponse |
| [[Keap]] | 1 | keap |
| [[Mailcheck]] | 1 | mailcheck |
| [[Mailerlite]]| 1 | mailerLite |
| [[Postmark]] | 1 | postmark |
| [[Emelia]] | 1 | emelia |

### Databases (32 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Postgres]] | 12 | postgres, code, gmail |
| [[Airtable]] | 4 | airtable, cron |
| [[Strapi]] | 4 | strapi, code |
| [[Redis]] | 3 | redis, code |
| [[Supabase]] | 3 | supabase |
| [[Graphql]] | 2 | graphql, cron |
| [[Baserow]] | 1 | baserow |
| [[Elasticsearch]] | 1 | elasticSearch |
| [[Grist]] | 1 | grist |
| [[Nocodb]] | 1 | nocoDb |

### AI Tools / MCP (32 workflows)

n8n's AI Agent tool nodes for natural-language-driven automation:

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Gmailtool]] | 6 | gmailTool, mcpClientTool |
| [[Googlecalendartool]] | 5 | googleCalendarTool |
| [[Postgrestool]] | 5 | postgresTool |
| [[Airtabletool]] | 2 | airtableTool |
| [[Discordtool]] | 2 | discordTool |
| [[Jiratool]] | 2 | jiraTool |
| [[Mongodbtool]] | 2 | mongoDbTool |
| [[Mysqltool]] | 2 | mySqlTool |
| [[Airtoptool]] | 1 | airtopTool |
| [[Googledrivetool]] | 1 | googleDriveTool |
| [[Googlesheetstool]] | 1 | googleSheetsTool |
| [[Googletaskstool]] | 1 | googleTasksTool |
| [[Telegramtool]] | 1 | telegramTool |
| [[Twittertool]] | 1 | twitterTool |

### CRM (28 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Mautic]] | 8 | mautic, gmail, webhook |
| [[Hubspot]] | 7 | hubspot, httpRequest, gmail |
| [[Zendesk]] | 6 | zendesk, code |
| [[Pipedrive]] | 3 | pipedrive |
| [[Odoo]] | 2 | odoo |
| [[Copper]] | 1 | copper |
| [[Zohocrm]] | 1 | zohoCrm |

### DevOps & Monitoring (22 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Github]] | 9 | github, cron, slack |
| [[Gitlab]] | 4 | gitlab, code |
| [[Netlify]] | 3 | netlify, slack |
| [[Bitbucket]] | 1 | bitbucket |
| [[Onfleet]] | 1 | onfleet |
| [[Posthog]] | 1 | posthog |
| [[Signl4]] | 1 | signl4 |
| [[Travisci]] | 1 | travisCi |
| [[Uptimerobot]] | 1 | uptimeRobot |

### Productivity & Project Management (21 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Trello]] | 5 | trello, code |
| [[Mondaycom]] | 4 | mondayCom, code |
| [[Asana]] | 3 | asana |
| [[Clickup]] | 3 | clickUp |
| [[Notion]] | 3 | notion |
| [[Jira]] | 2 | jira |
| [[Todoist]] | 1 | todoist |

### Social Media (19 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Linkedin]] | 13 | linkedIn, gmail, twitter |
| [[Twitter]] | 3 | twitter, cron |
| [[Facebook]]| 1 | facebook |
| [[Facebookleadads]] | 1 | facebookLeadAds |
| [[Youtube]] | 1 | youtube |

### E-Commerce (19 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Shopify]] | 10 | shopify, code |
| [[Woocommerce]] | 3 | woocommerce |
| [[Quickbooks]] | 2 | quickbooks |
| [[Chargebee]] | 1 | chargebee |
| [[Gumroad]] | 1 | gumroad |
| [[Invoiceninja]] | 1 | invoiceNinja |
| [[Paypal]] | 1 | paypal |

### AI & LLM (15 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Openai]] | 8 | openAi, googleSheets, telegram |
| [[Summarize]] | 3 | summarize, code |
| [[Deep]] | 2 | openai, code, notion |
| [[Cortex]] | 1 | cortex |
| [[Humanticai]] | 1 | humanticAi |

### Forms & Scheduling (15 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Calendly]] | 7 | calendlyTrigger, hubspot |
| [[Typeform]] | 4 | typeformTrigger, airtable |
| [[Acuityscheduling]] | 1 | acuityScheduling |
| [[Jotform]] | 1 | jotform |
| [[Surveymonkey]] | 1 | surveyMonkey |
| [[Wufoo]] | 1 | wufoo |

### Content & Formatting (10 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Rssfeedread]] | 6 | rssFeedRead, cron, telegram |
| [[Markdown]] | 3 | markdown, email |
| [[Xml]] | 1 | xml |

### Microsoft Services (7 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Microsoftoutlook]] | 4 | microsoftOutlook |
| [[Microsoftexcel]] | 1 | microsoftExcel |
| [[Microsoftonedrive]] | 1 | microsoftOneDrive |
| [[Microsofttodo]] | 1 | microsoftToDo |

### AWS Services (6 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Awss3]] | 3 | awsS3 |
| [[Awsrekognition]] | 1 | awsRekognition |
| [[Awssns]] | 1 | awsSns |
| [[Awstextract]] | 1 | awsTextract |

### Infrastructure (2 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Amqp]] | 1 | amqp |
| [[Mqtt]] | 1 | mqtt |

### Local Execution (5 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[Executecommand]] | 5 | executeCommand, function |

### Other / Uncategorized (92 workflows)

| Category | Workflows |
|---|---|
| [[Openweathermap]] | 13 |
| [[Executeworkflow]] | 9 |
| [[Automation]] | 6 |
| [[Automate]] | 5 |
| [[Hunter]] | 5 |
| [[Wordpress]] | 5 |
| [[Templates]] | 4 |
| [[Lemlist]] | 3 |
| [[Clockify]] | 3 |
| [[Readbinaryfiles]] | 3 |
| [[Bannerbear]] | 2 |
| [[Crypto]] | 2 |
| [[Wise]] | 2 |
| [[Woocommercetool]] | 2 |
| And 18 more single-workflow categories | 1 each |

---

## Trigger Type Reference

The 87 trigger types found across all workflows, grouped by frequency:

**High volume (100+ workflows):**
- `manualTrigger` - 927 workflows
- `webhook` - 313 workflows
- `scheduleTrigger` - 311 workflows
- `executeWorkflowTrigger` - 180 workflows
- `respondToWebhook` - 161 workflows
- `formTrigger` - 114 workflows
- `telegramTrigger` - 94 workflows

**Medium volume (10-99):**
- `gmailTrigger` (53), `googleDriveTrigger` (40), `typeformTrigger` (24), `googleSheetsTrigger` (21), `errorTrigger` (18), `notionTrigger` (13), `airtableTrigger` (11), `githubTrigger` (11), `shopifyTrigger` (11), `calendlyTrigger` (10)

**Long tail (1-9):** 62 additional triggers covering every major service integration.

---

## How to Use This Catalog

### Browsing
Each category directory in `sources/n8n-workflows/workflows/` maps to an integration or node type. The section headers above link to [[wikilinks]] that describe each category's role and patterns.

### Searching for patterns
To find all workflows that use a specific integration, search the workflow JSON files for the node type string (e.g., `n8n-nodes-base.telegram` or `@n8n/n8n-nodes-langchain.openAi`).

### Common workflow topologies
1. **Webhook -> Transform -> Deliver**: An external service sends data via webhook, n8n transforms it (Set/Code), then delivers to a target (Slack, email, database).
2. **Schedule -> Fetch -> Notify**: A cron-based trigger polls an API (HTTP Request), processes results, and pushes notifications (Telegram, Slack, email).
3. **Form -> Store -> Respond**: A form submission triggers a workflow that stores data in Airtable/Google Sheets and sends a confirmation.
4. **Email Trigger -> Classify -> Route**: Incoming email triggers the workflow, an AI node classifies intent, and a Switch node routes to different handlers.
5. **AI Agent -> Tool -> Action**: A LangChain/openAi node uses tool sub-nodes (Gmail, Calendar, Database) to execute natural-language-driven automations.

### File naming convention
Workflow filenames follow the pattern `[ID]_[Description]_[TriggerType].json` -- e.g., `9001_Scalable_Webhook_Orchestrator_Webhook.json`. The ID is a sequential number; the trigger type suffix indicates the primary trigger.

---

## See Also

- [[integrations/README|Integration Sub-Index]]
- [[sources/n8n-workflows/README|Source Repository README]]
