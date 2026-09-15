"""Stage 1 executable contract reference, not a harness implementation.

Production adopts these models in ssr.contracts; do not ship duplicate owners.
Requires Pydantic 2. Source boundary and database association checks live in owners.
"""
from __future__ import annotations
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

I64 = 2**63 - 1
Id = Annotated[str, StringConstraints(strict=True, pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')]
Digest = Annotated[str, StringConstraints(strict=True, pattern=r'^[0-9a-f]{64}$')]
Count = Annotated[int, Field(strict=True, ge=0, le=I64)]
Line = Annotated[int, Field(strict=True, ge=1, le=I64)]
Limit = Annotated[int, Field(strict=True, ge=1, le=200)]
Budget = Annotated[int, Field(strict=True, ge=1, le=1_000_000)]
Version = Annotated[int, Field(strict=True, ge=1, le=1)]
Token = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=4096)]
Category = Annotated[str, StringConstraints(strict=True, pattern=r'^[a-z][a-z0-9_]{0,63}$')]
Language = Literal['python','javascript','jsx','typescript','tsx','php','c','cpp','java','lua','bash','zsh']
CallableKind = Literal['FUNCTION','METHOD','CONSTRUCTOR','DESTRUCTOR','LAMBDA']
SymbolKind = Literal['FUNCTION','METHOD','CONSTRUCTOR','DESTRUCTOR','LAMBDA','CLASS','INTERFACE','TYPE','MODULE','VARIABLE']
StepState = Literal['PENDING','RUNNING','FAILED','SUCCEEDED','NOT_APPLICABLE']
Outcome = Literal['RESOLVED','AMBIGUOUS','UNRESOLVED']
BindingBasis = Literal['LEXICAL_DECLARATION','CAPTURED_IMPORT','DECLARED_RECEIVER_TYPE','CONSTRUCTOR_INITIALIZER','CLANG_REFERENCE','DYNAMIC_TARGET','MISSING_IMPORT','MISSING_BUILD_CONTEXT','UNSUPPORTED_BINDING','EXTERNAL_SOURCE_NOT_CAPTURED','CONTEXT_DISAGREEMENT','MULTIPLE_CANDIDATES']
Usage = Literal['CALL','CONSTRUCT','IMPORT','CALLBACK_ARGUMENT','SYMBOL_USE','SOURCE']

class Model(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True)

class ByteRange(Model):
    start_byte: Count
    end_byte: Count

    @model_validator(mode='after')
    def ordered(self):
        if self.end_byte < self.start_byte:
            raise ValueError('end_byte must be >= start_byte')
        return self

class SourceRange(ByteRange):
    start_line: Line
    end_line: Line
    start_column: Line
    end_column: Line

    @model_validator(mode='after')
    def coordinates(self):
        if (self.end_line, self.end_column) < (self.start_line, self.start_column):
            raise ValueError('exclusive end position precedes start')
        return self

class StepCoverage(Model):
    total_files: Count
    completed_files: Count
    failed_files: Count

    @model_validator(mode='after')
    def disjoint(self):
        if self.completed_files + self.failed_files > self.total_files:
            raise ValueError('completed and failed counts exceed total')
        return self

class Coverage(Model):
    index_complete: bool
    extraction: StepCoverage
    resolution: StepCoverage
    flagging: StepCoverage

    @model_validator(mode='after')
    def completion(self):
        if self.index_complete and any(s.completed_files != s.total_files or s.failed_files for s in (self.extraction,self.resolution,self.flagging)):
            raise ValueError('index_complete requires all displayed work complete')
        return self

class OccurrenceRef(ByteRange):
    occurrence_id: Id
    path: str
    start_line: Line
    end_line: Line

    @model_validator(mode='after')
    def lines_ordered(self):
        if self.end_line < self.start_line:
            raise ValueError('end_line precedes start_line')
        return self

class FunctionItem(Model):
    symbol_id: Id
    local_name: str | None
    qualified_name: str
    kind: CallableKind
    language: Language
    signature: str | None
    signature_complete: bool
    definitions: Annotated[list[OccurrenceRef], Field(max_length=8)]
    declarations: Annotated[list[OccurrenceRef], Field(max_length=8)]
    definitions_cursor: Token | None
    declarations_cursor: Token | None
    occurrences_complete: bool

class FunctionSearchRequest(Model):
    index_run_id: Id
    pattern: Annotated[str, Field(min_length=1, max_length=4096)]
    mode: Literal['wildcard','regex']
    case_sensitive: bool = True
    path_glob: str | None = None
    language: Language | None = None
    limit: Limit = 50
    cursor: Token | None = None

class Page(Model):
    index_run_id: Id
    snapshot_id: Id
    next_cursor: Token | None
    coverage: Coverage

class FunctionSearchPage(Page):
    items: Annotated[list[FunctionItem], Field(max_length=200)]

class ReadFunctionRequest(Model):
    index_run_id: Id
    symbol_id: Id
    occurrence_id: Id
    max_bytes: Budget | None = None

class ContinueReadRequest(Model):
    continuation: Token

class ReadFileRequest(Model):
    index_run_id: Id
    path: str
    start_line: Line = 1
    end_line: Line | None = None
    max_bytes: Budget | None = None

    @model_validator(mode='after')
    def interval(self):
        if self.end_line is not None and self.end_line < self.start_line:
            raise ValueError('end_line precedes start_line')
        return self

class SourcePage(Model):
    subject_kind: Literal['function','file']
    index_run_id: Id
    snapshot_id: Id
    symbol_id: Id | None
    occurrence_id: Id | None
    path: str
    source: str
    range: SourceRange
    next_continuation: Token | None
    coverage: Coverage

    @model_validator(mode='after')
    def subject(self):
        present = self.symbol_id is not None and self.occurrence_id is not None
        absent = self.symbol_id is None and self.occurrence_id is None
        if (self.subject_kind == 'function' and not present) or (self.subject_kind == 'file' and not absent):
            raise ValueError('subject kind and function identifiers disagree')
        return self

class SourceToken(Model):
    v: Version
    type: Literal['source']
    subject_kind: Literal['function','file']
    index_run_id: Id
    snapshot_id: Id
    file_id: Id
    symbol_id: Id | None
    occurrence_id: Id | None
    selection_start: Count
    selection_end: Count
    page_start: Count
    page_end: Count
    budget: Budget
    reader_profile: Literal['source-v1']

    @model_validator(mode='after')
    def boundaries(self):
        if not self.selection_start <= self.page_start < self.page_end <= self.selection_end:
            raise ValueError('continuation must advance within its selection')
        present = self.symbol_id is not None and self.occurrence_id is not None
        absent = self.symbol_id is None and self.occurrence_id is None
        if (self.subject_kind == 'function' and not present) or (self.subject_kind == 'file' and not absent):
            raise ValueError('token subject identifiers disagree')
        return self

class QueryKey(Model):
    path: str
    start_byte: Count
    record_id: Id

QueryOperation = Literal['find_functions','search_text','get_callers','get_callees','get_references','get_file_outline','list_directory','find_files','find_flags','list_occurrences','list_diagnostics','get_call_arguments','get_binding_targets']
class QueryToken(Model):
    v: Version
    type: Literal['query']
    operation: QueryOperation
    index_run_id: Id
    query_digest: Digest
    last_key: QueryKey

class TextSearchRequest(Model):
    index_run_id: Id
    pattern: Annotated[str, Field(min_length=1, max_length=4096)]
    case_sensitive: bool = True
    multiline: bool = False
    path_glob: str | None = None
    language: Language | None = None
    limit: Limit = 50
    cursor: Token | None = None

class TextMatch(Model):
    match_id: Id
    file_id: Id
    path: str
    range: SourceRange
    excerpt: str
    excerpt_truncated: bool
    symbol_id: Id | None
    occurrence_id: Id | None

class TextSearchPage(Page):
    items: Annotated[list[TextMatch], Field(max_length=200)]

class SymbolPageRequest(Model):
    index_run_id: Id
    symbol_id: Id
    limit: Limit = 50
    cursor: Token | None = None

class ReferencesRequest(SymbolPageRequest):
    usage: Usage | None = None

class Argument(Model):
    ordinal: Count
    keyword: str | None
    spread: bool
    range: ByteRange

class Target(Model):
    symbol_id: Id
    name: str
    definition: OccurrenceRef | None

class ReferenceItem(Model):
    reference_id: Id
    usage: Usage
    path: str
    range: SourceRange
    owner_symbol_id: Id | None
    owner_name: str | None
    receiver: ByteRange | None
    arguments: Annotated[list[Argument], Field(max_length=8)]
    resolution_state: Literal['PENDING','RUNNING','FAILED','SUCCEEDED']
    outcome: Outcome | None
    basis: BindingBasis | None
    targets: Annotated[list[Target], Field(max_length=8)]
    external_name: str | None
    arguments_cursor: Token | None
    targets_cursor: Token | None

    @model_validator(mode='after')
    def target_count(self):
        if (self.owner_symbol_id is None) != (self.owner_name is None):
            raise ValueError('owner identity and name must both be present or both null')
        if self.resolution_state == 'SUCCEEDED' and self.outcome is None:
            raise ValueError('completed resolution requires an outcome')
        if self.resolution_state != 'SUCCEEDED' and self.outcome is not None:
            raise ValueError('unfinished resolution has no final outcome')
        if self.outcome == 'RESOLVED' and (len(self.targets) != 1 or self.targets_cursor is not None):
            raise ValueError('resolved binding requires one target')
        if self.outcome == 'AMBIGUOUS' and len(self.targets) < 2 and self.targets_cursor is None:
            raise ValueError('ambiguous binding needs multiple candidates')
        if self.resolution_state == 'SUCCEEDED' and self.basis is None:
            raise ValueError('completed resolution requires its binding basis')
        if self.outcome == 'UNRESOLVED' and (self.targets or self.targets_cursor is not None):
            raise ValueError('unresolved binding has no established targets')
        return self

class ReferencePage(Page):
    items: Annotated[list[ReferenceItem], Field(max_length=200)]

class FileProgress(Model):
    extract: StepState
    resolve: StepState
    name_flags: StepState
    semgrep_flags: StepState
    text_metadata: StepState

class FileItem(Model):
    file_id: Id | None
    path: str
    entry_type: Literal['file','directory','symlink']
    language: Language | None
    size_bytes: Count | None
    progress: FileProgress | None

class FilePage(Page):
    items: Annotated[list[FileItem], Field(max_length=200)]

class DirectoryRequest(Model):
    index_run_id: Id
    path: str = ''
    limit: Limit = 50
    cursor: Token | None = None

class FindFilesRequest(Model):
    index_run_id: Id
    path_glob: str
    language: Language | None = None
    limit: Limit = 50
    cursor: Token | None = None

class OutlineRequest(Model):
    index_run_id: Id
    path: str
    limit: Limit = 50
    cursor: Token | None = None

class OutlineItem(Model):
    symbol_id: Id
    parent_symbol_id: Id | None
    depth: Count
    kind: SymbolKind
    display_name: str
    signature: str | None
    signature_complete: bool
    occurrence: OccurrenceRef

class OutlinePage(Page):
    items: Annotated[list[OutlineItem], Field(max_length=200)]
    extraction_state: StepState

class FlagItem(Model):
    flag_id: Id
    category: Category
    signal_kind: Literal['INTERESTING_NAME','CODE_PATTERN']
    reason: str
    file_id: Id
    path: str
    range: SourceRange
    owner_symbol_id: Id | None
    engine: Literal['name','semgrep']
    rule_id: str
    manifest_digest: Digest

class FlagPage(Page):
    items: Annotated[list[FlagItem], Field(max_length=200)]
    rule_mode: Literal['combined','custom_only']
    rule_manifest_digest: Digest

class FindFlagsRequest(Model):
    index_run_id: Id
    categories: list[Category] | None = None
    path_glob: str | None = None
    symbol_id: Id | None = None
    limit: Limit = 50
    cursor: Token | None = None

class OccurrencesRequest(SymbolPageRequest):
    kind: Literal['definition','declaration']

class OccurrencePage(Page):
    items: Annotated[list[OccurrenceRef], Field(max_length=200)]

ErrorCode = Literal['INDEX_INITIALIZING','INVALID_ARGUMENT','INVALID_PATTERN','UNKNOWN_LANGUAGE','RUN_NOT_FOUND','SYMBOL_NOT_FOUND','OCCURRENCE_NOT_FOUND','OCCURRENCE_MISMATCH','PATH_NOT_FOUND','PATH_OUTSIDE_SNAPSHOT','SOURCE_NOT_TEXT','SOURCE_RANGE_INVALID','INVALID_CONTINUATION','CURSOR_MISMATCH','RESPONSE_BUDGET_TOO_SMALL','RESPONSE_ITEM_TOO_LARGE','QUERY_TIMEOUT','STORAGE_UNAVAILABLE','STORAGE_INTEGRITY_ERROR','INTERNAL_ERROR']
class ErrorPosition(Model):
    unit: Literal['input_character','source_byte','source_line']
    start: Count
    end: Count | None

class ErrorItem(Model):
    code: ErrorCode
    operation: str
    field_path: list[str | int] | None
    component: str | None
    position: ErrorPosition | None
    message: Annotated[str, Field(max_length=768)]
    expected: str | None
    received: str | None
    remediation: Annotated[str, Field(max_length=1024)]
    retryable: bool
    diagnostic_id: Id | None
    requested_bytes: Count | None = None
    minimum_required_bytes: Count | None = None

class ErrorResponse(Model):
    errors: Annotated[list[ErrorItem], Field(min_length=1, max_length=32)]

class NameRule(Model):
    id: Annotated[str, Field(min_length=1, max_length=128)]
    mode: Literal['wildcard','regex']
    pattern: Annotated[str, Field(min_length=1, max_length=4096)]
    case_sensitive: bool
    categories: Annotated[list[Category], Field(min_length=1)]
    reason: Annotated[str, Field(min_length=1, max_length=1024)]

    @model_validator(mode='after')
    def unique_categories(self):
        if len(self.categories) != len(set(self.categories)):
            raise ValueError('categories must be unique')
        return self

class NameRules(Model):
    schema_version: Version
    rules: list[NameRule]

PUBLIC_MODELS = [FunctionSearchRequest, FunctionSearchPage, ReadFunctionRequest, ContinueReadRequest,
    ReadFileRequest, SourcePage, SourceToken, QueryToken, TextSearchRequest, TextSearchPage,
    SymbolPageRequest, ReferencesRequest, ReferencePage, DirectoryRequest, FindFilesRequest,
    FilePage, OutlineRequest, OutlinePage, FindFlagsRequest, FlagPage, OccurrencesRequest,
    OccurrencePage, ErrorResponse, NameRules]

class ReferenceDetailRequest(Model):
    index_run_id: Id
    reference_id: Id
    limit: Limit = 50
    cursor: Token | None = None

class ArgumentPage(Page):
    items: Annotated[list[Argument], Field(max_length=200)]

class TargetPage(Page):
    items: Annotated[list[Target], Field(max_length=200)]

GitOid = Annotated[str, StringConstraints(pattern=r'^(?:[0-9a-f]{40}|[0-9a-f]{64})$')]
class CreateProjectRequest(Model):
    label: Annotated[str, Field(min_length=1,max_length=200)]

class ProjectReceipt(Model):
    project_id: Id
    label: str

class CaptureRequest(Model):
    project_id: Id
    source: str
    revision: str | None = None
    fetch_submodules: bool = False
    include_ignored: bool = False

class CaptureReceipt(Model):
    project_id: Id
    snapshot_id: Id
    state: Literal['CAPTURING','FINALIZING','READY','FAILED']
    source_kind: Literal['local','https']
    source_locator: str
    requested_revision: str | None
    resolved_upstream_commit: GitOid | None
    managed_commit: GitOid | None
    tree_oid: GitOid | None
    included_files: Count
    excluded_entries: Count
    diagnostic_count: Count

class CreateIndexRequest(Model):
    snapshot_id: Id
    rule_mode: Literal['combined','custom_only'] = 'combined'
    custom_rules: list[str] = Field(default_factory=list)
    profile_path: str | None = None

class Progress(Model):
    index_run_id: Id
    snapshot_id: Id
    state: Literal['PLANNED','RUNNING','PAUSED','FAILED','SUCCEEDED']
    query_ready: bool
    extraction_id: Id
    resolution_id: Id
    flagging_id: Id
    rule_mode: Literal['combined','custom_only']
    rule_manifest_digest: Digest
    coverage: Coverage

class DiagnosticRequest(Model):
    index_run_id: Id
    component: str | None = None
    file_id: Id | None = None
    limit: Limit = 50
    cursor: Token | None = None

class DiagnosticItem(Model):
    diagnostic_id: Id
    file_id: Id | None
    path: str | None
    component: str
    code: str
    message: str
    remediation: str
    retryable: bool
    attempt: Count | None

class DiagnosticPage(Page):
    items: Annotated[list[DiagnosticItem], Field(max_length=200)]

PUBLIC_MODELS += [ReferenceDetailRequest,ArgumentPage,TargetPage,CreateProjectRequest,
    ProjectReceipt,CaptureRequest,CaptureReceipt,CreateIndexRequest,Progress,
    DiagnosticRequest,DiagnosticPage]
