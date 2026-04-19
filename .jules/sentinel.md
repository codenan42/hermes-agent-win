# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path-Based Access Control]
**Vulnerability:** Sensitive files like SSH keys and environment files were protected against writing, but remained vulnerable to unauthorized reading, searching, and deletion. Secondary tools like the V4A patch parser and vision analysis tool also bypassed these protections.
**Learning:** Security guards for filesystem access must be applied consistently across all entry points. Relying on "write-only" protection creates significant information leakage and integrity risks. Bypasses often occur in tools that execute raw shell commands (rm, mv) or specialized processing (base64 inlining for vision).
**Prevention:** Centralize path-based security logic and enforce it at the lowest possible layer for all operation types (read/write/search/delete/move). Ensure every tool that accepts a file path as input validates it against the centralized deny list before any disk activity.
