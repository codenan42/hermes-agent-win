"""Tests for _is_path_denied() — verifies deny list blocks sensitive paths on all platforms."""

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


class TestVisionPathDeny:
    @pytest.mark.asyncio
    async def test_vision_analyze_denied_path(self, monkeypatch):
        from tools.vision_tools import vision_analyze_tool
        import json

        # Mock is_interrupted
        monkeypatch.setattr("tools.interrupt.is_interrupted", lambda: False)

        # We need to mock Path.is_file to return True for a protected path
        home = str(Path.home())
        protected_path = os.path.join(home, ".ssh", "id_rsa")

        orig_is_file = Path.is_file
        def mock_is_file(self):
            if str(self) == protected_path:
                return True
            return orig_is_file(self)
        monkeypatch.setattr(Path, "is_file", mock_is_file)

        result_json = await vision_analyze_tool(protected_path, "what is this?")
        result = json.loads(result_json)

        assert result["success"] is False
        assert "denied" in result["error"].lower()


class TestPatchParserPathDeny:
    def test_patch_delete_denied_path(self):
        from tools.patch_parser import _apply_delete
        from unittest.mock import MagicMock

        home = str(Path.home())
        protected_path = os.path.join(home, ".ssh", "id_rsa")

        file_ops = MagicMock()
        from tools.patch_parser import PatchOperation, OperationType
        op = PatchOperation(operation=OperationType.DELETE, file_path=protected_path)

        success, message = _apply_delete(op, file_ops)
        assert success is False
        assert "denied" in message.lower()

    def test_patch_move_denied_path(self):
        from tools.patch_parser import _apply_move
        from unittest.mock import MagicMock

        home = str(Path.home())
        protected_path = os.path.join(home, ".ssh", "id_rsa")
        safe_path = "/tmp/safe"

        file_ops = MagicMock()
        from tools.patch_parser import PatchOperation, OperationType

        # Deny source
        op1 = PatchOperation(operation=OperationType.MOVE, file_path=protected_path, new_path=safe_path)
        success1, message1 = _apply_move(op1, file_ops)
        assert success1 is False
        assert "denied" in message1.lower()

        # Deny destination
        op2 = PatchOperation(operation=OperationType.MOVE, file_path=safe_path, new_path=protected_path)
        success2, message2 = _apply_move(op2, file_ops)
        assert success2 is False
        assert "denied" in message2.lower()
