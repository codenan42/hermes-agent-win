## 2025-05-15 - Optimize skills system prompt assembly
**Learning:** Redundant file I/O and YAML parsing in prompt assembly loops significantly increase agent initialization latency. Using `yaml.CSafeLoader` provides a massive speedup over the pure-Python loader for frequent small file parsing.
**Action:** Consolidate multiple reads/parses of the same metadata files into a single helper. Always check for and use `CSafeLoader` when parsing YAML in hot paths.
