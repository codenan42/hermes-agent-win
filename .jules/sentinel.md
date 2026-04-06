# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-14 - [Path-based Security Hardening]
**Vulnerability:** Security restrictions for sensitive paths were only enforced on write operations. An agent could still read sensitive files like `~/.ssh/id_rsa` or `~/.hermes/.env`. Furthermore, V4A patch operations (Delete/Move) bypassed security checks because they used raw shell commands.
**Learning:** Security checks must be applied consistently across all access vectors. If a path is "denied", it should be denied for reading, writing, searching, and deleting. Also, higher-level tool abstractions (like V4A patching) must re-verify these core security constraints before invoking low-level primitives.
**Prevention:** Use a centralized, generalized path validation function (`_is_path_denied`) and apply it at the entry point of all file-related tools. Ensure that any tool that can modify the filesystem through indirect means (like move or delete in a patch) also enforces these path restrictions.
