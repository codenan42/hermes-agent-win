import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from tools.patch_parser import parse_v4a_patch, apply_v4a_operations
from tools.file_operations import ShellFileOperations

def test_patch_delete_blocked():
    """Verify that V4A patch now blocks deleting sensitive files."""
    mock_env = MagicMock()
    mock_env.execute.return_value = {"output": "", "returncode": 0}
    mock_env.cwd = "/"
    file_ops = ShellFileOperations(mock_env)

    # Path to a sensitive file
    sensitive_path = os.path.expanduser("~/.ssh/id_rsa")

    patch_content = f"""
*** Begin Patch
*** Delete File: {sensitive_path}
*** End Patch
"""
    operations, error = parse_v4a_patch(patch_content)
    assert not error

    # This should now fail and NOT call rm
    result = apply_v4a_operations(operations, file_ops)

    assert result.success is False
    assert "Write denied" in result.error
    # Verify that rm was NOT called
    for call in mock_env.execute.call_args_list:
        assert "rm" not in call[0][0]

def test_patch_move_blocked():
    """Verify that V4A patch now blocks moving sensitive files."""
    mock_env = MagicMock()
    mock_env.execute.return_value = {"output": "", "returncode": 0}
    mock_env.cwd = "/"
    file_ops = ShellFileOperations(mock_env)

    # Path to a sensitive file
    sensitive_path = os.path.expanduser("~/.ssh/id_rsa")
    dest_path = "/tmp/stolen_key"

    patch_content = f"""
*** Begin Patch
*** Move File: {sensitive_path} -> {dest_path}
*** End Patch
"""
    operations, error = parse_v4a_patch(patch_content)
    assert not error

    # This should now fail and NOT call mv
    result = apply_v4a_operations(operations, file_ops)

    assert result.success is False
    assert "Write denied" in result.error
    # Verify that mv was NOT called
    for call in mock_env.execute.call_args_list:
        assert "mv" not in call[0][0]
