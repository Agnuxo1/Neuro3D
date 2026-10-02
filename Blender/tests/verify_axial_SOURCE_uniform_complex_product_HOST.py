"""Independent stdlib oracle for uniform product target A*fixed represented UNIT, not scene admission."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-COMPLEX-PRODUCT-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-BOX-GUARD-COUNTEREXAMPLE-HOST-001-CODEX.json'
PARENT_SHA='54ec7a9d9dcb98354685d7751ad1ed14012e05497543f520d54f05a3e1583f35'
ENC='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-HILO-DECODE-HOST-001-CODEX.json'
BARE='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'
MODEL='axial-variable-SOURCE-box-fixed-represented-UNIT-uniform-product-HOST-v1'
FLAG='uniform_bare_product_to_fixed_represented_UNIT_bound_HOST_proved'
ARITH='binary32/binary64 RN-even; gradual underflow; exact widening; no FTZ/FMA'
MAX=F((2**53-1)*2**971)
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
def pow2(e):return F(1<<e) if e>=0 else F(1,1<<(-e))
def decode64(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)&2047;m=w&((1<<52)-1)
    assert e<2047 and (e>0 or m==0)
    return (-1 if w>>63 else 1)*(m+((1<<52) if e else 0))*pow2((e if e else 1)-1075)
def rn(x,width):
    if x==0:return F(0)
    a=abs(x);e=a.numerator.bit_length()-a.denominator.bit_length()
    while pow2(e)>a:e-=1
    while pow2(e+1)<=a:e+=1
    q=pow2(max(e-(24 if width==32 else 53)+1,-149 if width==32 else -1074))
    t=a/q;k=t.numerator//t.denominator
    n=min((k,k+1),key=lambda n:(abs(n*q-a),n%2))
    return (-1 if x<0 else 1)*n*q
def main():
    r=json.loads((ROOT/REPORT).read_bytes());pb=(ROOT/PARENT).read_bytes();assert sha(pb)==PARENT_SHA;p=json.loads(pb)
    inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert r['task_id']=='AXIAL-SOURCE-UNIFORM-COMPLEX-PRODUCT-HOST-001' and r['model']==MODEL and r['base_commit']=='ff54076e85206ab76d001b56bdba379fbd333405'
    assert len(inherited)==448 and len(own)==4 and len(pins)==452 and not set(inherited)&set(own) and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    run=payload(r);negative=payload(p)['data']
    encoder=payload(json.loads((ROOT/ENC).read_bytes()))['data']
    bare=payload(json.loads((ROOT/BARE).read_bytes()))['data']['audit']
    assert run['PASS'] is True and run['tests']==5
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def allfalse(v):assert all(v[k] is False for k in flags)
    def proof(v,b,words):
        assert v['model']==MODEL and v['arithmetic_model']==ARITH and v[FLAG] is True and v['status']=='STOP'
        assert v['box_reim']==b['box_reim'] and v['encoder_bound_sha256']==digest(b)
        assert v['fixed_represented_UNIT_uint64']==words and len(words)==2
        u=list(map(decode64,words));L=sum(map(abs,u),F(0))
        assert v['fixed_represented_UNIT_reim']==list(map(pair,u)) and v['represented_UNIT_norm_L1']==pair(L)
        maxima=[rat(c['decoded_output_max_bound']) for c in b['components']]
        assert v['decoded_SOURCE_component_max']==list(map(pair,maxima))
        E=rat(b['source_encoding_uniform_L1_bound']);D=rat(b['source_decode_RN64_uniform_L1_bound'])
        assert b['source_encoding_plus_decode_uniform_L1_bound']==pair(E+D)
        mags=[maxima[0]*abs(u[0]),maxima[1]*abs(u[1]),maxima[0]*abs(u[1]),maxima[1]*abs(u[0])]
        labels=['ac','bd','ad','bc','real','imag'];nodes=[];errors=[];outputs=[]
        for i,label in enumerate(labels):
            mag=mags[i] if i<4 else (outputs[0]+outputs[1] if i==4 else outputs[2]+outputs[3])
            assert 0<=mag<=MAX
            err=mag/F(2**53)+F(1,2**1075) if mag else F(0)
            assert mag+err<=MAX
            nodes.append({'label':label,'op':'mul' if i<4 else 'add','exact_argument_max':pair(mag),'RN64_error_bound':pair(err),'output_max':pair(mag+err)})
            errors.append(err);outputs.append(mag+err)
        assert v['nodes']==nodes
        N=sum(errors,F(0));charges={'source_encoding_times_UNIT_L1':E*L,'source_decode_times_UNIT_L1':D*L,'product_six_RN64_nodes_L1':N}
        assert v['charges_L1']=={k:pair(x) for k,x in charges.items()}
        assert v['uniform_error_to_A_times_fixed_represented_UNIT_L1']==pair(E*L+D*L+N)
        assert v['ideal_target']=='variable ORIGINAL A times FIXED represented UNIT; not ORIGINAL ideal exp(i theta)'
        for k in ('UNIT_error_to_ORIGINAL_included','material_reduction_projection_included','uniform_SOURCE_enclosure_proved','frozen_guard_admission_for_entire_box_proved','device_model_authenticated','signed_zero_execution_policy_proved'):assert v[k] is False
        assert v['uniform_executed_SOURCE_error_L1'] is v['phase_bound_rad'] is None;allfalse(v)
    data=run['data']
    for variant,valid in (('real_missing',False),('explicit_None_missing',False),('synthetic_domains',True)):
        a=data[variant];ec=encoder[variant];gc=negative[variant]
        assert a['variant']==variant and a['model']==MODEL and a['case_order']==ec['case_order']==gc['case_order'] and set(a['cases'])==set(ec['cases'])
        assert a['inherited_pins_verified']==448 and a['analytical_product_bounds']==a['blocked_guard_boxes_preserved']==(2 if valid else 0)
        for k in ('new_native_operations','old_suites_producers_reexecuted','group_admissions'):assert a[k]==0
        assert a['uniform_SOURCE_enclosure_proved'] is a['UNIT_error_to_ORIGINAL_included'] is False;allfalse(a)
        for name,c in a['cases'].items():
            assert c['context']==ec['cases'][name]['context']==gc['cases'][name]['context']==bare['cases'][name]['context']
            assert c['domain_INPUT_valid'] is valid and c['status']=='STOP'
            assert c['uniform_executed_SOURCE_error_L1'] is c['group_phase_bound_rad'] is c['group_field_bound_L1'] is None
            assert c['uniform_SOURCE_enclosure_proved'] is False;allfalse(c)
            if not valid:assert c['sources'] is None;continue
            assert len(c['sources'])==1
            for s,e,g,b in zip(c['sources'],ec['cases'][name]['sources'],gc['cases'][name]['sources'],bare['cases'][name]['sources']):
                assert s['source_id']==e['source_id']==g['source_id']==b['source_id']
                assert s['domain_source_sha256']==e['domain_source_sha256']==g['domain_source_sha256']
                assert s['negative_guard_source_sha256']==digest(g) and s['retained_bare_SOURCE_row_sha256']==digest(b)
                assert s['whole_box_guard_admission_disproved'] is g['proof']['whole_box_frozen_guard_admission_disproved_HOST'] is True
                words=b['result']['unit_uint64'];assert words==b['admission']['unit_uint64']
                proof(s['proof'],e['bound'],words)
    real=data['real_missing'];assert len(real['cases'])==17 and sum(len(c['context']['source_order']) for c in real['cases'].values())==19
    name='nonexact_geometry_phase_PASS';b=encoder['synthetic_domains']['cases'][name]['sources'][0]['bound'];words=bare['cases'][name]['sources'][0]['result']['unit_uint64']
    one=1023<<52;neg=one|(1<<63)
    controls={'zero':[0,0],'axis_one':[one,0],'opposite':[one,neg],'negative_axis':[neg,0]}
    assert set(data['UNIT_controls'])==set(controls)
    for n,w in controls.items():proof(data['UNIT_controls'][n],b,w)
    sample_proof=data['sample_product_proof'];proof(sample_proof,b,words);u=list(map(decode64,words))
    anchor=decode64(bare['cases'][name]['sources'][0]['admission']['ORIGINAL_source_uint64'][0])
    xs=[(anchor,F(0)),(anchor,pow2(-149)),(anchor,-pow2(-149)),(anchor,pow2(-20)),(anchor,-pow2(-20)),(anchor+pow2(-24),F(0)),(anchor-pow2(-24),F(0)),(anchor,pow2(-21))]
    assert len(data['exact_RNE_simulations'])==len(xs)==8
    for s,xy in zip(data['exact_RNE_simulations'],xs):
        assert s['kind']=='CPU_synthetic_exact_RNE_simulation' and s['SOURCE_A_reim']==list(map(pair,xy))
        dec=[]
        for x,ends in zip(xy,b['box_reim']):
            lo,hi=map(rat,ends);assert lo<=x<=hi and rn(x,64)==x
            high=rn(x,32);res=rn(x-high,64);low=rn(res,32);dec.append(rn(high+low,64))
        assert s['decoded_SOURCE_reim']==list(map(pair,dec))
        a,bb=dec;c,d=u;mul=[rn(a*c,64),rn(bb*d,64),rn(a*d,64),rn(bb*c,64)]
        re=rn(mul[0]-mul[1],64);im=rn(mul[2]+mul[3],64);out=mul+[re,im]
        target=[xy[0]*c-xy[1]*d,xy[0]*d+xy[1]*c];error=abs(re-target[0])+abs(im-target[1])
        assert s['product_nodes']==list(map(pair,out)) and s['target_A_times_fixed_UNIT_reim']==list(map(pair,target)) and s['observed_error_L1']==pair(error)
        assert error<=rat(sample_proof['uniform_error_to_A_times_fixed_represented_UNIT_L1'])
        args=[a*c,bb*d,a*d,bb*c,mul[0]-mul[1],mul[2]+mul[3]]
        for arg,value,node in zip(args,out,sample_proof['nodes']):
            assert abs(arg)<=rat(node['exact_argument_max']) and abs(value-arg)<=rat(node['RN64_error_bound'])
    assert [v['label'] for v in data['model_word_range_rejections']]==['model','arithmetic_FMA','bool_UNIT_word','nonfinite_UNIT','UNIT_count','typed_encoder_flag','encoder_charge_forgery','node_MAX_margin']
    assert [v['label'] for v in data['INPUT_SHA_rejections']]==['late_context','late_SOURCE_gauge','UNIT_binding','typed_guard_negative','parent_SHA']
    assert r['synthetic_controls_are_real_INPUT'] is r['output_fitted_INPUT'] is False and r['JEV_provenance']=='LOCAL'
    print(json.dumps({'PASS':True,'pins':452,'tests':5,'anchored_product_bounds':2,'blocked_guard_boxes_preserved':2,'UNIT_controls':4,
        'exact_RNE_simulations':8,'model_word_range_rejections':8,'INPUT_SHA_rejections':5,'REAL_missing_cases':17,'REAL_missing_sources':19,
        'UNIT_error_to_ORIGINAL_included':False,'complete_uniform_SOURCE_error':None,'scope':'HOST variable A times fixed represented UNIT only; no guard/device/phase/full-field admission'},sort_keys=True))
if __name__=='__main__':main()
