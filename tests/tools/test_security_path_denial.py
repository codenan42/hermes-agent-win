"""Security regression tests for path-based denial of service.

Verifies that read, write, delete, and move operations correctly honor restricted paths.
"""

import os
import pytest
from types import SimpleNamespace
from tools.file_operations import ShellFileOperations, ReadResult, WriteResult, PatchResult
from tools.patch_parser import parse_v4a_patch, apply_v4a_operations

class FakeEnvironment:
    def __init__(self):
        self.cwd = "/app"
    def execute(self, command, cwd=None, **kwargs):
        # Default behavior: success for non-restricted commands
        return {"output": "success", "returncode": 0}

@pytest.fixture
def file_ops():
    return ShellFileOperations(FakeEnvironment())

def test_read_file_denied(file_ops):
    path = os.path.expanduser("~/.ssh/id_rsa")
    result = file_ops.read_file(path)
    assert result.error is not None
    assert "Read denied" in result.error

def test_write_file_denied(file_ops):
    path = os.path.expanduser("~/.hermes/.env")
    result = file_ops.write_file(path, "SECRET=key")
    assert result.error is not None
    assert "Write denied" in result.error

def test_patch_replace_denied(file_ops):
    path = "/etc/shadow"
    result = file_ops.patch_replace(path, "old", "new")
    assert result.error is not None
    assert "Write denied" in result.error

def test_patch_v4a_delete_denied(file_ops):
    patch_content = """*** Begin Patch
*** Delete File: /etc/sudoers
*** End Patch"""
    ops, err = parse_v4a_patch(patch_content)
    assert err is None
    result = apply_v4a_operations(ops, file_ops)
    assert result.success is False
    assert "Delete denied" in result.error

def test_patch_v4a_move_source_denied(file_ops):
    patch_content = """*** Begin Patch
*** Move File: ~/.ssh/authorized_keys -> /tmp/leaked_keys
*** End Patch"""
    ops, err = parse_v4a_patch(patch_content)
    assert err is None
    result = apply_v4a_operations(ops, file_ops)
    assert result.success is False
    assert "Move denied (source)" in result.error

def test_patch_v4a_move_destination_denied(file_ops):
    patch_content = """*** Begin Patch
*** Move File: /tmp/new_keys -> ~/.ssh/authorized_keys
*** End Patch"""
    ops, err = parse_v4a_patch(patch_content)
    assert err is None
    result = apply_v4a_operations(ops, file_ops)
    assert result.success is False
    assert "Move denied (destination)" in result.error
