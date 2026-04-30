## 2025-05-15 - Consolidate skill file reads and parsing
**Learning:** Redundant I/O and parsing of frontmatter in `build_skills_system_prompt` (once for compatibility/description and once for conditions) caused significant overhead when scaling to many skills. Using `f.read(limit)` instead of `Path.read_text()[:limit]` is also slightly more efficient for memory and prevents reading large files.
**Action:** Always look for multiple functions reading the same metadata from the same file in a loop. Consolidate into a single pass and use targeted reads.
