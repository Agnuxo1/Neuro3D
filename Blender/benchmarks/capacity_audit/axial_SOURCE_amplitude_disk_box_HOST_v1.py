"""Opt-in conditional SOURCE amplitude-box disk lemma; no scene uniform error claimed."""
import math,struct
from fractions import Fraction as F
from copy import deepcopy
import axial_SOURCE_phase_quota_consumer_HOST_v1 as prior
io,allocation,require,digest=prior.io,prior.allocation,prior.require,prior.digest
original=prior.phase.original
FALSE=prior.FALSE
MODEL='axial-ORIGINAL-SOURCE-amplitude-box-conditional-disk-HOST-v1'
UNITS='ORIGINAL-SOURCE-field-amplitude'
SCOPE='SOURCE_field_reim_only; fixed ORIGINAL geometry/wavelength/path/material/gauges'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-QUOTA-CONSUMER-HOST-001-CODEX.json'
PARENT_SHA='7acd92eb57129f998f2eb8b3ab8a315f43118c18ca77682bea0f48ed7eca43c3'
FLAG='conditional_amplitude_box_phase_lemma_HOST_proved'

def pair(x):return [x.numerator,x.denominator]
def rational(x):
    require(type(x) is list and len(x)==2 and all(type(n) is int and n.bit_length()<=4096 for n in x)
            and x[1]>0 and math.gcd(*x)==1,'bounded canonical signed rational; bool/nonfinite/missing invalid')
    return F(*x)
def box_values(box):
    require(type(box) is list and len(box)==2 and all(type(i) is list and len(i)==2 for i in box),'two closed component intervals')
    values=[tuple(rational(v) for v in interval) for interval in box]
    require(all(lo<=hi for lo,hi in values),'ordered closed intervals, no swapping')
    return values
def distance_zero(interval):
    lo,hi=interval
    return F(0) if lo<=0<=hi else min(abs(lo),abs(hi))
def conditional_disk_box_HOST(box,error_sup_hypothesis_L1,*,model):
    require(type(model) is str and model==MODEL,'explicit conditional SOURCE box model')
    intervals=box_values(box);lower=max(distance_zero(i) for i in intervals)
    out={'model':MODEL,'box_reim':deepcopy(box),'component_min_abs':[pair(distance_zero(i)) for i in intervals],
         'amplitude_lower_bound':pair(lower),'uniform_error_hypothesis_L1':deepcopy(error_sup_hypothesis_L1),
         'uniform_executed_SOURCE_error_L1':None,'uniform_SOURCE_enclosure_proved':False,
         'conditional_phase_bound_rad':None,'positive_radial_lower_bound':None,FLAG:False,
         'group_phase_bound_rad':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    if error_sup_hypothesis_L1 is None:
        out['reason']='missing uniform SOURCE error proof; point error is not a uniform enclosure'
        return out
    eps=rational(error_sup_hypothesis_L1)
    require(eps>=0 and lower>0 and eps<lower,'strict uniform error disk away from zero over ENTIRE declared amplitude box')
    gap=lower-eps
    out.update({'conditional_phase_bound_rad':pair(eps/gap),'positive_radial_lower_bound':pair(gap),FLAG:True,
        'reason':'conditional theorem ONLY: IF |z(A)-A exp(i ORIGINAL theta)(-1)|_1 <= eps FOR EVERY A in this box; not an executed uniform SOURCE certificate'})
    return out

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA))
    require(r['task_id']=='AXIAL-SOURCE-PHASE-QUOTA-CONSUMER-HOST-001','parent task identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded,certs,stage,consumer,inputs,oldpins=prior.load_retained()
    require(all(pins.get(p)==h for p,h in oldpins.items()),'same pinned SOURCE/context branches')
    return loaded[0][0],stage,pins

def validate_domain(packet,ctx,plan):
    if plan is None:return {'domain_INPUT_valid':False,'sources':None,'reason':'missing explicit amplitude domain INPUT',**dict.fromkeys(FALSE,False)}
    require(type(plan) is dict and set(plan)=={'model','units','context_sha256','scope','sources'},'domain whitelist, no error/cap/output/authority')
    for k,v in (('model',MODEL),('units',UNITS),('context_sha256',digest(ctx)),('scope',SCOPE)):
        require(type(plan[k]) is str and plan[k]==v,'fixed context/model/units/domain scope')
    rows=plan['sources'];keys={'source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id','box_reim'}
    require(type(rows) is list and len(rows)==len(ctx['source_order']) and all(type(s) is dict and set(s)==keys for s in rows),'complete domain sources')
    require([s['source_id'] for s in rows]==ctx['source_order']==[a['source_id'] for a in ctx['assignments']],'complete ordered domain identities')
    snap,_=original.snapshot_from_packet(packet,ctx);checked=[]
    for i,(row,a) in enumerate(zip(rows,ctx['assignments'])):
        for k in ('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id'):
            require(type(row[k]) is str and row[k]==a[k],'fixed ORIGINAL SOURCE/terminal gauges')
        require(a['terminal_reference_id']==a['common_terminal_reference_id'],'fixed common terminal gauge')
        field=snap['sources'][i]['field_reim']
        require(type(field) is list and len(field)==2 and all(type(x) is float and math.isfinite(x) for x in field),'binary64 ORIGINAL SOURCE amplitude')
        center=[F.from_float(x) for x in field];intervals=box_values(row['box_reim'])
        require(all(lo<=x<=hi for x,(lo,hi) in zip(center,intervals)),'declared box contains exact ORIGINAL SOURCE INPUT anchor')
        words=[struct.unpack('<Q',struct.pack('<d',x))[0] for x in field]
        checked.append({**deepcopy(row),'ORIGINAL_source_uint64':words,'ORIGINAL_anchor_reim':[pair(x) for x in center],
            'conditional_geometry':conditional_disk_box_HOST(row['box_reim'],None,model=MODEL),
            'uniform_executed_SOURCE_error_L1':None,'uniform_SOURCE_enclosure_proved':False,
            'domain_authentication':False,'status':'STOP',**dict.fromkeys(FALSE,False)})
    return {'domain_INPUT_valid':True,'domain_sha256':digest(plan),'context_sha256':digest(ctx),
        'scope':SCOPE,'sources':checked,**dict.fromkeys(FALSE,False)}

def audit_scene_domains_HOST(case_order,plans,*,model):
    require(type(model) is str and model==MODEL,'explicit SOURCE amplitude domain model')
    require(type(case_order) is list and 1<=len(case_order)<=64 and all(type(n) is str and n for n in case_order)
            and len(set(case_order))==len(case_order),'bounded unique cases')
    require(type(plans) is dict and set(plans)<=set(case_order),'selected domain INPUT plans only')
    packets,stage,pins=load_retained();require(set(case_order)<=set(packets),'known ORIGINAL cases')
    cases={}
    for name in case_order:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        retained=stage['synthetic_partial']['cases'].get(name,stage['real_missing']['cases'].get(name))
        require(retained is not None and ctx==retained['context'],'same retained ORIGINAL context')
        v=validate_domain(packets[name],ctx,plans.get(name))
        cases[name]={'context':ctx,'domain_INPUT':v,'uniform_executed_SOURCE_error_L1':None,
            'uniform_SOURCE_enclosure_proved':False,'group_field_bound_L1':None,'group_phase_bound_rad':None,
            'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_order),'cases':cases,'inherited_pins_verified':len(pins),
        'domain_INPUT_valid_cases':sum(c['domain_INPUT']['domain_INPUT_valid'] for c in cases.values()),
        'uniform_SOURCE_enclosure_proved':False,'group_admissions':0,'new_native_operations':0,
        'old_suites_producers_reexecuted':0,'point_error_reused_as_uniform':False,
        'cost_scope':'HOST INPUT/conditional rational box only; IO/setup/upstream/rest UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
