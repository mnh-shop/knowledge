---
name: podlet-architecture
tags:
  - podlet
  - quadlet
  - conversion
  - architecture
description: "Podlet Architecture"
---

# Podlet Architecture
**Source:** `sources/podlet/`

## Conversion Pipeline Overview

Podlet's core pipeline is a linear sequence: **Input -> Parse -> Map -> Serialize -> Output**. Each stage operates at a distinct abstraction level.

```
Input                     Parse                      Map                    Serialize            Output
------                    -----                      ---                    ---------            ------
podman run <args>    ->   clap derive structs   ->   quadtlet::Container   ->  serde::quadlet  ->   stdout / file
  (raw CLI string)        (cli::Container)           (quadlet::File)           "Key=Value\n"        (.container)
                                                                                                   
compose.yaml         ->   compose_spec crate    ->   multiple quadlet::File  -> serde::quadlet ->   .container/.volume/
  (structured YAML)       (compose_spec::Compose)    per service/resource        per file             .network files
                                                                                                   
existing container   ->   podman inspect ->     ->   cli::ContainerParser -> quadtlet::Container    .container
  (running object)        CLI arg re-parsing          quadtlet::File
```

---

## Stage 1: CLI Parsing (Input)

### Entry Point

`src/main.rs` line 28:
```rust
Cli::parse().print_or_write_files()
```

The `Cli` struct (`src/cli.rs` line 54) is the top-level clap parser. It defines:
- Global flags: `--file`, `--unit-directory`, `--quadlets-file`, `--name`, `--overwrite`, `--split-options`, `--skip-services-check`, `--podman-version`, `--absolute-host-paths`, `--service-name`, `--disable-default-quadlet-dependencies`, `--no-start-with-pod`
- Systemd sections: `[Unit]` (via `#[command(flatten)] unit: Unit`), `[Install]` (via `install: Install`)
- A subcommand `Commands` enum (line 567) with variants: `Podman`, `Compose`, `Generate`, `Kube`, `Network`, `Volume`, `Build`, `Image`, `Artifact`

### The Commands Enum

```rust
enum Commands {
    Podman { global_args: GlobalArgs, command: ContainerCommand },
    Compose(Compose),
    Generate(Generate),
    Kube(Kube),
    Network { global_args: GlobalArgs, command: NetworkCommand },
    Volume { global_args: GlobalArgs, command: VolumeCommand },
    Build { global_args: GlobalArgs, command: BuildCommand },
    Image { global_args: GlobalArgs, command: ImageCommand },
    Artifact { global_args: GlobalArgs, command: ArtifactCommand },
}
```

Each subcommand wraps the corresponding `podlet podman run/create/kube/network/volume/build/image/artifact` command, where Podlet intercepts all supported Quadlet flags at the clap level and routes unsupported ones to `PodmanArgs=`.

### Container Flag Mapping (the Core)

`src/cli/container/quadlet.rs` defines the `QuadletOptions` struct -- approximately 80+ clap-derive fields, each annotated with a doc comment like `/// Converts to "ContainerName=NAME"`. This doc comment is the contract: every field maps to exactly one Quadlet key.

The mapping structure separates fields into three categories within `src/cli/container.rs`:

1. **QuadletOptions** (`quadlet_options: QuadletOptions`): All flags that have direct Quadlet key equivalents (e.g., `--cap-add` -> `AddCapability=`, `--env` -> `Environment=`, `--publish` -> `PublishPort=`)
2. **PodmanArgs** (`podman_args: PodmanArgs`): Flags without direct Quadlet equivalents that are serialized into `PodmanArgs=` (e.g., `--cgroup-conf`, `--cpu-period`, `--cpuset-cpus`, etc.)
3. **SecurityOpt** (`security_opt: Vec<SecurityOpt>`): `--security-opt` values that either map to Quadlet keys (`apparmor=`, `mask=`, `unmask=`, `no-new-privileges`, `seccomp=`, `label=...`) or fall through to `PodmanArgs=`

Key examples of flag-to-Quadlet mapping:

| podman run flag | Quadlet key | Source location |
|----------------|-------------|-----------------|
| `--cap-add` | `AddCapability=` | `src/cli/container/quadlet.rs:48` |
| `--device` | `AddDevice=` | `src/cli/container/quadlet.rs:56` |
| `--dns` | `DNS=` | `src/cli/container/quadlet.rs:95` |
| `--entrypoint` | `Entrypoint=` | `src/cli/container/quadlet.rs:127` |
| `-e` / `--env` | `Environment=` | `src/cli/container/quadlet.rs:135` |
| `--env-file` | `EnvironmentFile=` | `src/cli/container/quadlet.rs:143` |
| `--expose` | `ExposeHostPort=` | `src/cli/container/quadlet.rs:157` |
| `--health-cmd` | `HealthCmd=` | `src/cli/container/quadlet.rs:179` |
| `-h` / `--hostname` | `HostName=` | `src/cli/container/quadlet.rs:263` |
| `--ip` | `IP=` | `src/cli/container/quadlet.rs:276` |
| `--ip6` | `IP6=` | `src/cli/container/quadlet.rs:282` |
| `-l` / `--label` | `Label=` | `src/cli/container/quadlet.rs:290` |
| `--log-driver` | `LogDriver=` | `src/cli/container/quadlet.rs:296` |
| `-m` / `--memory` | `Memory=` | `src/cli/container/quadlet.rs:310` |
| `--mount` | `Mount=` | `src/cli/container/quadlet.rs:318` |
| `--network` | `Network=` | `src/cli/container/quadlet.rs:326` |
| `--pids-limit` | `PidsLimit=` | `src/cli/container/quadlet.rs:353` |
| `-p` / `--publish` | `PublishPort=` | `src/cli/container/quadlet.rs:365` |
| `--pull` | `Pull=` | `src/cli/container/quadlet.rs:371` |
| `--read-only` | `ReadOnly=` | `src/cli/container/quadlet.rs:377` |
| `--secret` | `Secret=` | `src/cli/container/quadlet.rs:419` |
| `--sdnotify` | `Notify=` | `src/cli/container/quadlet.rs:342` |
| `--stop-signal` | `StopSignal=` | `src/cli/container/quadlet.rs:431` |
| `--stop-timeout` | `StopTimeout=` | `src/cli/container/quadlet.rs:439` |
| `--tz` | `Timezone=` | `src/cli/container/quadlet.rs:465` |
| `--volume` | `Volume=` | `src/cli/container/quadlet.rs:482` |
| `--workdir` | `WorkingDir=` | `src/cli/container/quadlet.rs:497` |

### PodmanArgs Passthrough

`src/cli/container/podman.rs` defines the `PodmanArgs` struct: flags that Quadlet does not have direct keys for, which accumulate into a single `PodmanArgs=` value. The `Display` impl serializes them into `--key value --key2 value2` format, ready to be appended after all known Quadlet keys.

This is the escape hatch: if Podman adds a new flag before Quadlet supports it, Podlet passes it through `PodmanArgs=` automatically.

---

## Stage 2: Domain Model Parsing (Map)

### The File Structure

The central domain type is `quadlet::File` (`src/quadlet.rs` line 57):

```rust
pub struct File {
    pub name: String,       // Filename stem (e.g., "my-container")
    pub unit: Unit,         // [Unit] section
    pub resource: Resource, // One of 8 resource types
    pub globals: Globals,   // Global Podman options
    pub quadlet: Quadlet,   // [Quadlet] section
    pub service: Service,   // [Service] section
    pub install: Install,   // [Install] section
}
```

### The Resource Enum

```rust
pub enum Resource {
    Container(Box<Container>),
    Pod(Pod),
    Kube(Kube),
    Network(Network),
    Volume(Volume),
    Build(Box<Build>),
    Image(Image),
    Artifact(Artifact),
}
```

Each resource variant represents a Quadlet file type with its own section name (e.g., `[Container]`, `[Pod]`, `[Kube]`) and keys. The serializer writes the section header and then the struct's fields as `Key=Value` lines.

### CLI-to-Domain Conversion

The `From<cli::Container>` impl for `quadlet::Container` (`src/cli/container.rs` line 109) performs the actual mapping:

1. Takes the parsed `QuadletOptions` (80+ typed fields)
2. Processes `SecurityOpt` values: extracts known options (apparmor, mask, seccomp, labels, etc.) into the corresponding Quadlet struct fields; unknown security opts go into `PodmanArgs=`
3. Converts `PodmanArgs` to a string via its `Display` impl
4. Joins the command into `Exec=` via `command_join()` from `escape.rs`
5. Constructs the final `quadlet::Container` with all fields populated

The same pattern applies to other resource types. For example, `quadlet::Network::try_from(compose_spec::Network)` in `src/quadlet/network.rs` handles compose-to-quadlet network conversion.

### Podman Version Downgrade

Each resource type implements the `Downgrade` trait. The downgrade system (`src/quadlet/container.rs` lines 392-690) has per-version removal methods (e.g., `remove_v5_0_options`, `remove_v4_6_options`) that:

1. Take Quadlet-only options added in that version
2. Convert them to `--flag value` strings via `push_args()` or `push_arg()`
3. Push those strings into `PodmanArgs=`

This allows generating Quadlet files compatible with specific Podman versions while still using modern features when targeting a current Podman.

---

## Stage 3: Serialization

### Quadlet Format Serializer

`src/serde/quadlet.rs` implements a custom **serde `Serializer`** that produces Quadlet INI format output. Key design:

- The `Serializer` struct maintains a `String` buffer
- When serializing a struct, it writes `[SectionName]\n` before writing fields
- Each field is serialized as `Key=Value\n`
- **JoinOption**: Multi-valued keys (like `Environment=`) can be serialized as either separate lines or joined with spaces on one line. This is controlled by the `JoinOption` set passed at serialization time. The `SeqValueSerializer` (line 531) handles this: if the key is in `join_options`, values are space-joined; otherwise each gets its own `Key=Value\n` line.
- The `File` struct's `Serialize` impl (line 96) controls the order: `[Unit]` -> Resource section -> `[Quadlet]` -> `[Service]` -> `[Install]`, only including sections that have content.

### Kubernetes YAML Serializer

`src/cli/k8s.rs` uses `serde_yaml` to serialize Kubernetes `Pod` and `PersistentVolumeClaim` objects. Multiple PVCs are separated with `---` YAML document delimiters before the Pod spec.

### PodmanArgs Serializer

`src/serde/args.rs` produces `--flag value --flag2 value2` format for the `PodmanArgs=` passthrough. Uses a separate `Serializer` that writes args in this format.

---

## Stage 4: Output

`print_or_write_files()` (`src/cli.rs` line 261) handles all output modes:

1. **File output** (if `--file`, `--unit-directory`, or `--quadlets-file` is set):
   - Validates combinations (e.g., `--file <path>` with `compose` requires a directory, not a file)
   - Resolves the target path via `file_path()` (line 336), which returns either `FilePath::Dir(path)` or `FilePath::Full(path)`
   - For Unix: calls `check_existing()` (line 951) which uses D-Bus (`zbus`) to query systemd for conflicting unit files. This inspects both system and user systemd instances.
   - For `--quadlets-file`: concatenates all serialized files into one `.quadlets` file
   - For separate files: iterates files, each calling `File::write()` which serializes then writes

2. **stdout** (default): Concatenates all files into `.quadlets` format and prints to stdout

---

## Compose File Conversion (Detailed)

`src/cli/compose.rs:try_into_files()` handles the `podlet compose` subcommand.

### Flow

1. Read compose file (from path, stdin, or auto-detect `compose.yaml`/`compose.yml`/etc.)
2. Apply merge options (for multi-file compose)
3. Validate (via `compose_spec::Compose::validate_all()`)
4. Branch on `--kube` vs default (Quadlet) vs `--pod`

### --kube Path

1. Convert `Compose` -> `k8s::File` (Kubernetes Pod + PVCs)
2. Create a `quadlet::Kube` unit referencing `{name}-kube.yaml`
3. Output: `.kube` file + Kubernetes YAML file

### Default (Quadlet) Path

1. Extract services, networks, volumes from the compose spec
2. Call `parts_try_into_files()` (`src/cli/compose.rs` line 248):
   - Maps volumes to check which need separate Quadlet volume definitions (non-empty compose volumes)
   - Calls `services_try_into_quadlet_files()`: iterates each compose `Service`, converts to `quadlet::Container` via `TryFrom<compose_spec::Service>` (`src/cli/container.rs` line 64)
   - Calls `networks_try_into_quadlet_files()`: maps `compose_spec::Network` to `quadlet::Network` with IPAM support
   - Calls `volumes_try_into_quadlet_files()`: maps compose volumes to `quadlet::Volume` for volumes with options, or uses inline volume references otherwise

### --pod Path (with --pod)

Same as default path, plus:
- Collects published ports from all services into `pod_ports`
- Creates a `quadlet::Pod` file with those ports
- Links each container to the pod via `Pod=name.pod` and sets `StartWithPod=true`

### Compose Unsupported Features

Podlet explicitly rejects compose features without Quadlet equivalents. The `compose::ensure_empty()` method (`src/cli/container/compose.rs` line 250) checks for unsupported fields like `build`, `deploy`, `develop`, `profiles`, `links`, `external_links`, `volumes_from`, `extends`, `domain_name`, `configs`, `credential_spec`, `cpu_count`, `cpu_percent`, `scale`, `attach`, `isolation`, and compose extensions.

---

## Generate Subcommand (From Existing Objects)

`podlet generate` (`src/cli/generate.rs`) reverse-engineers running objects into Quadlet files.

### For Containers

1. Runs `podman container inspect <name>` (via `podman_inspect()`)
2. Deserializes the JSON output into `ContainerInspect { config: { create_command: Vec<String> } }`
3. The `create_command` (e.g., `["podman", "run", "--name", "myapp", "image:tag"]`) is filtered by `filter_container_create_command()` to strip `podman`, `container`, `run`/`create` leading tokens
4. The remaining args are parsed through the same `ContainerParser` used for direct `podman run` input, ensuring consistent flag-to-Quadlet mapping
5. The same `From<cli::Container>` for `quadlet::Container` impl produces the Quadlet file

### For Pods

1. Runs `podman pod inspect <name>` to get the pod's `create_command` and list of container names
2. Parses the pod create command through `PodParser`
3. Inspects each non-infra container (filters out names ending in `-infra`)
4. Each contained container gets its own `ContainerParser::from_container()` call
5. Returns a vector containing the pod's `.pod` file plus each container's `.container` file, with proper `Pod=` references

### For Networks, Volumes, Images

Each uses `podman inspect` with the appropriate resource type and maps the inspect output fields to Quadlet fields. These are simpler than containers as they have fewer flags.

---

## Service Conflict Detection

On Unix, before writing files, `check_existing()` (`src/cli.rs` line 951):
1. Connects to systemd via D-Bus (`org.freedesktop.systemd1.Manager`)
2. Calls `ListUnitFiles()` to get all known service units
3. Compares generated file names against existing units
4. If a conflict exists and the conflicting unit is not `generated` status, returns an error with a suggestion

This prevents accidentally overwriting system-managed services.

---

## Custom Serde Serializer Architecture

The Quadlet format serializer (`src/serde/quadlet.rs`) is a `serde::Serializer` implementation rather than a template-based writer. This is a deliberate design choice:

- **`Serializer`** (line 73): Top-level serializer. Handles structs -> writes `[SectionName]\n` header, then delegates each field. Sequences are handled by `SeqValueSerializer`.
- **`ValueSerializer`** (line 363): Writes individual `Key=Value\n` lines.
- **`SeqValueSerializer`** (line 531): Handles repeated keys. Either writes `Key=Value\n` per value (split mode) or `Key=Value1 Value2 Value3\n` (joined mode) based on `JoinOption`.
- **Key encoding**: The serializer uses `#[serde(rename = "PascalCase")]` on Quadlet structs, so Rust `container_name` becomes `ContainerName` in output.

The `to_string()` function (line 42) accepts any `T: Serialize` and the `JoinOption` set, producing the final Quadlet string.

---

## Error Handling Pattern

Podlet uses `color-eyre` throughout with chained `wrap_err()` calls that provide context at each conversion boundary. The pattern is consistent:

```
operation at one level
  -> wrap_err("context about what went wrong")
  -> optional .suggestion("how to fix")
```

This produces user-friendly error messages like:
```
Error: error converting compose file
  caused by: error converting network `frontend` into a Quadlet network
  caused by: `attachable` is not supported
  Suggestion: Remove the `attachable` field from the compose network definition
```

## Related

- [[podlet-deployment]] -- Installation, usage patterns, and deployment workflow
- [[podlet-quadlet-examples]] -- Concrete conversion examples demonstrating the pipeline
- [[podlet]] -- Wiki overview, key features, and source file roles
