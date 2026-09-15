"""Fixture -> production profile mapping and semantic projections, without I/O.

This is a reference for config/planning owners, not an adapter or compiler runner.
Only main() reads the authored corpus. Source strings are never executed.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'contracts/v1'))
from models import Digest, Id, Model
from records import canonical_bytes, semantic_digest
from settings import SemanticProfile, snapshot_directory, snapshot_file

JS_LANGUAGES = {'javascript', 'jsx', 'typescript', 'tsx'}
LANGUAGES = JS_LANGUAGES | {'python', 'c', 'cpp', 'java', 'php', 'lua', 'bash', 'zsh'}
PROFILE_KEYS = {'mode', 'package_root', 'php_input', 'compiler', 'include_root',
                'translation_units', 'shell_mode', 'cwd_snapshot'}
SEMANTIC_FIELDS = {'schema_version', 'language_overrides', 'encoding_overrides',
                   'package_roots', 'module_aliases', 'compilation_database',
                   'file_options', 'compiler_options'}


def _join(root: str, path: str, *, directory: bool = False) -> str:
    if not isinstance(path, str):
        raise ValueError('fixture path must be a string')
    relative = '' if directory and path == '.' else path
    (snapshot_directory if directory else snapshot_file)(relative)
    return '/'.join(part for part in (root, relative) if part)


def default_file_options(path: str, language: str) -> dict:
    """Frozen extension defaults after authoritative language selection.

    Exact file_options precede generic language overrides; neither a suffix nor
    target package metadata changes an explicit mode. No source sniffing here.
    """
    snapshot_file(path)
    if language not in LANGUAGES:
        raise ValueError('unsupported selected language')
    value = {'path': path, 'language': language}
    if language in JS_LANGUAGES:
        suffix = Path(path).suffix
        mode = 'module' if suffix in ('.mjs', '.mts') else 'commonjs' if suffix in ('.cjs', '.cts') else 'script'
        value.update(mode=mode, strict=mode == 'module')
    elif language == 'php':
        value['input'] = 'mixed'
    elif language in {'bash', 'zsh'}:
        value['cwd_snapshot'] = None
    return value


def fixture_to_profile(case: dict, *, root: str = '') -> SemanticProfile:
    """Map every supported fixture key or reject it; original bytes stay intact.

    root is the canonical mount of this *individual* fixture in its snapshot.
    Compiler/relative-import semantics are not pooled across benchmark replicas.
    """
    snapshot_directory(root)
    fixture = case['profile']
    if not isinstance(fixture, dict) or set(fixture) - PROFILE_KEYS:
        raise ValueError('unknown fixture profile fields')
    sources = case['sources']
    if not sources:
        raise ValueError('fixture needs source inventory')
    languages = {s['language'] for s in sources}
    if len(languages) != 1 or not languages <= LANGUAGES:
        raise ValueError('fixture shorthand requires one supported dialect')
    language = next(iter(languages))
    allowed = ({'mode'} if language in JS_LANGUAGES else
               {'package_root'} if language == 'python' else
               {'php_input'} if language == 'php' else
               {'compiler', 'include_root', 'translation_units'} if language in {'c', 'cpp'} else
               {'shell_mode', 'cwd_snapshot'} if language in {'bash', 'zsh'} else set())
    if set(fixture) - allowed:
        raise ValueError('fixture field does not apply to selected dialect')
    for key, value in fixture.items():
        if key == 'translation_units':
            if not isinstance(value, list) or not value or any(not isinstance(p, str) for p in value):
                raise ValueError('translation_units must be a nonempty path array')
        elif not isinstance(value, str):
            raise ValueError('fixture option must be a string')
    if ('include_root' in fixture or 'translation_units' in fixture) and 'compiler' not in fixture:
        raise ValueError('compiler selection is required for compiler fixture paths')
    if 'shell_mode' in fixture and fixture['shell_mode'] != language:
        raise ValueError('shell_mode contradicts fixture source dialect')
    inventory = {}
    options = []
    for source in sources:
        path = _join(root, source['path'])
        if path in inventory:
            raise ValueError('duplicate fixture source path')
        inventory[path] = language
        option = default_file_options(path, language)
        if 'mode' in fixture:
            option.update(mode=fixture['mode'], strict=fixture['mode'] == 'module')
        if 'php_input' in fixture:
            option['input'] = fixture['php_input']
        if 'cwd_snapshot' in fixture:
            option['cwd_snapshot'] = _join(root, fixture['cwd_snapshot'], directory=True)
        options.append(option)
    data = {'file_options': options}
    if 'package_root' in fixture:
        data['package_roots'] = [_join(root, fixture['package_root'], directory=True)]
    if 'compiler' in fixture:
        units = fixture.get('translation_units')
        if units is None:
            suffixes = {'.c'} if language == 'c' else {'.cc', '.cpp', '.cxx', '.C'}
            units = [s['path'] for s in sources if Path(s['path']).suffix in suffixes]
        data['compiler_options'] = [{'language': language, 'standard': fixture['compiler'],
            'include_roots': [_join(root, fixture.get('include_root', '.'), directory=True)],
            'translation_units': [_join(root, path) for path in units]}]
    profile = SemanticProfile.model_validate(data)
    validate_profile_inventory(profile, inventory)
    return profile


def validate_profile_inventory(profile: SemanticProfile, inventory: Mapping[str, str | None]) -> None:
    """Pure owner predicate over captured regular-file metadata, not filesystem I/O.

    Runtime supplies canonical, decoded-alias-checked, no-follow inventory. None
    is allowed for unsupported files such as a selected compilation database.
    """
    directories = {''}
    for path in inventory:
        snapshot_file(path)
        parts = path.split('/')
        directories.update('/'.join(parts[:i]) for i in range(1, len(parts)))
    if set(inventory) & directories:
        raise ValueError('inventory file/directory collision')
    roots = [*profile.package_roots]
    if any(path not in directories and path not in inventory for path in profile.module_aliases.values()):
        raise ValueError('module alias target is not captured')
    for option in profile.file_options:
        if option.path not in inventory or inventory[option.path] != option.language:
            raise ValueError('exact-path option missing or selected dialect mismatch')
        if option.language in {'bash', 'zsh'} and option.cwd_snapshot is not None:
            roots.append(option.cwd_snapshot)
    for compiler in profile.compiler_options:
        roots.extend(compiler.include_roots)
        if any(path not in inventory or inventory[path] != compiler.language for path in compiler.translation_units):
            raise ValueError('translation unit missing or selected dialect mismatch')
    if any(root not in directories for root in roots):
        raise ValueError('profile directory is not captured')
    if profile.compilation_database is not None and profile.compilation_database not in inventory:
        raise ValueError('compilation database is not captured')


def _data(profile: SemanticProfile) -> dict:
    value = profile.model_dump(mode='json')
    if set(value) != SEMANTIC_FIELDS:
        raise ValueError('profile projection must explicitly account for every contract field')
    return value


def extraction_projection(profile: SemanticProfile) -> dict:
    value = _data(profile)
    options = []
    for item in sorted(value['file_options'], key=lambda item: item['path'].encode('utf-8')):
        # cwd supplies source-link resolution only; the selected shell dialect
        # still changes extraction and is never omitted.
        options.append({k: v for k, v in item.items() if k != 'cwd_snapshot'})
    return {'projection': 'language-extraction-v1', 'schema_version': value['schema_version'],
            'language_overrides': value['language_overrides'], 'encoding_overrides': value['encoding_overrides'],
            'file_options': options}


def resolution_projection(profile: SemanticProfile) -> dict:
    value = _data(profile)
    return {'projection': 'language-resolution-v1', 'schema_version': value['schema_version'],
            'package_roots': value['package_roots'], 'module_aliases': value['module_aliases'],
            'compilation_database': value['compilation_database'], 'compiler_options': value['compiler_options'],
            'shell_cwds': sorted([item for item in value['file_options'] if item['language'] in {'bash', 'zsh'}],
                                key=lambda item: item['path'].encode('utf-8'))}


class FingerprintInputs(Model):
    snapshot_id: Id
    parser_resources_digest: Digest
    resolver_digest: Digest
    compiler_inputs_digest: Digest


class ProfileFingerprints(Model):
    extraction: Digest
    resolution: Digest


def profile_fingerprints(profile: SemanticProfile, inputs: FingerprintInputs) -> ProfileFingerprints:
    """Actual inputs are required; there is no placeholder tool/default digest.

    compiler_inputs_digest covers the frozen pre-work census, including explicit
    invalid/default contexts. Observation IDs, results and machine paths cannot
    enter it. Settings has no argument here: operational changes cannot hash in.
    """
    extraction = semantic_digest({'snapshot_id': inputs.snapshot_id,
        'parser_resources_digest': inputs.parser_resources_digest, 'profile': extraction_projection(profile)})
    resolution = semantic_digest({'extraction_fingerprint': extraction,
        'resolver_digest': inputs.resolver_digest, 'compiler_inputs_digest': inputs.compiler_inputs_digest,
        'profile': resolution_projection(profile)})
    return ProfileFingerprints(extraction=extraction, resolution=resolution)


def main() -> None:
    from reference_language_fixtures import load_fixtures
    parser = argparse.ArgumentParser(description='Print a validated production profile for one authored fixture')
    parser.add_argument('--fixture', required=True)
    parser.add_argument('--root', default='')
    args = parser.parse_args()
    fixtures = {case['id']: case for case in load_fixtures()}
    if args.fixture not in fixtures:
        parser.error('unknown fixture')
    try:
        profile = fixture_to_profile(fixtures[args.fixture], root=args.root)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(canonical_bytes(profile.model_dump(mode='json')).decode('utf-8'))


if __name__ == '__main__':
    main()
