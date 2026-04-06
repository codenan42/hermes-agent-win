"""Regression tests for path-based security enhancements.

Verifies that sensitive paths are protected against read, search, and
V4A patch operations (delete/move).
"""

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

class TestPathSecurityRegression:
    def test_read_denied_path(self, file_ops):
        """Verifies that read_file blocks access to sensitive files."""
        path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
        result = file_ops.read_file(path)
        assert result.error is not None
        assert "Read denied" in result.error
        assert "protected system/credential file" in result.error
        # Ensure it didn't even try to execute shell commands
        assert file_ops.env.execute.call_count == 0

    def test_search_denied_path(self, file_ops):
        """Verifies that search blocks access to sensitive paths."""
        path = os.path.join(str(Path.home()), ".ssh")
        result = file_ops.search("pattern", path=path)
        assert result.error is not None
        assert "Search denied" in result.error
        assert "protected system/credential path" in result.error
        assert file_ops.env.execute.call_count == 0

    def test_v4a_delete_denied_path(self, file_ops):
        """Verifies that V4A patch delete blocks sensitive files."""
        path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
        patch_content = f"""*** Begin Patch
*** Delete File: {path}
*** End Patch"""

        ops, err = parse_v4a_patch(patch_content)
        assert err is None
        result = apply_v4a_operations(ops, file_ops)

        assert result.success is False
        assert "Delete denied" in result.error
        assert path in result.error
        # Ensure no shell command was executed
        assert file_ops.env.execute.call_count == 0

    def test_v4a_move_source_denied_path(self, file_ops):
        """Verifies that V4A patch move blocks sensitive source files."""
        path = os.path.join(str(Path.home()), ".ssh", "id_rsa")
        patch_content = f"""*** Begin Patch
*** Move File: {path} -> /tmp/stolen_key
*** End Patch"""

        ops, err = parse_v4a_patch(patch_content)
        assert err is None
        result = apply_v4a_operations(ops, file_ops)

        assert result.success is False
        assert "Move denied" in result.error
        assert path in result.error
        assert file_ops.env.execute.call_count == 0

    def test_v4a_move_target_denied_path(self, file_ops):
        """Verifies that V4A patch move blocks sensitive target paths."""
        target = os.path.join(str(Path.home()), ".ssh", "authorized_keys")
        patch_content = f"""*** Begin Patch
*** Move File: /tmp/evil_key -> {target}
*** End Patch"""

        ops, err = parse_v4a_patch(patch_content)
        assert err is None
        result = apply_v4a_operations(ops, file_ops)

        assert result.success is False
        assert "Move denied" in result.error
        assert target in result.error
        assert file_ops.env.execute.call_count == 0
