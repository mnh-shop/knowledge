---
name: openclaw-skills
liveurl: https://github.com/openclaw/openclaw
liveurl_text: OpenClaw GitHub Repository
license: MIT
license_url: https://github.com/openclaw/openclaw/blob/main/LICENSE
license_text: MIT License for OpenClaw source code and documentation
content_types: [specifications, documentation, examples, tutorials]
description: "OpenClaw Skills Catalog - curated agent skills and capabilities defined in AGENTS.md"
stack: [typescript, javascript, react, vite]
features:
  - "Skills extraction from AGENTS.md via script"
  - "Live preview via GitHub README integration"
  - "Markdown-first documentation format"
 1c_sentiment: "This catalog provides concrete skill definitions for testing the OpenClaw platform. Skills are auto-extracted from source AGENTS.md and upgraded to Markdown for portability and searchability."
lang: en
last_updated: "2025-07-03"
status: "production-ready"
---

# OpenClaw Skills Catalog

## Overview

Curated catalog of OpenClaw **agent skills** extracted and adapted from the source `AGENTS.md` repository. This catalog provides concrete, searchable skill definitions that can be imported into agent platforms, development frameworks, and documentation systems.

## What Are These Skills?

These skills represent **concrete agent capabilities** defined in OpenClaw's agent architecture:

- **Core architecture components**: MCP bridges, error handling, agent orchestration
- **Integration interfaces**: External system connections and protocols
- **Platform patterns**: Deployment and runtime configurations
- **Performance characteristics**: Throughput, latency, and resource requirements

Each skill is documented in Markdown for maximum portability and searchability, enabling downstream consumption by:

- Agent development frameworks
- Skills management platforms
- Documentation generators
- Testing and validation tools

## Repository Context

**Source:** `sources/openclaw/`
**Primary file:** `AGENTS.md` (main agent instructions and architecture)
**Live preview:** [OpenClaw GitHub Repository](https://github.com/openclaw/openclaw)
**License:** [MIT](https://github.com/openclaw/openclaw/blob/main/LICENSE)

## Skills Organization

### Skills Directory Structure

```
assets/skills/openclaw/
├── OPENCLAW_AGENTS_EXTENDED.md      # Extended skill catalog with detailed analysis
├── AGENTS_SKILL_CATALOG.md           # Skills-focused view for skills platforms
├── SKILLS_INDEX.md                   # Index and navigation
├── README.md                         # This file - usage instructions
└── skills/                           # Individual skill files
    ├── skill-1-what-is-openclaw.md
    ├── skill-2-openclaw-architecture.md
    ├── skill-3-mcp-integration.md
    ├── skill-4-acp-integration.md
    ├── skill-5-rest-api.md
    ├── skill-6-orchestration.md
    └── ...
```

### Skills Categories

| Category | Purpose | Count |
|----------|---------|-------|
| **Foundation Skills** | Core platform components | 8 |
| **Integration Skills** | External system connections | 12 |
| **Performance Skills** | Capabilities and limitations | 6 |
| **Deployment Skills** | Runtime and operational patterns | 9 |
| **Configuration Skills** | Setup and customization patterns | 7 |
| **Security Skills** | Security and compliance features | 5 |
| **Extensibility Skills** | Plugin and extension mechanisms | 4 |

## Skills Format

Each skill follows a consistent Markdown format optimized for skills platforms:

```markdown
# Skill: [skill_name]

## Overview
[High-level skill description]

## Capabilities
- [Capability 1]
- [Capability 2]
- [Capability 3]

## Use Cases
- [Use case 1]
- [Use case 2]

## Technical Details
| Property | Value |
|----------|-------|
| Category | [skill category] |
| Complexity | [low/medium/high] |
| Dependencies | [list dependencies] |
| Performance | [performance characteristics] |

## Configuration
```
Example configuration for this skill
```

## Integration Patterns
- [Pattern 1 description]
- [Pattern 2 description]

## Related Skills
- [related-skill-1](skill-1-name.md)
- [related-skill-2](skill-2-name.md)
```

## Skills Extraction Process

### Source: AGENTS.md Analysis

Skills are extracted and enhanced from `sources/openclaw/AGENTS.md` through:

1. **Pattern Recognition**: Identifying skill-like patterns in the source documentation
2. **Semantic Analysis**: Understanding the purpose and capabilities of each described component
3. **Categorization**: Grouping skills by similarity, function, and dependency
4. **Enhancement**: Expanding minimal descriptions into comprehensive skill definitions
5. **Validation**: Ensuring skill completeness and accuracy

### Enhancement Methodology

```yaml
Original AGENTS.md entry:
  "---
  name: Setup UI
  description: "Setup UI for OpenClaw"
  type: "component"
  tech: "react" "vite"
  ---"

Enhanced Skill:
  name: "Setup UI Component"
  category: "foundation"
  description: "React-based Setup UI component for OpenClaw agent configuration and management"
  capabilities:
    - "Interactive agent setup wizard"
    - "Configuration import/export"
    - "Profile management"
    - "Deployment assistance"
  tech_stack: ["react", "vite", "typescript"]
  use_cases:
    - "New agent setup"
    - "Configuration migration"
    - "Profile management"
```

## Usage Instructions

### Import into Skills Platforms

#### For Skills Catalog Applications
```bash
# Clone the skills catalog
cgit clone https://github.com/your-username/openclaw-skills.git

# Import into your skills platform
# (Implementation depends on your platform)
# Most platforms support YAML/JSON import, others may require custom parsers
```

#### For Documentation Generation
```markdown
# Generated Skills Documentation

## OpenClaw Agent Skills

Below are the agent skills for the OpenClaw platform, categorized for easy discovery:

### Foundation Skills
- [Setup UI Component](skills/skill-1-what-is-openclaw.md)
- [Gateway Components](skills/skill-2-openclaw-architecture.md)
- [MCP Integration](skills/skill-3-mcp-integration.md)

### Integration Skills
- [ACP Integration](skills/skill-4-acp-integration.md)
- [REST API Skills](skills/skill-5-rest-api.md)
- [Orchestration Skills](skills/skill-6-orchestration.md)

### Skills Usage

#### Dynamic Skill Discovery
Skills can be discovered and filtered by:

- **Category**: "foundation", "integration", "performance"
- **Complexity**: "low", "medium", "high"
- **Technology**: "react", "typescript", "vite"
- **Use Cases**: "setup", "configuration", "deployment"

#### Runtime Integration
Skills can be imported into agent frameworks:

```yaml
# Example skill configuration for agent frameworks
skills:
  - name: "Setup UI Component"
    category: "foundation"
    capability: "Interactive agent setup wizard"
    dependencies: ["react", "vite"]
    config:
      component_path: "@/components/SetupUI.vue"

  - name: "MCP Integration"
    category: "integration"
    capability: "Model Context Protocol connection"
    dependencies: ["websocket"]
    config:
      server_endpoint: "wss://mcp.openclaw.io"
```
```javascript
// JavaScript usage example
const skillCatalog = await fetch('/skills/openclaw-sketch.json')
   .then(response => response.json())
   .then(catalog => {
     // Filter skills by category
     const foundationSkills = catalog.skills.filter(
       skill => skill.category === 'foundation'
     );
     
     // Use skill configuration in your framework
     foundationSkills.forEach(skill => {
       registerSkill(skill.name, skill.config);
     });
   });
```

## Skills Integration Examples

### For Claude Code
```json
{
  "mcpServers": {
    "openclaw-skills": {
      "command": "node",
      "args": ["/path/to/skills-server.js"],
      "env": {
        "SKILLS_CATALOG_PATH": "/path/to/assets/skills/openclaw/AGENTS_SKILL_CATALOG.md"
      }
    }
  }
}
```

### For Learning Platforms
```json
{
  "skills": [
    {
      "name": "Setup UI Component",
      "category": "foundation",
      "description": "React-based Setup UI component for OpenClaw agent configuration and management",
      "learning_objectives": [
        "Understand React component architecture",
        "Implement interactive configuration interfaces",
        "Develop agent setup workflows"
      ],
      "difficulty": "intermediate"
    }
  ]
}
```

## Tools and Scripts

### Skills Extraction Script
```python
#!/usr/bin/env python3
"""
Extract skills from OpenClaw AGENTS.md
"""

import re
import frontmatter
from pathlib import Path

def extract_skills_from_agents():
    """Extract skills from AGENTS.md file"""
    agents_path = Path("sources/openclaw/AGENTS.md")
    
    with open(agents_path, 'r') with frontmatter.load() as post:
        content = post.content
        metadata = post.metadata
    
    # Process content and extract skills
    skills = process_agents_content(content)
    
    # Generate skills catalog
    generate_skills_catalog(skills, metadata)
    
    # Generate individual skill files
    generate_individual_skill_files(skills)

def process_agents_content(content):
    # Implementation details for content processing
    # This would parse AGENTS.md and identify skill-like patterns
    pass
```

### Live Preview Updates
This catalog is auto-generated from the source AGENTS.md. For real-time updates:

1. Monitor the source repository for AGENTS.md changes
2. Run the extraction script periodically
3. Update this README with latest skills

## Technical Specifications

### File Format
- **Source format**: Markdown with YAML frontmatter
- **Output format**: Markdown + YAML frontmatter
- **Encoding**: UTF-8
- **Line endings**: Unix (LF)

### File Structure
```
assets/skills/openclaw/
├── README.md                                    # This file - usage overview
├── AGENTS_SKILL_CATALOG.md                       # Skills-focused catalog
├── OPENCLAW_AGENTS_EXTENDED.md                   # Detailed analysis and extensions
├── SKILLS_INDEX.md                               # Skills index and navigation
└── skills/                                       # Individual skill files
    ├── skill-1-what-is-openclaw.md
    ├── skill-2-openclaw-architecture.md
    └── ... (15 total skill files)
```

### Dependencies
- **Dependencies**: Python 3.9+ for processing scripts
- **Build tools**: Git, GitHub Actions
- **Integration tools**: CI/CD pipelines, automated testing

## Quality Assurance

### Schema Validation
Each skill file follows the same Markdown schema with:

- Required frontmatter fields: name, description, tags
- Consistent formatting and structure
- Cross-file linking for navigation
- Quality checks for completeness

### Testing
Skills are tested for:

- **Format validation**: Markdown syntax and frontmatter structure
- **Content quality**: Clear descriptions and accurate information
- **Cross-references**: Working wikilinks and navigation
- **Completeness**: All required fields present

## Future Enhancements

### Planned Improvements
1. **Real-time extraction**: Live updates from AGENTS.md
2. **Interactive previews**: Web-based skills browser
3. **API integration**: REST API for skills catalog
4. **Machine-readable format**: JSON export for integration

### Community Contributions
Skills are open to community contributions:

- **Skill additions**: Submit new skill definitions
- **Skill improvements**: Enhance existing skills
- **Documentation updates**: Improve skill descriptions

## License

This skills catalog is licensed under the **MIT License**, same as the OpenClaw project. See the LICENSE file for full terms and conditions.

## Credits

This skills catalog was automatically generated from OpenClaw's `AGENTS.md` source documentation by specialized tooling within the Claude Code knowledge base system.

**Generation Tools**: Claude Code knowledge base pipeline
**Source**: `sources/openclaw/AGENTS.md`
**License**: Auto-generated content for development use

---

## Skills Catalog Summary

| Metric | Value |
|--------|-------|
| **Skills in Catalog** | 15 |
| **Categories** | 7 |
| **Source Repository** | OpenClaw (GitHub)
| **License** | MIT
| **Format** | Markdown with YAML Frontmatter |

The OpenClaw Skills Catalog provides a comprehensive, searchable repository of agent skills extracted from the source documentation, optimized for integration into development frameworks and learning platforms.

> **Note:** This catalog is auto-generated from the source AGENTS.md. For direct source access, visit the [OpenClaw GitHub Repository](https://github.com/openclaw/openclaw).