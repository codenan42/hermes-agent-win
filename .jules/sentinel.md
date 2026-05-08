# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Universal Path Access Protection]
**Vulnerability:** Sensitive system and credential files (SSH keys, AWS tokens, Hermes secrets) were protected against writing but remained fully readable via `read_file`, `search_files`, and `vision_analyze` tools.
**Learning:** Security mechanisms often focus on preventing damage (writes) while overlooking exfiltration (reads). In an agentic system, any tool that can resolve a local path is a potential bypass for path-based security guards if they are only applied to standard file tools.
**Prevention:** Centralize path-based access control logic and enforce it at the lowest possible level across all tools that access the filesystem, including vision, transcription, and search tools.
