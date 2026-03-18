"""Anthropic prompt caching (system_and_3 strategy).

Reduces input token costs by ~75% on multi-turn conversations by caching
the conversation prefix. Uses 4 cache_control breakpoints (Anthropic max):
  1. System prompt (stable across all turns)
  2-4. Last 3 non-system messages (rolling window)

Pure functions -- no class state, no AIAgent dependency.
"""

from typing import Any, Dict, List


def _apply_cache_marker(msg: dict, cache_marker: dict) -> dict:
    """Add cache_control to a single message, handling all format variations.
    Returns a new dict (shallow copy + modification) if changes were needed,
    otherwise returns the original dict.
    """
    role = msg.get("role", "")
    content = msg.get("content")

    if role == "tool":
        new_msg = msg.copy()
        new_msg["cache_control"] = cache_marker
        return new_msg

    if content is None or content == "":
        new_msg = msg.copy()
        new_msg["cache_control"] = cache_marker
        return new_msg

    if isinstance(content, str):
        new_msg = msg.copy()
        new_msg["content"] = [
            {"type": "text", "text": content, "cache_control": cache_marker}
        ]
        return new_msg

    if isinstance(content, list) and content:
        new_msg = msg.copy()
        new_content = list(content)
        last = new_content[-1]
        if isinstance(last, dict):
            new_last = last.copy()
            new_last["cache_control"] = cache_marker
            new_content[-1] = new_last
        new_msg["content"] = new_content
        return new_msg

    return msg


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        List of messages with cache_control breakpoints injected.
        Only modified messages are shallow-copied; others are shared with input.
    """
    if not api_messages:
        return []

    # Shallow copy the list to avoid modifying the input list
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    breakpoints_used = 0

    if messages[0].get("role") == "system":
        messages[0] = _apply_cache_marker(messages[0], marker)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        messages[idx] = _apply_cache_marker(messages[idx], marker)

    return messages
