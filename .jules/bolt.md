## 2025-05-22 - [Optimization of `copy.deepcopy` in `agent/prompt_caching.py`]
**Learning:** `copy.deepcopy` is extremely slow on large list of dictionaries like conversation histories. Selective shallow copying (using `list.copy()` and `dict.copy()`) is much faster and safe if only specific parts of the structure need to be modified.
**Action:** Always check if `copy.deepcopy` is necessary. If only a few elements in a nested structure need change, prefer selective shallow copying to maintain immutability without the performance hit.
