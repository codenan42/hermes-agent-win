## 2025-05-14 - [Shallow copy for prompt caching]
**Learning:** Using `copy.deepcopy` on large message histories (1000+ items) adds significant latency (~3ms per call) which becomes a bottleneck in the agent loop. Selective shallow copying (shallow copy list, then only shallow copy specific dicts/lists to be modified) provides a ~30x speedup while maintaining safety.
**Action:** Always prefer selective shallow copying over `copy.deepcopy` for large data structures that only need surgical modifications.
