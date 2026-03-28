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

    NOTE: This function MUTATES the input dictionary. The caller is responsible
    for passing a copy if the original must be preserved.
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
        A new list of messages with cache_control breakpoints injected.
        Original messages are NOT mutated.
    """
    if not api_messages:
        return []

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices that need markers
    indices_to_mark = set()
    breakpoints_used = 0

    if api_messages[0].get("role") == "system":
        indices_to_mark.add(0)
        breakpoints_used += 1

    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(api_messages)) if api_messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        indices_to_mark.add(idx)

    # Build new list, only copying/modifying marked messages.
    # This is significantly faster than copy.deepcopy for large histories.
    new_messages = []
    for i, msg in enumerate(api_messages):
        if i in indices_to_mark:
            # Deepish copy of just this message to avoid mutating original history
            # We need to copy content if it's a list too.
            new_msg = msg.copy()
            content = new_msg.get("content")
            if isinstance(content, list):
                new_msg["content"] = [c.copy() if isinstance(c, dict) else c for c in content]

            _apply_cache_marker(new_msg, marker)
            new_messages.append(new_msg)
        else:
            new_messages.append(msg)

    return new_messages
