# Sentinel's Security Journal

## 2025-05-14 - [Enhanced Secret Redaction]
**Vulnerability:** Common sensitive data like Basic Auth headers, session cookies, and CSRF tokens were not being redacted from logs and tool outputs, potentially leading to credential leakage.
**Learning:** The redaction system relied on a specific list of prefixes and keys. As the application expands into more integrations (e.g., gateway messengers, web tools), the surface area for sensitive data leakage increases.
**Prevention:** Regularly audit the types of data flowing through tools and logs. Use broad patterns for standard authentication schemes (Basic, Bearer) and common sensitive identifiers (cookie, session, csrf) to ensure defense in depth.

## 2025-05-15 - [Comprehensive Path Access Control]
**Vulnerability:** The application originally only implemented security checks for "write" operations on sensitive paths (e.g., `.ssh`, `.env`). This left a major gap where the agent could still read, search, or even delete/move (via the patch parser's raw shell calls) these sensitive files.
**Learning:** Security controls focused only on one side of the I/O (writes) provide a false sense of security. Path-based restrictions must be applied across all file-system interactions (Read, Write, Search, Delete, Move) to be effective. Additionally, providing tools with raw shell access (`_exec`) without wrapping them in security-aware methods allows for easy bypasses.
**Prevention:** Centralize path security logic into a single, robust `_is_path_denied` function and ensure it is called by every tool that touches the filesystem. Standardize tool interfaces (like `FileOperations`) to include all necessary primitives (delete, move) so that internal implementations don't fall back to insecure raw shell calls.
