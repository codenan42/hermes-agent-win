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

    Expects msg to be a shallow copy if it was shared.
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
        # Shallow copy the content list to avoid side effects on the original history.
        new_content = list(content)
        last = new_content[-1]
        if isinstance(last, dict):
            # Shallow copy the last block dictionary to safely inject cache_control.
            last = last.copy()
            last["cache_control"] = cache_marker
            new_content[-1] = last
        msg["content"] = new_content


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        List of messages with cache_control breakpoints injected. Uses selective
        shallow copying for performance instead of copy.deepcopy.
    """
    if not api_messages:
        return api_messages

    # Shallow copy the outer list.
    messages = list(api_messages)

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify target indices for cache breakpoints.
    target_indices = []
    if messages[0].get("role") == "system":
        target_indices.append(0)

    remaining = 4 - len(target_indices)
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    target_indices.extend(non_sys[-remaining:])

    # Apply markers only to targeted messages.
    # Each modified message is shallow-cloned to protect the original list.
    for idx in target_indices:
        msg = messages[idx].copy()
        _apply_cache_marker(msg, marker)
        messages[idx] = msg

    return messages
