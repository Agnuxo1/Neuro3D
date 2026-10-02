"""Opt-in closure ledger: retained corner gates are not whole-domain evidence."""
from copy import deepcopy
from fractions import Fraction as F
import struct
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-retained-stage-domain-closure-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-GROUP-RELATIVE-HOST-001-CODEX.json'
PREVIOUS_SHA='997acd5255a9b3b0b115316f4c28cfeefc2b4459fff621edacb7dc42c39c7959'
FIELD='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
POWER='coordinacion/respuestas/AXIAL-GROUP-POWER-HOST-001-CODEX.json'
TREE='coordinacion/respuestas/AXIAL-TREE-LINEAGE-HOST-001-CODEX.json'
PARTIAL='accepted_retained_corner_field_power_limits_CPU_only'
TREE_FLAG='tree_lineage_matches_restricted_CPU_only'
STAGES=('restricted_geometry_lineage','source_error_entire_domain','group_RN_error_entire_domain',
        'power_error_entire_domain','ORIGINAL_reference_lower_entire_domain',
        'remaining_field_stage_error','remaining_power_stage_error')
VARIANTS=('missing','explicit_synthetic_INPUT_controls','zero_absolute','zero_relative')
FALSE=('stage_closure_proved','remaining_stages_error_proved','accepted_full_field_pipeline','detector_evaluated',
       'execution_authenticated','coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission')
def require(ok,why):
    if not ok:raise ValueError(why)
def pair(x):return [x.numerator,x.denominator]
def decode(w):
    require(type(w) is int and 0<=w<2**64,'uint64 finite word')
    e=(w>>52)&2047;m=w&((1<<52)-1);require(e<2047,'nonfinite word')
    if e:m+=1<<52
    return (-1 if w>>63 else 1)*F(m)*F(2)**(e-1075 if e else -1074)
def reserved_stage_obligation(reserve,*,units,model):
    """Synthetic contract primitive; a reservation, even zero, contains no proof."""
    require(model==MODEL and units in ('field_L1','power_abs'),'explicit model and separate units')
    if reserve is not None:allocation.rational(reserve)
    return {'reserved':deepcopy(reserve),'units':units,'proved':False,
            'reason':'reservation is INPUT accounting, not error evidence; absent or zero cannot close stage'}
def _round_receipt(op,left,right):
    a,b=decode(left),decode(right);exact=a+b if op=='add' else a*b
    out=struct.unpack('<Q',struct.pack('<d',float(exact)))[0]
    return {'op':op,'left_uint64':left,'right_uint64':right,'output_uint64':out,
            'exact_rational':pair(exact),'RN_error_abs':pair(abs(decode(out)-exact))}
def synthetic_domain_counterexamples(*,model):
    """Eight new tiny synthetic RN nodes, not a scene computation or previous replay."""
    require(model==MODEL,'explicit model for synthetic controls')
    one=0x3ff0000000000000;two=0x4000000000000000;inside=one+1
    square=[_round_receipt('mul',x,x) for x in (one,two)]
    addition=[_round_receipt('add',a,b) for a,b in ((one,one),(one,two),(two,one),(two,two))]
    return {'square':{'label':'SYNTHETIC_NOT_SCENE','corners':square,'interior':_round_receipt('mul',inside,inside),
                      'box_real':[pair(F(1)),pair(F(2))],'corner_RN_bound':[0,1],
                      'reason':'exact endpoint squares do not bound RN error at interior'},
            'sum':{'label':'SYNTHETIC_NOT_SCENE','corners':addition,'interior':_round_receipt('add',inside,one),
                   'box_each_source':[pair(F(1)),pair(F(2))],'corner_RN_bound':[0,1],
                   'reason':'exact endpoint sums do not bound RN error at interior'},
            'reference':{'label':'SYNTHETIC_NOT_SCENE','real_interval':[[-1,1],[1,1]],
                         'observed_corner_L1':[[1,1],[1,1]],'corner_error_bound':[0,1],
                         'corner_ORIGINAL_lower':[[1,1],[1,1]],'interior_original_field':[0,1],
                         'entire_domain_original_lower':[0,1],'reason':'positive corner denominators do not imply interior nonzero'},
            'synthetic_RN_nodes':8,'scope':'counterexamples to a GENERAL inference, not failures of any retained scene'}
def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-GROUP-RELATIVE-HOST-001','retained task identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    data=io.payload(r)['data']
    f=io.payload(allocation.parse(io.read(FIELD,pins[FIELD])))['data']
    p=io.payload(allocation.parse(io.read(POWER,pins[POWER])))['data']
    tree=io.payload(allocation.parse(io.read(TREE,pins[TREE])))['data']['audit']['cases']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:c['parent'] for n,c in controls.items()})
    return packets,data,f,p,tree,pins
def audit_stage_closure_HOST(case_names,*,retained_variant,model):
    """Pinned evidence only. No caller claim, proof, reservation, cap or scope override."""
    require(model==MODEL,'explicit closure model')
    require(type(retained_variant) is str and retained_variant in VARIANTS,'pinned variant')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique case names')
    packets,relative,fields,powers,trees,pins=load_retained()
    selected=relative[retained_variant]['cases']
    require(set(case_names)<=set(selected),'known cases in selected retained variant')
    out={};total=0;available=0
    for n in case_names:
        r=selected[n];p=powers[retained_variant]['cases'][n];f=fields[p['retained_variant']]['cases'][n];t=trees[n]
        ctx=allocation.context_from_packet(packets[n],allocation.digest(packets[n]),model=allocation.MODEL)
        require(ctx==r['context']==p['context']==f['context'],'same fresh INPUT, field, power and relative context')
        require(t['input_packet_sha256']==ctx['input_packet_sha256'],'same tree INPUT')
        require(type(t[TREE_FLAG]) is bool,'strict tree scope flag')
        if t[TREE_FLAG]:require(t['context']==ctx,'tree context')
        require([s['source_id'] for s in f['sources']]==ctx['source_order'],'complete field source coverage/order')
        require([[g['port'],g['coherence_group']] for g in r['groups']]==ctx['groups']
                ==[[g['port'],g['coherence_group']] for g in f['groups']]
                ==[[g['port'],g['coherence_group']] for g in p['groups']],'complete group coverage/order')
        for k in FALSE[1:]:require(r[k] is False,'retained scope is partial: '+k)
        groups=[]
        for i,(rg,fg,pg) in enumerate(zip(r['groups'],f['groups'],p['groups'])):
            require(rg['retained_field_group_sha256']==allocation.digest(fg)
                    and rg['retained_power_group_sha256']==allocation.digest(pg),'exact group predecessors')
            require(rg['source_order']==fg['source_order']==pg['source_order'],'complete group sources')
            require(type(rg[PARTIAL]) is bool and (rg['status']=='PASS_PARTIAL')==rg[PARTIAL],'partial flag/status')
            for k in FALSE[1:]:require(rg[k] is False,'no promoted group scope: '+k)
            tree_available=t[TREE_FLAG]
            if tree_available:
                require([s['source_id'] for s in t['sources']]==ctx['source_order'],'tree complete source IDs')
                require(all(s[TREE_FLAG] is True for s in t['sources']),'tree source flags')
            field_valid=f['stage_result']['stage_INPUT_valid'] is True
            field_reserved=f['stage_result']['groups'][i]['other_stages_reserved_L1'] if field_valid else None
            if field_valid:require(f['stage_result']['other_stages_error_proved'] is False,'field reserve not proof')
            power_valid=p['power_plan_result']['power_INPUT_valid'] is True
            power_reserved=p['power_plan_result']['groups'][i]['other_power_stages_reserved_abs'] if power_valid else None
            if power_valid:require(p['power_plan_result']['other_power_stages_error_proved'] is False,'power reserve not proof')
            refs={'restricted_geometry_lineage':{'report_path':TREE,'report_sha256':pins[TREE],'row_sha256':allocation.digest(t)},
                  'source_error_entire_domain':{'report_path':FIELD,'report_sha256':pins[FIELD],
                     'source_rows_sha256':[allocation.digest(s) for s in f['sources'] if s['source_id'] in rg['source_order']]},
                  'group_RN_error_entire_domain':{'report_path':FIELD,'report_sha256':pins[FIELD],'row_sha256':allocation.digest(fg)},
                  'power_error_entire_domain':{'report_path':POWER,'report_sha256':pins[POWER],'row_sha256':allocation.digest(pg)},
                  'ORIGINAL_reference_lower_entire_domain':{'report_path':PREVIOUS,'report_sha256':PREVIOUS_SHA,'row_sha256':allocation.digest(rg)},
                  'remaining_field_stage_error':{'report_path':FIELD,'report_sha256':pins[FIELD],'row_sha256':allocation.digest(f['stage_result'])},
                  'remaining_power_stage_error':{'report_path':POWER,'report_sha256':pins[POWER],'row_sha256':allocation.digest(p['power_plan_result'])}}
            obligations=[]
            for stage in STAGES:
                proved=tree_available if stage==STAGES[0] else False
                domain='restricted axial tree only' if stage==STAGES[0] else 'entire claimed field/reference domain, not corners'
                node={'stage_id':stage,'required_domain':domain,'evidence':refs[stage],
                      'proved_for_required_domain':proved,'status':'RETAINED_RESTRICTED_GEOMETRY' if proved else 'MISSING_REQUIRED_DOMAIN_EVIDENCE'}
                if stage==STAGES[5]:node['reservation']=reserved_stage_obligation(field_reserved,units='field_L1',model=model)
                if stage==STAGES[6]:node['reservation']=reserved_stage_obligation(power_reserved,units='power_abs',model=model)
                obligations.append(node);total+=1;available+=int(proved)
            row={'port':rg['port'],'coherence_group':rg['coherence_group'],'source_order':deepcopy(rg['source_order']),
                 'retained_relative_group_sha256':allocation.digest(rg),'retained_corner_limits_pass':rg[PARTIAL],
                 'retained_group_status':rg['status'],'retained_group_reason':rg['reason'],
                 'stage_obligations':obligations,'missing_stage_ids':[v['stage_id'] for v in obligations if not v['proved_for_required_domain']],
                 **dict.fromkeys(FALSE,False)}
            # No new proof checker exists for the remaining required domains.
            if rg[PARTIAL]:
                row.update(status='STOP',reason='corner limits fit but entire-domain and remaining-stage proofs are missing',
                           reason_provenance='new_stage_domain_coverage_requirement')
            else:row.update(status=rg['status'],reason=rg['reason'],reason_provenance='unchanged_retained_STOP_FAIL')
            groups.append(row)
        out[n]={'context':ctx,'retained_variant':retained_variant,'groups':groups,
                'retained_case_sha256':allocation.digest(r),'retained_source_STOP_FAILs':deepcopy(r['retained_source_STOP_FAILs']),
                **dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':list(case_names),'retained_variant':retained_variant,'cases':out,
            'required_stage_ids':list(STAGES),'inherited_pins_verified':len(pins),'obligations_checked':total,
            'restricted_geometry_obligations_available':available,'missing_obligations':total-available,
            'new_scene_RN_nodes':0,'new_scene_geometry_phase_field_power_computations':0,
            **dict.fromkeys(FALSE,False),
            'scope':'closure coverage ledger only; SHA identity not execution/coherence authentication; no new proof or GPU admission',
            'next_requirement':'explicit separately checked full-domain certificates; reserved zero and partial flags are not certificates'}
