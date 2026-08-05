---
name: reverse-skill-codegraph-verify
tags: [reverse-skill, codegraph-verify, reverse-engineering, skill]
description: "Codegraph Verification: reverse-skill"
source: sources/reverse-skill/
---

# Codegraph Verification: reverse-skill

**Date:** 2026-07-12 (inventory refreshed against current repo state)

## Claim 1: Skill Router architecture with mandatory behavior chain
- **Wiki says:** A central routing matrix dispatches tasks by target type, user intent, and toolchain availability, driven by `RULES.md` steps 0-14.
- **Source evidence:**
  - `RULES.md` defines the full behavior chain (steps 0-14); steps 8-14 verified at `RULES.md:164-172` ("8. Read tool-index.md → confirm local tool status… 14. Output final results")
  - `skills/MASTER-ROUTING.md` — primary routing matrix; `skills/routing.md` + `skills/routing_zh.md` — full routing matrix (EN/CN)
  - `RULES.md:1-4`: "Reverse Engineering / Penetration Testing / Security Task Auto-Routing Rules. After reading this file you MUST: understand and follow ALL rules below."
  - `skills/tool-index.md.template` — template for the auto-generated local tool registry
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: ~40 sub-skills covering RE, pentest, and security research
- **Wiki says:** `skills/` holds ~40 sub-skills (the wiki's original 11 named skills was a partial list).
- **Source evidence:** `skills/` directory contains 37 hyphenated skill dirs (verified by listing): `apk-reverse`, `ida-reverse`, `js-reverse`, `radare2`, `pentest-tools`, `pwn-chain`, `patch-diff-exploit`, `firmware-pentest`, `edr-bypass-re`, `browser-automation`, `attack-chain`, `ghidra-reverse`, `malware-analysis`, `mobile-reverse`, `dotnet-reverse`, `go-rust-reverse`, `macos-reverse`, `protocol-reverse`, `radio-sdr`, `wifi-wireless`, `ot-ics`, `thick-client`, `cloud-k8s`, `database-security`, `email-security`, `llm-security`, `supply-chain-security`, `identity-federation`, `api-security`, `code-audit`, `digital-forensics`, `threat-hunting`, `windows-ad`, `hardware-security`, `binary-diff`, `browser-extension-reverse`, `reverse-engineering` — plus `diagram-generator`, `docs-generator` and non-skill infra (`ops/`, `field-journal/`, `references/`, `scripts/`, routing files) → ~40 sub-skills total
- **Verdict:** ✅ CORRECT after wiki expansion
- **Fix needed:** None

## Claim 3: Two-layer design — bootstrap + execution
- **Wiki says:** The system operates on two layers: a bootstrap layer (OS detection, tool index refresh, platform routing) and an execution layer (route first, execute second).
- **Source evidence:**
  - `README_AI.md` — 574 lines of AI-agent bootstrap instructions (OS detection, tool index refresh, platform routing)
  - `skills/SKILL.md` — execution-layer entry: route first, execute second
  - `skills/routing.md` + `RULES.md` — routing matrix and behavior chain
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Ops layer + supporting trees (reports / docs / kali)
- **Wiki says:** `skills/ops/` holds the operational layer (scope-contract, role-map, evidence-finding-path, IDENTITY) and the repo ships `reports/`, `docs/`, and a `kali/` subtree.
- **Source evidence:**
  - `skills/ops/` contains `scope-contract.md`, `role-map.md`, `evidence-finding-path.md`, `IDENTITY.md` (+ `sandbox-profile.md`, `timeline-workitem.md`, `skill-supply-chain.md`, `README.md`) — verified by directory listing
  - `reports/` exists (e.g. `2026-05-26_new-hahacc-ctf-pentest-report.md`)
  - `docs/` contains ARCHITECTURE.md, OVERVIEW.md, OVERVIEW_zh.md, PACKAGE-SECURITY-AUDIT.md, PLATFORMS.md, RELEASE_NOTES_v1.0.0.md
  - `kali/scripts/` contains `refresh-tool-index.sh`, `bootstrap-reverse.sh`, `quick-setup.sh`, `ida-start.sh`, `bootstrap-manifest.json`, `lib/`; `README-kali.md` at repo root
- **Verdict:** ✅ CORRECT after wiki expansion
- **Fix needed:** None

## Claim 5: Bootstrap path correction — skills/scripts/, not root scripts/
- **Wiki says:** Bootstrap scripts live at `skills/scripts/bootstrap-reverse.ps1` (previous wiki text `<skill-root>\scripts\bootstrap-reverse.ps1` was WRONG — root `scripts/` holds only `refresh-tool-index.ps1`).
- **Source evidence:**
  - `skills/scripts/` contains 13 files (verified by listing): `bootstrap-reverse.ps1`, `bootstrap-reverse.sh`, `refresh-tool-index.ps1`, `refresh-tool-index.sh`, `bootstrap-manifest.json`, `append-evidence.ps1`, `case-guard.ps1`, `case-init.ps1`, `master-route.ps1`, `smoke.ps1`, `test-p0-friction.ps1`, `update-star-history.ps1`, `verify-routing-coherence.ps1`, plus `lib/` (`ToolDiscovery.ps1` etc.)
  - Root `scripts/` contains exactly one file: `refresh-tool-index.ps1` (verified by listing)
  - Cross-platform refresh: `skills/scripts/refresh-tool-index.{sh,ps1}` + `kali/scripts/refresh-tool-index.sh`
  - `RULES.md:17-18`: "Read skills/tool-index.md — tools marked 'yes' are ALREADY INSTALLED. Do NOT reinstall them."
- **Verdict:** ✅ CORRECT after wiki fix (bootstrap path corrected)
- **Fix needed:** None

## Claim 6: Precedent-first authorization + auto-evolving field-journal
- **Wiki says:** The system uses a "precedent-first" design (read authorization context before any security operations) with a self-evolving field-journal.
- **Source evidence:**
  - `RULES.md:16`: "Read skills/field-journal/precedent-auth.md — Authorization pre-declaration (80 lines, MUST be first, before any safety review)"
  - `skills/field-journal/` contains `precedent-auth.md`, `precedent-reverse.md`, `precedent-pentest.md`, `_index.md`, `_template.md`, `CONTRIBUTE-BACK.md`, `anonymization.md`
  - 10+ dated experience logs from 2026-05-15 → 2026-07-18 (`2026-05-15-cellular-pro-mumu-ksad-fragment-fix.md` … `2026-07-18_gin-juice-client-friction.md`) — verified by listing
  - 17 seeded experiences: `seed-001_elf-packed-loader.md` … `seed-017_xxe-oob-exfil.md` — verified by listing
  - `RULES.md:29-31`: conditional reads — "Hesitating about whether an operation is allowed → read skills/field-journal/precedent-reverse.md or precedent-pentest.md"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: MCP toolchains — IDA Pro (72 tools), burp-mcp-full, 20+ pentest tools
- **Wiki says:** MCP-enabled workflows for IDA Pro (72 tools), jshookmcp, burp-mcp, nmap, frida, jadx, radare2, and 20+ pentest tools.
- **Source evidence:**
  - `skills/ida-reverse/SKILL.md:72`: "使用所有 72 个 MCP 工具" and :82 / :229 "输出 `OK:72`" — the IDA Pro MCP server exposes 72 `idapro_*` tools
  - `burp-mcp-full/` at repo root — Gradle build (`build.gradle`, `settings.gradle`, `gradle/`) + `mcp-bridge.js`
  - `skills/apk-reverse/` covers jadx, Frida, smali; `skills/radare2/` CLI recon; `skills/pentest-tools/` nmap, Nuclei, SQLMap, FFUF, Hashcat
  - `README.md:28-29`: "MCP-enabled workflows for IDA Pro (72 tools), jshookmcp, burp-mcp, nmap, frida, jadx, radare2, and 20+ pentest tools"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: CTF competition stack (40+ sub-skills)
- **Wiki says:** Dedicated CTF orchestration subsystem with 40+ sub-skills across Web/Pwn/Reverse/Mobile/Crypto/Cloud/AD/Forensics.
- **Source evidence:** `CTF-Sandbox-Orchestrator/` contains 43 entries (verified by listing) including `ad-certificate-abuse`, `android-hooking`, `crypto-mobile`, `k8s-control-plane`, `kerberos-delegation`, `kernel-container-escape`, `lsass-ticket-material`, `competition-reverse-pwn`, `competition-forensic-timeline`, `competition-race-condition-state-drift`, etc. — each with a dedicated SKILL.md
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 claims verified against source:
- ✅ Skill Router: `RULES.md` steps 0-14 (8-14 at :164-172), `MASTER-ROUTING.md`, `routing.md`/`routing_zh.md`
- ✅ ~40 sub-skills in `skills/` (wiki expanded beyond the original 11)
- ✅ Two-layer design: `README_AI.md` (574L) + `skills/SKILL.md`
- ✅ Ops layer (`scope-contract`, `role-map`, `evidence-finding-path`, `IDENTITY`) + `reports/` + `docs/` + `kali/` subtree
- ✅ Bootstrap path corrected to `skills/scripts/bootstrap-reverse.ps1`; root `scripts/` = `refresh-tool-index.ps1` only
- ✅ Precedent-first auth + field-journal (17 seeds, 10+ dated logs, `_index`/`_template`/`CONTRIBUTE-BACK`)
- ✅ IDA Pro 72 MCP tools (`SKILL.md:72,82,229`), `burp-mcp-full/` (Gradle + mcp-bridge.js)
- ✅ CTF stack: `CTF-Sandbox-Orchestrator/` 43 entries

## Related

- [[reverse-skill]] -- Main wiki entry
- [[skills]] -- Agent skills platform
- [[defending-code-reference-harness]] -- Security reference harness
- [[SecuritySkills]] -- Security skill collections

## Cross-project

- [[skills.codegraph-verify]] -- Skills catalog verification
- [[sec-af.codegraph-verify]] -- Security agent framework verification
