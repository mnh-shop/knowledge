#!/usr/bin/env python3
"""Add sources/raw/codegraph references to files missing them."""
import os

BASE = "/Users/admin1/Documents/knowledge"

MISSING = {
    'buildah': [
        'domains/architecture/buildah-architecture.md',
        'domains/deployment/buildah-deployment.md',
    ],
    'crun-vm': [
        'domains/architecture/crun-vm-architecture.md',
        'domains/deployment/crun-vm-deployment.md',
    ],
    'sec-af': [
        'domains/architecture/sec-af-architecture.md',
        'assets/agent-profiles/sec-af-profile.md',
    ],
    'swe-af': [
        'domains/architecture/swe-af-architecture.md',
        'assets/agent-profiles/swe-af-profile.md',
    ],
    'af-reactive-atlas-mongodb': [
        'domains/architecture/af-reactive-atlas-mongodb-architecture.md',
        'assets/agent-profiles/af-reactive-atlas-mongodb-profile.md',
    ],
    'openclaw': [
        'domains/deployment/openclaw-deployment.md',
    ],
    'sablier': [
        'domains/deployment/sablier-deployment.md',
        'assets/deployment/sablier-quadlet.md',
    ],
    'hermes-agent': [
        'assets/deployment/hermes-agent-quadlet.md',
    ],
}

def human_size(path):
    if os.path.exists(path):
        size = 0
        if os.path.isfile(path):
            size = os.path.getsize(path)
        elif os.path.isdir(path):
            for dp, dn, fn in os.walk(path):
                for f in fn:
                    fp = os.path.join(dp, f)
                    try:
                        size += os.path.getsize(fp)
                    except:
                        pass
        if size > 100 * 1024 * 1024:
            return f" ({size // 1024 // 1024}MB DB)"
        elif size > 0:
            return f" ({size // 1024 // 1024}MB)"
    return ""

def add_ref(path_rel, project):
    path = os.path.join(BASE, path_rel)
    if not os.path.exists(path):
        print(f"SKIP: {path} not found")
        return
    with open(path) as f:
        content = f.read()
    if 'sources/' in content:
        print(f"SKIP: {path_rel} already has sources/ ref")
        return
    lines = content.split('\n')
    fm_count = 0
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.strip() == '---':
            fm_count += 1
            if fm_count == 2:
                insert_pos = i + 1
                break
    for i in range(insert_pos, len(lines)):
        if lines[i].startswith('# '):
            insert_pos = i + 1
            break
    # Build size strings
    raw_path_rel = f'raw/{project}/{project}.xml'
    raw_path = os.path.join(BASE, raw_path_rel)
    raw_extra = human_size(raw_path)
    cg_path = os.path.join(BASE, f'graphs/{project}/.codegraph/')
    cg_extra = human_size(cg_path)
    ref_block = f'\n**Source:** `sources/{project}/`\n**Raw:** `{raw_path_rel}`{raw_extra}\n**Codegraph:** `graphs/{project}/`{cg_extra}\n'
    new_content = '\n'.join(lines[:insert_pos]) + ref_block + '\n'.join(lines[insert_pos:])
    with open(path, 'w') as f:
        f.write(new_content)
    print(f"+ {path_rel}")

for project, files in MISSING.items():
    for f in files:
        add_ref(f, project)
print("DONE")
