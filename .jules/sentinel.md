# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Regex-based Redaction Bypass for Quoted Strings with Spaces]
**Vulnerability:** Environment variable assignments with secrets enclosed in quotes and containing spaces (e.g., `MY_PASSWORD="secret with spaces"`) were only partially redacted, leaking the portion after the first space.
**Learning:** The `\S+` pattern in regex only matches non-whitespace characters. When combined with a backreference to a quote, it fails to capture the full content if spaces are present, as the non-whitespace match terminates early and the quote backreference fails to match at that position.
**Prevention:** Use non-greedy patterns that explicitly allow spaces within delimiters (e.g., `(?:(['\"])(.*?)\2|(\S+))`) when redacting potentially multi-word secrets in quoted environment assignments.
