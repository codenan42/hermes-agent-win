## 2025-05-15 - Optimize Anthropic prompt caching with selective shallow copying
**Learning:** Using `copy.deepcopy()` on large message histories (500+ messages) is a major performance bottleneck, taking ~4.5ms per call. Selective shallow copying of only the modified messages reduces this to ~0.15ms.
**Action:** Always prefer selective shallow copying over `deepcopy` for large data structures where only a small subset of the data is modified. Ensure nested structures (like message content lists) are also shallow-copied to avoid side effects.
