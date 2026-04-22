# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path-Based Access Control]
**Vulnerability:** Security guards were only enforced for write operations, leaving sensitive credential and system files (e.g., SSH keys, .env files, /etc/shadow) exposed to read, search, and vision analysis tools.
**Learning:** Security boundaries must be enforced consistently across all tools that interact with the filesystem. An LLM agent can bypass a write-block by reading sensitive info and using it elsewhere, or by using indirect tools like vision analysis to "see" file contents.
**Prevention:** Implement a centralized path-based security check (_is_path_denied) and ensure it is called by every tool that performs file I/O, search, or analysis. Use path normalization (realpath) to prevent bypasses.
