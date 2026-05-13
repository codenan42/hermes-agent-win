import os
import pytest
from pathlib import Path
from tools.file_operations import _is_path_denied, ShellFileOperations

class MockEnv:
    def __init__(self, cwd="/"):
        self.cwd = cwd
    def execute(self, command, cwd=None, **kwargs):
        return {"output": "", "returncode": 0}

def test_is_path_denied_exact_paths():
    home = str(Path.home())
    # Test specific blocked paths
    assert _is_path_denied(os.path.join(home, ".ssh/id_rsa")) is True
    assert _is_path_denied(os.path.join(home, ".hermes/.env")) is True
    assert _is_path_denied("/etc/shadow") is True

    # Test safe paths
    assert _is_path_denied("/tmp/safe.txt") is False

def test_is_path_denied_prefixes():
    home = str(Path.home())
    # Test prefix-based blocks
    assert _is_path_denied(os.path.join(home, ".ssh/random_file")) is True
    assert _is_path_denied("/etc/sudoers.d/custom") is True

    # Test that it blocks the directory itself
    assert _is_path_denied(os.path.join(home, ".ssh")) is True
    assert _is_path_denied("/etc/systemd") is True

def test_shell_file_ops_read_denied():
    env = MockEnv()
    file_ops = ShellFileOperations(env)
    home = str(Path.home())

    path = os.path.join(home, ".bashrc")
    result = file_ops.read_file(path)
    assert "Access denied" in result.error
    assert "protected" in result.error

def test_shell_file_ops_search_denied():
    env = MockEnv()
    file_ops = ShellFileOperations(env)
    home = str(Path.home())

    # Search in a protected directory
    path = os.path.join(home, ".ssh")
    result = file_ops.search("pattern", path=path)
    assert "Access denied" in result.error
    assert "protected" in result.error

def test_is_path_denied_safe_paths():
    assert _is_path_denied("/tmp/my_project/main.py") is False
    assert _is_path_denied("relative/path/to/file.txt") is False
    assert _is_path_denied("/var/log/syslog") is False
