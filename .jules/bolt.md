
## 2026-05-25 - Skill Parsing I/O and YAML Consolidation
**Learning:** Parsing 90+ skills for the system prompt was a significant bottleneck (~151ms) due to redundant file reads and slow pure-Python YAML parsing.  is ~7.5x faster than  for small frontmatter blocks.
**Action:** Always use  when available for batch parsing tasks. Consolidate file I/O to ensure each file is read only once per logical operation.

## 2026-05-25 - Skill Parsing I/O and YAML Consolidation
**Learning:** Parsing 90+ skills for the system prompt was a significant bottleneck (~151ms) due to redundant file reads and slow pure-Python YAML parsing. `yaml.CSafeLoader` is ~7.5x faster than `yaml.SafeLoader` for small frontmatter blocks.
**Action:** Always use `yaml.CSafeLoader` when available for batch parsing tasks. Consolidate file I/O to ensure each file is read only once per logical operation.
