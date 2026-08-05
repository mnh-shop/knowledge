---
name: redhound-arsenal
tags: [security, pentesting, red-team, offensive-security, skills, agent-skills, cybersecurity, wiki, redhound-arsenal]
description: "76 offensive security agent skills covering 95+ tools across 18 category sections — MIT-licensed, built by Red Hound InfoSec for pentesters and red teamers"
source: sources/redhound-arsenal/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# RedHound Arsenal

| Field | Value |
|---|---|
| **Origin** | [RedHoundInfosec/redhound-arsenal](https://github.com/RedHoundInfosec/redhound-arsenal) |
| **License** | MIT (skill content; each tool's own license in per-skill frontmatter `license` field) |
| **Format** | Markdown SKILL.md files with YAML frontmatter (agentskills.io format) |
| **Deployment** | 76 skill folders at repo root — copy per-skill SKILL.md or serve over HTTP |
| **Source** | `sources/redhound-arsenal/` |

## What is it?

A curated arsenal of 76 offensive security agent skills covering 95+ tools, purpose-built for AI coding agents used by penetration testers and red teamers. Each skill is a standalone `SKILL.md` file in its own folder at the **repository root** (there is no `skills/` subdirectory), following the [agentskills.io](https://agentskills.io) format with YAML frontmatter and structured markdown content (README.md:54, 121-124).

Built by Red Hound InfoSec — 20+ years of Fortune 500 offensive security experience — the arsenal transforms AI coding agents into capable security assistants that can guide reconnaissance, exploitation, post-exploitation, and reporting workflows (README.md:11, 574).

## Key Features

- **76 Skills:** Comprehensive offensive security skills for AI agents, all at the repo root (README.md:30, 121).
- **95+ Tools Analyzed:** Nmap, Masscan, Metasploit, Burp Suite, BloodHound, Impacket, NetExec, Responder, Ligolo-ng, Chisel, Ghidra, and many more (README.md:32). Note: **CrackMapExec is not included** — its successor NetExec (`netexec`) is, and its skill explicitly covers the cme→nxc migration (netexec/SKILL.md).
- **18 Category Sections in the Tool Index:** The README's own stats table says 17 categories, but the Tool Index actually contains **18 sections** (README.md:31 vs 132-292). Full list below.
- **Operator-Grade Depth:** 300-500 lines per skill covering seven standard sections (README.md:33, 363, 551).
- **Structured Format:** Consistent YAML frontmatter — `name`, `description`, `license`, `metadata.{author, version, repo, language}` (README.md:494-504; nmap/SKILL.md).
- **Auto-Activation:** Skills activate automatically via keyword/semantic matching on the `description` field — no manual invocation required (README.md:9, 63, 302).
- **Multi-Skill Stacking:** Related skills activate simultaneously — e.g., an AD attack chain can load bloodhound, impacket, responder, and hashcat together (README.md:345, 490-492).
- **Agent-Ready:** Documented for Perplexity Computer, Claude Code, Cursor, Codex CLI, manual system-prompt injection, and HTTP serving. Skills are plain markdown — they work anywhere a system prompt or context file is accepted (README.md:56-124, 110).
- **Portable:** No runtime dependencies; copy, serve, or inject directly into context.

## Categories (Tool Index — 18 sections)

The README Tool Index is organized into these sections (README.md:132-292). The stats table's "17" is the repo's own undercount; on disk there are 18:

| # | Category | Example Tools |
|---|---|---|
| 1 | Information Gathering | nmap, masscan, rustscan, theHarvester, AutoRecon, recon-ng |
| 2 | Reconnaissance | gitleaks, subfinder, httpx, Sherlock, Katana, Amass, SpiderFoot |
| 3 | Web Application | PayloadsAllTheThings, sqlmap, Burp Suite, ffuf, WPScan, OWASP ZAP, gobuster, Nikto, XSStrike, feroxbuster, Commix, Arjun |
| 4 | Vulnerability Analysis | Nuclei |
| 5 | Password Attacks | SecLists, John the Ripper, Hydra, Hashcat, CeWL, Crunch |
| 6 | Active Directory | Responder, NetExec, Mimikatz, Impacket, BloodHound, Evil-WinRM, Kerbrute |
| 7 | Exploitation | Metasploit, ExploitDB, BeEF |
| 8 | Post-Exploitation | PEASS-ng, GTFOBins, pspy |
| 9 | Reverse Engineering | Ghidra, JADX, Frida, Apktool, Pwntools, Binwalk, Radare2, GDB+GEF |
| 10 | Sniffing & Spoofing | Wireshark, Bettercap, mitmproxy, Scapy, tcpdump |
| 11 | Wireless Attacks | Aircrack-ng, Wifite |
| 12 | Forensics | YARA, Volatility3, CyberChef, Autopsy, Chainsaw |
| 13 | Social Engineering | Evilginx2, SET |
| 14 | C2 Frameworks | Sliver, Havoc |
| 15 | Pivoting & Tunneling | Chisel, Ligolo-ng, Proxychains |
| 16 | Cloud Security | ScoutSuite, Pacu |
| 17 | Evasion | Veil |
| 18 | Reporting | EyeWitness |

## Skill Format (Frontmatter)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Machine-readable skill identifier, matches the folder name |
| `description` | string | Activation trigger text — index this field for routing |
| `license` | string | License of the upstream tool |
| `metadata.author` | string | Skill author (`redhoundinfosec`) |
| `metadata.version` | string | Skill version |
| `metadata.repo` | string | Upstream tool repository URL |
| `metadata.language` | string | Primary implementation language of the tool |

(README.md:494-504; nmap/SKILL.md:1-16)

There are no `tools`, `category`, or `tags` frontmatter fields — all 76/76 skill files carry `name`, `description`, and `metadata` (verified across `*/SKILL.md`).

## Ranking Methodology

Each tool received a composite 4-factor score used to prioritize inclusion and ordering (README.md:389-419):

```
Score = (real_world_usage × 3.0)
      + (uniqueness × 2.5)
      + (normalized_stars × 1.5)
      + (kali_top10_bonus × 2.0)
```

Tier interpretation: 30+ = Tier 1 essential; 25-29 = Tier 2 high-value; 20-24 = Tier 3 specialized; below 20 = Tier 4 niche.

## Skill Content

Every skill covers seven engagement-grade sections (README.md:351-363): **When to Use**, **Core Concepts**, **Installation**, **CLI Reference**, **Common Workflows**, **Advanced Techniques**, and **Troubleshooting** — 300-500 lines encoding practitioner knowledge (real flags, hardened-target workflows, engagement gotchas), not documentation summaries. Example sizes: nmap 408 lines, metasploit-framework 453, burpsuite 453, ligolo-ng 330.

## Deployment

### Copy individual skill files (documented for Claude Code / Cursor)

Skills live at the repo root — there is no `skills/` subdirectory. The README's documented bulk pattern is a shell loop over root folders:

```bash
git clone https://github.com/redhoundinfosec/redhound-arsenal.git
cd redhound-arsenal
for dir in */; do
  [ -f "$dir/SKILL.md" ] && cp "$dir/SKILL.md" ~/.claude/skills/"${dir%/}.md"
done
```

(README.md:74-78; Cursor variant at 90-96. Replace `~/.claude/skills/` with the target agent's skill directory.)

### Perplexity Computer

Upload the `SKILL.md` from any skill folder via [perplexity.ai/computer/skills](https://perplexity.ai/computer/skills) — becomes available immediately (README.md:56-63).

### Codex CLI and other agents

Point the agent's skill loader at the `SKILL.md` path directly — e.g. `codex --context nmap/SKILL.md "scan 192.168.1.0/24 for web services"` — or inject the file into the system prompt/custom instructions (README.md:98-114).

### Serve via HTTP

```bash
cd redhound-arsenal
python3 -m http.server 8000    # Serve skills for remote agents (README.md:513)
curl http://localhost:8000/nmap/SKILL.md
```

## Related

- [[SecuritySkills]] — Complementary security skills collection
- [[Anthropic-Cybersecurity-Skills]] — Anthropic's cybersecurity skill pack
- [[kali-pentest]] — Kali Linux pentesting skills
- [[hexstrike-ai]] — Security-focused agent framework
- [[abvx-agent-skills]] — General-purpose agent skill pack
- [[hermes-agent]] — MCP hub that can load these SKILL.md files
