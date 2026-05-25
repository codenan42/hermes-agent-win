# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Quoted Secret Leakage in Redaction]
**Vulnerability:** Quoted secrets containing spaces (e.g., `SECRET="my secret"`) were partially leaked in logs because the redaction regex used `\S+`, which stops at the first whitespace.
**Learning:** Standard regex patterns for key-value pairs often overlook that values can be quoted and contain spaces. Relying on non-whitespace characters (`\S+`) is insufficient for robust redaction.
**Prevention:** Use non-capturing groups with backreferences (e.g., `(?:(['"])(.*?)\2|(\S+))`) to correctly capture and redact both quoted (with spaces) and unquoted values in sensitive assignments and headers.
