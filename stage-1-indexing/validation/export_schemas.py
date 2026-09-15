from pathlib import Path
import importlib.util,sys,json
from typing import Union
from pydantic import TypeAdapter
p=Path(__file__).resolve().parent.parent/'contracts/v1/models.py'
s=importlib.util.spec_from_file_location('stage1_contracts_export',p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
b=TypeAdapter(Union[tuple(m.PUBLIC_MODELS)]).json_schema()
b['$schema']='https://json-schema.org/draft/2020-12/schema'
b['title']='SSR Stage 1 request/response contract bundle'
b['description']='Select the named $defs model for the called operation. Pydantic model validators and owner checks additionally enforce cross-field and database/source invariants.'
(p.parent/'api.schema.json').write_text(json.dumps(b,separators=(',', ':'))+'\n')
sys.path.insert(0, str(p.parent))
from records import INTERNAL_MODELS
from settings import Settings, SemanticProfile
internal = TypeAdapter(Union[tuple(INTERNAL_MODELS)]).json_schema()
internal['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
internal['title'] = 'SSR Stage 1 internal extraction contract bundle'
internal['description'] = 'SourceUnit is ephemeral; persist only typed bundle projections. Owner checks additionally verify source bytes and dataset identity.'
(p.parent/'internal.schema.json').write_text(json.dumps(internal,separators=(',', ':'))+'\n')
settings = TypeAdapter(Union[Settings, SemanticProfile]).json_schema()
settings['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
settings['title'] = 'SSR Stage 1 operational settings and semantic profile schemas'
(p.parent/'settings.schema.json').write_text(json.dumps(settings,separators=(',', ':'))+'\n')
from compiler_records import COMPILER_MODELS
compiler = TypeAdapter(Union[tuple(COMPILER_MODELS)]).json_schema()
compiler['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
compiler['title'] = 'SSR Stage 1 durable compiler context contract bundle'
compiler['description'] = 'Internal context census, work and observation models. Source, selected-publication, lock and native compiler checks remain owner/runtime obligations.'
(p.parent/'compiler.schema.json').write_text(json.dumps(compiler,separators=(',', ':'))+'\n')
