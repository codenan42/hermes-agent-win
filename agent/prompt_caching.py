"""Anthropic prompt caching (system_and_3 strategy).

Reduces input token costs by ~75% on multi-turn conversations by caching
the conversation prefix. Uses 4 cache_control breakpoints (Anthropic max):
  1. System prompt (stable across all turns)
  2-4. Last 3 non-system messages (rolling window)

Pure functions -- no class state, no AIAgent dependency.
"""

from typing import Any, Dict, List


def _apply_cache_marker(msg: dict, cache_marker: dict) -> None:
    """Add cache_control to a single message, handling all format variations.

    Note: Expects msg to be a shallow copy if it came from a shared list.
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
        # Shallow copy the content list to avoid side effects on original
        new_content = list(content)
        msg["content"] = new_content
        last = new_content[-1]
        if isinstance(last, dict):
            # Shallow copy the last block to avoid side effects on original
            new_last = last.copy()
            new_last["cache_control"] = cache_marker
            new_content[-1] = new_last


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Uses selective shallow copying instead of deepcopy for performance.
    """
    if not api_messages:
        return []

    # Shallow copy the message list
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices that need caching (system prompt + last 3 non-system)
    indices_to_cache = []
    if messages[0].get("role") == "system":
        indices_to_cache.append(0)

    remaining = 4 - len(indices_to_cache)
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_cache.extend(non_sys[-remaining:])

    # Apply markers only to selected messages, shallow copying them first
    for idx in indices_to_cache:
        messages[idx] = messages[idx].copy()
        _apply_cache_marker(messages[idx], marker)

    return messages
