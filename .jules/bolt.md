# Bolt's Journal - Performance Optimizations

## 2025-05-14 - [Initial Learning]
**Learning:** `copy.deepcopy` is a major performance bottleneck in message processing pipelines, especially as conversation history grows. For a history of 500 messages, it can take ~3ms per call, which adds up across multiple internal transformations before each API request.
**Action:** Prefer shallow copies of the message list and individual message dictionaries when only specific fields need to be modified or removed.

## 2025-05-14 - [SessionDB Overhead]
**Learning:** `SessionDB` initialization performs schema checks and migrations on every instantiation. While relatively fast (~0.8ms on subsequent inits), it's redundant if the DB is already initialized in the same process.
**Action:** Consider a singleton pattern or a global flag to skip initialization if already done.
