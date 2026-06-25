#!/usr/bin/env python3
import json, os, urllib.request, urllib.error

def get_latest_tag(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read().decode())
            return data['tag_name']
    except Exception as e:
        print(f"Error fetching {repo}: {e}")
        return None

def download_file(url, dest):
    print(f"  Downloading {url.split('/')[-1]}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"    -> {dest}")
    except Exception as e:
        print(f"    -> Error: {e}")

plugins = {
    "smart-connections": {
        "repo": "brianpetro/obsidian-smart-connections",
        "dir": ".obsidian/plugins/smart-connections"
    },
    "infranodus-graph-view": {
        "repo": "noduslabs/infranodus-graph-view",
        "dir": ".obsidian/plugins/infranodus-graph-view"
    }
}

base_dir = os.path.dirname(os.path.abspath(__file__))

for name, info in plugins.items():
    print(f"\n=== {name} ===")
    tag = get_latest_tag(info["repo"])
    if not tag:
        print(f"  Could not get tag for {info['repo']}")
        continue
    print(f"  Latest: {tag}")

    plugin_dir = os.path.join(base_dir, info["dir"])
    os.makedirs(plugin_dir, exist_ok=True)

    base_url = f"https://github.com/{info['repo']}/releases/download/{tag}"

    for fname in ["main.js", "manifest.json", "styles.css"]:
        dest = os.path.join(plugin_dir, fname)
        url = f"{base_url}/{fname}"
        download_file(url, dest)
