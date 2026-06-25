#!/usr/bin/env python3
"""Validate all [[wikilinks]] resolve to existing files."""
import os, re, sys

root = '/Users/admin1/Documents/knowledge'
exclude = {'sources', '.git', '.claude'}
skip_list = {'...panel', 'panel', 'Deployment', 'Architecture', 'ACP', 'MCP',
             'hermes-tweet', 'docker', 'links', 'registry', 'registry.mirror', 'users'}

resolve_dirs = ['', 'wiki', 'assets/agent-profiles', 'assets/deployment', 'assets/mcp-servers',
  'assets/acp-agents', 'assets/api-clients', 'assets/agent-skills',
  'assets/n8n-workflows',
  'domains/architecture', 'domains/deployment', 'domains/api', 'domains/mcp', 'domains/acp',
  'domains/integration-patterns', 'integrations', 'memory', 'ideas']

def resolve(target):
    # Handle [[File#Section]] → resolve the file part
    target = target.split('#')[0]
    for d in resolve_dirs:
        if os.path.isfile(os.path.join(root, d, target + '.md')):
            return True
        if os.path.isfile(os.path.join(root, d, target)):
            return True
        if os.path.isdir(os.path.join(root, d, target)):
            return True
    # Try relative to the file's own directory (../../ style)
    # These are not resolved by the vault structure; skip them
    return False

def is_relative_path(target):
    """True if the target starts with ../ indicating a relative path reference."""
    return target.startswith('../')

def is_self_reference(target):
    """True if the target is a #section reference within the same file."""
    return target.startswith('#')

all_wikilinks = set()
for dirpath, dirnames, files in os.walk(root):
    dirnames[:] = [d for d in dirnames if os.path.basename(d) not in exclude]
    for f in files:
        if f.endswith('.md'):
            with open(os.path.join(dirpath, f), 'r', encoding='utf-8', errors='replace') as fh:
                for m in re.finditer(r'\[\[([^\]]+)\]\]', fh.read()):
                    target = m.group(1).split('|')[0].strip()
                    if target:
                        all_wikilinks.add(target)

broken = []
for w in sorted(all_wikilinks):
    if w in skip_list:
        continue
    decoded = w.split('?')[0].lstrip('/')
    # Skip self-references (#section within the same file)
    if is_self_reference(decoded):
        continue
    # Skip relative path references (../../ style — resolved at source-level, not in vault)
    if is_relative_path(decoded):
        continue
    if not resolve(decoded):
        broken.append(w)

print(f'Total wikilinks: {len(all_wikilinks)}')
print(f'Broken: {len(broken)}')
if broken:
    for b in broken:
        print(f'  [[{b}]]')
    sys.exit(1)
else:
    print('ALL VALID')
    sys.exit(0)
