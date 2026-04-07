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

    Note: This function mutates the provided msg dictionary. The caller should
    ensure they pass a shallow copy of the message if the original must remain
    unmodified.
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
        # Convert string content to Anthropic content-block list with cache_control
        msg["content"] = [
            {"type": "text", "text": content, "cache_control": cache_marker}
        ]
        return

    if isinstance(content, list) and content:
        # Shallow copy the list and the last element to avoid side effects
        new_content = content[:]
        last = new_content[-1]
        if isinstance(last, dict):
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

    Uses selective shallow copying instead of copy.deepcopy for performance.
    Only the messages receiving markers are cloned.

    Returns:
        A list of messages with cache_control breakpoints injected.
    """
    if not api_messages:
        return api_messages

    # Shallow copy the list of messages
    messages = api_messages[:]

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices that should receive markers
    indices_to_mark = []
    breakpoints_used = 0

    if messages[0].get("role") == "system":
        indices_to_mark.append(0)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_mark.extend(non_sys[-remaining:])

    # Apply markers to shallow-copied message dictionaries
    for idx in indices_to_mark:
        msg = messages[idx].copy()
        _apply_cache_marker(msg, marker)
        messages[idx] = msg

    return messages
