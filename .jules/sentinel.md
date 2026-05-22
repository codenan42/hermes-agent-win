# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Access Control]
**Vulnerability:** Sensitive system and credential files (SSH keys, environment files, shell profiles) were protected against writes but remained accessible for reading, searching, and manipulation via other tools like the vision tool or patch parser.
**Learning:** Security policies must be applied consistently across all access vectors. A "write-only" deny list creates a false sense of security if the same files can be exfiltrated via read/search operations or analyzed by proxy using vision models.
**Prevention:** Centralize path-based access control and integrate it into every tool that interacts with the filesystem. Use a "fail-closed" approach for path resolution and ensure that moving or deleting protected files is also blocked.
