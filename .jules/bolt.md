## 2025-05-15 - [SessionDB Initialization Optimization]
**Learning:** `SessionDB` performed full schema and migration checks on every instantiation. While SQLite's `IF NOT EXISTS` is fast, it still incurs a measurable cost (~0.8ms to 1.3ms per call) when many instances are created (e.g., in a gateway or interactive CLI).
**Action:** Use a class-level cache to track initialized database paths in the current process and skip `_init_schema` for subsequent instantiations of the same database.
