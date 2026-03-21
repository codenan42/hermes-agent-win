# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2026-03-21 - [Expanded Path-Based Access Control]
**Vulnerability:** Path-based security was only enforced for write operations, allowing information disclosure of sensitive host files (SSH keys, .env files, system config) via the `read_file` tool and V4A patches.
**Learning:** Security boundaries must be consistent across all IO operations. Protecting only against modification leaves a large surface area for data exfiltration.
**Prevention:** Always implement a unified "is path denied" check that applies to read, write, delete, and move operations. Fail-secure by denying access if path resolution fails or is indeterminate.
