# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path-Based Access Control]
**Vulnerability:** Sensitive files like SSH keys were only protected from being written to. They could still be read, searched, deleted, or moved, especially through secondary tools like the V4A patch parser which used raw shell commands.
**Learning:** Security guards must be centralized and applied to all I/O operations, not just writes. Secondary parsers or tools that wrap shell commands are common bypass vectors if they don't explicitly call into the central security logic.
**Prevention:** Use a unified `_is_path_denied` check for all file operations (read, write, search, delete, move). Ensure all tools that interact with the filesystem (like patch parsers) are integrated with this central guard.
