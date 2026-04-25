## 2025-05-15 - Consolidate skill parsing in prompt builder
**Learning:** Redundant file I/O and YAML parsing for skill indexing significantly slows down system prompt assembly. Consolidation into a single pass with optimized file reading (first 2KB) provides a measurable speedup.
**Action:** Avoid calling multiple helper functions that independently read and parse the same configuration or metadata files. Consolidate into a single "load_metadata" style function.
