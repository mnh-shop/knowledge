---
name: cockpit
description: "Cockpit Project — web-based Linux server management interface"
source: sources/cockpit-podman/
tags: [ui, podman, cockpit-podman, administration, monitoring]
---

# Cockpit Project

The [Cockpit](https://cockpit-project.org/) Project is a web-based Linux server management interface that provides a graphical UI for system administration tasks. It offers a simplified, user-friendly alternative to command-line system management tools, making Linux server administration more accessible while maintaining full access to underlying systemd and system capabilities.

## Overview

Cockpit serves as a comprehensive server administration dashboard accessible through any modern web browser. It connects directly to the host system's systemd, journald, and other core Linux services without requiring agents or daemons beyond the standard Cockpit bridge. The interface is designed for both novice and experienced administrators, providing quick access to common tasks while preserving the full power of the underlying system.

## Key Features

### System Administration
- **Service Management**: Start, stop, restart, enable, and disable systemd services with real-time status
- **Storage Management**: View and configure storage pools, drives, partitions, and filesystems
- **Network Configuration**: Configure network interfaces, bonds, bridges, VLANs, and DNS settings
- **User Management**: Create, modify, and remove system users and groups with sudo privileges

### Monitoring and Diagnostics
- **Real-time Metrics**: CPU, memory, disk I/O, and network activity graphs
- **Journal Integration**: Browse systemd journal logs with powerful filtering capabilities
- **Process Monitoring**: Top-like process view with sorting and search
- **Performance Analysis**: Built-in diagnostic tools for troubleshooting system issues

### Container and Pod Management
- **Podman Integration**: Full container lifecycle management through cockpit-podman module
- **Image Management**: Pull, search, delete, and prune container images
- **Pod Orchestration**: Create and manage Podman pods with port and volume mappings
- **Terminal Access**: Interactive console access to containers via web-based terminal

### Security and Access Control
- **Two-Factor Authentication**: TOTP/HOTP support for user accounts
- **SSH Key Management**: Centralized SSH key storage and distribution
- **SELinux Troubleshooting**: SELinux context monitoring and policy violation detection
- **Sudo Access**: Fine-grained privilege escalation for administrative actions

### Multi-User Support
- **Concurrent Sessions**: Multiple administrators can access Cockpit simultaneously
- **User Isolation**: Per-user views of containers, services, and resources
- **Session Recording**: Optional session audit logging for compliance

## Architecture

Cockpit operates as a systemd service (`cockpit.socket`) that spawns the Cockpit bridge on demand. The web interface runs entirely client-side in the browser, with all administrative actions proxied through the bridge to the host system. This architecture ensures:

- No persistent daemon consuming resources
- Direct integration with systemd and Linux system APIs
- Secure access via standard HTTPS with optional certificate authentication
- Support for both system-level (root) and user-level (rootless) sessions

## Development and Extensibility

Cockpit supports modular extensions through its plugin system. Key development aspects:

- **Starter Kit**: Template project for building new Cockpit modules
- **WebSocket Protocol**: Real-time communication between browser and system
- **PatternFly Components**: Consistent UI design through Red Hat's design system
- **Internationalization**: Comprehensive translation support via gettext and Weblate

## Related

- [[cockpit-podman]] — Cockpit web UI module for managing Podman containers
- [[podman]] — Container engine managed by Cockpit
- [[bootc]] — Bootable container OS deployable with Cockpit

## Installation

Cockpit is available in most Linux distribution repositories:

- **Fedora/RHEL**: `dnf install cockpit`
- **Debian/Ubuntu**: `apt install cockpit`
- **Arch Linux**: `pacman -S cockpit`

After installation, enable and start with:
```
sudo systemctl enable --now cockpit.socket
```

The web interface is accessible at `https://server-address:9090`.

## In This Vault

- [[cockpit-podman]] — Cockpit web UI module for managing Podman containers
- [[podman]] — Container engine managed by Cockpit
- [[quadlet]] — systemd-native container management integration