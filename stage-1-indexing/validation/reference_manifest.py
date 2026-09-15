"""Typed extraction output manifests; SQL activation remains a runtime owner."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'contracts/v1'))
from records import ExtractionBundle, ExtractionDiagnostic, semantic_digest

COLLECTION_IDS = {
    'symbols': 'symbol_id', 'occurrences': 'occurrence_id', 'scopes': 'scope_id',
    'imports': 'import_id', 'declarations': 'declaration_id', 'references': 'reference_id',
}


def extraction_manifest(bundle: ExtractionBundle) -> dict:
    if bundle.status != 'SUCCEEDED':
        raise ValueError('failed extraction cannot produce a successful output manifest')
    records = []
    for collection, key in COLLECTION_IDS.items():
        for item in getattr(bundle, collection):
            value = item.model_dump(mode='json')
            records.append({'collection': collection, 'record_id': value[key], 'value': value})
    for diagnostic in bundle.diagnostics:
        value = diagnostic.model_dump(mode='json')
        records.append({'collection': 'diagnostics', 'record_id': semantic_digest(value), 'value': value})
    records.sort(key=lambda item: (item['collection'], item['record_id']))
    return {'schema_version': 1, 'records': records}


def publication_diagnostics(rows: list[dict], publication_id: str) -> list[dict]:
    """Project only this publication; general and stale-attempt errors stay out."""
    values = []
    for row in rows:
        if row.get('publication_id') == publication_id:
            value = ExtractionDiagnostic.model_validate(row['detail'])
            if value.severity != 'limitation':
                raise ValueError('successful publication cannot include error diagnostics')
            if row.get('code') != value.code:
                raise ValueError('diagnostic code disagrees with typed detail')
            values.append(value.model_dump(mode='json'))
    return values
