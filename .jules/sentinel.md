# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Path-based security bypass via V4A patches]
**Vulnerability:** The V4A patch parser used direct shell commands (`rm`, `mv`) for DELETE and MOVE operations, bypassing established path-based security checks. Additionally, sensitive files were readable because protection was only enforced on writes.
**Learning:** Security guards must be applied consistently across all filesystem-interacting tools. A "write-only" deny list is insufficient for full defense in depth when sensitive credentials can still be read or deleted/moved via side-channels like patch parsers.
**Prevention:** Consolidate path-based security into a robust `_is_path_denied` function and enforce it for all file operations (read, write, delete, move). Ensure that high-level abstractions (like patch parsers) always call these guards before executing low-level shell commands.
