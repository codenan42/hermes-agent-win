## 2025-05-14 - Consolidating Skill File Parsing
**Learning:** Redundant I/O and parsing in loops (e.g., reading the same SKILL.md twice for description and then for conditions) significantly impacts performance when scaling to many items. Also, Path.read_text() reads the entire file before slicing, which is wasteful for preamble extraction.
**Action:** Consolidate multiple reads/parses into a single-pass function. Use open() with f.read(N) to only fetch the necessary bytes from the start of the file.
