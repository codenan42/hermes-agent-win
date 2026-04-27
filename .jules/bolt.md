# Bolt's Journal - Critical Learnings Only

## 2024-05-15 - Selective Shallow Copying for Message History
**Learning:** Replacing `copy.deepcopy` with selective shallow copying in message-processing pipelines (like `prompt_caching.py` and `run_agent.py`) results in 10x-100x speedups for large conversation histories.
**Action:** Always check if `deepcopy` is actually necessary for large data structures, especially when only a few fields need modification.

## 2024-05-15 - Skill Indexing Optimization
**Learning:** Consolidating redundant file reads and YAML parsing during skill indexing in `agent/prompt_builder.py` significantly reduces latency. Using `f.read(2000)` instead of `Path.read_text()` for frontmatter preamble avoids memory overhead.
**Action:** Use targeted reads when only partial file content is needed.
