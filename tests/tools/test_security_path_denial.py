import os
import pytest
from tools.file_operations import ShellFileOperations
from pathlib import Path

class MockEnv:
    def __init__(self, cwd):
        self.cwd = cwd
    def execute(self, command, cwd=None, **kwargs):
        # Mock execution for tests that should be blocked before reaching this
        return {"output": "Should not reach here", "returncode": 1}

@pytest.fixture
def file_ops(tmp_path):
    env = MockEnv(str(tmp_path))
    return ShellFileOperations(env)

def test_read_file_denied(file_ops):
    """Test that read_file blocks access to sensitive paths."""
    # Using a path that's guaranteed to be in WRITE_DENIED_PATHS or WRITE_DENIED_PREFIXES
    # os.path.expanduser("~/.ssh/id_rsa") is one such path.
    sensitive_path = os.path.expanduser("~/.ssh/id_rsa")

    result = file_ops.read_file(sensitive_path)
    assert "Access denied" in result.error
    assert "protected system/credential file" in result.error

def test_write_file_denied(file_ops):
    """Test that write_file blocks access to sensitive paths."""
    sensitive_path = os.path.expanduser("~/.ssh/authorized_keys")

    result = file_ops.write_file(sensitive_path, "public key")
    assert "Access denied" in result.error
    assert "protected system/credential file" in result.error

def test_patch_replace_denied(file_ops):
    """Test that patch_replace blocks access to sensitive paths."""
    sensitive_path = os.path.expanduser("~/.hermes/.env")

    result = file_ops.patch_replace(sensitive_path, "OLD", "NEW")
    assert "Access denied" in result.error
    assert "protected system/credential file" in result.error

def test_patch_v4a_delete_denied(file_ops):
    """Test that V4A delete blocks access to sensitive paths."""
    sensitive_path = "/etc/shadow"

    patch_content = f"""*** Begin Patch
*** Delete File: {sensitive_path}
*** End Patch"""

    result = file_ops.patch_v4a(patch_content)
    assert result.success is False
    assert "Access denied" in result.error
    assert sensitive_path in result.error

def test_patch_v4a_move_source_denied(file_ops):
    """Test that V4A move blocks access if source is a sensitive path."""
    sensitive_path = "/etc/passwd"

    patch_content = f"""*** Begin Patch
*** Move File: {sensitive_path} -> /tmp/passwd_copy
*** End Patch"""

    result = file_ops.patch_v4a(patch_content)
    assert result.success is False
    assert "Access denied" in result.error
    assert sensitive_path in result.error

def test_patch_v4a_move_dest_denied(file_ops):
    """Test that V4A move blocks access if destination is a sensitive path."""
    sensitive_path = os.path.expanduser("~/.ssh/config")

    patch_content = f"""*** Begin Patch
*** Move File: /tmp/new_config -> {sensitive_path}
*** End Patch"""

    result = file_ops.patch_v4a(patch_content)
    assert result.success is False
    assert "Access denied" in result.error
    assert sensitive_path in result.error
