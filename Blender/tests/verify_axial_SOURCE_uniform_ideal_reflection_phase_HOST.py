"""Independent stdlib conditional reflection/phase receipt oracle, no production imports."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-IDEAL-REFLECTION-PHASE-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-UNIT-ORIGINAL-LINK-HOST-001-CODEX.json'
PARENT_SHA='2160956d3e6b9feaaabe70329698fdb4d5df177a1d9cf7a899fa65477dd6b34c'
MATERIAL='coordinacion/respuestas/AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001-CODEX.json'
AMP='coordinacion/respuestas/AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001-CODEX.json'
MODEL='axial-SOURCE-box-ideal-minus-one-principal-phase-conditional-HOST-v1'
FLAG='conditional_SOURCE_box_ideal_reflection_phase_HOST_proved'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]
def rat(x):
    assert type(x) is list and len(x)==2 and all(type(n) is int and n.bit_length()<=4096 for n in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(''.join(t['stdout_zlib_base64_chunks'])))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());b=(ROOT/PARENT).read_bytes();assert sha(b)==PARENT_SHA;p=json.loads(b)
    inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert len(inherited)==458 and len(own)==4 and len(pins)==462 and r['code_doc_sha256']==pins and not set(inherited)&set(own)
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['task_id']=='AXIAL-SOURCE-UNIFORM-IDEAL-REFLECTION-PHASE-HOST-001' and r['model']==MODEL and r['base_commit']=='b1935473b5392f3dece3b4a439c6e1075cd82095'
    run=payload(r);previous=payload(p)['data'];mat=payload(json.loads((ROOT/MATERIAL).read_bytes()))['data']['audit'];amp=payload(json.loads((ROOT/AMP).read_bytes()))['data']
    assert run['tests']==5 and run['PASS'] is True
    t=r['test_run'];assert t['rc']==0 and not t['timed_out'] and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def nf(x):assert all(x[k] is False for k in flags)
    def proof(x,box,charges):
        assert x['model']==MODEL and x['material_model']=='exact ideal -1 sign reversal; L1 isometry; NOT physical material' and x['box_reim']==box
        d=[]
        for lo,hi in box:
            lo,hi=rat(lo),rat(hi);assert lo<=hi;d.append(F(0) if lo<=0<=hi else min(abs(lo),abs(hi)))
        m=max(d);assert x['component_min_abs']==list(map(pair,d)) and x['amplitude_modulus_lower_bound']==pair(m)
        eps=None if charges is None else sum(map(rat,charges.values()),F(0))
        expected=None if charges is None else {**charges,'ideal_material_exact_model_L1':[0,1]}
        assert x['fifteen_conditional_reflected_charges_L1']==expected
        assert x['conditional_reflected_RN_model_error_L1']==(None if eps is None else pair(eps))
        good=eps is not None and m>0 and eps<m;assert x[FLAG] is good
        assert x['conditional_principal_phase_bound_rad']==(pair(eps/(m-eps)) if good else None)
        assert x['positive_radial_projection_lower_bound']==(pair(m-eps) if good else None)
        assert x['reference']=='variable ORIGINAL A times exp(i fixed ORIGINAL theta) times exact ideal -1'
        for k in ('material_executed','physical_material_authenticated','uniform_SOURCE_enclosure_proved','unwrapped_phase_proved','frozen_guard_admission_for_entire_box_proved'):assert x[k] is False
        for k in ('executed_material_charge_L1','uniform_executed_SOURCE_error_L1','phase_INPUT_quota_fits'):assert x[k] is None
        assert x['status']=='STOP';nf(x)
    for variant in ('real_missing','explicit_None_missing','synthetic_domains'):
        a=run['data'][variant];old=previous[variant];valid=variant=='synthetic_domains'
        assert a['case_order']==old['case_order'] and a['variant']==variant and a['model']==MODEL and a['inherited_pins_verified']==458
        assert a['conditional_reflected_phase_bounds']==(2 if valid else 0) and a['new_native_operations']==a['old_suites_producers_reexecuted']==a['group_admissions']==0;nf(a)
        for name in a['case_order']:
            c=a['cases'][name];oc=old['cases'][name];mc=mat['cases'][name]
            assert c['context']==oc['context']==mc['context'] and c['status']=='STOP'
            assert c['group_field_bound_L1'] is c['group_phase_bound_rad'] is None;nf(c)
            if not valid:assert c['sources'] is None;continue
            domain=amp['synthetic_scene_domains']['cases'][name]['domain_INPUT']['sources']
            for x,src,oldrow,mr in zip(c['sources'],domain,oc['sources'],mc['sources']):
                assert x['source_id']==src['source_id']==oldrow['source_id']==mr['source_id']
                assert x['domain_source_sha256']==digest(src) and x['retained_UNIT_link_SOURCE_sha256']==digest(oldrow) and x['retained_material_admission_SOURCE_sha256']==digest(mr)
                assert mr['retained_source_row_sha256']==oldrow['retained_bare_SOURCE_row_sha256']
                assert mr['phase_reference_id']==src['source_phase_reference_id'] and mr['terminal_reference_id']==src['terminal_reference_id']==src['common_terminal_reference_id']
                pmat=mr['material_profile'];assert type(pmat['mirror_phase_ORIGINAL_uint64']) is int and pmat['mirror_phase_ORIGINAL_uint64'] in (0,1<<63)
                assert digest(pmat['ideal_coefficient_exact_reim'])==digest([[-1,1],[0,1]])
                proof(x['proof'],src['box_reim'],oldrow['bare_charges_L1'])
                assert len(x['proof']['fifteen_conditional_reflected_charges_L1'])==15 and x['whole_box_guard_admission_disproved'] is True
    controls=run['data']['boundary_controls'];assert len(controls)==6
    for p in controls.values():
        q=p['fifteen_conditional_reflected_charges_L1'];proof(p,p['box_reim'],None if q is None else {k:v for k,v in q.items() if k!='ideal_material_exact_model_L1'})
    assert len(run['data']['typed_rejections'])==7 and len(run['data']['INPUT_SHA_rejections'])==7
    examples=run['data']['isometry_examples_not_execution'];assert len(examples)==3
    for x in examples:
        z,w=list(map(rat,x['z'])),list(map(rat,x['w']))
        assert rat(x['error_before'])==rat(x['error_after'])==sum((abs(a-b) for a,b in zip(z,w)),F(0))
    print(json.dumps({'PASS':True,'pins':len(pins),'conditional_phase_bounds':2,'guard_boxes_STILL_STOP':2,'executed_material_error':None,'native_operations':0},sort_keys=True))
if __name__=='__main__':main()
