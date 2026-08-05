---
name: quadlet-nix-architecture
type: architecture
tags: [architecture, container, declarative, home-manager, nix, nixos, podman, quadlet, quadlet-nix, systemd, virtualization]
description: "Architecture: quadlet-nix"
source: sources/quadlet-nix/
---

# Architecture: quadlet-nix

**Source:** `sources/quadlet-nix/`
**Layer:** Container orchestration / deployment platform
**Paradigm:** Nix module system over Podman Quadlets (rootful NixOS + rootless Home Manager)

## Overview

quadlet-nix is a 1:1 declarative mapping of Podman Quadlet unit options into Nix module options. A single interface — `virtualisation.quadlet` — drives two deployment backends behind one abstraction:

1. **NixOS module** (`nixos-module.nix`) — rootful units in `/etc/containers/systemd/`
2. **Home Manager module** (`home-manager-module.nix`) — rootless units in `~/.config/containers/systemd/` with a systemd user-service overlay

The architecture has four pillars: **option typing + encoding strategies**, **deployment backends**, **cross-resource `.ref` resolution**, and **systemd lifecycle integration**.

---

## 1. Encoder Strategies ↔ Podman Lookup Semantics

`utils.nix:10-11` states the core design principle: values are encoded "based on how podman parses them", citing Podman's `pkg/systemd/quadlet/quadlet.go` lookup functions. Four scalar encoders mirror four Podman lookup families:

| Encoder (`utils.nix`) | Podman lookup family | Behavior |
|---|---|---|
| `scalar.legacy` (`:26`) | `Lookup`, `LookupAll`, `LookupLast`, `LookupAllRaw`, `LookupLastRaw` | `systemdUtils.lib.toOption`, no escaping |
| `scalar.raw` (`:29-37`) | raw lookups (no systemd unescaping) | `toOption` verbatim; **throws** if value contains `\r`/`\n` (would corrupt the unit file) |
| `scalar.quotedEscaped` (`:41`) | `LookupAllArgs`, `LookupAllKeyVal` | `builtins.toJSON` (double-quoted, C-escaped) |
| `scalar.quotedUnescaped` (`:44-54`) | `LookupAllStrv` | Quoted but **not** unescaped; throws when the escaped form differs from the plain quoted form |

All four are wrapped by `makePassive` (`utils.nix:15-22`): if the plain `toOption` output is byte-identical to the encoded form — or the difference is only surrounding quotes with no whitespace — the plain form is emitted, keeping files human-readable. The `autoEscape` toggle (`options.nix:174-176`, default `true`) controls whether the escaping applies; when disabled, `_autoEscapeRequired` (computed per resource via `quadletUtils.autoEscapeRequired`) feeds a build-time assertion (`options.nix:279-283`) that fails if any value would need quoting.

Each option is declared through `quadletOptions.mkOption` (`options.nix:7-33`), which attaches three pieces of metadata to a normal `lib.mkOption`: `property` (the Quadlet key), `cli` (the equivalent `podman` CLI flag, used for help/descriptions), and `encoders` (overrides the default encoding per value type).

---

## 2. Deployment Backends

### Rootful — NixOS module (`nixos-module.nix`)

```nix
environment.etc = map (p: {
  "containers/systemd/${p.ref}" = { text = p._configText; mode = "0600"; };
}) allObjects;          # :35-42
```

- Files land in `/etc/containers/systemd/`; Quadlet's systemd generator turns them into units at boot.
- `systemd.packages` gets a `linkFarm` of `etc/systemd/system/<svc>.service` symlinks pointing at `/run/systemd/generator/<svc>.service` (`:45-52`) — unnecessary for systemd to honor the units, but required for the **NixOS activation process** to detect updates.
- `systemd.services` entries use `overrideStrategy = "asDropin"` so the Nix activation diffing sees real changes (`:54-71`).

### Rootless — Home Manager module (`home-manager-module.nix`)

- Units go through `xdg.configFile."containers/systemd/${p.ref}"` (text) plus `systemd/user/<svc>.service.d/override.conf` that **imports** the quadlet-generated unit as a drop-in override, so `systemctl --user` sees the real service while Quadlet keeps ownership.
- An activation script symlinks the quadlet generator output into `${XDG_RUNTIME_DIR}/systemd/generator/` (`home.activation.quadletNix`).
- The auto-update service/timer is defined inline (`systemd.user.services.podman-auto-update` + `systemd.user.timers`) because of an upstream Podman packaging gap.
- `supportRootless = false` is passed to `options.nix` (`home-manager-module.nix`), meaning `rootlessConfig` options are **not** exposed — the user context already is rootless.

---

## 3. The Rootless `Type=simple` Hack (`pod.nix:244-272`)

Podman's stock Quadlet pod units use `PIDFile=` at `%t/%N.pid` for the infra container. Under rootless + system systemd that breaks: the unprivileged process cannot own a PIDFile in a root-owned runtime dir, and system systemd rejects PIDFiles owned by unprivileged users when the process is outside the service.

The workaround (`pod.nix:254-272`):
- `podmanArgs` gets `--infra-conmon-pidfile=/run/user/<uid>/%N.pid` appended (`:261-263`)
- `serviceConfig.Type = "simple"` (`:264`) — no PIDFile-based readiness
- `ExecStart` runs `/bin/sh -c "podman pod start <name> && (read pid < /run/user/<uid>/%N.pid; exec tail -f --pid \$pid)"` (`:265-267`) — after the pod starts, it reads the conmon PID and blocks on it, keeping the service alive
- `ExecStopPost` removes the pid file (`:268-272`)

The same `_rootless` flag also wires `serviceConfig.User`, `Wants=linger-users.service`, and `Requires/After=user@<uid>.service` via `applyRootlessConfig` (`options.nix:236-254`), and the container module gets `SubUIDMap`/`SubGIDMap` options (`container.nix:672-680`) plus `rootlessConfig.uid`.

---

## 4. `.ref` Resolution

Every resource object generates a Quadlet file name at config time: `ref = "${name}.pod"` (`pod.nix:247`), `ref = "${name}.build"` (`build.nix:285`), and so on. The top-level modules expose these as `.ref` attributes, so `pods.app.ref` → `app.pod`.

Resolution points:
- **Deployment:** `nixos-module.nix:37` writes `containers/systemd/${p.ref}`; `pod.nix:247` is the source of the ref for pods.
- **Consumption:** users interpolate `networks.backend.ref` into `containerConfig.networks` etc. — the value emitted is the plain unit name (e.g. `backend.network`), which Podman's Quadlet parser resolves into a systemd dependency.
- **Cross-type service dependencies:** `unitConfig.Requires`/`After` accept refs (e.g. `containers.database.ref`) in `README.md` examples, so systemd ordering follows Nix references rather than manual target names.

There is no runtime resolution — refs are pure Nix attribute access on the config tree, resolved before any unit text is generated.

---

## 5. Systemd Lifecycle Integration

### Change detection via `X-QuadletNixConfigHash`

Both backends inject a hash of the generated config text into the unit's `[Unit]` section:

- NixOS: `unitConfig.X-QuadletNixConfigHash = builtins.hashString "sha256" p._configText` (`nixos-module.nix:58`) inside an `asDropin` override
- Home Manager: `Unit.X-QuadletNixConfigHash` in `systemd.user.services` (`home-manager-module.nix`) — must live in the main file, the only thing the HM switch process inspects

The NixOS/HM switch diff sees the hash change and restarts the service on config drift.

### `wantedBy` / `autoStart`

`autoStart` (bool or target name) maps to `wantedBy`: `multi-user.target` on NixOS (`nixos-module.nix:61-67` — systemd recommends multi-user over default), `default.target` under Home Manager. `systemd.services` generates the `.targets.wants` symlinks.

### `podman-auto-update` timers

- **NixOS:** `systemd.timers.podman-auto-update` with `OnCalendar = [ "" cfg.autoUpdate.calendar ]`, `overrideStrategy = "asDropin"` (`nixos-module.nix:73-80`)
- **Home Manager:** inline user service + `systemd.user.timers` with `Persistent = true` (`home-manager-module.nix`)

Default schedule: `"*-*-* 00:00:00"` (`options.nix:187-191`).

---

## 6. Build-Time Assertions (`options.nix:256-293`)

| Assertion | Trigger | Message intent |
|---|---|---|
| Container/pod name uniqueness (`:270-277`) | Same name in `containers` and `pods` | Podman's `PodName` rule — the pod infra container collides |
| `autoEscape` required (`:279-283`) | Any object's `_autoEscapeRequired` while `autoEscape = false` | Values need quoting; enable autoEscape or undo manual quoting |
| docker-archive FQDN tag (`:286-291`) | `docker-archive:` image without `tag` (`:262-267` detection) | Archive images must name the fully qualified image reference as the tag |

`mkAssertions` composes user extras and is consumed by both modules (`nixos-module.nix:31`, `home-manager-module.nix`).

---

## 7. Escape Hatches

When typed options are insufficient, three levels of raw escape hatches exist, ordered by granularity:

1. **`rawConfig`** — replaces the entire generated unit text with hand-written Quadlet content (per-resource `_configText` check, e.g. `build.nix:282`), while keeping module infra (refs, autoStart, hashing).
2. **`PodmanArgs`** — appended after the subcommand (`container.nix:494`, `pod.nix:146`, `network.nix:159`, `build.nix:175`, `image.nix:106`, `volume.nix:116`, `kube.nix:91`) — e.g. `--infra-conmon-pidfile=` in the rootless hack.
3. **`GlobalArgs`** — inserted between `podman` and the subcommand (`container.nix:211`, `build.nix:120`, etc.) — e.g. `--log-level=debug`.

All use `scalar.quotedEscaped`, so arbitrary CLI arguments round-trip safely.

---

## 8. NixOS vs Home Manager — Decision Table

| Aspect | NixOS module | Home Manager module |
|---|---|---|
| Scope | System-wide (rootful) | User-level (rootless) |
| Unit location | `/etc/containers/systemd/` | `~/.config/containers/systemd/` |
| Podman package | `config.virtualisation.podman.package` | `osConfig.virtualisation.podman.package or pkgs.podman` |
| Rootless support | `rootlessConfig.uid` + linger + `user@<uid>.service` wiring (`options.nix:236-254`) | Inherent (user context); `supportRootless = false` hides `rootlessConfig` |
| Rootless readiness | `Type=simple` + conmon PID tail hack (`pod.nix:244-272`) | n/a (systemd --user handles PIDFile) |
| Service target | `multi-user.target` | `default.target` |
| Override mechanism | `systemd.services` with `overrideStrategy = "asDropin"` | `systemd/user/<svc>.service.d/override.conf` importing generator output |
| Hash injection | Drop-in `X-QuadletNixConfigHash` (`nixos-module.nix:58`) | Main file `X-QuadletNixConfigHash` (HM switch reads main file only) |
| Auto-update | `systemd.timers.podman-auto-update` drop-in | Inline user service + timer |
| When to use | System containers, host networking needs, rootful services | User-scoped apps, rootless by default, no sudo needed |

---

## 9. Firewall/DNS Recipes (`README.md:375-409`)

Podman DNS must be enabled *and* allowed through the firewall:
- Default network: `virtualisation.podman.defaultNetwork.settings.dns_enabled = true` (optionally pin `network_interface = "podman0"`)
- Custom Quadlet networks: DNS is on by default unless `disableDns`; open UDP 53 on the bridge interface — `virtualisation.quadlet.networks.foo.networkConfig.interfaceName = "br-foo"` + `networking.firewall.interfaces.br-foo.allowedUDPPorts = [ 53 ]`
- An `enable-dns.nix` module pattern derives both the interface names and firewall rules from the same `networks` option set, so they can't drift

---

## Related

- [[quadlet-nix]] — wiki summary
- [[quadlet-nix.codegraph-verify]] — evidence-backed verification
- [[quadlet-lsp]] / [[quadlet-lsp-guide]] — editor tooling for the generated units
- [[nix-podman-stacks-architecture]] — sibling Nix+Quadlet deployment architecture
- [[podman-quadlet]] — official Quadlet reference
