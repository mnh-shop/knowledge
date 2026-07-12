---
name: pydantic-ai-skills-codegraph-verify
tags: [pydantic-ai-skills, codegraph-verify, pydantic, skills]
description: "Codegraph Verification: pydantic-ai-skills"
source: sources/pydantic-ai-skills/
---

# Codegraph Verification: pydantic-ai-skills

**Date:** 2026-07-12

## Claim 1: Type-safe Python library implementing the Agent Skills specification for Pydantic AI
- **Wiki says:** A lightweight, type-safe Python library (Python >=3.10) implementing the Agent Skills specification for the Pydantic AI ecosystem, providing standardized composable framework for modular Agent Skills.

- **Source evidence:** `pyproject.toml` line 6-7: `name = "pydantic-ai-skills"` version `1.1.0`, line 29: `requires-python = ">=3.10"`. `README.md` lines 2-7: "A standardized, composable framework for building and managing Agent Skills within the Pydantic AI ecosystem... implements the Agent Skills specification (https://agentskills.io/home) for Pydantic AI." The `pydantic_ai_skills/` module uses Python dataclasses with full type hints throughout `types.py`, `toolset.py`, `capability.py`, etc. Source includes a `py.typed` marker file confirming PEP 561 compliance. `pyproject.toml` line 31-33: core dependencies on `pydantic-ai-slim>=1.105`, `anyio>=4.0.0`, `pyyaml>=6.0`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Four-tool agent interface with progressive disclosure model
- **Wiki says:** When integrated, the toolset registers up to four agent-callable tools: `list_skills()`, `load_skill(name)`, `read_skill_resource(name, resource)`, `run_skill_script(name, script, args)`. Skills follow a layered disclosure model: Discovery → Loading → Resources → Execution.

- **Source evidence:** `toolset.py` implements `SkillsToolset` (extending `FunctionToolset[Any]`) with exactly these four tool handlers. README.md lines 68-75 document the four tools and their purposes. Lines 79-86 document the progressive disclosure layers: "1. Discovery — Skill names and descriptions injected into agent system prompt. 2. Loading — Agent calls load_skill(name) to get full instructions. 3. Resources — Agent calls read_skill_resource() for supplementary files. 4. Execution — Agent calls run_skill_script() to execute scripts." The `instruction_template` parameter in `SkillsToolset.__init__` (lines 168-180 in README rendered docs) supports custom templates with `{skills_list}` placeholder. Any tool can be excluded via `exclude_tools` for security.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Filesystem discovery with SKILL.md parsing and multi-source loading (programmatic, filesystem, registries)
- **Wiki says:** Skills come from three sources: Programmatic (Python code via Skill dataclass or @toolset.skill decorator), Filesystem (SKILL.md files discovered by SkillsDirectory), and Registry (remote via GitSkillsRegistry, S3SkillsRegistry).

- **Source evidence:** `directory.py` implements `SkillsDirectory` with `discover_skills()` — searching for `SKILL.md` files up to configurable `max_depth` (default 3). `_parsing.py` provides `parse_skill_md(content)` returning `(frontmatter_dict, instructions_markdown)` and `validate_skill_metadata()` for validation. `registries/git.py` implements `GitSkillsRegistry` with repo URL, path, token, ssh_key_file, and clone_options. `registries/s3.py` implements `S3SkillsRegistry` with bucket, prefix, and boto3 client. `registries/combined.py` provides `CombinedRegistry` for aggregating multiple registries. README.md lines 57-63 document the priority: Programmatic > Filesystem > Registry. `examples/basic_usage.py` and `examples/programatic_skills.py` demonstrate all three loading modes.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Script execution with subprocess isolation, timeout, and path traversal prevention
- **Wiki says:** Script execution uses subprocess isolation with timeout (default 30s), shebang-first dispatch, named argument passing as --key value flags, and layered security defense including path traversal prevention, symlink escape detection, and tool exclusion.

- **Source evidence:** `local.py` implements `LocalSkillScriptExecutor` with timeout parameter (default 30 seconds), `anyio.open_process` for subprocess execution, concurrent stdout/stderr draining with `anyio.EndOfStream` handling. README.md lines 135-152 document the executor. `local.py` supports `FileBasedSkillScript` (extending `SkillScript`) and `FileBasedSkillResource` (extending `SkillResource`). README.md lines 285-293 document the security model: "Path traversal prevention — All file resolution validates against the skill directory boundary. Symlink escape detection — Symlinks pointing outside the skill directory are blocked with warnings. Timeout enforcement — Scripts killed after configurable timeout. Subprocess isolation — Scripts run as subprocesses, not in-process." Tool exclusion via `exclude_tools` can disable script execution entirely.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: 15+ test files covering toolset, types, discovery, parsing, validation, registries, and edge cases
- **Wiki says:** Test suite uses pytest with asyncio_mode=auto, covering core toolset behavior, dataclass validation, filesystem discovery, script execution, SKILL.md parsing, metadata validation, programmatic creation, edge cases, capability integration, Git and S3 registries, registry composition, and auto-reload.

- **Source evidence:** The `tests/` directory contains 17 test files: `test_toolset.py`, `test_types.py`, `test_discovery.py`, `test_local.py`, `test_parsing.py`, `test_validation.py`, `test_programmatic_skills.py`, `test_edge_cases.py`, `test_capability.py`, `test_git_registry.py`, `test_s3_registry.py`, `test_registry_composition.py`, `test_reload.py`, `test_coverage_improvements.py`, `test_toolset_coverage.py`, `test_pydantic_ai_compat.py`. `pyproject.toml` lines 57-62 define `[test]` dependencies: `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, `pytest-cov>=4.1.0`, `types-PyYAML>=6.0.12`. `pytest.ini` confirms `asyncio_mode = auto`. `AGENTS.md` (the project AGENTS.md file) line 23 documents: "pytest.ini uses asyncio_mode = auto (do not require @pytest.mark.asyncio)."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Registry composition with filtering, prefixing, renaming, and combined wrappers
- **Wiki says:** Registry composition provides CombinedRegistry, FilteredRegistry, PrefixedRegistry, RenamedRegistry, and WrapperRegistry for delegating and transforming skill access.

- **Source evidence:** `registries/_base.py` defines the `SkillRegistry` ABC with async methods `search()`, `get()`, `install()`, `update()` and sync `get_skills()`. `registries/filtered.py` implements `FilteredRegistry(wrapped, predicate)` — filters skills by callable. `registries/prefixed.py` implements `PrefixedRegistry(wrapped, prefix)` — prepends prefix to skill names. `registries/renamed.py` implements `RenamedRegistry(wrapped, name_map)` — renames via `{new_name: original_name}` dict. `registries/combined.py` implements `CombinedRegistry(registries)` — aggregates multiple registries. `registries/wrapper.py` implements `WrapperRegistry(wrapped)` — base delegation for selective override. README.md lines 270-276 document all five composition wrappers. `tests/test_registry_composition.py` tests all composition patterns.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[pydantic-ai-skills]] -- Main wiki entry
- [[skills]] -- Agent skills platform
- [[openai-skills]] -- OpenAI skill collections
- [[nanobot]] -- Agent framework

## Cross-project

- [[skills.codegraph-verify]] -- Skills catalog verification
- [[nanobot.codegraph-verify]] -- Nanobot verification
