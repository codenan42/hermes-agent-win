# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Unified Path Access Control]
**Vulnerability:** Sensitive files (SSH keys, system configs, env vars) were protected against modification via `_is_write_denied` but could still be read using `read_file` or `vision_analyze` (by passing the path as a local "image_url").
**Learning:** Security controls often focus on "write" operations while neglecting "read" operations, which can be just as dangerous if they lead to credential exfiltration. Tools that accept local file paths (like vision tools) can bypass standard file tool restrictions if they don't implement the same path guards.
**Prevention:** Centralize path-based security logic and apply it consistently to all file-accessing operations (read, write, search, analyze). Ensure any new tool that interacts with the filesystem inherits or calls these centralized guards.
