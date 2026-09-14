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
(p.parent/'api.schema.json').write_text(json.dumps(b,indent=2)+'\n')
