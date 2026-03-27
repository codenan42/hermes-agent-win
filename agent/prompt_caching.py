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

    WARNING: This function mutates the msg dict in place.
    It is used by apply_anthropic_cache_control after shallow copying.
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
        # We must clone the list to avoid mutating the original message's content list
        new_content = list(content)
        last = new_content[-1]
        if isinstance(last, dict):
            # We must clone the last content block to avoid mutating the original
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
    Optimized to avoid full deepcopy of the message list.

    Returns:
        Shallow copy of the list with specific modified messages cloned.
    """
    if not api_messages:
        return api_messages

    # Shallow copy the list to avoid mutating the original
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    breakpoints_used = 0

    if messages[0].get("role") == "system":
        # Clone the message before mutating it
        messages[0] = messages[0].copy()
        _apply_cache_marker(messages[0], marker)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        # Clone the message before mutating it
        messages[idx] = messages[idx].copy()
        _apply_cache_marker(messages[idx], marker)

    return messages
