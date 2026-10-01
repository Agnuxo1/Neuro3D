"""Opt-in static HOST allocation INPUT contract; NOT numerical field acceptance."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
import math
MODEL = 'axial-static-amplitude-L1-allocation-HOST-v1'
UNITS = 'ORIGINAL-source-field-amplitude-L1'
BUFFERS = {'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
def require(ok, why):
    if not ok:
        raise ValueError(why)
def canon(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
def digest(v):
    return hashlib.sha256(canon(v)).hexdigest()
def pair(v):
    return [v.numerator,v.denominator]
def rational(v):
    require(type(v) is list and len(v)==2 and all(type(n) is int for n in v)
            and v[0]>=0 and v[1]>0 and math.gcd(v[0],v[1])==1,
            'canonical nonnegative L1 rational required; absent is not zero')
    return F(*v)
def parse(raw):
    def unique(items):
        out={}
        for k,v in items:
            require(k not in out,'duplicate JSON key')
            out[k]=v
        return out
    def invalid(v):
        raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=unique,parse_constant=invalid)
def context_from_packet(packet, expected_packet_sha256, *, model):
    require(model==MODEL,'explicit allocation HOST model required')
    require(digest(packet)==expected_packet_sha256,'INPUT receipt')
    require(type(packet['buffers_base64']) is dict and set(packet['buffers_base64'])==BUFFERS,
            'INPUT-only buffer roles')
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    require(set(packet['manifest']['buffers'])==BUFFERS,'manifest buffer coverage')
    for k,v in buffers.items():
        require(packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()},
                'buffer receipt')
    meta=parse(buffers['input_metadata_json']);snap=parse(buffers['original_scene_json'])
    require(meta['original_snapshot_sha256']==hashlib.sha256(buffers['original_scene_json']).hexdigest(),
            'ORIGINAL snapshot receipt')
    ids=meta['source_order']
    require(type(ids) is list and 1<=len(ids)<=64 and all(type(s) is str and s for s in ids)
            and len(ids)==len(set(ids)) and ids==[s['id'] for s in snap['sources']],
            'ordered complete unique ORIGINAL source IDs')
    require(meta['case_name']==packet['manifest']['case_name'],'case identity')
    group=meta['explicit_group_contract']
    require(group['scene_binding_sha256']==meta['scene_binding_sha256'],'group scene binding')
    limits=group['limits'];cap=rational(limits['field_L1'])
    assignments=group['assignments']
    require(type(assignments) is list and len(assignments)==len(ids)
            and [v['source_id'] for v in assignments]==ids,'complete ordered assignments')
    groups=[]
    for v in assignments:
        require(type(v['port']) is str and v['port'] and
                type(v['coherence_group']) is str and v['coherence_group'],'explicit port/group')
        require(v['source_phase_reference_id']=='original-source-zero:'+meta['scene_binding_sha256']+':'+v['source_id'],
                'ORIGINAL source gauge')
        require(type(v['terminal_reference_id']) is str and v['terminal_reference_id'] and
                type(v['common_terminal_reference_id']) is str and v['common_terminal_reference_id'],
                'explicit terminal gauges')
        key=[v['port'],v['coherence_group']]
        if key not in groups:
            groups.append(key)
    # Context is derived input, not scene/coherence authorization or numerical evidence.
    return {'model':MODEL,'units':UNITS,'case_name':meta['case_name'],
            'input_packet_sha256':expected_packet_sha256,'scene_binding_sha256':meta['scene_binding_sha256'],
            'word_ABI_sha256':meta['word_ABI_sha256'],'original_snapshot_sha256':meta['original_snapshot_sha256'],
            'original_group_contract_sha256':digest(group),'source_order':deepcopy(ids),
            'assignments':deepcopy(assignments),'groups':groups,'unchanged_field_L1_cap':pair(cap),
            'unchanged_limits':deepcopy(limits),
            'grouping_provenance':group['grouping_provenance'],
            'execution_authenticated':False,'coherence_authenticated':False}
def _validate_allocation(context, allocation, *, model):
    require(model==MODEL==context['model'] and context['units']==UNITS,'explicit allocation model/units')
    if allocation is None:
        return {'allocation_INPUT_valid':False,'reason':'missing explicit per-source L1 allocation INPUT; no default split/zero',
                'source_order':deepcopy(context['source_order']),'context_sha256':digest(context),
                'amplitude_budget_accepted':False,'accepted_full_field_pipeline':False,'GPU_executed':False}
    require(type(allocation) is dict and set(allocation)=={'model','units','context_sha256','sources','groups'},
            'allocation INPUT whitelist; no outputs/gates supplied')
    require(allocation['model']==MODEL and allocation['units']==UNITS and
            allocation['context_sha256']==digest(context),'allocation model/units/context binding')
    sources=allocation['sources'];groups=allocation['groups'];ids=context['source_order']
    require(type(sources) is list and len(sources)==len(ids),'complete source allocation')
    require(all(type(v) is dict and set(v)=={'source_id','cap_L1'} for v in sources),'source allocation whitelist')
    require([v['source_id'] for v in sources]==ids,'ordered source identity/no duplicates')
    source_caps={v['source_id']:rational(v['cap_L1']) for v in sources}
    require(type(groups) is list and len(groups)==len(context['groups']),'complete explicit group reservations')
    require(all(type(v) is dict and set(v)=={'port','coherence_group','remaining_stages_reserved_L1'} for v in groups),
            'group reservation whitelist')
    require([[v['port'],v['coherence_group']] for v in groups]==context['groups'],'ordered exact port/group/no duplicates')
    cap=rational(context['unchanged_field_L1_cap']);rows=[]
    for v in groups:
        reserve=rational(v['remaining_stages_reserved_L1'])
        members=[a['source_id'] for a in context['assignments'] if
                 a['port']==v['port'] and a['coherence_group']==v['coherence_group']]
        total=sum((source_caps[s] for s in members),F(0));spent=total+reserve
        require(spent<=cap,'source caps plus remaining-stage reservation exceed unchanged ORIGINAL group field-L1 cap')
        rows.append({'port':v['port'],'coherence_group':v['coherence_group'],'source_order':members,
                     'source_caps_sum_L1':pair(total),'remaining_stages_reserved_L1':pair(reserve),
                     'unchanged_group_field_L1_cap':pair(cap),'unallocated_L1':pair(cap-spent)})
    return {'allocation_INPUT_valid':True,'context_sha256':digest(context),'allocation_sha256':digest(allocation),
            'source_order':deepcopy(ids),'source_caps_L1':{s:pair(v) for s,v in source_caps.items()},
            'groups':rows,'unchanged_limits':deepcopy(context['unchanged_limits']),
            'amplitude_budget_accepted':False,'source_product_gate_evaluated':False,
            'remaining_stages_error_proved':False,'field_values_computed':False,
            'detector_evaluated':False,'coherence_authenticated':False,'execution_authenticated':False,
            'accepted_full_field_pipeline':False,'GPU_executed':False,
            'scope':'static INPUT accounting only; no auto-split, no output-dependent allocation, no native/GPU admission'}

def audit_allocation_HOST(packet, expected_packet_sha256, allocation, *, model):
    """Admission entry point: always derive fresh context from INPUT, never caller context."""
    context=context_from_packet(packet,expected_packet_sha256,model=model)
    result=_validate_allocation(context,allocation,model=model)
    return {'context':context,'result':result,'HOST_only':True,
            'amplitude_budget_accepted':False,'source_product_gate_evaluated':False,
            'remaining_stages_error_proved':False,'field_values_computed':False,
            'detector_evaluated':False,'coherence_authenticated':False,'execution_authenticated':False,
            'accepted_full_field_pipeline':False,'GPU_executed':False}
