"""Independent stdlib contract/capture/pin checker; no production imports or old runs."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-HOST-READOUT-CONTRACT-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-SINGLETON-POWER-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='6fc6191ae3fed5ccaa52df1922df3c7947950b234d064f2c6ede1c39f6db96d2'
MODEL='axial-HOST-readout-retained-power-contract-v1'
STAGES=('ORIGINAL_ingress','scene_transport','source_encoding','reflection','reduction','power',
        'readout','upload','execution','download','host_validation')
KEYS=('input_packet_sha256','scene_binding_sha256','word_ABI_sha256','original_snapshot_sha256',
      'original_group_contract_sha256','source_order','groups','assignments','unchanged_limits','unchanged_field_L1_cap')
FLAG='restricted_complete_singleton_power_error_to_ORIGINAL_proved'
EXTRA=('readout_executed_new','readout_budget_accepted','physical_detector_calibrated',
       'equal_work_comparison_admitted','complete_costs_measured')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(p,h):
    raw=(ROOT/p).read_bytes();assert sha(raw)==h,p;return json.loads(raw)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    v=r['inherited_pin_source'];d=pins_from(read(v['path'],v['sha256']))
    d[v['path']]=v['sha256'];d.update(r['own_code_doc_sha256']);return d
def payload(r):
    t=r['test_run'];assert t['rc']==0 and not t['timed_out'] and t['threads']==1 and t['affinity_mask']==1
    assert t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60
    raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(raw)==t['stdout_bytes'] and sha(raw)==t['stdout_sha256']
    return json.loads(raw)
r=json.loads((ROOT/REPORT).read_bytes())
assert r['task_id']=='AXIAL-HOST-READOUT-CONTRACT-001'
assert r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==297 and len(r['own_code_doc_sha256'])==4
oldreport=read(PREVIOUS,PREVIOUS_SHA);old=payload(oldreport)['data']['audit']
data=payload(r);assert data['PASS'] is True and data['tests']==4
data=data['data'];plan=data['proposed_contract'];result=data['audit']
assert plan['model']==result['model']==MODEL
assert plan['provenance']=='SYNTHETIC proposed INPUT; absent from retained scene'
assert plan['retained_power_report']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
assert plan['case_order']==old['case_order'] and len(plan['case_order'])==17
assert plan['cost_ledger']==[{'stage':s,'status':'UNMEASURED','seconds':None,'bytes':None} for s in STAGES]
assert plan['comparison_contract']=={'status':'STOP','same_work_and_outputs_authenticated':False,'guard_and_exclusive_job_receipt':None}
false=tuple(oldreport['proof_scope'])+EXTRA
for obj in (plan,result,r['proof_scope']):
    for k in false:assert obj[k] is False,k
assert set(plan)==set(false)|{'model','provenance','retained_power_report','case_order','outputs','cost_ledger','comparison_contract'}
assert result['contract_schema_valid'] is True and result['contract_sha256']==digest(plan)
assert result['contract_provenance']==plan['provenance']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
# Historical early captures omit newer execution-envelope keys; verify bytes/hash/exit without executing.
def old_payload(report):
    t=report['test_run'];assert t['rc']==0
    raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(raw)==t['stdout_bytes'] and sha(raw)==t['stdout_sha256'];return json.loads(raw)
packets=old_payload(read(ingress,pins[ingress]))['packets']
packets.update({n:v['parent'] for n,v in old_payload(read(presence,pins[presence]))['synthetic_controls'].items()})
expected=[];proved=blocked=0
for n in old['case_order']:
    case=old['cases'][n];ctx=case['context'];packet=packets[n]
    assert digest(packet)==ctx['input_packet_sha256']
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for role,raw in buffers.items():assert packet['manifest']['buffers'][role]=={'bytes':len(raw),'sha256':sha(raw)}
    meta=json.loads(buffers['input_metadata_json']);snap=json.loads(buffers['original_scene_json'])
    assert sha(buffers['original_scene_json'])==ctx['original_snapshot_sha256']
    assert meta['source_order']==ctx['source_order']==[s['id'] for s in snap['sources']]
    assert ctx['assignments']==meta['explicit_group_contract']['assignments']
    assert [[g['port'],g['coherence_group']] for g in case['groups']]==ctx['groups']
    for gi,g in enumerate(case['groups']):
        refs=[a for a in ctx['assignments'] if [a['port'],a['coherence_group']]==[g['port'],g['coherence_group']]]
        assert [a['source_id'] for a in refs]==g['source_order']
        out={'case_name':n,'group_index':gi,'port':g['port'],'coherence_group':g['coherence_group'],
             'complete_source_order':g['source_order'],'input_binding':{k:ctx[k] for k in KEYS},
             'retained_power_row_sha256':digest(g),'references':refs,
             'observable':'HOST_squared_modulus_of_complete_coherent_group',
             'units':'ORIGINAL-source-field-amplitude-squared',
             'group_combination':'none; separate outputs, no detector integration',
             'readout_operation':'identity_uint64_receipt; no new rounding','calibration':None,
             'area_integration':None,'exposure':None,'gain':None,'offset':None,'quantization':None,'budget_allocation_INPUT':None}
        expected.append(out)
        actual=plan['outputs'][len(expected)-1];row=result['outputs'][len(expected)-1]
        assert digest(actual)==digest(out) and type(actual['group_index']) is int
        assert row['output_contract_sha256']==digest(out) and row['retained_power_row_sha256']==digest(g)
        assert (row['case_name'],row['group_index'])==(n,gi)
        assert row['readout_status']=='STOP' and row['budget_allocation_INPUT_present'] is False
        for k in false:assert row[k] is False,k
        assert row['restricted_power_proof_available'] is g[FLAG]
        if g[FLAG]:
            proved+=1;assert n in ('positive','negative') and g['source_order']==['s']
            words=[q['retained_power_uint64'] for q in g['proof']['retained_corner_checks']]
            assert len(words)==4 and len(set(words))==1
            assert row['retained_power_uint64_decimal']==str(words[0])
            assert row['reason']=='missing source/reduction/power/readout INPUT allocations and executed readout receipt'
        else:
            blocked+=1;assert row['retained_power_uint64_decimal'] is None and row['reason']==g['reason']
assert len(plan['outputs'])==len(result['outputs'])==len(expected)==17
assert (proved,blocked)==(2,15)
assert (result['restricted_power_receipts_available'],result['upstream_unproved_groups'],result['all_readouts_stopped'])==(2,15,17)
assert result['inherited_pins_verified']==293 and result['retained_unit_STOPs']==14 and result['nonzero_domains_not_refined']==2
assert result['retained_zero_budget_FAIL_controls']==old['retained_zero_budget_FAIL_controls']
for cases in result['retained_zero_budget_FAIL_controls'].values():
    for v in cases.values():assert v['group_statuses']==['FAIL'] and v['accepted_groups']==[False]
assert result['new_RN_or_scene_producer_executions']==0 and result['unmeasured_cost_stages']==list(STAGES)
assert len(data['rejections'])==len({v['label'] for v in data['rejections']})==43
assert all(type(v['reason']) is str and v['reason'] for v in data['rejections'])
print(json.dumps({'PASS':True,'pins':len(pins),'complete_outputs':17,'readouts_STOP':17,
 'restricted_power_receipts_available':2,'upstream_unproved_groups':15,'unmeasured_cost_stages':11,
 'rejections':43,'new_RN_or_scene_producer_executions':0,'detector_or_GPU_admission':False},sort_keys=True))
