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

    Note: msg must be a copy that is safe to mutate in-place.
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
        # Mutating msg['content'] from string to list is safe since msg is a copy.
        msg["content"] = [
            {"type": "text", "text": content, "cache_control": cache_marker}
        ]
        return

    if isinstance(content, list) and content:
        # Shallow copy the content list to avoid mutating the original message's content.
        new_content = list(content)
        last = new_content[-1]
        # Shallow copy the last part before injecting cache_control.
        if isinstance(last, dict):
            last_part = last.copy()
            last_part["cache_control"] = cache_marker
            new_content[-1] = last_part
            msg["content"] = new_content


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.
    Uses selective shallow copying for performance instead of full deepcopy.

    Returns:
        A list of messages with cache_control breakpoints injected.
        Only modified messages are copied; others reference the original dicts.
    """
    if not api_messages:
        return []

    # Shallow copy the list so we can replace specific message dicts.
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    breakpoints_used = 0

    # 1. Always cache the system prompt if present (breakpoint 1)
    if messages[0].get("role") == "system":
        msg = messages[0].copy()
        _apply_cache_marker(msg, marker)
        messages[0] = msg
        breakpoints_used += 1

    # 2. Cache up to the last 3 non-system messages (breakpoints 2-4)
    remaining = 4 - breakpoints_used
    non_sys_indices = [
        i for i, m in enumerate(messages) if m.get("role") != "system"
    ]

    for idx in non_sys_indices[-remaining:]:
        msg = messages[idx].copy()
        _apply_cache_marker(msg, marker)
        messages[idx] = msg

    return messages
