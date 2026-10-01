"""Declared grouping of scene-derived terminal fields, synthetic RN64 only."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from axial_geometry_unit_cpu_v1 import report,digest
from axial_source_product_rn64_cpu_v1 import payload
from axial_geometry_source_cpu_v1 import cap
from axial_unit_rn64_cpu_v1 import component64
from axial_relative_gate_cpu_v1 import ratio,_relative
from axial_reduction_detector_rn64_cpu_v1 import Nodes,detector_words,MODEL as NUMERIC
from axial_reduction_argument_rn64_cpu_v1 import CachedNodes
ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-GEOMETRY-SOURCE-001-CODEX.json'
SHA='75b6c5dd33596707875e228acd032997c15b7045c9eac5bde8237831207e8d5e'
CACHE='coordinacion/respuestas/AXIAL-REDUCTION-ARGUMENT-RN64-001-CODEX.json'
CACHE_SHA='b355de12848533fb13c02b171f7459c1c8ad2689ae2f65e11f3e81cf793dfe24'
CODE='Blender/benchmarks/capacity_audit/axial_reduction_detector_rn64_cpu_v1.py'
MODEL='scene-terminal-declared-group-reduction-detector-RN64-CPU-v1'
DECLARATION='explicit CPU coherence hypothesis; not measured scene/native/physical coherence'
LIMITS=('field_L1','power','relative_field','relative_power')

def put(bank,key,m):
    if key in bank and digest(bank[key])!=digest(m):raise ValueError('conflicting pure cache')
    bank[key]=deepcopy(m)

def load_retained():
    r=report(REPORT,SHA);old=report(CACHE,CACHE_SHA)
    if r['id']!='AXIAL-GEOMETRY-SOURCE-001' or r['test_run']['rc']!=0 or old['run']['rc']!=0:
        raise ValueError('retained identity/status mismatch')
    pins=dict(r['code_doc_sha256'],**{REPORT:SHA})
    if pins[CODE]!=old['code_doc_sha256'][CODE]:raise ValueError('cached numeric code mismatch')
    steps={};detectors={};adds={}
    for c in payload(old)['audit']['cases'].values():
        if not c['scene_field_reduced']:continue
        sig=c['cache_signature']
        if sig['model']!=NUMERIC or sig['reducer_code_sha256']!=pins[CODE]:
            raise ValueError('cached numeric model/signature mismatch')
        terminals=sig['ordered_terminals'];byid={t['source_id']:t for t in terminals}
        if len(byid)!=len(terminals):raise ValueError('cached duplicate source ID')
        for port,p in c['ports'].items():
            for group,g in p['groups'].items():
                order=[t['source_id'] for t in terminals if t['port']==port and t['coherence_group']==group]
                if order!=g['source_ids'] or order!=[s['source_id'] for s in g['steps']]:
                    raise ValueError('cached ordered group coverage mismatch')
                acc=[0,0]
                for step in g['steps']:
                    words=byid[step['source_id']]['terminal_uint64'];trace=step['operations']
                    if len(trace)!=2:raise ValueError('two-node reduction step required')
                    put(steps,tuple(acc+words),trace);acc=[n['output_uint64'] for n in trace]
                if acc!=g['output_uint64']:raise ValueError('cached group output mismatch')
                put(detectors,tuple(acc),g['detector'])
            prev=0
            for node in p['add_steps']:
                q=F(*node['inputs_rational'][1])
                matches={g['detector']['output_uint64'] for g in p['groups'].values() if F(*g['detector']['observed_power_rational'])==q}
                if len(matches)!=1:raise ValueError('unambiguous cached detector word required')
                put(adds,(prev,matches.pop()),[node]);prev=node['output_uint64']
    return pins,payload({'run':r['test_run']})['audit']['cases'],steps,detectors,adds

def contract_for(c,groups,limits):
    """Explicit host contract helper; caller must declare groups and all caps."""
    if type(groups) is not dict or set(groups)!=set(c['source_order']):
        raise ValueError('complete source grouping declaration required')
    if any(type(g) is not str or not g or len(g)>64 for g in groups.values()):
        raise ValueError('bounded explicit group names required')
    binding=c['original_scene_binding_sha256']
    return {'scene_binding_sha256':binding,'grouping_provenance':DECLARATION,'limits':limits,
            'assignments':[{'source_id':sid,'port':'D','coherence_group':groups[sid],
                            'source_phase_reference_id':'original-source-zero:'+binding+':'+sid,
                            'common_phase_reference_id':'declared-common-source-gauge:'+binding+':'+groups[sid]}
                           for sid in c['source_order']]}

def compose(c,contract,steps,detectors,adds,code_sha):
    binding=c['original_scene_binding_sha256'];ids=c['source_order']
    if type(contract) is not dict or contract.get('scene_binding_sha256')!=binding or contract.get('grouping_provenance')!=DECLARATION:
        raise ValueError('explicit binding-linked CPU coherence hypothesis required')
    rows=contract.get('assignments')
    if not isinstance(rows,list) or [r['source_id'] for r in rows]!=ids or ids!=[p['source_id'] for p in c['paths']]:
        raise ValueError('complete ordered unique source assignment required')
    if not ids or len(set(ids))!=len(ids):raise ValueError('unique nonempty source IDs required')
    lim=contract.get('limits')
    if type(lim) is not dict or set(lim)!=set(LIMITS):raise ValueError('explicit complete group/port caps; no defaults')
    limits={k:cap(lim[k]) for k in LIMITS}
    for row in rows:
        group=row['coherence_group'];sid=row['source_id']
        if type(group) is not str or not group or len(group)>64 or row['port']!='D':
            raise ValueError('bounded declared group and explicit terminal D required')
        if row['source_phase_reference_id']!='original-source-zero:'+binding+':'+sid or row['common_phase_reference_id']!='declared-common-source-gauge:'+binding+':'+group:
            raise ValueError('declared source/common phase reference mismatch')
    out={'original_scene_binding_sha256':binding,'source_product_case_sha256':digest(c),
         'contract':{**deepcopy(contract),'limits':{k:ratio(v) for k,v in limits.items()}},
         'previous_source_product_accepted':c['accepted_source_product_absolute_CPU_only'],
         'accepted_reduction_detector_CPU_only':False,'scene_field_reduced':False,'detector_evaluated':False,
         'coherence_authenticated':False,'accepted_full_field_pipeline':False,'ports':{},
         'new_RN64_operations':0,'cached_RN64_operations_NOT_executed':0,'cache_signatures':[]}
    if not c['accepted_source_product_absolute_CPU_only']:
        return {**out,'reason':'retained scene/source/unit/product rejected; no reduction/detector'}
    groups={}
    for p,row in zip(c['paths'],rows):
        if not p['accepted_source_product_absolute_CPU_only'] or p['source_id']!=row['source_id'] or p['port']!=row['port'] or p['phase_reference_id']!=row['source_phase_reference_id']:
            raise ValueError('retained terminal source/port/reference mismatch')
        words=p['measurement']['output_uint64'];z=list(map(component64,words))
        if [ratio(v) for v in z]!=p['measurement']['observed_path_field_rational']:
            raise ValueError('retained terminal word/decode mismatch')
        group=row['coherence_group'];g=groups.setdefault(group,{'words':[0,0],'source_ids':[],'steps':[],
            'path_bound':F(0),'red_bound':F(0),'common_phase_reference_id':row['common_phase_reference_id']})
        key=tuple(g['words']+words);reuse=key in steps;o=CachedNodes(steps[key]) if reuse else Nodes()
        result=[];delta=[]
        for j in range(2):
            v,d,w=o.rn(component64(g['words'][j]),z[j],'add','reduce.'+str(j));result.append(w);delta.append(d)
        out['cached_RN64_operations_NOT_executed' if reuse else 'new_RN64_operations']+=2
        out['cache_signatures'].append({'kind':'reduce2','input_uint64':list(key),'model':NUMERIC,'code_sha256':code_sha,'report_sha256':CACHE_SHA if reuse else None})
        g['words']=result;g['source_ids'].append(p['source_id']);g['steps'].append({'source_id':p['source_id'],'operations':o.trace,'cache_reused':reuse})
        g['path_bound']+=F(*p['composed_path_field_error_L1']);g['red_bound']+=sum(map(abs,delta),F(0))
    power=F(0);power_word=0;total_bound=F(0);valid=True
    port={'groups':{},'add_steps':[]}
    for group,g in groups.items():
        y=list(map(component64,g['words']));e=g['path_bound']+g['red_bound'];norm=sum(map(abs,y),F(0))
        relative=_relative(norm,e,limits['relative_field'])
        key=tuple(g['words']);reuse=key in detectors
        d=deepcopy(detectors[key]) if reuse else detector_words(g['words'],detector_model=NUMERIC)
        out['cached_RN64_operations_NOT_executed' if reuse else 'new_RN64_operations']+=3
        out['cache_signatures'].append({'kind':'detector3','input_uint64':list(key),'model':NUMERIC,'code_sha256':code_sha,'report_sha256':CACHE_SHA if reuse else None})
        transport=2*norm*e+e*e;pb=transport+F(*d['detector_error_upper_rational']);q=F(*d['observed_power_rational'])
        key=(power_word,d['output_uint64']);reuse=key in adds;o=CachedNodes(adds[key]) if reuse else Nodes()
        power,delta,power_word=o.rn(power,q,'add','port.incoherent_sum')
        out['cached_RN64_operations_NOT_executed' if reuse else 'new_RN64_operations']+=1
        out['cache_signatures'].append({'kind':'power_add1','input_uint64':list(key),'model':NUMERIC,'code_sha256':code_sha,'report_sha256':CACHE_SHA if reuse else None})
        total_bound+=pb+abs(delta);port['add_steps'].append({'coherence_group':group,'operations':o.trace,'cache_reused':reuse})
        port['groups'][group]={'source_ids':g['source_ids'],'common_phase_reference_id':g['common_phase_reference_id'],
            'output_uint64':g['words'],'observed_field_rational':[ratio(v) for v in y],'steps':g['steps'],
            'path_error_L1':ratio(g['path_bound']),'reduction_error_L1':ratio(g['red_bound']),
            'composed_field_error_L1':ratio(e),'field_absolute_pass':e<=limits['field_L1'],
            'relative_field':relative,'detector':d,'detector_cache_reused':tuple(g['words']) in detectors,
            'transport_power_error':ratio(transport),'group_power_error':ratio(pb)}
        valid=valid and e<=limits['field_L1'] and relative['relative_budget_satisfied']
    relative=_relative(power,total_bound,limits['relative_power'])
    port.update(observed_power_uint64=power_word,observed_power_rational=ratio(power),
                composed_power_error=ratio(total_bound),power_absolute_pass=total_bound<=limits['power'],relative_power=relative)
    valid=valid and port['power_absolute_pass'] and relative['relative_budget_satisfied']
    out.update(ports={'D':port},scene_field_reduced=True,detector_evaluated=True,accepted_reduction_detector_CPU_only=valid)
    return out

def audit_scene_reduction(*,case_names,case_contracts,reduction_model):
    if reduction_model!=MODEL:raise ValueError('explicit scene reduction-detector CPU model required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):
        raise ValueError('explicit unique retained cases required')
    pins,cases,steps,detectors,adds=load_retained()
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    if type(case_contracts) is not dict or set(case_contracts)!=set(case_names):raise ValueError('explicit complete case contracts required')
    result={n:compose(cases[n],case_contracts[n],steps,detectors,adds,pins[CODE]) for n in case_names}
    return {'model':MODEL,'cases':result,'pins_verified':pins,'retained_source_report_sha256':SHA,
            'cache_report_sha256':CACHE_SHA,'new_RN64_operations':sum(c['new_RN64_operations'] for c in result.values()),
            'cached_RN64_operations_NOT_executed':sum(c['cached_RN64_operations_NOT_executed'] for c in result.values()),
            'GPU_executed':False,'ALU_executed':False,'native_reduction_detector_implemented':False,
            'execution_authenticated':False,'coherence_authenticated':False,'accepted_full_field_pipeline':False,
            'native_promotion_allowed':False,'geometry_unit_source_or_producer_rerun':False,
            'cost_scope':'changed pure RN64 reduction/detector/add nodes only; identical model/code/word cache NOT executed; IO/RAM/build/guard/energy/upstream/full costs excluded'}
