"""Tests for _is_path_denied() — verifies deny list blocks sensitive paths on all platforms."""

import os
import pytest
import unittest.mock
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


class TestOperationSecurity:
    """Verify that file operations respect the path deny list."""

    @pytest.fixture
    def mock_env(self):
        from unittest.mock import MagicMock
        env = MagicMock()
        env.execute.return_value = {"output": "", "returncode": 0}
        return env

    @pytest.fixture
    def file_ops(self, mock_env):
        from tools.file_operations import ShellFileOperations
        return ShellFileOperations(mock_env)

    def test_read_file_denied(self, file_ops):
        result = file_ops.read_file("~/.ssh/id_rsa")
        assert result.error is not None
        assert "access denied" in result.error.lower()

    def test_search_denied(self, mock_env, file_ops):
        # We need to mock _has_command so it doesn't fail on rg/grep availability
        # and instead reaches our security check.
        def has_command_side_effect(cmd):
            return True

        with unittest.mock.patch.object(file_ops, '_has_command', side_effect=has_command_side_effect):
            result = file_ops.search("pattern", path="~/.ssh")
            assert result.error is not None
            assert "access denied" in result.error.lower()

    def test_patch_parser_delete_denied(self, file_ops):
        from tools.patch_parser import PatchOperation, OperationType, _apply_delete
        op = PatchOperation(operation=OperationType.DELETE, file_path="~/.ssh/id_rsa")
        success, message = _apply_delete(op, file_ops)
        assert success is False
        assert "access denied" in message.lower()

    def test_patch_parser_move_source_denied(self, file_ops):
        from tools.patch_parser import PatchOperation, OperationType, _apply_move
        op = PatchOperation(operation=OperationType.MOVE, file_path="~/.ssh/id_rsa", new_path="/tmp/stolen_key")
        success, message = _apply_move(op, file_ops)
        assert success is False
        assert "access denied" in message.lower()

    def test_patch_parser_move_dest_denied(self, file_ops):
        from tools.patch_parser import PatchOperation, OperationType, _apply_move
        op = PatchOperation(operation=OperationType.MOVE, file_path="/tmp/benign", new_path="~/.ssh/authorized_keys")
        success, message = _apply_move(op, file_ops)
        assert success is False
        assert "access denied" in message.lower()

    @pytest.mark.asyncio
    async def test_vision_analyze_denied(self, tmp_path):
        from tools.vision_tools import vision_analyze_tool
        import json

        # Create a file that would be denied (simulated by using its path)
        denied_path = os.path.join(str(Path.home()), ".ssh", "id_rsa")

        # We need to mock is_file to return True for this path for the test
        from unittest.mock import patch
        with patch("pathlib.Path.is_file", return_value=True):
            result_json = await vision_analyze_tool(denied_path, "Describe this")
            result = json.loads(result_json)
            assert result["success"] is False
            assert "access denied" in result["error"].lower()
