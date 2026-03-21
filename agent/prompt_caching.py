"""Anthropic prompt caching (system_and_3 strategy).

Reduces input token costs by ~75% on multi-turn conversations by caching
the conversation prefix. Uses 4 cache_control breakpoints (Anthropic max):
  1. System prompt (stable across all turns)
  2-4. Last 3 non-system messages (rolling window)

Pure functions -- no class state, no AIAgent dependency.
"""

from typing import Any, Dict, List


def _apply_cache_marker(msg: dict, cache_marker: dict) -> dict:
    """Add cache_control to a single message, handling all format variations.

    Returns a new shallow-copied dictionary if modifications are made,
    otherwise returns the original message.
    """
    new_msg = msg.copy()
    role = new_msg.get("role", "")
    content = new_msg.get("content")

    if role == "tool":
        new_msg["cache_control"] = cache_marker
        return new_msg

    if content is None or content == "":
        new_msg["cache_control"] = cache_marker
        return new_msg

    if isinstance(content, str):
        new_msg["content"] = [
            {"type": "text", "text": content, "cache_control": cache_marker}
        ]
        return new_msg

    if isinstance(content, list) and content:
        # Shallow copy content list so we don't mutate shared history
        new_content = list(content)
        last = new_content[-1]
        if isinstance(last, dict):
            new_last = last.copy()
            new_last["cache_control"] = cache_marker
            new_content[-1] = new_last
        new_msg["content"] = new_content
        return new_msg

    return new_msg


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        New list of messages with cache_control breakpoints injected.
        Only modified messages are shallow-copied; others are reused.
    """
    if not api_messages:
        return []

    # Shallow copy the message list
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices to modify
    indices_to_modify = []
    if messages[0].get("role") == "system":
        indices_to_modify.append(0)

    breakpoints_used = len(indices_to_modify)
    remaining = 4 - breakpoints_used

    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_modify.extend(non_sys[-remaining:])

    # Apply markers only to the target messages
    for idx in indices_to_modify:
        messages[idx] = _apply_cache_marker(messages[idx], marker)

    return messages
