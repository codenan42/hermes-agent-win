import json
import pytest
import os
from unittest.mock import MagicMock, patch
from tools.vision_tools import vision_analyze_tool

@pytest.mark.asyncio
async def test_vision_analyze_denied_path():
    """Test that vision_analyze_tool blocks access to protected paths."""
    protected_path = os.path.expanduser("~/.ssh/id_rsa")

    # Mock Path.is_file to return True for the protected path
    with patch("pathlib.Path.is_file", return_value=True):
        result_json = await vision_analyze_tool(
            image_url=protected_path,
            user_prompt="What is this?"
        )
        result = json.loads(result_json)

        assert result["success"] is False
        assert "Access denied" in result["error"]
        assert "protected" in result["error"]

@pytest.mark.asyncio
async def test_vision_analyze_allowed_path():
    """Test that vision_analyze_tool allows access to safe paths."""
    safe_path = "/tmp/safe_image.jpg"

    # Mock Path.is_file and other things to avoid actual LLM call and file access
    with patch("pathlib.Path.is_file", return_value=True), \
         patch("pathlib.Path.stat") as mock_stat, \
         patch("tools.vision_tools._image_to_base64_data_url", return_value="data:image/jpeg;base64,abc"), \
         patch("tools.vision_tools.async_call_llm") as mock_llm:

        mock_stat.return_value.st_size = 1024
        mock_llm.return_value.choices[0].message.content = "Analysis result"

        result_json = await vision_analyze_tool(
            image_url=safe_path,
            user_prompt="What is this?"
        )
        result = json.loads(result_json)

        assert result["success"] is True
        assert result["analysis"] == "Analysis result"
