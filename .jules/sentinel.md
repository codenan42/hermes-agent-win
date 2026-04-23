# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Incomplete Path-Based Access Control]
**Vulnerability:** The application implemented a "write deny list" to protect sensitive files (e.g., SSH keys, credentials), but did not apply the same restrictions to read or search operations. This allowed an agent to read sensitive credentials or perform unauthorized file deletions/moves via patch tools that bypassed the centralized guard.
**Learning:** Security guards focused on a single operation (like "write") often leave gaps for other dangerous operations (read, delete, move). Centralized path-based security must be enforced across all file interaction entry points.
**Prevention:** Use a unified "path deny list" and enforce it consistently in `read_file`, `write_file`, `search`, and all patch/manipulation tools. Ensure secondary tools (like patch parsers) also respect these centralized guards.
