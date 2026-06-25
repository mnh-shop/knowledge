#!/bin/bash
# Validate markdown files in the knowledge base for common issues.
# Checks: unclosed code fences, empty/minimal files, frontmatter completeness.
# Exit 0 if all checks pass, 1 if any issues found.

set -u

KNOWLEDGE_ROOT="/Users/admin1/Documents/knowledge"
EXCLUDE_DIRS=("sources" ".git" ".claude")
ERRORS=0

# Build exclusion flags for find
EXCLUDE_FLAGS=()
for d in "${EXCLUDE_DIRS[@]}"; do
    EXCLUDE_FLAGS+=( -not -path "${KNOWLEDGE_ROOT}/${d}/*" )
done

echo "=== Validation: Markdown quality checks ==="
echo ""

# ---------------------------------------------------------------
# Check 1: Unclosed code fences (odd count of ```)
# ---------------------------------------------------------------
echo "--- Check 1: Unclosed code fences ---"
echo ""
FENCE_ERRORS=0
while IFS= read -r -d '' md_file; do
    count=$(grep -c '^```' "$md_file" 2>/dev/null || echo 0)
    if (( count % 2 != 0 )); then
        echo "  UNCLOSED: ${md_file#${KNOWLEDGE_ROOT}/} (${count} fence markers, expected even number)"
        FENCE_ERRORS=$((FENCE_ERRORS + 1))
    fi
done < <(find "$KNOWLEDGE_ROOT" -name "*.md" "${EXCLUDE_FLAGS[@]}" -print0)

if (( FENCE_ERRORS == 0 )); then
    echo "  OK: No unclosed code fences found."
else
    echo "  Found ${FENCE_ERRORS} file(s) with unclosed code fences."
    ERRORS=$((ERRORS + FENCE_ERRORS))
fi
echo ""

# ---------------------------------------------------------------
# Check 2: Minimal content (files under 50 bytes are suspicious)
# ---------------------------------------------------------------
echo "--- Check 2: Minimal content check (>50 bytes) ---"
echo ""
SIZE_ERRORS=0
while IFS= read -r -d '' md_file; do
    size=$(wc -c < "$md_file" 2>/dev/null || echo 0)
    if (( size < 50 )); then
        echo "  TOO_SMALL: ${md_file#${KNOWLEDGE_ROOT}/} (${size} bytes)"
        SIZE_ERRORS=$((SIZE_ERRORS + 1))
    fi
done < <(find "$KNOWLEDGE_ROOT" -name "*.md" "${EXCLUDE_FLAGS[@]}" -print0)

if (( SIZE_ERRORS == 0 )); then
    echo "  OK: All files have adequate content."
else
    echo "  Found ${SIZE_ERRORS} file(s) with insufficient content."
    ERRORS=$((ERRORS + SIZE_ERRORS))
fi
echo ""

# ---------------------------------------------------------------
# Check 3: Frontmatter completeness (name and description fields)
# ---------------------------------------------------------------
echo "--- Check 3: Frontmatter completeness (name + description) ---"
echo ""
FM_ERRORS=0
while IFS= read -r -d '' md_file; do
    first_line=$(head -1 "$md_file" 2>/dev/null)
    if [[ "$first_line" == "---" ]]; then
        has_name=false
        has_desc=false
        # Read until closing ---
        while IFS= read -r line; do
            if [[ "$line" == "---" ]]; then
                break
            fi
            if [[ "$line" =~ ^name: ]]; then
                has_name=true
            fi
            if [[ "$line" =~ ^description: ]]; then
                has_desc=true
            fi
        done < <(tail -n +2 "$md_file" 2>/dev/null)
        if ! $has_name || ! $has_desc; then
            missing=""
            $has_name || missing+=" name"
            $has_desc || missing+=" description"
            echo "  MISSING${missing}: ${md_file#${KNOWLEDGE_ROOT}/}"
            FM_ERRORS=$((FM_ERRORS + 1))
        fi
    fi
done < <(find "$KNOWLEDGE_ROOT" -name "*.md" "${EXCLUDE_FLAGS[@]}" -print0)

if (( FM_ERRORS == 0 )); then
    echo "  OK: All files with frontmatter have name and description."
else
    echo "  Found ${FM_ERRORS} file(s) with incomplete frontmatter."
    ERRORS=$((ERRORS + FM_ERRORS))
fi
echo ""

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
echo "=== Summary ==="
if (( ERRORS == 0 )); then
    echo "SUCCESS: All markdown validation checks passed."
    exit 0
else
    echo "FAILURE: ${ERRORS} issue(s) found across all checks."
    exit 1
fi
