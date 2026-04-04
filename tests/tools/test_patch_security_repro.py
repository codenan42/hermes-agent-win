import pytest
from unittest.mock import MagicMock
from tools.file_operations import ShellFileOperations
from tools.patch_parser import parse_v4a_patch, apply_v4a_operations

@pytest.fixture
def mock_env():
    env = MagicMock()
    env.execute.return_value = {"output": "", "returncode": 0}
    return env

@pytest.fixture
def file_ops(mock_env):
    return ShellFileOperations(mock_env)

def test_delete_security_bypass(file_ops, mock_env):
    # Try to delete a protected file via V4A patch
    patch = """*** Begin Patch
*** Delete File: ~/.ssh/id_rsa
*** End Patch"""

    ops, error = parse_v4a_patch(patch)
    assert error is None

    result = apply_v4a_operations(ops, file_ops)

    # Check if it was blocked
    assert "denied" in result.error.lower()

def test_read_security_bypass(file_ops, mock_env):
    # Try to read a protected file
    result = file_ops.read_file("~/.ssh/id_rsa")

    # Check if it was blocked
    assert "denied" in result.error.lower()

def test_move_security_bypass(file_ops, mock_env):
    # Try to move a protected file via V4A patch
    patch = """*** Begin Patch
*** Move File: ~/.ssh/id_rsa -> /tmp/stolen_key
*** End Patch"""

    ops, error = parse_v4a_patch(patch)
    assert error is None

    result = apply_v4a_operations(ops, file_ops)

    # Check if it was blocked
    assert "denied" in result.error.lower()
