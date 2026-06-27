---
name: hermes-notification-relay
description: "Hermes Agent used as a multi-platform notification relay for alert forwarding"
tags: [hermes-agent, notifications, telegram, integration-patterns]
---

# Hermes Notification Relay

Hermes Agent can serve as a notification relay in deployment stacks, forwarding alerts from Mission Control to multiple platforms (Telegram, Slack, Email). It listens on port 9090 and accepts webhook payloads for routing.

See [[stack-reference-mission-control]] for the deployment pattern.
