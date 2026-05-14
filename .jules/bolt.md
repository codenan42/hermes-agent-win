## 2026-05-14 - Optimize Prompt Caching with Selective Shallow Copying
**Learning:** Using `copy.deepcopy` on large conversation histories (500+ messages) during prompt assembly creates a significant O(N) bottleneck, taking ~0.5s per turn. Selective shallow copying of only the affected messages (max 4 for Anthropic caching) reduces overhead to <0.01s.
**Action:** Always prefer selective shallow copying over `copy.deepcopy` when modifying a small number of elements in a large list, ensuring nested structures are also shallow-copied if they need mutation to avoid side effects.
