# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path-Based Access Control]
**Vulnerability:** Security restrictions were inconsistent, only blocking writes to sensitive paths while allowing reads, searches, deletions, and moves. Some tools (like `patch_parser.py`) bypassed checks by using raw shell commands.
**Learning:** Defense in depth requires consistent enforcement across all I/O boundaries. Relying on tool-specific logic for security checks leads to gaps when new tools are added or existing ones are refactored.
**Prevention:** Centralize path-based security in the core file operations layer. Use a unified `_is_path_denied` check that is called by all higher-level tools (read, write, search, patch, vision) after path expansion and resolution.
