# Bolt's Journal - Critical Learnings

## 2025-05-14 - Initial Setup
**Learning:** Starting fresh as Bolt. Previous optimizations include prompt caching and skill indexing.
**Action:** Focus on finding new bottlenecks in agent history or tool discovery.

## 2025-05-14 - Skill Indexing Optimization
**Learning:** Consolidating I/O and switching to `CSafeLoader` for YAML parsing reduced latency of `build_skills_system_prompt` from ~160ms to ~90ms (~43% speedup). Multiple `read_text` calls on the same file are a common bottleneck in prompt assembly.
**Action:** Always look for redundant file reads in prompt builders and consolidate them into single-pass data structures. Use `CSafeLoader` for all YAML parsing where performance is critical.
