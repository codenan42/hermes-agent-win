"""Tests for _is_path_denied() — verifies deny list blocks sensitive paths on all platforms."""

import os
from pathlib import Path
from tools.file_operations import _is_path_denied

class TestIsPathDenied:
    def test_shadow_denied(self):
        assert _is_path_denied("/etc/shadow") is True

    def test_passwd_denied(self):
        assert _is_path_denied("/etc/passwd") is True

    def test_sudoers_denied(self):
        assert _is_path_denied("/etc/sudoers") is True

    def test_ssh_authorized_keys_denied(self):
        assert _is_path_denied("~/.ssh/authorized_keys") is True

    def test_ssh_id_rsa_denied(self):
        path = os.path.expanduser("~/.ssh/id_rsa")
        assert _is_path_denied(path) is True

    def test_ssh_id_ed25519_denied(self):
        path = os.path.expanduser("~/.ssh/id_ed25519")
        assert _is_path_denied(path) is True

    def test_ssh_config_denied(self):
        path = os.path.expanduser("~/.ssh/config")
        assert _is_path_denied(path) is True

    def test_hermes_env_denied(self):
        path = os.path.expanduser("~/.hermes/.env")
        assert _is_path_denied(path) is True

    def test_shell_configs_denied(self):
        home = str(Path.home())
        for name in [".bashrc", ".zshrc", ".profile", ".bash_profile", ".zprofile"]:
            assert _is_path_denied(os.path.join(home, name)) is True, f"{name} should be denied"

    def test_auth_configs_denied(self):
        home = str(Path.home())
        for name in [".netrc", ".pgpass", ".npmrc", ".pypirc"]:
            assert _is_path_denied(os.path.join(home, name)) is True, f"{name} should be denied"

    def test_ssh_directory_denied(self):
        path = os.path.expanduser("~/.ssh")
        assert _is_path_denied(path) is True
        assert _is_path_denied(path + "/") is True

    def test_aws_directory_denied(self):
        path = os.path.expanduser("~/.aws")
        assert _is_path_denied(path) is True

    def test_gnupg_directory_denied(self):
        path = os.path.expanduser("~/.gnupg")
        assert _is_path_denied(path) is True

    def test_kube_directory_denied(self):
        path = os.path.expanduser("~/.kube")
        assert _is_path_denied(path) is True

    def test_etc_prefixes_denied(self):
        assert _is_path_denied("/etc/sudoers.d/custom") is True
        assert _is_path_denied("/etc/systemd/system/evil.service") is True

    def test_safe_paths_allowed(self):
        assert _is_path_denied("/tmp/safe_file.txt") is False
        assert _is_path_denied("/home/user/project/main.py") is False

    def test_partial_match_allowed(self):
        # /etc/sudoers.d is denied, but /etc/sudoers.debug should not be
        # (Assuming /etc/sudoers.d/ is in PREFIXES)
        path = "/etc/sudoers.debug"
        assert _is_path_denied(path) is False

    def test_none_or_empty_allowed(self):
        assert _is_path_denied(None) is False
        assert _is_path_denied("") is False
