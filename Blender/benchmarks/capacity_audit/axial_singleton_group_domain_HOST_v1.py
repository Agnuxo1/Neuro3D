"""Uniform restricted group linkage by complete singleton-copy identity; HOST only."""
from copy import deepcopy
from fractions import Fraction as F
import axial_reflected_source_domain_HOST_v1 as reflected
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-complete-singleton-group-domain-copy-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='9375bdec28cd0704f8a52bb151ad0c2ac72955800a1ac8c7607add4ff47addcb'
REDUCTION='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
REDUCTION_SHA='44e1af7a17f3fdb9577d274dc001212f9cefe7ea17af7548c9ba5f7f113a942d'
TREE='coordinacion/respuestas/AXIAL-TREE-LINEAGE-HOST-001-CODEX.json'
FLAG='restricted_complete_singleton_group_error_to_ORIGINAL_proved'
FALSE=reflected.FALSE+('uniform_group_error_proved','group_budget_accepted',
                       'native_reduction_implemented','group_copy_executed_new')
require=io.require
number=reflected.number
pair=reflected.pair
decode=reflected.decode
digest=allocation.digest

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-REFLECTED-SOURCE-DOMAIN-HOST-001','reflected domain predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    require(pins[REDUCTION]==REDUCTION_SHA,'reduction receipt SHA')
    old=io.payload(r)['data']['audit']
    reductions=io.payload(allocation.parse(io.read(REDUCTION,REDUCTION_SHA)))['data']
    tree=io.payload(allocation.parse(io.read(TREE,pins[TREE])))['data']['audit']['cases']
    mirrors=io.payload(allocation.parse(io.read(reflected.MIRROR,pins[reflected.MIRROR])))['data']['missing']['cases']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    require(set(packets)==set(old['cases'])==set(tree)==set(mirrors)==set(reductions['missing']['cases'])
            ==set(reductions['explicit_synthetic_INPUT_controls']['cases']),'complete retained case coverage')
    # Preserve the pinned metadata defect; the exact captured audit is authoritative.
    recorded=r['evidence']['unchanged_per_source_L1_error']
    require(recorded==[1,36028797018963970],'known metadata defect not silently rewritten')
    require(all(s['proof']['uniform_ideal_reflected_source_L1_error_to_fixed_ORIGINAL_bound']==[1,2**55]
                for c in old['cases'].values() for s in c['sources'] if 'proof' in s),'authoritative exact bound unchanged')
    discrepancy={'path':PREVIOUS,'sha256':PREVIOUS_SHA,'field':'evidence.unchanged_per_source_L1_error',
                 'recorded_rational':deepcopy(recorded),'captured_audit_rational':[1,2**55],
                 'metadata_matches_captured_audit':False,'predecessor_modified':False,
                 'scope':'summary metadata discrepancy only; captured audit and independent oracle exact'}
    return packets,old,reductions,tree,mirrors,pins,discrepancy

def group_members(context,key,sources):
    require(type(key) is list and len(key)==2 and key in context['groups'],'declared group key')
    require([s['source_id'] for s in sources]==context['source_order'],'complete source order; no caller partial list')
    assignments=context['assignments']
    require([a['source_id'] for a in assignments]==context['source_order'],'complete assignment order')
    require(len(set(context['source_order']))==len(sources),'unique complete sources')
    members=[(a,s) for a,s in zip(assignments,sources) if [a['port'],a['coherence_group']]==key]
    require(members,'nonempty complete declared group')
    return members

def singleton_proof(context,key,sources,redcase,tree,mirror):
    members=group_members(context,key,sources)
    require(len(members)==1,'complete singleton only; never partial multi-source sum')
    assignment,src=members[0];sid=src['source_id'];index=context['source_order'].index(sid)
    require(src['restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved'] is True,'uniform restricted reflected source required')
    require(src['status']=='STOP' and src['reason_provenance']=='missing_static_INPUT_allocation','allocation STOP not promoted')
    p=src['proof'];require(p['missing_source_allocation_NOT_promoted'] is True,'source allocation admission remains absent')
    require(p['profile']['restricted_entire_domain_event_chain_proved'] is True,'uniform event/domain chain required')
    require(context==redcase['context']==tree['context']==mirror['context'],'same complete INPUT context, not caller context')
    require(tree['tree_lineage_matches_restricted_CPU_only'] is True
            and tree['input_packet_sha256']==context['input_packet_sha256'],'matching retained tree required')
    require([s['source_id'] for s in tree['sources']]==context['source_order'],'complete tree source order')
    require(redcase['retained_tree_row_sha256']==digest(tree),'retained reduction/tree identity')
    require(assignment['terminal_reference_id']==assignment['common_terminal_reference_id']
            and number(assignment['rebase_cycles'])==0,'same terminal gauge; no silent rotation')
    m=mirror['sources'][index]
    require([s['source_id'] for s in mirror['sources']]==context['source_order'],'complete mirror source order')
    require(p['retained_mirror_source_row_sha256']==digest(m),'exact reflected-source receipt chain')
    require(tree['retained_source_product_row_sha256s'][index]==m['retained_product_row_sha256'],'same tree/source product')
    require(tree['sources'][index]['native_event_row_sha256']==m['retained_event_row_sha256'],'same tree/mirror event')
    require([[g['port'],g['coherence_group']] for g in redcase['groups']]==context['groups'],'complete reduction group order')
    rg=redcase['groups'][context['groups'].index(key)]
    require(rg['source_order']==[sid] and rg['certificate_sha256']==tree['certificate_sha256'],'same complete singleton/certificate')
    corners=p['retained_corner_identities'];require(len(corners)==4,'four retained source identities')
    words=corners[0]['reflected_uint64'];values=list(map(decode,words))
    original=list(map(number,corners[0]['negated_fixed_ORIGINAL_source_rational']))
    error=number(p['uniform_ideal_reflected_source_L1_error_to_fixed_ORIGINAL_bound'])
    require(error==F(1,2**55) and sum(abs(v-o) for v,o in zip(values,original))==error,'same nonzero source error to ORIGINAL')
    require(len(rg['corner_sums'])==4,'four retained singleton reduction receipts')
    checks=[]
    for i,(c,r) in enumerate(zip(corners,rg['corner_sums'])):
        require(list(map(decode,c['reflected_uint64']))==values and c['reflected_uint64']==words
                and list(map(number,c['negated_fixed_ORIGINAL_source_rational']))==original,'uniform constant source words/reference')
        require(number(c['uniform_reflected_source_error_L1'])==error,'same fixed-source charge at all identities')
        require(r['corner_indices']==[i] and r['source_uint64']==[words] and r['sum_uint64']==words,'copy first complete source bit-exact')
        require(all(type(w) is int for w in r['sum_uint64']),'strict singleton sum words, no bool')
        require(list(map(number,r['sum_rational']))==values
                and list(map(number,r['exact_represented_sources_sum']))==values,'same exact represented sum')
        require(type(r['RN64_additions']) is int and r['RN64_additions']==0 and r['trace']==[]
                and number(r['rounding_error_L1_bound'])==number(r['actual_error_L1_to_represented_sum'])==0,'singleton copy has zero RN/error')
        checks.append({'source_identity_sha256':digest(c),'reduction_corner_sha256':digest(r),
                       'retained_copy_uint64':deepcopy(words),'bit_copy_identities_checked':2,'new_RN_or_copy_executions':0})
    require(number(rg['source_errors_L1_sum'])==number(rg['error_L1_to_ORIGINAL_group_corner_sum_bound'])==error
            and number(rg['reduction_RN64_error_L1_bound'])==0,'reduction error/source ledger unchanged')
    return {'model':MODEL,FLAG:True,'complete_source_order':[sid],
            'retained_reflected_source_row_sha256':digest(src),'retained_reduction_group_sha256':digest(rg),
            'retained_tree_row_sha256':digest(tree),'certificate_sha256':tree['certificate_sha256'],
            'grouping_provenance':context['grouping_provenance'],'terminal_reference_id':assignment['common_terminal_reference_id'],
            'uniform_group_L1_error_to_fixed_ORIGINAL_bound':pair(error),'reduction_rounding_error_L1':[0,1],
            'retained_copy_identities':checks,'missing_source_and_stage_allocation_NOT_promoted':True,
            'synthetic_budget_admission_NOT_inherited':True,'new_RN_or_copy_or_scene_producer_executions':0,
            'scope':'complete singleton in inherited restricted domain; mathematical identity, not authenticated detector field',
            **dict.fromkeys(FALSE,False)}

def audit_singleton_group_domain_HOST(case_names,*,model):
    require(model==MODEL,'explicit complete singleton domain model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,red,tree,mirror,pins,discrepancy=load_retained()
    require(set(case_names)<=set(packets),'known retained cases')
    cases={};proved=blocked=identities=0
    for n in case_names:
        ctx=allocation.context_from_packet(packets[n],digest(packets[n]),model=allocation.MODEL)
        prior=old['cases'][n];missing=red['missing']['cases'][n];synthetic=red['explicit_synthetic_INPUT_controls']['cases'][n]
        require(ctx==prior['context']==missing['context']==synthetic['context'],'fresh complete INPUT/group/caps identity')
        require(missing['allocation_result']['allocation_INPUT_valid'] is False
                and missing['stage_result']['stage_INPUT_valid'] is False,'missing source/stage allocations stay absent')
        require(all(g['accepted_retained_corner_group_reduction_CPU_only'] is False for g in missing['groups']),
                'missing-budget group admission stays false')
        groups=[]
        for key in ctx['groups']:
            members=group_members(ctx,key,prior['sources']);ids=[a['source_id'] for a,s in members]
            unavailable=[s['source_id'] for a,s in members if s['restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved'] is not True]
            g={'port':key[0],'coherence_group':key[1],'source_order':ids,FLAG:False,
               'status':'STOP','group_budget_evaluated':False,**dict.fromkeys(FALSE,False)}
            if unavailable:
                g.update(reason='complete group required; retained source domain STOP/nonzero preserved',
                         reason_provenance='unchanged_source_domain_blockers',blocked_source_ids=unavailable);blocked+=1
            elif len(members)!=1:
                g.update(reason='multi-source domain reduction not proved; no partial sum',reason_provenance='not_singleton');blocked+=1
            else:
                proof=singleton_proof(ctx,key,prior['sources'],synthetic,tree[n],mirror[n]);proved+=1;identities+=8
                g.update(proof=proof,reason='missing explicit source and reduction-stage INPUT allocation; proof is not admission',
                         reason_provenance='missing_static_INPUT_allocation',**{FLAG:True})
            groups.append(g)
        cases[n]={'context':ctx,'sources':deepcopy(prior['sources']),'groups':groups,
                  'retained_source_domain_case_sha256':digest(prior),
                  'retained_missing_budget_case_sha256':digest(missing),**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
            'restricted_complete_singleton_groups_proved':proved,'blocked_complete_groups':blocked,
            'retained_bit_copy_identities':identities,'retained_unit_STOPs':old['retained_unit_STOPs'],
            'nonzero_domains_not_refined':old['nonzero_domains_not_refined'],'new_RN_or_copy_or_scene_producer_executions':0,
            'predecessor_metadata_discrepancy':discrepancy,**dict.fromkeys(FALSE,False)}
