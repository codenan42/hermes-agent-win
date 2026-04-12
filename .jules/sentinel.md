# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path Protection]
**Vulnerability:** The patch parser's delete and move operations bypassed existing security guards, and the path denylist only applied to write operations, leaving sensitive credentials (SSH keys, AWS configs) vulnerable to unauthorized reading and searching.
**Learning:** Security guards focused only on 'write' operations are insufficient for data privacy. Furthermore, new tool implementations (like the V4A patch parser) can easily introduce bypasses if they don't explicitly call the centralized security logic.
**Prevention:** Consistently apply a unified path-based security guard (_is_path_denied) to all filesystem-interacting tools, including read, search, delete, and move operations. Always use os.path.realpath and os.path.expanduser to prevent traversal and symlink bypasses.
