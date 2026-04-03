# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [V4A Patch Security Bypass]
**Vulnerability:** The V4A patch parser's `Delete` and `Move` operations were executing raw shell commands (`rm`, `mv`) without checking the target paths against the application's write deny list, allowing unauthorized deletion or relocation of sensitive files like `~/.ssh/id_rsa`.
**Learning:** Security enforcement at the tool level (e.g., in `write_file_tool`) is insufficient if internal parsers or helpers bypass those tools to perform direct actions. Defense-in-depth requires that all paths to dangerous operations (write, delete, move) are gated by the same security policies.
**Prevention:** Centralize path-based security checks and ensure they are invoked by every component that performs filesystem modifications, regardless of whether it uses a high-level tool or a low-level shell command.
