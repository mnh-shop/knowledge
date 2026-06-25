---
name: podman-deployment
tags: [podman, deployment, golang, container-engine, daemonless, rootless, oci, container, developer-tools, security, automation, cli, docker, event-bus, git, monitoring, quadlet, storage, systemd, virtualization]
description: "Podman Deployment"
---
# Podman Deployment
**Source:** `sources/podman/`

## Installation

### Linux

Podman is available in the package manager of all major Linux distributions. The canonical installation documentation is at https://podman.io/getting-started/installation.

```bash
# Fedora / RHEL / CentOS
sudo dnf install podman

# Debian / Ubuntu
sudo apt install podman

# Arch Linux
sudo pacman -S podman
```

#### Requirements Verification

```bash
# cgroups v2 is required
podman info --format {{.Host.CgroupsVersion}}
# Should return "v2"

# Verify the installation
podman info          # Shows version, storage driver, network backend
podman version       # Shows client and server versions

# Smoke test
podman run --rm docker.io/library/alpine echo ok
```

#### Rootless Setup

```bash
# 1. Add subuid/subgid mappings
sudo usermod --add-subuids 200000-201000 --add-subgids 200000-201000 $USER

# Alternatively, edit /etc/subuid and /etc/subgid directly:
# Format: USERNAME:START_UID:RANGE
# Example: alice:200000:65536

# 2. Install fuse-overlayfs (for rootless overlay on kernels < 5.12)
sudo dnf install fuse-overlayfs  # Fedora / RHEL
# Configure in ~/.config/containers/storage.conf:
# [storage.options]
# mount_program = "/usr/bin/fuse-overlayfs"

# 3. Enable lingering for rootless containers to survive logout
sudo loginctl enable-linger $UID

# 4. (Optional) Delegate cgroup controllers for CPU limits
# Create /etc/systemd/system/user@.service.d/delegate.conf:
# [Service]
# Delegate=memory pids cpu cpuset
# Then log out and back in.
```

#### SELinux Considerations

```bash
# Bind-mounted volumes need SELinux labels:
#   :z -- shared between multiple containers
#   :Z -- private to this container (relabels the host dir)
podman run -v /host/path:/container/path:Z myimage

# Disable SELinux for a container:
podman run --security-opt label=disable myimage

# Custom storage location needs SELinux equivalence:
sudo semanage fcontext -a -e /var/lib/containers /srv/containers
sudo restorecon -R -v /srv/containers
```

### macOS

Podman on macOS requires a Linux virtual machine -- containers are Linux-native and cannot run directly on macOS.

```bash
# Install via Homebrew
brew install podman

# Verify
podman version
```

#### Podman Machine Lifecycle

```bash
# Step 1: Initialize the VM
podman machine init [--cpus 4] [--memory 4096] [--disk-size 50] [--rootful]

# Options:
#   --rootful   - Makes the VM use rootful containers (needed for ports < 1024)
#   --volume    - Mount host directories into the VM (default: $HOME:$HOME)
#   --now       - Start immediately after init

# Step 2: Start the VM
podman machine start

# Step 3: Use Podman (it connects to the VM automatically)
podman info
podman run --rm docker.io/library/alpine echo ok

# Step 4: Stop the VM
podman machine stop

# Switch to rootful mode:
podman machine set --rootful
podman machine stop && podman machine start
```

#### Other Machine Commands

```bash
podman machine list        # List all VMs with state, CPU, memory, disk
podman machine ssh         # SSH into the VM (useful for debugging)
podman machine inspect     # Detailed JSON configuration
podman machine os apply    # Apply OS updates
podman machine rm          # Remove a VM
podman machine reset       # Wipe all machines and environment
```

#### API Forwarding (macOS)

On macOS, Podman automatically configures API forwarding through a Unix socket at `~/.local/share/containers/podman/machine/podman.sock` (or similar). A `docker.sock` symlink is created when `--rootful` is set, enabling Docker-compatible API access.

#### Port Binding on macOS

Rootless containers on the macOS VM bind to ports above 1024 by default. For ports below 1024:

1. Run the machine in rootful mode: `podman machine set --rootful`
2. Change `ip_unprivileged_port_start` inside the VM:
   ```bash
   podman machine ssh 'sudo sh -c "echo 80 > /proc/sys/net/ipv4/ip_unprivileged_port_start"'
   ```

---

## Quadlet Deployment Lifecycle

Quadlet is the primary mechanism for deploying Podman containers as production systemd services. It translates `.container`, `.volume`, `.network`, `.pod`, `.kube`, `.build`, and `.image` files into systemd `.service` units.

### Directory Layout

```bash
# Rootless (user services):
~/.config/containers/systemd/
  myapp.container
  myapp.volume
  myapp.network
  myapp.container.d/
    10-secrets.conf     # Secret references

# Rootful (system services):
/etc/containers/systemd/
  myapp.container
```

### Step-by-Step Deployment

#### 1. Write Quadlet Files

Create your `.container` file:

```ini
# ~/.config/containers/systemd/myapp.container
[Unit]
Description=My App
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/myapp:latest
ContainerName=myapp
PublishPort=127.0.0.1:8080:8080
Volume=myapp.volume:/data:Z
UserNS=keep-id
HealthCmd=curl -sf http://localhost:8080/health || exit 1
HealthInterval=30s
HealthRetries=3
Notify=healthy
DropCapability=all
NoNewPrivileges=true

[Service]
Restart=on-failure
RestartSec=30s
TimeoutStartSec=900

[Install]
WantedBy=default.target
```

#### 2. Place in Search Path

```bash
cp myapp.container ~/.config/containers/systemd/
```

#### 3. Reload systemd

```bash
systemctl --user daemon-reload
```

This triggers the `podman-system-generator` to read all Quadlet files and create `.service` units in the generator output directory.

#### 4. Verify Generation

```bash
# Check what was generated
/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun

# Analyze the generated unit
systemd-analyze --user --generators=true verify myapp.service
```

#### 5. Start the Service

```bash
systemctl --user start myapp.service
```

#### 6. Enable Auto-Start at Boot

The `[Install]` section is applied by the generator at `daemon-reload` time. **Do NOT use `systemctl enable`** -- it will fail with "Unit is transient or generated."

Instead, ensure the Quadlet file has:

```ini
[Install]
WantedBy=default.target    # For rootless (starts at user login)
# Or:
WantedBy=multi-user.target  # For rootful (starts at system boot)
```

Then run `systemctl --user daemon-reload` to apply.

#### 7. Monitor

```bash
# Service status
systemctl --user status myapp.service

# Logs
journalctl --user -u myapp.service -f

# Container status
podman ps
podman logs myapp
```

#### 8. Stop and Remove

```bash
systemctl --user stop myapp.service
systemctl --user disable myapp.service   # Remove from [Install] Wants
rm ~/.config/containers/systemd/myapp.container
systemctl --user daemon-reload          # Clean up generated files
```

### Quadlet Install Command

Podman provides a convenience command for installing Quadlet files:

```bash
# Install a single file
podman quadlet install myapp.container

# Install an application directory
podman quadlet install --application=myapp ./dir/

# Install from a URL
podman quadlet install https://example.com/myapp.container
```

This copies the file to the correct user search path and runs `systemctl --user daemon-reload`.

---

## Secret Lifecycle

Secrets are sensitive data (up to 512 kB) -- passwords, TLS certs, SSH keys, API tokens -- that containers need at runtime but should not be in images or source control.

### Creating Secrets

```bash
# From a file
podman secret create my_secret ./secret.txt

# From stdin
echo "sk-abc123..." | podman secret create openai-key -

# From environment variable
podman secret create --env=true my_secret MYSECRET

# With rotation (overwrite without error)
podman secret create --replace my_secret new_value
```

### Listing and Inspecting

```bash
podman secret ls
podman secret ls --filter name=confidential
podman secret inspect my_secret
podman secret inspect --pretty my_secret          # Human-readable
podman secret inspect --showsecret my_secret     # WARNING: reveals the data
```

### Using Secrets in Quadlet

Secrets go in a drop-in file (not in the main `.container` file, which may be committed):

```ini
# ~/.config/containers/systemd/myapp.container.d/10-secrets.conf
[Container]

# Secret as environment variable
Secret=my-api-key,type=env,target=API_KEY

# Secret as mounted file (default mount path: /run/secrets/<name>)
Secret=my-config-file,type=mount,target=/etc/app/config.yaml,mode=0440

# Multiple secrets
Secret=db-password,type=env,target=DB_PASSWORD
Secret=jwt-secret,type=env,target=JWT_SECRET
```

Options for `Secret=`:
- `type=mount` or `type=env` (default: `mount`)
- `target=` -- env var name (for `type=env`) or absolute path (for `type=mount`)
- `mode=` -- 4-digit octal permissions (default 0444, for `type=mount` only)
- `uid=`, `gid=` -- ownership override (for `type=mount` only)

### Secret Rotation

```bash
# 1. Create the new secret (replaces the old one)
podman secret create --replace my_secret new_value

# 2. The old value remains in running containers -- recreate them
systemctl --user restart myapp.service

# 3. Verify the new value
podman exec $(podman ps -q -f name=myapp) env | grep API_KEY
```

### Secret Safety

- Secrets are **not** committed to images with `podman commit`.
- Secrets are **not** exported with `podman export`.
- Secrets are copied into the container at creation time and are not accessible from other containers.
- Removing a secret in use is safe -- the container already has a copy.
- A new secret with the same name does **not** update running containers.
- Secrets are removed by `podman system prune --all` and `podman system reset`.

### Backup

Secrets are **not** individually exportable or backupable. Store secret values separately:
- Password manager
- HashiCorp Vault
- Encrypted file in a separate backup system

---

## Healthcheck Integration

### Containerfile HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

- Exit code 0 = healthy, 1 = unhealthy, 125 = error.

### Quadlet Healthcheck Options

All go in the `[Container]` section of a `.container` file:

```ini
[Container]
HealthCmd=/usr/bin/command          # The healthcheck command
HealthInterval=30s                   # How often to run (default: 30s)
HealthTimeout=10s                    # Max time per check
HealthRetries=3                      # Consecutive failures before unhealthy
HealthStartPeriod=30s                # Grace period at container start
HealthOnFailure=kill                 # Action when unhealthy -- kill integrates with systemd restart
HealthLogDestination=local           # Where to store logs
HealthMaxLogCount=5                  # Max log entries (0 = infinite)
HealthMaxLogSize=500                 # Max chars per log entry
```

### Notify=healthy (CRITICAL for Deployment)

Setting `Notify=healthy` in the `[Container]` section postpones the systemd `READY=1` notification until the container is marked healthy by Podman's healthcheck mechanism.

```ini
[Container]
HealthCmd=curl -f http://localhost:3000/health
HealthInterval=10s
HealthRetries=3
Notify=healthy
```

This means systemd waits for the application to be truly healthy before considering the service "started." Dependencies (`After=`, `Requires=`) on this service also wait for health.

### Startup Healthcheck

For containers with unpredictable startup times (e.g., running database migrations), use a startup healthcheck:

```ini
[Container]
HealthCmd=curl -f http://localhost:3000/health
HealthStartupCmd=curl -f http://localhost:3000/startup
HealthStartupInterval=1m
HealthStartupRetries=8
HealthStartupSuccess=2
HealthStartupTimeout=1m33s
```

The startup check runs until `HealthStartupSuccess` consecutive successes, then transitions to the regular healthcheck.

### Self-Healing Pattern

The recommended production pattern:

```ini
[Container]
HealthOnFailure=kill

[Service]
Restart=on-failure
```

When the container becomes unhealthy, Podman kills it. Systemd restarts it automatically -- no external monitoring needed.

### Runtime Healthcheck Commands

```bash
# Trigger a healthcheck on demand
podman healthcheck run <container>

# Show current health status
podman inspect --format '{{.State.Health.Status}}' <container>

# Debug healthcheck failures
podman --log-level debug healthcheck run <container>

# View healthcheck logs
podman inspect --format '{{.State.Health.Log}}' <container>

# Update healthcheck settings on a running container
podman update --health-max-log-count=10 <container>
```

---

## Auto-Updates

Podman provides an automatic update mechanism that polls container registries for new image versions and restarts containers that have `AutoUpdate=registry` set.

### Enabling Auto-Updates

Two components are needed:

1. **Quadlet label** on each container to enable updates:
   ```ini
   [Container]
   AutoUpdate=registry
   ```

2. **The auto-update systemd timer** to trigger updates on a schedule:
   ```bash
   # Rootful
   sudo systemctl enable --now podman-auto-update.timer
   
   # Rootless (user service)
   systemctl --user enable --now podman-auto-update.timer
   ```

   The timer fires daily with a randomized delay (default 900 seconds) to avoid thundering herds:
   ```ini
   # contrib/systemd/podman-auto-update.timer
   [Unit]
   Description=Podman auto-update timer
   
   [Timer]
   OnCalendar=daily
   RandomziedDelaySec=900
   
   [Install]
   WantedBy=timers.target
   ```

### How It Works

```bash
# Manual trigger (same logic as the timer)
podman auto-update
```

The auto-update process:

1. Queries each container's configured registry for a newer image digest/tag matching the `AutoUpdate` label value (`registry` or `local`).
2. If a newer image exists, pulls it.
3. Stops the running container and restarts it with the new image.
4. Containers running under systemd (Quadlet) are restarted via systemd, which keeps the service alive through the transition.

### Update Modes

| Mode | Label Value | Behavior |
|------|-------------|----------|
| Registry | `AutoUpdate=registry` | Checks the image registry for newer tags/digests (default with label) |
| Local | `AutoUpdate=local` | Uses a locally available image (pulled externally, e.g., via CI) |

### Integration with Quadlet

Auto-update works naturally with Quadlet-managed containers:
- The `AutoUpdate=registry` label is set in the Quadlet file.
- `podman auto-update` restarts the container via systemd, which re-pulls the image (if `PullPolicy=newer` or `PullPolicy=always`).
- The `[Service] Restart=on-failure` handles any restart during the update.

### Rollback on Failure

Podman auto-updates do not automatically roll back. To implement safe rollback:

1. Pin image tags in Quadlet (e.g., `Image=myapp:v1.2.3` instead of `myapp:latest`).
2. Use a CI/CD pipeline to update the specific tag and restart.
3. To roll back, update the Quadlet file with the previous image tag, then run `systemctl --user daemon-reload && systemctl --user restart myapp.service`.

### Checking Update Status

```bash
# Dry-run to see what would update
podman auto-update --dry-run

# Check when the timer last ran
systemctl --user status podman-auto-update.timer
journalctl --user -u podman-auto-update.service

# View container update labels
podman inspect --format '{{.Config.Labels}}' <container>
```

---

## Network Configuration

### Publishing Ports

```bash
# With podman run
podman run -p 8080:80 -p 443:443 myapp
# Format: [ip:][hostPort:]containerPort[/protocol]

# With Quadlet (.container)
# [Container]
# PublishPort=127.0.0.1:8080:80    # Rootless: bind to 127.0.0.1 for security
# PublishPort=443:443              # Rootful only (needs CAP_NET_BIND_SERVICE)
```

**Rootless port security**: Always bind to `127.0.0.1` in rootless mode to avoid exposing ports on all interfaces. Use a reverse proxy (nginx, Caddy, Traefik) for external access.

### Custom Networks

```bash
# Create manually
podman network create --subnet 192.168.50.0/24 --gateway 192.168.50.1 mynet
podman network create --subnet 10.89.0.0/24 --ipv6 mynet6

# With Quadlet (.network file)
# # mynet.network
# [Network]
# NetworkName=stack
# Subnet=10.89.0.0/24
# Gateway=10.89.0.1
# Driver=bridge
```

### Inter-Container DNS

On custom networks, **aardvark-dns** registers each container under its name and the first 12 characters of its container ID:

```ini
# Container A
[Container]
ContainerName=web
Network=stack.network
NetworkAlias=web

# Container B
[Container]
ContainerName=app
Network=stack.network
Exec=curl http://web:8080/api  # Resolves via aardvark-dns
```

### Network Isolation

- `Internal=true` -- restricts external access for a network.
- `--opt isolate=true` or `--opt isolate=strict` -- prevents inter-container communication on the same network.
- `Network=host` -- host networking (cannot use `PublishPort=` with host networking).
- `Network=none` -- no networking.

### Pod Networking

- Ports must be published at the pod level, not per-container within the pod.
- Containers in a pod communicate over `127.0.0.1`.
- With custom networks (non-pod), containers use DNS names for communication.

### Firewall Considerations

```bash
# Firewall rules may be lost after firewall-cmd --reload
# Restore them:
podman network reload --all

# Consider a systemd hook with busctl/dbus-monitor for automation
```

---

## Resource Limits

### Available Limits in Quadlet

```ini
[Container]
Memory=512m              # Memory limit (512m, 2g, etc.)
PidsLimit=1000           # PID limit

[Service]
CPUQuota=50%             # CPU quota percentage
CPUAccounting=true
MemoryMax=512M
TasksMax=512
```

### Via podman run

```bash
podman run --memory=512m --cpus=0.5 --pids-limit=1000 myapp
```

### Rootless Cgroup Constraints

Rootless users do not have cgroup delegation by default. Setting CPU or cpuset limits will fail with:

```
Error: OCI runtime error: crun: the requested cgroup controller `cpu` is not available
```

**Check delegated controllers:**

```bash
cat "/sys/fs/cgroup/user.slice/user-$(id -u).slice/user@$(id -u).service/cgroup.controllers"
```

Typical default: `memory pids` (CPU and cpuset may be missing).

**Enable CPU and cpuset delegation:**

Create `/etc/systemd/system/user@.service.d/delegate.conf`:

```ini
[Service]
Delegate=memory pids cpu cpuset
```

Log out and back in for the change to take effect.

**Summary:**

| Resource | Rootless (default) | With Delegate Config | Rootful |
|----------|-------------------|---------------------|---------|
| Memory | Works | Works | Works |
| CPU | Fails | Works | Works |
| PIDs | Works | Works | Works |
| cpuset | Fails | Works | Works |

### macOS Podman Machine

Resource limits are enforced inside the VM's Linux kernel. Set VM-level resources at init time, then per-container limits within the VM:

```bash
podman machine init --cpus 4 --memory 4096
```

---

## Backup and Restore

### Quadlet Files (Best Backup)

Quadlet files under `~/.config/containers/systemd/` (rootless) or `/etc/containers/systemd/` (rootful) are the authoritative container definitions. **Back these up first.**

### Volumes

```bash
# Export a named volume to a tar file
podman volume export <name> > volume-backup.tar

# Import a volume from a tar file
podman volume import <name> < volume-backup.tar

# Backup all volumes
podman volume ls -q | while read vol; do
  podman volume export $vol > ${vol}.tar
done
```

### Images

```bash
# Save images to tar files
podman save -o myimage.tar myimage:tag

# Load on new host
podman load -i myimage.tar

# Save all local images
podman images --format "{{.Repository}}:{{.Tag}}" | \
  xargs -I{} sh -c 'podman save -o $(echo {} | tr / _).tar {}'
```

### Secrets

Secrets are **not** individually exportable. Store secret values in a password manager or Vault. Recreate on the new host:

```bash
podman secret create my_secret ./secret_value.txt
```

### Complete Migration Between Hosts

1. Backup Quadlet files.
2. Export volumes: `podman volume ls -q | while read v; do podman volume export $v > ${v}.tar; done`
3. Save images: `podman save -o images.tar $(podman images -q)`
4. On new host: copy Quadlet files, import volumes/images, recreate secrets.
5. Run `systemctl --user daemon-reload` and start services.

### Storage Cleanup

```bash
# Selective cleanup
podman system prune                 # Remove unused containers, images, networks
podman system prune --all           # Also remove unused volumes and secrets
podman image prune -f               # Remove dangling images
podman volume prune                 # Remove unused volumes

# Nuclear option (removes everything except Quadlet files)
podman system reset
```

---

## Troubleshooting

### 1. subuid/subgid Not Configured

**Symptom:** `setup user: invalid argument`

**Fix:** Ensure `/etc/subuid` and `/etc/subgid` have entries for the user.

```bash
sudo usermod --add-subuids 200000-201000 --add-subgids 200000-201000 $USER
```

### 2. cgroups v2 Missing or CPU Limits Unavailable

**Symptom:** `crun: the requested cgroup controller 'cpu' is not available`

**Fix:** Create `/etc/systemd/system/user@.service.d/delegate.conf` with:

```ini
[Service]
Delegate=memory pids cpu cpuset
```

Log out and back in.

### 3. Port Already Bound (macOS)

**Symptom:** Port 127.0.0.1:7777 already bound after deleting a VM.

**Fix:** `kill -9 $(lsof -i:7777)` to remove the hanging gv-proxy process.

### 4. SELinux Denials

**Symptom:** `Permission denied` on bind-mounted volumes.

**Fix:** Use `:z` or `:Z` volume suffix, or `--security-opt label=disable`.

### 5. Containers Exit at Logout

**Symptom:** Rootless containers stop when user logs out.

**Fix:** `sudo loginctl enable-linger $UID`

### 6. Quadlet Unit Not Found

**Symptom:** `Failed to start my.service: Unit my.service not found`

**Fix:** Run `/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun` to see generated output and error messages.

### 7. Cannot Enable Quadlet Unit

**Symptom:** `Failed to enable unit: Unit is transient or generated`

**Fix:** Do NOT use `systemctl enable`. Add `[Install] WantedBy=default.target` to the Quadlet file and run `systemctl --user daemon-reload`.

### 8. Image Pull Timeout

**Symptom:** Service fails to start because image pull exceeds 90 seconds.

**Fix:** Add `[Service] TimeoutStartSec=900` to the Quadlet file.

### 9. Connection Reset on Published Ports

**Symptom:** Connecting to a published port gives `Connection reset by peer`.

**Fix:** Don't bind the container application to `127.0.0.1` -- bind to `0.0.0.0` instead.

### 10. Permission Denied for Ports Below 1024 (Rootless)

**Symptom:** `pasta failed with exit code 1: Permission denied`

**Fix:** Either use rootful mode, or lower the unprivileged port start:

```bash
sudo sh -c "echo 80 > /proc/sys/net/ipv4/ip_unprivileged_port_start"
# Make permanent:
echo 'net.ipv4.ip_unprivileged_port_start=80' | sudo tee /etc/sysctl.d/99-unprivileged-ports.conf
```

### 11. Podman Machine Stuck After Sleep

**Fix:** `podman machine stop && podman machine start`

### Debugging Commands

```bash
# Podman events
podman events

# Container logs
podman logs <container>

# Healthcheck logs
podman inspect --format '{{.State.Health.Log}}' <container>

# Debug logging
podman --log-level debug <command>

# Systemd journal
journalctl --user -u myapp.service -f           # Rootless
journalctl -u myapp.service -f                   # Rootful
```

---

## Related

- [[podman]] -- Wiki entry with overview and installation
- [[podman-architecture]] -- Deep-dive architecture document
- [[podman-quadlet-examples]] -- Production-ready Quadlet file collection
- [[podman-profile]] -- Quick-reference profile card
- [[podman.codegraph-verify]] -- Codegraph verification of architecture claims
