"""Independent immutable-receipt oracle; stdlib exact rationals, no production imports."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-HILO-DECODE-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001-CODEX.json'
PARENT_SHA='822d58a334b8be92f7e8421eb330013865c76fab7f55314eff5926f76e52a28e'
MODEL='axial-SOURCE-uniform-hilo32-RN64decode-declared-box-HOST-v1'
ARITH='binary32/binary64 RN-even; gradual underflow; exact widening; no FTZ/FMA'
FLAG='uniform_encoder_decode_bound_for_declared_box_HOST_proved'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def payload(r):
    t=r['test_run'];s=''.join(t['stdout_zlib_base64_chunks']) if 'stdout_zlib_base64_chunks' in t else t['stdout_zlib_base64']
    b=zlib.decompress(base64.b64decode(s));assert sha(b)==t['stdout_sha256'] and len(b)==t['stdout_bytes']
    return json.loads(b)
def pair(x):return [x.numerator,x.denominator]
def rat(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int and n.bit_length()<=4096 for n in v)
    assert v[1]>0 and math.gcd(*v)==1
    return F(*v)
def pow2(e):return F(1<<e) if e>=0 else F(1,1<<(-e))
def nearest(x,bits):
    # Independent neighbor-distance selection; no native arithmetic or producer.
    if x==0:return F(0)
    a=abs(x);e=a.numerator.bit_length()-a.denominator.bit_length()
    while pow2(e)>a:e-=1
    while pow2(e+1)<=a:e+=1
    q=pow2(max(e-(24 if bits==32 else 53)+1,-149 if bits==32 else -1074))
    t=a/q;n=t.numerator//t.denominator
    candidates=[n,n+1];best=min(candidates,key=lambda k:(abs(k*q-a),k%2))
    return (-1 if x<0 else 1)*best*q
def main():
    r=json.loads((ROOT/REPORT).read_bytes());pb=(ROOT/PARENT).read_bytes();assert sha(pb)==PARENT_SHA
    p=json.loads(pb);inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert r['task_id']=='AXIAL-SOURCE-UNIFORM-HILO-DECODE-HOST-001' and r['model']==MODEL
    assert r['base_commit']=='845cdae52ecefaf18dbe0210e06d79cfcf03774e'
    assert len(inherited)==438 and len(own)==4 and len(pins)==442 and not set(inherited)&set(own) and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    run=payload(r);old=payload(p)['data'];assert run['PASS'] is True and run['tests']==5
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def allfalse(v):assert all(v[k] is False for k in flags)
    def bound(v,expected_box):
        assert v['model']==MODEL and v['arithmetic_model']==ARITH and v['box_reim']==expected_box and v[FLAG] is True
        assert len(v['components'])==2
        assert v['graph']==['h=RN32(x)','r=RN64(x-h)','low=RN32(r)','decoded=RN64(widen(h)+widen(low))']
        assert v['unit_Horner_product_material_reduction_errors_included'] is False
        assert v['phase_bound_rad'] is v['uniform_executed_SOURCE_error_L1'] is None and v['status']=='STOP'
        for k in ('uniform_SOURCE_enclosure_proved','frozen_guard_admission_for_entire_box_proved','device_model_authenticated','signed_zero_execution_policy_proved'):assert v[k] is False
        allfalse(v);E=D=F(0)
        for ends,c in zip(expected_box,v['components']):
            lo,hi=map(rat,ends);assert lo<=hi;m=max(abs(lo),abs(hi))
            def ernd(a,b):
                assert 0<=a<=F((2**(24 if b==32 else 53)-1)*2**(104 if b==32 else 971))
                return a*pow2(-24 if b==32 else -53)+pow2(-150 if b==32 else -1075) if a else F(0)
            eh=ernd(m,32);er=ernd(eh,64);el=ernd(eh+er,32);enc=er+el;ed=ernd(m+enc,64)
            expected={'max_abs_ORIGINAL_component':m,'high_cast_error_bound':eh,'high_output_max_bound':m+eh,
                'exact_residual_max_bound':eh,'residual_RN64_error_bound':er,'residual_output_max_bound':eh+er,
                'low_cast_error_bound':el,'low_output_max_bound':eh+er+el,'encoding_error_bound':enc,
                'exact_decode_sum_max_bound':m+enc,'decode_RN64_error_bound':ed,'decoded_output_max_bound':m+enc+ed,
                'encoding_plus_decode_bound':enc+ed}
            assert set(c)==set(expected)
            for k,x in expected.items():assert c[k]==pair(x) and rat(c[k])==x,k
            assert m+eh<=F((2**24-1)*2**104) and eh+er+el<=F((2**24-1)*2**104)
            assert m+enc+ed<=F((2**53-1)*2**971);E+=enc;D+=ed
        assert v['source_encoding_uniform_L1_bound']==pair(E)
        assert v['source_decode_RN64_uniform_L1_bound']==pair(D)
        assert v['source_encoding_plus_decode_uniform_L1_bound']==pair(E+D)
    data=run['data']
    for variant,valid in (('real_missing',False),('explicit_None_missing',False),('synthetic_domains',True)):
        audit=data[variant];prev=old['synthetic_scene_domains' if valid else 'real_missing']
        assert audit['case_order']==prev['case_order'] and set(audit['cases'])==set(prev['cases'])
        assert audit['variant']==variant and audit['model']==MODEL and audit['arithmetic_model']==ARITH
        assert audit['inherited_pins_verified']==438 and audit['analytical_encoder_decode_bounds']==(2 if valid else 0)
        for k in ('new_native_operations','old_suites_producers_reexecuted','group_admissions'):assert audit[k]==0
        for k in ('point_error_reused_as_uniform','uniform_SOURCE_enclosure_proved','frozen_guard_admission_for_entire_box_proved'):assert audit[k] is False
        allfalse(audit)
        for name,c in audit['cases'].items():
            pc=prev['cases'][name];domain=pc['domain_INPUT'];assert c['context']==pc['context'] and c['domain_INPUT_valid'] is valid
            assert c['uniform_executed_SOURCE_error_L1'] is c['group_phase_bound_rad'] is c['group_field_bound_L1'] is None
            assert c['uniform_SOURCE_enclosure_proved'] is False and c['status']=='STOP';allfalse(c)
            if not valid:assert c['sources'] is None;continue
            assert len(c['sources'])==len(domain['sources'])==1
            for s,ps in zip(c['sources'],domain['sources']):
                assert s['source_id']==ps['source_id'] and s['domain_source_sha256']==digest(ps)
                assert s['ORIGINAL_source_uint64']==ps['ORIGINAL_source_uint64']
                assert s['uniform_executed_SOURCE_error_L1'] is None and s['status']=='STOP';allfalse(s)
                bound(s['bound'],ps['box_reim'])
    real=data['real_missing'];assert len(real['cases'])==17 and sum(len(c['context']['source_order']) for c in real['cases'].values())==19
    z=F(0);tiny=pow2(-149);pp=lambda x:[pair(x),pair(x)]
    expected_controls={'zero':[pp(z),pp(z)],'signed_subnormal':[[pair(-tiny),pair(tiny)],pp(z)],
        'positive_normal':[[[1,1],[2,1]],[[3,1],[4,1]]],'negative_normal':[[[-3,1],[-2,1]],[[-2,1],[-1,1]]]}
    assert set(data['box_controls'])==set(expected_controls)
    for n,b in data['box_controls'].items():bound(b,expected_controls[n])
    tie=F(1)+pow2(-24)
    xs=[z,pow2(-1074),-pow2(-1074),tiny,-tiny,F.from_float(0.1),F.from_float(-0.1),tie,-tie,tie-pow2(-52),tie+pow2(-52),pow2(100)+pow2(76)]
    assert len(data['exact_RNE_simulations'])==len(xs)==12
    for s,x in zip(data['exact_RNE_simulations'],xs):
        assert s['kind']=='CPU_synthetic_exact_RNE_simulation' and rat(s['x'])==x and nearest(x,64)==x
        h=nearest(x,32);res=nearest(x-h,64);low=nearest(res,32);a=nearest(h+low,64)
        for key,val in (('h',h),('residual',res),('low',low),('decoded',a),('encoding_error',abs(h+low-x)),('decode_error',abs(a-h-low)),('total_error',abs(a-x))):assert s[key]==pair(val)
        bound(s['bound'],[pp(x),pp(z)]);c=s['bound']['components'][0]
        assert abs(h+low-x)<=rat(c['encoding_error_bound']) and abs(a-h-low)<=rat(c['decode_RN64_error_bound'])
        assert abs(a-x)<=rat(c['encoding_plus_decode_bound'])
        assert h+low-x==(res-(x-h))+(low-res) # dependency cancellation, not two independent high charges
    assert [v['label'] for v in data['model_range_rejections']]==['model','arithmetic_FTZ','above_MAX32','MAX32_margin','reversed','bool','noncanonical','oversize']
    assert [v['label'] for v in data['INPUT_SHA_rejections']]==['late_context','late_SOURCE_gauge','late_anchor_outside','typed_retained_digest','parent_SHA']
    assert r['synthetic_controls_are_real_INPUT'] is r['output_fitted_INPUT'] is False and r['JEV_provenance']=='LOCAL'
    print(json.dumps({'PASS':True,'pins':442,'tests':5,'anchored_encoder_decode_bounds':2,'box_controls':4,'exact_RNE_simulations':12,
        'model_range_rejections':8,'INPUT_SHA_rejections':5,'REAL_missing_cases':17,'REAL_missing_sources':19,
        'uniform_complete_SOURCE_error':None,'guard_device_admission':False,'group_admissions':0,
        'scope':'analytical HOST encoder/decode under explicit RN gradual model only; no native/GPU/RT/physical execution'},sort_keys=True))
if __name__=='__main__':main()
