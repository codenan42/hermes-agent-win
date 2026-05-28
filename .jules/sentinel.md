# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2026-05-25 - [Unified Path Access Control]
**Vulnerability:** The agent's access control was limited to write operations, leaving sensitive files (SSH keys, environment files, agent config) readable by the agent loop, searchable, and exploitable via visual analysis tools or move/delete operations.
**Learning:** Security must be enforced at the path resolution layer for all file-based operations. An agent that can read its own config or SSH keys can exfiltrate them or use them to escalate privileges.
**Prevention:** Implement a centralized path-based access control system that is explicitly integrated into every tool that interacts with the filesystem. Use a fail-closed policy and canonical path resolution to prevent bypasses.
