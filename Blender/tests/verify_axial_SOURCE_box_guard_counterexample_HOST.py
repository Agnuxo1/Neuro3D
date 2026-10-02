"""Independent stdlib oracle: exact IEEE words, domain containment, immutable negative proof."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-BOX-GUARD-COUNTEREXAMPLE-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-HILO-DECODE-HOST-001-CODEX.json'
PARENT_SHA='0c0bba56d7a617280bf7d8bce70b18fe201cccd86cb367adb5845b2997987602'
DOMAIN='coordinacion/respuestas/AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001-CODEX.json'
GUARD='Blender/benchmarks/capacity_audit/axial_geometry_decode_guard_CPU_v1.py'
MODEL='axial-SOURCE-box-frozen-guard-exact-counterexample-HOST-v1'
FLAG='whole_box_frozen_guard_admission_disproved_HOST'
TINY=F(1,2**149)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(v):return [v.numerator,v.denominator]
def rat(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int and n.bit_length()<=4096 for n in v)
    assert v[1]>0 and math.gcd(*v)==1
    return F(*v)
def payload(r):
    t=r['test_run'];s=''.join(t['stdout_zlib_base64_chunks']) if 'stdout_zlib_base64_chunks' in t else t['stdout_zlib_base64']
    b=zlib.decompress(base64.b64decode(s));assert sha(b)==t['stdout_sha256'] and len(b)==t['stdout_bytes']
    return json.loads(b)
def decode(w,width,normal):
    assert type(w) is int and 0<=w<2**width
    frac,bias,eb=(23,127,8) if width==32 else (52,1023,11)
    exponent=(w>>frac)&((1<<eb)-1);mantissa=w&((1<<frac)-1)
    assert exponent!=(1<<eb)-1
    assert not normal or exponent!=0 or mantissa==0
    power=(exponent if exponent else 1)-bias-frac
    factor=F(1<<power) if power>=0 else F(1,1<<(-power))
    return (-1 if w>>(width-1) else 1)*(mantissa+((1<<frac) if exponent else 0))*factor
def main():
    r=json.loads((ROOT/REPORT).read_bytes());pb=(ROOT/PARENT).read_bytes();assert sha(pb)==PARENT_SHA
    p=json.loads(pb);inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert r['task_id']=='AXIAL-SOURCE-BOX-GUARD-COUNTEREXAMPLE-HOST-001' and r['model']==MODEL
    assert r['base_commit']=='139ef7b3534bc6481d055e24cdd6445cfc6c50c6'
    assert len(inherited)==443 and len(own)==4 and len(pins)==447 and not set(inherited)&set(own) and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['frozen_guard_file_sha256']==pins[GUARD]
    guard_text=(ROOT/GUARD).read_text()
    assert "def bits(word,width,*,normal=True):" in guard_text
    assert "require(not normal or e>0 or m==0,'normal-or-zero selected word')" in guard_text
    assert "value=bits(w,width)" in guard_text # check_RN default policy, preserved pinned graph.
    run=payload(r);parent=payload(p)['data'];domain=payload(json.loads((ROOT/DOMAIN).read_bytes()))['data']
    assert run['PASS'] is True and run['tests']==5
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def allfalse(v):assert all(v[k] is False for k in flags)
    def proof(v,box,anchors,found):
        assert v['model']==MODEL and v['box_reim']==box and v['ORIGINAL_anchor_uint64']==anchors and v[FLAG] is found
        intervals=[tuple(map(rat,i)) for i in box];assert len(intervals)==2 and all(lo<=hi for lo,hi in intervals)
        assert len(anchors)==2
        assert all(lo<=decode(w,64,True)<=hi for w,(lo,hi) in zip(anchors,intervals))
        for k in ('frozen_guard_admission_for_entire_box_proved','native_cast_executed','SOURCE_graph_executed','device_model_authenticated','signed_zero_execution_policy_proved','uniform_SOURCE_enclosure_proved'):assert v[k] is False
        assert v['uniform_executed_SOURCE_error_L1'] is v['phase_bound_rad'] is None and v['status']=='STOP';allfalse(v)
        eligible=[(i,q) for i,(lo,hi) in enumerate(intervals) for q in (TINY,-TINY) if lo<=q<=hi]
        if not found:
            assert not eligible and v['witness'] is None
            assert v['reason']=='no +/-2^-149 witness found; absence is NOT whole-box admission proof'
            return
        w=v['witness'];i,q=eligible[0]
        assert type(w['component']) is int and w['component']==i and rat(w['value'])==q
        sg=int(q<0);word64=((1023-149)<<52)|(sg<<63);word32=1|(sg<<31)
        assert w['input_uint64']==word64 and type(w['input_uint64']) is int
        assert w['derived_RN32_high_uint32']==word32 and type(w['derived_RN32_high_uint32']) is int
        expected=list(anchors);expected[i]=word64;assert w['SOURCE_input_uint64']==expected
        values=[decode(word,64,True) for word in expected];assert w['SOURCE_input_reim']==list(map(pair,values))
        assert all(lo<=x<=hi for x,(lo,hi) in zip(values,intervals))
        assert decode(word64,64,True)==decode(word32,32,False)==q
        assert (word64>>52)&2047==1023-149 # binary64 normal.
        assert ((word32>>23)&255)==0 and (word32&((1<<23)-1))==1 # binary32 nonzero subnormal.
        assert w['RN32_conversion_exact_proved'] is w['HOST_frozen_guard_check_rejected'] is True
        assert w['rejection_reason']=='normal-or-zero selected word'
        assert w['rejection_scope']=='selected high word; no native cast or complete SOURCE graph executed'
    data=run['data']
    for variant,valid in (('real_missing',False),('explicit_None_missing',False),('synthetic_domains',True)):
        a=data[variant];prev=parent[variant];domains=domain['synthetic_scene_domains' if valid else 'real_missing']
        assert a['model']==MODEL and a['variant']==variant and a['inherited_pins_verified']==443
        assert a['case_order']==prev['case_order']==domains['case_order'] and set(a['cases'])==set(prev['cases'])
        assert a['exact_guard_counterexamples']==(2 if valid else 0)
        assert a['frozen_guard_changed'] is a['uniform_SOURCE_enclosure_proved'] is False;allfalse(a)
        for k in ('new_native_operations','old_suites_producers_reexecuted','group_admissions'):assert a[k]==0
        for name,c in a['cases'].items():
            pc=prev['cases'][name];dc=domains['cases'][name]
            assert c['context']==pc['context']==dc['context'] and c['domain_INPUT_valid'] is valid and c['status']=='STOP'
            assert c['group_phase_bound_rad'] is c['group_field_bound_L1'] is c['uniform_executed_SOURCE_error_L1'] is None
            assert c['uniform_SOURCE_enclosure_proved'] is False;allfalse(c)
            if not valid:assert c['sources'] is None;continue
            assert len(c['sources'])==len(pc['sources'])==len(dc['domain_INPUT']['sources'])==1
            for s,ps,ds in zip(c['sources'],pc['sources'],dc['domain_INPUT']['sources']):
                assert s['source_id']==ps['source_id']==ds['source_id']
                assert s['domain_source_sha256']==ps['domain_source_sha256']==digest(ds)
                assert s['retained_encoder_decode_bound_sha256']==digest(ps['bound'])
                assert ps['bound']['box_reim']==ds['box_reim']
                proof(s['proof'],ds['box_reim'],ds['ORIGINAL_source_uint64'],True)
                assert s['proof']['witness']['component']==1 and s['proof']['witness']['derived_RN32_high_uint32']==1
    real=data['real_missing'];assert len(real['cases'])==17 and sum(len(c['context']['source_order']) for c in real['cases'].values())==19
    z=[[0,1],[0,1]]
    controls={'positive':([z,[[0,1],pair(2*TINY)]],[0,0],True),
        'negative':([z,[pair(-2*TINY),[0,1]]],[0,0],True),
        'zero_only':([z,z],[0,0],False),'normal_only':([[[1,1],[2,1]],z],[1023<<52,0],False)}
    assert set(data['controls'])==set(controls)
    for n,(box,anchors,found) in controls.items():proof(data['controls'][n],box,anchors,found)
    assert [v['label'] for v in data['model_type_domain_rejections']]==['model','bool_anchor','float_endpoint','reversed','anchor_outside','nonfinite_anchor','oversize']
    assert [v['label'] for v in data['INPUT_SHA_rejections']]==['late_context','late_SOURCE_gauge','typed_retained_validity','typed_analytic_flag','parent_SHA']
    assert r['synthetic_controls_are_real_INPUT'] is r['output_fitted_INPUT'] is False and r['JEV_provenance']=='LOCAL'
    print(json.dumps({'PASS':True,'pins':447,'tests':5,'anchored_guard_counterexamples':2,'controls':4,
        'type_domain_rejections':7,'INPUT_SHA_rejections':5,'REAL_missing_cases':17,'REAL_missing_sources':19,
        'uniform_complete_SOURCE_error':None,'whole_box_guard_admission':False,'native_operations':0,
        'scope':'exact HOST counterexamples to frozen selected-normal policy; no cast/SOURCE/device execution'},sort_keys=True))
if __name__=='__main__':main()
