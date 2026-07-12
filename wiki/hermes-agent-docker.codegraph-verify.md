---
title: hermes-agent-docker
subtitle: CodeGraph Verification
date: 2026-07-12
tags: [hermes-agent-docker, codegraph-verify, hermes-agent, docker]
suffix: .codegraph-verify
source: sources/hermes-agent-docker/
related: [[hermes-agent-docker]], [[hermes-agent]], [[hermes-suite]], [[podman]]
verified-by: codegraph-explore
---

# hermes-agent-docker — CodeGraph Verification

**Verification date:** 2026-07-12
**Verified by:** codegraph-explore
**Source reference:** `sources/hermes-agent-docker/`

## Claim-1: Minimal Docker image packaging for Hermes Agent

The repository provides a minimal Docker image that packages [Hermes Agent](https://github.com/NousResearch/hermes-agent) for containerized deployment.

**Source evidence:** README.md line 1-3:
> "# hermes-agent-docker\n\nMinimal Docker image packaging for [Hermes Agent](https://github.com/NousResearch/hermes-agent)."

**Supporting detail:** The README explains the image installs Hermes with the official upstream install script, includes `mini-swe-agent`, persists Hermes state under `/home/agent/.hermes`, and is intended for straightforward local builds and multi-arch publishing (lines 5-11).

## Claim-2: Single-stage Dockerfile based on docker/sandbox-templates:shell

The Dockerfile uses `docker/sandbox-templates:shell` as its base image and installs Hermes via the official curl-pipe-bash installer.

**Source evidence:** Dockerfile lines 1-22:
```dockerfile
FROM docker/sandbox-templates:shell
ARG HERMES_REF=main
ARG CODEX_VERSION=0.118.0
...
RUN curl -fsSL "https://raw.githubusercontent.com/NousResearch/hermes-agent/${HERMES_REF}/scripts/install.sh" \
    | bash -s -- --skip-setup --branch "${HERMES_REF}" --dir /home/agent/hermes-agent
```

**Supporting detail:** The `HERMES_REF` build arg defaults to `main` and can point to either a branch or a tag (README line 31). The image also installs `@openai/codex` via npm globally (line 24).

## Claim-3: Entrypoint script seeds defaults on first empty run

The `docker-entrypoint.sh` script seeds Hermes default config into an empty mounted volume on first start.

**Source evidence:** `docker-entrypoint.sh` lines 10-13:
```sh
if [ ! -e "$SEED_MARKER" ] && [ -z "$(find "$HERMES_HOME" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
  cp -a "$DEFAULTS_DIR"/. "$HERMES_HOME"/
  : > "$SEED_MARKER"
fi
```

**Supporting detail:** The Dockerfile prepares default state at `/usr/local/share/hermes-home/` (Dockerfile lines 35-38). The entrypoint copies these into the mounted volume when empty and writes a `.docker-defaults-seeded` marker to avoid re-seeding on restarts.

## Claim-4: Volume persistence for Hermes state across container runs

The image is designed to persist Hermes config, sessions, memories, and state via a mounted volume at `/home/agent/.hermes`.

**Source evidence:** README lines 56-62:
> "Hermes stores config, sessions, memories, and related state in `/home/agent/.hermes` inside the container. Mount that path to keep state across runs."

**Supporting detail:** The Dockerfile declares `VOLUME ["/home/agent/.hermes"]` (line 42) and the README provides run examples mounting `$HOME/.hermes:/home/agent/.hermes` (lines 39-45).

## Claim-5: Supports multi-arch builds and version pinning

The image is intended for multi-arch publishing and supports building specific Hermes tags via build arguments.

**Source evidence:** README lines 23-31:
> ```bash
> docker build \
>   --build-arg HERMES_REF=v2026.3.30 \
>   -t hermes-agent-docker:v2026.3.30 .
> ```
> "`HERMES_REF` defaults to `main` and can point to either a branch or a tag."

**Supporting detail:** The README states the image is "intended for straightforward local builds and multi-arch publishing" (line 11). The base image `docker/sandbox-templates:shell` provides multi-platform support.

## Claim-6: Includes doctor command support for diagnostics

The image supports running `hermes doctor` for setup diagnostics inside the container.

**Source evidence:** README lines 49-54:
> ```bash
> docker run --rm \
>   -v "$HOME/.hermes:/home/agent/.hermes" \
>   hermes-agent-docker:local \
>   hermes doctor
> ```

**Supporting detail:** The entrypoint design (`exec "$@"`) passes through any command to the Hermes binary, enabling `hermes doctor`, `hermes setup`, and other subcommands.

## Dependency Map

```
hermes-agent-docker
  └─► hermes-agent (upstream Hermes Agent source repo)
  └─► hermes-suite (depends on hermes-agent-docker pattern for composite image)
  └─► podman (alternative runtime target)
```
