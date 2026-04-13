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
        New list of messages with cache_control breakpoints injected into copies
        of the affected messages.
    """
    if not api_messages:
        return api_messages

    # Shallow copy the list to avoid mutating the caller's list
    messages = api_messages.copy()

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices to modify: system prompt + up to 3 most recent messages
    indices_to_modify = []
    if messages[0].get("role") == "system":
        indices_to_modify.append(0)

    # Remaining breakpoints (up to 4 total) for the most recent non-system messages
    remaining = 4 - len(indices_to_modify)
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_modify.extend(non_sys[-remaining:])

    # Apply markers ONLY to deep copies of the affected messages.
    # We use deepcopy for these specific messages because _apply_cache_marker
    # may mutate nested structures like the 'content' list.
    for idx in indices_to_modify:
        messages[idx] = copy.deepcopy(api_messages[idx])
        _apply_cache_marker(messages[idx], marker)

    return messages
