# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Access Control]
**Vulnerability:** Sensitive files like `~/.ssh/id_rsa` and `~/.hermes/config.yaml` were protected against writes but remained accessible for reading and searching. The `vision_analyze` tool also lacked path-based security checks for local files.
**Learning:** Security checks must be applied consistently across all access vectors (read, write, search, and specialized tools). Relying on a "write-only" deny list creates a false sense of security and leaves data exfiltration vectors open.
**Prevention:** Centralize path-based security logic into a unified `_is_path_denied` helper and integrate it into all tools that interact with the filesystem. Use `os.path.realpath` and `os.path.expanduser` to prevent path traversal and symlink-based bypasses.
