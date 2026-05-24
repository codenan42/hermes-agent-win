# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Access Control]
**Vulnerability:** Security checks were inconsistently applied across tools. While `write_file` blocked sensitive paths, `read_file`, `search`, and `vision_analyze` allowed access to SSH keys and credentials.
**Learning:** A "write-only" protection is insufficient when the agent can still read or move protected files to unprotected locations. Security boundaries must be unified across all access vectors.
**Prevention:** Centralize path-based security logic into a single `_is_path_denied` helper that handles expansion, resolution, and fail-closed logic. Integrate this check into all tools that touch the filesystem (read, write, search, move, delete, vision).
