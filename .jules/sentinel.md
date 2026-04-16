# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2026-04-16 - [Comprehensive Path Protection]
**Vulnerability:** The security system only enforced write restrictions on sensitive paths, leaving them vulnerable to unauthorized reading or deletion via shell-based file operations.
**Learning:** Security guards at the lower-level file operation layer must cover all CRUD actions (Read, Update, Delete) to be effective. Relying on higher-level tools to enforce their own security often leads to gaps, especially when those tools execute raw shell commands.
**Prevention:** Centralize path-based security checks in the core file operations module and ensure all specialized parsers (like the patch parser) use these secure methods instead of reaching for raw shell execution.
