"""Run specification checks, not the future harness integration suite."""
from pathlib import Path
import importlib.util,json,sys,uuid,random
from jsonschema import Draft202012Validator
from pydantic import ValidationError
HERE=Path(__file__).resolve().parent
MODEL_PATH=HERE.parent/'contracts/v1/models.py'
spec=importlib.util.spec_from_file_location('stage1_contracts',MODEL_PATH)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
from reference_paging import Subject,compact,decode,encode
checks=[]
def check(name, fn):
    fn();checks.append(name)
def expect_bad(cls, payload):
    try:cls.model_validate(payload)
    except ValidationError:return
    raise AssertionError(f'{cls.__name__} unexpectedly accepted invalid input')
I=[str(uuid.UUID(int=i)) for i in range(1,8)]
for cls in m.PUBLIC_MODELS:
    check('schema:'+cls.__name__,lambda cls=cls:Draft202012Validator.check_schema(cls.model_json_schema()))
base=dict(index_run_id=I[0],pattern='*command*',mode='wildcard')
for limit in [1,50,200]:
    check('valid-limit:'+str(limit),lambda limit=limit:m.FunctionSearchRequest.model_validate({**base,'limit':limit}))
for limit in [0,-1,201,True,50.0,'50']:
    check('invalid-limit:'+repr(limit),lambda limit=limit:expect_bad(m.FunctionSearchRequest,{**base,'limit':limit}))
for delta in [{'mode':'exact'},{'case_sensitive':'false'},{'qualified':True},{'index_run_id':'fn_42'}]:
    check('invalid-search:'+str(delta),lambda delta=delta:expect_bad(m.FunctionSearchRequest,{**base,**delta}))
check('bad-byte-range',lambda:expect_bad(m.ByteRange,dict(start_byte=50,end_byte=49)))
check('bad-line-range',lambda:expect_bad(m.ReadFileRequest,dict(index_run_id=I[0],path='a.py',start_line=5,end_line=4)))
check('bad-coverage-count',lambda:expect_bad(m.StepCoverage,dict(total_files=3,completed_files=3,failed_files=1)))
zero=dict(total_files=0,completed_files=0,failed_files=0)
partial=dict(index_complete=False,extraction=dict(total_files=100,completed_files=9,failed_files=0),resolution=zero,flagging=zero)
late={**partial,'extraction':dict(total_files=100,completed_files=100,failed_files=0)}
check('bad-complete-coverage',lambda:expect_bad(m.Coverage,{**partial,'index_complete':True}))
check('singular-error-rejected',lambda:expect_bad(m.ErrorResponse,{'error':{}}))
check('empty-error-rejected',lambda:expect_bad(m.ErrorResponse,{'errors':[]}))
check('empty-name-categories-rejected',lambda:expect_bad(m.NameRule,dict(id='x',mode='wildcard',pattern='*',case_sensitive=True,categories=[],reason='x')))

def paging_case(text,budget):
    subject=Subject(text.encode('utf-8'),'src/测试.cpp',*I[:5])
    page=subject.initial(budget,partial);m.SourcePage.model_validate(page)
    output=page['source'];previous_end=page['range']['end_byte'];tokens=[]
    while page['next_continuation']:
        token=page['next_continuation'];tokens.append(token)
        original=subject.continuation(token,partial);replay=subject.continuation(token,late)
        assert original['source']==replay['source'] and original['range']==replay['range']
        assert replay['range']['start_byte']==previous_end
        assert len(compact(replay))<=budget
        m.SourcePage.model_validate(replay);m.SourceToken.model_validate(decode(token))
        page=replay;previous_end=page['range']['end_byte'];output+=page['source']
        assert len(tokens)<len(subject.data)+1
    assert output==text and previous_end==len(subject.data)
    if tokens:
        payload=decode(tokens[0]);payload['snapshot_id']=I[6]
        try:subject.continuation(encode(payload),late)
        except ValueError:pass
        else:raise AssertionError('mismatched snapshot accepted')

samples=['','a\n','\ufeffdef x():\r\n    return "猫"\r\n',('x'*10000)+'\n',('"\\\t\x01🙂猫\r\n')*2000]
for n,text in enumerate(samples):
    for budget in [2500,5000,50000]:
        check(f'paging:{n}:{budget}',lambda text=text,budget=budget:paging_case(text,budget))
rng=random.Random(41)
for n in range(10):
    text=''.join(rng.choice(['a','猫','🙂','\\','"','\t','\n','\r\n']) for _ in range(1000))
    check(f'paging-random:{n}',lambda text=text:paging_case(text,3000))
subject=Subject(b'large source','a.py',*I[:5])
def tiny():
    try:subject.initial(1,partial)
    except ValueError as e:assert str(e)=='RESPONSE_BUDGET_TOO_SMALL'
    else:raise AssertionError('tiny budget accepted')
check('tiny-budget-is-not-pagination',tiny)
def accepted_minimum():
    minimum=subject.minimum(1,partial)
    page=subject.initial(minimum,partial)
    assert page['range']['end_byte']>0
check('calculated-minimum-is-sufficient',accepted_minimum)
check('boolean-token-version-rejected',lambda:expect_bad(m.SourceToken,{**subject.payload(0,1,50000),'v':True}))

# Validate task DAG and approved requirement coverage.
root=HERE.parent
tasks=json.loads((root/'implementation/tasks.json').read_text())['tasks']
seen=set()
for t in tasks:
    assert all(d in seen for d in t['depends_on']), t
    assert (root/'implementation'/t['file']).is_file()
    seen.add(t['id'])
check('task-dag',lambda:None)
trace=json.loads((root/'TRACEABILITY.json').read_text())['requirements']
assert len(trace)==83 and all(set(ts)<=seen for ts in trace.values())
check('approved-requirement-mapping',lambda:None)
# Structural package checks do not execute Semgrep or database statements.
import yaml, re, tomllib, ast, posixpath
name_data=yaml.safe_load((root/'contracts/v1/builtin-names.yaml').read_text())
check('builtin-name-contract',lambda:m.NameRules.model_validate(name_data))
name_rules=name_data['rules']
assert len({x['id'] for x in name_rules})==len(name_rules)
check('builtin-name-identities',lambda:None)
scanner=yaml.safe_load((root/'contracts/v1/builtin-semgrep.yaml').read_text())['rules']
fixtures=json.loads((root/'contracts/v1/rule-fixtures.json').read_text())['fixtures']
assert len({x['id'] for x in scanner})==len(scanner)
assert {x['id'] for x in scanner}=={x['rule_id'] for x in fixtures}
assert all(x['positive'] and x['negative'] and x['positive']!=x['negative'] for x in fixtures)
check('scanner-fixture-accounting-only',lambda:None)
check('defaults-toml',lambda:tomllib.loads((root/'contracts/v1/defaults.toml').read_text()))
for py in [root/'contracts/v1/models.py', HERE/'reference_paging.py', HERE/'export_schemas.py', HERE/'check_contracts.py']:
    check('python-syntax:'+py.name,lambda py=py:ast.parse(py.read_text()))
# Links to inherited documents are checked against the connector-read baseline manifest.
baseline={'requirements/'+x for x in ['source-intake.md','indexing-progress.md','function-records.md','reference-records.md','flag-records.md','source-retrieval.md','tool-errors.md','live-pagination.md']}
baseline|={'contracts/function-search.md','contracts/source-reading.md'}
for md in root.rglob('*.md'):
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',md.read_text()):
        if '://' in target or target.startswith('#'):continue
        target=target.split('#')[0]
        resolved=posixpath.normpath(str(md.parent.relative_to(root)/target))
        assert (root/resolved).exists() or resolved in baseline, (md,target,resolved)
check('relative-links-with-baseline',lambda:None)
result={'checks_passed':len(checks),'checks':checks,'python':sys.version.split()[0],
        'scope':'schema/model, pure UTF-8 paging reference, and package-structure checks only; no harness/SQL/parser/scanner integration executed',
        'name_rules':len(name_rules),'semgrep_rules':len(scanner),'semgrep_fixtures':len(fixtures),
        'requirements_mapped':len(trace),'ordered_tasks':len(tasks)}
(HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
