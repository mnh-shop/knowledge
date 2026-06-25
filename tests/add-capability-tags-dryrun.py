"""Dry-run: print what capability tags would be added without writing files."""
import os
import re

BASE = "/Users/admin1/Documents/knowledge"
EXCLUDE = {"sources", ".git", ".claude", "raw", "graphs", "node_modules", ".smart-env", ".obsidian", "tests"}

def glob_files():
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, BASE)
                yield rel, full

def determine_capability_tags(rel_path, content):
    tags = set()
    p = rel_path.lower()
    if "/architecture/" in p: tags.add("architecture")
    if "/deployment/" in p: tags.add("deployment")
    if "/api/" in p: tags.add("rest-api")
    if "/mcp/" in p: tags.add("mcp")
    if "/acp/" in p: tags.add("acp")
    if "assets/deployment/" in p or "quadlet" in content.lower(): tags.update(["quadlet", "systemd"])
    if "assets/mcp-servers/" in p: tags.add("mcp")
    if "assets/acp-agents/" in p: tags.add("acp")
    if "assets/agent-skills/" in p: tags.add("skills-platform")
    if "assets/agent-profiles/" in p: tags.add("agent-profile")
    if "assets/api-clients/" in p: tags.add("rest-api")
    if "assets/n8n-workflows/" in p: tags.update(["automation", "workflow"])
    if "integrations/" in p: tags.update(["integration", "architecture"])
    c_lower = content.lower()
    if "docker" in c_lower: tags.add("docker")
    if "podman" in c_lower or "quadlet" in c_lower: tags.add("container")
    if "nix" in c_lower and ("nix-podman" in c_lower or "home-manager" in c_lower or "nixos" in c_lower): tags.add("nix")
    if "mcp" in c_lower and "mcp" not in tags: tags.add("mcp")
    if "acp" in c_lower and "acp" not in tags: tags.add("acp")
    if "webhook" in c_lower: tags.add("webhook")
    if "cli" in c_lower and "cli" not in tags and "rest-api" not in tags: tags.add("cli")
    if "messaging" in c_lower or "multi-platform" in c_lower or "telegram" in c_lower or "discord" in c_lower or "slack" in c_lower: tags.add("messaging")
    if "orchestrat" in c_lower: tags.add("orchestration")
    if "monitor" in c_lower: tags.add("monitoring")
    if "secur" in c_lower or "iam" in c_lower or "did" in c_lower: tags.add("security")
    if "automation" in c_lower: tags.add("automation")
    if "storage" in c_lower or "database" in c_lower or "postgres" in c_lower: tags.add("storage")
    if "optimiz" in c_lower: tags.add("optimization")
    if "ai-llm" in c_lower or "llm" in c_lower or "agent" in c_lower: tags.add("ai-llm")
    if "git" in c_lower: tags.add("git")
    if "virtual" in c_lower or "vm" in c_lower or "kvm" in c_lower: tags.add("virtualization")
    if "bootc" in c_lower: tags.add("bootc")
    if "terraform" in c_lower: tags.add("terraform")
    if "ansible" in c_lower: tags.add("ansible")
    if "event" in c_lower and "bus" in c_lower: tags.add("event-bus")
    if "plugin" in c_lower or "skill" in c_lower: tags.add("plugin-sdk")
    if "dashboard" in c_lower: tags.add("dashboard")
    if "desktop" in c_lower or "tauri" in c_lower: tags.add("desktop-app")
    if p.endswith("index.md") or p.endswith("readme.md"): tags.add("documentation")
    if p.startswith("memory/"): tags.add("ai-llm")
    return sorted(tags)

def main():
    changes = []
    for rel_path, full_path in sorted(glob_files()):
        with open(full_path) as f:
            content = f.read()
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        fm_lines = parts[1].split("\n")
        body = parts[2]
        existing_tags = []
        tags_line = None
        for line in fm_lines:
            if line.startswith("tags:"):
                tags_line = line
                m = re.search(r'\[(.*?)\]', line)
                if m:
                    existing_tags = [t.strip() for t in m.group(1).split(",") if t.strip()]
                break
        if not tags_line:
            continue
        capability = determine_capability_tags(rel_path, content)
        added = [t for t in capability if t not in set(existing_tags)]
        if added:
            changes.append((rel_path, added, set(existing_tags) | set(capability)))
    for c in changes:
        print(f"+{', '.join(c[1])}  {c[0]}")
    print(f"\nTotal: {len(changes)} files need tag updates")

if __name__ == "__main__":
    main()
