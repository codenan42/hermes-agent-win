"""Anthropic prompt caching (system_and_3 strategy).

Reduces input token costs by ~75% on multi-turn conversations by caching
the conversation prefix. Uses 4 cache_control breakpoints (Anthropic max):
  1. System prompt (stable across all turns)
  2-4. Last 3 non-system messages (rolling window)

Pure functions -- no class state, no AIAgent dependency.
"""

import copy
from typing import Any, Dict, List


def _apply_cache_marker(msg: dict, cache_marker: dict) -> dict:
    """Add cache_control to a single message, handling all format variations.

    Returns a new dict (shallow copy with modifications) to avoid side effects
    without requiring a full deepcopy of the entire message list.
    """
    # Create a shallow copy of the message to avoid modifying the input
    new_msg = msg.copy()
    role = new_msg.get("role", "")
    content = new_msg.get("content")

    if role == "tool":
        new_msg["cache_control"] = cache_marker
        return new_msg

    if content is None or content == "":
        new_msg["cache_control"] = cache_marker
        return new_msg

    if isinstance(content, str):
        new_msg["content"] = [
            {"type": "text", "text": content, "cache_control": cache_marker}
        ]
        return new_msg

    if isinstance(content, list) and content:
        # Shallow copy the content list
        new_content = list(content)
        # Shallow copy the last content block to inject cache_control
        last = new_content[-1].copy()
        last["cache_control"] = cache_marker
        new_content[-1] = last
        new_msg["content"] = new_content
        return new_msg

    return new_msg


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        New list of messages with cache_control breakpoints injected.
        Uses shallow copying for efficiency (~40x faster than deepcopy).
    """
    if not api_messages:
        return []

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Shallow copy the list
    messages = list(api_messages)

    # Identify indices to modify
    indices_to_modify = []
    breakpoints_used = 0

    if messages[0].get("role") == "system":
        indices_to_modify.append(0)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_modify.extend(non_sys[-remaining:])

    # Only clone and modify the specific messages that need markers
    for idx in indices_to_modify:
        messages[idx] = _apply_cache_marker(messages[idx], marker)

    return messages
