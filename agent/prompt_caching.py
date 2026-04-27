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
    """Add cache_control to a single message, handling all format variations.

    Note: The caller MUST ensure 'msg' is a shallow copy if it came from
    a shared history to avoid side effects. This function further shallow
    copies nested content structures if they need modification.
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
        msg["content"] = [
            {"type": "text", "text": content, "cache_control": cache_marker}
        ]
        return

    if isinstance(content, list) and content:
        # Shallow copy the list to avoid mutating the original message's content list
        msg["content"] = list(content)
        last = msg["content"][-1]
        if isinstance(last, dict):
            # Shallow copy the last part if we're going to inject cache_control
            msg["content"][-1] = last.copy()
            msg["content"][-1]["cache_control"] = cache_marker


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        List of messages with cache_control breakpoints. Messages that were modified
        are shallow copies to avoid side effects on the input list.
    """
    if not api_messages:
        return api_messages

    # Identify indices that need cache markers
    indices_to_cache = set()
    breakpoints_used = 0

    if api_messages[0].get("role") == "system":
        indices_to_cache.add(0)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(api_messages)) if api_messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        indices_to_cache.add(idx)

    # Reconstruct message list with selective shallow copying
    messages = []
    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    for i, msg in enumerate(api_messages):
        if i in indices_to_cache:
            # Copy only the message we're about to modify
            new_msg = msg.copy()
            _apply_cache_marker(new_msg, marker)
            messages.append(new_msg)
        else:
            # Keep original reference for unmodified messages
            messages.append(msg)

    return messages
