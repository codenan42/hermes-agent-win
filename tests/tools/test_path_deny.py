"""Tests for _is_path_denied() — verifies deny list blocks sensitive paths on all platforms."""

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


class TestOperationBlocking:
    @pytest.fixture
    def file_ops(self):
        env = MagicMock()
        # Mock _expand_path behavioral dependency: ShellFileOperations calls _exec("echo $HOME")
        def execute_side_effect(command, **kwargs):
            if "echo $HOME" in command:
                return {"output": str(Path.home()), "returncode": 0}
            if "echo ~" in command:
                 return {"output": str(Path.home()), "returncode": 0}
            if "command -v" in command:
                 return {"output": "yes", "returncode": 0}
            if "test -e" in command:
                 return {"output": "exists", "returncode": 0}
            return {"output": "some content", "returncode": 0}

        env.execute.side_effect = execute_side_effect
        return ShellFileOperations(env)

    def test_read_blocked(self, file_ops):
        result = file_ops.read_file("~/.ssh/id_rsa")
        assert result.error is not None
        assert "Read denied" in result.error

    def test_write_blocked(self, file_ops):
        result = file_ops.write_file("~/.ssh/authorized_keys", "hacker key")
        assert result.error is not None
        assert "Write denied" in result.error

    def test_patch_blocked(self, file_ops):
        result = file_ops.patch_replace("~/.bashrc", "old", "new")
        assert result.error is not None
        assert "Write denied" in result.error

    def test_search_blocked(self, file_ops):
        result = file_ops.search("password", path="~/.ssh")
        assert result.error is not None
        assert "Search denied" in result.error

    def test_patch_v4a_delete_blocked(self, file_ops):
        from tools.patch_parser import parse_v4a_patch, apply_v4a_operations
        patch = """*** Begin Patch
*** Delete File: ~/.ssh/id_rsa
*** End Patch"""
        ops, err = parse_v4a_patch(patch)
        assert err is None
        result = apply_v4a_operations(ops, file_ops)
        assert result.success is False
        assert "Delete denied" in result.error

    def test_patch_v4a_move_blocked(self, file_ops):
        from tools.patch_parser import parse_v4a_patch, apply_v4a_operations
        patch = """*** Begin Patch
*** Move File: ~/.ssh/id_rsa -> /tmp/stolen_key
*** End Patch"""
        ops, err = parse_v4a_patch(patch)
        assert err is None
        result = apply_v4a_operations(ops, file_ops)
        assert result.success is False
        assert "Move denied" in result.error
