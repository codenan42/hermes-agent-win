# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-14 - [Unified Path Access Control]
**Vulnerability:** Access control for sensitive files was limited to write operations. The agent could still read, search, delete, move, or analyze (via vision tools) sensitive credentials (SSH keys, `.env` files) and system configurations (`/etc/shadow`), leading to potential data leakage and unauthorized manipulation.
**Learning:** Security boundaries must be enforced at the data level across all access methods. Relying only on "write denial" is insufficient when read or metadata access can also expose secrets. Centralizing the path validation logic and applying it consistently to all file-touching tools ensures defense in depth.
**Prevention:** Use a unified `_is_path_denied` check across all tools that accept file paths as input. Ensure this check handles path expansion (~, relative paths) and symlink resolution (`realpath`) to prevent bypasses.
