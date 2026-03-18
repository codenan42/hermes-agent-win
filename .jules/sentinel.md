# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-20 - [Comprehensive Path Protection]
**Vulnerability:** Security restrictions were inconsistent across file operation entry points. While writing to sensitive paths (SSH keys, config files) was blocked, reading from them was allowed. Additionally, multi-operation tools like the V4A patch parser could bypass protections for file deletion and movement.
**Learning:** Security controls must be applied uniformly to all access modes (read, write, delete, move). Centralizing path validation is essential, but it must be explicitly invoked by every tool that manipulates files, especially those that wrap low-level shell commands like `rm` or `mv`.
**Prevention:** Use a common security validator for all file-related tools. Ensure that higher-level abstraction layers (like patch parsers) also enforce these checks before delegating to the environment. Always handle edge cases like `None` paths in security functions to prevent robustness issues.
