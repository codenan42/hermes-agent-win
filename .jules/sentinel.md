# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Access Control]
**Vulnerability:** Access control was only enforced on "write" operations. Sensitive files (SSH keys, credentials, agent config) could still be read via `read_file`, `search_files`, `patch` (move), and even OCR'd via `vision_analyze_tool`.
**Learning:** Security must be centralized and "fail-closed". A single `_is_path_denied` function now protects all tool access vectors (read, write, search, delete, move, vision). Moving a file to an unprotected location is a high-risk exfiltration vector that must be blocked.
**Prevention:** Always apply path-based access controls to any tool that takes a file path as input, regardless of whether it's a read or write operation.
