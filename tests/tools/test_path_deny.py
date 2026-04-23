"""Tests for _is_path_denied() — _is_path_denied() — verifies deny list blocks sensitive paths on all platforms."""

import os
import pytest
from pathlib import Path

from tools.file_operations import _is_path_denied


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


class TestOperationBlocking:
    """Verifies that ShellFileOperations methods respect path denial."""

    @pytest.fixture
    def file_ops(self):
        from tools.file_operations import ShellFileOperations
        from unittest.mock import MagicMock
        mock_env = MagicMock()
        # Mock _expand_path's internal echo $HOME for various paths
        def mock_execute(command, cwd=None, **kwargs):
            if "echo $HOME" in command:
                return {"output": str(Path.home()), "returncode": 0}
            if command.startswith("echo "):
                # Mock shell expansion for ~ paths
                path = command[5:].strip()
                if path.startswith("~"):
                    return {"output": str(Path.home()) + path[1:], "returncode": 0}
                return {"output": path, "returncode": 0}
            return {"output": "", "returncode": 0}

        mock_env.execute.side_effect = mock_execute
        return ShellFileOperations(mock_env)

    def test_read_denied(self, file_ops):
        result = file_ops.read_file("/etc/shadow")
        assert "Access denied" in result.error
        assert result.content == ""

    def test_write_denied(self, file_ops):
        result = file_ops.write_file("/etc/shadow", "data")
        assert "Write denied" in result.error

    def test_search_denied(self, file_ops):
        result = file_ops.search("pattern", path="/etc/shadow")
        assert "Access denied" in result.error
        assert result.total_count == 0

    def test_patch_denied(self, file_ops):
        result = file_ops.patch_replace("/etc/shadow", "old", "new")
        assert "Write denied" in result.error

    def test_patch_v4a_delete_denied(self, file_ops):
        from tools.patch_parser import parse_v4a_patch, apply_v4a_operations
        patch = "*** Begin Patch\n*** Delete File: /etc/shadow\n*** End Patch"
        ops, _ = parse_v4a_patch(patch)
        result = apply_v4a_operations(ops, file_ops)
        assert result.success is False
        assert "Delete denied" in result.error

    def test_patch_v4a_move_denied(self, file_ops):
        from tools.patch_parser import parse_v4a_patch, apply_v4a_operations
        patch = "*** Begin Patch\n*** Move File: /etc/shadow -> /tmp/shadow\n*** End Patch"
        ops, _ = parse_v4a_patch(patch)
        result = apply_v4a_operations(ops, file_ops)
        assert result.success is False
        assert "Move denied" in result.error
