"""
Test suite for ansible-role-restic
"""
import os
from typing import Any

import testinfra.utils.ansible_runner
from testinfra.host import Host

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_bzip2_package_installed(host: Host) -> None:
    """Test that bzip2 package is installed."""
    bzip2 = host.package("bzip2")
    assert bzip2.is_installed


def test_restic_binary_installed(host: Host) -> None:
    """Test that restic binary is installed and executable."""
    restic = host.file("/usr/local/bin/restic")
    assert restic.exists
    assert restic.is_symlink
    assert restic.mode == 0o755  # symlink permissions


def test_restic_actual_binary_exists(host: Host) -> None:
    """Test that the actual restic binary exists and is executable."""
    # Get the target of the symlink
    restic_link = host.file("/usr/local/bin/restic")
    target: str = host.check_output("readlink /usr/local/bin/restic")
    
    restic_binary = host.file(target)
    assert restic_binary.exists
    assert restic_binary.is_file
    assert restic_binary.mode == 0o755
    assert restic_binary.user == "root"
    assert restic_binary.group == "root"


def test_restic_config_directory(host: Host) -> None:
    """Test that restic config directory exists."""
    config_dir = host.file("/etc/restic")
    assert config_dir.exists
    assert config_dir.is_directory
    assert config_dir.mode == 0o755


def test_restic_files_config(host: Host) -> None:
    """Test that restic files configuration exists."""
    files_config = host.file("/etc/restic/files")
    assert files_config.exists
    assert files_config.is_file
    assert files_config.mode == 0o644
    assert files_config.user == "root"
    assert files_config.group == "root"
    
    # Check content contains expected files
    content: str = files_config.content_string
    assert "/etc/hostname" in content
    assert "/etc/os-release" in content


def test_restic_env_file(host: Host) -> None:
    """Test that restic environment file exists with correct permissions."""
    env_file = host.file("/etc/restic/env")
    assert env_file.exists
    assert env_file.is_file
    assert env_file.mode == 0o600
    assert env_file.user == "root"
    assert env_file.group == "root"
    
    # Check content contains required environment variables
    content: str = env_file.content_string
    assert "RESTIC_REPOSITORY=" in content
    assert "RESTIC_PASSWORD=" in content


def test_restic_backup_script(host: Host) -> None:
    """Test that backup script exists and is executable."""
    backup_script = host.file("/usr/local/bin/restic-backup")
    assert backup_script.exists
    assert backup_script.is_file
    assert backup_script.mode == 0o755
    assert backup_script.user == "root"
    assert backup_script.group == "root"
    
    # Check script contains expected commands
    content: str = backup_script.content_string
    assert "#!/usr/bin/env bash" in content
    assert "set -euxo pipefail" in content
    assert "backup --files-from /etc/restic/files" in content
    assert "forget --keep-last" in content
    assert "--prune" in content


def test_systemd_service_file(host: Host) -> None:
    """Test that systemd service file exists."""
    service_file = host.file("/etc/systemd/system/restic.service")
    assert service_file.exists
    assert service_file.is_file
    assert service_file.mode == 0o644
    assert service_file.user == "root"
    assert service_file.group == "root"
    
    # Check service configuration
    content: str = service_file.content_string
    assert "[Unit]" in content
    assert "Description=Restic backup" in content
    assert "[Service]" in content
    assert "Type=oneshot" in content
    assert "User=root" in content
    assert "ExecStart=/usr/local/bin/restic-backup" in content
    assert "EnvironmentFile=/etc/restic/env" in content


def test_systemd_timer_file(host: Host) -> None:
    """Test that systemd timer file exists."""
    timer_file = host.file("/etc/systemd/system/restic.timer")
    assert timer_file.exists
    assert timer_file.is_file
    assert timer_file.mode == 0o644
    assert timer_file.user == "root"
    assert timer_file.group == "root"
    
    # Check timer configuration
    content: str = timer_file.content_string
    assert "[Unit]" in content
    assert "Description=Run Restic on a schedule" in content
    assert "[Timer]" in content
    assert "OnCalendar=" in content
    assert "[Install]" in content
    assert "WantedBy=timers.target" in content


def test_systemd_timer_enabled(host: Host) -> None:
    """Test that restic timer is enabled."""
    timer = host.service("restic.timer")
    assert timer.is_enabled


def test_restic_version_command(host: Host) -> None:
    """Test that restic command works and shows version."""
    cmd = host.run("/usr/local/bin/restic version")
    assert cmd.rc == 0
    assert "restic 0.18.0" in cmd.stdout


def test_restic_repository_backup(host: Host) -> None:
    """
    Test that restic repository can be initialized, backed up, and pruned via
    the script provided in the role.
    """

    # Source the environment file and run the restic backup script
    cmd = host.run("env $(cat /etc/restic/env | grep -E -v '^#|^$') /usr/local/bin/restic-backup")
    assert cmd.rc == 0
