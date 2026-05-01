# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path-Based Access Control]
**Vulnerability:** Sensitive files (SSH keys, credentials, system configs) were protected against writing, but remained vulnerable to unauthorized reading, searching, or manipulation via Vision and Patch tools.
**Learning:** Defense-in-depth requires access control at every filesystem interaction point. Relying only on write-protection leaves significant data exfiltration and exploration vectors open.
**Prevention:** Maintain a centralized path-denial utility and enforce it across all filesystem-bound tools (Read, Write, Search, Delete, Move, Vision). Use robust directory matching (trailing separators) to prevent partial-path bypasses.
