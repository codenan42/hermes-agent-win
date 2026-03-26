# Bolt's Journal - Hermes Agent Performance

This journal documents critical performance learnings and patterns discovered while optimizing the Hermes Agent codebase.

## 2025-05-14 - Selective Copying for Message Pipelines
**Learning:** `copy.deepcopy` on large message histories (hundreds of messages) is a significant bottleneck, taking ~8-10ms for 1000 messages. Since most pipeline operations only modify a few messages or specific fields, they can be replaced by a shallow list copy and selective dictionary/list copying.
**Action:** Use `messages.copy()` and only `copy()` or `dict()` individual message objects that need modification. For nested structures like `content` lists or `tool_calls`, perform selective shallow/deep copies as needed.
