# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Path-Based Security Bypasses]
**Vulnerability:** Security restrictions were only applied to write operations, allowing sensitive files (SSH keys, env files, system configs) to be read or searched. Additionally, V4A patch operations (Delete and Move) bypassed these checks.
**Learning:** Security must be applied at the lowest possible layer and cover all relevant operations (Read, Write, Search, Delete, Move). Deny lists should be named descriptively (e.g., `_is_path_denied` instead of `_is_write_denied`) to prevent developer confusion.
**Prevention:** Ensure all file manipulation tools (including specialized ones like V4A patch parsers) consistently call the central security check. Verify that both directory prefixes and the directories themselves are correctly matched.
