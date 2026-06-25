#!/usr/bin/env python3
"""Download Obsidian community plugins."""
import json, os, sys, urllib.request, urllib.error

plugins = {
    "smart-connections": "brianpetro/obsidian-smart-connections",
    "infranodus-graph-view": "noduslabs/infranodus-graph-view",
}

base = "/Users/admin1/Documents/knowledge/.obsidian/plugins"

for name, repo in plugins.items():
    print(f"\n=== {name} ===")
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "python"})
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        tag = data["tag_name"]
        print(f"  Latest: {tag}")

        d = os.path.join(base, name)
        for fname in ["manifest.json", "main.js", "styles.css"]:
            raw_url = f"https://raw.githubusercontent.com/{repo}/{tag}/{fname}"
            try:
                dl = urllib.request.urlopen(urllib.request.Request(raw_url, headers={"User-Agent": "python"}))
                content = dl.read()
                with open(os.path.join(d, fname), "wb") as fh:
                    fh.write(content)
                print(f"  Downloaded {fname} ({len(content)} bytes)")
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    print(f"  {fname}: HTTP {e.code}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n=== Verify ===")
for name in plugins:
    d = os.path.join(base, name)
    for f in os.listdir(d):
        fp = os.path.join(d, f)
        print(f"  {name}/{f} ({os.path.getsize(fp)} bytes)")
