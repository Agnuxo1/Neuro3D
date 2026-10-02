"""Opt-in HOST power on pinned retained group corners; not a complete detector."""
from copy import deepcopy
from fractions import Fraction as F
import struct
import axial_source_budget_gate_HOST_v1 as receipts
import axial_amplitude_allocation_HOST_v1 as allocation

MODEL='axial-retained-group-power-3RN64-HOST-v1'
UNITS='ORIGINAL-group-power-absolute'
PREVIOUS='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
PREVIOUS_SHA='44e1af7a17f3fdb9577d274dc001212f9cefe7ea17af7548c9ba5f7f113a942d'
FIELD_FLAG='accepted_retained_corner_group_reduction_CPU_only'
FLAG='accepted_retained_corner_group_power_CPU_only'
VARIANTS=('missing','explicit_synthetic_INPUT_controls','missing_stage','zero_source')
FALSE=('accepted_full_field_pipeline','detector_evaluated','remaining_stages_error_proved',
       'execution_authenticated','coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission')

def require(ok,why):
    if not ok:raise ValueError(why)

def pair(v):return [v.numerator,v.denominator]

def decode(w):
    require(type(w) is int and 0<=w<2**64,'finite uint64 word required')
    e=(w>>52)&2047;m=w&((1<<52)-1);require(e<2047,'nonfinite word')
    if e:m|=1<<52
    return (-1 if w>>63 else 1)*F(m)*F(2)**(e-1075 if e else -1074)

def rn_node(a,b,op):
    left=decode(a);right=decode(b);exact=left*right if op=='mul' else left+right
    # Graph only squares and addition of nonnegative squares, all zero outputs +0.
    require(exact>=0,'nonnegative power graph')
    try:word=struct.unpack('<Q',struct.pack('<d',float(exact)))[0]
    except (OverflowError,struct.error) as exc:raise ValueError('power RN64 overflow') from exc
    value=decode(word);require(value>=0,'nonnegative rounded power')
    return {'op':op,'left_uint64':a,'right_uint64':b,'output_uint64':word,
            'exact_rational':pair(exact),'rounding_error_abs':pair(abs(value-exact))}

def measure_words(words,field_bound_L1,*,model):
    """Synthetic bit primitive, never caller field data as scene admission."""
    require(model==MODEL,'explicit power HOST model')
    require(type(words) is list and len(words)==2,'two complex component words')
    r,i=[decode(w) for w in words];bound=allocation.rational(field_bound_L1)
    re=rn_node(words[0],words[0],'mul');im=rn_node(words[1],words[1],'mul')
    total=rn_node(re['output_uint64'],im['output_uint64'],'add')
    trace=[re,im,total];rn=sum((allocation.rational(t['rounding_error_abs']) for t in trace),F(0))
    represented=r*r+i*i;observed=decode(total['output_uint64'])
    require(abs(observed-represented)<=rn,'three-node power RN error invariant')
    magnitude=max(abs(r),abs(i))
    propagation=2*magnitude*bound+bound*bound
    combined=propagation+rn
    margin=magnitude-bound
    lower=margin*margin if margin>0 else F(0)
    return {'input_uint64':list(words),'input_field_L1_error_bound':pair(bound),
            'observed_power_uint64':total['output_uint64'],'observed_power_rational':pair(observed),
            'represented_input_power_exact':pair(represented),'trace':trace,'RN64_operations':3,
            'actual_error_abs_to_represented_power':pair(abs(observed-represented)),
            'field_to_power_error_abs_bound':pair(propagation),'power_RN64_error_abs_bound':pair(rn),
            'combined_error_abs_to_ORIGINAL_power_bound':pair(combined),
            'ORIGINAL_power_lower_bound':pair(lower),
            'relative_power_error_bound':pair(combined/lower) if lower else None,
            'relative_scope':'ORIGINAL denominator lower bound; absent when ORIGINAL may be zero, no epsilon',
            'scope':'HOST arithmetic primitive only, not scene evidence'}

def load_retained():
    report=allocation.parse(receipts.read(PREVIOUS,PREVIOUS_SHA))
    require(report['task_id']=='AXIAL-GROUP-REDUCTION-HOST-001','retained reduction ID')
    pins=receipts.pins_from(report);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():receipts.read(p,h)
    d=receipts.payload(report)['data'];variants={v:d[v]['cases'] for v in VARIANTS}
    ingress=receipts.INGRESS;presence=receipts.PRESENCE
    packets=receipts.payload(allocation.parse(receipts.read(ingress,pins[ingress])))['packets']
    controls=receipts.payload(allocation.parse(receipts.read(presence,pins[presence])))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    require(set(packets)==set(variants['missing'])==set(variants['explicit_synthetic_INPUT_controls']),'retained case coverage')
    return packets,variants,pins

def validate_plan(ctx,retained,plan,variant):
    if plan is None:return {'power_INPUT_valid':False,'reason':'missing explicit power INPUT allocation; absent is not zero'}
    require(type(plan) is dict and set(plan)=={'model','units','context_sha256','retained_variant',
            'field_allocation_INPUT_sha256','field_reduction_stage_INPUT_sha256','groups'},
            'power INPUT whitelist; no values or gates supplied')
    require(plan['model']==MODEL and plan['units']==UNITS and plan['retained_variant']==variant and
            plan['context_sha256']==allocation.digest(ctx),'power model/units/variant/INPUT context')
    a=retained['allocation_result'];s=retained['stage_result']
    require(a['allocation_INPUT_valid'] is True and s['stage_INPUT_valid'] is True,'explicit upstream INPUT plans required')
    require(plan['field_allocation_INPUT_sha256']==a['allocation_sha256'] and
            plan['field_reduction_stage_INPUT_sha256']==s['stage_plan_sha256'],'exact field source/reduction INPUT SHA')
    groups=plan['groups']
    require(type(groups) is list and len(groups)==len(ctx['groups']),'complete power group plans')
    require(all(type(g) is dict and set(g)=={'port','coherence_group','field_to_power_cap_abs',
            'power_RN64_cap_abs','other_power_stages_reserved_abs','relative_power_cap'} for g in groups),
            'power group INPUT whitelist')
    require([[g['port'],g['coherence_group']] for g in groups]==ctx['groups'],'ordered exact power port/group')
    power_cap=allocation.rational(ctx['unchanged_limits']['power'])
    relative_cap=allocation.rational(ctx['unchanged_limits']['relative_power'])
    for g in groups:
        charge=sum((allocation.rational(g[k]) for k in
                   ('field_to_power_cap_abs','power_RN64_cap_abs','other_power_stages_reserved_abs')),F(0))
        require(charge<=power_cap,'power-stage cups plus reserve exceed unchanged ORIGINAL power cap')
        require(allocation.rational(g['relative_power_cap'])<=relative_cap,'relative power cup exceeds unchanged ORIGINAL cap')
    return {'power_INPUT_valid':True,'power_plan_sha256':allocation.digest(plan),'groups':deepcopy(groups),
            'units':UNITS,'unchanged_power_cap_abs':pair(power_cap),'unchanged_relative_power_cap':pair(relative_cap),
            'other_power_stages_error_proved':False,'field_L1_reserve_used_as_power_budget':False}

def audit_group_power_HOST(case_names,power_plans_by_case,*,retained_variant,model):
    """Only pinned case selection, explicit receipt variant and static power INPUT admitted."""
    require(model==MODEL,'explicit power HOST model')
    require(type(retained_variant) is str and retained_variant in VARIANTS,'explicit pinned receipt variant')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded ordered unique case names')
    require(type(power_plans_by_case) is dict and set(power_plans_by_case)==set(case_names),'complete power INPUT map including None')
    packets,variants,pins=load_retained();prior=variants[retained_variant]
    require(set(case_names)<=set(prior),'unknown case in selected pinned receipt variant')
    cases={};ops=0;corners=0
    for n in case_names:
        old=prior[n];ctx=allocation.context_from_packet(packets[n],allocation.digest(packets[n]),model=allocation.MODEL)
        require(ctx==old['context'],'fresh INPUT / retained reduction context')
        plan=validate_plan(ctx,old,power_plans_by_case[n],retained_variant)
        require([[g['port'],g['coherence_group']] for g in old['groups']]==ctx['groups'],'retained group coverage/order')
        groups=[]
        for index,g in enumerate(old['groups']):
            row={'port':g['port'],'coherence_group':g['coherence_group'],'source_order':deepcopy(g['source_order']),
                 'retained_group_row_sha256':allocation.digest(g),FLAG:False,'power_evaluated_HOST':False,
                 **dict.fromkeys(FALSE,False)}
            if g[FIELD_FLAG] is not True:
                row.update(status='STOP',reason=g['reason'],reason_provenance='unchanged_retained_field_group_STOP',
                           retained_field_status=g['status'])
                if 'blocked_source_ids' in g:row['blocked_source_ids']=deepcopy(g['blocked_source_ids'])
            elif not plan['power_INPUT_valid']:
                row.update(status='STOP',reason=plan['reason'],reason_provenance='missing_power_INPUT')
            else:
                bound=g['error_L1_to_ORIGINAL_group_corner_sum_bound'];results=[]
                propagation=F(0);rounding=F(0);combined=F(0);relative=F(0);zero_reference=False
                for c in g['corner_sums']:
                    value=measure_words(c['sum_uint64'],bound,model=model)
                    results.append({'retained_field_corner_sha256':allocation.digest(c),
                                    'corner_indices':deepcopy(c['corner_indices']),**value})
                    propagation=max(propagation,allocation.rational(value['field_to_power_error_abs_bound']))
                    rounding=max(rounding,allocation.rational(value['power_RN64_error_abs_bound']))
                    combined=max(combined,allocation.rational(value['combined_error_abs_to_ORIGINAL_power_bound']))
                    if value['relative_power_error_bound'] is None:zero_reference=True
                    else:relative=max(relative,allocation.rational(value['relative_power_error_bound']))
                    ops+=3;corners+=1
                caps=plan['groups'][index];pc=allocation.rational(caps['field_to_power_cap_abs'])
                rc=allocation.rational(caps['power_RN64_cap_abs']);relc=allocation.rational(caps['relative_power_cap'])
                absolute_ok=(propagation<=pc and rounding<=rc and combined<=allocation.rational(ctx['unchanged_limits']['power']))
                relative_ok=not zero_reference and relative<=relc and relative<=allocation.rational(ctx['unchanged_limits']['relative_power'])
                accepted=absolute_ok and relative_ok
                row.update(status='STOP' if zero_reference else ('PASS_PARTIAL' if accepted else 'FAIL'),
                           reason='ORIGINAL may be zero; relative power denominator not proved positive' if zero_reference else
                           ('retained-corner power fits explicit absolute/relative INPUT cups' if accepted else
                            'retained-corner power exceeds explicit absolute/relative INPUT cups'),
                           power_evaluated_HOST=True,power_corners=results,field_to_power_error_abs_bound=pair(propagation),
                           power_RN64_error_abs_bound=pair(rounding),combined_error_abs_to_ORIGINAL_power_bound=pair(combined),
                           relative_power_error_bound=None if zero_reference else pair(relative),
                           absolute_power_gate=absolute_ok,relative_power_gate=relative_ok,
                           unchanged_original_limits=deepcopy(ctx['unchanged_limits']),**{FLAG:accepted})
            groups.append(row)
        cases[n]={'context':ctx,'retained_variant':retained_variant,'power_plan_result':plan,'groups':groups,
                  'retained_source_rows_sha256':[allocation.digest(s) for s in old['sources']],
                  'retained_source_STOP_FAILs':[{'source_id':s['source_id'],'status':s['status'],'reason':s['reason']}
                                               for s in old['sources'] if s['status'] in ('STOP','FAIL')],
                  FLAG:all(g[FLAG] for g in groups),**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'units':UNITS,'case_order':list(case_names),'retained_variant':retained_variant,'cases':cases,
            'inherited_pins_verified':len(pins),'power_corner_evaluations':corners,'new_RN64_power_operations':ops,
            'new_field_products':0,'new_field_reductions':0,'new_trigonometry':0,'new_ray_traces':0,
            **dict.fromkeys(FALSE,False),'field_L1_reserve_used_as_power_budget':False,
            'scope':'squared modulus of restricted retained HOST group corners; no full detector, continuous scene or incoherent-port sum',
            'cost_scope':'3 new power RN64 per corner; exact bounds/receipts/hash/INPUT extra, NOT complete costs or native timing'}
