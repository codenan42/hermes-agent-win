# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Quick Command Security Bypass]
**Vulnerability:** User-defined "quick commands" in `cli.py` and `gateway/run.py` were executed directly via shell without passing through the `check_all_command_guards` security system, allowing potentially dangerous commands to run without approval.
**Learning:** Features that bypass the main agent loop (like slash commands or quick aliases) often bypass centralized security hooks if they are implemented as separate execution paths.
**Prevention:** Always integrate core security guards at the lowest possible level before command execution, or ensure all execution paths (including "quick" ones) call the same validation logic.

## 2025-05-15 - [Partial Secret Redaction Leak]
**Vulnerability:** Redaction regexes for ENV and JSON assignments failed to correctly capture quoted values containing spaces, leading to only the first word being redacted (e.g., `SECRET="pass word"` became `SECRET=*** word"`).
**Learning:** Simple regexes using `\S+` or greedy matching without considering quotes can leak sensitive data when secrets contain whitespace.
**Prevention:** Use non-capturing groups and backreferences `(?:(['"])(.*?)\2|(\S+))` to robustly handle both quoted (with spaces) and unquoted values in redaction patterns.
