#!/usr/bin/env python3
"""Deterministically build design schemas; never import the harness or a target."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
D={}
def ref(name): return {'$ref':'#/$defs/'+name}
def text(n=4096, minimum=1): return {'type':'string','minLength':minimum,'maxLength':n}
def integer(lo=0,hi=9007199254740991): return {'type':'integer','minimum':lo,'maximum':hi}
def enum(*values): return {'type':'string','enum':list(values)}
def nullable(s): return {'anyOf':[s,{'type':'null'}]}
def array(s,n=128,minimum=0): return {'type':'array','items':s,'minItems':minimum,'maxItems':n}
def obj(**fields): return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False,'x-python-field-order':list(fields)}
def add(name,**fields): D[name]=obj(**fields); return ref(name)
ID={**text(200),'pattern':r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$'}; HASH={'type':'string','pattern':'^[0-9a-f]{64}$'}; TOKEN={**text(4096),'pattern':r'^[A-Za-z0-9._:-]+$'}; BOOL={'type':'boolean'}
TASK=enum('SYMBOL_REVIEW','FILE_REVIEW','LINK_REVIEW','FOCUSED_ANALYSIS','CONTEXT_REVIEW','INVESTIGATION','FALSIFICATION')
ARTIFACT=enum('SYMBOL_RESULT','FILE_SYNTHESIS','LINK_RESULT','FOCUSED_RESULT','CONTEXT_ANSWER','CONTEXT_RESULT','INVESTIGATION_ARGUMENT','INVESTIGATION_DISPOSITION','INVESTIGATION_PROGRESS','FALSIFICATION_VERDICT','LEAD_ORIGIN','ANALYSIS_OBSERVATION')
STATE=enum('PENDING','LEASED','RUNNING','WAITING_DEPENDENCY','COMPLETED','FAILED','CANCELLED','SUPERSEDED','SKIPPED')
CODE=enum('INVALID_INPUT','UNAUTHORIZED','STALE_INPUT','STALE_ATTEMPT','NOT_FOUND','NOT_AVAILABLE','CONTRACT_MISMATCH','INTEGRITY_FAILURE','RECEIPT_PENDING','SETTLEMENT_BLOCKED','CONTEXT_LIMIT','TOKEN_ACCOUNTING_UNAVAILABLE','LIMIT_REACHED','NO_PROGRESS','CONFLICT','OUTCOME_UNKNOWN','INTERNAL_ERROR')
add('Subject',kind=enum('symbol','file','candidate','artifact','relationship'),id=ID)
add('Reference',kind=enum('SOURCE','EVIDENCE','ARTIFACT','RELATIONSHIP'),id=text(16384))
add('Assertion',claim=text(),references=array(ref('Reference'),32,1))
add('Facet',facet_id=ID,status=enum('ESTABLISHED','CONTRADICTED','UNRESOLVED','OUT_OF_SCOPE'),analysis=text(),references=array(ref('Reference'),32))
add('IssueDetails',expected_type=nullable(enum('STRING','INTEGER','BOOLEAN','ARRAY','OBJECT','REFERENCE','CONTRACT')),expected_maximum=nullable(integer()),observed_integer=nullable(integer()),expected_contract=nullable(ID),reference_kind=nullable(enum('SOURCE','EVIDENCE','ARTIFACT','RELATIONSHIP')))
add('Issue',code=CODE,location=text(512,0),message=text(1024),retry_kind=enum('FIX_INPUT','MORE_ANALYSIS','RETRY_SAME_OPERATION','HOST_RECOVERY','NONE'),repair_action=enum('CORRECT_FIELD','READ_REFERENCED_SOURCE','REFRESH_INPUT','FETCH_EXACT_RESULT','CONTINUE_SAME_CURSOR','RETRY_SAME_OPERATION','REQUEST_HOST_RECOVERY','NONE'),details=ref('IssueDetails'))
add('Error',contract={'const':'collaborative-v1'},code=CODE,message=text(1024),correlation_id=ID,issues=array(ref('Issue'),16),omitted_issue_count=integer(),commit_state=enum('NONE','PREPARED','COMMITTED','UNKNOWN'))
add('AttemptIdentity',review_run_id=ID,snapshot_id=ID,task_id=ID,agent_run_id=ID,attempt_number=integer(1),control_generation=integer(1))
add('InputRevision',contract={'const':'input-v1'},review_run_id=ID,snapshot_id=ID,task_id=ID,generation=integer(1),predecessor_digest=nullable(HASH),assignment_digest=HASH,policy_digest=HASH,material_manifest_hash=HASH,request_manifest_hash=HASH,checkpoint_id=nullable(ID),checkpoint_hash=nullable(HASH),required_delta_manifest_hash=HASH)
add('InputTokenPayload',contract={'const':'input-token-v1'},key_id=ID,identity=ref('AttemptIdentity'),revision_id=ID,revision_hash=HASH,required_delta_manifest_hash=HASH)
add('OriginCall',call_id=ID,call_ordinal=integer(0,255),tool_name=ID,arguments_hash=HASH)
add('TranscriptPrefix',contract={'const':'transcript-prefix-v1'},capture_id=ID,capture_identity_hash=HASH,execution_contract_hash=HASH,identity=ref('AttemptIdentity'),request_id=ID,response_id=ID,end_record_sequence=integer(1),record_count=integer(1),total_bytes=integer(),head_hash=HASH,request_hash=HASH,response_hash=HASH,parent_prefix_hash=nullable(HASH))
add('CaptureProof',mode=enum('REQUIRED','OPTIONAL','OFF'),disposition=enum('VERIFIED','OPTIONAL_UNAVAILABLE','DISABLED'),prefix_id=nullable(ID),prefix_hash=nullable(HASH))
add('RuntimePrefix',contract={'const':'runtime-prefix-v1'},identity=ref('AttemptIdentity'),execution_contract_hash=HASH,input_revision_hash=HASH,request_id=ID,response_id=ID,request_hash=HASH,response_hash=HASH,end_event_sequence=integer(1),event_chain_hash=HASH,parent_prefix_hash=nullable(HASH),delivery_manifest_hash=HASH,origin_calls=array(ref('OriginCall'),256,1),transcript=ref('CaptureProof'))
add('RequestBinding',contract={'const':'request-binding-v1'},identity=ref('AttemptIdentity'),request_id=ID,request_hash=HASH,input_revision_id=ID,input_revision_hash=HASH,input_token_hash=HASH,delivered_delta_manifest_hash=HASH,delivery_manifest_hash=HASH,status=enum('PREPARED','OBSERVED'),response_id=nullable(ID),response_hash=nullable(HASH))
add('RequestEvent',contract={'const':'runtime-event-v2'},sequence=integer(1),kind={'const':'MODEL_REQUEST'},request_id=ID,request_hash=HASH,input_revision_hash=HASH,delivery_manifest_hash=HASH,input_token_hash=HASH,token_count=integer(),reserved_output_tokens=integer(1),counter_digest=HASH)
add('ResponseEvent',contract={'const':'runtime-event-v2'},sequence=integer(1),kind={'const':'MODEL_RESPONSE'},request_id=ID,response_id=ID,request_hash=HASH,response_hash=HASH,complete=BOOL,stop_reason=enum('TOOL_CALLS','END_TURN','MAX_OUTPUT','REFUSAL'),origin_calls=array(ref('OriginCall'),256),input_tokens=nullable(integer()),output_tokens=nullable(integer()))
add('ToolEvent',contract={'const':'runtime-event-v2'},sequence=integer(1),kind=enum('TOOL_EFFECT','TOOL_RESULT_DELIVERED'),response_id=ID,call_id=ID,call_ordinal=integer(0,255),operation_id=nullable(ID),arguments_hash=HASH,result_hash=HASH,committed=BOOL,delivery_manifest_hash=nullable(HASH))
add('TerminalEvent',contract={'const':'runtime-event-v2'},sequence=integer(1),kind={'const':'AGENT_TERMINAL'},status=enum('COMPLETED','INVALID_OUTPUT','TIMED_OUT','REFUSED','FAILED','CANCELLED'),termination_reason=enum('RESULT_ACCEPTED','YIELDED','INVALID_OUTPUT','TIMED_OUT','REFUSED','FAILED','CANCELLED'),yield_intent_id=nullable(ID),result_artifact_id=nullable(ID),final_input_revision_hash=HASH,settlement_manifest_hash=HASH)
add('FocusedResult',contract={'const':'focused-result-v1'},input_token=TOKEN,question=text(),checked_subjects=array(ref('Subject'),64,1),observations=array(ref('Assertion'),64),counterevidence=array(ref('Assertion'),64),assumptions=array(text(2048),32),unknowns=array(text(2048),32),disposition=enum('LEADS_RECORDED','NO_SUPPORTED_LEAD','INCONCLUSIVE'),registered_lead_ids=array(ID,64),next_context_request_ids=array(ID,8))
D['FocusedResult']['allOf']=[{'if':{'properties':{'disposition':{'const':'LEADS_RECORDED'}}},'then':{'properties':{'registered_lead_ids':{'minItems':1}}}},{'if':{'properties':{'disposition':{'const':'NO_SUPPORTED_LEAD'}}},'then':{'properties':{'registered_lead_ids':{'maxItems':0}}}},{'if':{'properties':{'disposition':{'const':'INCONCLUSIVE'}}},'then':{'properties':{'unknowns':{'minItems':1}}}}]
add('ContextAnswer',contract={'const':'context-answer-v1'},input_token=TOKEN,request_id=ID,request_revision=integer(1),scope_checked=array(ref('Subject'),64,1),facets=array(ref('Facet'),64,1),answer=text(8192),assumptions=array(text(2048),32),counterevidence=array(ref('Assertion'),64),unknowns=array(text(2048),32),outcome=enum('ANSWERED','CONTRADICTED_ASSUMPTION','INCONCLUSIVE','NEEDS_DIFFERENT_SCOPE'))
add('ContextResult',contract={'const':'context-result-v1'},input_token=TOKEN,answer_artifact_id=ID,answer_artifact_hash=HASH,request_id=ID,request_revision=integer(1),disposition=enum('ANSWERED','CONTRADICTED_ASSUMPTION','INCONCLUSIVE','NEEDS_DIFFERENT_SCOPE'))
add('SynthesisManifest',contract={'const':'synthesis-manifest-v1'},task_id=ID,input_revision_hash=HASH,snapshot_id=ID,file_id=ID,graph_id=ID,graph_hash=HASH,policy_hash=HASH,item_count=integer(),items_root=HASH,required_decision_count=integer(1),required_decisions_root=HASH,evidence_closure_root=HASH,origin_manifest_root=HASH)
add('SynthesisManifestItem',ordinal=integer(),item_key=ID,kind=enum('CONTRIBUTION','RECONCILIATION_OBLIGATION','RESIDUAL_FILE_OBLIGATION'),unit_id=nullable(ID),unit_input_hash=nullable(HASH),artifact_id=nullable(ID),artifact_hash=nullable(HASH),adoption_receipt_id=nullable(ID),subject_set_hash=HASH,evidence_closure_hash=HASH,dependency_closure_hash=HASH,origin_manifest_hash=HASH,required_decision_key=nullable(ID))
add('SynthesisDecision',kind={'const':'DECISION'},key=ID,action=enum('RETAIN','MERGE','REJECT_PROPOSAL','UNRESOLVED','FILE_ANALYSIS'),origin_set_key=nullable(ID),evidence_set_key=nullable(ID),rationale=text(8192),supersedes_digest=nullable(HASH))
add('SynthesisReferences',kind={'const':'REFERENCE_SET_PAGE'},set_key=ID,page_index=integer(),references=array(ref('Reference'),128,1),final_page=BOOL)
add('SynthesisStage',contract={'const':'synthesis-stage-v1'},input_token=TOKEN,session_id=ID,manifest_hash=HASH,expected_revision=integer(),entries=array({'oneOf':[ref('SynthesisDecision'),ref('SynthesisReferences')]},32,1))
add('SynthesisSeal',contract={'const':'synthesis-seal-v1'},input_token=TOKEN,session_id=ID,manifest_hash=HASH,expected_revision=integer(),journal_hash=HASH)
add('SynthesisReceipt',session_id=ID,manifest_hash=HASH,revision=integer(),journal_hash=HASH,committed_entry_count=integer(),operation_id=ID)
add('InvestigationProgress',contract={'const':'investigation-progress-v1'},input_token=TOKEN,candidate_revision=integer(1),outcome={'const':'NEED_CONTEXT'},checkpoint_id=ID,request_ids=array(ID,8,1),missing_facets=array(ID,32,1))
add('CallRange',start_byte=integer(),end_byte=integer(1))
add('ExpressionRef',range=ref('CallRange'),kind=enum('NAME','ATTRIBUTE','CALL','SUBSCRIPT','LITERAL','OTHER'))
add('CallArgument',ordinal=integer(0,255),kind=enum('POSITIONAL','KEYWORD','STAR','DOUBLE_STAR'),keyword=nullable(text(200)),expression=ref('ExpressionRef'),constant_bool=nullable(BOOL))
add('CallBinding',state=enum('EXACT','AMBIGUOUS','UNRESOLVED','NOT_SUPPORTED'),canonical_api=nullable(ID),basis=enum('IMPORT_ALIAS','FROM_IMPORT','BUILTIN_SCOPE','LOCAL_DECLARATION','SHADOWED','DYNAMIC','MISSING'),candidate_symbol_ids=array(ID,32))
D['CallBinding']['allOf']=[{'if':{'properties':{'state':{'const':'EXACT'}}},'then':{'properties':{'canonical_api':ID}}},{'if':{'properties':{'state':{'enum':['UNRESOLVED','NOT_SUPPORTED']}}},'then':{'properties':{'canonical_api':{'type':'null'}}}}]
add('Callsite',callsite_id=ID,containing_symbol_id=nullable(ID),range=ref('CallRange'),callee=ref('ExpressionRef'),receiver=nullable(ref('ExpressionRef')),arguments=array(ref('CallArgument'),256),arguments_complete=BOOL,binding=ref('CallBinding'),limitations=array(ID,32))
add('AdapterCallBinding',state=enum('EXACT','AMBIGUOUS','UNRESOLVED','NOT_SUPPORTED'),canonical_api=nullable(ID),basis=enum('IMPORT_ALIAS','FROM_IMPORT','BUILTIN_SCOPE','LOCAL_DECLARATION','SHADOWED','DYNAMIC','MISSING'),candidate_local_ids=array(ID,32))
add('AdapterCallsite',containing_symbol_local_id=nullable(ID),range=ref('CallRange'),callee=ref('ExpressionRef'),receiver=nullable(ref('ExpressionRef')),arguments=array(ref('CallArgument'),256),arguments_complete=BOOL,binding=ref('AdapterCallBinding'),limitations=array(ID,32))
add('AdapterCallsiteBatch',contract={'const':'callsite-adapter-v1'},file_hash=HASH,adapter_id=ID,adapter_version=ID,status=enum('COMPLETE','PARTIAL','UNSUPPORTED','ERROR'),calls=array(ref('AdapterCallsite'),10000),next_start_byte=nullable(integer()),limitations=array(ID,64))
add('CallsiteBatch',contract={'const':'callsite-ir-v1'},snapshot_id=ID,file_id=ID,file_hash=HASH,adapter_id=ID,adapter_version=ID,status=enum('COMPLETE','PARTIAL','UNSUPPORTED','ERROR'),calls=array(ref('Callsite'),10000),next_cursor=nullable(TOKEN),limitations=array(ID,64))
# SDK: every wire object has all keys present; nullable is explicit and field order frozen.
add('PageRequest',cursor=nullable(TOKEN),limit=integer(1,100))
add('WorkFilter',task_types=array(TASK,7),states=array(STATE,9),root_work_id=nullable(ID))
add('ArtifactFilter',subject=ref('Subject'),kinds=array(ARTIFACT,13),include_superseded=BOOL)
add('Capabilities',contract={'const':'collaborative-v1'},schema_bundle_hash=HASH,sdk_abi_hash=HASH,state_contract_hash=HASH,runtime_receipt_contract={'const':'2.0'},prefix_receipt_contract={'const':'1.0'},supported_task_types=array(TASK,7,7),max_page_items=integer(100,100))
add('ResourceCapacity',resource_id=ID,kind=enum('PROVIDER','MATCHER','HOST'),route_ids=array(ID,64),upper_bound=integer(1,1024))
add('SlicePlan',plan_id=ID,review_run_id=ID,config_hash=HASH,contract_hash=HASH,control_generation=integer(1),requested_capacity=integer(1,1024),effective_capacity=integer(0,1024),resources=array(ref('ResourceCapacity'),128),command_input_token_budget=integer(),command_output_token_budget=integer(),exact_task_id=nullable(ID),observed_sequence=integer(),expires_at={'type':'string','pattern':r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$'},plan_digest=HASH)
add('DriveResult',plan_id=ID,started=integer(),completed=integer(),failed=integer(),settling=integer(),waiting=integer(),still_running=integer(),reason=enum('SLICE_COMPLETE','CAPACITY_FULL','NO_ELIGIBLE_WORK','BUDGET_EXHAUSTED','CANCELLED','RECOVERY_REQUIRED'),completion=enum('ANALYZING','COMPLETE','COMPLETE_WITH_LIMITATIONS','BLOCKED','CANCELLED','FAILED'))
add('WorkSummary',task_id=ID,root_work_id=ID,task_type=TASK,state=STATE,attempt_id=nullable(ID),attempt_number=nullable(integer(1)),input_revision_hash=HASH,wait_generation=nullable(integer(1)),subject_manifest_ref=ID,result_manifest_ref=nullable(ID),blocker=nullable(enum('DEPENDENCY','SETTLING','RECEIPT','BUDGET','PROVIDER','CONTEXT','NO_PROGRESS','INTEGRITY')))
add('RequestSummary',request_id=ID,revision=integer(1),producer_task_id=nullable(ID),state=enum('REGISTERED','ROUTED','ANSWER_AVAILABLE','CLOSED','CANCELLED'),consumer_count=integer(),answer_artifact_id=nullable(ID),answer_hash=nullable(HASH))
add('ArtifactSummary',artifact_id=ID,kind=ARTIFACT,payload_hash=HASH,producer_task_id=ID,producer_attempt_id=ID,state=enum('ACCEPTANCE_PENDING','AVAILABLE','WITHDRAWN','REJECTED'),availability_sequence=nullable(integer(1)),availability_generation=integer(),subject_manifest_ref=ID)
add('FindingSummary',family_id=ID,candidate_id=ID,revision=integer(1),argument_hash=HASH,validity_generation=integer(1),verdict_artifact_id=ID,state={'const':'CURRENT'},review_complete=BOOL)
add('Completion',review_run_id=ID,status=enum('ANALYZING','COMPLETE','COMPLETE_WITH_LIMITATIONS','BLOCKED','CANCELLED','FAILED'),canonical_total=integer(),canonical_complete=integer(),required_open=integer(),settling_count=integer(),receipt_pending_count=integer(),unresolved_limitations=integer(),blockers=array(CODE,16),omitted_blocker_count=integer(),as_of_sequence=integer())
for n,item in [('WorkPage','WorkSummary'),('RequestPage','RequestSummary'),('ArtifactPage','ArtifactSummary'),('FindingPage','FindingSummary')]:
 add(n,items=array(ref(item),100),next_cursor=nullable(TOKEN),exhausted=BOOL,as_of_sequence=integer())
for name,field in [('Capabilities','supported_task_types'),('WorkFilter','task_types'),('WorkFilter','states'),('ArtifactFilter','kinds')]:D[name]['properties'][field]['uniqueItems']=True
SCHEMA={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:ssr:collaborative:hardening:1','title':'Collaborative-v1 hardening contracts','$defs':D}
p=ROOT/'contracts/schemas/hardening-v1.schema.json';p.write_text(json.dumps(SCHEMA,indent=2,ensure_ascii=False)+'\n')
# Function names, order, defaults, and annotations are exact ABI, not suggested pseudo-code.
methods=[
 ('CollaborativeReviewService','capabilities',[('context','CommandContext','POSITIONAL_OR_KEYWORD',None)],'Capabilities'),
 ('CollaborativeReviewService','plan_collaborative_slice',[('context','CommandContext','POSITIONAL_OR_KEYWORD',None),('review_run_id','str','KEYWORD_ONLY',None),('requested_capacity','int','KEYWORD_ONLY',None),('exact_task_id','str | None','KEYWORD_ONLY','None')],'SlicePlan'),
 ('CollaborativeReviewService','drive_collaborative_slice',[('context','CommandContext','POSITIONAL_OR_KEYWORD',None),('plan','SlicePlan','KEYWORD_ONLY',None),('admission_token','SchedulingAdmissionToken','KEYWORD_ONLY',None)],'DriveResult'),
 ('CollaborativeQueryService','list_work',[('context','ProjectQueryContext','POSITIONAL_OR_KEYWORD',None),('review_run_id','str','KEYWORD_ONLY',None),('filters','WorkFilter','KEYWORD_ONLY',None),('page','PageRequest','KEYWORD_ONLY',None)],'WorkPage'),
 ('CollaborativeQueryService','list_requests',[('context','ProjectQueryContext','POSITIONAL_OR_KEYWORD',None),('review_run_id','str','KEYWORD_ONLY',None),('task_id','str | None','KEYWORD_ONLY',None),('page','PageRequest','KEYWORD_ONLY',None)],'RequestPage'),
 ('CollaborativeQueryService','list_artifacts',[('context','ProjectQueryContext','POSITIONAL_OR_KEYWORD',None),('review_run_id','str','KEYWORD_ONLY',None),('filters','ArtifactFilter','KEYWORD_ONLY',None),('page','PageRequest','KEYWORD_ONLY',None)],'ArtifactPage'),
 ('CollaborativeQueryService','list_current_findings',[('context','ProjectQueryContext','POSITIONAL_OR_KEYWORD',None),('review_run_id','str','KEYWORD_ONLY',None),('page','PageRequest','KEYWORD_ONLY',None)],'FindingPage'),
 ('CollaborativeQueryService','get_review_completion',[('context','ProjectQueryContext','POSITIONAL_OR_KEYWORD',None),('review_run_id','str','KEYWORD_ONLY',None)],'Completion')]
ABI={'contract':'sdk-abi-v1','command_export':'ssr.application','query_export':'ssr.query','dto_export':'ssr.collaborative.dto','methods':[],'dto_field_order':{n:v['x-python-field-order'] for n,v in D.items()},'exception':'CollaborativeServiceError','error_schema':'Error','constructors':{'CollaborativeReviewService':'(config: SSRConfig)','CollaborativeQueryService':'()'}}
for cls,name,params,ret in methods:
 ABI['methods'].append({'class':cls,'name':name,'parameters':[{'name':n,'annotation':t,'kind':k,'default_expression':v} for n,t,k,v in params],'return_annotation':ret})
(ROOT/'contracts/schemas/sdk-abi.json').write_text(json.dumps(ABI,indent=2)+'\n')
print('generated',len(D),'closed object definitions and',len(methods),'SDK methods')
# Exhaustive selected transition rows. Guard semantics live in STATE_MACHINE.md.
transitions=[]
def tr(a,b,*guards): transitions.append({'from':a,'to':b,'guards':list(guards)})
tr('PENDING','LEASED','ADMIT');tr('PENDING','COMPLETED','ADOPT_COMPLETE_UNIT');tr('PENDING','CANCELLED','CANCEL_UNCLAIMED');tr('PENDING','SUPERSEDED','RETIRE_UNCLAIMED');tr('PENDING','SKIPPED','DECLARE_NONREVIEWABLE')
tr('LEASED','RUNNING','START');tr('LEASED','PENDING','RELEASE_UNDISPATCHED','RETRY_SETTLED')
for state in ['FAILED','CANCELLED','SUPERSEDED']:tr('LEASED',state,'TERMINAL_'+state+'_SAFE')
tr('RUNNING','RUNNING','PREPARE_YIELD','SAVE_PROGRESS');tr('RUNNING','WAITING_DEPENDENCY','PUBLISH_SETTLED_WAIT');tr('RUNNING','PENDING','PUBLISH_SETTLED_CONTINUATION','RETRY_SETTLED');tr('RUNNING','COMPLETED','COMPLETE_SETTLED');tr('RUNNING','FAILED','FAIL_SETTLED');tr('RUNNING','CANCELLED','CANCEL_SETTLED');tr('RUNNING','SUPERSEDED','RETIRE_SETTLED')
tr('WAITING_DEPENDENCY','PENDING','WAKE');tr('WAITING_DEPENDENCY','FAILED','STOP_NO_PROGRESS','DEPENDENCY_UNRECOVERABLE');tr('WAITING_DEPENDENCY','CANCELLED','CANCEL_WAIT');tr('WAITING_DEPENDENCY','SUPERSEDED','RETIRE_WAIT');tr('FAILED','PENDING','EXPLICIT_RETRY');tr('FAILED','SUPERSEDED','EXPLICIT_RETIRE');tr('CANCELLED','SUPERSEDED','EXPLICIT_RETIRE')
outcomes=[
 {'outcome':'SUPPORT_FOR_FALSIFICATION','tool':'submit_investigation','artifact':'INVESTIGATION_ARGUMENT','candidate':'READY_FOR_FALSIFICATION','task_after_settlement':'COMPLETED','successor':'FALSIFICATION','completion':'REQUIRED_SUCCESSOR'},
 {'outcome':'DISMISS_WITH_EVIDENCE','tool':'submit_investigation','artifact':'INVESTIGATION_DISPOSITION','candidate':'DISMISSED','task_after_settlement':'COMPLETED','successor':'NONE','completion':'DISPOSED'},
 {'outcome':'INCONCLUSIVE','tool':'submit_investigation','artifact':'INVESTIGATION_DISPOSITION','candidate':'INCONCLUSIVE','task_after_settlement':'COMPLETED','successor':'NONE','completion':'LIMITATION'},
 {'outcome':'NEED_CONTEXT','tool':'record_investigation_progress','artifact':'INVESTIGATION_PROGRESS','candidate':'NEEDS_CONTEXT','task_after_settlement':'WAITING_DEPENDENCY_OR_PENDING','successor':'CONTEXT_PRODUCERS','completion':'REQUIRED_OPEN'}]
M={'contract':'state-v1','task_states':STATE['enum'],'task_kinds':TASK['enum'],'task_transitions':transitions,'review_states':['CREATED','INDEXING','ANALYZING','COMPLETE','COMPLETE_WITH_LIMITATIONS','FAILED','CANCELLED'],'review_transitions':{'CREATED':['INDEXING','CANCELLED'],'INDEXING':['ANALYZING','FAILED','CANCELLED'],'ANALYZING':['COMPLETE','COMPLETE_WITH_LIMITATIONS','FAILED','CANCELLED'],'COMPLETE':[],'COMPLETE_WITH_LIMITATIONS':[],'FAILED':[],'CANCELLED':[]},'investigation_outcomes':outcomes,'runtime_mode':'collaborative-v1','historical_mode':'READ_ONLY'}
M['agent_states']=['CREATED','RUNNING','WAITING_FOR_TOOL','COMPLETED','INVALID_OUTPUT','TIMED_OUT','REFUSED','FAILED','CANCELLED']
M['agent_transitions']={'CREATED':['RUNNING','TIMED_OUT','FAILED','CANCELLED'], 'RUNNING':['WAITING_FOR_TOOL','COMPLETED','INVALID_OUTPUT','TIMED_OUT','REFUSED','FAILED','CANCELLED'], 'WAITING_FOR_TOOL':['RUNNING','COMPLETED','INVALID_OUTPUT','TIMED_OUT','REFUSED','FAILED','CANCELLED'], 'COMPLETED':[], 'INVALID_OUTPUT':[], 'TIMED_OUT':[], 'REFUSED':[], 'FAILED':[], 'CANCELLED':[]}
M['yield_intent_transitions']={'PREPARED':['SETTLING','BLOCKED'], 'SETTLING':['PUBLISHED','CANCELLED','BLOCKED'], 'BLOCKED':['SETTLING','CANCELLED'], 'PUBLISHED':[], 'CANCELLED':[]}
M['falsification_outcomes']=[{'outcome':'UPHELD','candidate_after_host_gate':'CONFIRMED','task_after_settlement':'COMPLETED','successor':'NONE','completion':'DISPOSED'}, {'outcome':'REFUTED','candidate_after_host_gate':'REFUTED','task_after_settlement':'COMPLETED','successor':'NONE','completion':'DISPOSED'}, {'outcome':'INCONCLUSIVE','candidate_after_host_gate':'INCONCLUSIVE','task_after_settlement':'COMPLETED','successor':'NONE','completion':'LIMITATION'}]
(ROOT/'contracts/schemas/state-transitions.json').write_text(json.dumps(M,indent=2)+'\n')
# This generated .pyi is the exact type/field/signature declaration, not an implementation.
def annotation(s):
 if '$ref' in s:return s['$ref'].rsplit('/',1)[-1]
 if 'anyOf' in s:return ' | '.join(annotation(x) for x in s['anyOf'])
 if 'oneOf' in s:return ' | '.join(annotation(x) for x in s['oneOf'])
 if 'const' in s:return 'Literal['+repr(s['const'])+']'
 if 'enum' in s:return 'Literal['+', '.join(repr(x) for x in s['enum'])+']'
 t=s.get('type');return {'string':'str','integer':'int','boolean':'bool','null':'None'}.get(t,'tuple['+annotation(s['items'])+', ...]' if t=='array' else 'object')
lines=['# Generated by tools/build_hardening_schemas.py. Do not edit independently.','from dataclasses import dataclass','from typing import Literal','from ssr.application import CommandContext, SSRConfig, SchedulingAdmissionToken','from ssr.query.context import ProjectQueryContext','']
for n,s in D.items():
 lines.extend(['@dataclass(frozen=True, slots=True, kw_only=True)',f'class {n}:'])
 lines.extend('    '+k+': '+annotation(v) for k,v in s['properties'].items());lines.append('')
for cls in ['CollaborativeReviewService','CollaborativeQueryService']:
 lines.append(f'class {cls}:');lines.append('    def __init__(self'+(', config: SSRConfig' if cls=='CollaborativeReviewService' else '')+') -> None: ...')
 for cl,n,params,ret in methods:
  if cl!=cls:continue
  p=['self'];kw=False
  for name,typ,kind,default in params:
   if kind=='KEYWORD_ONLY' and not kw:p.append('*');kw=True
   p.append(name+': '+typ+(' = '+default if default is not None else ''))
  lines.append('    def '+n+'('+', '.join(p)+') -> '+ret+': ...')
 lines.append('')
lines.extend(['class CollaborativeServiceError(RuntimeError):','    error: Error','    def __init__(self, error: Error) -> None: ...',''])
(ROOT/'contracts/reference/public-api.pyi').write_text('\n'.join(lines))

# Compose executable tool schemas locally; internal refs are rebased, never fetched remotely.
base_path=ROOT/'contracts/schemas/tool-inputs.schema.json'
base=json.loads(base_path.read_text())
base['$defs']={k:v for k,v in base['$defs'].items() if not k.startswith('h_')}
def rebase(value):
 if isinstance(value,dict):return {k:('#/$defs/h_'+v.rsplit('/',1)[-1] if k=='$ref' and isinstance(v,str) and v.startswith('#/$defs/') else rebase(v)) for k,v in value.items()}
 if isinstance(value,list):return [rebase(x) for x in value]
 return value
for name,definition in D.items():base['$defs']['h_'+name]=rebase(definition)
new_tools={'publish_context_answer':'ContextAnswer','submit_focused_analysis':'FocusedResult','submit_context_review':'ContextResult','record_investigation_progress':'InvestigationProgress','stage_file_synthesis':'SynthesisStage','submit_file_synthesis':'SynthesisSeal'}
for tool,name in new_tools.items():base['$defs'][tool]={'$ref':'#/$defs/h_'+name}
base['$defs']['yield_work']['properties']['request_ids']['maxItems']=8
existing=[x['properties']['tool']['const'] for x in base['oneOf']]
for tool in new_tools:
 if tool not in existing:
  base['oneOf'].append(obj(tool={'const':tool},arguments={'$ref':'#/$defs/'+tool}))
base['description']='Exact collaborative-v1 tool inputs. Generated hardening roles/proofs use local closed definitions; full host byte, ownership and semantic validation still applies.'
base_path.write_text(json.dumps(base,indent=2,ensure_ascii=False)+'\n')
