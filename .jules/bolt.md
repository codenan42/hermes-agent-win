## 2025-05-13 - Consolidated Skill Parsing and CSafeLoader
**Learning:** Redundant I/O and pure-Python YAML parsing are major bottlenecks when scanning large directories like `skills/` (91+ files). Consolidating multiple file reads/parses into a single pass and using `CSafeLoader` provides significant wins (~1.6x overall, ~8.5x for frontmatter parsing).
**Action:** Always prefer `CSafeLoader` (with fallback) for batch YAML processing. Look for opportunities to consolidate multiple passes over the same directory/files in prompt assembly logic.
