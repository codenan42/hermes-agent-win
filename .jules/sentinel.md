# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Access Control]
**Vulnerability:** Sensitive files (SSH keys, credentials, .env) were protected from writes but remained vulnerable to reading, searching, and deletion/movement via the patch tool and AI vision tool.
**Learning:** Security controls must be centralized and applied consistently across all data access vectors (I/O, search, vision, shell-based file management) to prevent "lateral" bypasses where an agent uses one tool to circumvent the protections of another.
**Prevention:** Implement a universal path-based access control function and enforce it at the entry point of every tool that interacts with the file system.
