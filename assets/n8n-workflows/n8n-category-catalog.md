---
name: n8n-category-catalog
tags: [n8n, catalog, documentation, automation, workflows]
description: "Catalog of all 188 n8n workflow category directories referenced in the INDEX"
---

# n8n Category Catalog

This page catalogs all **188 category directories** in `sources/n8n-workflows/workflows/`. Each category corresponds to a subdirectory containing workflow JSON files that demonstrate the named node type or integration pattern.

## Trigger & Flow Control (751 workflows)

| Category | Workflows | Primary Triggers |
|---|---|---|
| Manual | 391 | manualTrigger, scheduleTrigger, webhook |
| Http | 176 | manualTrigger, webhook, scheduleTrigger |
| Webhook | 65 | webhook, respondToWebhook, scheduleTrigger |
| Schedule | 52 | scheduleTrigger, manualTrigger |
| Respondtowebhook | 26 | respondToWebhook, webhook |
| Form | 23 | formTrigger, respondToWebhook |
| Error | 17 | errorTrigger, scheduleTrigger, manualTrigger |
| Cron | 1 | cron |

## Core n8n Nodes: Data Flow (683 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| Splitout | 194 | splitOut, aggregate, if, merge, code |
| Code | 183 | code, function, if, merge, httpRequest |
| Wait | 104 | wait, scheduleTrigger, if, merge |
| Stickynote | 57 | stickyNote, code, gmail, webhook |
| Noop | 24 | noop, function, httpRequest, webhook |
| Stopanderror | 24 | stopAndError, if, set, code |
| Filter | 23 | filter, if, merge, httpRequest |
| Limit | 22 | limit, merge, code, if |
| Datetime | 18 | dateTime, cron, if, merge |
| Aggregate | 16 | aggregate, if, merge, httpRequest |
| Functionitem | 13 | functionItem, function, httpRequest |
| Comparedatasets | 1 | compareDatasets |
| Removeduplicates | 1 | removeDuplicates |
| Splitinbatches | 1 | splitInBatches |

## Messaging & Communication (170 workflows)

| Category | Workflows | Primary Triggers |
|---|---|---|
| Telegram | 119 | telegramTrigger, manualTrigger, scheduleTrigger |
| Mattermost | 24 | webhook, typeFormTrigger, manualTrigger |
| Slack | 18 | webhook, slackTrigger, manualTrigger |
| Twilio | 4 | twilioTrigger, typeFormTrigger |
| Discord | 2 | formTrigger |
| Whatsapp | 2 | whatsappTrigger, webhook, respondToWebhook |
| Matrix | 1 | cron |

## Google Services (55 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| Googlesheets | 26 | googleSheets, code, webhook, gmail |
| Googlecalendar | 8 | googleCalendar, gmail, webhook |
| Googledocs | 6 | googleDocs, googleDrive, gmail |
| Googleanalytics | 4 | googleAnalytics, code |
| Googledrive | 3 | googleDrive, googleDocs |
| Googleslides | 3 | googleSlides, hubSpot |
| Googletasks | 2 | googleTasks, gmail |
| Googlebigquery | 1 | googleBigQuery |
| Googlecontacts | 1 | googleContacts |
| Googletranslate | 1 | googleTranslate |

## File Processing (41 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| Extractfromfile | 21 | extractFromFile, code, gmail, formTrigger |
| Localfile | 6 | localFileTrigger, code |
| Readbinaryfile | 5 | readBinaryFile, postgres |
| Converttofile | 3 | convertToFile, gmail |
| Compression | 2 | compression, httpRequest |
| Editimage | 2 | editImage, googleDrive |
| Writebinaryfile | 2 | writeBinaryFile |

## Email (36 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| Emailreadimap | 8 | emailReadImap, gmail, httpRequest |
| Gmail | 8 | gmail, googleSheets, googleDrive |
| Send | 3 | mcpClientTool |
| Emailsend | 2 | emailSend, hubspot |
| Mailchimp | 2 | mailchimp |
| Mailjet | 2 | mailjet |
| Autopilot | 2 | autopilot |
| Activecampaign | 1 | activeCampaign |
| Convertkit | 1 | convertKit |
| Customerio | 1 | customerIo |
| Getresponse | 1 | getResponse |
| Keap | 1 | keap |
| Mailcheck | 1 | mailcheck |
| Mailerlite | 1 | mailerLite |
| Postmark | 1 | postmark |
| Emelia | 1 | emelia |

## Databases (32 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| Postgres | 12 | postgres, code, gmail |
| Airtable | 4 | airtable, cron |
| Strapi | 4 | strapi, code |
| Redis | 3 | redis, code |
| Supabase | 3 | supabase |
| Graphql | 2 | graphql, cron |
| Baserow | 1 | baserow |
| Elasticsearch | 1 | elasticSearch |
| Grist | 1 | grist |
| Nocodb | 1 | nocoDb |

## AI Tools / MCP (32 workflows)

| Category | Workflows | Key Nodes |
|---|---|---|
| Gmailtool | 6 | gmailTool, mcpClientTool |
| Googlecalendartool | 5 | googleCalendarTool |
| Postgrestool | 5 | postgresTool |
| Airtabletool | 2 | airtableTool |
| Discordtool | 2 | discordTool |
| Jiratool | 2 | jiraTool |
| Mongodbtool | 2 | mongoDbTool |
| Mysqltool | 2 | mySqlTool |
| Airtoptool | 1 | airtopTool |
| Googledrivetool | 1 | googleDriveTool |
| Googlesheetstool | 1 | googleSheetsTool |
| Googletaskstool | 1 | googleTasksTool |
| Telegramtool | 1 | telegramTool |
| Twittertool | 1 | twitterTool |

## CRM (28 workflows)

Hubspot, Zendesk, Mautic, Pipedrive, Odoo, Copper, Zohocrm

## DevOps & Monitoring (22 workflows)

Github, Gitlab, Netlify, Bitbucket, Onfleet, Posthog, Signl4, Travisci, Uptimerobot

## Productivity & Project Management (21 workflows)

Trello, Mondaycom, Asana, Clickup, Notion, Jira, Todoist

## Social Media (19 workflows)

Linkedin, Twitter, Facebook, Facebookleadads, Youtube

## E-Commerce (19 workflows)

Shopify, Woocommerce, Quickbooks, Chargebee, Gumroad, Invoiceninja, Paypal

## AI & LLM (15 workflows)

Openai, Summarize, Deep, Cortex, Humanticai

## Forms & Scheduling (15 workflows)

Calendly, Typeform, Acuityscheduling, Jotform, Surveymonkey, Wufoo

## Content & Formatting (10 workflows)

Rssfeedread, Markdown, Xml

## Microsoft Services (7 workflows)

Microsoftoutlook, Microsoftexcel, Microsoftonedrive, Microsofttodo

## AWS Services (6 workflows)

Awss3, Awsrekognition, Awssns, Awstextract

## Infrastructure (2 workflows)

Amqp, Mqtt

## Local Execution (5 workflows)

Executecommand

## Other / Uncategorized (92 workflows)

Openweathermap, Executeworkflow, Automation, Automate, Hunter, Wordpress, Templates, Lemlist, Clockify, Readbinaryfiles, Bannerbear, Crypto, Wise, Woocommercetool, and 18 more single-workflow categories

## Trigger Type Reference

The **87 trigger types** across all workflows:

**High volume (100+):** manualTrigger (927), webhook (313), scheduleTrigger (311), executeWorkflowTrigger (180), respondToWebhook (161), formTrigger (114), telegramTrigger (94)

**Medium (10-99):** gmailTrigger (53), googleDriveTrigger (40), typeformTrigger (24), googleSheetsTrigger (21), errorTrigger (18), notionTrigger (13), airtableTrigger (11), githubTrigger (11), shopifyTrigger (11), calendlyTrigger (10)

**Long tail (1-9):** 62 additional integration-specific triggers

---

*This catalog mirrors the structure in the master [[INDEX|n8n Workflow Catalog INDEX]]. For detailed workflow examples, browse the `sources/n8n-workflows/workflows/` directories.*
