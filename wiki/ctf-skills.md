---
name: ctf-skills
tags: [ctf, security, hacking, web, pwn, crypto, reverse-engineering, forensics, osint, malware, ai, claude, skills]
description: "Agent Skills for CTF challenges across 9 categories — web, pwn, crypto, rev, forensics, OSINT, malware, AI/ML, misc — with solve-challenge orchestrator and writeup generator"
source: sources/ctf-skills/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# ctf-skills

**Source:** `sources/ctf-skills/`

Agent Skills for solving CTF challenges across 9 challenge categories: web exploitation, binary pwn, cryptography, reverse engineering, forensics, OSINT, malware analysis, AI/ML, and misc. Works with any tool that supports the Agent Skills spec, including Claude Code and Friday Studio. Ships 11 skill directories — the 9 challenge categories plus a `solve-challenge` orchestrator and a `ctf-writeup` generator.

| Field | Value |
|---|---|
| **Origin** | [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) |
| **License** | MIT |
| **Format** | Markdown SKILL.md files + Python/Bash scripts |
| **Skill Dirs** | 11 (9 challenge categories + solve-challenge + ctf-writeup) |
| **Content Files** | ~100 technique files across categories (README counts exclude each dir's SKILL.md) |
| **npx** | `npx skills add ljagiello/ctf-skills` |
| **Tooling** | Python (pyproject.toml), pytest tests, pre-commit, markdownlint |
| **Source** | `sources/ctf-skills/` |
| **Codegraph** | `graphs/ctf-skills/` |

## What is it?

ctf-skills provides structured, expert-level knowledge for solving Capture The Flag challenges, organized by challenge category. Each skill primes an AI coding agent with the techniques, tooling, edge cases, and exploitation methodologies needed for its domain. The repository includes a solve-challenge orchestrator that guides the agent through a systematic solve process and an automated writeup generator. A central pre-install script sets up all common CTF tooling across multiple package managers, and each skill lists its own Prerequisites for on-demand installs during a challenge.

## Key Features

- **9 Challenge Categories** — `ctf-web` (SQLi, XSS, SSTI, SSRF, JWT, prototype pollution, file upload RCE, Web3/Solidity), `ctf-pwn` (ROP, heap exploitation, FSOP, seccomp bypass, sandbox escapes), `ctf-crypto` (20+ RSA attacks, AES modes, ECC, PRNG, ZKP), `ctf-reverse` (custom VMs, anti-debug/anti-VM, deobfuscation, Android/.NET/Flutter RE), `ctf-forensics` (disk/memory, stego, USB/signals, network captures), `ctf-osint`, `ctf-malware` (C2 analysis, RATs, Cobalt Strike), `ctf-ai-ml` (adversarial examples, prompt injection, model extraction), `ctf-misc` (pyjails, esolangs, privesc)
- **Solve-Challenge Orchestrator** — Systematic challenge-solving workflow that analyzes a challenge and delegates to the appropriate category skills; invoked via `/solve-challenge <challenge description or URL>`
- **Writeup Generator** — Standardized submission-style writeups with metadata, solution steps, code, and lessons learned
- **Central Tool Installer** — `bash scripts/install_ctf_tools.sh` with modes `all`, `python`, `apt`, `brew`, `gems`, `go`, `manual` plus `--dry-run`, `--force`, and `--verify`; install logs saved to `~/.ctf-tools/`
- **Trigger-Activated** — Skills auto-load based on conversational context about specific challenge types; each SKILL.md carries a Prerequisites section for install-as-you-go
- **Quality Tooling** — Catalog + security auditor scripts, pytest suite, pre-commit hooks, markdownlint

### Skill Inventory

Per-category content files as listed in the README (note: counts exclude each directory's own `SKILL.md`):

| Skill | Content files | Coverage |
|---|---|---|
| **ctf-web** | 20 | SQLi (35+ techniques), XSS, SSTI, SSRF, JWT (JWK/JKU/KID), prototype pollution, PHP tricks, Web3/Solidity, GraphQL CSRF, React RCE (CVE-2025-55182) |
| **ctf-pwn** | 18 | Buffer overflow, ROP/ret2csu, heap (unlink, House of Force/Apple 2, Einherjar, tcache), FSOP, seccomp/sandbox escapes, io_uring, musl libc, custom VMs |
| **ctf-crypto** | 16 | 20+ RSA attacks, AES modes, ECC/ECDSA nonce reuse, PRNG (MT, XorShift128+), ZKP/Groth16, LWE/lattices, classic ciphers |
| **ctf-reverse** | 18 | Binary analysis, custom VMs, WASM/RISC-V, Android (Frida, smali), deobfuscation (D-810, GOOMBA), angr, Triton, Flutter/Dart AOT |
| **ctf-forensics** | 14 | Disk/memory forensics, steganography, USB HID, UART, side-channel, network captures, browser artifacts, KeePass cracking |
| **ctf-misc** | 12 | Pyjails, bash jails, encodings, esolangs (Piet/Malbolge/Whitespace), Docker/K8s escapes, privesc chains, Z3/SAT solving |
| **ctf-ai-ml** | 3 | Adversarial examples (FGSM, PGD, C&W), prompt injection, LLM jailbreaking, model extraction, backdoor detection, LoRA exploitation |
| **ctf-osint** | 3 | Geolocation, reverse image search, username enumeration, DNS recon, Shodan, gaming platform OSINT |
| **ctf-malware** | 3 | Obfuscated scripts, C2 traffic, PyInstaller unpacking, YARA, Poison Ivy/DarkComet/Cobalt Strike analysis |
| **solve-challenge** | — | Orchestrator — analyzes challenge and delegates to category skills |
| **ctf-writeup** | — | Generates standardized submission-style writeups |

## Tech Stack

| Component | Technology |
|---|---|
| **Skill Format** | Markdown SKILL.md (Agent Skills spec, YAML frontmatter) |
| **Scripts** | Python 3, Bash |
| **CLI** | `npx skills add` (Agent Skills CLI) |
| **Runtime** | Claude Code, Friday Studio, any Agent Skills-compatible tool |
| **Tool Installer** | Multi-package-manager installer (pip, apt, brew, gem, go, manual) |
| **Dev Tooling** | pyproject.toml, pytest, pre-commit, markdownlint, lychee link checker |

## Deployment

### npx (documented install path)

```bash
npx skills add ljagiello/ctf-skills
```

### Friday Studio (documented install path)

1. Install Friday from [hellofriday.ai](https://hellofriday.ai/) (macOS)
2. Open **Skills** in the Studio sidebar → **+ Add**
3. Import individual skills by reference (e.g. `ljagiello/ctf-skills/ctf-web`) or upload the repo as a folder
4. Reference them from any `workspace.yml`, or let agents auto-load them by description

Note: the repository documents only the two install paths above — the README contains no manual copy-to-user-skills-folder flow.

### Tool Installation

```bash
# Install all tool categories
bash scripts/install_ctf_tools.sh all

# Or install specific categories
bash scripts/install_ctf_tools.sh python
bash scripts/install_ctf_tools.sh apt
bash scripts/install_ctf_tools.sh brew
bash scripts/install_ctf_tools.sh gems
bash scripts/install_ctf_tools.sh go
bash scripts/install_ctf_tools.sh manual

# Preview without installing (skips already-present packages)
bash scripts/install_ctf_tools.sh --dry-run all

# Verify installed tools
bash scripts/install_ctf_tools.sh --verify

# Force reinstall of everything
bash scripts/install_ctf_tools.sh --force all
```

Install logs are saved to `~/.ctf-tools/` (`~/.ctf-tools/install-*.log`, plus a `venv` for Python tools).

## Usage

Skills are loaded automatically based on context. You can also invoke the orchestrator directly:

```text
/solve-challenge <challenge description or URL>
```

During a challenge, each skill's **Prerequisites** section lists only the tools needed for that category — install as you go when the agent encounters a missing tool.

### Repository Quality Tooling

- `scripts/generate_catalog.py` — regenerates the README skill catalog tables
- `scripts/skill_security_auditor.py` — audits skill content for security issues
- `tests/` — pytest suite: `test_skill_frontmatter.py`, `test_cross_references.py`, `test_skill_discoverability.py`, `test_skill_security_auditor.py`
- `pyproject.toml` — Python tooling config; `.pre-commit-config.yaml` + `.markdownlint-cli2.yaml` + `.lychee.toml` for CI checks

## Related

- [[Claude-Red]] — 58 offensive security skills for Claude Skills system
- [[Claude-OSINT]] — OSINT methodology and arsenal skills for Claude
- [[Hexstrike-redteam-full]] — AI-powered MCP cybersecurity automation platform
- [[SecOpsAgentKit]] — Security operations skills for AI coding agents
