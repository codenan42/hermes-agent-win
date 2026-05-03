# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path-Based Access Control]
**Vulnerability:** Path-based security was limited to write operations, allowing the agent to read sensitive files (e.g., `~/.ssh/id_rsa`, `~/.hermes/.env`) or search through protected directories.
**Learning:** Security controls should be holistic. Protecting against modification (integrity) without protecting against disclosure (confidentiality) or deletion (availability) leaves significant gaps, especially when AI agents have broad tool access.
**Prevention:** Centralize path-based security checks and apply them to all filesystem operations (read, write, search, delete, move). Ensure that directory-level blocks correctly handle the directory path itself by normalizing with trailing separators.
