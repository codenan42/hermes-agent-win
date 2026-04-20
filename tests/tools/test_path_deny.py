"""Tests for path-based security — verifies deny list blocks access to sensitive paths."""

import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from tools.file_operations import _is_path_denied, ShellFileOperations


class TestPathDenyExactPaths:
    def test_etc_shadow(self):
        assert _is_path_denied("/etc/shadow") is True

    def test_etc_passwd(self):
        assert _is_path_denied("/etc/passwd") is True

    def test_etc_sudoers(self):
        assert _is_path_denied("/etc/sudoers") is True

    def test_ssh_authorized_keys(self):
        assert _is_path_denied("~/.ssh/authorized_keys") is True

    def test_ssh_id_rsa(self):
        path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
        assert _is_path_denied(path) is True

    def test_ssh_id_ed25519(self):
        path = os.path.join(str(Path.home()), ".ssh", "id_ed25519")
        assert _is_path_denied(path) is True

    def test_netrc(self):
        path = os.path.join(str(Path.home()), ".netrc")
        assert _is_path_denied(path) is True

    def test_hermes_env(self):
        path = os.path.join(str(Path.home()), ".hermes", ".env")
        assert _is_path_denied(path) is True

    def test_shell_profiles(self):
        home = str(Path.home())
        for name in [".bashrc", ".zshrc", ".profile", ".bash_profile", ".zprofile"]:
            assert _is_path_denied(os.path.join(home, name)) is True, f"{name} should be denied"

    def test_package_manager_configs(self):
        home = str(Path.home())
        for name in [".npmrc", ".pypirc", ".pgpass"]:
            assert _is_path_denied(os.path.join(home, name)) is True, f"{name} should be denied"


class TestPathDenyPrefixes:
    def test_ssh_prefix(self):
        path = os.path.join(str(Path.home()), ".ssh", "some_key")
        assert _is_path_denied(path) is True

    def test_aws_prefix(self):
        path = os.path.join(str(Path.home()), ".aws", "credentials")
        assert _is_path_denied(path) is True

    def test_gnupg_prefix(self):
        path = os.path.join(str(Path.home()), ".gnupg", "secring.gpg")
        assert _is_path_denied(path) is True

    def test_kube_prefix(self):
        path = os.path.join(str(Path.home()), ".kube", "config")
        assert _is_path_denied(path) is True

    def test_sudoers_d_prefix(self):
        assert _is_path_denied("/etc/sudoers.d/custom") is True

    def test_systemd_prefix(self):
        assert _is_path_denied("/etc/systemd/system/evil.service") is True


class TestPathAllowed:
    def test_tmp_file(self):
        assert _is_path_denied("/tmp/safe_file.txt") is False

    def test_project_file(self):
        assert _is_path_denied("/home/user/project/main.py") is False

    def test_hermes_config_not_env(self):
        path = os.path.join(str(Path.home()), ".hermes", "config.yaml")
        assert _is_path_denied(path) is False


class TestOperationsSecurity:
    """Test that file operations actually enforce path-based security."""

    @pytest.fixture
    def mock_env(self):
        env = MagicMock()
        env.execute.return_value = {"output": "", "returncode": 0}
        return env

    @pytest.fixture
    def file_ops(self, mock_env):
        return ShellFileOperations(mock_env)

    def test_read_denied(self, file_ops):
        path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
        result = file_ops.read_file(path)
        assert result.error is not None
        assert "Read denied" in result.error

    def test_write_denied(self, file_ops):
        path = os.path.join(str(Path.home()), ".hermes", ".env")
        result = file_ops.write_file(path, "SECRET=123")
        assert result.error is not None
        assert "Write denied" in result.error

    def test_delete_denied(self, file_ops):
        path = "/etc/shadow"
        result = file_ops.delete_file(path)
        assert result.exit_code != 0
        assert "Delete denied" in result.stdout

    def test_move_source_denied(self, file_ops):
        src = "/etc/passwd"
        dst = "/tmp/passwd_backup"
        result = file_ops.move_file(src, dst)
        assert result.exit_code != 0
        assert "Move denied (source)" in result.stdout

    def test_move_destination_denied(self, file_ops):
        src = "/tmp/my_config"
        dst = os.path.join(str(Path.home()), ".bashrc")
        result = file_ops.move_file(src, dst)
        assert result.exit_code != 0
        assert "Move denied (destination)" in result.stdout
