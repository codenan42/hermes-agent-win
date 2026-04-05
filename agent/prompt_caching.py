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

    NOTE: Mutates the input msg in-place to maintain compatibility with existing tests.
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
        New list of messages with cache_control breakpoints injected.
        Only modified messages and their relevant nested parts are shallow-copied;
        others are reused.
    """
    if not api_messages:
        return api_messages

    # Shallow copy the top-level list
    messages = api_messages[:]

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    breakpoints_used = 0
    indices_to_cache = []

    if messages[0].get("role") == "system":
        indices_to_cache.append(0)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_cache.extend(non_sys[-remaining:])

    # Only copy and modify the messages that need markers
    for idx in indices_to_cache:
        msg = messages[idx].copy()
        content = msg.get("content")

        # If content is a list, we must shallow-copy it and its last item
        # to avoid mutating the original api_messages.
        if isinstance(content, list) and content:
            new_content = list(content)
            last = new_content[-1]
            if isinstance(last, dict):
                new_content[-1] = last.copy()
            msg["content"] = new_content

        _apply_cache_marker(msg, marker)
        messages[idx] = msg

    return messages
