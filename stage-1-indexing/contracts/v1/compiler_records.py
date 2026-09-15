"""Durable compiler inputs and observations, not a compiler or a queue.

W02/W09 adopt these internal values. SQL and publication owners enforce selected
dataset/publication membership; native W09 tests establish actual compiler evidence.
"""
from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID, uuid5

from pydantic import Field, model_validator
from models import ByteRange, Count, Digest, Id, Model, Usage, Version
from records import canonical_bytes, semantic_digest

Nonempty = Annotated[str, Field(min_length=1)]
Code = Annotated[str, Field(pattern=r'^[A-Z][A-Z0-9_]{0,95}$')]


def compiler_semantics(value):
    """Retain exact values while removing only extraction-publication audit links."""
    if isinstance(value, dict):
        return {k: compiler_semantics(v) for k, v in value.items() if k != 'extraction_publication_id'}
    if isinstance(value, (tuple, list)):
        return [compiler_semantics(v) for v in value]
    return value


def compiler_record_id(context_id: str, kind: str, value: dict) -> str:
    return str(uuid5(UUID(context_id), canonical_bytes([kind, compiler_semantics(value)]).decode('utf-8')))


class EffectiveContext(Model):
    """Exact logical hash payload of strict-posix-clang-v1 (no staging roots).

    The owner must compare this to actual sanitizer output; a DTO/digest alone
    cannot certify that untrusted compiler arguments passed the grammar.
    """
    version: Literal['strict-posix-clang-v1']
    snapshot: Id
    toolchain: Nonempty
    source: Nonempty
    flags: tuple[Nonempty, ...]
    assumptions: tuple[Literal['LANGUAGE_FROM_SUFFIX', 'DEFAULT_STANDARD', 'DEFAULT_TARGET'], ...]

    @model_validator(mode='after')
    def stable_assumptions(self):
        if list(self.assumptions) != sorted(set(self.assumptions)):
            raise ValueError('effective assumptions must be unique and sorted')
        return self


class ContextSpec(Model):
    """Input descriptor before allocating resolution/context identities.

    entry_digest identifies captured command data or an explicit conservative
    recipe. effective_digest is the strict sanitizer's stable logical projection.
    Raw executable strings and staging roots are never stored here.
    """
    ordinal: Count
    origin: Literal['compilation_database', 'conservative']
    entry_digest: Digest
    translation_unit_file_id: Id | None
    effective_digest: Digest | None
    effective: EffectiveContext | None
    rejection_code: Code | None

    @model_validator(mode='after')
    def accepted_or_rejected(self):
        if self.rejection_code is None:
            if self.translation_unit_file_id is None or self.effective is None or self.effective_digest is None:
                raise ValueError('accepted context requires a captured TU and effective profile')
            if self.effective_digest != semantic_digest(self.effective.model_dump(mode='json')):
                raise ValueError('effective compiler payload digest mismatch')
        elif self.effective_digest is not None or self.effective is not None:
            raise ValueError('rejected context cannot retain a partial effective profile')
        return self


class ContextDefinition(Model):
    context_id: Id
    spec: ContextSpec


def compiler_input_digest(profile_digest: str, specs: tuple[ContextSpec, ...]) -> str:
    return semantic_digest(dict(schema_version=1, profile_digest=profile_digest,
                                contexts=[s.model_dump(mode='json') for s in specs]))


class ContextCensus(Model):
    schema_version: Version = 1
    snapshot_id: Id
    extraction_id: Id
    resolution_id: Id
    profile_digest: Digest
    input_digest: Digest
    contexts: tuple[ContextDefinition, ...]

    @model_validator(mode='after')
    def exact_census(self):
        specs = tuple(c.spec for c in self.contexts)
        if [s.ordinal for s in specs] != list(range(len(specs))):
            raise ValueError('context ordinals must be contiguous captured selection order')
        if compiler_input_digest(self.profile_digest, specs) != self.input_digest:
            raise ValueError('compiler input census digest mismatch')
        for context in self.contexts:
            if context.spec.effective is not None and context.spec.effective.snapshot != self.snapshot_id:
                raise ValueError('effective context belongs to another snapshot')
            expected = compiler_record_id(self.resolution_id, 'context', context.spec.model_dump(mode='json'))
            if context.context_id != expected:
                raise ValueError('context identity is not derived from the frozen input')
        return self


class SourceEvidence(Model):
    file_id: Id
    range: ByteRange
    bytes_digest: Digest


class ReferenceAnchor(Model):
    reference_id: Id
    extraction_publication_id: Id
    usage: Usage
    source: SourceEvidence


class OccurrenceAnchor(Model):
    occurrence_id: Id
    symbol_id: Id
    extraction_publication_id: Id
    role: Literal['definition', 'declaration']
    source: SourceEvidence


class ReferenceCensus(Model):
    """O(R) durable inventory; expected context pairs are its Cartesian product.

    Publication IDs are audit links. reference_digest replaces them with exact
    immutable source identity when hashing, never with a resolution result.
    """
    resolution_id: Id
    extraction_id: Id
    references: tuple[ReferenceAnchor, ...]
    reference_digest: Digest

    @model_validator(mode='after')
    def exact_inventory(self):
        ids = [r.reference_id for r in self.references]
        if ids != sorted(set(ids)):
            raise ValueError('reference inventory must be unique and UUID sorted')
        projection = [r.model_dump(mode='json', exclude={'extraction_publication_id'}) for r in self.references]
        if self.reference_digest != semantic_digest(projection):
            raise ValueError('reference inventory digest mismatch')
        return self


class CompilerFileVisit(Model):
    file_id: Id
    bytes_digest: Digest
    visit_count: Annotated[int, Field(strict=True, ge=1)]
    inactive_ranges: tuple[SourceEvidence, ...] = ()

    @model_validator(mode='after')
    def inactive_evidence(self):
        if self.visit_count != 1 and self.inactive_ranges:
            raise ValueError('repeated inclusions cannot supply a universal inactive proof')
        last = 0
        for evidence in self.inactive_ranges:
            span = evidence.range
            if evidence.file_id != self.file_id or span.start_byte < last or span.start_byte == span.end_byte:
                raise ValueError('inactive spans must be nonempty, disjoint, ordered and in this file')
            last = span.end_byte
        return self


class CompilerEntity(Model):
    entity_id: Id
    usr: Nonempty
    cursor_kind: Nonempty
    anchor: OccurrenceAnchor


class ExternalEntity(Model):
    """Exact resource identity; never a captured occurrence or readable file ID."""
    resource_digest: Digest
    path: Nonempty
    range: ByteRange
    bytes_digest: Digest
    usr: Nonempty
    name: Nonempty

    @model_validator(mode='after')
    def logical_path(self):
        if self.path.startswith('/') or '\\' in self.path or any(p in ('', '.', '..') for p in self.path.split('/')):
            raise ValueError('external source must use a resource-relative path')
        return self


class CompilerObservation(Model):
    observation_id: Id
    reference_id: Id
    source: SourceEvidence
    spelling: SourceEvidence
    expansion: SourceEvidence
    cursor_kind: Nonempty
    dispatch: Literal['DIRECT', 'UNSUPPORTED']
    target_entity_id: Id | None
    external: ExternalEntity | None

    @model_validator(mode='after')
    def one_target(self):
        if (self.target_entity_id is None) == (self.external is None):
            raise ValueError('observation requires exactly one captured or external target')
        # v1 deliberately rejects ambiguous macro/instantiation mapping. A later
        # profile may support distinct extents only with an exact mapping proof.
        if self.spelling != self.source or self.expansion != self.source:
            raise ValueError('v1 requires one identical physical source extent')
        return self


class CompilerDiagnostic(Model):
    code: Literal['INVALID_CONTEXT', 'COMPILER_ERROR', 'COMPILER_WARNING',
                  'UNMAPPED_CURSOR', 'MULTIPLE_PHYSICAL_MAPPINGS', 'UNSUPPORTED_DISPATCH']
    severity: Literal['error', 'warning', 'limitation']
    source: SourceEvidence | None
    detail_code: Code | None
    message: Annotated[str, Field(max_length=2048)]

    @model_validator(mode='after')
    def severity_matches(self):
        if (self.code in ('INVALID_CONTEXT', 'COMPILER_ERROR')) != (self.severity == 'error'):
            raise ValueError('compiler rejection/error diagnostics must be errors')
        return self


class ContextOutput(Model):
    schema_version: Version = 1
    snapshot_id: Id
    extraction_id: Id
    resolution_id: Id
    context_id: Id
    input_digest: Digest
    status: Literal['VALID', 'INVALID']
    file_census_complete: bool
    files: tuple[CompilerFileVisit, ...] = ()
    entities: tuple[CompilerEntity, ...] = ()
    observations: tuple[CompilerObservation, ...] = ()
    diagnostics: tuple[CompilerDiagnostic, ...] = ()

    @model_validator(mode='after')
    def inventory(self):
        has_errors = any(d.severity == 'error' for d in self.diagnostics)
        if self.status == 'INVALID':
            if not has_errors or self.file_census_complete or self.files or self.entities or self.observations:
                raise ValueError('invalid context is diagnostic-only, never partial evidence')
        elif has_errors or not self.file_census_complete:
            raise ValueError('valid context requires a complete file census and no binding errors')
        for values, key in ((self.files, 'file_id'), (self.entities, 'entity_id'),
                            (self.observations, 'observation_id'), (self.observations, 'reference_id')):
            ids = [getattr(v, key) for v in values]
            if len(ids) != len(set(ids)):
                raise ValueError('duplicate compiler result identity or physical reference')
        digests = [semantic_digest(d.model_dump(mode='json')) for d in self.diagnostics]
        if len(digests) != len(set(digests)):
            raise ValueError('duplicate output diagnostic')
        file_ids = {f.file_id for f in self.files}
        entity_ids = {e.entity_id for e in self.entities}
        for entity in self.entities:
            if entity.anchor.source.file_id not in file_ids:
                raise ValueError('entity must have a captured file visit')
            value = entity.model_dump(mode='json', exclude={'entity_id'})
            if entity.entity_id != compiler_record_id(self.context_id, 'entity', value):
                raise ValueError('unstable compiler entity identity')
        for observation in self.observations:
            if observation.source.file_id not in file_ids:
                raise ValueError('observation must have a captured file visit')
            if observation.target_entity_id is not None and observation.target_entity_id not in entity_ids:
                raise ValueError('target entity must belong to the same compiler publication')
            value = observation.model_dump(mode='json', exclude={'observation_id'})
            if observation.observation_id != compiler_record_id(self.context_id, 'observation', value):
                raise ValueError('unstable compiler observation identity')
            for visit in self.files:
                if visit.file_id == observation.source.file_id:
                    for skipped in visit.inactive_ranges:
                        a, b = skipped.range, observation.source.range
                        if a.start_byte < b.end_byte and b.start_byte < a.end_byte:
                            raise ValueError('observed reference overlaps an inactive proof')
        return self


class ContextWork(Model):
    context_id: Id
    work_id: Id
    resolution_id: Id
    state: Literal['PENDING', 'RUNNING', 'FAILED', 'SUCCEEDED'] = 'PENDING'
    generation: Count = 0
    attempt_count: Count = 0
    retry_cycle_attempt_count: Count = 0
    lease_token: Id | None = None
    lease_expires_at: Count | None = None
    next_attempt_at: Count | None = None
    active_publication_id: Id | None = None
    last_diagnostic_id: Id | None = None

    @model_validator(mode='after')
    def ownership(self):
        if self.work_id != compiler_record_id(self.context_id, 'work', {}):
            raise ValueError('context work identity is immutable')
        if self.state == 'RUNNING':
            if self.lease_token is None or self.lease_expires_at is None or not self.generation:
                raise ValueError('running context requires current lease ownership')
        elif self.lease_token is not None or self.lease_expires_at is not None:
            raise ValueError('nonrunning context cannot own a lease')
        if (self.state == 'SUCCEEDED') != (self.active_publication_id is not None):
            raise ValueError('only success activates a publication')
        if self.retry_cycle_attempt_count > self.attempt_count:
            raise ValueError('cycle attempts exceed lifetime attempts')
        return self


class CompilerAttemptDiagnostic(Model):
    diagnostic_id: Id
    work_id: Id
    generation: Annotated[int, Field(strict=True, ge=1)]
    code: Literal['LIBRARY_START_FAILED', 'WORKER_CRASH', 'TIMEOUT', 'ISOLATION_FAILED',
                  'STORAGE_INTEGRITY_ERROR', 'TRANSIENT_IO', 'ADAPTER_ERROR', 'LEASE_EXPIRED']
    message: Annotated[str, Field(max_length=2048)]


class ContextPublication(Model):
    """Sealed candidate/final receipt, not a partially written staging row.

    Raw compiler_publications rows can have null count/digest while batches are
    incomplete; this model is constructed only after the complete output seals.
    """
    publication_id: Id
    work_id: Id
    generation: Annotated[int, Field(strict=True, ge=1)]
    committed: bool
    result_count: Annotated[int, Field(strict=True, ge=1)]
    result_digest: Digest
    output: ContextOutput


COMPILER_MODELS = [EffectiveContext, ContextSpec, ContextDefinition, ContextCensus, SourceEvidence,
                   ReferenceAnchor, OccurrenceAnchor, ReferenceCensus, CompilerFileVisit,
                   CompilerEntity, ExternalEntity, CompilerObservation, CompilerDiagnostic,
                   ContextOutput, ContextWork, CompilerAttemptDiagnostic, ContextPublication]
