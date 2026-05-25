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
    Optimized to use selective shallow copies instead of a full deep copy of history.

    Returns:
        New list of messages with cache_control breakpoints injected.
    """
    if not api_messages:
        return []

    # Shallow copy the list to avoid mutating the caller's list
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices that need cache_control breakpoints
    indices_to_modify = []
    if messages[0].get("role") == "system":
        indices_to_modify.append(0)

    remaining = 4 - len(indices_to_modify)
    non_sys_indices = [
        i for i in range(len(messages)) if messages[i].get("role") != "system"
    ]
    indices_to_modify.extend(non_sys_indices[-remaining:])

    # Shallow copy and modify ONLY the specific messages needing breakpoints.
    # This avoids O(N) deep-copy overhead for long conversation histories.
    for idx in indices_to_modify:
        msg = messages[idx].copy()
        content = msg.get("content")
        # If content is a list of blocks, shallow copy it to avoid in-place mutation
        # of the original message's content blocks by _apply_cache_marker.
        if isinstance(content, list):
            msg["content"] = [c.copy() for c in content]

        _apply_cache_marker(msg, marker)
        messages[idx] = msg

    return messages
