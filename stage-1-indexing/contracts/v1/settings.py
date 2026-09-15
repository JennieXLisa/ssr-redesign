"""Exact settings reference; loading never discovers configuration in target code."""
from copy import deepcopy
from typing import Annotated, Literal

from pydantic import Field, model_validator
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


class SemanticProfile(Model):
    schema_version: Version = 1
    language_overrides: list[LanguageOverride] = Field(default_factory=list)
    encoding_overrides: list[EncodingOverride] = Field(default_factory=list)
    package_roots: list[str] = Field(default_factory=list)
    module_aliases: dict[str, str] = Field(default_factory=dict)
    compilation_database: str | None = None

    @model_validator(mode='after')
    def paths(self):
        paths = [*self.package_roots, *self.module_aliases.values()]
        if self.compilation_database is not None:
            paths.append(self.compilation_database)
        for path in paths:
            if path.startswith('/') or '\x00' in path or any(p in ('.', '..') for p in path.split('/')):
                raise ValueError('profile paths must be normalized snapshot-relative paths')
        if self.compilation_database == '':
            raise ValueError('compilation database must name a snapshot file')
        if len(self.package_roots) != len(set(self.package_roots)):
            raise ValueError('package roots must be unique')
        if any(not alias for alias in self.module_aliases):
            raise ValueError('module aliases must be nonempty')
        # The canonical path owner additionally decodes %HH and validates scope.
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
