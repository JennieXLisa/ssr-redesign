"""Pure compiler census, publication and reconciliation decision reference.

No compiler/process/filesystem/database access. Caller-supplied catalogs stand for
visible selected-extraction rows and captured bytes; W09 must prove those inputs.
Clock values are integer test ticks standing for database timestamps.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

from compiler_records import (CompilerAttemptDiagnostic, ContextCensus, ContextDefinition, EffectiveContext,
    ContextOutput, ContextPublication, ContextSpec, ContextWork, OccurrenceAnchor,
    ReferenceAnchor, ReferenceCensus, SourceEvidence, compiler_input_digest,
    compiler_record_id, compiler_semantics)
from records import canonical_bytes, semantic_digest
from reference_lifecycle import can_claim, lease_valid


def effective_context(sanitized, profile) -> EffectiveContext:
    """Recover the sanitizer's exact logical payload; never replace macro substrings."""
    from reference_compiler import PATH_OPTIONS, PROFILE_VERSION
    flags = list(sanitized.flags)
    for i in range(1, len(flags)):
        if sanitized.flags[i - 1] not in PATH_OPTIONS:
            continue
        value = sanitized.flags[i]
        roots = (profile.snapshot, *profile.resources)
        matches = [root for root in roots if value == root.staged or value.startswith(root.staged + '/')]
        if len(matches) != 1:
            raise ValueError('sanitized include lacks one installed root identity')
        root = matches[0]
        flags[i] = root.name + ':/' + value[len(root.staged):].lstrip('/')
    payload = EffectiveContext(version=PROFILE_VERSION, snapshot=profile.snapshot_id,
        toolchain=profile.toolchain_id, source=sanitized.source_identity, flags=tuple(flags),
        assumptions=tuple(sorted(p for p in sanitized.provenance if p in
            ('LANGUAGE_FROM_SUFFIX', 'DEFAULT_STANDARD', 'DEFAULT_TARGET'))))
    if semantic_digest(payload.model_dump(mode='json')) != sanitized.fingerprint:
        raise ValueError('sanitizer fingerprint reconstruction mismatch')
    return payload


def context_specs(entries: tuple[object, ...], profile, file_ids: Mapping[str, str],
                  *, origin: str = 'compilation_database') -> tuple[ContextSpec, ...]:
    """Every captured array entry is retained, including invalid/non-object entries.

    file_ids uses decoded snapshot-relative POSIX paths from the canonical path
    owner. JSON framing/duplicate-key errors invalidate the selected database as a
    whole before this function; there is no empty-census fallback on parse error.
    """
    from reference_compiler import InvalidContext, sanitize
    specs = []
    for ordinal, entry in enumerate(entries):
        digest = semantic_digest(entry)
        try:
            sanitized = sanitize(entry, profile)
        except InvalidContext as exc:
            specs.append(ContextSpec(ordinal=ordinal, origin=origin, entry_digest=digest,
                translation_unit_file_id=None, effective_digest=None, effective=None,
                rejection_code=exc.code))
            continue
        effective = effective_context(sanitized, profile)
        prefix = profile.snapshot.name + ':/'
        if not effective.source.startswith(prefix) or effective.source[len(prefix):] not in file_ids:
            raise ValueError('sanitized TU lacks a captured file identity')
        specs.append(ContextSpec(ordinal=ordinal, origin=origin, entry_digest=digest,
            translation_unit_file_id=file_ids[effective.source[len(prefix):]],
            effective_digest=sanitized.fingerprint, effective=effective, rejection_code=None))
    return tuple(specs)


def conservative_context_specs(options: tuple, profile,
                               file_ids: Mapping[str, str]) -> tuple[ContextSpec, ...]:
    """CompilerOptions order/TU order/include order -> explicit sanitizer inputs.

    Paths have already passed the canonical snapshot-path owner and are decoded
    inventory keys. This helper never enumerates directories or parses source.
    """
    entries, recipes = [], []
    for option in options:
        language = 'c++' if option.language == 'cpp' else 'c'
        for path in option.translation_units:
            source = profile.snapshot.original + '/' + path
            arguments = ['clang++' if language == 'c++' else 'clang', '-x', language,
                         '-std=' + option.standard, '--target=' + profile.default_target]
            for root in option.include_roots:
                arguments.extend(('-I', profile.snapshot.original + ('/' + root if root else '')))
            entries.append(dict(directory=profile.snapshot.original, file=source,
                                arguments=[*arguments, source]))
            recipes.append(dict(language=option.language, standard=option.standard,
                                include_roots=list(option.include_roots), translation_unit=path))
    specs = context_specs(tuple(entries), profile, file_ids, origin='conservative')
    return tuple(ContextSpec.model_validate({**spec.model_dump(), 'entry_digest': semantic_digest(recipe)})
                 for spec, recipe in zip(specs, recipes, strict=True))


def freeze_inputs(snapshot_id: str, extraction_id: str, resolution_id: str,
                  profile_digest: str, specs: tuple[ContextSpec, ...]) -> ContextCensus:
    return ContextCensus(snapshot_id=snapshot_id, extraction_id=extraction_id,
        resolution_id=resolution_id, profile_digest=profile_digest,
        input_digest=compiler_input_digest(profile_digest, specs),
        contexts=tuple(ContextDefinition(context_id=compiler_record_id(resolution_id, 'context', s.model_dump(mode='json')),
                                         spec=s) for s in specs))


def freeze_references(census: ContextCensus, anchors: tuple[ReferenceAnchor, ...]) -> ReferenceCensus:
    ordered = tuple(sorted(anchors, key=lambda r: r.reference_id))
    digest = semantic_digest([r.model_dump(mode='json', exclude={'extraction_publication_id'}) for r in ordered])
    return ReferenceCensus(resolution_id=census.resolution_id, extraction_id=census.extraction_id,
                           references=ordered, reference_digest=digest)


def context_work(census: ContextCensus) -> tuple[ContextWork, ...]:
    return tuple(ContextWork(context_id=c.context_id, resolution_id=census.resolution_id,
                             work_id=compiler_record_id(c.context_id, 'work', {})) for c in census.contexts)


def _replace(model, **changes):
    # model_copy(update=...) skips Pydantic validation; every transition revalidates.
    return type(model).model_validate({**model.model_dump(), **changes})


def _identities(census: ContextCensus, output: ContextOutput) -> ContextDefinition:
    for field in ('snapshot_id', 'extraction_id', 'resolution_id', 'input_digest'):
        if getattr(census, field) != getattr(output, field):
            raise ValueError(f'compiler output {field} mismatch')
    contexts = {c.context_id: c for c in census.contexts}
    if output.context_id not in contexts:
        raise ValueError('unexpected compiler context')
    context = contexts[output.context_id]
    if context.spec.rejection_code is not None:
        if output.status != 'INVALID' or not any(d.code == 'INVALID_CONTEXT' and
                d.detail_code == context.spec.rejection_code for d in output.diagnostics):
            raise ValueError('rejected input requires its recorded diagnostic-only outcome')
    return context


def validate_output(census: ContextCensus, inventory: ReferenceCensus, output: ContextOutput,
                    occurrences: Mapping[str, OccurrenceAnchor], files: Mapping[str, bytes],
                    resources: Mapping[tuple[str, str], bytes]) -> None:
    """Publication owner checks over explicit immutable catalogs, not SQL evidence."""
    context = _identities(census, output)
    if (inventory.resolution_id, inventory.extraction_id) != (census.resolution_id, census.extraction_id):
        raise ValueError('wrong selected extraction reference census')
    references = {r.reference_id: r for r in inventory.references}

    def evidence(site: SourceEvidence):
        data = files.get(site.file_id)
        if data is None or site.range.end_byte > len(data):
            raise ValueError('compiler source outside captured file inventory')
        if hashlib.sha256(data[site.range.start_byte:site.range.end_byte]).hexdigest() != site.bytes_digest:
            raise ValueError('compiler source bytes mismatch')

    if output.status == 'VALID' and context.spec.translation_unit_file_id not in {f.file_id for f in output.files}:
        raise ValueError('complete TU file census must include the main file')
    for visit in output.files:
        if visit.file_id not in files or hashlib.sha256(files[visit.file_id]).hexdigest() != visit.bytes_digest:
            raise ValueError('compiler visited-file bytes mismatch')
        for skipped in visit.inactive_ranges:
            evidence(skipped)
    for entity in output.entities:
        if occurrences.get(entity.anchor.occurrence_id) != entity.anchor:
            raise ValueError('entity is not an exact visible selected-extraction occurrence')
        evidence(entity.anchor.source)
    for observation in output.observations:
        anchor = references.get(observation.reference_id)
        if anchor is None or anchor.source != observation.source:
            raise ValueError('observation does not map the expected physical reference')
        evidence(observation.source)
        if observation.external is not None:
            ext = observation.external
            data = resources.get((ext.resource_digest, ext.path))
            if data is None or ext.range.end_byte > len(data) or hashlib.sha256(
                    data[ext.range.start_byte:ext.range.end_byte]).hexdigest() != ext.bytes_digest:
                raise ValueError('external identity lacks exact pinned resource evidence')
    for diagnostic in output.diagnostics:
        if diagnostic.source is not None:
            evidence(diagnostic.source)


def output_rows(output: ContextOutput, publication_id: str) -> list[dict]:
    """Lossless typed SQL detail projections, including publication-bound diagnostics."""
    rows = [dict(publication_id=publication_id, collection='summary', record_id=output.context_id,
                 value=output.model_dump(mode='json', exclude={'files', 'entities', 'observations', 'diagnostics'}))]
    for collection, key in (('files', 'file_id'), ('entities', 'entity_id'),
                            ('observations', 'observation_id'), ('diagnostics', None)):
        for record in getattr(output, collection):
            value = record.model_dump(mode='json')
            record_id = getattr(record, key) if key else semantic_digest(value)
            rows.append(dict(publication_id=publication_id, collection=collection,
                             record_id=record_id, value=value))
    return rows


def reconstruct_output(rows: list[dict], publication_id: str) -> ContextOutput:
    """Only the already selected active publication; historical work errors excluded."""
    selected = [r for r in rows if r['publication_id'] == publication_id]
    headers = [r for r in selected if r['collection'] == 'summary']
    if len(headers) != 1:
        raise ValueError('compiler publication needs exactly one summary')
    value = dict(headers[0]['value'])
    known = {'summary', 'files', 'entities', 'observations', 'diagnostics'}
    if any(r['collection'] not in known for r in selected):
        raise ValueError('unknown compiler output collection')
    if len({(r['collection'], r['record_id']) for r in selected}) != len(selected):
        raise ValueError('duplicate compiler output row')
    for collection in known - {'summary'}:
        value[collection] = [r['value'] for r in sorted(selected, key=lambda r: r['record_id']) if r['collection'] == collection]
    output = ContextOutput.model_validate_json(canonical_bytes(value))
    expected = {(r['collection'], r['record_id']): r['value'] for r in output_rows(output, publication_id)}
    if expected != {(r['collection'], r['record_id']): r['value'] for r in selected}:
        raise ValueError('compiler SQL keys disagree with typed detail')
    return output


def output_manifest(output: ContextOutput) -> dict:
    rows = output_rows(output, 'audit-only')
    records = [dict(collection=r['collection'], record_id=r['record_id'],
                    value=compiler_semantics(r['value'])) for r in rows]
    return dict(schema_version=1, records=sorted(records, key=lambda r: (r['collection'], r['record_id'])))


def output_signature(output: ContextOutput) -> tuple[int, str]:
    manifest = output_manifest(output)
    return len(manifest['records']), semantic_digest(manifest)


def claim(work: ContextWork, *, parent_state: str, launching_intent: str, demand: bool,
          census_frozen: bool, reference_census_frozen: bool, extraction_complete: bool, resources_available: bool,
          now: int, token: str, lease_seconds: int, max_attempts: int) -> ContextWork:
    if lease_seconds <= 0 or max_attempts <= 0:
        raise ValueError('invalid operational retry/lease settings')
    allowed = can_claim(state=parent_state, launching_intent=launching_intent, work_state=work.state,
        demand=demand, prerequisites=extraction_complete and reference_census_frozen,
        due=work.next_attempt_at is None or work.next_attempt_at <= now,
        resources=resources_available, plan_frozen=census_frozen, component='resolve')
    if not allowed or work.retry_cycle_attempt_count >= max_attempts:
        raise ValueError('CONTEXT_NOT_ELIGIBLE')
    return _replace(work, state='RUNNING', generation=work.generation + 1,
        attempt_count=work.attempt_count + 1, retry_cycle_attempt_count=work.retry_cycle_attempt_count + 1,
        lease_token=token, lease_expires_at=now + lease_seconds, next_attempt_at=None)


def _lease(work: ContextWork, parent_state: str, token: str, generation: int, now: int) -> bool:
    return lease_valid(state=parent_state, work_state=work.state, token=token,
        current_token=work.lease_token, generation=generation, current_generation=work.generation,
        now=now, expires=work.lease_expires_at or 0)


def heartbeat(work: ContextWork, *, parent_state: str, token: str,
              generation: int, now: int, lease_seconds: int) -> ContextWork:
    if lease_seconds <= 0 or not _lease(work, parent_state, token, generation, now):
        raise ValueError('STALE_CONTEXT_LEASE')
    return _replace(work, lease_expires_at=now + lease_seconds)


def _failed_transition(work: ContextWork, *, now: int, transient: bool,
                       max_attempts: int, delay: int, diagnostic: CompilerAttemptDiagnostic) -> ContextWork:
    if work.state != 'RUNNING' or max_attempts <= 0 or delay < 0:
        raise ValueError('no running context attempt or invalid retry settings')
    if (diagnostic.work_id, diagnostic.generation) != (work.work_id, work.generation):
        raise ValueError('attempt diagnostic belongs to another context/generation')
    again = transient and work.retry_cycle_attempt_count < max_attempts
    return _replace(work, state='PENDING' if again else 'FAILED', lease_token=None,
                    lease_expires_at=None, next_attempt_at=now + delay if again else None,
                    last_diagnostic_id=diagnostic.diagnostic_id)


def fail_attempt(work: ContextWork, *, parent_state: str, token: str, generation: int,
                 now: int, transient: bool, max_attempts: int, delay: int,
                 diagnostic: CompilerAttemptDiagnostic) -> ContextWork:
    if not _lease(work, parent_state, token, generation, now):
        raise ValueError('STALE_CONTEXT_LEASE')
    return _failed_transition(work, now=now, transient=transient, max_attempts=max_attempts, delay=delay, diagnostic=diagnostic)


def recover_expired(work: ContextWork, *, parent_state: str, now: int,
                    max_attempts: int, delay: int, diagnostic: CompilerAttemptDiagnostic) -> ContextWork:
    if parent_state == 'SUCCEEDED' or work.state != 'RUNNING' or work.lease_expires_at > now:
        raise ValueError('context lease is not reclaimable')
    if diagnostic.code != 'LEASE_EXPIRED':
        raise ValueError('lease recovery requires an expiry diagnostic')
    return _failed_transition(work, now=now, transient=True, max_attempts=max_attempts, delay=delay, diagnostic=diagnostic)


def retry_failed(work: ContextWork, *, parent_state: str) -> ContextWork:
    if parent_state == 'SUCCEEDED' or work.state != 'FAILED':
        raise ValueError('explicit retry only resets failed contexts')
    return _replace(work, state='PENDING', retry_cycle_attempt_count=0, next_attempt_at=None, last_diagnostic_id=None)


def visible_output(work: ContextWork, publications: Mapping[str, ContextPublication]) -> ContextOutput | None:
    if work.state != 'SUCCEEDED':
        return None
    publication = publications.get(work.active_publication_id)
    if publication is None or publication.publication_id != work.active_publication_id or not publication.committed or publication.work_id != work.work_id or publication.generation != work.generation:
        raise ValueError('active compiler publication ownership mismatch')
    output = publication.output
    if output.context_id != work.context_id or output.resolution_id != work.resolution_id:
        raise ValueError('active compiler publication context mismatch')
    if output_signature(output) != (publication.result_count, publication.result_digest):
        raise ValueError('active compiler publication manifest mismatch')
    return output


def publish(work: ContextWork, output: ContextOutput, *, census: ContextCensus,
            inventory: ReferenceCensus, occurrences: Mapping[str, OccurrenceAnchor],
            files: Mapping[str, bytes], resources: Mapping[tuple[str, str], bytes],
            publication_id: str, token: str, generation: int, now: int, parent_state: str,
            publications: Mapping[str, ContextPublication]) -> tuple[ContextWork, ContextPublication]:
    validate_output(census, inventory, output, occurrences, files, resources)
    if (work.context_id, work.resolution_id) != (output.context_id, output.resolution_id):
        raise ValueError('wrong context work owner')
    count, digest = output_signature(output)
    if work.state == 'SUCCEEDED':
        visible_output(work, publications)
        old = publications[work.active_publication_id]
        if digest != old.result_digest:
            raise ValueError('NONDETERMINISTIC_OUTPUT')
        if (generation, publication_id) != (old.generation, old.publication_id):
            raise ValueError('STALE_CONTEXT_PUBLICATION')
        return work, old
    if not _lease(work, parent_state, token, generation, now):
        raise ValueError('STALE_CONTEXT_LEASE')
    if publication_id in publications:
        old = publications[publication_id]
        if old.work_id != work.work_id or old.generation != generation or old.committed or old.result_digest != digest:
            raise ValueError('CONFLICTING_STAGED_PUBLICATION')
    publication = ContextPublication(publication_id=publication_id, work_id=work.work_id,
        generation=generation, committed=True, result_count=count, result_digest=digest, output=output)
    return _replace(work, state='SUCCEEDED', active_publication_id=publication_id,
                    lease_token=None, lease_expires_at=None, next_attempt_at=None), publication


def context_barrier(census: ContextCensus, inventory: ReferenceCensus | None,
                    work: tuple[ContextWork, ...], publications: Mapping[str, ContextPublication],
                    *, extraction_complete: bool) -> str:
    expected = {c.context_id for c in census.contexts}
    if len({w.context_id for w in work}) != len(work) or any(w.context_id not in expected or
            w.resolution_id != census.resolution_id for w in work):
        raise ValueError('CONTEXT_CENSUS_MISMATCH')
    if inventory is not None and (inventory.resolution_id, inventory.extraction_id) != (census.resolution_id, census.extraction_id):
        raise ValueError('wrong compiler reference inventory')
    if {w.context_id for w in work} != expected or any(w.state == 'FAILED' for w in work):
        return 'FAILED'
    if not extraction_complete or inventory is None or any(w.state != 'SUCCEEDED' for w in work):
        return 'PENDING'
    for item in work:
        _identities(census, visible_output(item, publications))
    return 'READY'


@dataclass(frozen=True)
class ReferenceContextState:
    context_id: str
    state: str
    target_symbol_id: str | None = None
    external_identity: tuple[str, str] | None = None
    target_usr: str | None = None


@dataclass(frozen=True)
class Reconciliation:
    phase: str
    outcome: str | None
    basis: str | None
    targets: tuple[str, ...]
    contexts: tuple[ReferenceContextState, ...]


def _reference_state(context_id: str, anchor: ReferenceAnchor, work: ContextWork | None,
                     publications: Mapping[str, ContextPublication]) -> ReferenceContextState:
    def state(name, target=None, external=None, usr=None):
        return ReferenceContextState(context_id, name, target, external, usr)
    if work is None:
        return state('MISSING_WORK')
    if work.state != 'SUCCEEDED':
        return state('FAILED' if work.state == 'FAILED' else 'PENDING')
    output = visible_output(work, publications)
    if output.status == 'INVALID':
        return state('INVALID')
    visit = next((f for f in output.files if f.file_id == anchor.source.file_id), None)
    if visit is None:
        return state('NOT_IN_TU')
    span = anchor.source.range
    if any(r.range.start_byte <= span.start_byte < span.end_byte <= r.range.end_byte for r in visit.inactive_ranges):
        return state('INACTIVE')
    observed = next((o for o in output.observations if o.reference_id == anchor.reference_id), None)
    if observed is None:
        return state('MISSING')
    if observed.dispatch == 'UNSUPPORTED':
        return state('UNSUPPORTED')
    if observed.external is not None:
        return state('EXTERNAL', external=(observed.external.resource_digest, observed.external.usr))
    entity = next(e for e in output.entities if e.entity_id == observed.target_entity_id)
    return state('MAPPED', target=entity.anchor.symbol_id, usr=entity.usr)


def same_entity_representatives(outputs: tuple[ContextOutput, ...]) -> dict[str, str]:
    """Only validated VALID cursor identities, never names or uncommitted evidence."""
    groups: dict[str, set[str]] = {}
    parent: dict[str, str] = {}
    observed_usrs: dict[str, set[str]] = {}
    for output in outputs:
        if output.status == 'VALID':
            for entity in output.entities:
                symbol = entity.anchor.symbol_id
                parent.setdefault(symbol, symbol)
                observed_usrs.setdefault(symbol, set()).add(entity.usr)
    for symbol, usrs in observed_usrs.items():
        # A physical declaration can denote different semantic entities under
        # different macro contexts. It cannot bridge otherwise distinct USRs.
        if len(usrs) == 1:
            groups.setdefault(next(iter(usrs)), set()).add(symbol)

    def root(symbol):
        while parent[symbol] != symbol:
            symbol = parent[symbol]
        return symbol

    for symbols in groups.values():
        roots = sorted({root(s) for s in symbols})
        for symbol in roots[1:]:
            parent[symbol] = roots[0]
    return {s: root(s) for s in parent}


def reconcile_reference(census: ContextCensus, inventory: ReferenceCensus,
                        reference_id: str, work: tuple[ContextWork, ...],
                        publications: Mapping[str, ContextPublication], *, extraction_complete: bool) -> Reconciliation:
    anchors = {r.reference_id: r for r in inventory.references}
    if reference_id not in anchors:
        raise ValueError('unknown expected physical reference')
    barrier = context_barrier(census, inventory, work, publications, extraction_complete=extraction_complete)
    by_context = {w.context_id: w for w in work}
    states = tuple(_reference_state(c.context_id, anchors[reference_id], by_context.get(c.context_id), publications)
                   for c in census.contexts)
    if barrier != 'READY':
        return Reconciliation(barrier, None, None, (), states)
    outputs = tuple(visible_output(w, publications) for w in work)
    representatives = same_entity_representatives(outputs)
    symbol_usrs: dict[str, set[str]] = {}
    for value in outputs:
        for entity in value.entities:
            symbol_usrs.setdefault(entity.anchor.symbol_id, set()).add(entity.usr)
    identity_conflict = any(len(symbol_usrs.get(s.target_symbol_id, ())) > 1 for s in states if s.state == 'MAPPED')
    targets = tuple(sorted({representatives.get(s.target_symbol_id, s.target_symbol_id)
                            for s in states if s.state == 'MAPPED'}))
    active = [s for s in states if s.state not in ('NOT_IN_TU', 'INACTIVE')]
    if len(targets) >= 2:
        return Reconciliation('FINAL', 'AMBIGUOUS', 'CONTEXT_DISAGREEMENT', targets, states)
    if len(targets) == 1 and active and not identity_conflict and all(s.state == 'MAPPED' for s in active):
        return Reconciliation('FINAL', 'RESOLVED', 'CLANG_REFERENCE', targets, states)
    if active and all(s.state == 'EXTERNAL' for s in active) and len({s.external_identity for s in active}) == 1:
        basis = 'EXTERNAL_SOURCE_NOT_CAPTURED'
    elif not states or any(s.state == 'INVALID' for s in active):
        basis = 'MISSING_BUILD_CONTEXT'
    elif identity_conflict or any(s.state == 'EXTERNAL' for s in active):
        basis = 'CONTEXT_DISAGREEMENT'
    else:
        basis = 'UNSUPPORTED_BINDING'
    return Reconciliation('FINAL', 'UNRESOLVED', basis, (), states)


def resolution_can_complete(census: ContextCensus, inventory: ReferenceCensus | None,
                            work: tuple[ContextWork, ...], publications: Mapping[str, ContextPublication],
                            *, extraction_complete: bool, file_plan_audited: bool,
                            file_states: tuple[str, ...]) -> bool:
    return (file_plan_audited and all(s == 'SUCCEEDED' for s in file_states)
            and context_barrier(census, inventory, work, publications, extraction_complete=extraction_complete) == 'READY')
