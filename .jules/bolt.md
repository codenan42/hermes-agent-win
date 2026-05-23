## 2025-05-15 - [Consolidated Skill Loading]
**Learning:** Loading and parsing 90+ skill files (YAML frontmatter) is a significant bottleneck in system prompt construction, especially when done multiple times per turn. Redundant I/O and parsing can be halved by consolidating metadata loading. CSafeLoader provides an additional 5-8x speedup over pure Python SafeLoader.
**Action:** Always prefer consolidated I/O for batch file processing and use CSafeLoader for YAML parsing when performance is critical in hot paths like prompt construction.
