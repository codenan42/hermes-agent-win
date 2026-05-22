"""Tests for _is_path_denied() — verifies deny list blocks sensitive paths on all platforms."""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from tools.file_operations import _is_path_denied, ShellFileOperations
from tools.vision_tools import vision_analyze_tool
from tools.patch_parser import OperationType, PatchOperation, _apply_delete, _apply_move


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

    def test_hermes_config(self):
        path = os.path.join(str(Path.home()), ".hermes", "config.yaml")
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


class TestFileOperationsDeny:
    @pytest.fixture
    def file_ops(self):
        mock_env = MagicMock()
        mock_env.execute.return_value = {"output": "", "returncode": 0}
        return ShellFileOperations(mock_env)

    def test_read_file_denied(self, file_ops):
        path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
        result = file_ops.read_file(path)
        assert "Access denied" in result.error

    def test_write_file_denied(self, file_ops):
        path = os.path.join(str(Path.home()), ".ssh", "authorized_keys")
        result = file_ops.write_file(path, "evil key")
        assert "Access denied" in result.error

    def test_patch_replace_denied(self, file_ops):
        path = "/etc/shadow"
        result = file_ops.patch_replace(path, "old", "new")
        assert "Access denied" in result.error

    def test_search_denied(self, file_ops):
        path = os.path.join(str(Path.home()), ".ssh")
        result = file_ops.search("pattern", path=path)
        assert "Access denied" in result.error


@pytest.mark.asyncio
async def test_vision_tool_denied():
    path = os.path.join(str(Path.home()), ".hermes", "config.yaml")

    # We want to trigger the local file branch in vision_analyze_tool:
    # 1. Path(image_url).is_file() must be True
    # 2. _is_path_denied(str(local_path)) should then block it

    with MagicMock(spec=Path) as mock_path_instance:
        mock_path_instance.is_file.return_value = True
        mock_path_instance.__str__.return_value = path

        # When Path(image_url) is called, it returns our mock instance
        import unittest.mock as mock
        with mock.patch("tools.vision_tools.Path", return_value=mock_path_instance):
             result_json = await vision_analyze_tool(path, "what is in this file?")
             result = json.loads(result_json)

             assert result["success"] is False
             assert "Access denied" in result["error"]


def test_patch_parser_apply_delete_denied():
    mock_file_ops = MagicMock()
    path = "/etc/passwd"
    op = PatchOperation(operation=OperationType.DELETE, file_path=path)
    success, message = _apply_delete(op, mock_file_ops)
    assert success is False
    assert "Access denied" in message
    mock_file_ops.read_file.assert_not_called()


def test_patch_parser_apply_move_denied():
    mock_file_ops = MagicMock()
    src = "/etc/shadow"
    dst = "/tmp/shadow_copy"
    op = PatchOperation(operation=OperationType.MOVE, file_path=src, new_path=dst)
    success, message = _apply_move(op, mock_file_ops)
    assert success is False
    assert "Access denied" in message
    mock_file_ops._exec.assert_not_called()

    # Test move TO a protected location
    src2 = "/tmp/safe_file"
    dst2 = os.path.join(str(Path.home()), ".ssh", "id_rsa")
    op2 = PatchOperation(operation=OperationType.MOVE, file_path=src2, new_path=dst2)
    success2, message2 = _apply_move(op2, mock_file_ops)
    assert success2 is False
    assert "Access denied" in message2
    mock_file_ops._exec.assert_not_called()
