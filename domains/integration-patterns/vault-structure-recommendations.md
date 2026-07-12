---
name: vault-structure-recommendations
description: "Recommendations for improving agent context retrieval in the knowledge vault"
tags: [integration-patterns, reference, mcp, architecture]
metadata:
  type: reference
---

# Vault Structure Recommendations

Analysis of the knowledge vault structure and recommendations for better agent context retrieval.

## Current Structure Works

1. **Wikilink navigation** — `[[page-name]]` creates traversable relationships
2. **Tag taxonomy** — Ecosystem, language, and classification tags are consistent
3. **Layer architecture** — `sources/` (immutable), `wiki/domains/` (derived), `assets/` (curated) is sound
4. **Evidence-grounded** — `source:` fields point to authoritative code

## Key Blocking Issues

### 1. Missing Wiki Pages — ✅ Fixed

All 16 previously missing wiki pages are now created:
- `Android-Pentesting-Checklist`, `Anthropic-Cybersecurity-Skills`, `CyberStrikeAI`, `ECC`, `Hexstrike-redteam`, `hexstrike-ai`, `OpenViking`, `SecuritySkills`, `agent-rules-books`, `communitytools`, `defending-code-reference-harness`, `fedora-coreos-config`, `hermes-profiles`, `kali-pentest`, `outreachmagic`, `reverse-skill`
- All include proper frontmatter (source, tags), wikilinks, and <150-line structure

**Next:** `bootc` still needs a wiki page despite existing in namespace.

### 2. Profile System Confusion

`sources/hermes-profiles/profiles/` has 38 actual profiles (SOUL.md + profile.yaml)  
`assets/agent-references/` has 18 reference docs but references 8 non-existent profiles

**Fix:** Clarify distinction:
- Hermes profiles = runtime specialization (38 profiles in sources)
- Asset profiles = documentation (reference guides)

### 3. Duplicate Repo Naming

`ECC` vs `ecc`, `OpenViking` vs `openviking` — creates tag taxonomy confusion.

**Fix:** Normalize to lowercase; `ecc` is canonical per SCHEMA.

### 4. Orphaned `integrations/` Folder

Schema says "reserved" but has 1 file. Cross-repo compatibility in MEMORY.md but no machine-readable links.

**Fix:** Either remove or properly integrate into `domains/integration-patterns/`.

### 5. `.codegraph-verify.md` Undocumented

These 3 files validate claims against source code but aren't in SCHEMA.md format documentation.

**Fix:** Add to SCHEMA.md or move to proper location (perhaps `domains/architecture/`).

### 6. Disconnected CodeGraph

`graphs/` contains static data but no INDEX linking to wiki/domain context.

**Fix:** Add `graphs/INDEX.md` mapping repo → graph purpose + key queries.

## Recommendations

### Short Term

1. **Create missing wiki pages** — 16 repos need entries
2. **Fix broken cross-references** — Update `hermes-profiles-INDEX.md` to point to correct files or remove dead links
3. **Normalize tag taxonomy** — Remove `wiki` tag (not in classification list), enforce tag hygiene

### Medium Term

4. **Add machine-readable provenance** — Generate index files for `raw/` and `graphs/` directories
5. **Integrate profile system** — Decide: move profile INDEX to `sources/hermes-profiles/` or update assets to match reality
6. **Document companion pages pattern** — Add schema rule for pages that share parent ecosystem tags

### Long Term

7. **Consider CodeGraph at vault root** — Enable live `codegraph explore` queries against combined knowledge
8. **Add lifecycle for ideas/** — When validated, move ideas to appropriate layer instead of leaving static
9. **Create skill-to-profile mapping** — Link which skills are used by which Hermes profiles

## Related

- [[SCHEMA.md]] — Vault conventions and taxonomy
- [[MEMORY.md]] — Coverage status and cross-repo compatibility
- [[hermes-profiles]] — Profile system documentation