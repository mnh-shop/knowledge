---
name: n8n-workflow-catalog
description: "Master catalog of 2,061 n8n workflows across 415 integrations and 87 trigger types"
tags: [automation, catalog, documentation, n8n, workflows]
---

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
| [[n8n-category-catalog#Manual|Manual]] | 391 | manualTrigger, scheduleTrigger, webhook |
| [[n8n-category-catalog#Http|Http]] | 176 | manualTrigger, webhook, scheduleTrigger, many integration-specific triggers |
| [[n8n-category-catalog#Webhook|Webhook]] | 65 | webhook, respondToWebhook, scheduleTrigger |
| [[n8n-category-catalog#Schedule|Schedule]] | 52 | scheduleTrigger, manualTrigger |
| [[n8n-category-catalog#Respondtowebhook|Respondtowebhook]] | 26 | respondToWebhook, webhook |
| [[n8n-category-catalog#Form|Form]] | 23 | formTrigger, respondToWebhook |
| [[n8n-category-catalog#Error|Error]] | 17 | errorTrigger, scheduleTrigger, manualTrigger |
| [[n8n-category-catalog#Cron|Cron]] | 1 | cron |

### Core n8n Nodes: Data Flow (683 workflows)

Workflows demonstrating n8n's built-in processing nodes:

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Splitout|Splitout]] | 194 | splitOut, aggregate, if, merge, code |
| [[n8n-category-catalog#Code|Code]] | 183 | code, function, if, merge, httpRequest |
| [[n8n-category-catalog#Wait|Wait]] | 104 | wait, scheduleTrigger, if, merge |
| [[n8n-category-catalog#Stickynote|Stickynote]] | 57 | stickyNote, code, gmail, webhook |
| [[n8n-category-catalog#Noop|Noop]] | 24 | noop, function, httpRequest, webhook |
| [[n8n-category-catalog#Stopanderror|Stopanderror]] | 24 | stopAndError, if, set, code |
| [[n8n-category-catalog#Filter|Filter]] | 23 | filter, if, merge, httpRequest |
| [[n8n-category-catalog#Limit|Limit]] | 22 | limit, merge, code, if |
| [[n8n-category-catalog#Datetime|Datetime]] | 18 | dateTime, cron, if, merge |
| [[n8n-category-catalog#Aggregate|Aggregate]] | 16 | aggregate, if, merge, httpRequest |
| [[n8n-category-catalog#Functionitem|Functionitem]] | 13 | functionItem, function, httpRequest |
| [[n8n-category-catalog#Comparedatasets|Comparedatasets]] | 1 | compareDatasets |
| [[n8n-category-catalog#Removeduplicates|Removeduplicates]] | 1 | removeDuplicates |
| [[n8n-category-catalog#Splitinbatches|Splitinbatches]] | 1 | splitInBatches |

### Messaging & Communication (170 workflows)

| Category | Workflows | Primary Triggers |
|---|---|---|
| [[n8n-category-catalog#Telegram|Telegram]] | 119 | telegramTrigger, manualTrigger, scheduleTrigger |
| [[n8n-category-catalog#Mattermost|Mattermost]] | 24 | webhook, typeFormTrigger, manualTrigger |
| [[n8n-category-catalog#Slack|Slack]] | 18 | webhook, slackTrigger, manualTrigger |
| [[n8n-category-catalog#Twilio|Twilio]] | 4 | twilioTrigger, typeFormTrigger |
| [[n8n-category-catalog#Discord|Discord]] | 2 | formTrigger |
| [[n8n-category-catalog#Whatsapp|Whatsapp]] | 2 | whatsappTrigger, webhook, respondToWebhook |
| [[n8n-category-catalog#Matrix|Matrix]] | 1 | cron |

### Google Services (55 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Googlesheets|Googlesheets]] | 26 | googleSheets, code, webhook, gmail |
| [[n8n-category-catalog#Googlecalendar|Googlecalendar]] | 8 | googleCalendar, gmail, webhook |
| [[n8n-category-catalog#Googledocs|Googledocs]] | 6 | googleDocs, googleDrive, gmail |
| [[n8n-category-catalog#Googleanalytics|Googleanalytics]] | 4 | googleAnalytics, code |
| [[n8n-category-catalog#Googledrive|Googledrive]] | 3 | googleDrive, googleDocs |
| [[n8n-category-catalog#Googleslides|Googleslides]] | 3 | googleSlides, hubSpot |
| [[n8n-category-catalog#Googletasks|Googletasks]] | 2 | googleTasks, gmail |
| [[n8n-category-catalog#Googlebigquery|Googlebigquery]] | 1 | googleBigQuery |
| [[n8n-category-catalog#Googlecontacts|Googlecontacts]] | 1 | googleContacts |
| [[n8n-category-catalog#Googletranslate|Googletranslate]] | 1 | googleTranslate |

### File Processing (41 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Extractfromfile|Extractfromfile]] | 21 | extractFromFile, code, gmail, formTrigger |
| [[n8n-category-catalog#Localfile|Localfile]] | 6 | localFileTrigger, code |
| [[n8n-category-catalog#Readbinaryfile|Readbinaryfile]] | 5 | readBinaryFile, postgres |
| [[n8n-category-catalog#Converttofile|Converttofile]] | 3 | convertToFile, gmail |
| [[n8n-category-catalog#Compression|Compression]]| 2 | compression, httpRequest |
| [[n8n-category-catalog#Editimage|Editimage]] | 2 | editImage, googleDrive |
| [[n8n-category-catalog#Writebinaryfile|Writebinaryfile]] | 2 | writeBinaryFile |

### Email (36 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Emailreadimap|Emailreadimap]] | 8 | emailReadImap, gmail, httpRequest |
| [[n8n-category-catalog#Gmail|Gmail]] | 8 | gmail, googleSheets, googleDrive |
| [[n8n-category-catalog#Send|Send]] | 3 | mcpClientTool |
| [[n8n-category-catalog#Emailsend|Emailsend]] | 2 | emailSend, hubspot |
| [[n8n-category-catalog#Mailchimp|Mailchimp]] | 2 | mailchimp |
| [[n8n-category-catalog#Mailjet|Mailjet]] | 2 | mailjet |
| [[n8n-category-catalog#Autopilot|Autopilot]] | 2 | autopilot |
| [[n8n-category-catalog#Activecampaign|Activecampaign]] | 1 | activeCampaign |
| [[n8n-category-catalog#Convertkit|Convertkit]]| 1 | convertKit |
| [[n8n-category-catalog#Customerio|Customerio]] | 1 | customerIo |
| [[n8n-category-catalog#Getresponse|Getresponse]] | 1 | getResponse |
| [[n8n-category-catalog#Keap|Keap]] | 1 | keap |
| [[n8n-category-catalog#Mailcheck|Mailcheck]] | 1 | mailcheck |
| [[n8n-category-catalog#Mailerlite|Mailerlite]]| 1 | mailerLite |
| [[n8n-category-catalog#Postmark|Postmark]] | 1 | postmark |
| [[n8n-category-catalog#Emelia|Emelia]] | 1 | emelia |

### Databases (32 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Postgres|Postgres]] | 12 | postgres, code, gmail |
| [[n8n-category-catalog#Airtable|Airtable]] | 4 | airtable, cron |
| [[n8n-category-catalog#Strapi|Strapi]] | 4 | strapi, code |
| [[n8n-category-catalog#Redis|Redis]] | 3 | redis, code |
| [[n8n-category-catalog#Supabase|Supabase]] | 3 | supabase |
| [[n8n-category-catalog#Graphql|Graphql]] | 2 | graphql, cron |
| [[n8n-category-catalog#Baserow|Baserow]] | 1 | baserow |
| [[n8n-category-catalog#Elasticsearch|Elasticsearch]] | 1 | elasticSearch |
| [[n8n-category-catalog#Grist|Grist]] | 1 | grist |
| [[n8n-category-catalog#Nocodb|Nocodb]] | 1 | nocoDb |

### AI Tools / MCP (32 workflows)

n8n's AI Agent tool nodes for natural-language-driven automation:

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Gmailtool|Gmailtool]] | 6 | gmailTool, mcpClientTool |
| [[n8n-category-catalog#Googlecalendartool|Googlecalendartool]] | 5 | googleCalendarTool |
| [[n8n-category-catalog#Postgrestool|Postgrestool]] | 5 | postgresTool |
| [[n8n-category-catalog#Airtabletool|Airtabletool]] | 2 | airtableTool |
| [[n8n-category-catalog#Discordtool|Discordtool]] | 2 | discordTool |
| [[n8n-category-catalog#Jiratool|Jiratool]] | 2 | jiraTool |
| [[n8n-category-catalog#Mongodbtool|Mongodbtool]] | 2 | mongoDbTool |
| [[n8n-category-catalog#Mysqltool|Mysqltool]] | 2 | mySqlTool |
| [[n8n-category-catalog#Airtoptool|Airtoptool]] | 1 | airtopTool |
| [[n8n-category-catalog#Googledrivetool|Googledrivetool]] | 1 | googleDriveTool |
| [[n8n-category-catalog#Googlesheetstool|Googlesheetstool]] | 1 | googleSheetsTool |
| [[n8n-category-catalog#Googletaskstool|Googletaskstool]] | 1 | googleTasksTool |
| [[n8n-category-catalog#Telegramtool|Telegramtool]] | 1 | telegramTool |
| [[n8n-category-catalog#Twittertool|Twittertool]] | 1 | twitterTool |

### CRM (28 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Mautic|Mautic]] | 8 | mautic, gmail, webhook |
| [[n8n-category-catalog#Hubspot|Hubspot]] | 7 | hubspot, httpRequest, gmail |
| [[n8n-category-catalog#Zendesk|Zendesk]] | 6 | zendesk, code |
| [[n8n-category-catalog#Pipedrive|Pipedrive]] | 3 | pipedrive |
| [[n8n-category-catalog#Odoo|Odoo]] | 2 | odoo |
| [[n8n-category-catalog#Copper|Copper]] | 1 | copper |
| [[n8n-category-catalog#Zohocrm|Zohocrm]] | 1 | zohoCrm |

### DevOps & Monitoring (22 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Github|Github]] | 9 | github, cron, slack |
| [[n8n-category-catalog#Gitlab|Gitlab]] | 4 | gitlab, code |
| [[n8n-category-catalog#Netlify|Netlify]] | 3 | netlify, slack |
| [[n8n-category-catalog#Bitbucket|Bitbucket]] | 1 | bitbucket |
| [[n8n-category-catalog#Onfleet|Onfleet]] | 1 | onfleet |
| [[n8n-category-catalog#Posthog|Posthog]] | 1 | posthog |
| [[n8n-category-catalog#Signl4|Signl4]] | 1 | signl4 |
| [[n8n-category-catalog#Travisci|Travisci]] | 1 | travisCi |
| [[n8n-category-catalog#Uptimerobot|Uptimerobot]] | 1 | uptimeRobot |

### Productivity & Project Management (21 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Trello|Trello]] | 5 | trello, code |
| [[n8n-category-catalog#Mondaycom|Mondaycom]] | 4 | mondayCom, code |
| [[n8n-category-catalog#Asana|Asana]] | 3 | asana |
| [[n8n-category-catalog#Clickup|Clickup]] | 3 | clickUp |
| [[n8n-category-catalog#Notion|Notion]] | 3 | notion |
| [[n8n-category-catalog#Jira|Jira]] | 2 | jira |
| [[n8n-category-catalog#Todoist|Todoist]] | 1 | todoist |

### Social Media (19 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Linkedin|Linkedin]] | 13 | linkedIn, gmail, twitter |
| [[n8n-category-catalog#Twitter|Twitter]] | 3 | twitter, cron |
| [[n8n-category-catalog#Facebook|Facebook]]| 1 | facebook |
| [[n8n-category-catalog#Facebookleadads|Facebookleadads]] | 1 | facebookLeadAds |
| [[n8n-category-catalog#Youtube|Youtube]] | 1 | youtube |

### E-Commerce (19 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Shopify|Shopify]] | 10 | shopify, code |
| [[n8n-category-catalog#Woocommerce|Woocommerce]] | 3 | woocommerce |
| [[n8n-category-catalog#Quickbooks|Quickbooks]] | 2 | quickbooks |
| [[n8n-category-catalog#Chargebee|Chargebee]] | 1 | chargebee |
| [[n8n-category-catalog#Gumroad|Gumroad]] | 1 | gumroad |
| [[n8n-category-catalog#Invoiceninja|Invoiceninja]] | 1 | invoiceNinja |
| [[n8n-category-catalog#Paypal|Paypal]] | 1 | paypal |

### AI & LLM (15 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Openai|Openai]] | 8 | openAi, googleSheets, telegram |
| [[n8n-category-catalog#Summarize|Summarize]] | 3 | summarize, code |
| [[n8n-category-catalog#Deep|Deep]] | 2 | openai, code, notion |
| [[n8n-category-catalog#Cortex|Cortex]] | 1 | cortex |
| [[n8n-category-catalog#Humanticai|Humanticai]] | 1 | humanticAi |

### Forms & Scheduling (15 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Calendly|Calendly]] | 7 | calendlyTrigger, hubspot |
| [[n8n-category-catalog#Typeform|Typeform]] | 4 | typeformTrigger, airtable |
| [[n8n-category-catalog#Acuityscheduling|Acuityscheduling]] | 1 | acuityScheduling |
| [[n8n-category-catalog#Jotform|Jotform]] | 1 | jotform |
| [[n8n-category-catalog#Surveymonkey|Surveymonkey]] | 1 | surveyMonkey |
| [[n8n-category-catalog#Wufoo|Wufoo]] | 1 | wufoo |

### Content & Formatting (10 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Rssfeedread|Rssfeedread]] | 6 | rssFeedRead, cron, telegram |
| [[n8n-category-catalog#Markdown|Markdown]] | 3 | markdown, email |
| [[n8n-category-catalog#Xml|Xml]] | 1 | xml |

### Microsoft Services (7 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Microsoftoutlook|Microsoftoutlook]] | 4 | microsoftOutlook |
| [[n8n-category-catalog#Microsoftexcel|Microsoftexcel]] | 1 | microsoftExcel |
| [[n8n-category-catalog#Microsoftonedrive|Microsoftonedrive]] | 1 | microsoftOneDrive |
| [[n8n-category-catalog#Microsofttodo|Microsofttodo]] | 1 | microsoftToDo |

### AWS Services (6 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Awss3|Awss3]] | 3 | awsS3 |
| [[n8n-category-catalog#Awsrekognition|Awsrekognition]] | 1 | awsRekognition |
| [[n8n-category-catalog#Awssns|Awssns]] | 1 | awsSns |
| [[n8n-category-catalog#Awstextract|Awstextract]] | 1 | awsTextract |

### Infrastructure (2 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Amqp|Amqp]] | 1 | amqp |
| [[n8n-category-catalog#Mqtt|Mqtt]] | 1 | mqtt |

### Local Execution (5 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| [[n8n-category-catalog#Executecommand|Executecommand]] | 5 | executeCommand, function |

### Other / Uncategorized (92 workflows)

| Category | Workflows |
|---|---|
| [[n8n-category-catalog#Openweathermap|Openweathermap]] | 13 |
| [[n8n-category-catalog#Executeworkflow|Executeworkflow]] | 9 |
| [[n8n-category-catalog#Automation|Automation]] | 6 |
| [[n8n-category-catalog#Automate|Automate]] | 5 |
| [[n8n-category-catalog#Hunter|Hunter]] | 5 |
| [[n8n-category-catalog#Wordpress|Wordpress]] | 5 |
| [[n8n-category-catalog#Templates|Templates]] | 4 |
| [[n8n-category-catalog#Lemlist|Lemlist]] | 3 |
| [[n8n-category-catalog#Clockify|Clockify]] | 3 |
| [[n8n-category-catalog#Readbinaryfiles|Readbinaryfiles]] | 3 |
| [[n8n-category-catalog#Bannerbear|Bannerbear]] | 2 |
| [[n8n-category-catalog#Crypto|Crypto]] | 2 |
| [[n8n-category-catalog#Wise|Wise]] | 2 |
| [[n8n-category-catalog#Woocommercetool|Woocommercetool]] | 2 |
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
Each category directory in `sources/n8n-workflows/workflows/` maps to an integration or node type. The section headers above link to [[n8n-category-catalog#wikilinks|wikilinks]] that describe each category's role and patterns.

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
