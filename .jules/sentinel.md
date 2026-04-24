# Sentinel's Security Journal

## 2025-05-15 - [Path-Based Access Control Expansion]
**Vulnerability:** The existing protection mechanism only blocked writing to sensitive files, leaving them vulnerable to being read or searched by the AI agent. Additionally, operations like delete and move (via patch parser) bypassed these checks.
**Learning:** Security guards implemented at the tool level (e.g., `write_file`) can be bypassed if other tools or low-level operations (like raw shell commands in a patch parser) don't enforce the same restrictions.
**Prevention:** Centralize security validation logic (like `_is_path_denied`) and enforce it consistently across all file-system interacting tools (read, write, search, delete, move) and multimodal analysis tools (vision).

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.
