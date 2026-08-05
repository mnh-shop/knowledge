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

**Supporting detail:** The README explains the image installs Hermes with the official upstream install script, persists Hermes state under `/home/agent/.hermes`, and is intended for straightforward local builds and multi-arch publishing (lines 5-11). **Caveat:** the README also lists `mini-swe-agent` among the image contents (line 9), but no explicit install step for it exists anywhere in the Dockerfile and current hermes-agent `main` has no `mini-swe-agent/` directory — see Claim-8.

## Claim-2: Single-stage Dockerfile based on docker/sandbox-templates:shell

The Dockerfile is **single-stage** — a single `FROM` (Dockerfile:1) — and installs Hermes via the official curl-pipe-bash installer, layering everything onto one base image.

**Source evidence:** Dockerfile lines 1-43:
```dockerfile
FROM docker/sandbox-templates:shell
ARG HERMES_REF=main
ARG CODEX_VERSION=0.118.0
...
RUN curl -fsSL "https://raw.githubusercontent.com/NousResearch/hermes-agent/${HERMES_REF}/scripts/install.sh" \
    | bash -s -- --skip-setup --branch "${HERMES_REF}" --dir /home/agent/hermes-agent
```

**Supporting detail:** Multiple `RUN` layers build up the single stage: apt `ffmpeg` + home dir setup (Dockerfile:10-14), Hermes install (Dockerfile:21-22), npm `@openai/codex@${CODEX_VERSION}` (Dockerfile:24), npm audit fix passes for hermes-agent and whatsapp-bridge (Dockerfile:26-30), skills-list pre-cache (Dockerfile:32), and default-state staging into `/usr/local/share/hermes-home` (Dockerfile:34-38). The `HERMES_REF` build arg defaults to `main` and can point to either a branch or a tag (README line 31).

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

**Supporting detail:** The README states the image is "intended for straightforward local builds and multi-arch publishing" (line 11). The base image `docker/sandbox-templates:shell` provides multi-platform support, and the CI workflow pins `platforms: linux/amd64,linux/arm64` (docker.yml:66).

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

## Claim-7: CI/CD workflow publishes multi-arch image to GHCR

The repository includes `.github/workflows/docker.yml` that builds and publishes the image to GHCR on push to `main`, version tags, PRs, and manual dispatch.

**Source evidence:** `.github/workflows/docker.yml`:
- Lines 3-16: Triggers — push to `main` (5-6), tags `v*` (7-8), pull_request (9), and `workflow_dispatch` with a `hermes_ref` input (branch or tag, default `main`, lines 11-16).
- Line 66: `platforms: linux/amd64,linux/arm64` (QEMU setup at 33-34, Buildx at 36-37).
- Lines 52-57: Tag scheme — branch ref, tag ref, `type=sha`, `latest` on the default branch, and the `hermes_ref` input value for manual dispatch.
- Lines 39-45 and 67: GHCR login (`ghcr.io`, docker.yml:19) and `push: true` are gated on `github.event_name != 'pull_request'`.
- Lines 64-65: `HERMES_REF=${{ inputs.hermes_ref || 'main' }}` is passed as a build arg.

**Supporting detail:** Build uses `docker/build-push-action@v6` (line 60) with `type=gha` cache (lines 70-71). This is the automated path for the multi-arch publishing the README promises.

## Claim-8: mini-swe-agent inclusion is README-stated only (unverified)

The README lists `mini-swe-agent` as an image content, but the source provides no evidence of an install step.

**Source evidence:**
- README.md line 9: "- includes `mini-swe-agent`" — the only occurrence of the claim.
- Dockerfile lines 1-43: no `mini-swe-agent` install step anywhere (only hermes install, codex npm, audit fixes, skills pre-cache).
- hermes-agent `main` tree: no `mini-swe-agent/` directory exists (a top-level `mini_swe_runner.py` is present, but not the agent directory the README implies).

**Supporting detail:** The claim should be treated as README-stated/unverified until either the Dockerfile gains an explicit install step or hermes-agent ships a `mini-swe-agent/` layout.

## Dependency Map

```
hermes-agent-docker
  └─► hermes-agent (upstream Hermes Agent source repo)
  └─► hermes-suite (depends on hermes-agent-docker pattern for composite image)
  └─► podman (alternative runtime target)
```
