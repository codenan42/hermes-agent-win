# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2026-05-30 - [Robust Regex-Based Redaction]
**Vulnerability:** Structured secrets (ENV, JSON, Headers) were partially leaked or double-redacted when they contained spaces, used single quotes, or lacked optional fields like usernames in DB URLs.
**Learning:** Naive regexes using `\S+` or fixed quoting fail on real-world logs (e.g. Python dicts, quoted Shell variables). Applying prefix-based redaction early can mangle structured tokens before they are fully matched.
**Prevention:** Use non-capturing groups with backreferences `(?:(['"])(.*?)\2|(\S+))` for robust quote handling. Apply generic prefix redaction last and ensure masking is idempotent to avoid double-redaction.
