# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Ansible role for installing and configuring Restic backup system with systemd automation. The role downloads Restic binaries, sets up configuration, and creates systemd service/timer units for automated backups.

## Architecture

### Core Components

- **defaults/main.yml**: Default variable values including Restic version, download URLs, schedule, and retention settings
- **tasks/main.yml**: Main installation and configuration tasks
- **handlers/main.yml**: Systemd reload and restart handlers
- **meta/main.yml**: Role metadata including supported platforms and Galaxy information
- **templates/**: Jinja2 templates for generated configuration files

### Template Structure

The templates directory mirrors the target filesystem structure:
- `templates/etc/restic/env.j2` → `/etc/restic/env` (environment variables with mode 600)
- `templates/etc/systemd/system/restic.service.j2` → systemd service unit
- `templates/etc/systemd/system/restic.timer.j2` → systemd timer unit
- `templates/usr/local/bin/restic-backup.j2` → backup execution script

### Task Flow

1. Install bzip2 dependency
2. Download Restic binary from GitHub releases
3. Extract and install with proper permissions
4. Create symlink at `/usr/local/bin/restic`
5. Generate configuration files from templates
6. Create and enable systemd units
7. Start the timer for automated backups

## Variable Configuration

Key variables that control behavior:
- `restic_version`: Restic version to install
- `restic_repository`: Backup destination (supports all Restic backends)
- `restic_repository_password`: Repository encryption password
- `restic_files`: List of files/directories to backup
- `restic_schedule`: Systemd OnCalendar format schedule
- `restic_keep_last`: Number of snapshots to retain
- `restic_env`: Additional environment variables (for cloud credentials)

## Development Notes

- All file operations use absolute paths and proper ownership/permissions
- Security considerations: environment file is mode 600, backup runs as root
- Systemd timer is automatically enabled and handles backup scheduling
- The backup script includes repository initialization if needed
- Uses handler notifications for systemd daemon reloads

## Testing

This role uses Molecule for testing with UV for dependency management.

### Setup Testing Environment
```bash
uv sync --extra dev
```

### Run Tests
```bash
# Run all molecule tests
uv run molecule test

# Test specific scenario
uv run molecule test -s default

# Just run converge (without destroy)
uv run molecule converge

# Run verifier tests only
uv run molecule verify

# Clean up test environment
uv run molecule destroy
```

### Lint and Code Quality
```bash
# Run ansible-lint
uv run ansible-lint

# Run yamllint
uv run yamllint .
```

The molecule tests verify:
- Package installation (bzip2, restic binary)
- File permissions and ownership
- Configuration file content and structure  
- Systemd service and timer setup
- Restic functionality and repository initialization