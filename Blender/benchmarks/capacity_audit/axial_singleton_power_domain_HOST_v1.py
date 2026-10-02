"""Restricted uniform HOST squared-modulus proof from retained complete singleton words."""
import base64,struct
from copy import deepcopy
from fractions import Fraction as F
import axial_singleton_group_domain_HOST_v1 as group
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-complete-singleton-uniform-power-retained-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-SINGLETON-GROUP-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='d24f30f6ae6155bc628755883237230bb1fb32e748f40b5ddd4810d0f905b19b'
POWER='coordinacion/respuestas/AXIAL-GROUP-POWER-HOST-001-CODEX.json'
POWER_SHA='d6510bb52617324272bc47b45b2b2c09ecc4578e865b06f0fc1d332a51998763'
FLAG='restricted_complete_singleton_power_error_to_ORIGINAL_proved'
FALSE=group.FALSE+('uniform_power_error_proved','power_budget_accepted','native_power_implemented','power_executed_new')
require=io.require
number=group.number
pair=group.pair
decode=group.decode
digest=allocation.digest

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-SINGLETON-GROUP-DOMAIN-HOST-001','complete singleton predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    require(pins[POWER]==POWER_SHA,'retained power receipt SHA')
    old=io.payload(r)['data']['audit']
    power=io.payload(allocation.parse(io.read(POWER,POWER_SHA)))['data']
    red=io.payload(allocation.parse(io.read(group.REDUCTION,pins[group.REDUCTION])))['data']['explicit_synthetic_INPUT_controls']['cases']
    reflected=io.payload(allocation.parse(io.read(group.PREVIOUS,pins[group.PREVIOUS])))['data']['audit']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    require(set(packets)==set(old['cases'])==set(power['explicit_synthetic_INPUT_controls']['cases'])==set(red)==set(reflected['cases']),
            'complete retained case coverage')
    return packets,old,power,red,reflected,pins

def rn_cell(exact,word):
    """Verify recorded nonnegative normal/zero RN-even word; no float conversion or RN execution."""
    value=decode(word)
    require(exact>=0 and type(word) is int and 0<=word<2**63,'nonnegative recorded power word')
    if word==0:
        require(exact==0,'restricted exact-zero power node; no hidden underflow/FTZ')
        return {'recorded_uint64':word,'exact_zero_identity':True,'new_RN_executions':0}
    require((word>>52)>0,'normal power output only')
    lower=(decode(word-1)+value)/2;upper=(value+decode(word+1))/2
    even=word%2==0
    require(lower<exact<upper or (even and exact in (lower,upper)),'recorded word outside RN-even cell')
    return {'recorded_uint64':word,'lower_midpoint':pair(lower),'upper_midpoint':pair(upper),
            'ties_included':even,'exact_zero_identity':False,'new_RN_executions':0}

def retained_node(node,left,right,op):
    require(node['op']==op and type(node['left_uint64']) is int and type(node['right_uint64']) is int
            and node['left_uint64']==left and node['right_uint64']==right,'recorded power graph operand/op chain')
    a=decode(left);b=decode(right);exact=a*b if op=='mul' else a+b
    require(number(node['exact_rational'])==exact,'recorded exact operation rational')
    cell=rn_cell(exact,node['output_uint64'])
    error=abs(decode(node['output_uint64'])-exact)
    require(number(node['rounding_error_abs'])==error,'recorded RN error unchanged')
    return cell,error

def power_domain_proof(packet,ctx,prior_group,powercase,redcase,reflectedcase):
    require(prior_group[group.FLAG] is True and prior_group['status']=='STOP','proved complete group without budget admission')
    gp=prior_group['proof'];ids=prior_group['source_order']
    assignments=[a for a in ctx['assignments'] if [a['port'],a['coherence_group']]==[prior_group['port'],prior_group['coherence_group']]]
    require(len(ids)==len(assignments)==1 and ids==[a['source_id'] for a in assignments]==gp['complete_source_order'],
            'complete singleton group, no partial multi-source')
    require(ctx==powercase['context']==redcase['context']==reflectedcase['context'],'same complete fresh INPUT/gauge/ABI/caps')
    key=[prior_group['port'],prior_group['coherence_group']];index=ctx['groups'].index(key)
    require([[g['port'],g['coherence_group']] for g in powercase['groups']]==ctx['groups'],'complete power group order')
    pg=powercase['groups'][index];rg=redcase['groups'][index]
    require(pg['source_order']==ids==rg['source_order'] and pg['retained_group_row_sha256']==digest(rg)
            ==gp['retained_reduction_group_sha256'],'same complete retained reduction/power group')
    require(pg['power_evaluated_HOST'] is True and pg['unchanged_original_limits']==ctx['unchanged_limits'],'retained HOST power and original limits')
    sourceindex=ctx['source_order'].index(ids[0]);src=reflectedcase['sources'][sourceindex]
    require(gp['retained_reflected_source_row_sha256']==digest(src)
            and src['restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved'] is True,'same uniform reflected source')
    raw=base64.b64decode(packet['buffers_base64']['sources'],validate=True)
    snap=allocation.parse(base64.b64decode(packet['buffers_base64']['original_scene_json'],validate=True))
    originalwords=list(struct.unpack('<QQ',raw[128*sourceindex+112:128*sourceindex+128]))
    require(raw[128*sourceindex+112:128*sourceindex+128]==struct.pack('<dd',*snap['sources'][sourceindex]['field_reim']),'exact fixed ORIGINAL source')
    original=[-decode(w) for w in originalwords];original_power=sum(v*v for v in original)
    require(original_power>0,'strict positive ORIGINAL power; no epsilon denominator')
    field_error=number(gp['uniform_group_L1_error_to_fixed_ORIGINAL_bound'])
    require(field_error==F(1,2**55),'same nonzero uniform group L1 error')
    copies=gp['retained_copy_identities'];corners=pg['power_corners']
    require(len(copies)==len(corners)==len(rg['corner_sums'])==len(src['proof']['retained_corner_identities'])==4,
            'all four retained power/copy/source identities')
    checks=[];constant=None;absolute=None;relative=None;envelope=None;rn_total=None
    for i,(copy,c,red,sc) in enumerate(zip(copies,corners,rg['corner_sums'],src['proof']['retained_corner_identities'])):
        words=copy['retained_copy_uint64']
        require(copy['reduction_corner_sha256']==digest(red)==c['retained_field_corner_sha256']
                and c['input_uint64']==red['sum_uint64']==words and c['corner_indices']==[i],'retained power field input hash/bits')
        require(copy['source_identity_sha256']==digest(sc) and sc['reflected_uint64']==words
                and list(map(number,sc['negated_fixed_ORIGINAL_source_rational']))==original,'same fixed ORIGINAL reference')
        require(constant is None or constant==words,'uniform constant complete group words')
        constant=words;values=list(map(decode,words))
        require(type(c['RN64_operations']) is int and c['RN64_operations']==3 and len(c['trace'])==3,'exact three recorded power nodes')
        t=c['trace'];proofs=[];rounding=F(0)
        for node,left,right,op in [(t[0],words[0],words[0],'mul'),(t[1],words[1],words[1],'mul'),
                                  (t[2],t[0]['output_uint64'],t[1]['output_uint64'],'add')]:
            cell,err=retained_node(node,left,right,op);proofs.append(cell);rounding+=err
        observed=decode(t[2]['output_uint64']);represented=sum(v*v for v in values)
        require(c['observed_power_uint64']==t[2]['output_uint64'] and number(c['observed_power_rational'])==observed
                and number(c['represented_input_power_exact'])==represented,'retained power output/reference')
        require(number(c['input_field_L1_error_bound'])==field_error
                and number(c['actual_error_abs_to_represented_power'])==abs(observed-represented)
                and number(c['power_RN64_error_abs_bound'])==rounding,'separate unchanged field/powerRN ledger')
        magnitude=max(map(abs,values));propagation=2*magnitude*field_error+field_error*field_error
        combined=propagation+rounding;lower=(magnitude-field_error)**2
        require(magnitude>field_error and number(c['field_to_power_error_abs_bound'])==propagation
                and number(c['combined_error_abs_to_ORIGINAL_power_bound'])==combined
                and number(c['ORIGINAL_power_lower_bound'])==lower
                and number(c['relative_power_error_bound'])==combined/lower,'unchanged conservative power envelope/ORIGINAL denominator')
        exact_abs=abs(observed-original_power);exact_rel=exact_abs/original_power
        require(exact_abs<=combined and exact_rel<=combined/lower,'exact fixed ORIGINAL error inside retained conservative bounds')
        require(absolute is None or (exact_abs,exact_rel,combined,rounding)==(absolute,relative,envelope,rn_total),'uniform identical power across constant domain')
        absolute,relative,envelope,rn_total=exact_abs,exact_rel,combined,rounding
        checks.append({'retained_power_corner_sha256':digest(c),'retained_copy_identity_sha256':digest(copy),
                       'retained_power_uint64':c['observed_power_uint64'],'RN_cell_checks':proofs,
                       'exact_absolute_error_to_fixed_ORIGINAL_power':pair(exact_abs),
                       'exact_relative_error_to_fixed_ORIGINAL_power':pair(exact_rel),'new_RN_or_producer_executions':0})
    require(number(pg['combined_error_abs_to_ORIGINAL_power_bound'])==envelope
            and number(pg['power_RN64_error_abs_bound'])==rn_total,'same retained group-level power charges')
    return {'model':MODEL,FLAG:True,'complete_source_order':ids,
            'retained_uniform_group_row_sha256':digest(prior_group),'retained_power_group_sha256':digest(pg),
            'fixed_ORIGINAL_power_exact':pair(original_power),'uniform_exact_absolute_power_error':pair(absolute),
            'uniform_exact_relative_power_error':pair(relative),'retained_conservative_absolute_power_bound':pair(envelope),
            'retained_power_RN64_error_abs_bound':pair(rn_total),'retained_corner_checks':checks,
            'synthetic_power_budget_admission_NOT_inherited':True,'missing_allocation_NOT_promoted':True,
            'new_RN_or_copy_or_scene_producer_executions':0,
            'scope':'HOST squared modulus of complete singleton restricted constant domain; not physical detector energy',
            **dict.fromkeys(FALSE,False)}

def audit_singleton_power_domain_HOST(case_names,*,model):
    require(model==MODEL,'explicit restricted power domain model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique case selection')
    packets,old,power,red,reflected,pins=load_retained();require(set(case_names)<=set(packets),'known retained cases')
    cases={};proved=blocked=cells=0
    for n in case_names:
        ctx=allocation.context_from_packet(packets[n],digest(packets[n]),model=allocation.MODEL);prior=old['cases'][n]
        require(ctx==prior['context'],'fresh complete INPUT identity')
        rows=[]
        for g in prior['groups']:
            row={'port':g['port'],'coherence_group':g['coherence_group'],'source_order':deepcopy(g['source_order']),
                 'retained_complete_group_row_sha256':digest(g),'status':'STOP',FLAG:False,
                 'power_budget_evaluated':False,**dict.fromkeys(FALSE,False)}
            if g[group.FLAG] is not True:
                blocked+=1;row.update(reason=g['reason'],reason_provenance='unchanged_complete_group_domain_STOP')
                if 'blocked_source_ids' in g:row['blocked_source_ids']=deepcopy(g['blocked_source_ids'])
            else:
                proof=power_domain_proof(packets[n],ctx,g,power['explicit_synthetic_INPUT_controls']['cases'][n],red[n],reflected['cases'][n])
                proved+=1;cells+=12
                row.update(proof=proof,reason='missing explicit source/reduction/power INPUT allocations; uniform proof is not admission',
                           reason_provenance='missing_static_INPUT_allocations',**{FLAG:True})
            rows.append(row)
        cases[n]={'context':ctx,'groups':rows,'retained_sources_sha256':digest(prior['sources']),**dict.fromkeys(FALSE,False)}
    controls={k:{n:{'retained_case_sha256':digest(c),'group_statuses':[g['status'] for g in c['groups']],
                   'accepted_groups':[g['accepted_retained_corner_group_power_CPU_only'] for g in c['groups']]}
                 for n,c in power[k]['cases'].items()} for k in ('zero_absolute','zero_relative')}
    require(all(v['group_statuses']==['FAIL'] and v['accepted_groups']==[False] for d in controls.values() for v in d.values()),'zero-budget FAIL controls preserved')
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
            'restricted_complete_singleton_power_groups_proved':proved,'blocked_complete_groups':blocked,
            'retained_RN_cell_checks':cells,'retained_unit_STOPs':old['retained_unit_STOPs'],
            'nonzero_domains_not_refined':old['nonzero_domains_not_refined'],'retained_zero_budget_FAIL_controls':controls,
            'new_RN_or_copy_or_scene_producer_executions':0,**dict.fromkeys(FALSE,False)}
