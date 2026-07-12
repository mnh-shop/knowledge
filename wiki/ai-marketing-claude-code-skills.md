---
name: ai-marketing-claude-code-skills
tags: [ai-marketing-claude-code-skills, agent, skill, marketing, ai-llm, automation, cli, typescript, python, authorization]
description: "AI marketing agent skills for Claude Code: automated marketing workflows, content generation, lead nurturing, and campaign optimization"
source: sources/ai-marketing-claude-code-skills/
updated: 2026-07-06
---

# AI Marketing Claude Code Skills

**AI Marketing Claude Code Skills** is a comprehensive suite of agent skills for Claude Code that automates marketing workflows, content generation, and campaign optimization. Built around the SKILL_MODE pattern, this repository provides specialized skills for marketing teams and AI practitioners.

## What it is

AI Marketing Claude Code Skills transforms Claude Code into a powerful marketing automation platform. Instead of manually crafting marketing campaigns, creating content, or analyzing data, users simply describe what they want to achieve and the skills handle the entire workflow.

Key capabilities include:
- **Content Creation:** Automated writing of articles, social media posts, emails, and marketing copy
- **Campaign Management:** End-to-end marketing funnel automation from lead generation to conversion
- **Data Analysis:** Real-time insights from marketing performance, sentiment analysis, and competitive intelligence
- **Audience Targeting:** Personalized messaging based on user segments, behaviors, and preferences
- **Skill Orchestration:** Complex multi-step workflows with parallel execution and error handling

## Architecture

### Core Components

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| **SKILL_MODE Pattern** | Three-tier execution (quick/standard/deep) | Adaptive performance based on context |
| **Agent Skills** | Specialized marketing instructions | 23 free + 10 pro skills |
| **Workflow Engine** | Complex multi-step execution | Parallel processing, error recovery |
| **Data Integration** | Real-time insights & analytics | Web data, social signals, competitive intel |
| **Auth System** | Secure access management | API keys, OAuth, role-based permissions |

### Available Skill Categories

#### Strategy & Planning
- **Positioning Basics** – Value proposition and differentiation framework
- **Marketing Principles** – Growth hacking and conversion optimization
- **Marketing Framework** – AIA framework with 4 Cs

#### Content Creation
- **Cold Outreach** – Personalized 4-touch sequences
- **Content Idea Generator** – Trending topics and pillar creation
- **Homepage Audit** – Conversion optimization analysis
- **Testimonial Collector** – Social proof generation

#### Social Media & Community
- **LinkedIn Authority Builder** – Follower growth and engagement
- **LinkedIn Profile Optimizer** – Personal branding enhancement
- **Reddit Insights** – Community sentiment and trends
- **Last30Days** – Monthly performance analysis
- **Social Card Gen** – Visual content creation

#### Analytics & Optimization
- **AI Discoverability Audit** – Google visibility and AI search optimization
- **Marketing Principles** – Data-driven marketing frameworks
- **Homepage Audit** – Conversion optimization analysis

### Technology Stack

- **Language:** TypeScript (primary), Python (backend)
- **Framework:** Claude Code skill architecture
- **Storage:** SQLite for skill state and user data
- **APIs:** OpenAI, Google APIs, web scraping, social media platforms
- **Deployment:** Claude Code native skill system

## How It Works

### Skill Discovery
When you interact with Claude Code, skills are automatically discovered based on:

1. **Context Analysis** – Identifying topic domains (marketing, social, content, etc.)
2. **Intent Detection** – Recognizing what type of marketing task you're performing
3. **Skill Matching** – Selecting the most appropriate skill for the situation
4. **Mode Detection** – Quick vs. standard vs. deep execution based on user intent

### Execution Flow

```
User Request → Context Analysis → Skill Selection → Mode Detection → Skill Execution
```

1. **Context Analysis:** Claude Code analyzes your request to understand marketing domain and intent
2. **Skill Selection:** Automatically chooses the most relevant skill(s)
3. **Mode Detection:** Determines execution depth (quick for simple requests, standard for complex workflows, deep for extensive research)
4. **Skill Execution:** The selected skill follows its predefined workflow with appropriate output format

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/BrianRWagner/ai-marketing-claude-code-skills.git

# Install skills into Claude Code
mkdir -p ~/.claude/skills
cp -r ai-marketing-claude-code-skills/* ~/.claude/skills/
```

### Basic Usage

Once installed, you can use skills in Claude Code directly:

```
I'll create a cold outreach sequence for your SaaS company.
```

Or for specific tasks:

```
Analyze my LinkedIn profile and suggest improvements.
```

### Skill Categories

Navigate to the skills folder in Claude Code's skill directory:

- `skills/.marketing/` – Core marketing skills
- `skills/.social/` – Social media engagement skills
- `skills/.content/` – Content creation and optimization
- `skills/.analytics/` – Marketing analytics and insights

## Key Features

### Adaptive Execution

Every skill supports three modes automatically detected from context:

#### Quick Mode (< 15 minutes)
- Minimum viable output
- Single-pass execution
- No deep research or scoring
- Best for: Simple tasks, initial drafts, quick checks

#### Standard Mode (30-45 minutes)
- Full process execution
- All phases with scoring where relevant
- Priority output generation
- Best for: Complete workflows, comprehensive analysis, feature requests

#### Deep Mode (60-90 minutes)
- Extended research and iteration
- Framework generation for ongoing use
- Competitive intelligence integration
- Best for: Strategic planning, competitive analysis, long-term initiatives

### Workflow Capabilities

#### Sequential Execution
Skills can chain together for complex workflows:

1. Analyze current marketing position
2. Generate content strategy
3. Create campaign outline
4. Execute content creation
5. Optimize based on performance

#### Parallel Processing
Independent tasks can run simultaneously:

- Multi-channel content generation
- Simultaneous social media monitoring
- Parallel competitive analysis
- Concurrent audience segmentation

#### Error Recovery
Built-in resilience for marketing workflows:
- **Retry Logic:** Automatic retry for transient failures
- **Fallback Strategies:** Alternative approaches when primary fails
- **Partial Output:** Get what you can when something goes wrong

### Data & Integration

#### Real-Time Insights
Skills pull real-time data from:
- **Web Analytics:** Google Analytics, site performance
- **Social Signals:** Engagement metrics, sentiment analysis
- **Competitive Intelligence:** Competitor strategies, market trends
- **Industry Data:** Marketing benchmarks, best practices

#### Personal Data
User preferences are stored and learned:
- **Targeting Preferences:** Preferred industries, audience segments
- **Content Preferences:** Writing style, tone, format preferences
- **Performance History:** Learn from previous campaign results

## Use Cases

### For Marketing Teams

**Campaign Automation**
```
Create a LinkedIn lead gen campaign for B2B SaaS featuring:
- 4-touch sequence with personalization
- Automated follow-up based on engagement
- Competitive intelligence integration
- Performance tracking and optimization
```

**Content Strategy**
```
Develop a 30-day content plan for our tech startup covering:
- Industry trends and insights
- Product launch coverage
- Thought leadership pieces
- Customer success stories
```

**Market Research**
```
Analyze the competitive landscape for sustainable fashion:
- Competitor SWOT analysis
- Trend identification
- Audience segmentation
- Opportunity gaps
```

### For Individual Marketers

**Personal Branding**
```
Optimize my LinkedIn profile for senior marketing role:
- Headline and summary optimization
- Skills categorization and keyword optimization
- Content strategy suggestions
- Network building recommendations
```

**Campaign Management**
```
Setup and run a Q4 marketing campaign:
- Goal setting and KPI definition
- Budget allocation and channel strategy
- Content calendar and execution
- Performance tracking and reporting
```

## Technical Details

### Skill Architecture

Each skill follows a consistent pattern:

1. **SKILL.md** – Skill entry point, routing table, core rules
2. **references/** – On-demand knowledge files (looking up and citing sources)
3. **scripts/** – Python execution scripts for complex operations
4. **templates/** – Reusable templates for skill outputs

#### Skill Structure

```
skills/
  <skill-name>/               # Skill directory
    SKILL.md                  # Skill definition
    references/              # Knowledge base
    scripts/                 # Python scripts
    templates/               # Output templates
    config/                  # Skill configuration
    tests/                   # Automated tests
    README.md               # Skill documentation
```

### Configuration

Skills support extensive customization:

#### Environment Variables
- `API_KEY` – Service API keys
- `DATABASE_URL` – Data storage connection
- `LOG_LEVEL` – Logging verbosity
- `EXECUTION_MODE` – Skill execution mode

#### Configuration Files
- `config/skill-config.json` – Skill-specific settings
- `config/defaults.json` – Default configuration
- `config/development.json` – Development overrides

### Development

#### Adding New Skills

To add a new skill:

1. **Create skill directory** with SKILL.md
2. **Add references** for knowledge requirements
3. **Implement scripts** for skill logic
4. **Create templates** for output formatting
5. **Write tests** for validation
6. **Update documentation** for usage examples

#### Testing

Skills include comprehensive testing:

- **Unit Tests:** Individual skill component testing
- **Integration Tests:** End-to-end workflow testing
- **Performance Tests:** Execution time and resource usage
- **Compatibility Tests:** Cross-platform and cross-skill compatibility

### File Structure

```
ai-marketing-claude-code-skills/
├── skills/                    # Skill directories
│   ├── <skill-name>/         # Individual skills
│   │   ├── SKILL.md          # Skill definition
│   │   ├── references/       # Knowledge files
│   │   ├── scripts/          # Python scripts
│   │   ├── templates/        # Output templates
│   │   └── config/           # Configuration
│   └── ...
├── README.md                  # Project documentation
├── CHANGELOG.md              # Version history
├── SKILL-MODE-PATTERN.md       # Pattern documentation
└── tests/                    # Automated tests
```

## Integration

### With Claude Code

AI Marketing Skills integrates seamlessly with Claude Code:

#### Automatic Discovery
Skills are automatically discovered based on conversation context.

#### Context-Aware Selection
Claude Code selects the most appropriate skill for each marketing task.

#### Mode Adaptation
Skills automatically adapt their complexity based on user intent and context.

### Claude Code Compatibility

- **Native Integration:** Works directly within Claude Code's skill system
- **Command Line Interface:** Direct CLI commands for complex operations
- **API Integration:** Programmatic access for custom integrations
- **Plugin Architecture:** Extensible system for new skill types

## Benefits

### For Organizations

- **Consistency:** Standardized marketing execution across teams
- **Scalability:** Handle increasing marketing complexity without proportional overhead
- **Speed:** Rapid execution of marketing tasks without manual intervention
- **Quality:** Consistent, professional outputs based on expert frameworks

### For Individuals

- **Efficiency:** Automate repetitive marketing tasks
- **Learning:** Access expert marketing knowledge and frameworks
- **Productivity:** Focus on strategy while skills handle execution
- **Growth:** Build marketing expertise through guided practice

### For Content Creators

- **Creativity:** AI-powered content generation and optimization
- **Distribution:** Multi-channel content automation
- **Engagement:** Personalized audience targeting and nurturing
- **Analytics:** Data-driven content optimization

## Limitations

### Technical Considerations

- **Context Understanding:** Limited to marketing domain contexts
- **Creative Originality:** Generated content follows established frameworks
- **Personal Touch:** AI-generated content may lack personal anecdotes
- **Cultural Sensitivity:** Requires local customization for different markets

### Skill Coverage

- **Specialized Knowledge:** May not cover highly specialized marketing niches
- **Industry Specificity:** Framework-based approach may miss industry-specific nuances
- **Regulatory Compliance:** Legal and regulatory considerations require human oversight

## Future Directions

### Planned Enhancements

1. **Advanced AI Integration:** Deeper integration with emerging AI models
2. **Custom Skill Development:** Tools for creating specialized marketing skills
3. **Cross-Platform Synchronization:** Unified skill across multiple platforms
4. **Advanced Analytics:** Predictive analytics and marketing intelligence

### Research Areas

- **Marketing Attribution:** Advanced attribution modeling
- **Customer Journey Optimization:** AI-powered journey optimization
- **Content Personalization:** Hyper-personalized content generation
- **Marketing ROI Measurement:** Advanced ROI calculation and attribution

## Support & Community

### Documentation

- **README.md:** Project overview and quick start
- **SKILL-MODE-PATTERN.md:** Pattern documentation
- **CHANGELOG.md:** Version history and updates
- **SKILL.md:** Individual skill documentation (in each skill directory)

### Community

- **GitHub Issues:** Bug reports and feature requests
- **Discussions:** Community Q&A and best practices
- **Social Networks:** Updates and networking opportunities
- **Learning Resources:** Tutorials, examples, and case studies

### Contact

For questions, support, or collaboration opportunities:

- **GitHub Issues:** https://github.com/BrianRWagner/ai-marketing-claude-code-skills/issues
- **Discussions:** https://github.com/BrianRWagner/ai-marketing-claude-code-skills/discussions
- **Email:** brian@marketingclaude.com

## Legal & Licensing

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- **Inspired by:** Everything Claude Code (ECC) runtime profile system
- **Based on:** Agent Skills open standard
- **Powered by:** Claude Code skill architecture
- **Contributors:** Special thanks to all skill developers and contributors

## Version History

### v3.1 (March 2026)
- Added SKILL_MODE pattern support
- Enhanced workflow automation
- Improved user experience
- Bug fixes and stability improvements

### v2.0 (January 2026)
- Initial release
- Basic skill framework
- Core marketing skills

---

## References

### Source Documentation

- `sources/ai-marketing-claude-code-skills/` – Full source code repository
- `raw/ai-marketing-claude-code-skills/ai-marketing-claude-code-skills.xml` – Repomix XML export

### External Resources

- [Agent Skills Standard](https://agentskills.io/) – Skills definition and distribution
- [Claude Code Documentation](https://claude.ai/claude-code) – Claude Code platform docs
- [Marketing Frameworks](https://www.marketingframeworks.com/) – Marketing framework references

---

*This wiki entry is generated from the source repository and follows the AI Marketing Claude Code Skills repository's documentation standards.*

---

**Last Updated:** March 14, 2026  
**Generated:** Claude Code Wiki Generator  
**Verification:** Source code verified against `sources/ai-marketing-claude-code-skills/`