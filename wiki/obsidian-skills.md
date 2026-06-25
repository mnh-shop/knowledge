---
title: Obsidian Skills
parent: project-based-wiki
published: true
description: Agent skills for use with Obsidian - a collection of specialized skills following the Agent Skills specification
---

# Obsidian Skills

A comprehensive collection of agent skills designed specifically for use with Obsidian vaults, following the [Agent Skills specification](https://agentskills.io/specification) to ensure compatibility across different skill-compatible platforms including Claude Code, Codex, and OpenCode.

## Overview

The Obsidian Skills project provides a modular set of specialized skills that enable AI agents to work effectively with Obsidian-specific file formats and vault operations. Each skill is self-contained and follows the standard skill format for easy integration and discovery.

## Core Skills

### [obsidian-markdown](skills/obsidian-markdown)
Creates and edits [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown) (`.md`) files with full support for wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax.

### [obsidian-bases](skills/obsidian-bases)  
Creates and edits [Obsidian Bases](https://help.obsidian.md/bases/syntax) (`.base`) files containing views, filters, formulas, and summaries.

### [json-canvas](skills/json-canvas)
Creates and edits [JSON Canvas](https://jsoncanvas.org/) files (`.canvas`) with support for nodes, edges, groups, and connections.

### [obsidian-cli](skills/obsidian-cli)
Interact with Obsidian vaults via the [Obsidian CLI](https://help.obsidian.md/cli) including capabilities for plugin and theme development.

### [defuddle](skills/defuddle)
Extracts clean markdown from web pages using [Defuddle](https://github.com/kepano/defuddle), removing clutter to save tokens and improve content quality.

## Installation Methods

### 1. Marketplace Installation (Recommended)
```
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```

### 2. npx skills (For CLI-based installation)
```
npx skills add git@github.com:kepano/obsidian-skills.git
```

Alternatively with HTTPS:
```
npx skills add https://github.com/kepano/obsidian-skills
```

### 3. Manual Installation

#### For Claude Code
Add the entire repo contents to a `/.claude` folder in the root of your Obsidian vault. See the [official Claude Skills documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for details.

#### For Codex
Copy the `skills/` directory into your Codex skills path (typically `~/.codex/skills`). Follow the [Agent Skills specification](https://agentskills.io/specification) for the standard skill format.

#### For OpenCode
Clone the full repository into the OpenCode skills directory:
```sh
git clone https://github.com/kepano/obsidian-skills.git ~/.opencode/skills/obsidian-skills
```

**Important**: Clone the entire repo to maintain the correct directory structure `~/.opencode/skills/obsidian-skills/skills/<skill-name>/SKILL.md`. OpenCode automatically discovers all SKILL.md files and loads them after restart.

## Supported Platforms

- **Claude Code**: Native skill integration via `.claude` folder
- **Codex**: Standard skill directory integration
- **OpenCode**: Automatic discovery of skills via directory structure

## References

Each skill includes documentation and reference materials:

- obsidian-markdown references: [CALLOUTS.md](skills/obsidian-markdown/references/CALLOUTS.md), [EMBEDS.md](skills/obsidian-markdown/references/EMBEDS.md), [PROPERTIES.md](skills/obsidian-markdown/references/PROPERTIES.md)
- obsidian-bases references: [FUNCTIONS_REFERENCE.md](skills/obsidian-bases/references/FUNCTIONS_REFERENCE.md)
- json-canvas references: [EXAMPLES.md](skills/json-canvas/references/EXAMPLES.md)

## Purpose

The Obsidian Skills project enables AI agents to work seamlessly with Obsidian vaults by providing specialized capabilities for:

- Working with Obsidian's native file formats (MD, BASE, CANVAS)
- Performing vault operations via CLI
- Extracting and processing web content for Obsidian use
- Leveraging Obsidian-specific features like wikilinks, embeds, and metadata

This collection serves as a foundation for building Obsidian-native workflows and automating content creation and management tasks within the Obsidian ecosystem.