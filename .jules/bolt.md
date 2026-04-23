## 2025-05-15 - [Message History Optimization]
**Learning:** `copy.deepcopy` on large message histories (500+ messages) is a significant bottleneck, taking ~1.7ms to ~17ms per call depending on payload size. Replacing it with selective shallow copying (copy-on-write) provides a 15x to 100x speedup while maintaining safety.
**Action:** Always prefer selective shallow copying over `copy.deepcopy` when processing large lists of dictionaries where only a few items need modification. Shallow copy the list first, then shallow copy and modify specific items.
