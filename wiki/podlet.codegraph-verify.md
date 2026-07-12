---
name: podlet-codegraph-verify
tags: [codegraph-verify, podlet, podman, quadlet, rust]
description: "Codegraph Verification: podlet"
source: sources/podlet/
---

# Codegraph Verification: podlet

**Date:** 2026-07-12

## Claim 1: Quadlet file generator from `podman run` commands
- **Wiki says:** Podlet generates Podman Quadlet (systemd-like) `.container` files from a `podman run` command. Users pass the podman command as CLI args and podlet outputs the corresponding Quadlet INI file.

- **Source evidence:** `src/main.rs` line 1-3 states: "Podlet generates Podman Quadlet (systemd-like) files from a Podman command". `src/cli.rs` lines 612-628 define `PodmanCommands::Run` which maps to a `Container` Quadlet section with Image, Environment, and other options. The `main()` function at line 28 calls `Cli::parse().print_or_write_files()` which processes `podman run` args into `quadlet::File` structs (cli.rs:593-597).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Generates 8 Quadlet resource types (.container, .pod, .kube, .network, .volume, .build, .image, .artifact)
- **Wiki says:** Podlet supports 8 Quadlet resource types: Container, Pod, Kube, Network, Volume, Build, Image, and Artifact files.

- **Source evidence:** `src/quadlet.rs` lines 322-332 define `Resource` enum with these 8 variants: `Container(Box<Container>)`, `Pod(Pod)`, `Kube(Kube)`, `Network(Network)`, `Volume(Volume)`, `Build(Box<Build>)`, `Image(Image)`, `Artifact(Artifact)`. The `ResourceKind` enum at lines 488-497 lists all 8 kinds. The `Resource::extension()` method (lines 396-398) maps each kind to its file extension. `src/cli.rs` lines 611-709 list all `PodmanCommands` subcommands mapping to these resource types.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Compose file conversion (Docker Compose → Quadlet)
- **Wiki says:** Podlet converts Docker Compose files to Quadlet `.container`, `.volume`, and `.network` files, with optional pod and kube output modes.

- **Source evidence:** `src/cli/compose.rs` defines the `Compose` struct (lines 44-78) with `pod` and `kube` flags. The `Commands::Compose` variant at cli.rs line 569 converts compose files: "[creates] a `.container` file for each service, a `.volume` file for each volume, and a `.network` file for each network." The implementation in `Compose::try_into_files()` processes `compose_spec` types including `Service`, `Network`, and `Volumes`. The dependency on `compose_spec = "0.3.0"` in `Cargo.toml` confirms compose parsing support.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Existing object generation (from running Podman containers/pods/volumes/networks)
- **Wiki says:** Podlet can generate Quadlet files from existing Podman objects using `podlet generate` subcommands that read live state from the Podman API.

- **Source evidence:** `src/cli.rs` lines 571-576 define the `Generate` subcommand for "existing object" generation: "Generate a Podman Quadlet file from an existing object." The comment notes: "these commands require that Podman is installed and is searchable from the `PATH` environment variable." The `Commands::Generate` variant at line 575 invokes `try_into_quadlet_files()` which queries podman for existing containers, pods, networks, and volumes. On Unix, `Cargo.toml` lines 78-79 add `zbus` (D-Bus) dependency for systemd integration with `check_existing()` at cli.rs lines 951-983.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Podman version-aware downgrade (compatibility with older Podman releases)
- **Wiki says:** Podlet supports version-aware Quadlet generation that can downgrade output to be compatible with older Podman releases (v4.4 through v5.8).

- **Source evidence:** `src/quadlet.rs` lines 594-654 define `PodmanVersion` enum with variants from `V4_4` through `V5_8`, each with `value(name)` aliases. The `PodmanVersion::LATEST` constant is `V5_8` (line 659). The `Downgrade` trait (lines 577-588) provides a `downgrade()` method that is "a one-way transformation" — it restricts options to what was available in the specified Podman version. The `Cli` struct has a `--podman-version` / `-p` CLI flag (clap args at cli.rs lines 170-172). The `try_into_files()` method at cli.rs lines 453-472 applies downgrade when `self.podman_version < PodmanVersion::LATEST`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Dual output modes (stdout printing or file writing with `--file`/`--unit-directory`)
- **Wiki says:** Podlet outputs to stdout by default, or writes files with `--file` (custom path) or `--unit-directory` (default systemd path: `~/.config/containers/systemd/` for users, `/etc/containers/systemd/` for root).

- **Source evidence:** `src/cli.rs` lines 56-82 define `--file` and `--unit-directory` flags. The `file_path()` method (lines 336-369) resolves the unit directory: for root it returns `/etc/containers/systemd/`; for non-root it returns `$XDG_CONFIG_HOME/containers/systemd/`. The `print_or_write_files()` method (lines 261-333) checks: if no file flag, it prints to stdout (line 329: `print!("{files}");`); if file flags are set, it writes to files with optional overwrite (line 296-323). The `--overwrite` flag (cli.rs:111-114) handles existing file conflicts. The `open_file()` function (lines 899-921) implements create-new semantics with optional overwrite.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Kubernetes YAML output from compose files (`--kube` flag)
- **Wiki says:** Podlet can generate Kubernetes YAML + `.kube` Quadlet files from Docker Compose files using the `--kube` flag.

- **Source evidence:** `src/cli/compose.rs` lines 56-66 define the `--kube` flag. The comment at line 56-64 says: "Create a Kubernetes YAML file for a pod instead of separate containers. A `.kube` file using the generated Kubernetes YAML file is also created." The `File` enum at cli.rs lines 773-777 has both `Quadlet(quadlet::File)` and `Kubernetes(k8s::File)` variants. `src/quadlet/kube.rs` defines the `Kube` Quadlet section with fields including `yaml` (Kubernetes YAML file references), `config_map`, `network`, and `publish_port`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[podlet]] -- Main wiki entry for podlet
- [[podman]] -- Podman container engine
- [[quadlet]] -- Quadlet systemd unit generator
- [[podman-compose]] -- Podman compose support
- [[podlet.codegraph-verify]] -- This page

## Cross-project

- [[podman.codegraph-verify]] -- Podman verification
- [[buildah.codegraph-verify]] -- Buildah verification
