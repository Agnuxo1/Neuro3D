"""Independent rational/IEEE receipt oracle; no production imports or native replay."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-PHASE-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-GROUP-PREREQUISITES-HOST-001-CODEX.json'
PARENT_SHA='82f01820c150602bab94f03f0611424a14f87849c2b4c1938393665223bb86a2'
REFLECTION='coordinacion/respuestas/AXIAL-CURRENT-SOURCE-IDEAL-REFLECTION-CPU-001-CODEX.json'
SOURCE='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'
MATERIAL='coordinacion/respuestas/AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001-CODEX.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p
    return json.loads(b)
def payload(r):
    t=r['test_run'];s=''.join(t['stdout_zlib_base64_chunks']) if 'stdout_zlib_base64_chunks' in t else t['stdout_zlib_base64']
    b=zlib.decompress(base64.b64decode(s));assert sha(b)==t['stdout_sha256'] and len(b)==t['stdout_bytes']
    return json.loads(b)
def q(v):
    assert type(v) is list and len(v)==2 and all(type(x) is int for x in v)
    n,d=v;assert d>0 and math.gcd(n,d)==1
    return F(n,d)
def bits(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)&2047;m=w&((1<<52)-1);assert e!=2047 and (e!=0 or m==0)
    return F.from_float(struct.unpack('<d',struct.pack('<Q',w))[0])
def pair(v):return [v.numerator,v.denominator]
def verify_disk(p):
    a=list(map(bits,p['ORIGINAL_source_uint64']));z=list(map(bits,p['reflected_source_uint64']))
    assert len(a)==len(z)==2 and any(z)
    lo=max(map(abs,a));eps=q(p['point_reflected_error_L1']);assert 0<=eps<lo
    gap=lo-eps;phase=eps/gap
    assert p['ORIGINAL_amplitude_lower_bound']==pair(lo) and p['positive_radial_projection_lower_bound']==pair(gap)
    assert p['point_principal_phase_distance_bound_rad']==pair(phase)
    assert p['phase_INPUT_quota_fits'] is None
    for k in ('unwrapped_phase_proved','native_atan_or_arg_executed','zero_canonicalization_performed'):assert p[k] is False
    return phase
def main():
    r=json.loads((ROOT/REPORT).read_bytes());parent=read(PARENT,PARENT_SHA)
    inherited={**parent['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256']
    assert len(inherited)==413 and len(own)==4 and not set(inherited)&set(own)
    pins={**inherited,**own};assert r['code_doc_sha256']==pins and len(pins)==417
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(x is False for x in r['proof_scope'].values())
    def allfalse(v):assert all(v[k] is False for k in flags)
    old=payload(read(REFLECTION,pins[REFLECTION]))['data']['audit']
    bare=payload(read(SOURCE,pins[SOURCE]))['data']['audit']
    mat=payload(read(MATERIAL,pins[MATERIAL]))['data']['audit']
    run=payload(r);assert run['PASS'] is True and run['tests']==4
    d=run['data'];a=d['audit'];assert set(a['cases'])==set(old['cases'])
    assert a['model']=='axial-current-reflected-source-disk-principal-phase-HOST-v1'
    assert a['inherited_pins_verified']==413 and a['new_native_operations']==a['old_producers_suites_reexecuted']==0
    assert a['phase_INPUT_policy_adopted'] is a['new_group_admission'] is False;allfalse(a)
    count=missing=0;bounds={}
    for name,c in a['cases'].items():
        oc=old['cases'][name];ctx=oc['context'];assert c['context']==ctx and c['status']=='STOP';allfalse(c)
        assert [row['source_id'] for row in c['sources']]==ctx['source_order']
        for i,(row,orow) in enumerate(zip(c['sources'],oc['sources'])):
            allfalse(row);assert row['retained_reflection_row_sha256']==digest(orow) and row['status']=='STOP'
            flag='point_reflected_source_phase_bound_HOST_proved'
            if not orow['current_guarded_source_ideal_reflection_CPU_executed']:
                missing+=1;assert row[flag] is False and row['proof'] is None
                continue
            count+=1;assert row[flag] is True
            sr=bare['cases'][name]['sources'][i];mr=mat['cases'][name]['sources'][i]
            assert row['retained_bare_source_row_sha256']==digest(sr) and row['retained_material_admission_row_sha256']==digest(mr)
            assert row['context_sha256']==digest(ctx) and row['original_snapshot_sha256']==ctx['original_snapshot_sha256']
            assign=ctx['assignments'][i];v=orow['result'];p=row['proof']
            assert row['phase_reference_id']==assign['source_phase_reference_id']==v['phase_reference_id']
            assert row['terminal_reference_id']==assign['terminal_reference_id']==assign['common_terminal_reference_id']==v['terminal_reference_id']
            assert p['ORIGINAL_source_uint64']==sr['result']['source_encoder']['ORIGINAL_source_uint64']
            assert p['reflected_source_uint64']==v['reflected_uint64']
            charges=v['fifteen_source_material_charges_L1'];assert row['fifteen_reflected_charges_L1']==charges and len(charges)==15
            eps=sum(map(q,charges.values()),F(0));assert eps==q(v['point_reflected_source_bound_to_FIXED_ORIGINAL_L1'])==q(p['point_reflected_error_L1'])
            assert v['material_profile']['ideal_coefficient_exact_reim']==[[-1,1],[0,1]]
            # Modulus of fixed ideal coefficient is exactly one. Unit exp(i theta) is the prior reference model, not a represented approximate unit norm.
            bounds[name]=float(verify_disk(p))
    assert (count,missing)==(2,17)==(a['point_source_phase_certificates'],a['retained_sources_STOP'])
    controls=d['disk_controls'];assert len(controls['accepted'])==4 and len(controls['rejected'])==10
    for p in controls['accepted']:verify_disk(p['proof'])
    assert len(d['atomic_identity_rejections'])==11 and len(d['synthetic_angle_diagnostics'])==12
    assert controls['accepted'][0]['proof']['ORIGINAL_source_uint64'][0]==1<<63
    assert controls['accepted'][0]['proof']['point_principal_phase_distance_bound_rad']==[0,1]
    assert controls['accepted'][3]['proof']['point_principal_phase_distance_bound_rad']==[999,1]
    print(json.dumps({'PASS':True,'pins':len(pins),'point_SOURCE_phase_certificates':count,'retained_STOP_sources':missing,
        'principal_phase_bounds_rad':bounds,'disk_rejections':10,'atomic_identity_rejections':11,
        'scope':'HOST point phase only; phase INPUT quota None; no uniform/group/reduction/GPU/RT/physical admission'},sort_keys=True))
if __name__=='__main__':main()
