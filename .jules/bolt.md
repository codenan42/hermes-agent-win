## 2026-05-02 - Consolidated SKILL.md reads and optimized YAML parsing
**Learning:** Redundant file I/O and slow YAML parsing (PyYAML without CLoader) can significantly impact system prompt assembly time, especially as the number of skills grows. Consolidating reads and using CSafeLoader provided a ~2.3x speedup.
**Action:** Always check for redundant file reads in loops and prefer faster parsers (like PyYAML's CLoader) when available.
