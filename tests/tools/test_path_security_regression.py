
import os
import pytest
from pathlib import Path
from tools.file_operations import ShellFileOperations
from tools.patch_parser import parse_v4a_patch, apply_v4a_operations

class MockEnv:
    def __init__(self):
        self.commands = []
    def execute(self, command, cwd=None, **kwargs):
        self.commands.append(command)
        output = ""
        if "command -v" in command:
            output = "yes"
        return {"output": output, "returncode": 0}

def test_v4a_delete_denied():
    env = MockEnv()
    file_ops = ShellFileOperations(env)

    # Path that should be denied
    sensitive_path = os.path.expanduser("~/.hermes/.env")

    patch = f"""*** Begin Patch
*** Delete File: {sensitive_path}
*** End Patch"""

    ops, err = parse_v4a_patch(patch)
    assert not err

    result = apply_v4a_operations(ops, file_ops)

    # Operation should fail
    assert result.success is False
    assert "Access denied" in (result.error or "")
    # No rm command should be issued
    assert not any("rm -f" in cmd and sensitive_path in cmd for cmd in env.commands)

def test_v4a_move_denied():
    env = MockEnv()
    file_ops = ShellFileOperations(env)

    # Path that should be denied
    sensitive_path = os.path.expanduser("~/.ssh/id_rsa")
    dest_path = "/tmp/stolen_key"

    patch = f"""*** Begin Patch
*** Move File: {sensitive_path} -> {dest_path}
*** End Patch"""

    ops, err = parse_v4a_patch(patch)
    assert not err

    result = apply_v4a_operations(ops, file_ops)

    # Operation should fail
    assert result.success is False
    assert "Access denied" in (result.error or "")
    # No mv command should be issued
    assert not any("mv " in cmd and sensitive_path in cmd and dest_path in cmd for cmd in env.commands)

def test_read_file_denied():
    env = MockEnv()
    file_ops = ShellFileOperations(env)

    # Path that is in WRITE_DENIED_PATHS
    sensitive_path = os.path.expanduser("~/.hermes/.env")

    result = file_ops.read_file(sensitive_path)

    # Access should be denied
    assert "Access denied" in (result.error or "")
    # No read command should be issued
    assert not any("sed -n" in cmd and sensitive_path in cmd for cmd in env.commands)

def test_search_denied():
    env = MockEnv()
    file_ops = ShellFileOperations(env)

    # Path that should be denied
    sensitive_path = os.path.expanduser("~/.ssh")

    result = file_ops.search("pattern", path=sensitive_path)

    # Access should be denied
    assert "Access denied" in (result.error or "")
    # No search command should be issued
    assert not any("rg " in cmd and sensitive_path in cmd for cmd in env.commands) and \
           not any("grep " in cmd and sensitive_path in cmd for cmd in env.commands)

@pytest.mark.asyncio
async def test_vision_analyze_denied():
    from tools.vision_tools import vision_analyze_tool

    # Path that is in WRITE_DENIED_PATHS
    sensitive_path = os.path.expanduser("~/.hermes/.env")

    # Create the file if it doesn't exist so is_file() is True
    Path(sensitive_path).parent.mkdir(parents=True, exist_ok=True)
    Path(sensitive_path).touch()

    try:
        result_json = await vision_analyze_tool(image_url=sensitive_path, user_prompt="test")
        import json
        result = json.loads(result_json)

        # Access should be denied
        assert result["success"] is False
        assert "Access denied" in result["error"]
    finally:
        # Don't delete it if we didn't create it, but for test isolation we should cleanup
        # However, _isolate_hermes_home fixture in conftest.py usually handles this.
        pass
