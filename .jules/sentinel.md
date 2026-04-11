# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Protection]
**Vulnerability:** Path-based security was exclusively enforced on write operations (`_is_write_denied`), leaving sensitive files (SSH keys, env files) vulnerable to read operations, as well as `delete` and `move` operations via the patch parser which used raw shell commands.
**Learning:** Security controls based solely on the *type* of operation (e.g., "deny writes") are easily bypassed if the same sensitive paths can be accessed via other means (reads, deletions, moves). Defense in depth requires a centralized path-level check that applies to all filesystem interactions.
**Prevention:** Use a unified `_is_path_denied` check across all tools that touch the filesystem, including file operations, patch parsers, and vision analysis tools.
