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

    Note: assumes 'msg' is already a shallow copy that can be safely mutated.
    Internal structures like 'content' lists are shallow-copied before mutation
    to ensure the original input remains untouched.
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
        # Shallow copy the content list to avoid mutating the original
        new_content = list(content)
        last = new_content[-1]
        if isinstance(last, dict):
            # Shallow copy the last dict to avoid mutating the original
            new_content[-1] = last.copy()
            new_content[-1]["cache_control"] = cache_marker
        msg["content"] = new_content


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Performance: Uses selective shallow copying instead of deepcopy to avoid O(N)
    overhead on large conversation histories.

    Returns:
        New list of messages with cache_control breakpoints injected.
    """
    if not api_messages:
        return []

    # Shallow copy the outer list
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices to modify (max 4 breakpoints)
    indices_to_modify = []
    if messages[0].get("role") == "system":
        indices_to_modify.append(0)

    remaining = 4 - len(indices_to_modify)
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_modify.extend(non_sys[-remaining:])

    # Only copy and modify the specific messages that need breakpoints
    for idx in set(indices_to_modify):
        # Shallow copy the message dict
        messages[idx] = messages[idx].copy()
        _apply_cache_marker(messages[idx], marker)

    return messages
