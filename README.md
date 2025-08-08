# Ansible Role: Restic

An Ansible role to install and configure [Restic](https://restic.net/) backup system with systemd timer for automated backups.

## Requirements

- Linux system with systemd
- Internet access to download Restic binary
- Root privileges for installation

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

### Restic Installation

```yaml
restic_version: '0.18.0'
restic_arch: 'amd64'
restic_download_url: 'https://github.com/restic/restic/releases/download/v{{ restic_version }}/restic_{{ restic_version }}_linux_{{ restic_arch }}.bz2'
restic_install_path: /usr/local/bin/restic_{{ restic_version }}_linux_{{ restic_arch }}
```

### Backup Configuration

```yaml
restic_schedule: "*-*-* 0:00:00"  # Daily at midnight
restic_keep_last: 7               # Keep last 7 backups
restic_files: []                  # List of files/directories to backup
restic_repository: ""             # Restic repository URL
restic_repository_password: ""    # Repository password
restic_env: {}                    # Additional environment variables
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  become: yes
  roles:
    - role: hbjydev.restic
      vars:
        restic_repository: "s3:s3.amazonaws.com/my-backup-bucket"
        restic_repository_password: "my-secure-password"
        restic_files:
          - "/home"
          - "/etc"
          - "/var/log"
        restic_schedule: "0 2 * * *"  # Daily at 2 AM
        restic_keep_last: 30
        restic_env:
          AWS_ACCESS_KEY_ID: "{{ vault_aws_access_key }}"
          AWS_SECRET_ACCESS_KEY: "{{ vault_aws_secret_key }}"
```

## Backup Destinations

This role supports all Restic backends. Configure via `restic_repository` and `restic_env`:

### Local Directory
```yaml
restic_repository: "/path/to/backup/repo"
```

### SFTP
```yaml
restic_repository: "sftp:user@host:/path/to/repo"
```

### AWS S3
```yaml
restic_repository: "s3:s3.amazonaws.com/bucket-name"
restic_env:
  AWS_ACCESS_KEY_ID: "your-access-key"
  AWS_SECRET_ACCESS_KEY: "your-secret-key"
```

### Azure Blob Storage
```yaml
restic_repository: "azure:container-name"
restic_env:
  AZURE_ACCOUNT_NAME: "account-name"
  AZURE_ACCOUNT_KEY: "account-key"
```

### Google Cloud Storage
```yaml
restic_repository: "gs:bucket-name:/path"
restic_env:
  GOOGLE_PROJECT_ID: "project-id"
  GOOGLE_APPLICATION_CREDENTIALS: "/path/to/service-account.json"
```

## What This Role Does

1. Installs the `bzip2` package (required for extraction)
2. Downloads the specified Restic version
3. Extracts and installs Restic to the system
4. Creates a symlink at `/usr/local/bin/restic`
5. Sets up configuration files:
   - `/etc/restic/files` - List of files to backup
   - `/etc/restic/env` - Environment variables and credentials
   - `/usr/local/bin/restic-backup` - Backup script
6. Creates systemd service and timer for automated backups
7. Enables and starts the systemd timer

## Systemd Integration

The role creates two systemd units:

- `restic.service` - One-shot service that runs the backup
- `restic.timer` - Timer that triggers the backup service

The timer is automatically enabled and will run according to the `restic_schedule` variable.

## Security Notes

- The environment file (`/etc/restic/env`) is created with mode 600 (readable by root only)
- The backup script runs as root to ensure access to all files
- Store sensitive variables like passwords and API keys in Ansible Vault

## License

Apache-2.0

## Author Information

This role was created by [Hayden Young](https://hayden.moe).