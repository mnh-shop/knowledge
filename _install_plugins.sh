#!/bin/bash
set -e

SMART_CONNECTIONS="brianpetro/obsidian-smart-connections"
INFRANODUS="noduslabs/infranodus-graph-view"

echo "=== Smart Connections ==="
TAG=$(curl -sL "https://api.github.com/repos/$SMART_CONNECTIONS/releases/latest" | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])")
echo "Latest tag: $TAG"

DIR="/Users/admin1/Documents/knowledge/.obsidian/plugins/smart-connections"
echo "Downloading to $DIR"
curl -sL "https://github.com/$SMART_CONNECTIONS/releases/download/$TAG/main.js" -o "$DIR/main.js"
curl -sL "https://github.com/$SMART_CONNECTIONS/releases/download/$TAG/manifest.json" -o "$DIR/manifest.json"
curl -sL "https://github.com/$SMART_CONNECTIONS/releases/download/$TAG/styles.css" -o "$DIR/styles.css"
echo "Done"

echo ""
echo "=== InfraNodus Graph View ==="
TAG=$(curl -sL "https://api.github.com/repos/$INFRANODUS/releases/latest" | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])")
echo "Latest tag: $TAG"

DIR="/Users/admin1/Documents/knowledge/.obsidian/plugins/infranodus-graph-view"
echo "Downloading to $DIR"
curl -sL "https://github.com/$INFRANODUS/releases/download/$TAG/main.js" -o "$DIR/main.js"
curl -sL "https://github.com/$INFRANODUS/releases/download/$TAG/manifest.json" -o "$DIR/manifest.json"
curl -sL "https://github.com/$INFRANODUS/releases/download/$TAG/styles.css" -o "$DIR/styles.css" || echo "No styles.css"
echo "Done"

echo ""
echo "=== Verification ==="
echo "smart-connections/:"
ls -la /Users/admin1/Documents/knowledge/.obsidian/plugins/smart-connections/
echo ""
echo "infranodus-graph-view/:"
ls -la /Users/admin1/Documents/knowledge/.obsidian/plugins/infranodus-graph-view/
