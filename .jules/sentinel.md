# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Defense-in-Depth Path Security]
**Vulnerability:** Sensitive files (SSH keys, credentials, system configs) were protected against direct write operations, but could still be read by the agent or manipulated via patch operations (Delete/Move), leading to information leakage or unauthorized system modification.
**Learning:** Security controls focused on "write" protection often miss "read" or "move" exfiltration vectors. Centralizing path validation and applying it across all file-system interaction points (read, search, patch) is essential for defense-in-depth.
**Prevention:** Always validate user-provided paths against a centralized restriction list before performing ANY file system operation, not just writes. Ensure that directory-level blocks correctly handle the directory path itself, not just its children.
