"""Exact settings reference; loading never discovers configuration in target code."""
from copy import deepcopy
import re
from typing import Annotated, Literal
from urllib.parse import unquote_to_bytes

from pydantic import AfterValidator, Field, field_validator, model_validator
from models import Count, Language, Model, Version

Positive = Annotated[int, Field(strict=True, ge=1)]
Codec = Literal['utf-8', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']


class StorageSettings(Model):
    postgres_major: Annotated[int, Field(strict=True, ge=17, le=17)] = 17


class WorkerSettings(Model):
    heavy_slots: Positive = 4
    scanner_slots: Positive = 2
    lease_seconds: Positive = 120
    heartbeat_seconds: Positive = 20
    max_attempts: Positive = 3
    retry_delays_seconds: list[Count] = Field(default_factory=lambda: [1, 5])
    scanner_batch_files: Positive = 32
    memory_pause_available_bytes: Count = 2147483648
    memory_resume_available_bytes: Count = 3221225472

    @model_validator(mode='after')
    def budgets(self):
        if self.scanner_slots > self.heavy_slots:
            raise ValueError('scanner slots are part of, not additional to, heavy slots')
        if self.heartbeat_seconds >= self.lease_seconds:
            raise ValueError('heartbeat must be shorter than lease')
        if self.memory_resume_available_bytes <= self.memory_pause_available_bytes:
            raise ValueError('resume memory threshold must exceed pause threshold')
        if len(self.retry_delays_seconds) != self.max_attempts - 1:
            raise ValueError('one retry delay is required for each automatic retry')
        return self


class NavigationSettings(Model):
    page_default: Annotated[int, Field(strict=True, ge=1, le=200)] = 50
    page_max: Annotated[int, Field(strict=True, ge=200, le=200)] = 200
    metadata_response_bytes: Positive = 50000
    source_response_bytes: Annotated[int, Field(strict=True, ge=1, le=1000000)] = 50000
    source_response_max_bytes: Annotated[int, Field(strict=True, ge=1000000, le=1000000)] = 1000000
    error_response_target_bytes: Positive = 65536
    token_max_bytes: Annotated[int, Field(strict=True, ge=4096, le=4096)] = 4096
    query_timeout_seconds: Positive = 30
    signature_excerpt_bytes: Annotated[int, Field(strict=True, ge=1024, le=1024)] = 1024
    text_excerpt_bytes: Annotated[int, Field(strict=True, ge=512, le=512)] = 512
    nested_collection_page: Annotated[int, Field(strict=True, ge=8, le=8)] = 8


class RuleSettings(Model):
    mode: Literal['combined', 'custom_only'] = 'combined'
    name_timeout_seconds: Positive = 10
    semgrep_jobs_per_invocation: Annotated[int, Field(strict=True, ge=1, le=1)] = 1


class Settings(Model):
    schema_version: Version = 1
    storage: StorageSettings = Field(default_factory=StorageSettings)
    workers: WorkerSettings = Field(default_factory=WorkerSettings)
    navigation: NavigationSettings = Field(default_factory=NavigationSettings)
    rules: RuleSettings = Field(default_factory=RuleSettings)


class LanguageOverride(Model):
    path_glob: Annotated[str, Field(min_length=1)]
    language: Language


class EncodingOverride(Model):
    path_glob: Annotated[str, Field(min_length=1)]
    codec: Codec


def snapshot_directory(path: str) -> str:
    """Validate profile path syntax; inventory/alias containment remains owner work.

    The empty string denotes the snapshot root. Decode percent escapes once for
    boundary checks; never interpret a profile path as a host filesystem path.
    """
    if path == '':
        return path
    if re.search(r'%(?![0-9A-Fa-f]{2})', path):
        raise ValueError('malformed profile path escape')
    raw = unquote_to_bytes(path)
    if (b'\x00' in raw or b'\\' in raw or re.match(br'^[A-Za-z]:', raw)
            or any(part in (b'', b'.', b'..') for part in raw.split(b'/'))):
        raise ValueError('profile paths must be normalized snapshot-relative paths')
    return path


def snapshot_file(path: str) -> str:
    snapshot_directory(path)
    if not path:
        raise ValueError('profile file must name a snapshot entry')
    return path


SnapshotDirectory = Annotated[str, AfterValidator(snapshot_directory)]
SnapshotFile = Annotated[str, AfterValidator(snapshot_file)]


class BasicFileOptions(Model):
    path: SnapshotFile
    language: Literal['python', 'c', 'cpp', 'java', 'lua']


class JavaScriptFileOptions(Model):
    path: SnapshotFile
    language: Literal['javascript', 'jsx', 'typescript', 'tsx']
    mode: Literal['script', 'module', 'commonjs'] = 'script'
    strict: bool = False

    @model_validator(mode='before')
    @classmethod
    def mode_default(cls, value):
        if isinstance(value, dict) and 'strict' not in value:
            value = {**value, 'strict': value.get('mode') == 'module'}
        return value

    @model_validator(mode='after')
    def module_is_strict(self):
        if self.mode == 'module' and not self.strict:
            raise ValueError('module mode requires strict semantics')
        return self


class PhpFileOptions(Model):
    path: SnapshotFile
    language: Literal['php']
    input: Literal['mixed', 'php-only'] = 'mixed'


class ShellFileOptions(Model):
    path: SnapshotFile
    language: Literal['bash', 'zsh']
    cwd_snapshot: SnapshotDirectory | None = None


FileOptions = Annotated[
    BasicFileOptions | JavaScriptFileOptions | PhpFileOptions | ShellFileOptions,
    Field(discriminator='language'),
]
CStandard = Literal['c89', 'c90', 'c99', 'c11', 'c17', 'gnu89', 'gnu90', 'gnu99', 'gnu11', 'gnu17']
CppStandard = Literal['c++98', 'c++03', 'c++11', 'c++14', 'c++17', 'c++20',
                      'gnu++98', 'gnu++03', 'gnu++11', 'gnu++14', 'gnu++17', 'gnu++20']


def immutable_array(value):
    """JSON arrays become tuples; reject scalar strings, sets and generators."""
    if not isinstance(value, (list, tuple)):
        raise ValueError('profile collection must be an array')
    return tuple(value)


class CompilerOptions(Model):
    language: Literal['c', 'cpp']
    standard: CStandard | CppStandard
    include_roots: tuple[SnapshotDirectory, ...] = ('',)
    translation_units: Annotated[tuple[SnapshotFile, ...], Field(min_length=1)]

    @field_validator('include_roots', 'translation_units', mode='before')
    @classmethod
    def arrays(cls, value):
        return immutable_array(value)

    @model_validator(mode='after')
    def compatible_inputs(self):
        if ('++' in self.standard) != (self.language == 'cpp'):
            raise ValueError('compiler standard does not match selected dialect')
        for items in (self.include_roots, self.translation_units):
            if len(items) != len(set(items)):
                raise ValueError('compiler input paths must be unique')
        return self


class SemanticProfile(Model):
    schema_version: Version = 1
    language_overrides: list[LanguageOverride] = Field(default_factory=list)
    encoding_overrides: list[EncodingOverride] = Field(default_factory=list)
    package_roots: list[SnapshotDirectory] = Field(default_factory=list)
    module_aliases: dict[str, SnapshotDirectory] = Field(default_factory=dict)
    compilation_database: SnapshotFile | None = None
    file_options: tuple[FileOptions, ...] = ()
    compiler_options: tuple[CompilerOptions, ...] = ()

    @field_validator('file_options', 'compiler_options', mode='before')
    @classmethod
    def arrays(cls, value):
        return immutable_array(value)

    @model_validator(mode='after')
    def paths(self):
        if len(self.package_roots) != len(set(self.package_roots)):
            raise ValueError('package roots must be unique')
        if any(not alias for alias in self.module_aliases):
            raise ValueError('module aliases must be nonempty')
        selected = {item.path: item.language for item in self.file_options}
        if len(selected) != len(self.file_options):
            raise ValueError('one exact-path language option is allowed per file')
        if self.compilation_database is not None and self.compiler_options:
            raise ValueError('select compilation_database or compiler_options, not both')
        translation_units = []
        for options in self.compiler_options:
            for path in options.translation_units:
                if path in selected and selected[path] != options.language:
                    raise ValueError('translation unit contradicts exact-path dialect')
                translation_units.append(path)
        if len(translation_units) != len(set(translation_units)):
            raise ValueError('translation unit occurs in multiple explicit compiler selections')
        # The canonical path owner additionally verifies canonical display encoding,
        # captured node kind, decoded aliases, and all path/override associations.
        return self


def merge_settings(*layers: dict) -> Settings:
    """Low-to-high precedence; tables merge, arrays/scalars replace as a whole."""
    default = Settings().model_dump(mode='json')
    result = deepcopy(default)

    def merge(target, layer, shape, path=''):
        if not isinstance(layer, dict):
            raise ValueError(f'{path or "settings"} must be a table')
        for key, value in layer.items():
            if key not in shape:
                raise ValueError(f'unknown setting {path}{key}')
            if isinstance(shape[key], dict):
                merge(target[key], value, shape[key], f'{path}{key}.')
            else:
                target[key] = deepcopy(value)

    for layer in layers:
        merge(result, layer, default)
    return Settings.model_validate(result)
