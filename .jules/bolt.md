## 2026-05-05 - [Optimizing Skills Indexing]
**Learning:** Redundant file I/O and pure-Python YAML parsing in tight loops (like scanning 90+ skill files for system prompt assembly) significantly degrade performance. Consolidating reads and using `CSafeLoader` provides massive wins.
**Action:** Always look for repeated `read_text()` calls on the same file path and consolidate them. Use `CSafeLoader` for YAML parsing if performance matters.
