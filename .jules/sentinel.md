# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-14 - [Path-based Security Consolidation]
**Vulnerability:** Sensitive files (SSH keys, credentials, system configs) were protected against writes but remained accessible for reading, searching, deleting (via patch parser), and vision-based analysis.
**Learning:** Security guards often start focused on a single operation (like "write") but need to be comprehensive (read/write/search/move/delete) to be effective. Gaps often exist in secondary tools that bypass the primary tool logic by using raw shell commands or alternative file access paths (like vision analysis of local files).
**Prevention:** Use a centralized path-based security guard (`_is_path_denied`) and ensure it is integrated into EVERY tool that touches the filesystem, regardless of the operation type. Always expand and resolve paths (`realpath`, `expanduser`) before checking to prevent bypasses via symlinks or relative paths.
