"""Pure compiler-input reference model. No filesystem, shell or compiler I/O.

The caller supplies immutable inventories obtained through trusted no-follow
materialization. This models input validation, not a compiler sandbox or binding
engine. See specification/compiler-profile.md for the runtime release gates.
"""
from __future__ import annotations

import hashlib
import json
import re
import shlex
from dataclasses import dataclass
from typing import Mapping


PROFILE_VERSION = "strict-posix-clang-v1"
MAX_BYTES = 262_144
MAX_ARGS = 1_024
MAX_TOKEN_BYTES = 8_192
GUARD_FLAGS = ("-nostdinc", "-nostdinc++", "-fno-modules", "-fno-implicit-modules")
PATH_OPTIONS = ("-iframework", "-idirafter", "-isystem", "-iquote", "-I", "-F")
STANDARDS = {
    "c": frozenset(("c89", "c90", "c99", "c11", "c17", "gnu89", "gnu90", "gnu99", "gnu11", "gnu17")),
    "c++": frozenset(("c++98", "c++03", "c++11", "c++14", "c++17", "c++20", "gnu++98", "gnu++03", "gnu++11", "gnu++14", "gnu++17", "gnu++20")),
}
NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
TRIPLE = re.compile(r"[A-Za-z0-9_]+(?:-[A-Za-z0-9_.]+){1,4}\Z")
SHELL_OPERATORS = frozenset((";", "&", "&&", "|", "||", "<", ">", ">>", "<<", "(", ")"))


class InvalidContext(ValueError):
    """Expected input limitation: MISSING_BUILD_CONTEXT, never worker failure."""

    basis = "MISSING_BUILD_CONTEXT"

    def __init__(self, code: str, field: str = "arguments") -> None:
        self.code = code
        self.field = field
        # Do not echo untrusted values (which may contain secrets) into errors.
        super().__init__(f"{code}: {field}")


def _text(value: object, field: str, *, tabs: bool = False, limit: int = MAX_TOKEN_BYTES) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidContext("INVALID_FIELD", field)
    try:
        size = len(value.encode("utf-8", errors="strict"))
    except UnicodeError as exc:
        raise InvalidContext("INVALID_ENCODING", field) from exc
    if size > limit:
        raise InvalidContext("INPUT_LIMIT", field)
    if any((ord(c) < 32 and not (tabs and c == "\t")) or ord(c) == 127 for c in value):
        raise InvalidContext("CONTROL_CHARACTER", field)
    return value


def tokenize_command(command: object, platform: str = "posix") -> tuple[str, ...]:
    """Strict POSIX data tokenizer; rejects expansion even inside quotes."""
    if platform != "posix":
        raise InvalidContext("UNSUPPORTED_COMMAND_PLATFORM", "command")
    raw = _text(command, "command", tabs=True, limit=MAX_BYTES)
    if "$" in raw or "`" in raw:
        raise InvalidContext("SHELL_SYNTAX", "command")
    quote = None
    escaped = False
    for char in raw:
        if escaped:
            escaped = False
        elif char == "\\" and quote != "'":
            escaped = True
        elif quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char in ";&|<>()*?[]{}~#!":
            raise InvalidContext("SHELL_SYNTAX", "command")
    try:
        # comments=False is essential: never silently discard a command suffix.
        return tuple(shlex.split(raw, comments=False, posix=True))
    except ValueError as exc:
        raise InvalidContext("INVALID_COMMAND_QUOTING", "command") from exc


def _path_parts(value: str, field: str) -> tuple[str, ...]:
    _text(value, field)
    if value.startswith("@"):
        raise InvalidContext("RESPONSE_FILE", field)
    if "\\" in value or re.match(r"^[A-Za-z]:", value) or value.startswith("//"):
        raise InvalidContext("NON_POSIX_PATH", field)
    if "$" in value or "`" in value or value.startswith("~"):
        raise InvalidContext("SHELL_SYNTAX", field)
    return tuple(value.split("/"))


def _canonical_root(value: str) -> tuple[str, ...]:
    try:
        parts = _path_parts(value, "profile.root")
    except InvalidContext as exc:
        raise ValueError("invalid trusted profile root") from exc
    if not value.startswith("/") or value == "/" or any(p in ("", ".", "..") for p in parts[1:]):
        raise ValueError("profile roots must be canonical absolute POSIX paths other than /")
    return parts[1:]


@dataclass(frozen=True)
class Root:
    """Frozen virtual inventory; relative paths have no leading/trailing slash.

    Directories are inferred from entries, with optional captured empty dirs.
    Symlink names are known but no link is ever followed by this strict profile.
    Native root ancestors must have been verified separately by materialization.
    """

    name: str
    original: str
    staged: str
    files: frozenset[str]
    symlinks: frozenset[str] = frozenset()
    directories: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not NAME.fullmatch(self.name):
            raise ValueError("invalid root identity")
        _canonical_root(self.original)
        _canonical_root(self.staged)
        for collection, is_directory in ((self.files, False), (self.symlinks, False), (self.directories, True)):
            if not isinstance(collection, frozenset):
                raise ValueError("inventories must be frozen")
            for path in collection:
                if is_directory and path == "":
                    continue
                try:
                    parts = _path_parts(path, "profile.inventory")
                except InvalidContext as exc:
                    raise ValueError("invalid trusted inventory entry") from exc
                if any(p in ("", ".", "..") for p in parts):
                    raise ValueError("noncanonical inventory entry")
        if self.files & self.symlinks:
            raise ValueError("conflicting inventory node kinds")
        dirs = set(self.directories) | {""}
        for path in self.files | self.symlinks | self.directories:
            parts = path.split("/")
            dirs.update("/".join(parts[:i]) for i in range(1, len(parts)))
        if (self.files | self.symlinks) & dirs:
            raise ValueError("non-directory inventory ancestor")
        object.__setattr__(self, "directories", frozenset(dirs))


@dataclass(frozen=True)
class CompilerProfile:
    snapshot: Root
    resources: tuple[Root, ...]
    snapshot_id: str
    toolchain_id: str
    default_target: str
    allowed_targets: frozenset[str]
    drivers: frozenset[str] = frozenset(("clang", "clang++", "/usr/bin/clang", "/usr/bin/clang++"))
    system_includes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        roots = (self.snapshot, *self.resources)
        if not isinstance(self.resources, tuple) or not isinstance(self.system_includes, tuple):
            raise ValueError("profile collections must be immutable")
        if not isinstance(self.drivers, frozenset) or not isinstance(self.allowed_targets, frozenset):
            raise ValueError("profile allowlists must be immutable")
        if not self.snapshot_id or not self.toolchain_id or len({r.name for r in roots}) != len(roots):
            raise ValueError("missing or duplicate profile identity")
        for attr in ("original", "staged"):
            paths = [_canonical_root(getattr(r, attr)) for r in roots]
            for i, left in enumerate(paths):
                for right in paths[i + 1:]:
                    if left[:len(right)] == right or right[:len(left)] == left:
                        raise ValueError("profile roots must not overlap")
        if self.default_target not in self.allowed_targets or any(not TRIPLE.fullmatch(t) for t in self.allowed_targets):
            raise ValueError("invalid approved target profile")
        for driver in self.drivers:
            if not re.fullmatch(r"(?:/[A-Za-z0-9_.+/-]+/)?clang(?:\+\+)?(?:-[0-9]+)?", driver):
                raise ValueError("driver labels must be explicit Clang spellings")
            if "/" in driver:
                _canonical_root(driver)
        for include in self.system_includes:
            try:
                _map_path(include, self.snapshot.original, self, kind="directory", resource_only=True)
            except InvalidContext as exc:
                raise ValueError("invalid trusted system include") from exc


@dataclass(frozen=True)
class MappedPath:
    staged: str
    logical: str


def _map_path(value: str, directory: str, profile: CompilerProfile, *, kind: str,
              source_only: bool = False, resource_only: bool = False) -> MappedPath:
    parts = _path_parts(value, "path")
    absolute = value.startswith("/")
    combined = parts[1:] if absolute else tuple(directory.strip("/").split("/")) + parts
    roots = (profile.snapshot, *profile.resources)
    root = next((r for r in roots if combined[:len(_canonical_root(r.original))] == _canonical_root(r.original)), None)
    if root is None or (source_only and root != profile.snapshot) or (resource_only and root == profile.snapshot):
        raise InvalidContext("PATH_OUTSIDE_ROOT", "path")
    floor = len(_canonical_root(root.original))
    relative: list[str] = []
    tail = combined[floor:]
    for index, part in enumerate(tail):
        if part in ("", "."):
            continue
        if part == "..":
            if not relative:
                raise InvalidContext("PATH_TRAVERSAL", "path")
            relative.pop()
            continue
        relative.append(part)
        prefix = "/".join(relative)
        if prefix in root.symlinks:
            raise InvalidContext("SYMLINK_PATH", "path")
        # Check traversal components before lexical '..' normalization: a
        # regular/missing ancestor cannot be made into a directory by '/..'.
        if prefix not in root.directories and prefix not in root.files:
            raise InvalidContext("PATH_NOT_CAPTURED", "path")
        if prefix in root.files and index != len(tail) - 1:
            raise InvalidContext("NOT_A_DIRECTORY", "path")
    rel = "/".join(relative)
    inventory = root.files if kind == "file" else root.directories
    if rel not in inventory:
        raise InvalidContext("PATH_KIND_MISMATCH", "path")
    suffix = "/" + rel if rel else ""
    return MappedPath(root.staged + suffix, root.name + ":/" + rel)


@dataclass(frozen=True)
class SanitizedContext:
    source: str
    source_identity: str
    flags: tuple[str, ...]
    provenance: tuple[str, ...]
    fingerprint: str


def sanitize(entry: Mapping[str, object], profile: CompilerProfile, *, command_platform: str = "posix") -> SanitizedContext:
    """Validate one command object atomically; return no partial accepted flags."""
    if not isinstance(entry, Mapping) or set(entry) - {"directory", "file", "arguments", "command", "output"}:
        raise InvalidContext("INVALID_ENTRY", "entry")
    directory = _text(entry.get("directory"), "directory")
    if not directory.startswith("/"):
        raise InvalidContext("DIRECTORY_NOT_ABSOLUTE", "directory")
    _map_path(directory, profile.snapshot.original, profile, kind="directory", source_only=True)
    source_name = _text(entry.get("file"), "file")
    source = _map_path(source_name, directory, profile, kind="file", source_only=True)
    provenance = ["ARGV0_DISCARDED", "SOURCE_PASSED_SEPARATELY"]
    if "output" in entry:
        _text(entry["output"], "output")
        provenance.append("OUTPUT_METADATA_IGNORED")
    if "arguments" in entry:
        raw = entry["arguments"]
        if not isinstance(raw, list):
            raise InvalidContext("INVALID_ARGUMENT_ARRAY")
        if not 2 <= len(raw) <= MAX_ARGS:
            raise InvalidContext("ARGUMENT_COUNT")
        args = tuple(raw)
        if "command" in entry:
            provenance.append("COMMAND_IGNORED_ARGUMENTS_PREFERRED")
    else:
        args = tokenize_command(entry.get("command"), command_platform)
        provenance.append("POSIX_COMMAND_TOKENIZED")
    if not 2 <= len(args) <= MAX_ARGS:
        raise InvalidContext("ARGUMENT_COUNT")
    for token in args:
        _text(token, "arguments")
        if "$" in token or "`" in token or token in SHELL_OPERATORS:
            raise InvalidContext("SHELL_SYNTAX")
        if token.startswith("@"):
            raise InvalidContext("RESPONSE_FILE")
    if sum(len(t.encode("utf-8")) for t in args) > MAX_BYTES:
        raise InvalidContext("INPUT_LIMIT")
    if args[0] not in profile.drivers:
        raise InvalidContext("UNAPPROVED_DRIVER", "arguments[0]")
    flags: list[str] = []
    logical_flags: list[str] = []
    singleton: dict[str, str] = {}
    seen_source = False
    i = 1
    while i < len(args):
        token = args[i]
        option = None
        value = None
        for name in (*PATH_OPTIONS, "-D", "-U", "-x"):
            if token == name or token.startswith(name):
                option = name
                value = token[len(name):]
                break
        if token == "-target":
            option, value = "target", ""
        elif token.startswith("--target="):
            option, value = "target", token[len("--target="):]
            if not value:
                raise InvalidContext("MISSING_OPERAND")
        elif token.startswith("-std="):
            option, value = "std", token[len("-std="):]
            if not value:
                raise InvalidContext("MISSING_OPERAND")
        if option is not None:
            if not value:
                i += 1
                if i >= len(args) or args[i].startswith("-"):
                    raise InvalidContext("MISSING_OPERAND")
                value = args[i]
            if value.startswith("@"):
                raise InvalidContext("RESPONSE_FILE")
            if value.startswith(("-", "=")):
                raise InvalidContext("INVALID_OPERAND")
            if option in PATH_OPTIONS:
                path = _map_path(value, directory, profile, kind="directory")
                flags.extend((option, path.staged))
                logical_flags.extend((option, path.logical))
            elif option in ("-D", "-U"):
                name = value.split("=", 1)[0] if option == "-D" else value
                if not NAME.fullmatch(name):
                    raise InvalidContext("INVALID_MACRO")
                flags.append(option + value)
                logical_flags.append(option + value)
            else:
                key = "language" if option == "-x" else option
                if key in singleton:
                    raise InvalidContext("DUPLICATE_OPTION")
                singleton[key] = value
        elif token.startswith("-"):
            # Includes action/output/plugin/forwarding/module/config flags.
            raise InvalidContext("UNSUPPORTED_OPTION")
        else:
            if seen_source or i != len(args) - 1:
                raise InvalidContext("SOURCE_NOT_FINAL_OR_MULTIPLE")
            mapped = _map_path(token, directory, profile, kind="file", source_only=True)
            if mapped.logical != source.logical:
                raise InvalidContext("SOURCE_MISMATCH")
            seen_source = True
        i += 1
    if not seen_source:
        raise InvalidContext("MISSING_SOURCE")
    language = singleton.get("language")
    if language is None:
        suffix = source_name.rsplit(".", 1)[-1]
        language = "c" if suffix == "c" else "c++" if suffix in ("cc", "cpp", "cxx", "C") else None
        provenance.append("LANGUAGE_FROM_SUFFIX")
    if language not in STANDARDS:
        raise InvalidContext("UNSUPPORTED_LANGUAGE")
    standard = singleton.get("std", "c17" if language == "c" else "c++20")
    if standard not in STANDARDS[language]:
        raise InvalidContext("UNSUPPORTED_STANDARD")
    if "std" not in singleton:
        provenance.append("DEFAULT_STANDARD")
    target = singleton.get("target", profile.default_target)
    if target not in profile.allowed_targets:
        raise InvalidContext("UNAPPROVED_TARGET")
    if "target" not in singleton:
        provenance.append("DEFAULT_TARGET")
    prefix = (*GUARD_FLAGS, "-x", language, "-std=" + standard, "--target=" + target)
    flags = [*prefix, *flags]
    logical_flags = [*prefix, *logical_flags]
    for include in profile.system_includes:
        path = _map_path(include, directory, profile, kind="directory", resource_only=True)
        flags.extend(("-isystem", path.staged))
        logical_flags.extend(("-isystem", path.logical))
    encoded = json.dumps({"version": PROFILE_VERSION, "snapshot": profile.snapshot_id,
        "toolchain": profile.toolchain_id, "source": source.logical,
        "flags": logical_flags, "assumptions": sorted(p for p in provenance if p in (
            "LANGUAGE_FROM_SUFFIX", "DEFAULT_STANDARD", "DEFAULT_TARGET"))},
        sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return SanitizedContext(source.staged, source.logical, tuple(flags), tuple(provenance), hashlib.sha256(encoded).hexdigest())
