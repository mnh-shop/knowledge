---
name: slavinga-skills-codegraph-verify
tags: [slavinga-skills, codegraph-verify, skills, automation]
description: "Codegraph Verification: slavinga-skills — validating wiki claims against indexed source code symbols"
source: sources/slavinga-skills/
---

# Codegraph Verification: slavinga-skills

**Date:** 2026-07-12

## Claim 1: Claude Code skills based on The Minimalist Entrepreneur by Sahil Lavingia
- **Wiki says:** Claude Code skills based on "The Minimalist Entrepreneur" by Sahil Lavingia (founder of Gumroad). The skills implement the methodology from the book.
- **Source evidence:**
  - `README.md` line 1: "# The Minimalist Entrepreneur — Claude Code Skills"
  - `README.md` line 3: "Claude Code skills based on [The Minimalist Entrepreneur](https://www.minimalistentrepreneur.com/) by Sahil Lavingia."
  - `README.md` line 5: "In Claude Code: `/plugin marketplace add slavingia/skills`" — references slavingia's GitHub
  - `README.md` lines 48-60: "The Minimalist Entrepreneur Journey" section maps all 10 skills to the book's progression from Community → Validate → Build → Processize → Sell → Price → Market → Grow → Culture → Review
  - Each skill SKILL.md includes the phrase "channeling the philosophy of The Minimalist Entrepreneur by Sahil Lavingia"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 10 skills covering the full entrepreneur journey
- **Wiki says:** 10 skills: /find-community, /validate-idea, /mvp, /processize, /first-customers, /pricing, /marketing-plan, /grow-sustainably, /company-values, /minimalist-review.
- **Source evidence:**
  - `README.md` lines 33-46: Table listing all 10 skills with commands and "When to use" descriptions
  - `skills/find-community/SKILL.md` exists — "Looking for a business idea, trying to find your community"
  - `skills/validate-idea/SKILL.md` exists — "Testing if a business idea is worth pursuing"
  - `skills/mvp/SKILL.md` exists — "Ready to build your first product, struggling with scope"
  - `skills/processize/SKILL.md` exists — "Have a product idea, want to deliver value by hand before writing code"
  - `skills/first-customers/SKILL.md` exists — "Have a product, need to find your first 100 customers"
  - `skills/pricing/SKILL.md` exists — "Setting prices, considering price changes"
  - `skills/marketing-plan/SKILL.md` exists — "Have product-market fit, ready to scale with content"
  - `skills/grow-sustainably/SKILL.md` exists — "Making decisions about spending, hiring, or scaling"
  - `skills/company-values/SKILL.md` exists — "Defining culture, preparing to hire"
  - `skills/minimalist-review/SKILL.md` exists — "Gut-checking any business decision"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: MVP skill teaches manual-first → processized → productized progression
- **Wiki says:** The MVP skill teaches the Three Stages: Manual (do it yourself) → Processized (systematize the manual work) → Productized (automate the process). Core principle: build as little as possible.
- **Source evidence:**
  - `skills/mvp/SKILL.md` line 10: "**Build as little as possible.** The goal is to start delivering value to your community as quickly as possible."
  - `skills/mvp/SKILL.md` lines 13-29: Three Stages clearly defined:
    - Stage 1 Manual: "Solve the problem by hand for each customer"
    - Stage 2 Processized: "Document your process on a piece of paper so anyone could do it"
    - Stage 3 Productized: "Now automate each task so customers can use your product without you"
  - `skills/mvp/SKILL.md` lines 32-37: "The Four Build Questions" — scope to a weekend, customer benefit, willingness to pay, quick feedback
  - `skills/mvp/SKILL.md` lines 39-48: "What to Build" — CRUD apps, one thing, no polish, charge money, use existing tools
  - `skills/mvp/SKILL.md` lines 49-55: "What NOT to Build" — no someday features, no scale, no mobile app when website works, no code when spreadsheet works
  - `skills/mvp/SKILL.md` lines 75-81: "Output" section — defines 5 concrete deliverables
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: First customers skill teaches concentric circles sales strategy
- **Wiki says:** The first-customers skill teaches a concentric circles approach: Friends & Family → Your Community → Strangers (Cold Outreach). Core principle: skip the launch, focus on selling one by one.
- **Source evidence:**
  - `skills/first-customers/SKILL.md` line 10: "**Skip the launch. Focus on selling.** 'Viral success' is a myth."
  - `skills/first-customers/SKILL.md` lines 13-38: "The Concentric Circles of Sales" with three circles:
    - Circle 1: Friends and Family — "Pitch them on being your first customers, not investors"
    - Circle 2: Your Community — "Make a list of everyone... Contact them all personally"
    - Circle 3: Strangers (Cold Outreach) — "Cold emails, calls, messages — this works. It's how Gumroad grew."
  - `skills/first-customers/SKILL.md` line 33: Concrete example of Sahil's cold email that built Gumroad
  - `skills/first-customers/SKILL.md` lines 39-46: "Sales is Not a Dirty Word" philosophy
  - `skills/first-customers/SKILL.md` lines 69-76: "Output" section with 5 concrete action items
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Installation via Claude Code marketplace or local clone
- **Wiki says:** Install via Claude Code marketplace with `/plugin marketplace add slavingia/skills` and `/plugin install minimalist-entrepreneur`, or by cloning locally to `~/.claude/plugins/skills`.
- **Source evidence:**
  - `README.md` lines 7-30: Two installation methods documented
  - `README.md` lines 9-11: Marketplace method: "`/plugin marketplace add slavingia/skills`" then "`/plugin install minimalist-entrepreneur`"
  - `README.md` lines 12-14: "That's it — Claude Code will fetch the repo and register all 10 skills automatically."
  - `README.md` lines 16-28: Alternative local clone method: `git clone https://github.com/slavingia/skills.git ~/.claude/plugins/skills` then `/plugin marketplace add ~/.claude/plugins/skills` and `/plugin install minimalist-entrepreneur`
  - Each skill follows the SKILL.md format with YAML frontmatter (name, description) compatible with Claude Code's plugin system
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 5 key claims from the slavinga-skills wiki have been verified against the source code:
- ✅ Minimalist Entrepreneur methodology: 10 skills based on the book by Sahil Lavingia confirmed
- ✅ Full journey coverage: All 10 skills present from find-community to minimalist-review
- ✅ MVP three-stage progression: Manual → Processized → Productized confirmed in SKILL.md
- ✅ Concentric circles sales strategy: Friends → Community → Cold Outreach confirmed in SKILL.md
- ✅ Claude Code marketplace install: Dual marketplace + local clone methods confirmed

## Related

- [[slavinga-skills]] -- Main wiki entry
- [[skills]] -- Agent skills catalog
- [[abvx-agent-skills]] -- ABVX agent skill pack
- [[reverse-skill]] -- Reverse engineering skills

## Cross-project

- [[skills.codegraph-verify]] -- Skills catalog codegraph verification
- [[abvx-agent-skills.codegraph-verify]] -- ABVX agent skills codegraph verification
- [[hermes-agent.codegraph-verify]] -- Hermes agent codegraph verification
