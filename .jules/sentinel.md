# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2026-05-10 - [Unified Path Access Control]
**Vulnerability:** The file access protection system was only enforced on write operations (`write_file`, `patch`), leaving sensitive system and credential files (`~/.ssh/*`, `/etc/shadow`, etc.) vulnerable to exfiltration via `read_file`, `search_files`, and `vision_analyze`.
**Learning:** Security guards implemented at the "action" level (e.g., "deny writes") can leave gaps if they don't cover all access vectors to the same sensitive resources. A centralized, resource-centric guard is more robust than multiple action-centric guards.
**Prevention:** Generalize path-based security to block ALL access (read/write/search) to sensitive files and directories. Ensure that new tools (like vision or specialized parsers) inherit or explicitly call the centralized path guard.
