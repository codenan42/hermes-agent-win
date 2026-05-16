## 2025-05-15 - YAML and Skill Loading Optimization
**Learning:** `build_skills_system_prompt` was reading and parsing each `SKILL.md` file twice (once for compatibility/description and once for conditional activation). Additionally, the pure-Python `yaml.SafeLoader` is a significant bottleneck when parsing many small YAML blocks.
**Action:** Consolidate multiple file reads/parses into a single `_load_skill_data` call per file. Use `yaml.CSafeLoader` when available to achieve ~5x speedup for the entire skill index construction.
