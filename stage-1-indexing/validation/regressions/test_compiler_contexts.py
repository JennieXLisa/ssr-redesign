"""Pure context ownership/reconciliation evidence; no libclang or PostgreSQL."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import itertools
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'contracts/v1'), str(ROOT / 'validation')]

from compiler_records import (CompilerAttemptDiagnostic, CompilerDiagnostic, CompilerEntity, CompilerFileVisit,
    CompilerObservation, ContextOutput, ContextPublication, ContextSpec, ExternalEntity,
    OccurrenceAnchor, ReferenceAnchor, SourceEvidence, compiler_record_id)
from models import ByteRange
from records import semantic_digest
from reference_compiler import CompilerProfile, Root
from reference_contexts import (claim, conservative_context_specs, context_barrier,
    context_specs, context_work, fail_attempt, freeze_inputs, freeze_references,
    heartbeat, output_manifest, output_rows, output_signature, publish,
    reconcile_reference, reconstruct_output, recover_expired, resolution_can_complete,
    retry_failed, validate_output, visible_output)
from settings import CompilerOptions


def uid(number):
    return str(UUID(int=number))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def changed(model, **changes):
    return type(model).model_validate({**model.model_dump(), **changes})


FILES = {uid(10): b'void f(); void g();\nvoid h(){ f(); }\n',
         uid(11): b'#include "api.h"\nint main(){ h(); }\n',
         uid(12): b'#include "api.h"\nvoid f(){}\nvoid g(){}\n'}
FILE_IDS = {'api.h': uid(10), 'main.cpp': uid(11), 'impl.cpp': uid(12)}
EXTERNAL_DATA = b'void external();'
RESOURCE_DIGEST = digest(b'pinned resource tree')
RESOURCES = {(RESOURCE_DIGEST, 'api.h'): EXTERNAL_DATA}


def site(file_id, needle, *, last=False):
    data = FILES[file_id]
    start = data.rindex(needle) if last else data.index(needle)
    return SourceEvidence(file_id=file_id, range=ByteRange(start_byte=start, end_byte=start + len(needle)),
                          bytes_digest=digest(needle))


ANCHOR = ReferenceAnchor(reference_id=uid(30), extraction_publication_id=uid(100), usage='CALL',
                         source=site(uid(10), b'f()', last=True))
OCCURRENCES = {
    uid(20): OccurrenceAnchor(occurrence_id=uid(20), symbol_id=uid(40), extraction_publication_id=uid(100),
                             role='declaration', source=site(uid(10), b'void f();')),
    uid(21): OccurrenceAnchor(occurrence_id=uid(21), symbol_id=uid(41), extraction_publication_id=uid(101),
                             role='definition', source=site(uid(12), b'void f(){}')),
    uid(22): OccurrenceAnchor(occurrence_id=uid(22), symbol_id=uid(42), extraction_publication_id=uid(100),
                             role='declaration', source=site(uid(10), b'void g();')),
}


def tool_profile(staged='/stage/source'):
    root = Root('snapshot', '/source', staged, frozenset(FILE_IDS))
    return CompilerProfile(root, (), uid(1), 'pinned-clang-test', 'x86_64-unknown-linux-gnu',
                           frozenset({'x86_64-unknown-linux-gnu'}))


def entry(index=0, extra=()):
    path = 'main.cpp' if index % 2 == 0 else 'impl.cpp'
    return dict(directory='/source', file=path, arguments=['clang++', '-I.', *extra, path])


def fixture(count=2, *, rejected=()):
    entries = tuple(entry(i, ('-c',) if i in rejected else ()) for i in range(count))
    specs = context_specs(entries, tool_profile(), FILE_IDS)
    census = freeze_inputs(uid(1), uid(2), uid(3), digest(b'compiler profile'), specs)
    inventory = freeze_references(census, (ANCHOR,))
    return census, inventory, context_work(census)


def output(census, index=0, *, target=20, usr='usr:f', observed=True, included=True,
           inactive=False, invalid=False, external=False, unsupported=False, diagnostic=None):
    context = census.contexts[index]
    header = dict(snapshot_id=census.snapshot_id, extraction_id=census.extraction_id,
                  resolution_id=census.resolution_id, context_id=context.context_id, input_digest=census.input_digest)
    if invalid or context.spec.rejection_code:
        rejected = context.spec.rejection_code
        diag = CompilerDiagnostic(code='INVALID_CONTEXT' if rejected else 'COMPILER_ERROR', severity='error',
            source=None, detail_code=rejected or 'MISSING_HEADER', message='Context cannot establish binding')
        return ContextOutput(**header, status='INVALID', file_census_complete=False, diagnostics=(diag,))
    file_ids = {context.spec.translation_unit_file_id}
    entities, observations = (), ()
    if included:
        file_ids.add(ANCHOR.source.file_id)
    if observed and included and not inactive:
        if external:
            ext = ExternalEntity(resource_digest=RESOURCE_DIGEST, path='api.h',
                range=ByteRange(start_byte=0, end_byte=len(EXTERNAL_DATA)), bytes_digest=digest(EXTERNAL_DATA),
                usr='external:api', name='external')
            entity_id = None
        else:
            anchor = OCCURRENCES[uid(target)]
            file_ids.add(anchor.source.file_id)
            values = dict(usr=usr, cursor_kind='FUNCTION_DECL', anchor=anchor.model_dump(mode='json'))
            entity_id = compiler_record_id(context.context_id, 'entity', values)
            entities = (CompilerEntity(entity_id=entity_id, usr=usr, cursor_kind='FUNCTION_DECL', anchor=anchor),)
            ext = None
        values = dict(reference_id=ANCHOR.reference_id, source=ANCHOR.source.model_dump(mode='json'),
            spelling=ANCHOR.source.model_dump(mode='json'), expansion=ANCHOR.source.model_dump(mode='json'),
            cursor_kind='CALL_EXPR', dispatch='UNSUPPORTED' if unsupported else 'DIRECT',
            target_entity_id=entity_id, external=ext.model_dump(mode='json') if ext else None)
        observations = (CompilerObservation.model_validate_json(__import__('json').dumps(dict(
            observation_id=compiler_record_id(context.context_id, 'observation', values), **values))),)
    visits = tuple(CompilerFileVisit(file_id=f, bytes_digest=digest(FILES[f]), visit_count=1,
                  inactive_ranges=(ANCHOR.source,) if inactive and f == ANCHOR.source.file_id else ())
                   for f in sorted(file_ids))
    return ContextOutput(**header, status='VALID', file_census_complete=True, files=visits,
                         entities=entities, observations=observations, diagnostics=(diagnostic,) if diagnostic else ())


def running(work, *, now=10, token=uid(80), parent_state='RUNNING'):
    return claim(work, parent_state=parent_state, launching_intent='RUN', demand=True,
                 census_frozen=True, reference_census_frozen=True, extraction_complete=True, resources_available=True,
                 now=now, token=token, lease_seconds=120, max_attempts=3)


def attempt_error(work, code='WORKER_CRASH'):
    return CompilerAttemptDiagnostic(diagnostic_id=uid(900 + work.generation), work_id=work.work_id,
                                     generation=work.generation, code=code, message='Attempt failed')


def committed(census, inventory, works, outputs):
    result, publications = list(works), {}
    for index, value in enumerate(outputs):
        if value is None:
            continue
        work = running(result[index])
        work, publication = publish(work, value, census=census, inventory=inventory,
            occurrences=OCCURRENCES, files=FILES, resources=RESOURCES,
            publication_id=uid(200 + index), token=uid(80), generation=work.generation,
            now=11, parent_state='RUNNING', publications=publications)
        result[index] = work
        publications[publication.publication_id] = publication
    return tuple(result), publications


class CompilerContextTests(unittest.TestCase):
    def test_sanitizer_payload_reconstructs_fingerprint_without_touching_macros(self):
        spec = context_specs((entry(extra=('-DTEXT=/stage/source/include',)),), tool_profile(), FILE_IDS)[0]
        self.assertIn('snapshot:/', spec.effective.flags)
        self.assertIn('-DTEXT=/stage/source/include', spec.effective.flags)
        self.assertEqual(spec.effective_digest, semantic_digest(spec.effective.model_dump(mode='json')))

    def test_explicit_semantic_profile_census_preserves_tu_and_include_order(self):
        options = (CompilerOptions(language='cpp', standard='c++20', include_roots=('',),
                                   translation_units=('impl.cpp', 'main.cpp')),)
        specs = conservative_context_specs(options, tool_profile(), FILE_IDS)
        self.assertEqual([s.translation_unit_file_id for s in specs], [uid(12), uid(11)])
        self.assertTrue(all(s.origin == 'conservative' and s.rejection_code is None for s in specs))
        self.assertIn('-std=c++20', specs[0].effective.flags)
        original = tool_profile()
        relocated = replace(original, snapshot=replace(original.snapshot, original='/relocated/source', staged='/other/staging'))
        self.assertEqual(specs, conservative_context_specs(options, relocated, FILE_IDS))

    def test_census_retains_rejected_and_duplicate_commands(self):
        specs = context_specs((entry(), entry(), entry(extra=('-c',)), 'malformed'), tool_profile(), FILE_IDS)
        census = freeze_inputs(uid(1), uid(2), uid(3), digest(b'profile'), specs)
        self.assertEqual(len({c.context_id for c in census.contexts}), 4)
        self.assertEqual(specs[0].effective_digest, specs[1].effective_digest)
        self.assertEqual(specs[2].rejection_code, 'UNSUPPORTED_OPTION')
        self.assertEqual(specs[3].rejection_code, 'INVALID_ENTRY')
        self.assertIsNone(specs[2].effective)

    def test_context_ids_do_not_depend_on_staging_or_observations(self):
        entries = (entry(), entry(1))
        a = context_specs(entries, tool_profile('/stage/a'), FILE_IDS)
        b = context_specs(entries, tool_profile('/stage/b'), FILE_IDS)
        self.assertEqual(a, b)
        x = freeze_inputs(uid(1), uid(2), uid(3), digest(b'profile'), a)
        y = freeze_inputs(uid(1), uid(2), uid(3), digest(b'profile'), b)
        self.assertEqual(x, y)
        moved_resolution = freeze_inputs(uid(1), uid(2), uid(99), digest(b'profile'), a)
        self.assertEqual(x.input_digest, moved_resolution.input_digest)
        self.assertNotEqual(x.contexts[0].context_id, moved_resolution.contexts[0].context_id)

    def test_changed_semantics_changes_input_digest(self):
        a = context_specs((entry(extra=('-DX=1',)),), tool_profile(), FILE_IDS)
        b = context_specs((entry(extra=('-DX=2',)),), tool_profile(), FILE_IDS)
        first = freeze_inputs(uid(1), uid(2), uid(3), digest(b'profile'), a)
        second = freeze_inputs(uid(1), uid(2), uid(3), digest(b'profile'), b)
        self.assertNotEqual(first.input_digest, second.input_digest)

    def test_invalid_descriptor_hashes_ordinals_and_partial_nulls_rejected(self):
        census, _, _ = fixture()
        spec = census.contexts[0].spec
        for change in ({'effective_digest': digest(b'wrong')}, {'effective': None},
                       {'translation_unit_file_id': None}, {'rejection_code': 'UNKNOWN_FLAG'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                changed(spec, **change)
        with self.assertRaises(ValueError):
            freeze_inputs(uid(1), uid(2), uid(3), census.profile_digest, (changed(spec, ordinal=1),))
        with self.assertRaises(ValueError):
            changed(census, input_digest=digest(b'wrong'))
        with self.assertRaises(ValueError):
            freeze_inputs(uid(99), uid(2), uid(3), census.profile_digest, (spec,))

    def test_profile_collections_and_context_work_ids_are_immutable(self):
        census, _, works = fixture()
        with self.assertRaises((ValueError, AttributeError)):
            census.contexts = ()
        with self.assertRaises(TypeError):
            census.contexts[0].spec.effective.flags[0] = '-c'
        with self.assertRaises(ValueError):
            changed(works[0], work_id=uid(99))

    def test_reference_census_is_exact_and_audit_ids_do_not_change_digest(self):
        census, inventory, _ = fixture()
        again = freeze_references(census, (changed(ANCHOR, extraction_publication_id=uid(999)),))
        self.assertEqual(inventory.reference_digest, again.reference_digest)
        with self.assertRaises(ValueError):
            freeze_references(census, (ANCHOR, ANCHOR))
        with self.assertRaises(ValueError):
            changed(inventory, reference_digest=digest(b'wrong'))

    def test_w09_to_w12_agreement_links_exact_definition_usr(self):
        census, inventory, works = fixture()
        works, pubs = committed(census, inventory, works, [output(census), output(census, 1, target=21)])
        result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
        self.assertEqual((result.phase, result.outcome, result.basis, result.targets),
                         ('FINAL', 'RESOLVED', 'CLANG_REFERENCE', (uid(40),)))
        definition = visible_output(works[1], pubs).entities[0]
        self.assertEqual(definition.anchor.role, 'definition')
        self.assertEqual(definition.anchor.source, site(uid(12), b'void f(){}'))

    def test_all_expected_contexts_barrier_and_completion_order(self):
        census, inventory, works = fixture()
        one, pubs = committed(census, inventory, works, [output(census), None])
        result = reconcile_reference(census, inventory, uid(30), one, pubs, extraction_complete=True)
        self.assertEqual((result.phase, result.outcome, result.targets), ('PENDING', None, ()))
        self.assertEqual([s.state for s in result.contexts], ['MAPPED', 'PENDING'])
        both, pubs = committed(census, inventory, works, [output(census), output(census, 1)])
        results = [reconcile_reference(census, inventory, uid(30), order, pubs, extraction_complete=True)
                   for order in itertools.permutations(both)]
        self.assertEqual(results[0], results[1])

    def test_missing_expected_work_is_integrity_failure_not_agreement(self):
        census, inventory, works = fixture()
        result = reconcile_reference(census, inventory, uid(30), works[:1], {}, extraction_complete=True)
        self.assertEqual(result.phase, 'FAILED')
        self.assertEqual(result.contexts[1].state, 'MISSING_WORK')
        self.assertIsNone(result.outcome)

    def test_failed_context_blocks_finalization_and_other_pending_context_can_run(self):
        census, inventory, works = fixture()
        active = running(works[0])
        failed = fail_attempt(active, parent_state='RUNNING', token=uid(80), generation=1,
                              now=11, transient=False, max_attempts=3, delay=1, diagnostic=attempt_error(active))
        second = running(works[1], parent_state='FAILED')
        result = reconcile_reference(census, inventory, uid(30), (failed, second), {}, extraction_complete=True)
        self.assertEqual(result.phase, 'FAILED')
        self.assertEqual([s.state for s in result.contexts], ['FAILED', 'PENDING'])

    def test_invalid_context_completes_with_limitation_without_fake_observations(self):
        census, inventory, works = fixture(rejected=(1,))
        invalid = output(census, 1)
        self.assertEqual((invalid.files, invalid.entities, invalid.observations), ((), (), ()))
        works, pubs = committed(census, inventory, works, [output(census), invalid])
        self.assertEqual(context_barrier(census, inventory, works, pubs, extraction_complete=True), 'READY')
        result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
        self.assertEqual((result.outcome, result.basis, result.targets), ('UNRESOLVED', 'MISSING_BUILD_CONTEXT', ()))
        self.assertEqual(result.contexts[1].state, 'INVALID')

    def test_parse_error_invalidates_entire_context(self):
        census, inventory, works = fixture(1)
        invalid = output(census, invalid=True)
        with self.assertRaises(ValueError):
            changed(invalid, observations=output(census).observations)
        with self.assertRaises(ValueError):
            changed(invalid, diagnostics=())
        works, pubs = committed(census, inventory, works, [invalid])
        self.assertEqual(reconcile_reference(census, inventory, uid(30), works, pubs,
                         extraction_complete=True).contexts[0].state, 'INVALID')

    def test_missing_cursor_is_not_preprocessor_inactivity(self):
        census, inventory, works = fixture()
        diagnostic = CompilerDiagnostic(code='UNMAPPED_CURSOR', severity='limitation', source=None,
                                         detail_code='NO_PHYSICAL_MAPPING', message='No unique source reference')
        missing = output(census, 1, observed=False, diagnostic=diagnostic)
        self.assertEqual(missing.observations, ())
        works, pubs = committed(census, inventory, works, [output(census), missing])
        result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
        self.assertEqual(result.contexts[1].state, 'MISSING')
        self.assertEqual((result.outcome, result.targets), ('UNRESOLVED', ()))

    def test_positive_inactive_and_not_in_tu_evidence_are_not_agreement_votes(self):
        for options, expected in [({'inactive': True}, 'INACTIVE'), ({'included': False}, 'NOT_IN_TU')]:
            with self.subTest(options=options):
                census, inventory, works = fixture()
                works, pubs = committed(census, inventory, works, [output(census), output(census, 1, **options)])
                result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
                self.assertEqual(result.contexts[1].state, expected)
                self.assertEqual(result.outcome, 'RESOLVED')
        census, inventory, works = fixture(1)
        works, pubs = committed(census, inventory, works, [output(census, inactive=True)])
        self.assertEqual(reconcile_reference(census, inventory, uid(30), works, pubs,
                         extraction_complete=True).outcome, 'UNRESOLVED')

    def test_repeated_header_visits_cannot_prove_universal_inactivity(self):
        with self.assertRaises(ValueError):
            CompilerFileVisit(file_id=uid(10), bytes_digest=digest(FILES[uid(10)]), visit_count=2,
                               inactive_ranges=(ANCHOR.source,))

    def test_inactive_and_observed_overlap_is_rejected(self):
        census, _, _ = fixture(1)
        value = output(census)
        visits = tuple(changed(f, inactive_ranges=(ANCHOR.source,)) if f.file_id == uid(10) else f for f in value.files)
        with self.assertRaises(ValueError):
            changed(value, files=visits)

    def test_cross_context_disagreement_remains_ambiguous_with_invalid_context(self):
        census, inventory, works = fixture(3, rejected=(2,))
        works, pubs = committed(census, inventory, works,
            [output(census), output(census, 1, target=22, usr='usr:g'), output(census, 2)])
        result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
        self.assertEqual((result.outcome, result.basis, result.targets),
                         ('AMBIGUOUS', 'CONTEXT_DISAGREEMENT', (uid(40), uid(42))))

    def test_same_physical_target_with_conflicting_usrs_is_not_agreement(self):
        census, inventory, works = fixture()
        works, pubs = committed(census, inventory, works, [output(census, usr='usr:one'), output(census, 1, usr='usr:two')])
        result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
        self.assertEqual((result.outcome, result.basis, result.targets), ('UNRESOLVED', 'CONTEXT_DISAGREEMENT', ()))

    def test_context_dependent_symbol_cannot_bridge_distinct_usr_groups(self):
        census, inventory, works = fixture()
        first = output(census, target=21, usr='usr:one')
        second = output(census, 1, target=22, usr='usr:two')
        values = []
        for index, value in enumerate((first, second)):
            shared = output(census, index, usr='usr:one' if index == 0 else 'usr:two').entities[0]
            values.append(changed(value, entities=(*value.entities, shared)))
        works, pubs = committed(census, inventory, works, values)
        result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
        self.assertEqual((result.outcome, result.targets), ('AMBIGUOUS', (uid(41), uid(42))))

    def test_external_agreement_never_creates_a_captured_target(self):
        census, inventory, works = fixture()
        works, pubs = committed(census, inventory, works, [output(census, external=True), output(census, 1, external=True)])
        result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
        self.assertEqual((result.outcome, result.basis, result.targets), ('UNRESOLVED', 'EXTERNAL_SOURCE_NOT_CAPTURED', ()))

    def test_local_external_conflict_does_not_promote_single_candidate(self):
        census, inventory, works = fixture()
        works, pubs = committed(census, inventory, works, [output(census), output(census, 1, external=True)])
        result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
        self.assertEqual((result.outcome, result.targets), ('UNRESOLVED', ()))

    def test_unsupported_dispatch_is_not_a_proven_binding(self):
        census, inventory, works = fixture(1)
        works, pubs = committed(census, inventory, works, [output(census, unsupported=True)])
        result = reconcile_reference(census, inventory, uid(30), works, pubs, extraction_complete=True)
        self.assertEqual((result.outcome, result.contexts[0].state, result.targets), ('UNRESOLVED', 'UNSUPPORTED', ()))

    def test_empty_context_census_is_explicit_missing_build_context(self):
        census, inventory, works = fixture(0)
        result = reconcile_reference(census, inventory, uid(30), works, {}, extraction_complete=True)
        self.assertEqual((result.outcome, result.basis), ('UNRESOLVED', 'MISSING_BUILD_CONTEXT'))

    def test_wrong_snapshot_dataset_reference_or_source_hash_cannot_publish(self):
        census, inventory, _ = fixture(1)
        value = output(census)
        for field in ('snapshot_id', 'extraction_id', 'resolution_id', 'context_id'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_output(census, inventory, changed(value, **{field: uid(999)}), OCCURRENCES, FILES, RESOURCES)
        wrong = dict(FILES)
        wrong[uid(10)] = b'x' * len(FILES[uid(10)])
        with self.assertRaises(ValueError):
            validate_output(census, inventory, value, OCCURRENCES, wrong, RESOURCES)
        with self.assertRaises(ValueError):
            validate_output(census, changed(inventory, extraction_id=uid(999)), value, OCCURRENCES, FILES, RESOURCES)

    def test_target_occurrence_must_belong_to_active_selected_extraction(self):
        census, inventory, _ = fixture(1)
        wrong = dict(OCCURRENCES)
        wrong[uid(20)] = changed(wrong[uid(20)], extraction_publication_id=uid(999))
        with self.assertRaisesRegex(ValueError, 'selected-extraction'):
            validate_output(census, inventory, output(census), wrong, FILES, RESOURCES)

    def test_external_source_requires_pinned_resource_bytes(self):
        census, inventory, _ = fixture(1)
        with self.assertRaisesRegex(ValueError, 'pinned resource'):
            validate_output(census, inventory, output(census, external=True), OCCURRENCES, FILES, {})
        with self.assertRaises(ValueError):
            ExternalEntity(resource_digest=RESOURCE_DIGEST, path='../host/api.h', range=ByteRange(start_byte=0, end_byte=1),
                           bytes_digest=digest(b'x'), usr='api', name='api')

    def test_unmapped_or_duplicate_physical_cursors_cannot_fabricate_observations(self):
        census, _, _ = fixture(1)
        value = output(census)
        observed = value.observations[0]
        with self.assertRaises(ValueError):
            changed(value, observations=(observed, observed))
        with self.assertRaises(ValueError):
            changed(observed, spelling=site(uid(10), b'g()'))
        with self.assertRaises(ValueError):
            changed(observed, target_entity_id=None)
        with self.assertRaises(ValueError):
            changed(value, entities=())

    def test_complete_file_census_cannot_omit_main_tu(self):
        census, inventory, _ = fixture(1)
        value = output(census)
        omitted = changed(value, files=tuple(v for v in value.files if v.file_id != uid(11)))
        with self.assertRaisesRegex(ValueError, 'main file'):
            validate_output(census, inventory, omitted, OCCURRENCES, FILES, RESOURCES)

    def test_staging_is_invisible_and_active_publication_is_exact(self):
        census, inventory, works = fixture(1)
        value = output(census)
        count, checksum = output_signature(value)
        staged = ContextPublication(publication_id=uid(200), work_id=works[0].work_id, generation=1,
                                    committed=False, result_count=count, result_digest=checksum, output=value)
        self.assertIsNone(visible_output(running(works[0]), {uid(200): staged}))
        works, pubs = committed(census, inventory, works, [value])
        for change in ({'work_id': uid(999)}, {'generation': 2}, {'committed': False},
                       {'result_digest': digest(b'wrong')}, {'publication_id': uid(999)}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                visible_output(works[0], {uid(200): changed(pubs[uid(200)], **change)})

    def test_output_manifest_reconstructs_only_active_publication_diagnostics(self):
        census, _, _ = fixture(1)
        old = CompilerDiagnostic(code='UNMAPPED_CURSOR', severity='limitation', source=None,
                                 detail_code='UNMAPPED', message='abandoned diagnostic')
        new = changed(old, message='active diagnostic')
        active = output(census, diagnostic=new)
        rows = output_rows(output(census, diagnostic=old), uid(199)) + output_rows(active, uid(200))
        rebuilt = reconstruct_output(list(reversed(rows)), uid(200))
        self.assertEqual(rebuilt.diagnostics, (new,))
        self.assertEqual(output_manifest(rebuilt), output_manifest(active))
        self.assertEqual(output_signature(rebuilt)[0], 1 + len(active.files) + len(active.entities) + len(active.observations) + 1)

    def test_manifest_ignores_audit_ids_and_changes_when_diagnostics_change(self):
        census, _, _ = fixture(1)
        value = output(census)
        rows = output_rows(value, uid(200))
        for row in rows:
            if row['collection'] == 'entities':
                row['value']['anchor']['extraction_publication_id'] = uid(999)
        reconstructed = reconstruct_output(rows, uid(200))
        self.assertEqual(output_signature(reconstructed), output_signature(value))
        diagnostic = CompilerDiagnostic(code='COMPILER_WARNING', severity='warning', source=None,
                                         detail_code='WARNING', message='retained warning')
        self.assertNotEqual(output_signature(changed(value, diagnostics=(diagnostic,))), output_signature(value))

    def test_reconstruction_rejects_unknown_duplicate_and_forged_keys(self):
        census, _, _ = fixture(1)
        rows = output_rows(output(census), uid(200))
        for mutation in ('duplicate', 'key', 'missing_summary', 'unknown_collection'):
            bad = deepcopy(rows)
            if mutation == 'duplicate':
                bad.append(deepcopy(bad[-1]))
            elif mutation == 'key':
                bad[-1]['record_id'] = uid(999)
            elif mutation == 'missing_summary':
                bad = bad[1:]
            else:
                bad[-1]['collection'] = 'unexpected'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                reconstruct_output(bad, uid(200))

    def test_commit_replay_and_changed_result(self):
        census, inventory, works = fixture(1)
        value = output(census)
        works, pubs = committed(census, inventory, works, [value])
        kwargs = dict(census=census, inventory=inventory, occurrences=OCCURRENCES, files=FILES, resources=RESOURCES,
                      publication_id=uid(200), token=uid(80), generation=1, now=1000,
                      parent_state='SUCCEEDED', publications=pubs)
        self.assertEqual(publish(works[0], value, **kwargs), (works[0], pubs[uid(200)]))
        with self.assertRaisesRegex(ValueError, 'STALE_CONTEXT_PUBLICATION'):
            publish(works[0], value, **{**kwargs, 'generation': 2})
        with self.assertRaisesRegex(ValueError, 'NONDETERMINISTIC_OUTPUT'):
            publish(works[0], output(census, observed=False), **kwargs)

    def test_pause_allows_owned_heartbeat_and_publish_but_no_claim(self):
        census, inventory, works = fixture(1)
        run = running(works[0])
        beat = heartbeat(run, parent_state='PAUSED', token=uid(80), generation=1, now=50, lease_seconds=120)
        self.assertEqual(beat.lease_expires_at, 170)
        finished, _ = publish(beat, output(census), census=census, inventory=inventory, occurrences=OCCURRENCES,
            files=FILES, resources=RESOURCES, publication_id=uid(200), token=uid(80), generation=1, now=60,
            parent_state='PAUSED', publications={})
        self.assertEqual(finished.state, 'SUCCEEDED')
        with self.assertRaises(ValueError):
            claim(works[0], parent_state='PAUSED', launching_intent='PAUSE', demand=True,
                  census_frozen=True, reference_census_frozen=True, extraction_complete=True, resources_available=True,
                  now=10, token=uid(80), lease_seconds=120, max_attempts=3)

    def test_expiry_and_successor_fence_old_heartbeat_failure_and_publication(self):
        census, inventory, works = fixture(1)
        old = running(works[0])
        for tick in (130, 131):
            with self.assertRaises(ValueError):
                heartbeat(old, parent_state='RUNNING', token=uid(80), generation=1, now=tick, lease_seconds=120)
        pending = recover_expired(old, parent_state='PAUSED', now=130, max_attempts=3, delay=1,
                                   diagnostic=attempt_error(old, 'LEASE_EXPIRED'))
        successor = running(pending, now=131, token=uid(81))
        self.assertEqual((successor.generation, successor.attempt_count), (2, 2))
        with self.assertRaises(ValueError):
            fail_attempt(successor, parent_state='RUNNING', token=uid(80), generation=1,
                         now=132, transient=False, max_attempts=3, delay=1, diagnostic=attempt_error(old))
        with self.assertRaises(ValueError):
            publish(successor, output(census), census=census, inventory=inventory, occurrences=OCCURRENCES,
                    files=FILES, resources=RESOURCES, publication_id=uid(200), token=uid(80), generation=1,
                    now=132, parent_state='RUNNING', publications={})

    def test_retry_exhaustion_preserves_history_and_explicit_retry_admits_failed_dataset(self):
        _, _, works = fixture(1)
        value, tick = works[0], 10
        for attempt in range(1, 4):
            value = running(value, now=tick)
            value = fail_attempt(value, parent_state='RUNNING', token=uid(80), generation=attempt,
                                  now=tick + 1, transient=True, max_attempts=3, delay=1, diagnostic=attempt_error(value))
            tick += 2
        self.assertEqual((value.state, value.attempt_count, value.retry_cycle_attempt_count), ('FAILED', 3, 3))
        retried = retry_failed(value, parent_state='FAILED')
        self.assertIsNotNone(value.last_diagnostic_id)
        self.assertIsNone(retried.last_diagnostic_id)
        self.assertEqual((retried.generation, retried.attempt_count, retried.retry_cycle_attempt_count), (3, 3, 0))
        active = running(retried, now=tick, parent_state='FAILED')
        self.assertEqual((active.generation, active.attempt_count, active.retry_cycle_attempt_count), (4, 4, 1))

    def test_all_admission_prerequisites_are_required(self):
        _, _, works = fixture(1)
        args = dict(parent_state='RUNNING', launching_intent='RUN', demand=True, census_frozen=True,
            reference_census_frozen=True, extraction_complete=True, resources_available=True,
            now=10, token=uid(80), lease_seconds=120, max_attempts=3)
        for field in ('demand', 'census_frozen', 'reference_census_frozen', 'extraction_complete', 'resources_available'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                claim(works[0], **{**args, field: False})
        with self.assertRaises(ValueError):
            claim(changed(works[0], next_attempt_at=11), **args)
        with self.assertRaises(ValueError):
            claim(works[0], **{**args, 'parent_state': 'SUCCEEDED'})

    def test_parent_completion_includes_context_and_reference_census_obligations(self):
        census, inventory, works = fixture(1)
        args = dict(extraction_complete=True, file_plan_audited=True, file_states=('SUCCEEDED',))
        self.assertFalse(resolution_can_complete(census, inventory, works, {}, **args))
        works, pubs = committed(census, inventory, works, [output(census, invalid=True)])
        self.assertTrue(resolution_can_complete(census, inventory, works, pubs, **args))
        self.assertFalse(resolution_can_complete(census, None, works, pubs, **args))
        self.assertFalse(resolution_can_complete(census, inventory, works, pubs, **{**args, 'file_states': ('PENDING',)}))
        self.assertFalse(resolution_can_complete(census, inventory, works, pubs, **{**args, 'file_plan_audited': False}))

    def test_pure_full_path_does_not_open_source_or_execute_a_process(self):
        with patch('builtins.open', side_effect=AssertionError('unexpected filesystem read')), \
             patch('subprocess.Popen', side_effect=AssertionError('unexpected subprocess')):
            census, inventory, works = fixture()
            works, pubs = committed(census, inventory, works, [output(census), output(census, 1)])
            self.assertEqual(reconcile_reference(census, inventory, uid(30), works, pubs,
                             extraction_complete=True).outcome, 'RESOLVED')

    def test_schema_has_separate_census_work_active_view_and_publication_diagnostics(self):
        # Structural contract check only; real SQL application/rollback/FK races
        # remain W02/W09 gates and are never claimed by this string inspection.
        sql = (ROOT / 'contracts/v1/schema.sql').read_text()
        for table in ('compiler_context_plans', 'compiler_contexts', 'compiler_reference_inventory',
                      'compiler_context_work', 'compiler_publications', 'compiler_context_results',
                      'compiler_file_visits', 'compiler_entities', 'compiler_observations',
                      'compiler_output_diagnostics', 'compiler_attempt_diagnostics'):
            self.assertIn('CREATE TABLE ' + table, sql)
        self.assertIn('CREATE VIEW visible_compiler_publications', sql)
        self.assertIn('FOREIGN KEY(work_id,active_publication_id)', sql)
        self.assertIn('UNIQUE(work_id,generation)', sql)
        self.assertIn("reference_state='UNFROZEN' AND reference_count IS NULL AND reference_digest IS NULL", sql)


if __name__ == '__main__':
    unittest.main()
