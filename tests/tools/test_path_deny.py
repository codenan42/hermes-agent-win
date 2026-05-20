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


class TestShellFileOperationsDenial:
    @pytest.fixture
    def file_ops(self):
        mock_env = MagicMock()
        mock_env.execute.return_value = {"output": "some output", "returncode": 0}
        return ShellFileOperations(mock_env)

    def test_read_file_denied(self, file_ops):
        path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
        result = file_ops.read_file(path)
        assert "Read denied" in result.error

    def test_write_file_denied(self, file_ops):
        path = os.path.join(str(Path.home()), ".bashrc")
        result = file_ops.write_file(path, "evil content")
        assert "Write denied" in result.error

    def test_patch_replace_denied(self, file_ops):
        path = "/etc/sudoers"
        result = file_ops.patch_replace(path, "old", "new")
        assert "Write denied" in result.error

    def test_search_path_denied(self, file_ops):
        path = os.path.join(str(Path.home()), ".ssh")
        result = file_ops.search("pattern", path=path)
        assert "Access denied" in result.error

    def test_search_results_filtered(self, file_ops):
        # Mock find results containing a protected path
        home = str(Path.home())
        protected = os.path.join(home, ".ssh", "id_rsa")
        safe = "/tmp/safe.txt"

        file_ops._exec = MagicMock()
        file_ops._exec.return_value = MagicMock(
            stdout=f"123456789.0 {protected}\n987654321.0 {safe}",
            exit_code=0
        )
        file_ops._has_command = MagicMock(return_value=True)

        result = file_ops.search("*", path="/", target="files")
        assert protected not in result.files
        assert safe in result.files
