## 2025-05-15 - Message history deepcopy bottleneck
**Learning:** `copy.deepcopy()` on large conversation histories (500+ messages) is surprisingly slow, adding ~8-10ms of overhead per API iteration. For agents with long-running tool loops, this accumulates significantly.
**Action:** Use selective shallow copying for message history processing. Shallow copy the list and only clone individual message objects that actually require modification (e.g., for sanitization or prompt caching).

## 2025-05-15 - Redundant SessionDB schema initialization
**Learning:** Re-running `_init_schema()` on every `SessionDB` instantiation (common in gateway/CLI restarts) adds ~0.1-0.2ms of overhead. While small, this contributes to warm-start latency in high-frequency environments.
**Action:** Use a class-level cache (`_initialized_paths`) to skip schema checks for database paths that have already been initialized in the current process.
