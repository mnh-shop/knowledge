#!/bin/bash
# Validate that all [[wikilinks]] in the knowledge base resolve to existing files.
# Exit 0 if all good, 1 if any broken links found.
#
# Compatible with macOS (bash 3.2, BSD grep).

set -u

KNOWLEDGE_ROOT="/Users/admin1/Documents/knowledge"

# Directories to exclude from the search
EXCLUDE_DIRS=("sources" ".git" ".claude")

# Known false positives — these look like wikilinks but are not
SKIP_LIST=(
  "...panel"
  "panel"
  "Deployment"
  "Architecture"
  "ACP"
  "MCP"
  "hermes-tweet"
  "docker"
  "links"
  "registry"
  "registry.mirror"
  "users"
)

# Resolution paths: each check is "dir/target.md"
RESOLVE_DIRS=(
  ""
  "wiki"
  "assets/agent-profiles"
  "assets/deployment"
  "assets/mcp-servers"
  "assets/acp-agents"
  "assets/api-clients"
  "assets/agent-skills"
  "domains/architecture"
  "domains/deployment"
  "domains/api"
  "domains/mcp"
  "domains/acp"
  "domains/integration-patterns"
  "integrations"
  "memory"
)

# Check if a value is in the skip list
is_skipped() {
    local target="$1"
    for skip in "${SKIP_LIST[@]}"; do
        if [[ "$target" == "$skip" ]]; then
            return 0
        fi
    done
    return 1
}

# Resolve a target against all known directories
resolve_target() {
    local target="$1"
    local check_path

    # Check with .md extension
    for dir in "${RESOLVE_DIRS[@]}"; do
        if [[ -z "$dir" ]]; then
            check_path="${KNOWLEDGE_ROOT}/${target}.md"
        else
            check_path="${KNOWLEDGE_ROOT}/${dir}/${target}.md"
        fi
        if [[ -f "$check_path" ]]; then
            return 0
        fi
    done

    # Check as bare file (no .md appended)
    for dir in "${RESOLVE_DIRS[@]}"; do
        if [[ -z "$dir" ]]; then
            check_path="${KNOWLEDGE_ROOT}/${target}"
        else
            check_path="${KNOWLEDGE_ROOT}/${dir}/${target}"
        fi
        if [[ -f "$check_path" ]]; then
            return 0
        fi
    done

    # Check as directory name
    for dir in "${RESOLVE_DIRS[@]}"; do
        if [[ -z "$dir" ]]; then
            check_path="${KNOWLEDGE_ROOT}/${target}"
        else
            check_path="${KNOWLEDGE_ROOT}/${dir}/${target}"
        fi
        if [[ -d "$check_path" ]]; then
            return 0
        fi
    done

    return 1
}

echo "Scanning for [[wikilinks]] in ${KNOWLEDGE_ROOT}..."
echo ""

# Build exclusion flags for find
EXCLUDE_FLAGS=()
for d in "${EXCLUDE_DIRS[@]}"; do
    EXCLUDE_FLAGS+=( -not -path "${KNOWLEDGE_ROOT}/${d}/*" )
done

# Temp files
ALL_LINKS_FILE=$(mktemp /tmp/wikilink-all.XXXXXX) || { echo "ERROR: mktemp failed"; exit 1; }

# Find all .md files (excluding sources/, .git/, .claude/),
# extract each [[wikilink]] or [[wikilink|label]], strip brackets and pipe parts.
# grep -oh: -o = only matching, -h = no filename prefix
find "$KNOWLEDGE_ROOT" -name "*.md" "${EXCLUDE_FLAGS[@]}" \
  -exec grep -oh '\[\[[^]]*\]\]' {} + \
  | sed -e 's/^\[\[//' -e 's/\]\]$//' -e 's/|.*//' \
  > "$ALL_LINKS_FILE"

# Deduplicate and strip whitespace
SORTED_LINKS_FILE=$(mktemp /tmp/wikilink-sorted.XXXXXX) || { echo "ERROR: mktemp failed"; exit 1; }
sed 's/^[[:space:]]*//;s/[[:space:]]*$//' "$ALL_LINKS_FILE" | sort -u > "$SORTED_LINKS_FILE"

# Count and process
TOTAL=0
BROKEN=0
BROKEN_FILE=$(mktemp /tmp/wikilink-broken.XXXXXX) || { echo "ERROR: mktemp failed"; exit 1; }

while IFS= read -r target; do
    [[ -z "$target" ]] && continue
    TOTAL=$((TOTAL + 1))

    # Skip false positives
    if is_skipped "$target"; then
        continue
    fi

    # URL-decode common percent-encoded characters
    decoded="$(printf '%b' "${target//%/\\x}" 2>/dev/null)"
    # Strip query params (e.g., "target?query=val" -> "target")
    decoded="${decoded%%\?*}"
    # Strip leading slash
    decoded="${decoded#/}"

    if ! resolve_target "$decoded"; then
        echo "$decoded" >> "$BROKEN_FILE"
        BROKEN=$((BROKEN + 1))
    fi
done < "$SORTED_LINKS_FILE"

echo "=== Results ==="
echo ""

if (( BROKEN == 0 )); then
    echo "SUCCESS: All ${TOTAL} wikilinks resolved."
    rm -f "$BROKEN_FILE" "$ALL_LINKS_FILE" "$SORTED_LINKS_FILE"
    exit 0
else
    echo "FAILURE: ${BROKEN} broken wikilink(s) found (out of ${TOTAL} total)."
    echo ""
    echo "Broken links:"
    sort -u "$BROKEN_FILE" | while IFS= read -r link; do
        echo "  [[${link}]]"
    done
    rm -f "$BROKEN_FILE" "$ALL_LINKS_FILE" "$SORTED_LINKS_FILE"
    exit 1
fi
