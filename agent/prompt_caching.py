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
        List of messages with cache_control breakpoints injected. Selective deepcopy
        is used to ensure the input list and its contents are not mutated.
    """
    if not api_messages:
        return []

    # Shallow copy the list to avoid mutating the caller's list
    messages = api_messages.copy()

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify breakpoints to cache
    breakpoints_to_cache = []
    breakpoints_used = 0

    if messages[0].get("role") == "system":
        breakpoints_to_cache.append(0)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        breakpoints_to_cache.append(idx)

    # Only deepcopy and modify the messages that need caching to avoid unnecessary
    # overhead for long conversation histories.
    for idx in breakpoints_to_cache:
        messages[idx] = copy.deepcopy(messages[idx])
        _apply_cache_marker(messages[idx], marker)

    return messages
