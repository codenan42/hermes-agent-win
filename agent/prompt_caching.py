"""Anthropic prompt caching (system_and_3 strategy).

Reduces input token costs by ~75% on multi-turn conversations by caching
the conversation prefix. Uses 4 cache_control breakpoints (Anthropic max):
  1. System prompt (stable across all turns)
  2-4. Last 3 non-system messages (rolling window)

Pure functions -- no class state, no AIAgent dependency.
"""

import copy
from typing import Any, Dict, List


def _apply_cache_marker(msg: dict, cache_marker: dict) -> None:
    """Add cache_control to a single message, handling all format variations."""
    role = msg.get("role", "")
    content = msg.get("content")

    if role == "tool":
        msg["cache_control"] = cache_marker
        return

    if content is None or content == "":
        msg["cache_control"] = cache_marker
        return

    if isinstance(content, str):
        msg["content"] = [
            {"type": "text", "text": content, "cache_control": cache_marker}
        ]
        return

    if isinstance(content, list) and content:
        last = content[-1]
        if isinstance(last, dict):
            last["cache_control"] = cache_marker


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        A list of messages with cache_control breakpoints injected.
        The input list and its contained dicts are preserved (shallow-copied as needed).
    """
    if not api_messages:
        return api_messages

    # Shallow copy the list to avoid modifying the input
    messages = api_messages.copy()

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices that need cache markers
    indices_to_modify = []
    breakpoints_used = 0

    if messages[0].get("role") == "system":
        indices_to_modify.append(0)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        indices_to_modify.append(idx)

    # Only copy and modify the specific messages that need breakpoints.
    # This is significantly faster than copy.deepcopy() for large histories.
    for idx in indices_to_modify:
        msg = messages[idx].copy()
        content = msg.get("content")

        # If content is a list, shallow copy it to avoid side effects on the original
        if isinstance(content, list):
            msg["content"] = content.copy()
            if msg["content"] and isinstance(msg["content"][-1], dict):
                msg["content"][-1] = msg["content"][-1].copy()

        _apply_cache_marker(msg, marker)
        messages[idx] = msg

    return messages
