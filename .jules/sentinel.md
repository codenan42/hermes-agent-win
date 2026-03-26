# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path-Based Security]
**Vulnerability:** Path-based security was exclusively enforced on write operations, allowing sensitive files (SSH keys, system configs) to be read. Furthermore, `Delete` and `Move` operations in the V4A patch parser bypassed these checks by executing shell commands directly.
**Learning:** Security checks implemented at the tool level (e.g., `write_file`) can be bypassed if other tools (e.g., `patch`) implement similar functionality using lower-level primitives (e.g., `_exec`) without re-applying the same guards.
**Prevention:** Centralize path validation in a robust, multi-purpose utility (`_is_path_denied`) and enforce it across all file-system access points, including read, write, delete, and move operations, regardless of whether they use high-level Python APIs or direct shell execution.
