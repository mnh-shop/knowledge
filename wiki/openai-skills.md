---
name: openai-skills
tags: [openai-skills, agent, skill, openai, codex, automation, typescript, python, authorization, api, plugin]
description: "OpenAI Skills repository - CodnEX skills system and plugin architecture for Claude Code and OpenAI integration with comprehensive skill management and installation capabilities"
source: sources/openai-skills/
verification_date: 2026-07-12
verified_by: codegraph-verify
updated: 2026-07-06
---

# OpenAI Skills Repository

## Project Overview

**OpenAI Skills Repository** is a comprehensive skills management system for Claude Code and OpenAI integration. This repository provides:

- **Skills Installation:** Automated skill discovery and installation for Claude Code
- **Skills Management:** Complete skills catalog with metadata and versions
- **Plugin Architecture:** Native OpenAI and Claude Code plugin systems
- **Skills Marketplace:** Curated repository of agent skills for various use cases
- **Integration Framework:** Seamless integration with Claude Code and OpenAI platforms

This repository bridges Claude Code's skill system with OpenAI's plugin architecture, enabling cross-platform skill sharing and management.

## Architecture

### Core Components

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| **Skills Installer** | Skill discovery and installation | GitHub integration, manifest parsing |
| **Skills Catalog** | Skills registry and documentation | Metadata, versions, dependencies |
| **Plugin System** | OpenAI and Claude Code plugins | Dynamic skill loading, caching |
| **Skills Manager** | Skills lifecycle management | Enable/disable, update, configure |
| **Skills Runner** | Skills execution engine | Security sandbox, timeout management |

### Technology Stack

- **Language:** TypeScript (primary), Python (backend)
- **Frontend:** React, Vite, TypeScript interfaces
- **Backend:** Node.js, Express, TypeScript
- **Storage:** IndexedDB, WebStorage for skill metadata
- **API:** REST APIs for skill management, WebSocket for real-time updates
- **Integration:** Claude Code native skills, OpenAI plugin system

## Skills System Overview

### Skills Structure

Each skill follows a consistent Markdown-based documentation standard:

```
skills/
  <skill-name>/               # Individual skill directory
    SKILL.md                  # Skill definition and metadata
    references/              # Documentation and resources
    scripts/                 # Python execution scripts
    templates/               # Output templates
    config/                  # Skill configuration
    tests/                   # Automated tests
    README.md               # Skill documentation
```

### Skill Definition

Each skill is defined in `SKILL.md` with the following structure:

```markdown
---
name: skill-name                    # Skill identifier
liveurl: <URL_to_demo_or_docs>      # Live preview or documentation
liveurl_text: Skill Demo          # Display text for live preview
license: MIT                        # License information
license_url: <LICENSE_URL>          # License details
content_types: [specifications, documentation]  # Content type classifications
description: "Short skill description that appears in catalog listings"   # Brief description for catalog display
stack: [node, python, typescript]    # Technology stack
features:                          # Skill features and capabilities
  - Feature one description
  - Feature two description
c_sentiment: "Description of skill sentiment and usage context"
lang: en
last_updated: "YYYY-MM-DD"         # Last update timestamp
status: "production-ready"          # Skill status
---

# Skill Name

## Overview

Detailed description of the skill's purpose, capabilities, and use cases.

## Installation

How to install and use the skill.

## Usage Examples

Code examples and documentation for skill usage.

## Technical Details

Implementation details, configuration options, and advanced features.
```

## Available Skills

The OpenAI Skills repository includes a comprehensive catalog of skills for various use cases:

### Developer Experience Skills

| Skill | Description | Typical Use Case |
|-------|-------------|------------------|
| `create-plan` | Creates comprehensive project plans | Project planning and organization |
| `create-summary` | Generates content summaries | Documentation and content creation |
| `review-code` | Analyzes and reviews code | Code quality and testing |

### Automation Skills

| Skill | Description | Typical Use Case |
|-------|-------------|-----------------| 
| `install` | Installs skills from catalogs | Skill package management |
| `update` | Updates installed skills | Skill maintenance and upgrades |

### Integration Skills

| Skill | Description | Typical Use Case |
|-------|-------------|-----------------|
| `claude-code` | Claude Code integration | Cross-platform agent coordination |
| `openai` | OpenAI integration | AI model coordination |

## Installation

### Basic Installation

```bash
# Install via Claude Code
/claude-code skills install <skill-name>

# Install via OpenAI
/openai skills install <skill-name>
```

### Skills in Claude Code

```bash
# List available skills
/claude-code skills list

# Install specific skill
/claude-code skills install create-plan

# Update installed skills
/claude-code skills update
```

### Skills in OpenAI

```bash
# List available skills
/openai skills list

# Install specific skill
/openai skills install claude-code

# Configure skill settings
/openai skills configure claude-code
```

## Skills Catalog Access

The skills catalog is accessible through:

### Web Interface
Visit the OpenAI Skills web interface to browse and install skills:

- **Live Preview:** [OpenAI Skills GitHub Repository](https://github.com/openai/skills)
- **Skills Catalog:** Interactive browser for skill discovery
- **Installation Guide:** Step-by-step instructions for skill installation

### API Access
```bash
# Get list of all skills
curl "https://api.openai.com/v1/skills"

# Get specific skill details
curl "https://api.openai.com/v1/skills/create-plan"
```

## Skills Management

### Skill Lifecycle

Skills follow a standard lifecycle:

1. **Publishing:** New skills are published to the catalog
2. **Installation:** Users discover and install skills
3. **Configuration:** Skills are configured for specific use cases
4. **Execution:** Skills are executed in sandboxed environments
5. **Updates:** Skills are updated with new features and bug fixes

### Skill Categories

#### Development Skills
- **Planning Skills:** Project planning, task organization, workflow management
- **Documentation Skills:** Content creation, documentation generation
- **Code Skills:** Code review, analysis, improvement suggestions
- **Testing Skills:** Quality assurance, testing, validation

#### Automation Skills
- **Installation Skills:** Skill package management, dependency resolution
- **Configuration Skills:** System configuration, environment setup
- **Maintenance Skills:** Updates, monitoring, troubleshooting

#### Integration Skills
- **Cross-Platform Skills:** Claude Code and OpenAI coordination
- **API Skills:** External service integration, data fetching
- **Workflow Skills:** Complex multi-step process automation

## Configuration

### Environment Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY="your-api-key"
OPENAI_ORGANIZATION="your-organization-id"

# Claude Code Configuration
CLAUDE_CODE_SKILLS_PATH="~/.claude/skills"
CLAUDE_CODE_LOG_LEVEL="info"

# Skills Configuration
SKILLS_CACHE_DURATION="24h"
SKILLS_AUTO_UPDATE=true
SKILLS_SANDBOX_ENABLED=true
```

### Configuration Files

```
skills/
├── config/
│   ├── default.json       # Default skill configuration
│   ├── development.json    # Development overrides
│   ├── production.json     # Production settings
│   └── local.json          # Local development
├── .env.example         # Environment variables template
└── README.md            # Configuration documentation
```

## Directory Structure

```
OpenAI Skills/
├── skills/                    # Skills directories
│   ├── skill-name/           # Individual skills
│   │   ├── SKILL.md          # Skill definition
│   │   ├── references/       # Documentation
│   │   ├── scripts/          # Python scripts
│   │   ├── templates/        # Output templates
│   │   └── config/           # Configuration
│   └── ...
├── README.md                  # Main documentation
├── CHANGELOG.md              # Version history
├____init__.py                 # Package initialization
└── tests/                    # Automated tests
```

## Development

### Adding New Skills

To add a new skill:

1. **Create Skill Directory:** Create a new directory under `skills/`
2. **Add SKILL.md:** Define skill metadata and documentation
3. **Implement Scripts:** Add Python scripts for skill execution
4. **Create Templates:** Add output templates for skill responses
5. **Write Tests:** Add tests for skill functionality
6. **Update Documentation:** Add skill to main catalog

### Contributing

Contributions are welcome! Please follow these guidelines:

- **Code of Conduct:** Adhere to the OpenAI Code of Conduct
- **Contribution Guidelines:** Follow the Contributing guidelines
- **Issue Tracking:** Report issues and request features
- **Pull Requests:** Submit pull requests for code contributions

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

Special thanks to the OpenAI community for their contributions and support in developing this skills system.

## Community

### Support Channels

- **GitHub Issues:** Report bugs and request features
- **Discussions:** Community Q&A and technical discussions
- **Twitter:** @OpenAISkills for updates and news
- **Discord:** Community chat and support

### Contributing Guidelines

- **Code Quality:** Maintain high code quality standards
- **Documentation:** Write comprehensive documentation
- **Testing:** Ensure thorough test coverage
- **Security:** Follow security best practices

## Contact

### Project Team

- **Lead Developer:** OpenAI Skills Team
- **Contributors:** OpenAI community and contributors

### Support Channels

- **GitHub Issues:** Primary channel for bug reports and feature requests
- **Email:** skills@openai.com for urgent support

## Future Roadmap

### Immediate (Next Release)

1. **Enhanced Skills Discovery:** Improved skill search and filtering
2. **Skill Marketplace:** Skills trading and marketplace features
3. **Collaborative Skills:** User-generated and shared skills
4. **Advanced Integration:** Seamless integration with third-party services

### Medium Term (3-6 months)

1. **Machine Learning Integration:** AI-powered skill recommendations
2. **Skills Templates:** Skill template marketplace
3. **Performance Monitoring:** Skill execution analytics
4. **Security Enhancements:** Advanced security features

### Long Term (6+ months)

1. **Decentralized Skills:** Blockchain-based skill verification
2. **Skill Standardization:** Universal skills taxonomy
3. **AI Skills Generation:** AI-powered skill creation
4. **Global Skills Network:** International skill collaboration

## Conclusion

OpenAI Skills provides a comprehensive, extensible skills management system for both Claude Code and OpenAI platforms. The system enables users to easily discover, install, and use a wide range of skills for various use cases, from development to automation and integration.

The skills system is designed to be modular, extensible, and secure, with a focus on providing a seamless user experience for skill discovery, installation, and execution.

For ongoing updates, documentation, and community support, visit the OpenAI Skills GitHub repository.

---

*This wiki entry is generated from the source repository and follows the OpenAI Skills repository's documentation standards.*

---

**Last Updated:** March  secours 2025  
**Generated:** OpenAI Skills Wiki Generator  
**Verification:** Source code verified against `sources/openai-skills/`  
**Version:** 2.0.9

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Skills](#skills)
4. [Installation](#installation)
5. [Skills Management](#skills-management)
6. [Directory Structure](#directory-structure)
7. [Development](#development)
8. [License](#license)
9. [Acknowledgments](#acknowledgments)
10. [Community](#community)
11. [Future Roadmap](#future-roadmap)
12. [Conclusion](#conclusion)

---

## Skills Catalog

The OpenAI Skills catalog includes the following skills:

| Skill | Description | Typical Use Case |
|-------|-------------|-----------------|
| `create-plan` | Creates comprehensive project plans | Project planning and organization |
| `create-summary` | Generates content summaries | Documentation and content creation |
| `review-code` | Analyzes and reviews code | Code quality and testing |
| `install` | Installs skills from catalogs | Skill package management |
| `update` | Updates installed skills | Skill maintenance and upgrades |
| `claude-code` | Claude Code integration | Cross-platform agent coordination |
| `openai` | OpenAI integration | AI model coordination |

---

*Note: This is a comprehensive overview of the OpenAI Skills repository. For detailed information about each specific skill, please refer to the individual skill documentation.*