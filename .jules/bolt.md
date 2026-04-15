## 2025-05-22 - Consolidated Skill File Parsing
**Learning:** Redundant file I/O and frontmatter parsing in `build_skills_system_prompt` created a measurable bottleneck when scanning large numbers of skills. Using `Path.read_text()[:2000]` was also inefficient as it loaded entire files into memory before slicing.
**Action:** Consolidate multiple reads/parses into a single helper function and use `f.read(2000)` on an open file handle to only retrieve the necessary preamble.
