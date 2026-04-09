# Bolt's Journal - Critical Learnings

## 2025-05-14 - Optimize prompt caching by replacing deepcopy with targeted shallow copy
**Learning:** `copy.deepcopy` on large message histories (500+ messages) is a significant bottleneck in the API request pipeline. Since only a few messages (system + last 3) are ever modified for Anthropic prompt caching, copying the entire list is redundant.
**Action:** Use a shallow copy for the message list and only `copy.deepcopy` the specific message dictionaries that will be mutated. This preserves the original history while reducing processing time by over 25x for large histories.
