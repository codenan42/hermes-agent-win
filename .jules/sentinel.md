# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-14 - [Unified Path Access Control]
**Vulnerability:** File operations like `read_file` and `search` lacked path-based security checks, allowing the agent to read or search sensitive system files (SSH keys, AWS credentials, .env files) that were only protected from writes.
**Learning:** Security controls based only on write protection are insufficient to prevent data exfiltration. A unified approach that blocks ALL access (read, write, search) to sensitive paths is necessary for robust defense in depth.
**Prevention:** Centralize path-based access control and apply it uniformly across all file manipulation tools. Include the application's own configuration files in the protected list to prevent tampering or leakage of operational settings.
