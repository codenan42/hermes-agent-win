# Bolt's Journal - Critical Learnings Only

## 2026-05-25 - Selective Shallow Copying in Prompt Caching
**Learning:** Using `copy.deepcopy()` on entire message histories in `apply_anthropic_cache_control` creates a significant O(N) overhead as conversations grow. For a 2000-message history, deep copying can take ~500ms, while selective shallow copying takes ~15ms (a ~33x speedup). Shallow copying the list and only copying the specific message dictionaries that receive `cache_control` markers preserves immutability for the caller while drastically reducing CPU and memory pressure.
**Action:** Always prefer selective shallow copies over full deep copies when modifying large data structures where only a few elements change. Ensure nested structures (like message `content` lists) are also shallow-copied if they are modified in-place.
