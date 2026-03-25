#!/usr/bin/env python3
"""
File Operations Module

Provides file manipulation capabilities (read, write, patch, search) that work
across all terminal backends (local, docker, singularity, ssh, modal, daytona).

The key insight is that all file operations can be expressed as shell commands,
so we wrap the terminal backend's execute() interface to provide a unified file API.

Usage:
    from tools.file_operations import ShellFileOperations
    from tools.terminal_tool import _active_environments
    
    # Get file operations for a terminal environment
    file_ops = ShellFileOperations(terminal_env)
    
    # Read a file
    result = file_ops.read_file("/path/to/file.py")
    
    # Write a file
    result = file_ops.write_file("/path/to/new.py", "print('hello')")
    
    # Search for content
    result = file_ops.search("TODO", path=".", file_glob="*.py")
"""

import os
import re
import json
import difflib
import platform
import shutil
import fnmatch
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path


# ---------------------------------------------------------------------------
# Write-path deny list — blocks writes to sensitive system/credential files
# ---------------------------------------------------------------------------

def _get_hermes_home_str():
    from hermes_cli.config import get_hermes_home
    try:
        return str(get_hermes_home())
    except Exception:
        return str(Path.home() / ".hermes")

def _get_denied_paths():
    user_home = str(Path.home())
    hermes_home = _get_hermes_home_str()
    return {
        os.path.realpath(p) for p in [
            os.path.join(user_home, ".ssh", "authorized_keys"),
            os.path.join(user_home, ".ssh", "id_rsa"),
            os.path.join(user_home, ".ssh", "id_ed25519"),
            os.path.join(user_home, ".ssh", "config"),
            os.path.join(hermes_home, ".env"),
            os.path.join(user_home, ".bashrc"),
            os.path.join(user_home, ".zshrc"),
            os.path.join(user_home, ".profile"),
            os.path.join(user_home, ".bash_profile"),
            os.path.join(user_home, ".zprofile"),
            os.path.join(user_home, ".netrc"),
            os.path.join(user_home, ".pgpass"),
            os.path.join(user_home, ".npmrc"),
            os.path.join(user_home, ".pypirc"),
            "/etc/sudoers",
            "/etc/passwd",
            "/etc/shadow",
        ]
    }

def _get_denied_prefixes():
    user_home = str(Path.home())
    return [
        os.path.realpath(p) + os.sep for p in [
            os.path.join(user_home, ".ssh"),
            os.path.join(user_home, ".aws"),
            os.path.join(user_home, ".gnupg"),
            os.path.join(user_home, ".kube"),
            "/etc/sudoers.d",
            "/etc/systemd",
        ]
    ]

WRITE_DENIED_PATHS = _get_denied_paths()
WRITE_DENIED_PREFIXES = _get_denied_prefixes()


def _is_write_denied(path: str) -> bool:
    """Return True if path is on the write deny list."""
    if not path:
        return False

    try:
        resolved = os.path.realpath(os.path.expanduser(path))

        # Check against dynamic lists to handle HERMES_HOME changes in tests
        if resolved in _get_denied_paths():
            return True

        for prefix in _get_denied_prefixes():
            if resolved.startswith(prefix):
                return True
    except (OSError, ValueError):
        # If path is invalid or can't be resolved, fail closed (deny)
        return True

    return False


# =============================================================================
# Result Data Classes
# =============================================================================

@dataclass
class ReadResult:
    """Result from reading a file."""
    content: str = ""
    total_lines: int = 0
    file_size: int = 0
    truncated: bool = False
    hint: Optional[str] = None
    is_binary: bool = False
    is_image: bool = False
    base64_content: Optional[str] = None
    mime_type: Optional[str] = None
    dimensions: Optional[str] = None  # For images: "WIDTHxHEIGHT"
    error: Optional[str] = None
    similar_files: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None and v != []}


@dataclass
class WriteResult:
    """Result from writing a file."""
    bytes_written: int = 0
    dirs_created: bool = False
    error: Optional[str] = None
    warning: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class PatchResult:
    """Result from patching a file."""
    success: bool = False
    diff: str = ""
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    lint: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        result = {"success": self.success}
        if self.diff:
            result["diff"] = self.diff
        if self.files_modified:
            result["files_modified"] = self.files_modified
        if self.files_created:
            result["files_created"] = self.files_created
        if self.files_deleted:
            result["files_deleted"] = self.files_deleted
        if self.lint:
            result["lint"] = self.lint
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class SearchMatch:
    """A single search match."""
    path: str
    line_number: int
    content: str
    mtime: float = 0.0  # Modification time for sorting


@dataclass
class SearchResult:
    """Result from searching."""
    matches: List[SearchMatch] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)
    total_count: int = 0
    truncated: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        result = {"total_count": self.total_count}
        if self.matches:
            result["matches"] = [
                {"path": m.path, "line": m.line_number, "content": m.content}
                for m in self.matches
            ]
        if self.files:
            result["files"] = self.files
        if self.counts:
            result["counts"] = self.counts
        if self.truncated:
            result["truncated"] = True
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class LintResult:
    """Result from linting a file."""
    success: bool = True
    skipped: bool = False
    output: str = ""
    message: str = ""
    
    def to_dict(self) -> dict:
        if self.skipped:
            return {"status": "skipped", "message": self.message}
        return {
            "status": "ok" if self.success else "error",
            "output": self.output
        }


@dataclass
class ExecuteResult:
    """Result from executing a shell command."""
    stdout: str = ""
    exit_code: int = 0


# =============================================================================
# Abstract Interface
# =============================================================================

class FileOperations(ABC):
    """Abstract interface for file operations across terminal backends."""
    
    @abstractmethod
    def read_file(self, path: str, offset: int = 1, limit: int = 500) -> ReadResult:
        """Read a file with pagination support."""
        ...
    
    @abstractmethod
    def write_file(self, path: str, content: str) -> WriteResult:
        """Write content to a file, creating directories as needed."""
        ...
    
    @abstractmethod
    def patch_replace(self, path: str, old_string: str, new_string: str, 
                      replace_all: bool = False) -> PatchResult:
        """Replace text in a file using fuzzy matching."""
        ...
    
    @abstractmethod
    def patch_v4a(self, patch_content: str) -> PatchResult:
        """Apply a V4A format patch."""
        ...
    
    @abstractmethod
    def search(self, pattern: str, path: str = ".", target: str = "content",
               file_glob: Optional[str] = None, limit: int = 50, offset: int = 0,
               output_mode: str = "content", context: int = 0) -> SearchResult:
        """Search for content or files."""
        ...


# =============================================================================
# Implementation Constants
# =============================================================================

# Binary file extensions (fast path check)
BINARY_EXTENSIONS = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico', '.tiff', '.tif',
    '.svg',  # SVG is text but often treated as binary
    # Audio/Video
    '.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv', '.flac', '.ogg', '.webm',
    # Archives
    '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
    # Documents
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # Compiled/Binary
    '.exe', '.dll', '.so', '.dylib', '.o', '.a', '.pyc', '.pyo', '.class',
    '.wasm', '.bin',
    # Fonts
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    # Other
    '.db', '.sqlite', '.sqlite3',
}

# Image extensions (subset of binary that we can return as base64)
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico'}

# Linters by file extension
LINTERS = {
    '.py': 'python -m py_compile {file} 2>&1',
    '.js': 'node --check {file} 2>&1',
    '.ts': 'npx tsc --noEmit {file} 2>&1',
    '.go': 'go vet {file} 2>&1',
    '.rs': 'rustfmt --check {file} 2>&1',
}

# Max limits for read operations
MAX_LINES = 2000
MAX_LINE_LENGTH = 2000
MAX_FILE_SIZE = 50 * 1024  # 50KB


class ShellFileOperations(FileOperations):
    """
    File operations implemented via shell commands.
    
    Works with ANY terminal backend that has execute(command, cwd) method.
    This includes local, docker, singularity, ssh, modal, and daytona environments.
    """
    
    def __init__(self, terminal_env, cwd: str = None):
        """
        Initialize file operations with a terminal environment.
        
        Args:
            terminal_env: Any object with execute(command, cwd) method.
                         Returns {"output": str, "returncode": int}
            cwd: Working directory (defaults to env's cwd or current directory)
        """
        self.env = terminal_env
        self.cwd = cwd or getattr(terminal_env, 'cwd', None) or \
                   getattr(getattr(terminal_env, 'config', None), 'cwd', None) or "/"
        
        # Cache for command availability checks
        self._command_cache: Dict[str, bool] = {}

        # Detect if we should use native Python for local Windows environments
        from tools.environments.local import LocalEnvironment
        self._use_native = (
            platform.system() == "Windows" and
            isinstance(terminal_env, LocalEnvironment)
        )
        if self._use_native:
            self._native = NativeFileOperations(cwd=self.cwd)
    
    def _exec(self, command: str, cwd: str = None, timeout: int = None,
              stdin_data: str = None) -> ExecuteResult:
        """Execute command via terminal backend."""
        kwargs = {}
        if timeout:
            kwargs['timeout'] = timeout
        if stdin_data is not None:
            kwargs['stdin_data'] = stdin_data
        
        result = self.env.execute(command, cwd=cwd or self.cwd, **kwargs)
        return ExecuteResult(
            stdout=result.get("output", ""),
            exit_code=result.get("returncode", 0)
        )
    
    def _has_command(self, cmd: str) -> bool:
        """Check if a command exists in the environment (cached)."""
        if cmd not in self._command_cache:
            result = self._exec(f"command -v {cmd} >/dev/null 2>&1 && echo 'yes'")
            self._command_cache[cmd] = result.stdout.strip() == 'yes'
        return self._command_cache[cmd]
    
    def _is_likely_binary(self, path: str, content_sample: str = None) -> bool:
        """Check if a file is likely binary."""
        ext = os.path.splitext(path)[1].lower()
        if ext in BINARY_EXTENSIONS:
            return True
        
        # Content analysis: >30% non-printable chars = binary
        if content_sample:
            if not content_sample:
                return False
            non_printable = sum(1 for c in content_sample[:1000] 
                               if ord(c) < 32 and c not in '\n\r\t')
            return non_printable / min(len(content_sample), 1000) > 0.30
        
        return False
    
    def _is_image(self, path: str) -> bool:
        """Check if file is an image we can return as base64."""
        ext = os.path.splitext(path)[1].lower()
        return ext in IMAGE_EXTENSIONS
    
    def _add_line_numbers(self, content: str, start_line: int = 1) -> str:
        """Add line numbers to content in LINE_NUM|CONTENT format."""
        lines = content.split('\n')
        numbered = []
        for i, line in enumerate(lines, start=start_line):
            # Truncate long lines
            if len(line) > MAX_LINE_LENGTH:
                line = line[:MAX_LINE_LENGTH] + "... [truncated]"
            numbered.append(f"{i:6d}|{line}")
        return '\n'.join(numbered)
    
    def _expand_path(self, path: str) -> str:
        """Expand shell-style paths like ~ and ~user to absolute paths."""
        if not path:
            return path
        
        if self._use_native:
            return os.path.abspath(os.path.expanduser(path))

        # Handle ~ and ~user
        if path.startswith('~'):
            # Get home directory via the terminal environment
            result = self._exec("echo $HOME")
            if result.exit_code == 0 and result.stdout.strip():
                home = result.stdout.strip()
                if path == '~':
                    return home
                elif path.startswith('~/'):
                    return home + path[1:]  # Replace ~ with home
                # ~username format
                rest = path[1:]
                slash_idx = rest.find('/')
                username = rest[:slash_idx] if slash_idx >= 0 else rest
                if username and re.fullmatch(r'[a-zA-Z0-9._-]+', username):
                    expand_result = self._exec(f"echo {path}")
                    if expand_result.exit_code == 0 and expand_result.stdout.strip():
                        return expand_result.stdout.strip()
        
        return path
    
    def _escape_shell_arg(self, arg: str) -> str:
        """Escape a string for safe use in shell commands."""
        return "'" + arg.replace("'", "'\"'\"'") + "'"
    
    def _unified_diff(self, old_content: str, new_content: str, filename: str) -> str:
        """Generate unified diff between old and new content."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        diff = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}"
        )
        return ''.join(diff)
    
    # =========================================================================
    # READ Implementation
    # =========================================================================
    
    def read_file(self, path: str, offset: int = 1, limit: int = 500) -> ReadResult:
        """Read a file with pagination, binary detection, and line numbers."""
        if self._use_native:
            return self._native.read_file(path, offset, limit)

        path = self._expand_path(path)
        limit = min(limit, MAX_LINES)
        
        stat_cmd = f"wc -c < {self._escape_shell_arg(path)} 2>/dev/null"
        stat_result = self._exec(stat_cmd)
        
        if stat_result.exit_code != 0:
            return self._suggest_similar_files(path)
        
        try:
            file_size = int(stat_result.stdout.strip())
        except ValueError:
            file_size = 0
        
        if self._is_image(path):
            return ReadResult(
                is_image=True,
                is_binary=True,
                file_size=file_size,
                hint=(
                    "Image file detected. Automatically redirected to vision_analyze tool. "
                    "Use vision_analyze with this file path to inspect the image contents."
                ),
            )
        
        sample_cmd = f"head -c 1000 {self._escape_shell_arg(path)} 2>/dev/null"
        sample_result = self._exec(sample_cmd)
        
        if self._is_likely_binary(path, sample_result.stdout):
            return ReadResult(
                is_binary=True,
                file_size=file_size,
                error="Binary file - cannot display as text. Use appropriate tools to handle this file type."
            )
        
        end_line = offset + limit - 1
        read_cmd = f"sed -n '{offset},{end_line}p' {self._escape_shell_arg(path)}"
        read_result = self._exec(read_cmd)
        
        if read_result.exit_code != 0:
            return ReadResult(error=f"Failed to read file: {read_result.stdout}")
        
        wc_cmd = f"wc -l < {self._escape_shell_arg(path)}"
        wc_result = self._exec(wc_cmd)
        try:
            total_lines = int(wc_result.stdout.strip())
        except ValueError:
            total_lines = 0
        
        truncated = total_lines > end_line
        hint = None
        if truncated:
            hint = f"Use offset={end_line + 1} to continue reading (showing {offset}-{end_line} of {total_lines} lines)"
        
        return ReadResult(
            content=self._add_line_numbers(read_result.stdout, offset),
            total_lines=total_lines,
            file_size=file_size,
            truncated=truncated,
            hint=hint
        )
    
    def _suggest_similar_files(self, path: str) -> ReadResult:
        """Suggest similar files when the requested file is not found."""
        if self._use_native:
            return self._native._suggest_similar_files(path)

        dir_path = os.path.dirname(path) or "."
        filename = os.path.basename(path)
        
        ls_cmd = f"ls -1 {self._escape_shell_arg(dir_path)} 2>/dev/null | head -20"
        ls_result = self._exec(ls_cmd)
        
        similar = []
        if ls_result.exit_code == 0 and ls_result.stdout.strip():
            files = ls_result.stdout.strip().split('\n')
            for f in files:
                common = set(filename.lower()) & set(f.lower())
                if len(common) >= len(filename) * 0.5:
                    similar.append(os.path.join(dir_path, f))
        
        return ReadResult(
            error=f"File not found: {path}",
            similar_files=similar[:5]
        )
    
    # =========================================================================
    # WRITE Implementation
    # =========================================================================
    
    def write_file(self, path: str, content: str) -> WriteResult:
        """Write content to a file, creating parent directories as needed."""
        if self._use_native:
            return self._native.write_file(path, content)

        path = self._expand_path(path)

        if _is_write_denied(path):
            return WriteResult(error=f"Write denied: '{path}' is a protected system/credential file.")

        parent = os.path.dirname(path)
        dirs_created = False
        
        if parent:
            mkdir_cmd = f"mkdir -p {self._escape_shell_arg(parent)}"
            mkdir_result = self._exec(mkdir_cmd)
            if mkdir_result.exit_code == 0:
                dirs_created = True
        
        write_cmd = f"cat > {self._escape_shell_arg(path)}"
        write_result = self._exec(write_cmd, stdin_data=content)
        
        if write_result.exit_code != 0:
            return WriteResult(error=f"Failed to write file: {write_result.stdout}")
        
        stat_cmd = f"wc -c < {self._escape_shell_arg(path)} 2>/dev/null"
        stat_result = self._exec(stat_cmd)
        
        try:
            bytes_written = int(stat_result.stdout.strip())
        except ValueError:
            bytes_written = len(content.encode('utf-8'))
        
        return WriteResult(
            bytes_written=bytes_written,
            dirs_created=dirs_created
        )
    
    # =========================================================================
    # PATCH Implementation
    # =========================================================================
    
    def patch_replace(self, path: str, old_string: str, new_string: str,
                      replace_all: bool = False) -> PatchResult:
        """Replace text in a file using fuzzy matching."""
        if self._use_native:
            return self._native.patch_replace(path, old_string, new_string, replace_all)

        path = self._expand_path(path)

        if _is_write_denied(path):
            return PatchResult(error=f"Write denied: '{path}' is a protected system/credential file.")

        read_cmd = f"cat {self._escape_shell_arg(path)} 2>/dev/null"
        read_result = self._exec(read_cmd)
        
        if read_result.exit_code != 0:
            return PatchResult(error=f"Failed to read file: {path}")
        
        content = read_result.stdout
        
        from tools.fuzzy_match import fuzzy_find_and_replace
        
        new_content, match_count, error = fuzzy_find_and_replace(
            content, old_string, new_string, replace_all
        )
        
        if error:
            return PatchResult(error=error)
        
        if match_count == 0:
            return PatchResult(error=f"Could not find match for old_string in {path}")
        
        write_result = self.write_file(path, new_content)
        if write_result.error:
            return PatchResult(error=f"Failed to write changes: {write_result.error}")
        
        diff = self._unified_diff(content, new_content, path)
        lint_result = self._check_lint(path)
        
        return PatchResult(
            success=True,
            diff=diff,
            files_modified=[path],
            lint=lint_result.to_dict() if lint_result else None
        )
    
    def patch_v4a(self, patch_content: str) -> PatchResult:
        """Apply a V4A format patch."""
        from tools.patch_parser import parse_v4a_patch, apply_v4a_operations
        
        operations, parse_error = parse_v4a_patch(patch_content)
        if parse_error:
            return PatchResult(error=f"Failed to parse patch: {parse_error}")
        
        result = apply_v4a_operations(operations, self)
        return result
    
    def _check_lint(self, path: str) -> LintResult:
        """Run syntax check on a file after editing."""
        if self._use_native:
            return self._native._check_lint(path)

        ext = os.path.splitext(path)[1].lower()
        
        if ext not in LINTERS:
            return LintResult(skipped=True, message=f"No linter for {ext} files")
        
        linter_cmd = LINTERS[ext]
        base_cmd = linter_cmd.split()[0]
        
        if not self._has_command(base_cmd):
            return LintResult(skipped=True, message=f"{base_cmd} not available")
        
        cmd = linter_cmd.format(file=self._escape_shell_arg(path))
        result = self._exec(cmd, timeout=30)
        
        return LintResult(
            success=result.exit_code == 0,
            output=result.stdout.strip() if result.stdout.strip() else ""
        )
    
    # =========================================================================
    # SEARCH Implementation
    # =========================================================================
    
    def search(self, pattern: str, path: str = ".", target: str = "content",
               file_glob: Optional[str] = None, limit: int = 50, offset: int = 0,
               output_mode: str = "content", context: int = 0) -> SearchResult:
        """Search for content or files."""
        if self._use_native:
            return self._native.search(pattern, path, target, file_glob, limit, offset, output_mode, context)

        path = self._expand_path(path)
        
        check = self._exec(f"test -e {self._escape_shell_arg(path)} && echo exists || echo not_found")
        if "not_found" in check.stdout:
            return SearchResult(
                error=f"Path not found: {path}. Verify the path exists.",
                total_count=0
            )
        
        if target == "files":
            return self._search_files(pattern, path, limit, offset)
        else:
            return self._search_content(pattern, path, file_glob, limit, offset, 
                                        output_mode, context)
    
    def _search_files(self, pattern: str, path: str, limit: int, offset: int) -> SearchResult:
        """Search for files by name pattern (glob-like)."""
        if not self._has_command('find'):
            return SearchResult(
                error="File search requires 'find' command."
            )
        
        if not pattern.startswith('**/') and '/' not in pattern:
            search_pattern = pattern
        else:
            search_pattern = pattern.split('/')[-1]
        
        cmd = f"find {self._escape_shell_arg(path)} -type f -name {self._escape_shell_arg(search_pattern)} " \
              f"-printf '%T@ %p\\n' 2>/dev/null | sort -rn | tail -n +{offset + 1} | head -n {limit}"
        
        result = self._exec(cmd, timeout=60)
        
        if not result.stdout.strip():
            cmd_simple = f"find {self._escape_shell_arg(path)} -type f -name {self._escape_shell_arg(search_pattern)} " \
                        f"2>/dev/null | head -n {limit + offset} | tail -n +{offset + 1}"
            result = self._exec(cmd_simple, timeout=60)
        
        files = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split(' ', 1)
            if len(parts) == 2 and parts[0].replace('.', '').isdigit():
                files.append(parts[1])
            else:
                files.append(line)
        
        return SearchResult(
            files=files,
            total_count=len(files)
        )
    
    def _search_content(self, pattern: str, path: str, file_glob: Optional[str],
                        limit: int, offset: int, output_mode: str, context: int) -> SearchResult:
        """Search for content inside files (grep-like)."""
        if self._has_command('rg'):
            return self._search_with_rg(pattern, path, file_glob, limit, offset, 
                                        output_mode, context)
        elif self._has_command('grep'):
            return self._search_with_grep(pattern, path, file_glob, limit, offset,
                                          output_mode, context)
        else:
            return SearchResult(
                error="Content search requires ripgrep (rg) or grep."
            )
    
    def _search_with_rg(self, pattern: str, path: str, file_glob: Optional[str],
                        limit: int, offset: int, output_mode: str, context: int) -> SearchResult:
        """Search using ripgrep."""
        cmd_parts = ["rg", "--line-number", "--no-heading", "--with-filename"]
        if context > 0:
            cmd_parts.extend(["-C", str(context)])
        if file_glob:
            cmd_parts.extend(["--glob", self._escape_shell_arg(file_glob)])
        if output_mode == "files_only":
            cmd_parts.append("-l")
        elif output_mode == "count":
            cmd_parts.append("-c")
        
        cmd_parts.append(self._escape_shell_arg(pattern))
        cmd_parts.append(self._escape_shell_arg(path))
        
        fetch_limit = limit + offset + 200 if context > 0 else limit + offset
        cmd_parts.extend(["|", "head", "-n", str(fetch_limit)])
        
        cmd = " ".join(cmd_parts)
        result = self._exec(cmd, timeout=60)
        
        if result.exit_code == 2 and not result.stdout.strip():
            return SearchResult(error="Search failed", total_count=0)
        
        if output_mode == "files_only":
            all_files = [f for f in result.stdout.strip().split('\n') if f]
            total = len(all_files)
            page = all_files[offset:offset + limit]
            return SearchResult(files=page, total_count=total)
        elif output_mode == "count":
            counts = {}
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    parts = line.rsplit(':', 1)
                    if len(parts) == 2:
                        try:
                            counts[parts[0]] = int(parts[1])
                        except ValueError:
                            pass
            return SearchResult(counts=counts, total_count=sum(counts.values()))
        else:
            _match_re = re.compile(r'^([A-Za-z]:)?(.*?):(\d+):(.*)$')
            _ctx_re = re.compile(r'^([A-Za-z]:)?(.*?)-(\d+)-(.*)$')
            matches = []
            for line in result.stdout.strip().split('\n'):
                if not line or line == "--":
                    continue
                m = _match_re.match(line)
                if m:
                    matches.append(SearchMatch(
                        path=(m.group(1) or '') + m.group(2),
                        line_number=int(m.group(3)),
                        content=m.group(4)[:500]
                    ))
                    continue
                if context > 0:
                    m = _ctx_re.match(line)
                    if m:
                        matches.append(SearchMatch(
                            path=(m.group(1) or '') + m.group(2),
                            line_number=int(m.group(3)),
                            content=m.group(4)[:500]
                        ))
            
            total = len(matches)
            page = matches[offset:offset + limit]
            return SearchResult(
                matches=page,
                total_count=total,
                truncated=total > offset + limit
            )

    def _search_with_grep(self, pattern: str, path: str, file_glob: Optional[str],
                          limit: int, offset: int, output_mode: str, context: int) -> SearchResult:
        """Fallback search using grep."""
        cmd_parts = ["grep", "-rnH"]
        if context > 0:
            cmd_parts.extend(["-C", str(context)])
        if file_glob:
            cmd_parts.extend(["--include", self._escape_shell_arg(file_glob)])
        if output_mode == "files_only":
            cmd_parts.append("-l")
        elif output_mode == "count":
            cmd_parts.append("-c")
        
        cmd_parts.append(self._escape_shell_arg(pattern))
        cmd_parts.append(self._escape_shell_arg(path))
        
        fetch_limit = limit + offset + (200 if context > 0 else 0)
        cmd_parts.extend(["|", "head", "-n", str(fetch_limit)])
        
        cmd = " ".join(cmd_parts)
        result = self._exec(cmd, timeout=60)
        
        if result.exit_code == 2 and not result.stdout.strip():
            return SearchResult(error="Search failed", total_count=0)
        
        if output_mode == "files_only":
            all_files = [f for f in result.stdout.strip().split('\n') if f]
            total = len(all_files)
            page = all_files[offset:offset + limit]
            return SearchResult(files=page, total_count=total)
        elif output_mode == "count":
            counts = {}
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    parts = line.rsplit(':', 1)
                    if len(parts) == 2:
                        try:
                            counts[parts[0]] = int(parts[1])
                        except ValueError:
                            pass
            return SearchResult(counts=counts, total_count=sum(counts.values()))
        else:
            _match_re = re.compile(r'^([A-Za-z]:)?(.*?):(\d+):(.*)$')
            _ctx_re = re.compile(r'^([A-Za-z]:)?(.*?)-(\d+)-(.*)$')
            matches = []
            for line in result.stdout.strip().split('\n'):
                if not line or line == "--":
                    continue
                m = _match_re.match(line)
                if m:
                    matches.append(SearchMatch(
                        path=(m.group(1) or '') + m.group(2),
                        line_number=int(m.group(3)),
                        content=m.group(4)[:500]
                    ))
                    continue
                if context > 0:
                    m = _ctx_re.match(line)
                    if m:
                        matches.append(SearchMatch(
                            path=(m.group(1) or '') + m.group(2),
                            line_number=int(m.group(3)),
                            content=m.group(4)[:500]
                        ))
            
            total = len(matches)
            page = matches[offset:offset + limit]
            return SearchResult(
                matches=page,
                total_count=total,
                truncated=total > offset + limit
            )


class NativeFileOperations(FileOperations):
    """
    File operations implemented via native Python (os, shutil, re, glob).

    Used on Windows when backend is 'local' to avoid dependency on POSIX shell.
    """

    def __init__(self, cwd: str = "."):
        self.cwd = cwd

    def _resolve(self, path: str) -> str:
        """Resolve path relative to cwd."""
        expanded = os.path.expanduser(path)
        if os.path.isabs(expanded):
            return expanded
        return os.path.abspath(os.path.join(self.cwd, expanded))

    def _add_line_numbers(self, content: str, start_line: int = 1) -> str:
        lines = content.splitlines()
        numbered = []
        for i, line in enumerate(lines, start=start_line):
            if len(line) > MAX_LINE_LENGTH:
                line = line[:MAX_LINE_LENGTH] + "... [truncated]"
            numbered.append(f"{i:6d}|{line}")
        return '\n'.join(numbered)

    def read_file(self, path: str, offset: int = 1, limit: int = 500) -> ReadResult:
        resolved = self._resolve(path)
        if not os.path.isfile(resolved):
            return self._suggest_similar_files(path)

        file_size = os.path.getsize(resolved)
        ext = os.path.splitext(resolved)[1].lower()

        if ext in IMAGE_EXTENSIONS:
            return ReadResult(
                is_image=True, is_binary=True, file_size=file_size,
                hint="Image file detected. Use vision_analyze to inspect contents."
            )

        if ext in BINARY_EXTENSIONS:
            return ReadResult(is_binary=True, file_size=file_size, error="Binary file")

        try:
            with open(resolved, 'r', encoding='utf-8', errors='replace') as f:
                # Efficiency: skip lines without reading everything into memory
                for _ in range(offset - 1):
                    if not f.readline(): break

                lines = []
                for _ in range(limit):
                    line = f.readline()
                    if not line: break
                    lines.append(line)

                content = "".join(lines)

                # Simple binary check on sample
                sample = content[:1000]
                non_printable = sum(1 for c in sample if ord(c) < 32 and c not in '\n\r\t')
                if sample and len(sample) > 0 and non_printable / len(sample) > 0.3:
                    return ReadResult(is_binary=True, file_size=file_size, error="Likely binary file")

                # Get total lines for metadata
                f.seek(0)
                total_lines = sum(1 for _ in f)

                end = offset + len(lines) - 1
                truncated = total_lines > end
                hint = f"Use offset={end + 1} to continue reading (showing {offset}-{end} of {total_lines} lines)" if truncated else None

                return ReadResult(
                    content=self._add_line_numbers(content, offset),
                    total_lines=total_lines,
                    file_size=file_size,
                    truncated=truncated,
                    hint=hint
                )
        except Exception as e:
            return ReadResult(error=str(e))

    def _suggest_similar_files(self, path: str) -> ReadResult:
        resolved = self._resolve(path)
        dir_path = os.path.dirname(resolved)
        filename = os.path.basename(resolved)

        similar = []
        if os.path.isdir(dir_path):
            try:
                files = os.listdir(dir_path)
                for f in files:
                    if os.path.isfile(os.path.join(dir_path, f)):
                        common = set(filename.lower()) & set(f.lower())
                        if len(common) >= len(filename) * 0.5:
                            similar.append(os.path.relpath(os.path.join(dir_path, f), self.cwd))
            except Exception:
                pass

        return ReadResult(error=f"File not found: {path}", similar_files=similar[:5])

    def write_file(self, path: str, content: str) -> WriteResult:
        resolved = self._resolve(path)
        if _is_write_denied(resolved):
            return WriteResult(error=f"Write denied: {path} is protected")

        dirs_created = False
        parent = os.path.dirname(resolved)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
            dirs_created = True

        try:
            with open(resolved, 'w', encoding='utf-8') as f:
                f.write(content)
            return WriteResult(bytes_written=os.path.getsize(resolved), dirs_created=dirs_created)
        except Exception as e:
            return WriteResult(error=str(e))

    def patch_replace(self, path: str, old_string: str, new_string: str, replace_all: bool = False) -> PatchResult:
        resolved = self._resolve(path)
        if _is_write_denied(resolved):
            return PatchResult(error=f"Write denied: {path} is protected")

        try:
            if not os.path.isfile(resolved):
                return PatchResult(error=f"File not found: {path}")

            with open(resolved, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            from tools.fuzzy_match import fuzzy_find_and_replace
            new_content, count, error = fuzzy_find_and_replace(content, old_string, new_string, replace_all)

            if error: return PatchResult(error=error)
            if count == 0: return PatchResult(error="Match not found")

            self.write_file(path, new_content)

            diff = difflib.unified_diff(
                content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{path}", tofile=f"b/{path}"
            )

            return PatchResult(
                success=True, diff="".join(diff),
                files_modified=[path], lint=self._check_lint(path).to_dict()
            )
        except Exception as e:
            return PatchResult(error=str(e))

    def patch_v4a(self, patch_content: str) -> PatchResult:
        from tools.patch_parser import parse_v4a_patch, apply_v4a_operations
        ops, err = parse_v4a_patch(patch_content)
        if err: return PatchResult(error=err)
        return apply_v4a_operations(ops, self)

    def _check_lint(self, path: str) -> LintResult:
        resolved = self._resolve(path)
        ext = os.path.splitext(resolved)[1].lower()
        if ext not in LINTERS: return LintResult(skipped=True)

        linter_cmd = LINTERS[ext]
        base_cmd = linter_cmd.split()[0]
        if not shutil.which(base_cmd): return LintResult(skipped=True)

        try:
            cmd = linter_cmd.format(file=f'"{resolved}"')
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return LintResult(success=res.returncode == 0, output=res.stdout + res.stderr)
        except Exception as e:
            return LintResult(success=False, output=str(e))

    def search(self, pattern: str, path: str = ".", target: str = "content",
               file_glob: Optional[str] = None, limit: int = 50, offset: int = 0,
               output_mode: str = "content", context: int = 0) -> SearchResult:
        root = self._resolve(path)
        if not os.path.exists(root):
            return SearchResult(error=f"Path not found: {path}")

        if target == "files":
            return self._search_files(pattern, root, limit, offset)
        return self._search_content(pattern, root, file_glob, limit, offset, output_mode, context)

    def _search_files(self, pattern: str, root: str, limit: int, offset: int) -> SearchResult:
        matches = []
        norm_pattern = pattern.replace('\\', '/')
        if '/' not in norm_pattern:
            glob_pattern = f"**/{pattern}"
        else:
            glob_pattern = pattern

        for p in Path(root).rglob('*'):
            if p.is_file():
                rel = os.path.relpath(p, root)
                if fnmatch.fnmatch(rel.replace('\\', '/'), norm_pattern):
                    matches.append((p.stat().st_mtime, str(p)))

        matches.sort(key=lambda x: x[0], reverse=True)
        files = [os.path.relpath(m[1], self.cwd) for m in matches]
        return SearchResult(files=files[offset:offset+limit], total_count=len(files))

    def _search_content(self, pattern: str, root: str, file_glob: str, limit: int, offset: int, mode: str, context: int) -> SearchResult:
        matches = []
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except Exception as e:
            return SearchResult(error=f"Invalid regex: {e}")

        search_iter = Path(root).rglob(file_glob if file_glob else '*')

        for p in search_iter:
            if not p.is_file():
                continue
            if file_glob and not fnmatch.fnmatch(p.name, file_glob):
                continue

            try:
                if p.stat().st_size > 10 * 1024 * 1024: continue

                with open(p, 'r', encoding='utf-8', errors='replace') as f:
                    for i, line in enumerate(f):
                        if regex.search(line):
                            rel_path = os.path.relpath(p, self.cwd)
                            matches.append(SearchMatch(
                                path=rel_path,
                                line_number=i+1,
                                content=line.strip()[:500]
                            ))
                            if len(matches) >= offset + limit + 2000: break
                    if len(matches) >= offset + limit + 2000: break
            except Exception:
                continue

        total = len(matches)
        if mode == "files_only":
            paths = sorted(list({m.path for m in matches}))
            return SearchResult(files=paths[offset:offset+limit], total_count=len(paths))
        elif mode == "count":
            counts = {}
            for m in matches:
                counts[m.path] = counts.get(m.path, 0) + 1
            return SearchResult(counts=counts, total_count=total)

        return SearchResult(
            matches=matches[offset:offset+limit],
            total_count=total,
            truncated=total > offset + limit
        )
