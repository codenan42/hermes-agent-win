import pytest
from unittest.mock import MagicMock, patch
from rich.text import Text

class TestQuickCommandsSecurity:
    def _make_cli(self, quick_commands):
        from cli import HermesCLI
        # We need a more real-ish CLI to have _approval_callback
        cli = HermesCLI.__new__(HermesCLI)
        cli.config = {"quick_commands": quick_commands}
        cli.console = MagicMock()
        cli._approval_callback = MagicMock()
        return cli

    def test_cli_quick_command_blocked(self):
        cli = self._make_cli({"evil": {"type": "exec", "command": "rm -rf /"}})

        with patch('cli.check_all_command_guards') as mock_guard:
            mock_guard.return_value = {"approved": False, "message": "BLOCKED"}

            with patch('subprocess.run') as mock_run:
                cli.process_command("/evil")

                mock_guard.assert_called_once()
                mock_run.assert_not_called()
                cli.console.print.assert_called()
                args = str(cli.console.print.call_args[0][0])
                assert "BLOCKED" in args

    @pytest.mark.asyncio
    async def test_gateway_quick_command_blocked(self):
        from gateway.run import GatewayRunner
        runner = GatewayRunner.__new__(GatewayRunner)
        runner.config = {"quick_commands": {"evil": {"type": "exec", "command": "rm -rf /"}}}
        runner._is_user_authorized = MagicMock(return_value=True)
        runner._running_agents = {}
        runner._pending_messages = {}

        event = MagicMock()
        event.get_command.return_value = "evil"
        event.source.platform.value = "telegram"
        event.source.chat_type = "dm"
        event.source.chat_id = "123"
        event.source.thread_id = None
        event.source.user_id = "test_user"
        event.source.user_id_alt = None

        with patch('tools.approval.check_all_command_guards') as mock_guard:
            mock_guard.return_value = {"approved": False, "message": "BLOCKED"}

            with patch('asyncio.create_subprocess_shell') as mock_run:
                result = await runner._handle_message(event)

                mock_guard.assert_called_once()
                mock_run.assert_not_called()
                assert result == "BLOCKED"
