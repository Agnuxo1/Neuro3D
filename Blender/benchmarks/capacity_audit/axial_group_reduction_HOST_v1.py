"""Opt-in retained-corner group reduction; HOST RN64 only, never full pipeline admission."""
import base64
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import struct
import axial_source_budget_gate_HOST_v1 as receipts
import axial_amplitude_allocation_HOST_v1 as allocation

MODEL='axial-retained-corner-group-reduction-RN64-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-TREE-LINEAGE-HOST-001-CODEX.json'
PREVIOUS_SHA='e9ad9731436da1f75724354e8e6fb4fae9ed043d936a01a0752dc936abce7ae6'
MIRROR='coordinacion/respuestas/AXIAL-MIRROR-ZERO-HOST-001-CODEX.json'
MIRROR_SHA='5f5b8ce30a02a7b1a558d26ffbe5fd211d9fc9d78f9554456d93512f91d21586'
FLAG='accepted_retained_corner_group_reduction_CPU_only'
FALSE=('accepted_full_field_pipeline','amplitude_budget_accepted','remaining_stages_error_proved',
       'detector_evaluated','execution_authenticated','coherence_authenticated','native_kernel_implemented',
       'GPU_executed','GPU_job_admission')
SIGN=1<<63

def require(ok,why):
    if not ok:raise ValueError(why)

def pair(v):
    return [v.numerator,v.denominator]

def decode(w):
    require(type(w) is int and 0<=w<2**64,'finite uint64 word required')
    e=(w>>52)&2047;m=w&((1<<52)-1)
    require(e!=2047,'nonfinite word')
    p=e-1075 if e else -1074
    if e:m|=1<<52
    return (-1 if w&SIGN else 1)*F(m)*(F(2)**p)

def add_words(left,right):
    exact=decode(left)+decode(right)
    # RN-even binary64; zero keeps -0 only when both operands are negative zero.
    if not exact:word=SIGN if left==right==SIGN else 0
    else:
        try:word=struct.unpack('<Q',struct.pack('<d',float(exact)))[0]
        except (OverflowError,struct.error) as exc:raise ValueError('RN64 addition overflow') from exc
    rounded=decode(word)  # Reject nonfinite result; no clamping/FTZ.
    return {'left_uint64':left,'right_uint64':right,'output_uint64':word,
            'exact_sum':pair(exact),'rounding_error':pair(abs(rounded-exact))}

def reduce_words(source_words,*,model):
    """Bit arithmetic primitive, not public scene/gate evidence."""
    require(model==MODEL,'explicit HOST group-reduction model')
    require(type(source_words) is list and 1<=len(source_words)<=64,'bounded nonempty complete words')
    require(all(type(w) is list and len(w)==2 for w in source_words),'two component words per source')
    for w in source_words:
        for c in w:decode(c)
    current=list(source_words[0]);trace=[];error=F(0)
    for i,w in enumerate(source_words[1:],1):
        for c in range(2):
            op=add_words(current[c],w[c]);current[c]=op['output_uint64']
            op.update(source_index=i,component=c);trace.append(op);error+=allocation.rational(op['rounding_error'])
    exact=[sum((decode(w[c]) for w in source_words),F(0)) for c in range(2)]
    actual=sum((abs(decode(current[c])-exact[c]) for c in range(2)),F(0))
    require(actual<=error,'sequential additive L1 error invariant')
    return {'source_uint64':deepcopy(source_words),'sum_uint64':current,
            'sum_rational':[pair(decode(w)) for w in current],
            'exact_represented_sources_sum':[pair(v) for v in exact],
            'rounding_error_L1_bound':pair(error),'actual_error_L1_to_represented_sum':pair(actual),
            'RN64_additions':len(trace),'trace':trace,'scope':'primitive only, not scene evidence'}

def load_retained():
    r=allocation.parse(receipts.read(PREVIOUS,PREVIOUS_SHA))
    pins=receipts.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():receipts.read(p,h)
    require(pins[MIRROR]==MIRROR_SHA,'mirror lineage SHA')
    tree=receipts.payload(r)['data']['audit']['cases']
    reflected=receipts.payload(allocation.parse(receipts.read(MIRROR,MIRROR_SHA)))['data']['missing']['cases']
    packets,bare,_=receipts.load_retained()
    require(set(tree)==set(reflected)==set(packets)==set(bare),'retained complete case coverage')
    return packets,bare,reflected,tree,pins

def stage_plan(context,alloc,plan):
    if plan is None:return {'stage_INPUT_valid':False,'reason':'missing explicit reduction-stage INPUT; absent is not zero'}
    require(type(plan) is dict and set(plan)=={'model','units','context_sha256','source_allocation_sha256','groups'},
            'stage INPUT whitelist; no outputs or inferred defaults')
    require(plan['model']==MODEL and plan['units']==allocation.UNITS and
            plan['context_sha256']==allocation.digest(context),'stage model/units/INPUT context')
    require(alloc['allocation_INPUT_valid'] is True,'source allocation required before stage plan')
    require(plan['source_allocation_sha256']==alloc['allocation_sha256'],'stage/source allocation SHA')
    groups=plan['groups']
    require(type(groups) is list and len(groups)==len(context['groups']),'complete stage groups')
    require(all(type(g) is dict and set(g)=={'port','coherence_group','reduction_cap_L1','other_stages_reserved_L1'}
                for g in groups),'stage group whitelist')
    require([[g['port'],g['coherence_group']] for g in groups]==context['groups'],'ordered stage group identity')
    rows=[]
    for g,a in zip(groups,alloc['groups']):
        reduction=allocation.rational(g['reduction_cap_L1'])
        other=allocation.rational(g['other_stages_reserved_L1'])
        old=allocation.rational(a['remaining_stages_reserved_L1'])
        require(reduction+other<=old,'reduction plus other reservation exceeds existing stage reserve')
        rows.append({**deepcopy(g),'stage_unallocated_L1':pair(old-reduction-other)})
    return {'stage_INPUT_valid':True,'stage_plan_sha256':allocation.digest(plan),'groups':rows,
            'other_stages_error_proved':False}

def audit_group_reduction_HOST(case_names,allocations_by_case,stages_by_case,*,model):
    """Admission accepts only retained names and static INPUT plans, never caller products/gates."""
    require(model==MODEL,'explicit HOST group-reduction model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded ordered unique cases')
    require(type(allocations_by_case) is dict and type(stages_by_case) is dict and
            set(allocations_by_case)==set(stages_by_case)==set(case_names),'explicit complete plan maps including None')
    packets,bare,reflected,trees,pins=load_retained()
    require(set(case_names)<=set(packets),'unknown retained case')
    cases={};additions=0;corner_sums=0
    for name in case_names:
        packet=packets[name];old=bare[name];mirror=reflected[name];tree=trees[name]
        a=allocation.audit_allocation_HOST(packet,allocation.digest(packet),allocations_by_case[name],model=allocation.MODEL)
        ctx=a['context'];alloc=a['result'];stage=stage_plan(ctx,alloc,stages_by_case[name])
        require(ctx==mirror['context'],'fresh INPUT / retained mirror context')
        if 'context' in tree:require(ctx==tree['context'],'fresh INPUT / retained tree context')
        else:require(tree['tree_lineage_matches_restricted_CPU_only'] is False,'tree without INPUT context must STOP')
        require(tree['input_packet_sha256']==ctx['input_packet_sha256'],'retained tree INPUT packet SHA')
        for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
            require(old[k]==ctx[k],'bare product INPUT identity: '+k)
        require([s['source_id'] for s in mirror['sources']]==ctx['source_order'],'reflected source order')
        rows=[]
        for b,r,assignment in zip(old['sources'],mirror['sources'],ctx['assignments']):
            require(r['retained_product_row_sha256']==allocation.digest(b),'reflected/bare source receipt')
            require(r['phase_reference_id']==assignment['source_phase_reference_id'] and
                    r['terminal_reference_id']==assignment['terminal_reference_id'],'source and terminal gauge')
            row={'source_id':b['source_id'],'reflected_row_sha256':allocation.digest(r),
                 'source_budget_evaluated':False,'source_budget_fits':False}
            if not b['source_product_evaluated']:
                require(r['reason']==b['reason'],'preserved numeric STOP reason')
                row.update(status='STOP',reason=b['reason'],reason_provenance='unchanged_retained_numerical_STOP')
            elif not r['reflection_coefficient_applied_HOST']:
                row.update(status='STOP',reason=r['reason'],reason_provenance='unchanged_reflection_STOP')
            elif not alloc['allocation_INPUT_valid']:
                row.update(status='STOP',reason=alloc['reason'],reason_provenance='missing_source_allocation')
            else:
                bound=allocation.rational(r['reflected_source_error_L1_to_ORIGINAL_bound'])
                cap=allocation.rational(alloc['source_caps_L1'][b['source_id']]);ok=bound<=cap
                row.update(status='PASS_PARTIAL' if ok else 'FAIL',reason='retained reflected bound fits source cap' if ok else
                           'retained reflected bound exceeds source cap',source_budget_evaluated=True,source_budget_fits=ok,
                           source_error_L1=pair(bound),source_cap_L1=pair(cap))
            rows.append(row)
        groups=[]
        for index,key in enumerate(ctx['groups']):
            assignments=[v for v in ctx['assignments'] if [v['port'],v['coherence_group']]==key]
            ids=[v['source_id'] for v in assignments]
            members=[v for v in rows if v['source_id'] in ids]
            group={'port':key[0],'coherence_group':key[1],'source_order':ids,FLAG:False,
                   'retained_corner_sum_computed':False,**dict.fromkeys(FALSE,False)}
            blocked=[v['source_id'] for v in members if not v['source_budget_fits']]
            if blocked:group.update(status='STOP',reason='complete group required; source STOP/FAIL preserved',blocked_source_ids=blocked)
            elif tree['tree_lineage_matches_restricted_CPU_only'] is not True:
                group.update(status='STOP',reason='missing exact matching retained complete-tree lineage')
            elif not stage['stage_INPUT_valid']:
                group.update(status='STOP',reason=stage['reason'])
            elif not all(v['terminal_reference_id']==v['common_terminal_reference_id']==assignments[0]['common_terminal_reference_id']
                         and v['rebase_cycles']==[0,1] for v in assignments):
                group.update(status='STOP',reason='same INPUT terminal gauge and explicit zero rebase required; no silent rotation')
            elif len(ids)>4:group.update(status='STOP',reason='restricted retained corner enumeration maximum 4 sources')
            else:
                ms=[mirror['sources'][ctx['source_order'].index(s)] for s in ids]
                require(all(len(r['reflected_corner_products_HOST'])==4 for r in ms),'four retained corners per source')
                results=[];max_rn=F(0)
                for selection in product(range(4),repeat=len(ms)):
                    words=[r['reflected_corner_products_HOST'][i]['reflected_uint64'] for r,i in zip(ms,selection)]
                    numeric=reduce_words(words,model=model)
                    max_rn=max(max_rn,allocation.rational(numeric['rounding_error_L1_bound']))
                    results.append({'corner_indices':list(selection),**numeric})
                    additions+=numeric['RN64_additions'];corner_sums+=1
                source_bound=sum((allocation.rational(v['source_error_L1']) for v in members),F(0))
                plan=stage['groups'][index];rn_cap=allocation.rational(plan['reduction_cap_L1'])
                total=source_bound+max_rn;field_cap=allocation.rational(ctx['unchanged_field_L1_cap'])
                ok=max_rn<=rn_cap and total<=field_cap
                group.update(status='PASS_PARTIAL' if ok else 'FAIL',reason='retained-corner reduction fits explicit stage and unchanged field cap' if ok else
                             'retained-corner reduction exceeds explicit budget',retained_corner_sum_computed=True,
                             corner_sums=results,source_errors_L1_sum=pair(source_bound),reduction_RN64_error_L1_bound=pair(max_rn),
                             reduction_cap_L1=pair(rn_cap),error_L1_to_ORIGINAL_group_corner_sum_bound=pair(total),
                             unchanged_group_field_L1_cap=pair(field_cap),other_stages_reserved_L1=plan['other_stages_reserved_L1'],
                             certificate_sha256=tree['certificate_sha256'],**{FLAG:ok})
            groups.append(group)
        cases[name]={'context':ctx,'allocation_result':alloc,'stage_result':stage,'sources':rows,'groups':groups,
                     FLAG:all(g[FLAG] for g in groups),'retained_tree_row_sha256':allocation.digest(tree),
                     **dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'units':allocation.UNITS,'case_order':list(case_names),'cases':cases,
            'inherited_pins_verified':len(pins),'retained_corner_sums':corner_sums,'new_RN64_additions':additions,
            'new_products':0,'new_trigonometry':0,'new_ray_traces':0,'old_numeric_suites_executed':0,
            **dict.fromkeys(FALSE,False),
            'scope':'HOST retained encoded corners only; grouping INPUT hypothesis, not continuous scene, detector or physical coherence',
            'cost_scope':'new sequential RN64 additions counted; receipts/hash/decompression/INPUT accounting extra, NOT full costs'}
