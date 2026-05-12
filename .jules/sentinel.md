# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2026-05-12 - [Fix Partial Secret Leakage in Quoted Values]
**Vulnerability:** Redaction patterns using `\S+` failed to capture quoted secrets containing spaces, leading to partial leakage (e.g., `MY_PASSWORD="my secret password"` was redacted as `MY_PASSWORD=*** secret password"`).
**Learning:** Quoted values with spaces are common in configuration and headers. Regexes must use non-capturing groups with backreferences to correctly identify the full scope of a quoted value.
**Prevention:** Always use `(?:(['"])(.*?)\1|(\S+))` or similar patterns when redacting potentially quoted values to ensure the entire secret is captured regardless of whitespace.
