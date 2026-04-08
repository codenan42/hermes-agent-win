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

    Mutates msg in-place. Callers must ensure msg is a copy.
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
        # Shallow copy of the content list so we can modify the last element
        # without affecting the original list.
        content_copy = content[:]
        msg["content"] = content_copy
        last = content_copy[-1]
        if isinstance(last, dict):
            # Shallow copy of the last part dict to add cache_control
            content_copy[-1] = last.copy()
            content_copy[-1]["cache_control"] = cache_marker


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        New list of messages (shallow copy) with targeted deep copies for modified messages.
    """
    if not api_messages:
        return []

    # Shallow copy of the list
    messages = api_messages[:]

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices that need markers
    indices_to_modify = []
    if messages[0].get("role") == "system":
        indices_to_modify.append(0)

    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    remaining = 4 - len(indices_to_modify)
    if remaining > 0:
        for idx in non_sys[-remaining:]:
            if idx not in indices_to_modify:
                indices_to_modify.append(idx)

    # Only copy and modify the messages that actually need a breakpoint.
    # The rest remain as references to the original messages.
    for idx in indices_to_modify:
        msg = messages[idx].copy()
        _apply_cache_marker(msg, marker)
        messages[idx] = msg

    return messages
