"""Contract fixtures and state models only. No ssr runtime/target/provider imports."""
from __future__ import annotations
import ast
import copy
import itertools
import json
from pathlib import Path
import sqlite3
import unittest
from jsonschema import Draft202012Validator, ValidationError
from contract_reference import *
SCHEMA=json.loads((ROOT/'contracts/schemas/hardening-v1.schema.json').read_text())
MACHINE=json.loads((ROOT/'contracts/schemas/state-transitions.json').read_text())

def validator(name):return Draft202012Validator({**SCHEMA,'$ref':'#/$defs/'+name})

def minimal(schema):
    if '$ref' in schema:return minimal(SCHEMA['$defs'][schema['$ref'].split('/')[-1]])
    if 'const' in schema:return schema['const']
    if 'enum' in schema:return schema['enum'][0]
    if 'anyOf' in schema:return None if any(x.get('type')=='null' for x in schema['anyOf']) else minimal(schema['anyOf'][0])
    if 'oneOf' in schema:return minimal(schema['oneOf'][0])
    t=schema.get('type')
    if t=='object':
        result={k:minimal(v) for k,v in schema['properties'].items()}
        if result.get('state')=='EXACT' and 'canonical_api' in result:result['canonical_api']='python:subprocess.run'
        return result
    if t=='array':
        if schema.get('uniqueItems') and 'enum' in schema['items']:return schema['items']['enum'][:schema.get('minItems',0)]
        return [minimal(schema['items']) for _ in range(schema.get('minItems',0))]
    if t=='integer':return schema.get('minimum',0)
    if t=='boolean':return False
    if t=='null':return None
    if t=='string':
        if 'pattern' in schema:return '0'*64 if '64' in schema['pattern'] else '2026-09-09T00:00:00.000Z'
        return 'x'*max(1,schema.get('minLength',0))
    raise ValueError(schema)

class ContextPolicyTests(unittest.TestCase):
    def test_170k_exact_values(self):
        l=context_limits();self.assertEqual(l['max_input'],149520);self.assertEqual(l['checkpoint_at'],127092)
    def test_limit_and_oversize(self):
        for n in [149521,365000]:
            with self.subTest(n=n),self.assertRaises(ContractError):admit_context(n,context_limits(),'a','a')
        self.assertEqual(admit_context(149520,context_limits(),'a','a'),'CHECKPOINT')
    def test_smaller_route(self):self.assertEqual(context_limits(verified=128000)['max_input'],107520)
    def test_changed_request_and_unknown_counter(self):
        for args in [(None,'a','a'),(100,'a','b')]:
            with self.subTest(args=args),self.assertRaises(ContractError):admit_context(args[0],context_limits(),args[1],args[2])
    def test_schema_overhead(self):
        with self.assertRaises(ContractError):admit_context(140000+10000,context_limits(),'a','a')
    def test_dossier_limits(self):
        for args in [(8193,b'a',1,1),(100,b'a'*32769,1,1),(100,b'a',4097,1),(100,b'a',1,16385)]:
            with self.subTest(args=args[:1]),self.assertRaises(ContractError):validate_dossier(*args)
    def test_invalid_bounds(self):
        for n in [True,0,-1]:
            with self.subTest(n=n),self.assertRaises(ContractError):context_limits(configured=n)

class YieldTests(unittest.TestCase):
    def test_prepared_not_claimable(self):
        m=YieldModel();m.prepare();self.assertFalse(m.claim());self.assertEqual(m.attempt,1)
        with self.assertRaises(ContractError):m.publish()
    def test_answer_interleavings(self):
        # settle precedes publication; answer may arrive on either side of both.
        for order in [('answer','settle','publish'),('settle','answer','publish'),('settle','publish','answer')]:
            m=YieldModel();m.prepare()
            for event in order:
                if event=='answer':m.publish_answer()
                else:getattr(m,event)()
                if not m.publications:self.assertFalse(m.claim())
            self.assertEqual(m.state,'PENDING');self.assertTrue(m.claim());self.assertEqual(m.attempt,2)
    def test_cancel_during_settlement(self):
        m=YieldModel();m.prepare();m.cancelled=True;m.publish_answer();m.settle();m.publish();self.assertEqual(m.state,'CANCELLED');self.assertFalse(m.claim())
    def test_missing_receipts(self):
        for kwargs in [{'runtime':False},{'transcript':False}]:
            m=YieldModel();m.prepare()
            with self.assertRaises(ContractError):m.settle(**kwargs)
            self.assertFalse(m.claim())
    def test_replay(self):
        m=YieldModel();m.prepare();m.prepare();self.assertEqual(m.generation,1);m.settle();m.publish();m.publish();self.assertEqual(m.publications,1)
    def test_transition_matrix_total(self):
        allowed={(r['from'],r['to']):r['guards'] for r in MACHINE['task_transitions']}
        self.assertEqual(len(allowed),len(MACHINE['task_transitions']))
        for a,b in itertools.product(MACHINE['task_states'],repeat=2):
            with self.subTest(a=a,b=b):
                if a in ['COMPLETED','SKIPPED','SUPERSEDED']:self.assertNotIn((a,b),allowed)
                if (a,b) in allowed:self.assertTrue(allowed[a,b])
    def test_outcomes_complete(self):
        rows={r['outcome']:r for r in MACHINE['investigation_outcomes']}
        self.assertEqual(set(rows),{'SUPPORT_FOR_FALSIFICATION','DISMISS_WITH_EVIDENCE','NEED_CONTEXT','INCONCLUSIVE'})
        self.assertEqual(rows['INCONCLUSIVE']['completion'],'LIMITATION');self.assertEqual(rows['DISMISS_WITH_EVIDENCE']['successor'],'NONE');self.assertEqual(rows['NEED_CONTEXT']['tool'],'record_investigation_progress')
    def test_sql_claim_barrier(self):
        # A miniature SQL contract fixture, not the production claim query.
        db=sqlite3.connect(':memory:');db.executescript('CREATE TABLE tasks(id TEXT PRIMARY KEY,state TEXT,settled INT); CREATE TABLE yields(task TEXT PRIMARY KEY,published INT); INSERT INTO tasks VALUES("A","RUNNING",0); INSERT INTO yields VALUES("A",0);')
        q='SELECT id FROM tasks WHERE state="PENDING" AND settled=1 AND NOT EXISTS(SELECT 1 FROM yields WHERE task=tasks.id AND published=0)'
        self.assertEqual(db.execute(q).fetchall(),[])
        db.execute('UPDATE tasks SET state="PENDING"') # Deliberately corrupt early requeue.
        self.assertEqual(db.execute(q).fetchall(),[])
        db.execute('UPDATE tasks SET settled=1');self.assertEqual(db.execute(q).fetchall(),[])
        db.execute('UPDATE yields SET published=1');self.assertEqual(db.execute(q).fetchall(),[('A',)])
        db.close()

class PrefixTests(unittest.TestCase):
    def fixture(self,mode='OFF'):
        identity={'review_run_id':'r','snapshot_id':'s','task_id':'t','agent_run_id':'a','attempt_number':1,'control_generation':1}
        calls=[{'call_id':'c','call_ordinal':0,'tool_name':'report_lead','arguments_hash':'a'*64}]
        req=minimal(SCHEMA['$defs']['RequestEvent']);req.update(sequence=1,request_id='q',request_hash='2'*64,input_revision_hash='1'*64,delivery_manifest_hash='4'*64)
        res=minimal(SCHEMA['$defs']['ResponseEvent']);res.update(sequence=2,complete=True,origin_calls=calls,request_id='q',response_id='z',request_hash='2'*64,response_hash='3'*64)
        validator('RequestEvent').validate(req);validator('ResponseEvent').validate(res)
        events=[req,res]
        genesis=digest('ssr.runtime-genesis.v2',{'identity':identity,'execution_contract_hash':'5'*64})
        body={'contract':'runtime-prefix-v1','identity':identity,'execution_contract_hash':'5'*64,'input_revision_hash':'1'*64,'request_id':'q','response_id':'z','request_hash':'2'*64,'response_hash':'3'*64,'end_event_sequence':2,'event_chain_hash':chain('ssr.runtime-event.v2',genesis,events)[-1],'parent_prefix_hash':None,'delivery_manifest_hash':'4'*64,'origin_calls':calls,'transcript':{'mode':mode,'disposition':'DISABLED' if mode=='OFF' else 'OPTIONAL_UNAVAILABLE','prefix_id':None,'prefix_hash':None}}
        binding=minimal(SCHEMA['$defs']['RequestBinding']);binding.update(identity=identity,request_id='q',delivery_manifest_hash='4'*64,input_revision_hash='1'*64,request_hash='2'*64,status='OBSERVED',response_id='z',response_hash='3'*64);validator('RequestBinding').validate(binding)
        return body,events,genesis,binding
    def test_valid_and_future_append(self):
        b,e,g,i=self.fixture();validator('RuntimePrefix').validate(b);first=prefix_hash(b,e,g,i,None)
        e.append({'sequence':3,'kind':'TOOL_EFFECT'})
        self.assertEqual(prefix_hash(b,e,g,i,None),first)
    def test_tampering_gap_and_truncation(self):
        for kind in ['hash','gap','incomplete','calls']:
            b,e,g,i=self.fixture()
            if kind=='hash':e[0]['changed']=True
            if kind=='gap':e[1]['sequence']=3
            if kind=='incomplete':e[1]['complete']=False
            if kind=='calls':b['origin_calls']=[]
            with self.subTest(kind=kind),self.assertRaises(ContractError):prefix_hash(b,e,g,i,None)
    def test_input_binding(self):
        for change in ['input_revision_hash','status']:
            b,e,g,i=self.fixture();i[change]='PREPARED' if change=='status' else '0'*64
            with self.subTest(change=change),self.assertRaises(ContractError):prefix_hash(b,e,g,i,None)
    def test_required_capture(self):
        b,e,g,i=self.fixture('REQUIRED')
        with self.assertRaises(ContractError):prefix_hash(b,e,g,i,None)
    def test_optional_capture(self):
        b,e,g,i=self.fixture('OPTIONAL');self.assertEqual(len(prefix_hash(b,e,g,i,None)),64)
    def test_wrong_identity_exchange_and_delivery(self):
        for field,value in [('identity',{}),('request_id','wrong'),('delivery_manifest_hash','9'*64),('response_id','wrong'),('execution_contract_hash','9'*64)]:
            b,e,g,i=self.fixture();b[field]=value
            with self.subTest(field=field),self.assertRaises(ContractError):prefix_hash(b,e,g,i,None)
    def test_valid_required_transcript_and_wrong_capture(self):
        b,e,g,i=self.fixture('REQUIRED');t=minimal(SCHEMA['$defs']['TranscriptPrefix'])
        t.update(identity=b['identity'],execution_contract_hash=b['execution_contract_hash'],request_id=b['request_id'],response_id=b['response_id'],request_hash=b['request_hash'],response_hash=b['response_hash'])
        h=digest('ssr.transcript-prefix.v1',t);b['transcript'].update(disposition='VERIFIED',prefix_id='tp1:'+h,prefix_hash=h)
        self.assertEqual(len(prefix_hash(b,e,g,i,t)),64)
        t['response_id']='other'
        with self.assertRaises(ContractError):prefix_hash(b,e,g,i,t)
    def test_parent_chain_extension(self):
        b,e,g,i=self.fixture();first=copy.deepcopy(b)
        e += [{'sequence':3,'kind':'TOOL_EFFECT'},{**e[0],'sequence':4},{**e[1],'sequence':5}]
        b.update(end_event_sequence=5,event_chain_hash=chain('ssr.runtime-event.v2',g,e)[-1],parent_prefix_hash=digest('ssr.runtime-prefix.v1',first))
        self.assertEqual(len(prefix_hash(b,e,g,i,None,first)),64)
        first['event_chain_hash']='9'*64
        with self.assertRaises(ContractError):prefix_hash(b,e,g,i,None,first)
    def test_canonical(self):
        self.assertEqual(canonical({'b':2,'a':1}),canonical({'a':1,'b':2}))
        with self.assertRaises(ContractError):canonical({'x':1.5})

class SynthesisTests(unittest.TestCase):
    def decision(self,key):return {'kind':'DECISION','key':key,'action':'RETAIN','origin_set_key':None,'evidence_set_key':None,'rationale':'Checked against the exact manifest.','supersedes_digest':None}
    def stage(self,m,entries):return {'contract':'synthesis-stage-v1','input_token':'i','session_id':m.session_id,'manifest_hash':m.manifest_hash,'expected_revision':m.revision,'entries':entries}
    def seal(self,m):return {'contract':'synthesis-seal-v1','input_token':'i','session_id':m.session_id,'manifest_hash':m.manifest_hash,'expected_revision':m.revision,'journal_hash':m.root}
    def test_ten_thousand_required_decisions(self):
        keys=[f'unit:{i}' for i in range(10000)];m=SynthesisModel({'required_keys':keys})
        for n in range(0,len(keys),32):
            c=self.stage(m,[self.decision(k) for k in keys[n:n+32]]);self.assertLessEqual(len(canonical(c)),65536);m.stage(c)
        seal=self.seal(m);self.assertLess(len(canonical(seal)),8192);self.assertEqual(m.seal(seal),m.root)
    def test_maximum_seal_is_bounded(self):
        v={'contract':'synthesis-seal-v1','input_token':'i'*4096,'session_id':'s'*200,'manifest_hash':'a'*64,'expected_revision':9007199254740991,'journal_hash':'b'*64}
        validator('SynthesisSeal').validate(v);self.assertLess(len(canonical(v)),8192)
        v['input_token']='é'*4096
        with self.assertRaises(ValidationError):validator('SynthesisSeal').validate(v)
    def test_replay_and_missing_decision(self):
        m=SynthesisModel({'required_keys':['a','b']});c=self.stage(m,[self.decision('a')]);r=m.stage(c)
        with self.assertRaises(ContractError):m.seal(self.seal(m))
        m.stage(self.stage(m,[self.decision('b')]));self.assertEqual(m.stage(c),r);self.assertEqual(m.revision,2)
    def test_wrong_manifest_and_stale_generation(self):
        m=SynthesisModel({'required_keys':['a']});c=self.stage(m,[self.decision('a')]);c['manifest_hash']='f'*64
        with self.assertRaises(ContractError):m.stage(c)
        self.assertEqual(m.revision,0)
    def test_reconciliation_correction(self):
        m=SynthesisModel({'required_keys':['a']});m.stage(self.stage(m,[self.decision('a')]))
        c=self.decision('a');c['action']='UNRESOLVED'
        with self.assertRaises(ContractError):m.stage(self.stage(m,[c]))
        c['supersedes_digest']=m.decisions['a']['digest'];m.stage(self.stage(m,[c]));self.assertEqual(m.revision,2)
    def test_reference_pages(self):
        m=SynthesisModel({'required_keys':['a']});d=self.decision('a');d['evidence_set_key']='set1';m.stage(self.stage(m,[d]))
        with self.assertRaises(ContractError):m.seal(self.seal(m))
        e={'kind':'REFERENCE_SET_PAGE','set_key':'set1','page_index':0,'references':[{'kind':'EVIDENCE','id':'e'}],'final_page':False};m.stage(self.stage(m,[e]))
        with self.assertRaises(ContractError):m.seal(self.seal(m))
        e={**e,'page_index':1,'final_page':True};m.stage(self.stage(m,[e]));m.seal(self.seal(m))
    def test_invalid_receipt_or_material(self):
        m=SynthesisModel({'required_keys':['a']});m.stage(self.stage(m,[self.decision('a')]))
        for k in ['materials_current','receipts_valid']:
            with self.subTest(k=k),self.assertRaises(ContractError):m.seal(self.seal(m),**{k:False})
    def test_atomic_stage_rejection(self):
        m=SynthesisModel({'required_keys':['a']});root=m.root
        with self.assertRaises(ContractError):m.stage(self.stage(m,[self.decision('a'),self.decision('unknown')]))
        self.assertEqual(m.root,root);self.assertFalse(m.decisions)

class SchemaTests(unittest.TestCase):
    def test_all_closed_definitions_and_required_fields(self):
        for n,s in SCHEMA['$defs'].items():
            with self.subTest(n=n):
                self.assertFalse(s['additionalProperties']);self.assertEqual(list(s['properties']),s['x-python-field-order'])
                value=minimal(s)
                if n=='FocusedResult':value['registered_lead_ids']=['lead-1']
                if n=='CallBinding':value['canonical_api']='python:subprocess.run'
                validator(n).validate(value)
                with self.assertRaises(ValidationError):validator(n).validate({**value,'unexpected':True})
                for fieldname in s['required']:
                    v=dict(value);del v[fieldname]
                    self.assertTrue(list(validator(n).iter_errors(v)),(n,fieldname))
    def test_focus_outcome_requirements(self):
        v=minimal(SCHEMA['$defs']['FocusedResult']);v['disposition']='INCONCLUSIVE'
        self.assertTrue(list(validator('FocusedResult').iter_errors(v)))
    def test_dto_signature_manifest(self):
        abi=json.loads((ROOT/'contracts/schemas/sdk-abi.json').read_text());tree=ast.parse((ROOT/'contracts/reference/public-api.pyi').read_text())
        classes={c.name:c for c in tree.body if isinstance(c,ast.ClassDef)}
        for name,fields in abi['dto_field_order'].items():self.assertEqual([n.target.id for n in classes[name].body if isinstance(n,ast.AnnAssign)],fields)
        for method in abi['methods']:
            f=next(n for n in classes[method['class']].body if isinstance(n,ast.FunctionDef) and n.name==method['name'])
            self.assertEqual([a.arg for a in f.args.args][1:],[p['name'] for p in method['parameters'] if p['kind']=='POSITIONAL_OR_KEYWORD'])
            self.assertEqual([a.arg for a in f.args.kwonlyargs],[p['name'] for p in method['parameters'] if p['kind']=='KEYWORD_ONLY'])
            self.assertEqual(ast.unparse(f.returns),method['return_annotation'])
    def test_integer_not_bool_and_enum_closed(self):
        v={'cursor':None,'limit':True};self.assertTrue(list(validator('PageRequest').iter_errors(v)))
        v=minimal(SCHEMA['$defs']['ContextResult']);v['disposition']='SOMETHING_NEW';self.assertTrue(list(validator('ContextResult').iter_errors(v)))

class CallsitePilotTests(unittest.TestCase):
    def test_alias_and_from_import(self):
        for source in ['import subprocess as ps\nps.run(a,shell=True)','from subprocess import run as launch\nlaunch(a,shell=False)']:
            r=python_calls(source);self.assertEqual(r[0]['state'],'EXACT');self.assertIn(r[0]['shell'],[True,False])
    def test_shadow(self):
        for source in ['import subprocess as ps\ndef f(ps):\n ps.run(a)','import subprocess as ps\ndef f():\n ps.run(a)\n ps = other','import subprocess as ps\ndef f():\n import other as ps\n ps.run(a)','import subprocess as ps\nps=other\nps.run(a)']:
            self.assertEqual(python_calls(source)[0]['state'],'UNRESOLVED')
    def test_unknown_execute_and_dynamic_shell(self):
        self.assertEqual(python_calls('obj.execute(x)')[0]['state'],'UNRESOLVED')
        self.assertIsNone(python_calls('import subprocess\nsubprocess.run(x,shell=flag)')[0]['shell'])
    def test_unicode_and_same_line(self):
        source='import subprocess as ps\nlabel="é"; ps.run(a); ps.run(b)';r=python_calls(source);raw=source.encode()
        self.assertEqual(len(r),2);self.assertEqual(raw[r[0]['start_byte']:r[0]['end_byte']],b'ps.run(a)');self.assertNotEqual(r[0]['start_byte'],r[1]['start_byte'])
    def test_parser_error_and_star(self):
        self.assertEqual(python_calls('if (')[0]['state'],'ERROR')
        self.assertEqual(python_calls('import subprocess as ps\nfrom other import *\nps.run(a)')[0]['state'],'UNRESOLVED')

class FullIRTests(unittest.TestCase):
    def test_full_ir_schema_and_original_ranges(self):
        source='import subprocess as ps\nps.run(arg, shell=True)'
        batch=python_ir(source);validator('CallsiteBatch').validate(batch)
        call=batch['calls'][0];self.assertEqual(call['binding']['state'],'EXACT')
        self.assertEqual(call['arguments'][1]['keyword'],'shell');self.assertTrue(call['arguments'][1]['constant_bool'])
        self.assertEqual(source.encode()[call['range']['start_byte']:call['range']['end_byte']],b'ps.run(arg, shell=True)')
    def test_module_owner_and_explicit_existing_symbol(self):
        source='import subprocess as ps\ndef f():\n return ps.run(arg)'
        a=python_ir(source);b=python_ir(source,(('symbol-f',24,len(source.encode())),))
        self.assertIsNone(a['calls'][0]['containing_symbol_id']);self.assertEqual(b['calls'][0]['containing_symbol_id'],'symbol-f')
    def test_deterministic_identity_and_shadowed_shape(self):
        source='import subprocess as ps\ndef f(ps):\n return ps.run(arg)'
        a=python_ir(source);self.assertEqual(a,python_ir(source));validator('CallsiteBatch').validate(a)
        self.assertEqual(a['calls'][0]['binding']['state'],'UNRESOLVED');self.assertIsNone(a['calls'][0]['binding']['canonical_api'])
    def test_argument_overflow_visible(self):
        source='import subprocess as ps\nps.run('+','.join('x' for _ in range(257))+')'
        a=python_ir(source);validator('CallsiteBatch').validate(a)
        self.assertEqual(a['status'],'PARTIAL');self.assertFalse(a['calls'][0]['arguments_complete'])
    def test_error_is_not_empty_success(self):
        a=python_ir('if (');validator('CallsiteBatch').validate(a);self.assertEqual(a['status'],'ERROR')

class InputAndRoleTests(unittest.TestCase):
    def fixture(self):
        identity={'review_run_id':'r','snapshot_id':'s','task_id':'t','agent_run_id':'a','attempt_number':1,'control_generation':1}
        p={'contract':'input-token-v1','key_id':'key','identity':identity,'revision_id':'in1','revision_hash':'1'*64,'required_delta_manifest_hash':'2'*64}
        token=input_token(p,b'x'*32);binding={'observed':True,'token_hash':hashlib.sha256(token.encode()).hexdigest(),'revision_hash':'1'*64,'required_delta_manifest_hash':'2'*64}
        return identity,p,token,binding
    def test_valid_token(self):
        i,p,t,b=self.fixture();self.assertEqual(verify_input_token(t,b'x'*32,i,b),p)
    def test_token_tamper_and_other_attempt(self):
        i,p,t,b=self.fixture()
        with self.assertRaises(ContractError):verify_input_token(t,b'y'*32,i,b)
        with self.assertRaises(ContractError):verify_input_token(t,b'x'*32,{**i,'attempt_number':2},b)
    def test_unobserved_and_undelivered_delta(self):
        i,p,t,b=self.fixture()
        for update in [{'observed':False},{'required_delta_manifest_hash':'9'*64},{'token_hash':'8'*64}]:
            with self.subTest(update=update),self.assertRaises(ContractError):verify_input_token(t,b'x'*32,i,{**b,**update})
    def test_revision_ownership_changes_hash(self):
        p=minimal(SCHEMA['$defs']['InputRevision']);self.assertNotEqual(digest('ssr.input.v1',p),digest('ssr.input.v1',{**p,'task_id':'different'}))
    def test_answered_requires_all_facets(self):
        v=minimal(SCHEMA['$defs']['ContextAnswer']);v['facets'][0]['facet_id']='f';v['facets'][0]['references']=[{'kind':'EVIDENCE','id':'e'}]
        validate_context_answer(v,{'f'})
        with self.assertRaises(ContractError):validate_context_answer(v,{'f','g'})
        v['facets'][0]['status']='UNRESOLVED'
        with self.assertRaises(ContractError):validate_context_answer(v,{'f'})
    def test_contradiction_requires_evidence(self):
        v=minimal(SCHEMA['$defs']['ContextAnswer']);v['outcome']='CONTRADICTED_ASSUMPTION';v['facets'][0]['facet_id']='f';v['facets'][0]['status']='CONTRADICTED'
        with self.assertRaises(ContractError):validate_context_answer(v,{'f'})
        v['facets'][0]['references']=[{'kind':'EVIDENCE','id':'e'}];validate_context_answer(v,{'f'})

class BoundTests(unittest.TestCase):
    def fixture(self):
        db=sqlite3.connect(':memory:')
        db.executescript('CREATE TABLE quota(k TEXT PRIMARY KEY,used INTEGER NOT NULL,max INTEGER NOT NULL);CREATE TABLE ops(id TEXT PRIMARY KEY);INSERT INTO quota VALUES("root",0,1),("review",0,1);')
        return db
    def reserve(self,db,op):
        with db:
            if db.execute('SELECT 1 FROM ops WHERE id=?',(op,)).fetchone():return 'REPLAY'
            for key in ('root','review'):
                if db.execute('UPDATE quota SET used=used+1 WHERE k=? AND used<max',(key,)).rowcount!=1:raise ContractError('LIMIT_REACHED')
            db.execute('INSERT INTO ops VALUES(?)',(op,))
        return 'COMMITTED'
    def test_two_dimensions_and_exact_replay(self):
        db=self.fixture();self.assertEqual(self.reserve(db,'a'),'COMMITTED');self.assertEqual(self.reserve(db,'a'),'REPLAY')
        with self.assertRaises(ContractError):self.reserve(db,'b')
        self.assertEqual(db.execute('SELECT used FROM quota ORDER BY k').fetchall(),[(1,),(1,)]);db.close()
    def test_second_limit_rolls_back_first(self):
        db=self.fixture();db.execute('UPDATE quota SET used=1 WHERE k="review"');db.commit()
        with self.assertRaises(ContractError):self.reserve(db,'a')
        self.assertEqual(db.execute('SELECT used FROM quota WHERE k="root"').fetchone()[0],0);self.assertEqual(db.execute('SELECT COUNT(*) FROM ops').fetchone()[0],0);db.close()
    def test_no_progress_is_finite(self):
        count=0;seen=set()
        for ids in [(),(),()]:
            new=set(ids)-seen;count=0 if new else count+1;seen.update(ids)
        self.assertEqual(count,3)
        new={'accepted-answer-1'}-seen;count=0 if new else count+1;self.assertEqual(count,0)
    def test_agent_terminal_states_have_no_exits(self):
        for state in ['COMPLETED','INVALID_OUTPUT','TIMED_OUT','REFUSED','FAILED','CANCELLED']:
            self.assertEqual(MACHINE['agent_transitions'][state],[])
    def test_cutover_has_one_mode(self):
        self.assertEqual(MACHINE['runtime_mode'],'collaborative-v1');self.assertEqual(MACHINE['historical_mode'],'READ_ONLY')

class TranscriptPrefixTests(unittest.TestCase):
    def fixture(self):
        body=minimal(SCHEMA['$defs']['TranscriptPrefix']);body.update(end_record_sequence=2,record_count=2,parent_prefix_hash=None)
        genesis=digest('ssr.transcript-genesis.v2',{'identity':body['identity'],'execution_contract_hash':body['execution_contract_hash'],'capture_identity_hash':body['capture_identity_hash']})
        records=[{'sequence':1,'kind':'REQUEST','payload':'inert fixture'}, {'sequence':2,'kind':'ACCEPTED_RESPONSE','complete':True,**{k:body[k] for k in ('request_id','response_id','request_hash','response_hash')}}]
        body['total_bytes']=sum(len(canonical(r)) for r in records);body['head_hash']=chain('ssr.transcript-record.v2',genesis,records)[-1]
        return body,records,genesis
    def test_valid_prefix_remains_valid_after_append(self):
        b,r,g=self.fixture();h=transcript_prefix_hash(b,r,g);r.append({'sequence':3,'kind':'NEXT_REQUEST'});self.assertEqual(transcript_prefix_hash(b,r,g),h)
    def test_count_bytes_hash_boundary_and_identity_rejected(self):
        for field in ['record_count','total_bytes','head_hash','response_id','execution_contract_hash']:
            b,r,g=self.fixture();b[field]=99 if field in ('record_count','total_bytes') else 'changed'
            with self.subTest(field=field),self.assertRaises(ContractError):transcript_prefix_hash(b,r,g)
    def test_incomplete_capture_is_not_sealed(self):
        b,r,g=self.fixture();r[-1]['complete']=False
        with self.assertRaises(ContractError):transcript_prefix_hash(b,r,g)

if __name__=='__main__':unittest.main(verbosity=2)
