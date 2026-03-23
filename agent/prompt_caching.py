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

    Returns a shallow copy of the message with cache_control injected.
    Does not mutate the input message.
    """
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
        # Shallow copy the content list to avoid mutating the original
        new_content = list(content)
        last = new_content[-1]
        if isinstance(last, dict):
            # Shallow copy the last block before adding cache_control
            new_content[-1] = last.copy()
            new_content[-1]["cache_control"] = cache_marker
        new_msg["content"] = new_content

    return new_msg


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        A copy of messages with cache_control breakpoints injected.
        Optimized to avoid copy.deepcopy by using selective shallow copying.
    """
    if not api_messages:
        return []

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify which message indices need cache markers
    sys_idx = 0 if api_messages[0].get("role") == "system" else None
    breakpoints_used = 1 if sys_idx is not None else 0

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(api_messages)) if api_messages[i].get("role") != "system"]
    cache_indices = set(non_sys[-remaining:])
    if sys_idx is not None:
        cache_indices.add(sys_idx)

    # Reconstruct the list, only copying messages that need markers
    messages = []
    for i, msg in enumerate(api_messages):
        if i in cache_indices:
            messages.append(_apply_cache_marker(msg, marker))
        else:
            messages.append(msg)

    return messages
