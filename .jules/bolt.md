## 2025-05-14 - Selective Shallow Copying for Message Histories

**Learning:** `copy.deepcopy` is extremely expensive for large conversation histories (e.g., 500-1000 messages) in Python. In the `apply_anthropic_cache_control` function, deep-copying a 1000-message history took ~3-4ms, while most of the data was never modified.

**Action:** Use selective shallow copying when modifying only a small subset of a large data structure. By shallow-copying the list and then shallow-copying/modifying only the specific message dictionaries that need `cache_control` markers, we achieved a ~25-40x speedup (~0.1ms latency), reducing overhead significantly for long-running agent sessions.
