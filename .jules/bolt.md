## 2026-05-10 - Optimize skill prompt assembly performance
**Learning:** Consolidating multiple file reads and YAML parses into a single pass significantly reduces latency when scanning large numbers of skill files (91+).  provides a ~5.4x speedup over the pure-Python  for frontmatter parsing.
**Action:** Always prefer single-pass data loading and `CSafeLoader` for performance-critical prompt assembly paths.
## 2025-05-14 - Optimize skill prompt assembly performance
**Learning:** Consolidating multiple file reads and YAML parses into a single pass significantly reduces latency when scanning large numbers of skill files (91+). `yaml.CSafeLoader` provides a ~5.4x speedup over the pure-Python `SafeLoader` for frontmatter parsing.
**Action:** Always prefer single-pass data loading and `yaml.CSafeLoader` for performance-critical prompt assembly paths.
