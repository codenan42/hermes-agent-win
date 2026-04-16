"""Security tests for Sentinel's path-based and command-based protections."""

import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from tools.file_operations import ShellFileOperations, ReadResult
from tools.approval import check_all_command_guards

class TestSentinelPathProtections:
    @pytest.fixture
    def file_ops(self):
        env = MagicMock()
        env.execute.return_value = {"output": "", "returncode": 0}
        return ShellFileOperations(env, cwd="/tmp")

    def test_read_file_denied(self, file_ops):
        # Sensitive path should be blocked
        path = os.path.expanduser("~/.ssh/id_rsa")
        result = file_ops.read_file(path)
        assert "Read denied" in result.error

    def test_delete_file_denied(self, file_ops):
        # Sensitive path should be blocked
        path = "/etc/shadow"
        success = file_ops.delete_file(path)
        assert success is False
        # Verify execute was NOT called for the rm command
        assert not any("rm" in call.args[0] for call in file_ops.env.execute.call_args_list)

    def test_move_file_denied(self, file_ops):
        # Sensitive source should be blocked
        success = file_ops.move_file("/etc/sudoers", "/tmp/evil")
        assert success is False

        # Sensitive destination should be blocked
        success = file_ops.move_file("/tmp/safe", "/etc/sudoers.d/evil")
        assert success is False

        # Verify execute was NOT called for the mv command
        assert not any("mv" in call.args[0] for call in file_ops.env.execute.call_args_list)

class TestSentinelCommandProtections:
    def test_dangerous_command_blocked(self, monkeypatch):
        # Simulate CLI environment
        monkeypatch.setenv("HERMES_INTERACTIVE", "1")

        # A clearly dangerous command
        cmd = "rm -rf /"

        # Mock the interactive prompt to deny
        from tools import approval
        monkeypatch.setattr(approval, "prompt_dangerous_approval", lambda *args, **kwargs: "deny")

        result = check_all_command_guards(cmd, "local")
        assert result["approved"] is False
        assert "BLOCKED" in result["message"]

    def test_safe_command_allowed(self, monkeypatch):
        # Simulate CLI environment
        monkeypatch.setenv("HERMES_INTERACTIVE", "1")

        cmd = "ls -l"
        result = check_all_command_guards(cmd, "local")
        assert result["approved"] is True
        assert result["message"] is None
