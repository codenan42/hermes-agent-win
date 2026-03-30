## 2025-05-15 - [Optimize prompt caching with selective shallow copying]
**Learning:** `copy.deepcopy` on large message histories (e.g. 1000 messages) is a significant bottleneck (~2.9ms per turn). Since most messages in a history are never modified by the agent's logic (only the system prompt and the last few messages), we can achieve a >25x speedup by switching to selective shallow copying.
**Action:** Always prefer selective shallow copying (list copy + dictionary copy for modified elements) over `copy.deepcopy` when processing large history lists where only a few items are modified.
