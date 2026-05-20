# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Access Control]
**Vulnerability:** Sensitive system and credential files (SSH keys, AWS credentials, environment files) were only protected from modification (write-access), but could still be read, searched, moved, or analyzed via vision tools.
**Learning:** Security controls often start with the most obvious risk (modification/deletion) but can miss other high-risk vectors like exfiltration or discovery. A fragmented application of security checks across different tools creates gaps.
**Prevention:** Implement a centralized, unified path access control system that applies to all filesystem interactions (read, write, search, move, delete, vision). Use robust path resolution (abspath, realpath) to prevent bypasses and "fail closed" on any error.
