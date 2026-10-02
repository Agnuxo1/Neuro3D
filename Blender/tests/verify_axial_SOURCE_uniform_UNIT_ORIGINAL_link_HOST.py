"""Independent stdlib receipt/domain/UNIT-link oracle; no production imports."""
import ast,base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-UNIT-ORIGINAL-LINK-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-COMPLEX-PRODUCT-HOST-001-CODEX.json'
PARENT_SHA='f91e68a2fe8655827c3c1259db89a2caeffafa2ba5c0f02a4cbf4b826d59fd65'
UNIT='coordinacion/respuestas/AXIAL-GUARDED-ARGUMENT-UNIT-RN64-CPU-001-CODEX.json'
AMP='coordinacion/respuestas/AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001-CODEX.json'
MODEL='axial-SOURCE-box-fixed-geometry-UNIT-ORIGINAL-link-HOST-v1'
FLAG='SOURCE_box_UNIT_ORIGINAL_error_link_HOST_proved'
def sha(b):return hashlib.sha256(b).hexdigest()
def dig(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]
def rat(x):
    assert type(x) is list and len(x)==2 and all(type(a) is int and a.bit_length()<=4096 for a in x)
    assert x[1]>0 and math.gcd(*x)==1
    return F(*x)
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(''.join(t['stdout_zlib_base64_chunks'])))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());b=(ROOT/PARENT).read_bytes();assert sha(b)==PARENT_SHA;p=json.loads(b)
    inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert len(inherited)==453 and len(own)==4 and len(pins)==457 and r['code_doc_sha256']==pins and not set(inherited)&set(own)
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['task_id']=='AXIAL-SOURCE-UNIFORM-UNIT-ORIGINAL-LINK-HOST-001' and r['model']==MODEL and r['base_commit']=='2c21f0e47d31abbb34eaa60113c89857b8baecfd'
    run=payload(r);old=payload(p)['data'];unit=payload(json.loads((ROOT/UNIT).read_bytes()))['data']['audit'];amp=payload(json.loads((ROOT/AMP).read_bytes()))['data']
    assert run['tests']==5 and run['PASS'] is True
    t=r['test_run'];assert t['rc']==0 and not t['timed_out'] and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def noflags(x):assert all(x[k] is False for k in flags)
    def proof(x,box,charges):
        assert x['model']==MODEL and x[FLAG] is True and x['box_reim']==box
        maxima=[]
        for lo,hi in box:
            l,h=rat(lo),rat(hi);assert l<=h;maxima.append(max(abs(l),abs(h)))
        S=sum(maxima,F(0));q={n:rat(v) for n,v in charges.items()}
        assert len(q)==11 and all(v>=0 for v in q.values()) and sum(q.values(),F(0))<1
        assert x['ORIGINAL_SOURCE_component_max']==list(map(pair,maxima)) and x['ORIGINAL_SOURCE_box_norm_L1_bound']==pair(S)
        assert dig(x['fixed_UNIT_charges_to_ORIGINAL_L1'])==dig(charges)
        expected={'source_unit_'+n:pair(S*v) for n,v in q.items()}
        assert x['charges_L1']==expected and x['uniform_A_times_UNIT_error_to_A_times_ideal_UNIT_L1']==pair(S*sum(q.values(),F(0)))
        assert x['ideal_target']=='variable ORIGINAL A times exp(i fixed ORIGINAL theta); bare, before material'
        assert x['uniform_executed_SOURCE_error_L1'] is x['phase_bound_rad'] is None and x['status']=='STOP'
        assert x['frozen_guard_admission_for_entire_box_proved'] is x['uniform_SOURCE_enclosure_proved'] is False;noflags(x)
    for variant in ('real_missing','explicit_None_missing','synthetic_domains'):
        a=run['data'][variant];previous=old[variant]
        assert a['case_order']==previous['case_order'] and a['model']==MODEL and a['variant']==variant and a['inherited_pins_verified']==453
        valid=variant=='synthetic_domains';assert a['analytical_UNIT_links']==a['blocked_guard_boxes_preserved']==(2 if valid else 0)
        assert a['new_native_operations']==a['old_suites_producers_reexecuted']==a['group_admissions']==0;noflags(a)
        for name in a['case_order']:
            case=a['cases'][name];pc=previous['cases'][name]
            assert case['context']==pc['context']==unit['cases'][name]['context'] and case['domain_INPUT_valid'] is valid
            assert case['group_field_bound_L1'] is case['group_phase_bound_rad'] is None and case['status']=='STOP';noflags(case)
            if not valid:assert case['sources'] is None;continue
            sources=amp['synthetic_scene_domains']['cases'][name]['domain_INPUT']['sources']
            for x,ps,us,s in zip(case['sources'],pc['sources'],unit['cases'][name]['sources'],sources):
                assert x['source_id']==ps['source_id']==us['source_id']==s['source_id']
                assert x['domain_source_sha256']==dig(s) and x['retained_product_source_sha256']==dig(ps) and x['retained_UNIT_source_sha256']==dig(us)
                assert x['retained_bare_SOURCE_row_sha256']==ps['retained_bare_SOURCE_row_sha256']
                proof(x['link'],s['box_reim'],us['result']['unit_L1_charges_to_FIXED_ORIGINAL'])
                expected={**ps['proof']['charges_L1'],**x['link']['charges_L1']}
                assert len(expected)==14 and x['bare_charges_L1']==expected
                assert x['uniform_bare_RN_model_bound_to_A_times_ideal_UNIT_L1']==pair(sum(map(rat,expected.values()),F(0)))
                assert x['whole_box_guard_admission_disproved'] is True and x['material_included'] is False
                assert x['uniform_executed_SOURCE_error_L1'] is x['phase_bound_rad'] is None and x['status']=='STOP';noflags(x)
    controls=run['data']['algebra_controls']
    for x in controls.values():proof(x,x['box_reim'],x['fixed_UNIT_charges_to_ORIGINAL_L1'])
    examples=run['data']['algebra_examples_not_continuum_proof'];assert len(examples)==12
    for x in examples:
        a,b=map(rat,x['A_reim']);dr,di=map(rat,x['delta_UNIT_reim'])
        assert rat(x['observed_L1'])==abs(a*dr-b*di)+abs(a*di+b*dr)
        assert rat(x['observed_L1'])<=rat(controls[x['box']]['uniform_A_times_UNIT_error_to_A_times_ideal_UNIT_L1'])
    assert len(run['data']['typed_dependency_rejections'])==8 and len(run['data']['INPUT_SHA_rejections'])==6
    dep=run['data']['synthetic_domains']['dependency_contract'];tree=ast.parse((ROOT/dep['graph']).read_bytes())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
    keys=sorted({n.slice.value for n in ast.walk(fn) if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id=='admission'})
    assert keys==dep['numerical_admission_keys'] and 'field_reim' not in keys and dep['SOURCE_field_reim_read_by_execute'] is False
    print(json.dumps({'PASS':True,'pins':len(pins),'links':2,'separate_bare_charges':14,'algebra_examples':12,'guard_boxes_STILL_STOP':2,'native_operations':0,'full_SOURCE_phase_error':None},sort_keys=True))
if __name__=='__main__':main()
