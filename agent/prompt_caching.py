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

    Mutates the 'msg' dict. Caller should ensure 'msg' is a shallow copy if
    side effects on the original conversation history are not desired.
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
        # Shallow copy the content list and the last element to avoid side effects
        msg["content"] = list(content)
        last = content[-1]
        if isinstance(last, dict):
            msg["content"][-1] = dict(last)
            msg["content"][-1]["cache_control"] = cache_marker


def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system messages.

    Returns:
        Modified copy of the message list with cache_control breakpoints injected.
        Only the marked messages and their content fields are shallow-copied to
        avoid mutating the original conversation history.
    """
    if not api_messages:
        return api_messages

    # Shallow copy the message list
    messages = api_messages[:]

    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    # Identify indices that need markers
    indices_to_mark = []
    if messages[0].get("role") == "system":
        indices_to_mark.append(0)

    remaining = 4 - len(indices_to_mark)
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    indices_to_mark.extend(non_sys[-remaining:])

    for idx in indices_to_mark:
        # Shallow copy the dict before mutating it
        messages[idx] = messages[idx].copy()
        _apply_cache_marker(messages[idx], marker)

    return messages
