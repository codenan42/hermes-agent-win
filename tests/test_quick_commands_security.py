import pytest
from unittest.mock import MagicMock, patch
from cli import HermesCLI

def test_quick_command_security_guard():
    # Mock CLI setup
    cli = HermesCLI()
    cli.config = {
        "quick_commands": {
            "danger": {
                "type": "exec",
                "command": "rm -rf /"
            }
        }
    }
    cli.console = MagicMock()

    # Mock check_all_command_guards to return blocked
    with patch("tools.approval.check_all_command_guards") as mock_guard:
        mock_guard.return_value = {"approved": False, "message": "BLOCKED: Dangerous pattern detected."}

        # Execute dangerous command
        result = cli.process_command("/danger")

        # Verify guard was called
        mock_guard.assert_called_once()
        # Verify output reflects blocking
        cli.console.print.assert_any_call("[bold red]BLOCKED: Dangerous pattern detected.[/]")
        # Verify it returned True (stay in loop)
        assert result is True

def test_quick_command_allowed():
    # Mock CLI setup
    cli = HermesCLI()
    cli.config = {
        "quick_commands": {
            "safe": {
                "type": "exec",
                "command": "echo hello"
            }
        }
    }
    cli.console = MagicMock()

    # Mock check_all_command_guards to return approved
    with patch("tools.approval.check_all_command_guards") as mock_guard:
        mock_guard.return_value = {"approved": True}

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="hello", stderr="")

            # Execute safe command
            result = cli.process_command("/safe")

            # Verify guard was called
            mock_guard.assert_called_once()
            # Verify subprocess was called
            mock_run.assert_called_once()
            assert result is True
