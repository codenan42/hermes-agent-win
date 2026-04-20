# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path-Based Security]
**Vulnerability:** Sensitive system and credential files (e.g., `/etc/shadow`, `~/.ssh/id_rsa`) were protected from being written to, but remained accessible for reading, deletion, and moving. Additionally, the patch parser and vision tools bypassed existing write-denial checks.
**Learning:** Security guards focused only on write operations leave significant gaps for data exfiltration or DoS via file deletion/relocation. Secondary tools that perform filesystem operations using raw shell commands often fail to inherit centralized security checks.
**Prevention:** Implement a centralized "path-based" security guard (`_is_path_denied`) that is enforced for ALL filesystem interactions (read, write, delete, move, analyze). Ensure all tools use a secure, high-level file API rather than raw shell commands.
