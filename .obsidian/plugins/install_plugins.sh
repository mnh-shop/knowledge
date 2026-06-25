#!/bin/bash
# Smart Connections plugin download
SC_REPO="brianpetro/obsidian-smart-connections"
SC_DIR="/Users/admin1/Documents/knowledge/.obsidian/plugins/smart-connections"

IN_REPO="noduslabs/infranodus-graph-view"
IN_DIR="/Users/admin1/Documents/knowledge/.obsidian/plugins/infranodus-graph-view"

echo "=== Smart Connections ==="
SC_TAG=$(curl -sL "https://api.github.com/repos/$SC_REPO/releases/latest" | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])")
echo "Latest: $SC_TAG"

curl -sL "https://github.com/$SC_REPO/releases/download/$SC_TAG/main.js" -o "$SC_DIR/main.js"
curl -sL "https://github.com/$SC_REPO/releases/download/$SC_TAG/manifest.json" -o "$SC_DIR/manifest.json"
curl -sL "https://github.com/$SC_REPO/releases/download/$SC_TAG/styles.css" -o "$SC_DIR/styles.css" || echo "No styles.css"

echo "=== InfraNodus Graph View ==="
IN_TAG=$(curl -sL "https://api.github.com/repos/$IN_REPO/releases/latest" | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])")
echo "Latest: $IN_TAG"

curl -sL "https://github.com/$IN_REPO/releases/download/$IN_TAG/main.js" -o "$IN_DIR/main.js"
curl -sL "https://github.com/$IN_REPO/releases/download/$IN_TAG/manifest.json" -o "$IN_DIR/manifest.json"
curl -sL "https://github.com/$IN_REPO/releases/download/$IN_TAG/styles.css" -o "$IN_DIR/styles.css" || echo "No styles.css"

echo "=== Verification ==="
ls -la "$SC_DIR/"
echo ""
ls -la "$IN_DIR/"
echo ""
echo "Done"
