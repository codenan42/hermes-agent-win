"""Anthropic prompt caching (system_and_3 strategy).

Reduces input token costs by ~75% on multi-turn conversations by caching
the conversation prefix. Uses 4 cache_control breakpoints (Anthropic max):
  1. System prompt (stable across all turns)
  2-4. Last 3 non-system messages (rolling window)

Pure functions -- no class state, no AIAgent dependency.
"""

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
        Shallow copy of messages list with specific messages shallow-copied and
        cache_control breakpoints injected. This avoids the high overhead of
        copy.deepcopy while preventing side effects on the input list.
    """
    if not api_messages:
        return []

    # Shallow copy the list to avoid modifying the input list
    messages = api_messages.copy()

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices to modify
    indices_to_modify = []
    breakpoints_used = 0

    if messages[0].get("role") == "system":
        indices_to_modify.append(0)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        if idx not in indices_to_modify:
            indices_to_modify.append(idx)

    for idx in indices_to_modify:
        # Shallow copy the message dict so we don't modify the original
        msg = messages[idx].copy()

        # If content is a list, shallow copy it and its last element to avoid side effects
        content = msg.get("content")
        if isinstance(content, list):
            new_content = content.copy()
            if new_content and isinstance(new_content[-1], dict):
                new_content[-1] = new_content[-1].copy()
            msg["content"] = new_content

        _apply_cache_marker(msg, marker)
        messages[idx] = msg

    return messages
