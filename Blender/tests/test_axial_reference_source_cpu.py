"""Narrow opt-in referenced original-source CPU tests; no upstream runners."""
import json
import sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_reference_source_cpu_v1 as s
PINS,U,G,C=s.load_retained()
CAPS={n:{sid:s.CAP for sid in c['source_order']} for n,c in U['cases'].items()}
def compose(n='positive',u=None,g=None,caps=None,cache=None):
    u=deepcopy(U['cases'][n]) if u is None else u
    return s.compose(u,deepcopy(G[n]) if g is None else g,
        CAPS[n] if caps is None else caps,C if cache is None else cache,
        model=s.MODEL,expected_unit_sha256=s.digest(u))
def reject(fn):
    try:fn()
    except (ValueError,AssertionError,KeyError,TypeError,IndexError):return
    raise AssertionError('fail-closed rejection missing')
def coverage():
    a=s.audit(model=s.MODEL,field_caps=CAPS)
    assert a['counts']=={'cases':13,'sources':14,'products':6,'accepted_cases_CPU_only':5}
    assert a['costs']['new_product_RN64']==a['costs']['new_source_HOST_RN32']==0
    assert a['costs']['cached_product_RN64_NOT_executed']==48
    assert a['costs']['cached_source_HOST_RN32_NOT_executed']==24
    assert a['costs']['mirror_signbit_toggles_new']==12
    assert a['cases']['two_sources']['retained_closure_gates_UNCHANGED']==U['cases']['two_sources']['retained_closure_gates_UNCHANGED']
    return a
def no_replay():
    with patch.object(s,'encode_hilo',side_effect=AssertionError('old encoding replay')),patch.object(s,'product_words',side_effect=AssertionError('old product replay')):
        for n in U['cases']:compose(n)
def fresh_bounds():
    p=compose('nonexact_geometry_phase_PASS')['paths'][0]
    assert s.rat(p['source_encoding_error_L1'])==F(1,1<<55)
    assert s.rat(p['error_charges_L1']['source_encoding'])>0
    assert s.rat(p['composed_path_field_error_L1'])==sum(map(s.rat,p['error_charges_L1'].values()),F(0))
    strict=compose('nonexact_geometry_phase_PASS',caps={'s':[0,1]})
    assert strict['paths'][0]['measurement']==p['measurement']
    assert strict['accepted_source_absolute_CPU_only'] is False
def caps_models():
    for caps in ({},{'s':0.0},{'s':[True,1]},{'s':[-1,1]},{'s':[1,0]},{'s':s.CAP,'extra':s.CAP}):
        reject(lambda:compose(caps=caps))
    reject(lambda:s.audit(model='foreign',field_caps=CAPS))
    reject(lambda:s.audit(model=s.MODEL,field_caps={}))
def bindings():
    g=deepcopy(G['positive']);g['scene_snapshot']['sources'][0]['field_reim'][0]=0.2
    reject(lambda:compose(g=g))
    u=deepcopy(U['cases']['positive']);u['source_order']=['foreign']
    reject(lambda:compose(u=u))
    u=deepcopy(U['cases']['positive']);u['paths'][0]['source_phase_reference_id']='foreign'
    reject(lambda:compose(u=u))
    g=deepcopy(G['positive']);g['sources'][0]['mirror_owner']=1
    reject(lambda:compose(g=g))
    u=deepcopy(U['cases']['positive']);u['paths'][0]['accepted_unit_CPU_only']=1
    reject(lambda:compose(u=u))
    reject(lambda:s.compose(U['cases']['positive'],G['positive'],{'s':s.CAP},C,model=s.MODEL,expected_unit_sha256='0'*64))
def corrupt_cache():
    for kind in ('encoding','product'):
        c=deepcopy(C);item=next(iter(c.bank[kind].values()));item['output_sha256']='0'*64
        reject(lambda:compose(cache=c))
    for words in ([True,0,0,0],[1,0,0,0],[0x7f800000,0,0,0]):
        reject(lambda:s.component(words[0]))
def controls(a):
    assert a['strict_field_cap_zero_control']['accepted_source_absolute_CPU_only'] is False
    assert sum(c['accepted_source_absolute_CPU_only'] for c in a['controls'].values())==1
    n=a['numeric_source_product_control']
    assert n['source_encoding_cache']['cache_hit'] is n['product_cache']['cache_hit'] is False
    assert n['costs']['new_source_HOST_RN32']==4 and n['costs']['new_product_RN64']==8
    assert n['costs']['new_source_exact_residual_subtractions']==2
def scope(a):
    for k in ('GPU_executed','ALU_executed','Bpy_executed','execution_authenticated','physical_coherence_verified',
              'native_promotion_allowed','accepted_full_field_pipeline','scene_field_reduced','detector_evaluated',
              'coherent_group_budget_certified','old_upstream_producer_rerun'):
        assert a[k] is False
    for c in a['cases'].values():
        for k in ('scene_field_reduced','detector_evaluated','coherent_group_budget_certified','accepted_full_field_pipeline','execution_authenticated'):
            assert c[k] is False
def main():
    a=coverage();no_replay();fresh_bounds();caps_models();bindings();corrupt_cache();controls(a);scope(a)
    print(json.dumps({'tests':8,'PASS':True,'audit':a},sort_keys=True,separators=(',',':')))
if __name__=='__main__':main()
