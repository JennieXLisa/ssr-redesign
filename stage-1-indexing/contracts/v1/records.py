"""Shared internal extraction values. No parser, database, filesystem or process I/O.

W02 adopts these types; W07-W11 produce them. Original bytes occur only in the
ephemeral SourceUnit, never in the persisted ExtractionBundle.
"""
from __future__ import annotations

import hashlib
import json
from typing import Literal
from uuid import UUID, uuid5

from pydantic import Field, model_validator
from models import (Argument, ByteRange, Count, Digest, Id, Language, Model,
                    SourceRange, SymbolKind, Usage, Version)


def canonical_bytes(value) -> bytes:
    """SSR canonical JSON v1: sorted keys, ordered arrays, no whitespace/NaN."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':')).encode('utf-8')


def semantic_digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def source_record_id(extraction_id: str, file_id: str, kind: str,
                     span: ByteRange, enclosing_id: str | None, ordinal: int) -> str:
    if isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 0:
        raise ValueError('ordinal must be a nonnegative integer')
    key = [file_id, kind, span.start_byte, span.end_byte, enclosing_id, ordinal]
    return str(uuid5(UUID(extraction_id), canonical_bytes(key).decode('utf-8')))


class OffsetBoundary(Model):
    parser_byte: Count
    original_byte: Count


class SourceUnit(Model):
    snapshot_id: Id
    extraction_id: Id
    file_id: Id
    path: str
    language: Language
    parser_profile_digest: Digest
    codec: Literal['utf-8', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']
    bom_bytes: Literal[0, 2, 3]
    original_bytes: bytes
    parser_utf8: bytes
    boundaries: list[OffsetBoundary]

    @model_validator(mode='after')
    def exact_transcoding(self):
        boms = {'utf-8': b'\xef\xbb\xbf', 'utf-16-le': b'\xff\xfe',
                'utf-16-be': b'\xfe\xff'}
        if self.bom_bytes and self.original_bytes[:self.bom_bytes] != boms.get(self.codec):
            raise ValueError('BOM does not match selected codec')
        text = self.original_bytes[self.bom_bytes:].decode(self.codec, errors='strict')
        if text.encode('utf-8') != self.parser_utf8:
            raise ValueError('parser buffer must preserve decoded text and newlines')
        expected = [(0, self.bom_bytes)]
        p, o = 0, self.bom_bytes
        for scalar in text:
            p += len(scalar.encode('utf-8'))
            o += len(scalar.encode(self.codec))
            expected.append((p, o))
        if [(b.parser_byte, b.original_byte) for b in self.boundaries] != expected:
            raise ValueError('offset map must cover every scalar boundary exactly')
        return self


Origin = Literal['declared', 'inferred', 'unknown']


class TypeFact(Model):
    text: str | None
    origin: Origin
    evidence: list[ByteRange]

    @model_validator(mode='after')
    def known(self):
        if (self.origin == 'unknown') != (self.text is None):
            raise ValueError('unknown type has null text; known type requires text')
        if self.origin != 'unknown' and not self.evidence:
            raise ValueError('known type requires source evidence')
        return self


class PropertyFact(Model):
    name: Literal['access', 'static', 'async', 'generator', 'abstract', 'final',
                  'virtual', 'const', 'variadic', 'exported', 'template', 'ref_qualifier']
    value: str | bool | None
    origin: Origin
    evidence: list[ByteRange]

    @model_validator(mode='after')
    def known(self):
        if (self.origin == 'unknown') != (self.value is None):
            raise ValueError('unknown property has null value')
        if self.origin != 'unknown' and not self.evidence:
            raise ValueError('known property requires source evidence')
        return self


class Provenance(Model):
    backend: str
    version: str
    profile_digest: Digest
    evidence: list[ByteRange]
    limitations: list[str]


class ParameterRecord(Model):
    ordinal: Count
    name: str | None
    kind: Literal['positional_only', 'positional', 'keyword_only', 'varargs', 'kwargs', 'receiver']
    range: ByteRange
    type: TypeFact
    default_range: ByteRange | None


class ScopeRecord(Model):
    scope_id: Id
    parent_scope_id: Id | None
    owner_symbol_id: Id | None
    kind: Literal['module', 'callable', 'type', 'block', 'comprehension', 'namespace']
    range: ByteRange


class SymbolRecord(Model):
    symbol_id: Id
    owner_scope_id: Id
    local_name: str | None
    qualified_name: str
    kind: SymbolKind
    signature: str | None
    return_type: TypeFact
    properties: list[PropertyFact]
    provenance: Provenance


class OccurrenceRecord(Model):
    occurrence_id: Id
    symbol_id: Id
    role: Literal['definition', 'declaration']
    range: SourceRange
    body_range: ByteRange | None
    signature_range: ByteRange | None
    name_range: ByteRange | None
    parameters: list[ParameterRecord]

    @model_validator(mode='after')
    def nested_ranges(self):
        if self.role == 'declaration' and self.body_range is not None:
            raise ValueError('declarations have no body')
        spans = [self.body_range, self.signature_range, self.name_range]
        spans += [p.range for p in self.parameters]
        spans += [p.default_range for p in self.parameters]
        for span in spans:
            if span and not self.range.start_byte <= span.start_byte <= span.end_byte <= self.range.end_byte:
                raise ValueError('occurrence subrange lies outside occurrence')
        if [p.ordinal for p in self.parameters] != list(range(len(self.parameters))):
            raise ValueError('parameter ordinals must be contiguous source order')
        return self


class ReferenceRecord(Model):
    reference_id: Id
    scope_id: Id
    owner_symbol_id: Id | None
    usage: Usage
    range: SourceRange
    spelling: str
    callee_range: ByteRange | None
    receiver_range: ByteRange | None
    arguments: list[Argument]
    provenance: Provenance

    @model_validator(mode='after')
    def call_shape(self):
        if self.usage not in ('CALL', 'CONSTRUCT') and self.arguments:
            raise ValueError('only invocation occurrences have arguments')
        if [a.ordinal for a in self.arguments] != list(range(len(self.arguments))):
            raise ValueError('argument ordinals must be contiguous source order')
        for span in [self.callee_range, self.receiver_range, *[a.range for a in self.arguments]]:
            if span and not self.range.start_byte <= span.start_byte <= span.end_byte <= self.range.end_byte:
                raise ValueError('call subrange lies outside expression')
        return self


class ImportRecord(Model):
    import_id: Id
    reference_id: Id
    scope_id: Id
    kind: Literal['import', 'export', 'require', 'include', 'source', 'dynamic']
    module: str | None
    imported_name: str | None
    local_name: str | None
    exported_name: str | None
    relative_level: Count
    range: ByteRange


class DeclarationRecord(Model):
    """A lexical binding or invalidation; not a resolved reference result."""
    declaration_id: Id
    scope_id: Id
    name: str
    kind: Literal['symbol', 'parameter', 'import', 'assignment', 'delete', 'global', 'nonlocal']
    symbol_id: Id | None
    import_id: Id | None
    range: ByteRange
    visible_from: Count
    visibility: Literal['whole_scope', 'after_declaration', 'tdz', 'dynamic']
    namespace: Literal['value', 'type']


class ExtractionDiagnostic(Model):
    code: Literal['PARSE_ERROR', 'MISSING_NODE', 'OWNERSHIP_LIMITATION', 'UNSUPPORTED_SYNTAX', 'CLASSIFICATION_AMBIGUITY']
    severity: Literal['error', 'limitation']
    range: ByteRange | None
    message: str


class ExtractionBundle(Model):
    schema_version: Version
    snapshot_id: Id
    extraction_id: Id
    file_id: Id
    language: Language
    byte_length: Count
    parser_profile_digest: Digest
    status: Literal['SUCCEEDED', 'FAILED']
    symbols: list[SymbolRecord]
    occurrences: list[OccurrenceRecord]
    scopes: list[ScopeRecord]
    imports: list[ImportRecord]
    declarations: list[DeclarationRecord]
    references: list[ReferenceRecord]
    diagnostics: list[ExtractionDiagnostic]

    @model_validator(mode='after')
    def integrity(self):
        collections = [(self.symbols, 'symbol_id'), (self.occurrences, 'occurrence_id'),
                       (self.scopes, 'scope_id'), (self.imports, 'import_id'),
                       (self.declarations, 'declaration_id'), (self.references, 'reference_id')]
        ids = [getattr(record, key) for records, key in collections for record in records]
        if len(ids) != len(set(ids)):
            raise ValueError('logical record IDs must be unique throughout a bundle')
        errors = any(d.severity == 'error' for d in self.diagnostics)
        if (self.status == 'FAILED') != errors:
            raise ValueError('failed bundle requires errors; success forbids errors')
        if self.status == 'FAILED':
            if ids:
                raise ValueError('failed bundle retains diagnostics, not a partial successful inventory')
        else:
            scopes = {s.scope_id: s for s in self.scopes}
            symbols = {s.symbol_id: s for s in self.symbols}
            references = {r.reference_id: r for r in self.references}
            imports = {i.import_id: i for i in self.imports}
            roots = [s for s in self.scopes if s.parent_scope_id is None]
            if len(roots) != 1 or roots[0].kind != 'module':
                raise ValueError('successful bundle requires exactly one module root scope')
            if sum(scope.kind == 'module' for scope in self.scopes) != 1:
                raise ValueError('a per-file bundle cannot contain a nested module scope')
            module_owner = roots[0].owner_symbol_id
            if module_owner is not None and (module_owner not in symbols or symbols[module_owner].kind != 'MODULE'):
                raise ValueError('module scope owner must be null or its module symbol')
            if (roots[0].range.start_byte, roots[0].range.end_byte) != (0, self.byte_length):
                raise ValueError('module scope must span the whole original file')
            for scope in self.scopes:
                visited = set()
                node = scope
                while node is not None:
                    if node.scope_id in visited:
                        raise ValueError('scope parent cycle')
                    visited.add(node.scope_id)
                    if node.parent_scope_id is not None and node.parent_scope_id not in scopes:
                        raise ValueError('unknown parent scope')
                    node = scopes.get(node.parent_scope_id)
                if scope.owner_symbol_id is not None and scope.owner_symbol_id not in symbols:
                    raise ValueError('unknown scope owner')
                if scope.kind == 'callable' and (scope.owner_symbol_id is None or
                        symbols[scope.owner_symbol_id].kind not in ('FUNCTION', 'METHOD', 'CONSTRUCTOR', 'DESTRUCTOR', 'LAMBDA')):
                    raise ValueError('callable scope requires a callable symbol owner')
                if scope.kind == 'callable':
                    owner = symbols[scope.owner_symbol_id]
                    if owner.owner_scope_id != scope.parent_scope_id:
                        raise ValueError('callable is declared in its body scope parent, not in its own body')
                    if not any(o.symbol_id == scope.owner_symbol_id and o.role == 'definition'
                               and o.body_range == scope.range for o in self.occurrences):
                        raise ValueError('callable scope must match an actual definition body')
                if scope.parent_scope_id is not None:
                    parent_range = scopes[scope.parent_scope_id].range
                    if not parent_range.start_byte <= scope.range.start_byte <= scope.range.end_byte <= parent_range.end_byte:
                        raise ValueError('child scope lies outside parent source extent')
            for symbol in self.symbols:
                if symbol.owner_scope_id not in scopes:
                    raise ValueError('unknown symbol declaration scope')
                if len({p.name for p in symbol.properties}) != len(symbol.properties):
                    raise ValueError('duplicate symbol property')
                if symbol.provenance.profile_digest != self.parser_profile_digest:
                    raise ValueError('symbol profile mismatch')
            for occurrence in self.occurrences:
                if occurrence.symbol_id not in symbols:
                    raise ValueError('unknown occurrence symbol')
            for ref in self.references:
                if ref.scope_id not in scopes:
                    raise ValueError('unknown reference scope')
                node = scopes[ref.scope_id]
                while node.kind not in ('module', 'callable'):
                    node = scopes[node.parent_scope_id]
                if ref.owner_symbol_id != node.owner_symbol_id:
                    raise ValueError('reference owner must be its executable evaluation scope owner')
                if ref.provenance.profile_digest != self.parser_profile_digest:
                    raise ValueError('reference profile mismatch')
            for imp in self.imports:
                if imp.reference_id not in references or imp.scope_id not in scopes:
                    raise ValueError('import requires its source reference and scope')
                if references[imp.reference_id].scope_id != imp.scope_id:
                    raise ValueError('import and its source reference must share evaluation scope')
            for decl in self.declarations:
                if decl.scope_id not in scopes or decl.visible_from > self.byte_length:
                    raise ValueError('invalid declaration scope/visibility position')
                if decl.symbol_id is not None and decl.symbol_id not in symbols:
                    raise ValueError('unknown declaration symbol')
                if decl.import_id is not None and decl.import_id not in imports:
                    raise ValueError('unknown declaration import')
                if decl.kind == 'symbol' and decl.symbol_id is None:
                    raise ValueError('symbol declaration requires a symbol identity')
                if decl.kind == 'import' and decl.import_id is None:
                    raise ValueError('import declaration requires an import identity')
        def validate_spans(value):
            if isinstance(value, ByteRange) and value.end_byte > self.byte_length:
                raise ValueError('original-byte range exceeds file')
            if isinstance(value, Model):
                for name in type(value).model_fields:
                    validate_spans(getattr(value, name))
            elif isinstance(value, list):
                for item in value:
                    validate_spans(item)
        # Walk children, not self: no recursive call to the bundle validator.
        for name in type(self).model_fields:
            validate_spans(getattr(self, name))
        return self


def validate_bundle_source(bundle: ExtractionBundle, source: SourceUnit) -> None:
    """Publication-boundary reference: identities, original text and positions."""
    for field in ('snapshot_id', 'extraction_id', 'file_id', 'language', 'parser_profile_digest'):
        if getattr(bundle, field) != getattr(source, field):
            raise ValueError(f'bundle/source {field} mismatch')
    if bundle.byte_length != len(source.original_bytes):
        raise ValueError('bundle/source byte length mismatch')
    text = source.original_bytes[source.bom_bytes:].decode(source.codec)
    positions = {0: (1, 1), source.bom_bytes: (1, 1)}
    offset, line, column, previous_cr = source.bom_bytes, 1, 1, False
    for scalar in text:
        offset += len(scalar.encode(source.codec))
        if scalar == '\r':
            line, column = line + 1, 1
        elif scalar == '\n':
            if not previous_cr:
                line += 1
            column = 1
        else:
            column += 1
        previous_cr = scalar == '\r'
        positions[offset] = (line, column)

    def walk(value):
        if isinstance(value, ByteRange):
            if value.start_byte not in positions or value.end_byte not in positions:
                raise ValueError('source span splits an encoded scalar')
            if isinstance(value, SourceRange):
                if positions[value.start_byte] != (value.start_line, value.start_column) or positions[value.end_byte] != (value.end_line, value.end_column):
                    raise ValueError('source line/column disagrees with original bytes')
        if isinstance(value, Model):
            for name in type(value).model_fields:
                walk(getattr(value, name))
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(bundle)
    for ref in bundle.references:
        actual = source.original_bytes[ref.range.start_byte:ref.range.end_byte].decode(source.codec)
        if actual != ref.spelling:
            raise ValueError('reference spelling differs from captured source')


INTERNAL_MODELS = [SourceUnit, ExtractionBundle, TypeFact, PropertyFact, Provenance,
                   ParameterRecord, ScopeRecord, SymbolRecord, OccurrenceRecord,
                   ReferenceRecord, ImportRecord, DeclarationRecord, ExtractionDiagnostic]
