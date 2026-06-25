"""Clean up auto-added noise tags and re-apply with smarter context-aware matching.

Strategy:
1. For each file, get its ORIGINAL tags (from git HEAD~2 for existing files, or empty for new)
2. Strip the 8 noise tags from files where they were auto-added
3. Compute new capability tags with context-aware matching
4. Add new tags to the original set
5. Write final tag line
"""
import os
import re
import subprocess

BASE = "/Users/admin1/Documents/knowledge"
EXCLUDE = {"sources", ".git", ".claude", "raw", "graphs", "node_modules", ".smart-env", ".obsidian", "tests"}

# Tags that were potentially auto-added by the dumb keyword script
AUTO_NUISANCE = {'ai-llm', 'automation', 'cli', 'container', 'docker', 'git', 'orchestration', 'security'}


def glob_files():
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                yield os.path.relpath(os.path.join(root, f), BASE)


def get_original_tags(rel_path):
    """Get tags from git HEAD~2 (the commit before the first tag run)."""
    try:
        old = subprocess.run(
            ['git', 'show', f'HEAD~2:{rel_path}'],
            capture_output=True, text=True, cwd=BASE
        ).stdout
    except:
        old = ''
    if not old or not old.startswith('---'):
        return set()
    parts = old.split('---', 2)
    if len(parts) < 3:
        return set()
    m = re.search(r'tags: \[([^\]]+)\]', parts[1])
    if not m:
        return set()
    return set(x.strip() for x in m.group(1).split(','))


def extract_contexts(content):
    """Return (headings_text, bold_text, frontmatter_text, body_lower)."""
    parts = content.split("---", 2)
    if len(parts) < 3:
        return "", "", "", content.lower()
    fm = parts[1]
    body = parts[2]

    headings = re.findall(r'^(#{1,6})\s+(.+)', body, re.MULTILINE)
    headings_text = " ".join(h[1] for h in headings).lower()

    bold = re.findall(r'\*\*(.+?)\*\*', body)
    bold_text = " ".join(bold).lower()

    fm_name = ""
    fm_desc = ""
    for line in fm.split("\n"):
        if line.startswith("name:"):
            fm_name = line.split(":", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            fm_desc = line.split(":", 1)[1].strip().strip('"').strip("'")

    return headings_text, bold_text, f"{fm_name} {fm_desc}".lower(), body.lower()


def kw_in_context(keyword, headings, bold, frontmatter, body_lower):
    kw = keyword.lower()
    if kw in headings:
        return True
    if kw in frontmatter:
        return True
    if kw in bold:
        return True
    if body_lower.count(kw) >= 3:
        return True
    return False


def compute_new_tags(rel_path, content):
    """Context-aware capability tag determination."""
    tags = set()
    p = rel_path.lower()

    # ── Directory-based (always correct) ──
    if "/architecture/" in p:    tags.add("architecture")
    if "/deployment/" in p:      tags.add("deployment")
    if "/api/" in p:             tags.add("rest-api")
    if "/mcp/" in p:             tags.add("mcp")
    if "/acp/" in p:             tags.add("acp")

    # ── Asset directories ──
    if "assets/deployment/" in p or "quadlet" in content.lower():
        tags.update(["quadlet", "systemd"])
    if "assets/mcp-servers/" in p:      tags.add("mcp")
    if "assets/acp-agents/" in p:       tags.add("acp")
    if "assets/agent-skills/" in p:     tags.add("skills-platform")
    if "assets/agent-profiles/" in p:   tags.add("agent-profile")
    if "assets/api-clients/" in p:      tags.add("rest-api")
    if "assets/n8n-workflows/" in p:    tags.update(["automation", "workflow", "n8n"])
    if "integrations/" in p:            tags.update(["integration", "architecture"])

    if p.endswith("index.md") or p.endswith("readme.md"):
        tags.add("documentation")
    if p.startswith("memory/"):
        tags.add("ai-llm")

    # Skip content matching for n8n catalog files
    if "assets/n8n-workflows/" in p:
        return tags

    # ── Context-aware content matching ──
    headings, bold, frontmatter, body_lower = extract_contexts(content)

    if kw_in_context("docker", headings, bold, frontmatter, body_lower):
        tags.add("docker")
    if kw_in_context("podman", headings, bold, frontmatter, body_lower):
        tags.add("podman")
        tags.add("container")

    if "quadlet" in body_lower and "quadlet" not in tags:
        tags.update(["quadlet", "systemd"])
    if kw_in_context("container", headings, bold, frontmatter, body_lower):
        tags.add("container")

    nix_extra = "nix-podman" in body_lower or "home-manager" in body_lower or "nixos" in body_lower
    if kw_in_context("nix", headings, bold, frontmatter, body_lower) and nix_extra:
        tags.add("nix")

    if kw_in_context("messaging", headings, bold, frontmatter, body_lower):
        tags.add("messaging")
    for plat in ["telegram", "discord", "slack"]:
        if kw_in_context(plat, headings, bold, frontmatter, body_lower):
            tags.add("messaging")
    if kw_in_context("multi-platform", headings, bold, frontmatter, body_lower):
        tags.add("messaging")

    if kw_in_context("cli", headings, bold, frontmatter, body_lower):
        tags.add("cli")
    if kw_in_context("webhook", headings, bold, frontmatter, body_lower):
        tags.add("webhook")
    if "mcp" not in tags and kw_in_context("mcp", headings, bold, frontmatter, body_lower):
        tags.add("mcp")
    if "acp" not in tags and kw_in_context("acp", headings, bold, frontmatter, body_lower):
        tags.add("acp")
    if kw_in_context("orchestrat", headings, bold, frontmatter, body_lower):
        tags.add("orchestration")
    if kw_in_context("monitor", headings, bold, frontmatter, body_lower):
        tags.add("monitoring")
    if kw_in_context("secur", headings, bold, frontmatter, body_lower) or \
       kw_in_context("iam", headings, bold, frontmatter, body_lower):
        tags.add("security")
    if kw_in_context("automation", headings, bold, frontmatter, body_lower):
        tags.add("automation")
    if kw_in_context("storage", headings, bold, frontmatter, body_lower) or \
       kw_in_context("database", headings, bold, frontmatter, body_lower) or \
       kw_in_context("postgres", headings, bold, frontmatter, body_lower):
        tags.add("storage")
    if kw_in_context("optimiz", headings, bold, frontmatter, body_lower):
        tags.add("optimization")

    # AI/LLM — strong signals only
    if kw_in_context("ai-llm", headings, bold, frontmatter, body_lower) or \
       kw_in_context("llm", headings, bold, frontmatter, body_lower) or \
       kw_in_context("artificial intelligence", headings, bold, frontmatter, body_lower):
        tags.add("ai-llm")
    if "agent" in headings or "agent" in bold or "agent" in frontmatter:
        tags.add("ai-llm")

    if kw_in_context("git", headings, bold, frontmatter, body_lower):
        tags.add("git")
    if kw_in_context("virtual", headings, bold, frontmatter, body_lower) or \
       kw_in_context("vm", headings, bold, frontmatter, body_lower) or \
       kw_in_context("kvm", headings, bold, frontmatter, body_lower):
        tags.add("virtualization")
    if kw_in_context("bootc", headings, bold, frontmatter, body_lower):
        tags.add("bootc")
    if kw_in_context("terraform", headings, bold, frontmatter, body_lower):
        tags.add("terraform")
    if kw_in_context("ansible", headings, bold, frontmatter, body_lower):
        tags.add("ansible")
    if "event" in headings and "bus" in headings:
        tags.add("event-bus")
    elif kw_in_context("event", headings, bold, frontmatter, body_lower) and \
         kw_in_context("bus", headings, bold, frontmatter, body_lower):
        tags.add("event-bus")
    if kw_in_context("plugin", headings, bold, frontmatter, body_lower) or \
       kw_in_context("skill", headings, bold, frontmatter, body_lower):
        tags.add("plugin-sdk")
    if kw_in_context("dashboard", headings, bold, frontmatter, body_lower):
        tags.add("dashboard")
    if kw_in_context("desktop", headings, bold, frontmatter, body_lower) or \
       kw_in_context("tauri", headings, bold, frontmatter, body_lower):
        tags.add("desktop-app")

    return tags


def process_file(rel_path, dry_run=False):
    full_path = os.path.join(BASE, rel_path)
    with open(full_path) as f:
        content = f.read()

    if not content.startswith("---"):
        return "no frontmatter", None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return "no markers", None

    fm_lines = parts[1].split("\n")
    body = parts[2]

    tags_idx = None
    current_tags = []
    for i, line in enumerate(fm_lines):
        if line.startswith("tags:"):
            tags_idx = i
            m = re.search(r'\[(.*?)\]', line)
            if m:
                current_tags = [t.strip() for t in m.group(1).split(",") if t.strip()]
            break

    if tags_idx is None:
        return "no tags line", None

    # Get original tags (pre-tag-script)
    original_tags = get_original_tags(rel_path)
    # For new files (no git history), treat current as original (minus auto-added noise)
    if not original_tags:
        original_tags = set(current_tags) - AUTO_NUISANCE

    # Compute new capability tags with context-aware logic
    new_capability = compute_new_tags(rel_path, content)

    # Final tag set = original project tags + new context-aware capability tags
    final_tags = original_tags | new_capability
    final_sorted = sorted(final_tags)

    if set(current_tags) == final_tags:
        return "unchanged", None

    if dry_run:
        old_noise = set(current_tags) - original_tags
        added = final_tags - set(current_tags)
        removed = set(current_tags) - final_tags
        return "would_change", {"old": current_tags, "new": final_sorted, "removed": sorted(removed), "added": sorted(added), "noise": sorted(old_noise)}

    new_tag_line = f"tags: [{', '.join(final_sorted)}]"
    fm_lines[tags_idx] = new_tag_line
    new_content = "\n".join(fm_lines).join(["---", "---"]) + body

    with open(full_path, "w") as f:
        f.write(new_content)

    old_noise = set(current_tags) - original_tags
    added = final_tags - set(current_tags)
    removed = set(current_tags) - final_tags
    return "updated", {"removed": sorted(removed), "added": sorted(added), "noise_stripped": sorted(old_noise)}


def main():
    import sys
    dry_run = "--dry-run" in sys.argv

    results = {"updated": 0, "unchanged": 0, "skipped": 0}
    for rel_path in sorted(glob_files()):
        status, info = process_file(rel_path, dry_run)
        if dry_run and status == "would_change":
            print(f"  {rel_path}")
            if info["removed"]:
                print(f"    remove: {', '.join(info['removed'])}")
            if info["added"]:
                print(f"    add:    {', '.join(info['added'])}")
            results["updated"] += 1
        elif status == "updated":
            print(f"  {rel_path}")
            if info["noise_stripped"]:
                print(f"    noise stripped: {', '.join(info['noise_stripped'])}")
            if info["added"]:
                print(f"    added: {', '.join(info['added'])}")
            results["updated"] += 1
        elif status == "unchanged":
            results["unchanged"] += 1
        else:
            results["skipped"] += 1

    print(f"\nResults: {results['updated']} updated, {results['unchanged']} unchanged, {results['skipped']} skipped")
    if dry_run:
        print("(DRY RUN — no files changed)")


if __name__ == "__main__":
    main()
