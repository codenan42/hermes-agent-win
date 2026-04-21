# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path-Based Security]
**Vulnerability:** Sensitive files like SSH keys and credentials were only protected against writes, leaving them vulnerable to being read, deleted, or moved by the agent.
**Learning:** Security guards must be applied consistently across all I/O operations (Read, Write, Delete, Move). Secondary tools (like vision_analyze) that accept local paths can also be used as a bypass if they don't implement the same path-based security checks.
**Prevention:** Centralize path-based security logic (e.g., `_is_path_denied`) and ensure it's called in every tool that interacts with the filesystem. Always use `os.path.realpath` to resolve symlinks before checking against deny lists.
