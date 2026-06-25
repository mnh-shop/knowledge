"""Add capability tags to all .md files based on their content and location.
No API calls needed — deterministic mapping by directory + filename patterns."""

import os
import re

BASE = "/Users/admin1/Documents/knowledge"
EXCLUDE = {"sources", ".git", ".claude", "raw", "graphs", "node_modules", ".smart-env", ".obsidian", "tests"}

def glob_files():
    """Yield (relative_path, full_path) for all .md files."""
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, BASE)
                yield rel, full

def determine_capability_tags(rel_path, content):
    """Add capability tags based on file location and content hints."""
    tags = set()
    p = rel_path.lower()

    # Directory-based tags
    if "/architecture/" in p:
        tags.add("architecture")
    if "/deployment/" in p:
        tags.add("deployment")
    if "/api/" in p:
        tags.add("rest-api")
    if "/mcp/" in p:
        tags.add("mcp")
    if "/acp/" in p:
        tags.add("acp")

    # Asset subdirectory tags
    if "assets/deployment/" in p or "quadlet" in content.lower():
        tags.update(["quadlet", "systemd"])
    if "assets/mcp-servers/" in p:
        tags.add("mcp")
    if "assets/acp-agents/" in p:
        tags.add("acp")
    if "assets/agent-skills/" in p:
        tags.add("skills-platform")
    if "assets/agent-profiles/" in p:
        tags.add("agent-profile")
    if "assets/api-clients/" in p:
        tags.add("rest-api")
    if "assets/n8n-workflows/" in p:
        tags.update(["automation", "workflow"])
    if "integrations/" in p:
        tags.update(["integration", "architecture"])

    # Content-based tags
    c_lower = content.lower()
    if "docker" in c_lower:
        tags.add("docker")
    if "podman" in c_lower or "quadlet" in c_lower:
        tags.add("container")
    if "nix" in c_lower and ("nix-podman" in c_lower or "home-manager" in c_lower or "nixos" in c_lower):
        tags.add("nix")
    if "mcp" in c_lower and "mcp" not in tags:
        tags.add("mcp")
    if "acp" in c_lower and "acp" not in tags:
        tags.add("acp")
    if "webhook" in c_lower:
        tags.add("webhook")
    if "cli" in c_lower and "cli" not in tags and "rest-api" not in tags:
        tags.add("cli")
    if "messaging" in c_lower or "multi-platform" in c_lower or "telegram" in c_lower or "discord" in c_lower or "slack" in c_lower:
        tags.add("messaging")
    if "orchestrat" in c_lower:
        tags.add("orchestration")
    if "monitor" in c_lower:
        tags.add("monitoring")
    if "secur" in c_lower or "iam" in c_lower or "did" in c_lower:
        tags.add("security")
    if "automation" in c_lower:
        tags.add("automation")
    if "storage" in c_lower or "database" in c_lower or "postgres" in c_lower:
        tags.add("storage")
    if "optimiz" in c_lower:
        tags.add("optimization")
    if "ai-llm" in c_lower or "llm" in c_lower or "agent" in c_lower:
        tags.add("ai-llm")
    if "git" in c_lower:
        tags.add("git")
    if "virtual" in c_lower or "vm" in c_lower or "kvm" in c_lower:
        tags.add("virtualization")

    # Specific project/content patterns
    if "bootc" in c_lower:
        tags.add("bootc")
    if "terraform" in c_lower:
        tags.add("terraform")
    if "ansible" in c_lower:
        tags.add("ansible")
    if "event" in c_lower and "bus" in c_lower:
        tags.add("event-bus")
    if "plugin" in c_lower or "skill" in c_lower:
        tags.add("plugin-sdk")
    if "dashboard" in c_lower:
        tags.add("dashboard")
    if "desktop" in c_lower or "tauri" in c_lower:
        tags.add("desktop-app")

    # Index/README/catalog files
    if p.endswith("index.md") or p.endswith("readme.md"):
        tags.add("documentation")

    # memory/
    if p.startswith("memory/"):
        tags.add("ai-llm")

    return sorted(tags)


def read_frontmatter(content):
    """Return (frontmatter_lines, body_lines, has_fm) or None."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_lines = parts[1].split("\n")
            body = parts[2]
            return fm_lines, body, True
    return None, content, False


def write_frontmatter(fm_lines, body):
    """Reconstruct file from frontmatter + body."""
    fm = "\n".join(fm_lines)
    return f"---{fm}---{body}"


def update_tags_in_file(rel_path, full_path):
    with open(full_path) as f:
        content = f.read()

    result = read_frontmatter(content)
    if result is None:
        print(f"  SKIP (no frontmatter): {rel_path}")
        return False  # file has no frontmatter

    fm_lines, body, has_fm = result
    if not has_fm:
        print(f"  SKIP (no --- markers): {rel_path}")
        return False

    # Find existing tags line
    tags_idx = None
    existing_tags = []
    for i, line in enumerate(fm_lines):
        if line.startswith("tags:"):
            tags_idx = i
            # Extract tags from [tag1, tag2, ...]
            m = re.search(r'\[(.*?)\]', line)
            if m:
                existing_tags = [t.strip() for t in m.group(1).split(",") if t.strip()]
            break

    if tags_idx is None:
        print(f"  SKIP (no tags line): {rel_path}")
        return False

    # Add capability tags
    capability = determine_capability_tags(rel_path, content)
    current_set = set(existing_tags)
    added = [t for t in capability if t not in current_set]
    if not added:
        return False  # no new tags to add

    new_tags = existing_tags + added
    # Build the new tags line
    new_tag_line = f"tags: [{', '.join(new_tags)}]"
    fm_lines[tags_idx] = new_tag_line

    new_content = write_frontmatter(fm_lines, body)
    with open(full_path, "w") as f:
        f.write(new_content)

    print(f"  +{', '.join(added)}  {rel_path}")
    return True


def main():
    updated = 0
    for rel_path, full_path in sorted(glob_files()):
        if update_tags_in_file(rel_path, full_path):
            updated += 1
    print(f"\nUpdated tags in {updated} files.")


if __name__ == "__main__":
    main()
