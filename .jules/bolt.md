# Bolt's Journal - Critical Performance Learnings

## 2025-05-14 - Redundant Skill Parsing and YAML Optimization
**Learning:** In the skill system, each skill file was being read and parsed multiple times to extract different pieces of metadata (descriptions, platform compatibility, and activation conditions). Consolidating these into a single-pass `_load_skill_data` helper halved the I/O and parsing overhead. Additionally, `yaml.CSafeLoader` provides an ~8x speedup over the pure-Python `SafeLoader` for parsing skill frontmatter.
**Action:** Always look for patterns where the same file is read/parsed multiple times in a single loop. Prefer consolidated loading. Use C-optimized parsers like `CSafeLoader` for configuration and metadata files.
