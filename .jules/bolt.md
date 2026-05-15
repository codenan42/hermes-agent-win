# Bolt's Journal - Critical Learnings

## 2025-05-15 - PyYAML Performance in Skill Parsing
**Learning:** `yaml.CSafeLoader` (leveraging LibYAML) is approximately 8x faster than the pure-Python `SafeLoader` for parsing small YAML blocks like skill frontmatter in this codebase (0.23s vs 1.8s for 1000 iterations). Skill discovery and prompt building are frequent operations where this latency accumulates.
**Action:** Always prefer `yaml.CSafeLoader` (aliased via a safe fallback to `SafeLoader`) for high-frequency YAML parsing, especially when scanning directories of metadata files.
