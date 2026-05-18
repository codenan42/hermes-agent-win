## 2025-05-15 - Redundant I/O and YAML parsing in Skills System
**Learning:** `build_skills_system_prompt` previously called `_parse_skill_file` and `_read_skill_conditions` separately for every skill file, causing redundant file reads and YAML frontmatter parsing. Consolidating into `_load_skill_data` halves the I/O and parsing overhead. Additionally, using `yaml.CSafeLoader` instead of `yaml.SafeLoader` provides ~7x speedup in frontmatter parsing.
**Action:** Use consolidated loaders for multi-step file processing and prefer `CSafeLoader` for parsing large numbers of small metadata blocks.
