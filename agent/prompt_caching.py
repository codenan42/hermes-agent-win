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
    """Add cache_control to a single message, handling all format variations.

    Mutates the msg dict in-place, but copies nested content lists to avoid
    side effects on shared history.
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
        # Shallow copy the content list to avoid mutating original history
        new_content = list(content)
        last = new_content[-1]
        if isinstance(last, dict):
            # Shallow copy the last content block to avoid mutating original history
            new_content[-1] = last.copy()
            new_content[-1]["cache_control"] = cache_marker
        msg["content"] = new_content


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Optimization: uses selective shallow copying instead of full deepcopy.
    Only the targeted messages and their content blocks are copied.

    Returns:
        Optimized list of messages with cache_control breakpoints injected.
    """
    if not api_messages:
        return api_messages

    # Shallow copy the messages list
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify target messages for cache_control injection
    target_indices = []
    if messages[0].get("role") == "system":
        target_indices.append(0)

    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    remaining_slots = 4 - len(target_indices)
    if remaining_slots > 0:
        target_indices.extend(non_sys[-remaining_slots:])

    # Inject markers into shallow copies of target messages
    for idx in target_indices:
        msg_copy = messages[idx].copy()
        _apply_cache_marker(msg_copy, marker)
        messages[idx] = msg_copy

    return messages
