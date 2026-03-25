import copy
import time
import json

# Sample messages representing a long conversation
messages = []
for i in range(100):
    messages.append({"role": "user", "content": "Tell me a story about a robot."})
    messages.append({
        "role": "assistant",
        "content": "Once upon a time...",
        "tool_calls": [
            {
                "id": f"call_{i}",
                "type": "function",
                "function": {"name": "read_file", "arguments": '{"path": "story.txt"}'},
                "call_id": f"call_{i}",
                "response_item_id": f"fc_{i}"
            }
        ],
        "codex_reasoning_items": [{"type": "reasoning", "encrypted_content": "abc"}]
    })
    messages.append({
        "role": "tool",
        "tool_call_id": f"call_{i}",
        "content": "Success",
        "tool_name": "read_file"
    })

def benchmark(name, func, iterations=100):
    start = time.time()
    for _ in range(iterations):
        func()
    end = time.time()
    print(f"{name}: {end - start:.4f}s")

# 1. _prepare_anthropic_messages_for_api logic
def prepare_anthropic_deepcopy():
    transformed = copy.deepcopy(messages)
    # simulate transformation
    for msg in transformed:
        pass
    return transformed

def prepare_anthropic_shallow():
    transformed = [msg.copy() for msg in messages]
    # simulate transformation
    for msg in transformed:
        pass
    return transformed

print("--- _prepare_anthropic_messages_for_api ---")
benchmark("deepcopy", prepare_anthropic_deepcopy)
benchmark("shallow copy", prepare_anthropic_shallow)

# 2. _build_api_kwargs sanitization logic
def build_kwargs_deepcopy():
    sanitized_messages = copy.deepcopy(messages)
    for msg in sanitized_messages:
        msg.pop("codex_reasoning_items", None)
        tool_calls = msg.get("tool_calls")
        if isinstance(tool_calls, list):
            for tool_call in tool_calls:
                if isinstance(tool_call, dict):
                    tool_call.pop("call_id", None)
                    tool_call.pop("response_item_id", None)
    return sanitized_messages

def build_kwargs_selective():
    sanitized_messages = []
    for msg in messages:
        needs_copy = "codex_reasoning_items" in msg
        if not needs_copy:
            tool_calls = msg.get("tool_calls")
            if isinstance(tool_calls, list):
                for tc in tool_calls:
                    if isinstance(tc, dict) and ("call_id" in tc or "response_item_id" in tc):
                        needs_copy = True
                        break

        if needs_copy:
            new_msg = msg.copy()
            new_msg.pop("codex_reasoning_items", None)
            tool_calls = new_msg.get("tool_calls")
            if isinstance(tool_calls, list):
                new_msg["tool_calls"] = [tc.copy() for tc in tool_calls]
                for tc in new_msg["tool_calls"]:
                    if isinstance(tc, dict):
                        tc.pop("call_id", None)
                        tc.pop("response_item_id", None)
            sanitized_messages.append(new_msg)
        else:
            sanitized_messages.append(msg)
    return sanitized_messages

print("\n--- _build_api_kwargs sanitization ---")
benchmark("deepcopy", build_kwargs_deepcopy)
benchmark("selective copy", build_kwargs_selective)

# 3. apply_anthropic_cache_control logic
def apply_cache_deepcopy():
    msgs = copy.deepcopy(messages)
    # simplified logic: mark first and last 3
    if msgs[0]["role"] == "system":
        msgs[0]["cache_control"] = {"type": "ephemeral"}
    for m in msgs[-3:]:
        m["cache_control"] = {"type": "ephemeral"}
    return msgs

def apply_cache_selective():
    msgs = messages.copy()
    # simplified logic: mark first and last 3
    # needs to copy the messages being modified
    if msgs[0]["role"] == "system":
        msgs[0] = msgs[0].copy()
        msgs[0]["cache_control"] = {"type": "ephemeral"}

    for i in range(max(0, len(msgs)-3), len(msgs)):
        msgs[i] = msgs[i].copy()
        msgs[i]["cache_control"] = {"type": "ephemeral"}
    return msgs

print("\n--- apply_anthropic_cache_control ---")
benchmark("deepcopy", apply_cache_deepcopy)
benchmark("selective copy", apply_cache_selective)
