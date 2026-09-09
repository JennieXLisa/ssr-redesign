"""Executable specification models. NOT the harness, scheduler, SDK or tokenizer."""
from __future__ import annotations
import ast
from dataclasses import dataclass, field
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any, Iterable
ROOT=Path(__file__).resolve().parents[1]
class ContractError(ValueError):pass

def canonical(value: Any) -> bytes:
    def check(x):
        if isinstance(x,float):raise ContractError('floats are not canonical')
        if isinstance(x,int) and not isinstance(x,bool) and not 0<=x<=9007199254740991:raise ContractError('integer range')
        if isinstance(x,dict):
            if not all(isinstance(k,str) for k in x):raise ContractError('key type')
            for v in x.values():check(v)
        elif isinstance(x,(tuple,list)):
            for v in x:check(v)
        elif x is not None and not isinstance(x,(str,int,bool)):raise ContractError('value type')
    check(value)
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')

def digest(domain: str,value: Any) -> str:
    return hashlib.sha256(domain.encode()+b'\0'+canonical(value)).hexdigest()

def chain(domain: str,genesis: str,records: Iterable[dict]) -> list[str]:
    out=[];previous=bytes.fromhex(genesis)
    for n,record in enumerate(records,1):
        raw=canonical(record)
        previous=hashlib.sha256(domain.encode()+b'\0'+previous+n.to_bytes(8,'big')+len(raw).to_bytes(8,'big')+raw).digest()
        out.append(previous.hex())
    return out

def context_limits(configured=170000,verified=170000,output=16384,verified_output=16384,margin=4096):
    for x in (configured,verified,output,verified_output,margin):
        if type(x) is not int or x<=0:raise ContractError('invalid context bound')
    e=min(configured,verified);o=min(output,verified_output);i=e-o-margin
    if i<=0:raise ContractError('no input capacity')
    return {'effective':e,'output':o,'margin':margin,'max_input':i,'checkpoint_at':85*i//100}

def admit_context(count: int|None,limits:dict,request_hash:str,counted_hash:str):
    if count is None:raise ContractError('TOKEN_ACCOUNTING_UNAVAILABLE')
    if request_hash!=counted_hash:raise ContractError('REQUEST_CHANGED_AFTER_COUNT')
    if type(count) is not int or count<0 or count>limits['max_input']:raise ContractError('CONTEXT_LIMIT')
    return 'CHECKPOINT' if count>limits['checkpoint_at'] else 'ORDINARY'

def validate_dossier(token_count:int,raw:bytes,mandatory_tokens:int,mandatory_bytes:int):
    if token_count>8192 or len(raw)>32768 or mandatory_tokens>4096 or mandatory_bytes>16384:raise ContractError('DOSSIER_LIMIT')

def prefix_hash(body:dict,events:list[dict],genesis:str,request_binding:dict,transcript:dict|None,parent:dict|None=None):
    expected_genesis=digest('ssr.runtime-genesis.v2',{'identity':body['identity'],'execution_contract_hash':body['execution_contract_hash']})
    if genesis!=expected_genesis:raise ContractError('GENESIS_IDENTITY')
    if request_binding.get('identity')!=body['identity']:raise ContractError('ATTEMPT_BINDING')
    if request_binding.get('delivery_manifest_hash')!=body['delivery_manifest_hash']:raise ContractError('DELIVERY_BINDING')
    if request_binding.get('request_id')!=body['request_id']:raise ContractError('REQUEST_ID')
    if parent is None and body['parent_prefix_hash'] is not None:raise ContractError('PARENT_MISSING')
    if parent is not None:
        if body['parent_prefix_hash']!=digest('ssr.runtime-prefix.v1',parent) or parent['identity']!=body['identity'] or parent['execution_contract_hash']!=body['execution_contract_hash']:raise ContractError('PREFIX_PARENT')
        if parent['end_event_sequence']>=body['end_event_sequence']:raise ContractError('PREFIX_NOT_EXTENSION')
        if chain('ssr.runtime-event.v2',genesis,events[:parent['end_event_sequence']])[-1]!=parent['event_chain_hash']:raise ContractError('PREFIX_PARENT_CHAIN')
    end=body['end_event_sequence']
    if end<1 or len(events)<end:raise ContractError('PREFIX_GAP')
    if any(e.get('sequence')!=i for i,e in enumerate(events[:end],1)):raise ContractError('PREFIX_SEQUENCE')
    if events[end-1].get('kind')!='MODEL_RESPONSE':raise ContractError('PREFIX_NOT_RESPONSE')
    if events[end-1].get('complete') is not True:raise ContractError('PREFIX_INCOMPLETE')
    for key in ('request_id','response_id','request_hash','response_hash'):
        if events[end-1].get(key)!=body[key]:raise ContractError('EXCHANGE_BINDING')
    if not body['origin_calls'] or any(c['call_ordinal']!=n for n,c in enumerate(body['origin_calls'])):raise ContractError('CALL_ORDINAL')
    if len({c['call_id'] for c in body['origin_calls']})!=len(body['origin_calls']):raise ContractError('DUPLICATE_CALL')
    hashes=chain('ssr.runtime-event.v2',genesis,events[:end])
    if hashes[-1]!=body['event_chain_hash']:raise ContractError('PREFIX_HASH')
    if body['input_revision_hash']!=request_binding['input_revision_hash'] or body['request_hash']!=request_binding['request_hash']:raise ContractError('INPUT_BINDING')
    if request_binding.get('status')!='OBSERVED':raise ContractError('INPUT_UNOBSERVED')
    if body['origin_calls']!=events[end-1].get('origin_calls'):raise ContractError('CALL_BINDING')
    proof=body['transcript'];mode=proof['mode']
    if mode=='REQUIRED' and (proof['disposition']!='VERIFIED' or transcript is None):raise ContractError('REQUIRED_PREFIX_MISSING')
    if proof['disposition']=='VERIFIED':
        if transcript is None or transcript['identity']!=body['identity'] or transcript['execution_contract_hash']!=body['execution_contract_hash'] or transcript['request_id']!=body['request_id'] or transcript['response_id']!=body['response_id'] or transcript['request_hash']!=body['request_hash'] or transcript['response_hash']!=body['response_hash']:raise ContractError('TRANSCRIPT_BINDING')
        actual=digest('ssr.transcript-prefix.v1',transcript)
        if actual!=proof['prefix_hash'] or proof['prefix_id']!='tp1:'+actual:raise ContractError('TRANSCRIPT_HASH')
    elif proof['prefix_id'] is not None or proof['prefix_hash'] is not None:raise ContractError('FALSE_TRANSCRIPT_PROOF')
    if mode=='OFF' and proof['disposition']!='DISABLED':raise ContractError('CAPTURE_MODE')
    if mode=='OPTIONAL' and proof['disposition'] not in ('VERIFIED','OPTIONAL_UNAVAILABLE'):raise ContractError('CAPTURE_MODE')
    return digest('ssr.runtime-prefix.v1',body)

@dataclass
class YieldModel:
    state:str='RUNNING'
    attempt:int=1
    prepared:bool=False
    settled:bool=False
    answer:bool=False
    cancelled:bool=False
    generation:int=0
    publications:int=0
    def prepare(self):
        if self.prepared:return self.generation
        if self.state!='RUNNING':raise ContractError('NOT_RUNNING')
        self.prepared=True;self.generation+=1;return self.generation
    def publish_answer(self):
        self.answer=True
        if self.state=='WAITING_DEPENDENCY' and self.settled and not self.cancelled:self.state='PENDING'
    def settle(self,*,runtime=True,transcript=True):
        if not self.prepared or not runtime or not transcript:raise ContractError('SETTLEMENT_BLOCKED')
        self.settled=True
    def publish(self):
        if not self.settled:raise ContractError('SETTLEMENT_BLOCKED')
        if self.publications:return self.state
        self.state='CANCELLED' if self.cancelled else ('PENDING' if self.answer else 'WAITING_DEPENDENCY')
        self.publications+=1;return self.state
    def claim(self):
        if self.state!='PENDING' or not self.settled or self.publications!=1:return False
        self.attempt+=1;self.state='LEASED';return True

@dataclass
class SynthesisModel:
    manifest:dict
    session_id:str='session-1'
    revision:int=0
    decisions:dict=field(default_factory=dict)
    sets:dict=field(default_factory=dict)
    receipts:dict=field(default_factory=dict)
    sealed:bool=False
    def __post_init__(self):
        self.manifest_hash=digest('ssr.synthesis-manifest.v1',self.manifest)
        self.root=digest('ssr.synthesis-journal.v1',{'session_id':self.session_id,'manifest_hash':self.manifest_hash,'input_revision_hash':'0'*64})
    def stage(self,call:dict):
        if len(canonical(call))>65536:raise ContractError('INPUT_TOO_LARGE')
        op=digest('operation',call)
        if op in self.receipts:return self.receipts[op]
        if self.sealed or call['manifest_hash']!=self.manifest_hash or call['expected_revision']!=self.revision:raise ContractError('STALE_STAGE')
        if not 1<=len(call['entries'])<=32:raise ContractError('ENTRY_LIMIT')
        # Copy-on-write models a rollback-safe owner transaction, not a storage implementation.
        decisions=dict(self.decisions);sets={k:dict(v) for k,v in self.sets.items()};rev=self.revision;root=self.root
        for entry in call['entries']:
            if entry['kind']=='DECISION':
                key=entry['key'];old=decisions.get(key)
                if key not in self.manifest['required_keys']:raise ContractError('UNKNOWN_DECISION')
                expected=old['digest'] if old else None
                if entry['supersedes_digest']!=expected:raise ContractError('DECISION_CAS')
                decisions[key]={'entry':entry,'digest':digest('decision',entry)}
            else:
                pages=sets.setdefault(entry['set_key'],{})
                if entry['page_index'] in pages or any(p['final_page'] for p in pages.values()):raise ContractError('SET_PAGE_CONFLICT')
                if entry['page_index']!=len(pages):raise ContractError('SET_PAGE_GAP')
                pages[entry['page_index']]=entry
            rev+=1;raw=canonical(entry)
            root=hashlib.sha256(b'ssr.synthesis-entry.v1\0'+bytes.fromhex(root)+rev.to_bytes(8,'big')+len(raw).to_bytes(8,'big')+raw).hexdigest()
        self.decisions,self.sets,self.revision,self.root=decisions,sets,rev,root
        result={'revision':rev,'journal_hash':root};self.receipts[op]=result;return result
    def seal(self,call:dict,*,materials_current=True,receipts_valid=True):
        if len(canonical(call))>8192:raise ContractError('SEAL_TOO_LARGE')
        if call['manifest_hash']!=self.manifest_hash or call['expected_revision']!=self.revision or call['journal_hash']!=self.root:raise ContractError('STALE_SEAL')
        if not materials_current or not receipts_valid:raise ContractError('MATERIAL_OR_RECEIPT_BLOCKER')
        if set(self.decisions)!=set(self.manifest['required_keys']):raise ContractError('MISSING_DECISION')
        for value in self.decisions.values():
            for fieldname in ('origin_set_key','evidence_set_key'):
                key=value['entry'][fieldname]
                if key is not None:
                    pages=self.sets.get(key,{})
                    if not pages or not pages[max(pages)]['final_page']:raise ContractError('UNSEALED_REFERENCE_SET')
        self.sealed=True;return self.root

# Intentionally small pilot: top-level aliases and ordinary function bodies only.
def python_calls(source:str)->list[dict]:
    try:tree=ast.parse(source)
    except SyntaxError:return [{'state':'ERROR','reason':'PARSE_ERROR'}]
    aliases={}
    for node in tree.body:
        if isinstance(node,ast.Import):
            for a in node.names:
                aliases[a.asname or a.name.split('.')[0]]=a.name
        if isinstance(node,ast.ImportFrom) and node.module=='subprocess':
            for a in node.names:
                if a.name!='*':aliases[a.asname or a.name]='subprocess.'+a.name
    supported={'subprocess.run','subprocess.call','subprocess.Popen','subprocess.check_call','subprocess.check_output'}
    lines=source.encode('utf-8').splitlines(keepends=True);starts=[0]
    for line in lines:starts.append(starts[-1]+len(line))
    out=[]
    def binders(nodes):
        names=set();unsupported=False
        for root in nodes:
            for n in ast.walk(root):
                if isinstance(n,ast.Name) and isinstance(n.ctx,(ast.Store,ast.Del)):names.add(n.id)
                elif isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):names.add(n.name)
                elif isinstance(n,ast.arg):names.add(n.arg)
                elif isinstance(n,(ast.Import,ast.ImportFrom)):
                    for a in n.names:
                        if a.name=='*':unsupported=True
                        else:names.add(a.asname or a.name.split('.')[0])
                elif isinstance(n,ast.Attribute) and isinstance(n.ctx,(ast.Store,ast.Del)) and isinstance(n.value,ast.Name):names.add(n.value.id)
                elif isinstance(n,(ast.Global,ast.Nonlocal,ast.Lambda,ast.ListComp,ast.SetComp,ast.DictComp,ast.GeneratorExp,ast.Match)):unsupported=True
                elif isinstance(n,ast.ExceptHandler) and n.name:names.add(n.name)
        return names,unsupported
    module_shadow,_=binders([n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.AsyncFunctionDef))])
    def visit(node,shadow:set[str],unsupported:bool=False):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            bound,bad=binders([node]);shadow=shadow|bound;unsupported=unsupported or bad
        if isinstance(node,ast.Call):
            f=node.func;root=None;api=None
            if isinstance(f,ast.Name):root=f.id;api=aliases.get(root)
            elif isinstance(f,ast.Attribute) and isinstance(f.value,ast.Name):root=f.value.id;api=(aliases.get(root,'')+'.'+f.attr)
            state='EXACT' if api in supported and root not in shadow and not unsupported else 'UNRESOLVED'
            shell=None
            if not any(k.arg is None for k in node.keywords):
                for k in node.keywords:
                    if k.arg=='shell' and isinstance(k.value,ast.Constant) and type(k.value.value) is bool:shell=k.value.value
            start=starts[node.lineno-1]+node.col_offset;end=starts[node.end_lineno-1]+node.end_col_offset
            out.append({'state':state,'api':api if state=='EXACT' else None,'start_byte':start,'end_byte':end,'shell':shell})
        for child in ast.iter_child_nodes(node):visit(child,shadow,unsupported)
    module_bad=any(isinstance(n,ast.ImportFrom) and any(a.name=='*' for a in n.names) for n in tree.body)
    visit(tree,module_shadow,module_bad)
    return sorted(out,key=lambda r:(r['start_byte'],r['end_byte']))

def python_ir(source:str,symbol_ranges:tuple[tuple[str,int,int],...]=())->dict:
    """Build the declared IR for inert fixture source; not an installed adapter."""
    raw=source.encode();file_hash=hashlib.sha256(raw).hexdigest()
    batch={'contract':'callsite-ir-v1','snapshot_id':'fixture-snapshot','file_id':'fixture-file','file_hash':file_hash,'adapter_id':'python-reference-fixture','adapter_version':'1.0','status':'COMPLETE','calls':[],'next_cursor':None,'limitations':[]}
    simple=python_calls(source)
    if simple and simple[0].get('state')=='ERROR':batch.update(status='ERROR',limitations=['PARSE_ERROR']);return batch
    tree=ast.parse(source);lines=raw.splitlines(keepends=True);starts=[0]
    for line in lines:starts.append(starts[-1]+len(line))
    def span(n):return {'start_byte':starts[n.lineno-1]+n.col_offset,'end_byte':starts[n.end_lineno-1]+n.end_col_offset}
    def expr(n):
        kinds={ast.Name:'NAME',ast.Attribute:'ATTRIBUTE',ast.Call:'CALL',ast.Subscript:'SUBSCRIPT',ast.Constant:'LITERAL'}
        return {'range':span(n),'kind':kinds.get(type(n),'OTHER')}
    nodes=sorted((n for n in ast.walk(tree) if isinstance(n,ast.Call)),key=lambda n:(span(n)['start_byte'],span(n)['end_byte']))
    for node,item in zip(nodes,simple):
        r=span(node);contained=[s for s in symbol_ranges if s[1]<=r['start_byte'] and r['end_byte']<=s[2]];owner=min(contained,key=lambda s:s[2]-s[1])[0] if contained else None
        args=[]
        for a in node.args:args.append((span(a)['start_byte'],'STAR' if isinstance(a,ast.Starred) else 'POSITIONAL',None,a.value if isinstance(a,ast.Starred) else a))
        for k in node.keywords:args.append((span(k)['start_byte'],'DOUBLE_STAR' if k.arg is None else 'KEYWORD',k.arg,k.value))
        args.sort(key=lambda a:a[0]);entries=[]
        for ordinal,(_,kind,key,e) in enumerate(args[:256]):entries.append({'ordinal':ordinal,'kind':kind,'keyword':key,'expression':expr(e),'constant_bool':e.value if isinstance(e,ast.Constant) and type(e.value) is bool else None})
        limits=[] if len(args)<=256 else ['LIMIT_ARGUMENTS']
        key={'snapshot_id':batch['snapshot_id'],'file_id':batch['file_id'],'file_hash':file_hash,'start_byte':r['start_byte'],'end_byte':r['end_byte'],'adapter_id':batch['adapter_id'],'adapter_version':'1.0'}
        batch['calls'].append({'callsite_id':'cs1:'+digest('ssr.callsite.v1',key),'containing_symbol_id':owner,'range':r,'callee':expr(node.func),'receiver':expr(node.func.value) if isinstance(node.func,ast.Attribute) else None,'arguments':entries,'arguments_complete':not limits,'binding':{'state':item['state'],'canonical_api':'python:'+item['api'] if item['api'] else None,'basis':'IMPORT_ALIAS' if item['state']=='EXACT' else 'DYNAMIC','candidate_symbol_ids':[]},'limitations':limits})
        if limits:batch['status']='PARTIAL'
    if len(batch['calls'])>10000:batch.update(calls=batch['calls'][:10000],status='PARTIAL',limitations=['LIMIT_CALLS'])
    return batch

def validate_context_answer(value:dict,required_facets:set[str]):
    facets=value['facets'];ids=[f['facet_id'] for f in facets]
    if len(ids)!=len(set(ids)) or set(ids)!=required_facets:raise ContractError('FACET_COVERAGE')
    if value['outcome']=='ANSWERED' and any(f['status']!='ESTABLISHED' for f in facets):raise ContractError('FALSE_ANSWERED')
    if value['outcome']=='CONTRADICTED_ASSUMPTION' and not any(f['status']=='CONTRADICTED' and f['references'] for f in facets):raise ContractError('MISSING_COUNTEREVIDENCE')
    if value['outcome'] in ('INCONCLUSIVE','NEEDS_DIFFERENT_SCOPE') and not any(f['status'] in ('UNRESOLVED','OUT_OF_SCOPE') for f in facets):raise ContractError('MISSING_LIMITATION')
    if any(f['status'] in ('ESTABLISHED','CONTRADICTED') and not f['references'] for f in facets):raise ContractError('MISSING_EVIDENCE')

def input_token(payload:dict,key:bytes)->str:
    import base64
    enc=lambda b:base64.urlsafe_b64encode(b).rstrip(b'=').decode()
    raw=canonical(payload)
    result='i1.'+enc(raw)+'.'+enc(hmac.digest(key,b'ssr.input-token.v1\0'+raw,'sha256'))
    if len(result)>4096:raise ContractError('TOKEN_LIMIT')
    return result

def verify_input_token(token:str,key:bytes,identity:dict,request_binding:dict)->dict:
    import base64
    if len(token)>4096:raise ContractError('TOKEN_LIMIT')
    try:
        prefix,body,tag=token.split('.')
        if prefix!='i1' or '=' in body or '=' in tag:raise ValueError()
        raw=base64.b64decode(body+'='*(-len(body)%4),altchars=b'-_',validate=True)
        supplied=base64.b64decode(tag+'='*(-len(tag)%4),altchars=b'-_',validate=True)
    except (ValueError,UnicodeError) as exc:raise ContractError('TOKEN_FORMAT') from exc
    expected=hmac.digest(key,b'ssr.input-token.v1\0'+raw,'sha256')
    if not hmac.compare_digest(supplied,expected):raise ContractError('TOKEN_MAC')
    def pairs(items):
        if len({k for k,_ in items})!=len(items):raise ContractError('DUPLICATE_KEY')
        return dict(items)
    try:payload=json.loads(raw,object_pairs_hook=pairs)
    except (ValueError,UnicodeError) as exc:raise ContractError('TOKEN_JSON') from exc
    if canonical(payload)!=raw:raise ContractError('TOKEN_CANONICAL')
    required={'contract','key_id','identity','revision_id','revision_hash','required_delta_manifest_hash'}
    if set(payload)!=required or payload['contract']!='input-token-v1':raise ContractError('TOKEN_SHAPE')
    if payload['identity']!=identity:raise ContractError('TOKEN_ATTEMPT')
    if request_binding.get('observed') is not True or request_binding['token_hash']!=hashlib.sha256(token.encode()).hexdigest() or request_binding['revision_hash']!=payload['revision_hash'] or request_binding['required_delta_manifest_hash']!=payload['required_delta_manifest_hash']:raise ContractError('TOKEN_DELIVERY')
    return payload


def transcript_prefix_hash(body:dict,records:list[dict],genesis:str):
    expected=digest('ssr.transcript-genesis.v2',{'identity':body['identity'],'execution_contract_hash':body['execution_contract_hash'],'capture_identity_hash':body['capture_identity_hash']})
    if genesis!=expected:raise ContractError('CAPTURE_GENESIS')
    end=body['end_record_sequence']
    if end<1 or end>len(records) or body['record_count']!=end:raise ContractError('CAPTURE_COUNT')
    if any(r['sequence']!=i for i,r in enumerate(records[:end],1)):raise ContractError('CAPTURE_GAP')
    last=records[end-1]
    if last.get('kind')!='ACCEPTED_RESPONSE' or last.get('complete') is not True:raise ContractError('CAPTURE_INCOMPLETE')
    for key in ('request_id','response_id','request_hash','response_hash'):
        if last.get(key)!=body[key]:raise ContractError('CAPTURE_EXCHANGE')
    if body['total_bytes']!=sum(len(canonical(r)) for r in records[:end]):raise ContractError('CAPTURE_BYTES')
    if body['head_hash']!=chain('ssr.transcript-record.v2',genesis,records[:end])[-1]:raise ContractError('CAPTURE_CHAIN')
    return digest('ssr.transcript-prefix.v1',body)
