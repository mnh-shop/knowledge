---
tags: [ai-llm, cli, git, plugin-sdk, security]
  - pydantic-ai
  - agent-skills
  - python-library
  - agent-capabilities
  - tool-calling
---

# pydantic-ai-skills

A lightweight, type-safe Python library (Python >=3.10) that implements the [Agent Skills specification](https://agentskills.io/home) for the Pydantic AI ecosystem. It provides a standardized, composable framework for building and managing modular **Agent Skills** -- collections of instructions, scripts, tools, and resources that enable AI agents to progressively discover, load, and execute specialized capabilities for domain-specific tasks.

- **Repository:** <https://github.com/dougtrajano/pydantic-ai-skills>
- **Author:** Douglas Trajano
- **Version:** 0.11.0
- **License:** MIT
- **Docs site:** <https://dougtrajano.github.io/pydantic-ai-skills>

## Architecture

The library is organized into several layers:

```
pydantic_ai_skills/
  __init__.py       # Public API surface
  _parsing.py       # SKILL.md parsing & validation helpers
  types.py          # Core dataclasses: Skill, SkillResource, SkillScript, SkillWrapper
  directory.py      # Filesystem discovery: SkillsDirectory, discover_skills()
  local.py          # Local execution: LocalSkillScriptExecutor, CallableSkillScriptExecutor, File-based types
  toolset.py        # Primary integration: SkillsToolset (FunctionToolset subclass)
  capability.py     # Capability API: SkillsCapability (AbstractCapability wrapper)
  registries/
    __init__.py
    _base.py        # SkillRegistry ABC
    git.py          # GitSkillsRegistry
    s3.py           # S3SkillsRegistry
    _copy.py        # copy_skill_directory helper
    combined.py     # CombinedRegistry
    filtered.py     # FilteredRegistry
    prefixed.py     # PrefixedRegistry
    renamed.py      # RenamedRegistry
    wrapper.py      # WrapperRegistry (base delegation)
```

### Integration Modes

Two ways to integrate:

1. **`SkillsToolset`** (extends `pydantic_ai.toolsets.FunctionToolset`) -- Use with `toolsets=[...]` on the agent. Skills are exposed as agent-callable tools.
2. **`SkillsCapability`** (implements `pydantic_ai.capabilities.AbstractCapability`) -- Prefer this approach; uses the `capabilities=[...]` API and wraps an internal `SkillsToolset`.

Both paths are equivalent in behavior; `SkillsCapability` delegates entirely to `SkillsToolset`.

## Core Concepts

### Skills

A **Skill** is a named collection of instructions (content), optional resources, and optional scripts. Skills come from three sources:

| Source | Description | Priority |
|--------|-------------|----------|
| Programmatic | Defined in Python via `Skill(...)` dataclass or `@toolset.skill` decorator | Highest |
| Filesystem | `SKILL.md` files discovered by `SkillsDirectory` | Middle |
| Registry | Remote sources via `SkillRegistry` (Git, S3) | Lowest |

### The Four Agent Tools

When integrated, the toolset registers up to four tools the agent can call:

| Tool | Purpose |
|------|---------|
| `list_skills()` | List all available skills with descriptions |
| `load_skill(name)` | Load complete instructions for a skill |
| `read_skill_resource(name, resource)` | Read static/dynamic resource files |
| `run_skill_script(name, script, args)` | Execute a skill's script |

Any tool can be excluded via `exclude_tools=['run_skill_script']` for security.

### Progressive Disclosure

Skills follow a layered disclosure model to minimize context:

1. **Discovery** -- Skill names and descriptions injected into agent system prompt via `get_instructions(ctx)`
2. **Loading** -- Agent calls `load_skill(name)` to get full instructions when relevant
3. **Resources** -- Agent calls `read_skill_resource()` for supplementary files
4. **Execution** -- Agent calls `run_skill_script()` to execute scripts

## Types (`types.py`)

Core dataclasses:

- **`Skill`** -- name, description, content, license, compatibility, resources, scripts, uri, metadata
  - `Skill.from_file(path, validate, script_executor)` -- Load from SKILL.md
  - `Skill.resource(func, ...)` -- Decorator to register a callable resource
  - `Skill.script(func, ...)` -- Decorator to register a callable script
- **`SkillResource`** -- name, description, content (static), function (dynamic), takes_ctx, function_schema, uri
- **`SkillScript`** -- name, description, function, takes_ctx, function_schema, uri, skill_name
- **`SkillWrapper[DepsT]`** -- Generic wrapper for `@toolset.skill` decorator, with `.resource()` and `.script()` decorators and `.to_skill()` converter
- **`normalize_skill_name(name)`** -- Converts underscore-separated names to lowercase-hyphenated format

### Skill Naming Rules

Names must match `^[a-z0-9]+(-[a-z0-9]+)*$`, max 64 characters, cannot contain reserved words `anthropic` or `claude`.

## Filesystem Discovery (`directory.py`)

### SkillsDirectory

```python
SkillsDirectory(path="./skills", validate=True, max_depth=3, script_executor=None)
```

Searches for `SKILL.md` files up to configurable depth (default 3), loads their frontmatter + body, and discovers:
- **Resources** -- Text files with extensions `.md`, `.json`, `.yaml`, `.yml`, `.csv`, `.xml`, `.txt` (excluding SKILL.md)
- **Scripts** -- Executables with extensions `.py`, `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1`, `.bat`, `.cmd` or files with execute bit

### SKILL.md Format

```yaml
---
name: my-skill
description: A brief description
version: 1.0.0  # Optional
license: MIT    # Optional
compatibility: python>=3.10  # Optional, max 500 chars
---
# Instructions

Markdown content for the agent.
```

Required frontmatter fields: `name`, `description` (max 1024 chars).

## Execution (`local.py`)

### LocalSkillScriptExecutor

Executes file-based scripts as subprocesses with:
- **Timeout** -- Default 30 seconds, kills process group
- **Shebang-first dispatch** -- Uses `#!` line first, falls back to suffix-based interpreter
- **Named arguments** -- Dict args become `--key value` CLI flags
- **Env vars** -- Static `env_vars` dict + dynamic `context_env_vars_extractor` callable
- **Async** -- Uses `anyio.open_process` with concurrent stdout/stderr draining

```python
LocalSkillScriptExecutor(python_executable=None, timeout=30, env_vars=None, context_env_vars_extractor=None)
```

### CallableSkillScriptExecutor

Wraps an arbitrary Python callable as a script executor:

```python
CallableSkillScriptExecutor(func=my_async_func)
```

### FileBased Types

- **`FileBasedSkillResource`** -- Extends `SkillResource`, loads from disk; JSON/YAML parsed, others as text
- **`FileBasedSkillScript`** -- Extends `SkillScript`, executes via executor

## Toolset (`toolset.py`)

### SkillsToolset

The primary integration class, extending `FunctionToolset[Any]`:

```python
SkillsToolset(
    skills=None,               # Pre-loaded Skill objects
    directories=None,          # Directories or SkillsDirectory instances
    registries=None,           # SkillRegistry instances
    validate=True,             # Validate skill structure
    max_depth=3,               # Max discovery depth (None = unlimited)
    id=None,                   # Unique toolset identifier
    instruction_template=None, # Custom template with {skills_list}
    exclude_tools=None,        # Tools to exclude from registration
    auto_reload=False,         # Re-scan directories before each run
    max_retries=1,             # Model retry budget for ModelRetry errors
)
```

Key methods:
- **`skills`** property -- `dict[str, Skill]` of loaded skills
- **`get_skill(name)`** -- Get by name or raise KeyError
- **`get_instructions(ctx)`** -- Build the skills system prompt (or None if no skills), auto-reloads if configured
- **`reload(include_registries=False)`** -- Re-scan directories + optionally registries
- **`skill(func, ...)`** -- Decorator to define a programmatic skill

Default instruction template:
```
You have access to a collection of skills containing domain-specific knowledge and capabilities.
...
<available_skills>
{skills_list}
</available_skills>
When a task falls within a skill's domain:
1. Use `load_skill` first to read the complete skill instructions
...
```

### Priority Order

Programmatic skills > directory skills > registry skills. Within directory skills, later directories override earlier ones (last-directory-wins).

## Capability (`capability.py`)

```python
SkillsCapability(
    skills=None, directories=None, registries=None,
    validate=True, max_depth=3, id=None,
    instruction_template=None, exclude_tools=None, auto_reload=False,
)
```

Thin wrapper around `SkillsToolset`. Exposes `.toolset` property and `get_toolset()` method. The `get_instructions()` method returns `None` (instructions are pulled natively from the toolset by the agent framework).

`SkillsCapability` is designed to be import-safe on older pydantic-ai versions (runtime error on use, not import-time crash).

## Registries (`registries/`)

### SkillRegistry (ABC)

Abstract base with async methods: `search(query, limit)`, `get(skill_name)`, `install(skill_name, target_dir)`, `update(skill_name, target_dir)` and sync `get_skills()`.

Convenience view methods return wrapper registries (never modify the original):
- `filtered(predicate)` -> `FilteredRegistry`
- `prefixed(prefix)` -> `PrefixedRegistry`
- `renamed(name_map)` -> `RenamedRegistry`

### GitSkillsRegistry

Clones a remote Git repository and exposes its skills:

```python
GitSkillsRegistry(
    repo_url="https://github.com/anthropics/skills",
    path="skills",
    target_dir="./anthropics-skills",
    token=None,           # PAT; falls back to GITHUB_TOKEN env var
    ssh_key_file=None,    # SSH key path for SSH auth
    clone_options=None,   # GitCloneOptions for fine-grained control
    validate=True,
    auto_install=True,
)
```

Requires `pip install pydantic-ai-skills[git]` (GitPython).

### GitCloneOptions

`depth`, `branch`, `single_branch`, `sparse_paths`, `env`, `multi_options`, `git_options` -- all map to GitPython kwargs.

### S3SkillsRegistry

Downloads skills from an S3 bucket (or S3-compatible store: MinIO, Ceph, Cloudflare R2):

```python
S3SkillsRegistry(
    bucket="my-skills-bucket",
    prefix="skills",
    target_dir="./s3-skills",
    boto3_client=None,    # Fully configured boto3 S3 client
    validate=True,
    auto_install=True,
)
```

Requires `pip install pydantic-ai-skills[s3]` (boto3).

### Composition Wrappers

- **`CombinedRegistry(registries)`** -- Aggregate multiple registries; search/get/install/update queries all
- **`FilteredRegistry(wrapped, predicate)`** -- Filter skills by callable predicate
- **`PrefixedRegistry(wrapped, prefix)`** -- Prepend prefix to all skill names
- **`RenamedRegistry(wrapped, name_map)`** -- Rename skills via `{new_name: original_name}` map
- **`WrapperRegistry(wrapped)`** -- Base delegation wrapper (override methods selectively)

## SKILL.md Parsing (`_parsing.py`)

- **`parse_skill_md(content)`** -- Returns `(frontmatter_dict, instructions_markdown)`, handles missing/empty frontmatter
- **`validate_skill_metadata(frontmatter, instructions, uri)`** -- Validates name format, description length (max 1024), compatibility length (max 500), instruction line count (max 500). Emits `UserWarning` for issues, returns `True`/`False`.

## Security

Layered defense:
- **Path traversal prevention** -- All file resolution validates against the skill directory boundary
- **Symlink escape detection** -- Symlinks pointing outside the skill directory are blocked with warnings
- **Timeout enforcement** -- Scripts killed after configurable timeout (default 30s)
- **Subprocess isolation** -- Scripts run as subprocesses, not in-process
- **Argument validation** -- JSON schema validation via `BeforeValidator` on script args
- **Tool exclusion** -- `exclude_tools` can disable script execution entirely
- **Reserved word checks** -- `anthropic` and `claude` reserved in skill names

## Testing

Test suite uses pytest (`asyncio_mode = auto`):

```bash
pip install -e ".[test]"
pytest
```

Test files in `tests/`:

| File | Coverage |
|------|----------|
| `test_toolset.py` | Core toolset behavior |
| `test_types.py` | Dataclass validation |
| `test_discovery.py` | Filesystem discovery |
| `test_local.py` | Script execution |
| `test_parsing.py` | SKILL.md parsing |
| `test_validation.py` | Metadata validation |
| `test_programmatic_skills.py` | Programmatic skill creation |
| `test_edge_cases.py` | Edge cases and error handling |
| `test_capability.py` | Capability integration |
| `test_git_registry.py` | GitSkillsRegistry |
| `test_s3_registry.py` | S3SkillsRegistry |
| `test_registry_composition.py` | Registry wrappers |
| `test_reload.py` | auto_reload behavior |
| `test_coverage_improvements.py` | Coverage improvements |
| `test_toolset_coverage.py` | Additional toolset coverage |

## Dependencies

**Required:**
- `anyio>=4.0.0`
- `pydantic-ai-slim>=1.74`
- `pyyaml>=6.0`

**Optional extras:**
- `[git]` -- `gitpython>=3.1.40`
- `[s3]` -- `boto3>=1.26.0`
- `[test]` -- `pytest`, `pytest-asyncio`, `pytest-cov`, `types-PyYAML`
- `[docs]` -- `mkdocs`, `mkdocs-material`, `mkdocstrings[python]`, others
- `[examples]` -- `uvicorn`, `httpx`, `arxiv`, `gitpython`, `langchain-community`, `ddgs`, others

## Example Skills

Three example skills provided:

- **arxiv-search** -- Search arXiv preprint repository; script `scripts/arxiv_search.py` with `--query` and `--max-papers` args
- **pydanticai-docs** -- Pydantic AI framework references (AGENT.md, DEPENDENCIES.md, FUNCTION_TOOLS.md, MCP.md, MESSAGES.md, MODELS.md, OUTPUT.md, TOOLS_AND_TOOLSETS.md)
- **web-research** -- Web research skill

## Code Style

- Single quotes for Python strings (Ruff)
- Line length <= 120
- Google-style docstrings for public APIs
- Target Python >=3.10
- Ruff with flake8-quotes, isort, pydocstyle (google convention)
