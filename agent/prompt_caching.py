"""Anthropic prompt caching (system_and_3 strategy).

Reduces input token costs by ~75% on multi-turn conversations by caching
the conversation prefix. Uses 4 cache_control breakpoints (Anthropic max):
  1. System prompt (stable across all turns)
  2-4. Last 3 non-system messages (rolling window)

Pure functions -- no class state, no AIAgent dependency.
"""

from typing import Any, Dict, List


def _apply_cache_marker(msg: dict, cache_marker: dict) -> None:
    """Add cache_control to a single message, handling all format variations.

    IMPORTANT: This function mutates the input 'msg' dictionary. The caller
    must provide a (shallow) copy if the original message must be preserved.
    """
    role = msg.get("role", "")
    content = msg.get("content")

    if role == "tool":
        msg["cache_control"] = cache_marker
        return

    if content is None or content == "":
        msg["cache_control"] = cache_marker
        return

    if isinstance(content, str):
        # Convert string content to list of blocks to support cache_control
        msg["content"] = [
            {"type": "text", "text": content, "cache_control": cache_marker}
        ]
        return

    if isinstance(content, list) and content:
        # Shallow copy the content list so we don't mutate the original history
        new_content = list(content)
        last = new_content[-1]
        if isinstance(last, dict):
            # Shallow copy the last block so we don't mutate the original history
            new_last = last.copy()
            new_last["cache_control"] = cache_marker
            new_content[-1] = new_last
        msg["content"] = new_content


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        A list of messages where modified messages are shallow copies of the originals.
        Unmodified messages are returned as-is (referencing the original objects).
    """
    if not api_messages:
        return []

    # Shallow copy the top-level list
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    breakpoints_used = 0

    # 1. System prompt (if present, it's always the first breakpoint)
    if messages[0].get("role") == "system":
        # Shallow copy the message dict before mutation
        messages[0] = messages[0].copy()
        _apply_cache_marker(messages[0], marker)
        breakpoints_used += 1

    # 2. Last 3 non-system messages
    remaining = 4 - breakpoints_used
    non_sys_indices = [i for i, m in enumerate(messages) if m.get("role") != "system"]

    for idx in non_sys_indices[-remaining:]:
        # Shallow copy the message dict before mutation
        messages[idx] = messages[idx].copy()
        _apply_cache_marker(messages[idx], marker)

    return messages
