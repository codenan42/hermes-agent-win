## 2025-05-15 - [Selective Shallow Copy for Prompt Caching]
**Learning:** `copy.deepcopy` of large message histories (1000+ messages) is a significant bottleneck (~17ms per call). Selective shallow copying of only modified parts reduces this to <0.2ms.
**Action:** Use selective shallow copying (list copy + targeted dict/list copies) when modifying large nested structures where most of the data remains unchanged.
