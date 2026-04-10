# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path-Based Security]
**Vulnerability:** Path-based security was only enforced for write operations, allowing agents to read or search sensitive system and credential files (e.g., `~/.ssh/id_rsa`, `/etc/shadow`). Additionally, directory-level access was not fully blocked due to trailing separator logic in prefix matching.
**Learning:** In an agentic environment, read access to sensitive data is often as critical as write access. A "write-deny" list must be treated as a "path-deny" list for all file and search operations to prevent credential exfiltration.
**Prevention:** Enforce path-based security (Defense in Depth) at the lowest possible layer for all filesystem-touching tools (read, write, search, patch, vision). Ensure directory matching correctly handles both the directory itself and its recursive contents.
