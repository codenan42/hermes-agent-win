# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Access Control]
**Vulnerability:** The existing security model only blocked writes to sensitive files (SSH keys, AWS credentials, etc.), leaving them vulnerable to information disclosure via `read_file`, `search`, `vision_analyze`, and `patch_parser` move/delete operations.
**Learning:** Security guards must be centralized and applied to all I/O boundaries. Blocking only one type of operation (e.g., writes) is insufficient when an agent has multiple tools that can interact with the filesystem.
**Prevention:** Use a centralized `_is_path_denied` check across all tools that accept file paths as input. Ensure it handles directory exact matches and prefix-based subpath blocking to prevent unauthorized access to sensitive configuration directories.
