"""Tests for security path denial across read and patch tools."""

import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from tools.file_operations import ShellFileOperations
from tools.patch_parser import parse_v4a_patch, apply_v4a_operations

@pytest.fixture()
def mock_env():
    """Create a mock terminal environment."""
    env = MagicMock()
    env.cwd = "/tmp/test"
    env.execute.return_value = {"output": "", "returncode": 0}
    return env

@pytest.fixture()
def file_ops(mock_env):
    return ShellFileOperations(mock_env)

def test_read_file_denied_path(file_ops):
    """Verify that read_file blocks access to sensitive paths."""
    sensitive_path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
    result = file_ops.read_file(sensitive_path)
    assert result.error is not None
    assert "Read denied" in result.error

def test_patch_delete_denied_path(file_ops):
    """Verify that patch DELETE blocks access to sensitive paths."""
    sensitive_path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
    patch = f"""*** Begin Patch
*** Delete File: {sensitive_path}
*** End Patch"""
    ops, err = parse_v4a_patch(patch)
    assert err is None

    result = apply_v4a_operations(ops, file_ops)
    assert result.success is False
    assert "Delete denied" in result.error

def test_patch_move_source_denied_path(file_ops):
    """Verify that patch MOVE blocks access to sensitive source paths."""
    sensitive_path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
    patch = f"""*** Begin Patch
*** Move File: {sensitive_path} -> /tmp/leaked_key
*** End Patch"""
    ops, err = parse_v4a_patch(patch)
    assert err is None

    result = apply_v4a_operations(ops, file_ops)
    assert result.success is False
    assert "Move denied" in result.error
    assert "source" in result.error.lower()

def test_patch_move_dest_denied_path(file_ops):
    """Verify that patch MOVE blocks access to sensitive destination paths."""
    sensitive_path = os.path.join(str(Path.home()), ".ssh", "authorized_keys")
    patch = f"""*** Begin Patch
*** Move File: /tmp/my_key -> {sensitive_path}
*** End Patch"""
    ops, err = parse_v4a_patch(patch)
    assert err is None

    result = apply_v4a_operations(ops, file_ops)
    assert result.success is False
    assert "Move denied" in result.error
    assert "destination" in result.error.lower()
