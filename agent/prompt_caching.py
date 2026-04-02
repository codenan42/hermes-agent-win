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

    Note: This function mutates the provided message dictionary. The caller
    should ensure 'msg' is a copy if the original must be preserved.
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
        # Shallow copy the content list to avoid mutating the original
        msg["content"] = content[:]
        last = msg["content"][-1]
        if isinstance(last, dict):
            # Shallow copy the last item dictionary to avoid mutating the original
            msg["content"][-1] = last.copy()
            msg["content"][-1]["cache_control"] = cache_marker


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        List of messages with cache_control breakpoints injected. Original
        messages and their nested objects are preserved via selective shallow copies.
    """
    if not api_messages:
        return []

    # Shallow copy the messages list.
    # We will shallow copy individual message dicts only when they need mutation.
    messages = api_messages[:]

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    breakpoints_used = 0

    indices_to_mark = []
    if messages[0].get("role") == "system":
        indices_to_mark.append(0)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_mark.extend(non_sys[-remaining:])

    for idx in indices_to_mark:
        # Shallow copy the message dict before mutation
        msg_copy = messages[idx].copy()
        _apply_cache_marker(msg_copy, marker)
        messages[idx] = msg_copy

    return messages
