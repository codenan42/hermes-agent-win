## 2025-05-14 - Selective Shallow Copying for Message Histories
**Learning:** Using `copy.deepcopy` on large message histories (e.g., 500+ messages) in every turn introduces measurable latency (~1.4ms per call). Since most turns only modify the very end of the history (e.g., for prompt caching or sanitization), deepcopying the entire list is wasteful.
**Action:** Replace full-list `copy.deepcopy` with a shallow list copy and only deepcopy the specific message objects that require mutation. This reduced latency by >20x (from ~1.4ms to ~0.06ms) for 500 messages.
