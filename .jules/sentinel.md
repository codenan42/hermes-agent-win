# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Access Control]
**Vulnerability:** The agent was only restricted from writing to sensitive paths, but could still read sensitive files like SSH keys (~/.ssh/id_rsa) or its own configuration (~/.hermes/config.yaml).
**Learning:** Security controls must be applied consistently across all data access vectors. Protecting only the write path leaves a significant exfiltration and reconnaissance surface.
**Prevention:** Centralize path-based security logic and enforce it at the entry point of all file-touching tools (read, write, search, delete, move, and vision analysis).
