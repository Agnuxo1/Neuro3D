"""Opt-in ORIGINAL relative-L1 gate on retained HOST corners; no field/power replay."""
from copy import deepcopy
from fractions import Fraction as F
import axial_source_budget_gate_HOST_v1 as receipts
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-retained-corner-relative-L1-ORIGINAL-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-GROUP-POWER-HOST-001-CODEX.json'
PREVIOUS_SHA='d6510bb52617324272bc47b45b2b2c09ecc4578e865b06f0fc1d332a51998763'
FIELD='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
FIELD_SHA='44e1af7a17f3fdb9577d274dc001212f9cefe7ea17af7548c9ba5f7f113a942d'
FIELD_FLAG='accepted_retained_corner_group_reduction_CPU_only'
POWER_FLAG='accepted_retained_corner_group_power_CPU_only'
FLAG='accepted_retained_corner_field_power_limits_CPU_only'
VARIANTS=('missing','explicit_synthetic_INPUT_controls','zero_absolute','zero_relative')
FALSE=('accepted_full_field_pipeline','remaining_stages_error_proved','detector_evaluated',
       'execution_authenticated','coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission')

def require(ok,why):
    if not ok:raise ValueError(why)

def pair(v):return [v.numerator,v.denominator]

def decode(w):
    require(type(w) is int and 0<=w<2**64,'finite uint64 word required')
    e=(w>>52)&2047;m=w&((1<<52)-1);require(e<2047,'nonfinite word')
    if e:m|=1<<52
    return (-1 if w>>63 else 1)*F(m)*F(2)**(e-1075 if e else -1074)

def relative_bound_words(words,field_error_L1,relative_cap,*,model):
    """Exact-rational primitive; no caller word/cap is scene admission."""
    require(model==MODEL,'explicit ORIGINAL relative-L1 HOST model')
    require(type(words) is list and len(words)==2,'two component words')
    values=[decode(w) for w in words];norm=sum(map(abs,values),F(0))
    bound=allocation.rational(field_error_L1);cap=allocation.rational(relative_cap)
    lower=max(F(0),norm-bound);relative=bound/lower if lower else None
    fits=relative is not None and relative<=cap
    return {'input_uint64':list(words),'observed_field_L1_exact':pair(norm),
            'field_error_L1_to_ORIGINAL_bound':pair(bound),'ORIGINAL_field_L1_lower_bound':pair(lower),
            'relative_field_L1_upper_bound':pair(relative) if relative is not None else None,
            'unchanged_relative_field_cap':pair(cap),'relative_field_gate_satisfied':fits,
            'status':'STOP' if relative is None else ('PASS_PARTIAL' if fits else 'FAIL'),
            'reason':'no positive ORIGINAL L1 lower bound; no epsilon' if relative is None else
                     ('relative field L1 bound fits cap' if fits else 'relative field L1 bound exceeds cap'),
            'metric':'relative complex L1 per group; ORIGINAL ideal L1 denominator',
            'new_RN_operations':0,'scope':'rational primitive only; not caller scene evidence'}

def load_retained():
    report=allocation.parse(receipts.read(PREVIOUS,PREVIOUS_SHA))
    require(report['task_id']=='AXIAL-GROUP-POWER-HOST-001','retained power ID')
    pins=receipts.pins_from(report);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():receipts.read(p,h)
    require(pins[FIELD]==FIELD_SHA,'retained field SHA')
    d=receipts.payload(report)['data'];powers={v:d[v]['cases'] for v in VARIANTS}
    f=receipts.payload(allocation.parse(receipts.read(FIELD,FIELD_SHA)))['data']
    fields={v:f[v]['cases'] for v in ('missing','explicit_synthetic_INPUT_controls','missing_stage','zero_source')}
    packets=receipts.payload(allocation.parse(receipts.read(receipts.INGRESS,pins[receipts.INGRESS])))['packets']
    controls=receipts.payload(allocation.parse(receipts.read(receipts.PRESENCE,pins[receipts.PRESENCE])))['synthetic_controls']
    packets.update({n:c['parent'] for n,c in controls.items()})
    return packets,fields,powers,pins

def audit_group_relative_HOST(case_names,*,retained_variant,model):
    """Only pinned names/variant/model; no caller fields, bounds, caps or changed receipts."""
    require(model==MODEL,'explicit ORIGINAL relative-L1 HOST model')
    require(type(retained_variant) is str and retained_variant in VARIANTS,'explicit pinned power variant')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded ordered unique cases')
    packets,fields,powers,pins=load_retained();prior=powers[retained_variant]
    require(set(case_names)<=set(prior),'unknown case in pinned variant')
    cases={};denominators=0
    for n in case_names:
        power=prior[n];fv=power['retained_variant'];require(fv in fields,'explicit retained field variant')
        field=fields[fv][n];packet=packets[n]
        ctx=allocation.context_from_packet(packet,allocation.digest(packet),model=allocation.MODEL)
        require(ctx==power['context']==field['context'],'fresh INPUT / field / power context')
        require(power['retained_source_rows_sha256']==[allocation.digest(s) for s in field['sources']],
                'retained field source coverage/receipt')
        require([[g['port'],g['coherence_group']] for g in power['groups']]==ctx['groups']
                ==[[g['port'],g['coherence_group']] for g in field['groups']],'exact group coverage/order')
        groups=[]
        for f,p in zip(field['groups'],power['groups']):
            require(p['retained_group_row_sha256']==allocation.digest(f) and p['source_order']==f['source_order'],
                    'power / field exact group receipt and complete source order')
            row={'port':f['port'],'coherence_group':f['coherence_group'],'source_order':deepcopy(f['source_order']),
                 'retained_field_group_sha256':allocation.digest(f),'retained_power_group_sha256':allocation.digest(p),
                 'field_relative_gate_evaluated':False,'field_relative_gates_satisfied':False,FLAG:False,
                 **dict.fromkeys(FALSE,False)}
            if f[FIELD_FLAG] is not True:
                row.update(status=p['status'],reason=p['reason'],reason_provenance='unchanged_retained_field_power_STOP')
                if 'blocked_source_ids' in p:row['blocked_source_ids']=deepcopy(p['blocked_source_ids'])
            else:
                bound=f['error_L1_to_ORIGINAL_group_corner_sum_bound'];cap=ctx['unchanged_limits']['relative_field']
                comparisons=[]
                for c in f['corner_sums']:
                    gate=relative_bound_words(c['sum_uint64'],bound,cap,model=model)
                    comparisons.append({'retained_field_corner_sha256':allocation.digest(c),
                                        'corner_indices':deepcopy(c['corner_indices']),**gate});denominators+=1
                relative_ok=all(c['relative_field_gate_satisfied'] for c in comparisons)
                absolute_ok=allocation.rational(bound)<=allocation.rational(ctx['unchanged_limits']['field_L1'])
                power_ok=p[POWER_FLAG] is True
                if power_ok:
                    require(p['absolute_power_gate'] is True and p['relative_power_gate'] is True and
                            p['unchanged_original_limits']==ctx['unchanged_limits'],'retained power ORIGINAL gates/limits')
                accepted=absolute_ok and relative_ok and power_ok
                row.update(field_relative_gate_evaluated=True,field_relative_gates_satisfied=relative_ok,
                           absolute_field_gate=absolute_ok,retained_absolute_relative_power_gates=power_ok,
                           field_relative_corners=comparisons,unchanged_original_limits=deepcopy(ctx['unchanged_limits']),
                           **{FLAG:accepted})
                if not power_ok:
                    row.update(status=p['status'],reason=p['reason'],reason_provenance='unchanged_retained_power_STOP_FAIL')
                elif any(c['status']=='STOP' for c in comparisons):
                    row.update(status='STOP',reason='ORIGINAL field L1 may be zero; no epsilon',reason_provenance='new_relative_ORIGINAL_reference_gate')
                else:
                    row.update(status='PASS_PARTIAL' if accepted else 'FAIL',
                               reason='all four ORIGINAL field/power limits fit retained corners only' if accepted else
                                      'ORIGINAL relative field or absolute field gate fails',
                               reason_provenance='exact_relative_L1_and_retained_power_gates')
            groups.append(row)
        cases[n]={'context':ctx,'retained_variant':retained_variant,'groups':groups,
                  'retained_source_STOP_FAILs':deepcopy(power['retained_source_STOP_FAILs']),
                  FLAG:all(g[FLAG] for g in groups),**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':list(case_names),'retained_variant':retained_variant,'cases':cases,
            'inherited_pins_verified':len(pins),'new_exact_relative_denominator_checks':denominators,
            'new_RN_operations':0,'new_field_products':0,'new_field_reductions':0,'new_power_operations':0,
            'new_trigonometry':0,'new_ray_traces':0,**dict.fromkeys(FALSE,False),
            'scope':'four limits at retained encoded HOST corners only; not full pipeline, continuous scene, stage closure or authorization',
            'cost_scope':'exact rational relative checks plus receipts/context/hash; no numerical field/power replay, NOT fullcost'}
