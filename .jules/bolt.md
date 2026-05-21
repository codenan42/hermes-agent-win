## 2025-05-14 - Optimized Skill Discovery with consolidated I/O and CSafeLoader
**Learning:** PyYAML's pure-Python `SafeLoader` is significantly slower than `CSafeLoader`. In this codebase, the skill discovery process was performing redundant I/O and parsing by calling multiple functions that each read and parsed the same SKILL.md files.
**Action:** Always prefer `CSafeLoader` when available for batch YAML parsing. Consolidate metadata extraction into a single-pass function to minimize I/O and redundant parsing when iterating over large numbers of files.
