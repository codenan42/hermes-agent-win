import os
import pytest
from pathlib import Path
from tools.file_operations import _is_path_denied, ShellFileOperations

def test_is_path_denied_directory_and_contents():
    """Verify that restricted directories and their files are correctly denied."""
    home = str(Path.home())

    # Directory itself should be denied
    ssh_dir = os.path.join(home, ".ssh")
    assert _is_path_denied(ssh_dir) is True, f"Directory {ssh_dir} should be denied"

    # File inside directory should be denied
    ssh_key = os.path.join(ssh_dir, "id_rsa")
    assert _is_path_denied(ssh_key) is True, f"File {ssh_key} should be denied"

    # Specific file path should be denied
    env_file = os.path.join(home, ".hermes", ".env")
    assert _is_path_denied(env_file) is True, f"File {env_file} should be denied"

    # Safe path should NOT be denied
    safe_path = os.path.join(home, "projects", "main.py")
    assert _is_path_denied(safe_path) is False, f"Path {safe_path} should be allowed"

class MockEnv:
    def __init__(self):
        self.cwd = "/"
    def execute(self, cmd, cwd=None, **kwargs):
        if "wc -c" in cmd:
            return {"output": "100", "returncode": 0}
        if "head -c" in cmd:
            return {"output": "some content", "returncode": 0}
        if "sed -n" in cmd:
            return {"output": "file content", "returncode": 0}
        if "wc -l" in cmd:
            return {"output": "10", "returncode": 0}
        return {"output": "", "returncode": 0}

def test_read_file_denied():
    """Verify that read_file enforces path restrictions."""
    file_ops = ShellFileOperations(MockEnv())
    path = os.path.expanduser("~/.ssh/id_rsa")

    result = file_ops.read_file(path)
    assert result.error is not None
    assert "Access denied" in result.error
    assert result.content == ""

def test_search_denied():
    """Verify that search enforces path restrictions."""
    file_ops = ShellFileOperations(MockEnv())
    path = os.path.expanduser("~/.ssh")

    result = file_ops.search("pattern", path=path)
    assert result.error is not None
    assert "Access denied" in result.error
    assert not result.matches

def test_write_file_denied():
    """Verify that write_file enforces path restrictions."""
    file_ops = ShellFileOperations(MockEnv())
    path = os.path.expanduser("~/.hermes/.env")

    result = file_ops.write_file(path, "SECRET=123")
    assert result.error is not None
    assert "Access denied" in result.error

if __name__ == "__main__":
    # Manual run if not using pytest
    test_is_path_denied_directory_and_contents()
    print("test_is_path_denied_directory_and_contents passed")
    test_read_file_denied()
    print("test_read_file_denied passed")
    test_search_denied()
    print("test_search_denied passed")
    test_write_file_denied()
    print("test_write_file_denied passed")
