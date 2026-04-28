# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path Security]
**Vulnerability:** Path-based security was only enforced for write operations, allowing sensitive files (SSH keys, env files) to be read or searched by the agent.
**Learning:** Security guards in a file-system-aware agent must be applied to the entire CRUD lifecycle. Blocking writes while allowing reads is a major data exfiltration risk.
**Prevention:** Always use a centralized path security function (`_is_path_denied`) and apply it to all tools that interact with the filesystem (read, write, search, patch, vision). Ensure prefix matching handles directory boundaries correctly (consistent trailing slashes).
