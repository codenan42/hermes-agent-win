"""Tests for is_path_denied() — verifies deny list blocks sensitive paths on all platforms."""

import os
import pytest
from pathlib import Path

from tools.file_operations import is_path_denied


class TestPathDenyExactPaths:
    def test_etc_shadow(self):
        assert is_path_denied("/etc/shadow") is True

    def test_etc_passwd(self):
        assert is_path_denied("/etc/passwd") is True

    def test_etc_sudoers(self):
        assert is_path_denied("/etc/sudoers") is True

    def test_ssh_authorized_keys(self):
        assert is_path_denied("~/.ssh/authorized_keys") is True

    def test_ssh_id_rsa(self):
        path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
        assert is_path_denied(path) is True

    def test_ssh_id_ed25519(self):
        path = os.path.join(str(Path.home()), ".ssh", "id_ed25519")
        assert is_path_denied(path) is True

    def test_netrc(self):
        path = os.path.join(str(Path.home()), ".netrc")
        assert is_path_denied(path) is True

    def test_hermes_env(self):
        path = os.path.join(str(Path.home()), ".hermes", ".env")
        assert is_path_denied(path) is True

    def test_hermes_config(self):
        path = os.path.join(str(Path.home()), ".hermes", "config.yaml")
        assert is_path_denied(path) is True

    def test_shell_profiles(self):
        home = str(Path.home())
        for name in [".bashrc", ".zshrc", ".profile", ".bash_profile", ".zprofile"]:
            assert is_path_denied(os.path.join(home, name)) is True, f"{name} should be denied"

    def test_package_manager_configs(self):
        home = str(Path.home())
        for name in [".npmrc", ".pypirc", ".pgpass"]:
            assert is_path_denied(os.path.join(home, name)) is True, f"{name} should be denied"


class TestPathDenyPrefixes:
    def test_ssh_prefix(self):
        path = os.path.join(str(Path.home()), ".ssh", "some_key")
        assert is_path_denied(path) is True

    def test_aws_prefix(self):
        path = os.path.join(str(Path.home()), ".aws", "credentials")
        assert is_path_denied(path) is True

    def test_gnupg_prefix(self):
        path = os.path.join(str(Path.home()), ".gnupg", "secring.gpg")
        assert is_path_denied(path) is True

    def test_kube_prefix(self):
        path = os.path.join(str(Path.home()), ".kube", "config")
        assert is_path_denied(path) is True

    def test_sudoers_d_prefix(self):
        assert is_path_denied("/etc/sudoers.d/custom") is True

    def test_systemd_prefix(self):
        assert is_path_denied("/etc/systemd/system/evil.service") is True


class TestPathAllowed:
    def test_tmp_file(self):
        assert is_path_denied("/tmp/safe_file.txt") is False

    def test_project_file(self):
        assert is_path_denied("/home/user/project/main.py") is False


class TestPathDenyIntegration:
    """Tests integration of path denial into tools."""

    @pytest.mark.asyncio
    async def test_read_file_denied(self):
        from tools.file_tools import read_file_tool
        path = os.path.join(str(Path.home()), ".hermes", "config.yaml")
        result_json = read_file_tool(path=path)
        import json
        result = json.loads(result_json)
        assert "error" in result
        assert "Access denied" in result["error"]

    @pytest.mark.asyncio
    async def test_write_file_denied(self):
        from tools.file_tools import write_file_tool
        path = os.path.join(str(Path.home()), ".hermes", "config.yaml")
        result_json = write_file_tool(path=path, content="evil")
        import json
        result = json.loads(result_json)
        assert "error" in result
        assert "Write denied" in result["error"]

    @pytest.mark.asyncio
    async def test_patch_denied(self):
        from tools.file_tools import patch_tool
        path = os.path.join(str(Path.home()), ".hermes", "config.yaml")
        result_json = patch_tool(path=path, old_string="foo", new_string="bar")
        import json
        result = json.loads(result_json)
        assert "error" in result
        assert "Write denied" in result["error"]

    @pytest.mark.asyncio
    async def test_vision_analyze_denied(self):
        from tools.vision_tools import vision_analyze_tool
        path = os.path.join(str(Path.home()), ".hermes", "config.yaml")
        result_json = await vision_analyze_tool(image_url=path, user_prompt="describe")
        import json
        result = json.loads(result_json)
        assert result["success"] is False
        assert "Access denied" in result["error"]
