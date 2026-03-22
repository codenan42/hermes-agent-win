import time
import copy
from typing import List, Dict, Any

# Mocking the current implementation
def _apply_cache_marker_current(msg: dict, cache_marker: dict) -> None:
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

def apply_anthropic_cache_control_current(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    messages = copy.deepcopy(api_messages)
    if not messages:
        return messages
    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"
    breakpoints_used = 0
    if messages[0].get("role") == "system":
        _apply_cache_marker_current(messages[0], marker)
        breakpoints_used += 1
    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        _apply_cache_marker_current(messages[idx], marker)
    return messages

# Mocking the optimized implementation
def _apply_cache_marker_optimized(msg: dict, cache_marker: dict) -> dict:
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
        new_content = list(content)
        last = new_content[-1]
        if isinstance(last, dict):
            new_content[-1] = last.copy()
            new_content[-1]["cache_control"] = cache_marker
        new_msg["content"] = new_content
        return new_msg
    return new_msg

def apply_anthropic_cache_control_optimized(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
) -> List[Dict[str, Any]]:
    if not api_messages:
        return api_messages
    messages = list(api_messages)
    marker = {"type": "ephemeral"}
    if cache_ttl == "1h":
        marker["ttl"] = "1h"

    indices_to_modify = []
    breakpoints_used = 0
    if messages[0].get("role") == "system":
        indices_to_modify.append(0)
        breakpoints_used += 1
    remaining = 4 - breakpoints_used
    non_sys = [i for i in range(len(messages)) if messages[i].get("role") != "system"]
    for idx in non_sys[-remaining:]:
        indices_to_modify.append(idx)

    for idx in indices_to_modify:
        messages[idx] = _apply_cache_marker_optimized(messages[idx], marker)
    return messages

# Generate a large message list
num_messages = 500
large_messages = []
large_messages.append({"role": "system", "content": "You are a helpful assistant." * 100})
for i in range(num_messages):
    role = "user" if i % 2 == 0 else "assistant"
    large_messages.append({"role": role, "content": f"This is message number {i}. " * 50})

# Benchmark
iterations = 100

start_time = time.time()
for _ in range(iterations):
    _ = apply_anthropic_cache_control_current(large_messages)
end_time = time.time()
current_duration = end_time - start_time
print(f"Current implementation: {current_duration:.4f} seconds for {iterations} iterations")

start_time = time.time()
for _ in range(iterations):
    _ = apply_anthropic_cache_control_optimized(large_messages)
end_time = time.time()
optimized_duration = end_time - start_time
print(f"Optimized implementation: {optimized_duration:.4f} seconds for {iterations} iterations")

speedup = current_duration / optimized_duration
print(f"Speedup: {speedup:.2f}x")
