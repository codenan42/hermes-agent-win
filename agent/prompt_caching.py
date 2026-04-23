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
        Shallow copy of messages list with specific marked message dicts shallow-copied.
        Avoids full deepcopy for performance on large histories.
    """
    if not api_messages:
        return api_messages

    # Shallow copy the list to avoid mutating the caller's list
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices to mark for caching
    indices_to_mark = []
    if messages[0].get("role") == "system":
        indices_to_mark.append(0)

    breakpoints_remaining = 4 - len(indices_to_mark)
    non_sys_indices = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_mark.extend(non_sys_indices[-breakpoints_remaining:])

    for idx in indices_to_mark:
        # Shallow copy the message dict before modification
        msg = messages[idx].copy()

        # If content is a list, we MUST shallow copy it to avoid mutating original history
        content = msg.get("content")
        if isinstance(content, list):
            msg["content"] = list(content)
            if msg["content"] and isinstance(msg["content"][-1], dict):
                # Shallow copy the specific content block we'll be marking
                msg["content"][-1] = msg["content"][-1].copy()

        messages[idx] = msg
        _apply_cache_marker(msg, marker)

    return messages
