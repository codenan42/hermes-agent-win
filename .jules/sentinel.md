# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Denial Bypass]
**Vulnerability:** Path-based security was inconsistently applied (write-only) and bypassed in `V4A` patch operations (Delete/Move) by using direct shell execution.
**Learning:** Security checks must be applied at the lowest common interface. Relying on "write" tools to catch all modifications is insufficient if other tools (like patch) use lower-level methods (like `rm` or `mv`).
**Prevention:** Use a unified `_is_path_denied` utility for all filesystem access (read/write/delete/move). Implement defense-in-depth with substring pattern matching to catch sensitive files even when home directory resolution varies between the host and the sandbox.
