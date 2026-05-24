## 2025-05-22 - Optimized Skill Indexing
**Learning:** `build_skills_system_prompt` was performing two separate read/parse passes per skill file (one for metadata, one for conditions). Consolidating these into a single pass and using `yaml.CSafeLoader` significantly reduces I/O and CPU overhead.
**Action:** Always prefer consolidated I/O when multiple pieces of metadata are needed from the same file, and use the optimized C-based YAML loader for batch processing.
