# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2026-05-13 - [Unified Path Access Control]
**Vulnerability:** Sensitive system and credential files (SSH keys, shell profiles, etc.) were protected from modification but could still be read or searched by the agent, potentially leading to credential leakage.
**Learning:** Security checks should be centralized and applied to all access vectors (read, write, search, vision) to ensure consistency and prevent backdoors. A "write-only" protection is insufficient for sensitive data.
**Prevention:** Use a unified path access control system that covers all file-related operations. Implement "fail-closed" logic where access is denied if path resolution fails.
