## 2026-05-25 - Consolidating I/O and utilizing C-accelerated YAML parsing
**Learning:** Batch parsing of skill frontmatter (91+ files) during system prompt construction was a bottleneck. Redundant file I/O and pure-Python YAML parsing were causing the operation to take ~244ms.
**Action:** Consolidate redundant file reads by returning parsed data from helper functions, and use `yaml.CSafeLoader` for a significant speedup in parsing performance.
