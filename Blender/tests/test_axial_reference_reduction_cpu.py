"""Referenced-terminal grouping/reduction tests only; no upstream replay."""
import json
import sys
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_reference_reduction_cpu_v1 as m
PINS,S,C=m.load_retained()
CONTRACTS={n:m.contract_for(c,{sid:'g' for sid in c['source_order']},m.AUDIT_LIMITS) for n,c in S['cases'].items()}
def compose(n='positive',source=None,contract=None,cache=None):
    s=deepcopy(S['cases'][n]) if source is None else source
    return m.compose(s,deepcopy(CONTRACTS[n]) if contract is None else contract,C if cache is None else cache,
        model=m.MODEL,expected_source_sha256=m.digest(s))
def reject(fn):
    try:fn()
    except (ValueError,AssertionError,KeyError,TypeError,IndexError):return
    raise AssertionError('fail-closed rejection missing')
def coverage(a):
    assert a['counts']=={'cases':13,'sources':14,'reduced_cases':5,'accepted_cases_CPU_only':4}
    assert a['new_RN64_operations']==0 and a['cached_RN64_operations_NOT_executed']==32
    for n,c in a['cases'].items():
        assert c['previous_source_accepted'] is S['cases'][n]['accepted_source_absolute_CPU_only']
        assert c['retained_closure_gates_UNCHANGED']==S['cases'][n]['retained_closure_gates_UNCHANGED']
    assert sum(not c['scene_field_reduced'] for c in a['cases'].values())==8
def gauge_contract():
    for key,value in [('port','M'),('source_phase_reference_id','foreign'),('terminal_reference_id','foreign'),
                      ('common_terminal_reference_id','foreign'),('rebase_cycles',[1,4]),('coherence_group','')]:
        ct=deepcopy(CONTRACTS['positive']);ct['assignments'][0][key]=value
        reject(lambda:compose(contract=ct))
    ct=deepcopy(CONTRACTS['positive']);ct['grouping_provenance']='physical coherence verified'
    reject(lambda:compose(contract=ct))
def caps_coverage():
    for bad in ({},{'field_L1':[0,1]},{**m.AUDIT_LIMITS,'power':[-1,1]},{**m.AUDIT_LIMITS,'power':[True,1]}):
        ct=deepcopy(CONTRACTS['positive']);ct['limits']=bad
        reject(lambda:compose(contract=ct))
    ct=deepcopy(CONTRACTS['two_sources']);ct['assignments'].reverse()
    reject(lambda:compose('two_sources',contract=ct))
    ct=deepcopy(CONTRACTS['positive']);ct['scene_binding_sha256']='foreign'
    reject(lambda:compose(contract=ct))
    reject(lambda:m.audit(model='foreign',case_contracts=CONTRACTS))
    reject(lambda:m.audit(model=m.MODEL,case_contracts={}))
def source_identity():
    source=deepcopy(S['cases']['positive']);source['paths'][0]['terminal_reference_id']='foreign'
    reject(lambda:compose(source=source))
    source=deepcopy(S['cases']['positive']);source['paths'][0]['measurement']['observed_path_field_rational'][0]=[1,1]
    reject(lambda:compose(source=source))
    source=deepcopy(S['cases']['positive']);source['accepted_source_absolute_CPU_only']=1
    reject(lambda:compose(source=source))
    reject(lambda:m.compose(S['cases']['positive'],CONTRACTS['positive'],C,model=m.MODEL,expected_source_sha256='0'*64))
def no_replay():
    with patch.object(m,'Nodes',side_effect=AssertionError('old arithmetic replay')),patch.object(m,'detector_words',side_effect=AssertionError('old detector replay')):
        a=m.audit(model=m.MODEL,case_contracts=CONTRACTS)
    assert a['new_RN64_operations']==0
def corrupt():
    for kind in C.bank:
        c=deepcopy(C)
        for item in c.bank[kind].values():item['output_sha256']='0'*64
        reject(lambda:compose(cache=c))
def cancellation_and_caps(a):
    p=a['cases']['two_sources']['ports']['D']
    assert p['observed_power_rational']==[0,1] and p['relative_power']['relative_budget_satisfied'] is False
    assert p['groups']['g']['relative_field']['ideal_reference_lower_rational']==[0,1]
    assert a['cases']['two_sources']['accepted_reduction_detector_CPU_only'] is False
    split=a['separate_group_control'];assert split['accepted_reduction_detector_CPU_only'] is True
    assert F(*split['ports']['D']['observed_power_rational'])>0
    assert split['contract']['limits']==a['cases']['two_sources']['contract']['limits']
    strict=a['zero_field_cap_control'];normal=a['cases']['positive']
    assert strict['accepted_reduction_detector_CPU_only'] is False
    assert strict['ports']['D']['groups']['g']['output_uint64']==normal['ports']['D']['groups']['g']['output_uint64']
    assert strict['ports']['D']['observed_power_uint64']==normal['ports']['D']['observed_power_uint64']
def scope(a):
    for k in ('GPU_executed','ALU_executed','Bpy_executed','execution_authenticated','coherence_authenticated',
              'native_promotion_allowed','accepted_full_field_pipeline','old_upstream_producer_rerun'):
        assert a[k] is False
    for c in a['cases'].values():
        assert c['accepted_full_field_pipeline'] is c['coherence_authenticated'] is c['execution_authenticated'] is False
        assert all(r['rebase_cycles']==[0,1] for r in c['contract']['assignments'])
def main():
    a=m.audit(model=m.MODEL,case_contracts=CONTRACTS)
    coverage(a);gauge_contract();caps_coverage();source_identity();no_replay();corrupt();cancellation_and_caps(a);scope(a)
    print(json.dumps({'tests':8,'PASS':True,'audit':a},sort_keys=True,separators=(',',':')))
if __name__=='__main__':main()
