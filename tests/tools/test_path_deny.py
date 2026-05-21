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
        # We need to test the resolved path since _is_path_denied calls expanduser
        path = os.path.expanduser("~/.ssh/authorized_keys")
        assert _is_path_denied(path) is True

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
        # Using a subpath of /tmp to ensure it doesn't match any prefix
        assert _is_path_denied("/tmp/project/main.py") is False


class TestShellFileOperationsPathDeny:
    def setup_method(self):
        self.env = MagicMock()
        self.ops = ShellFileOperations(self.env)
        self.protected_path = os.path.join(str(Path.home()), ".ssh", "id_rsa")

    def test_read_file_denied(self):
        result = self.ops.read_file(self.protected_path)
        assert result.error is not None
        assert "Access denied" in result.error
        self.env.execute.assert_not_called()

    def test_write_file_denied(self):
        result = self.ops.write_file(self.protected_path, "content")
        assert result.error is not None
        assert "Access denied" in result.error
        self.env.execute.assert_not_called()

    def test_patch_replace_denied(self):
        result = self.ops.patch_replace(self.protected_path, "old", "new")
        assert result.error is not None
        assert "Access denied" in result.error
        self.env.execute.assert_not_called()

    def test_search_files_denied_in_results(self):
        # Mock ripgrep output including a protected file
        self.env.execute.return_value = {
            "output": f"safe.py:1:content\n{self.protected_path}:1:secret",
            "returncode": 0
        }
        # We need to mock _has_command and _expand_path for search to work
        self.ops._has_command = MagicMock(side_effect=lambda cmd: cmd == 'rg')
        self.ops._expand_path = MagicMock(side_effect=lambda p: p)

        result = self.ops.search("pattern", target="content")
        assert len(result.matches) == 1
        assert result.matches[0].path == "safe.py"
        assert all(m.path != self.protected_path for m in result.matches)

def test_patch_parser_delete_denied():
    from tools.patch_parser import _apply_delete, PatchOperation, OperationType
    file_ops = MagicMock()
    # Mock read_file to return successfully (so it doesn't exit early)
    file_ops.read_file.return_value = MagicMock(error=None)

    protected_path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
    op = PatchOperation(operation=OperationType.DELETE, file_path=protected_path)

    success, message = _apply_delete(op, file_ops)
    assert success is False
    assert "Access denied" in message
    file_ops._exec.assert_not_called()

def test_patch_parser_move_denied():
    from tools.patch_parser import _apply_move, PatchOperation, OperationType
    file_ops = MagicMock()

    protected_path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
    safe_path = "/tmp/safe"

    # Deny source
    op = PatchOperation(operation=OperationType.MOVE, file_path=protected_path, new_path=safe_path)
    success, message = _apply_move(op, file_ops)
    assert success is False
    assert "Access denied" in message
    assert "(source)" in message

    # Deny destination
    op = PatchOperation(operation=OperationType.MOVE, file_path=safe_path, new_path=protected_path)
    success, message = _apply_move(op, file_ops)
    assert success is False
    assert "Access denied" in message
    assert "(destination)" in message

    file_ops._exec.assert_not_called()

@pytest.mark.asyncio
async def test_vision_tool_denied():
    import json
    from tools.vision_tools import vision_analyze_tool

    # ~/.bashrc usually exists and is in our deny list.
    bashrc = os.path.expanduser("~/.bashrc")

    # The tool catches exceptions and returns them as a JSON structure
    result_json = await vision_analyze_tool(bashrc, "what is this?")
    result = json.loads(result_json)

    assert result["success"] is False
    assert "Access denied" in result["error"]
