"""Exact zero-angle singleton refinement for pinned canonical-zero HOST Horner26."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import math
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation

MODEL='axial-zero-singleton-canonical-HOST-Horner26-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='c81d8e34b11d73db75470096f95bec6ca738cd08af030e3977da077bf4a9df97'
RECTANGLE='coordinacion/respuestas/AXIAL-ARGUMENT-RECTANGLE-HOST-001-CODEX.json'
UNIT='coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json'
ONE=0x3ff0000000000000
SIGN=1<<63
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated',
       'coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission',
       'whole_scene_parameter_enclosure_proved','native_argument_implemented','general_3D_geometry_proved',
       'physical_scene_uncertainty_certified','native_signed_zero_graph_equivalence_proved')
require=io.require
pair=allocation.pair

def decode(word):
    require(type(word) is int and 0<=word<2**64,'strict uint64')
    e=(word>>52)&2047;m=word%2**52
    require(e<2047 and (e!=0 or m==0),'finite normal-or-zero word')
    return (-1 if word>>63 else 1)*F((2**52+m) if e else 0)*F(2)**(e-1075)

def number(v):
    require(type(v) is list and len(v)==2 and all(type(x) is int for x in v)
            and v[1]>0 and math.gcd(*v)==1,'canonical rational pair')
    return F(*v)

def zero_interval(v):
    require(type(v) is list and len(v)==2,'two exact interval endpoints')
    require(all(number(x)==0 for x in v),'exact zero interval only')

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    prior=io.payload(r)['data']['audit']
    rect=io.payload(allocation.parse(io.read(RECTANGLE,pins[RECTANGLE])))['data']['audit']
    units=io.payload(allocation.parse(io.read(UNIT,pins[UNIT])))['cases']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    require(set(packets)==set(prior['cases'])==set(rect['cases'])==set(units),'complete retained cases')
    return packets,prior,rect,units,pins

def profile_from_retained(units):
    profile=deepcopy(units['positive']['sources'][0]['ideal_ORIGINAL_unit_HOST']['rotation_RN64']['coefficients'])
    require(set(profile)=={'cos','sin'},'fixed coefficient names')
    for name,odd in (('cos',0),('sin',1)):
        require(len(profile[name])==7,'seven Taylor coefficients')
        for j,c in enumerate(profile[name]):
            exact=F((-1)**j,math.factorial(2*j+odd))
            require(c['exact_rational']==pair(exact),'fixed Taylor coefficient')
            require(c['error_rational']==pair(abs(decode(c['uint64'])-exact)),'coefficient error identity')
        require(profile[name][0]['uint64']==ONE,'constant coefficient exactly one')
    return profile

def exact_trace(profile):
    """Internal identity rules; no rounding algorithm, numeric producer or float simulation."""
    require(set(profile)=={'cos','sin'},'fixed coefficient names')
    trace=[{'label':'square','op':'mul','inputs_rational':[[0,1],[0,1]],
            'output_uint64':0,'rounding_delta_rational':[0,1]}]
    ieee_negative_zero_labels=[]
    for name in ('cos','sin'):
        require(len(profile[name])==7 and profile[name][0]['uint64']==ONE,'fixed c0=1')
        cs=[decode(c['uint64']) for c in profile[name]]
        require(all(cs),'nonzero finite normal coefficients')
        h=cs[-1]
        for j in range(5,-1,-1):
            if h<0:ieee_negative_zero_labels.append(name+'.mul'+str(j))
            trace.append({'label':name+'.mul'+str(j),'op':'mul','inputs_rational':[pair(h),[0,1]],
                          'output_uint64':0,'rounding_delta_rational':[0,1]})
            # Exact 0+c is the stored coefficient; no coefficient error contributes at x=0.
            h=cs[j]
            trace.append({'label':name+'.add'+str(j),'op':'add','inputs_rational':[[0,1],pair(h)],
                          'output_uint64':profile[name][j]['uint64'],'rounding_delta_rational':[0,1]})
    trace.append({'label':'sin.final','op':'mul','inputs_rational':[[1,1],[0,1]],
                  'output_uint64':0,'rounding_delta_rational':[0,1]})
    require(len(trace)==26,'Horner26 identity coverage')
    return trace,ieee_negative_zero_labels

def permuted_zero(quarter):
    require(type(quarter) is int and -2<=quarter<=2,'bounded exact quarter index')
    # Retained HOST quadrant permutation is word sign-XOR, including signed final zeros.
    return {0:[ONE,0],1:[SIGN,ONE],2:[ONE^SIGN,SIGN],3:[0,ONE^SIGN]}[quarter%4]

def verify_zero_graph(unit,profile,quarter):
    trace,mismatch=exact_trace(profile)
    q=unit['quarter_argument'];rot=unit['rotation_RN64']
    require(q['quarter_turns_HOST']==quarter and type(q['quarter_turns_HOST']) is int,'same quarter')
    for k in ('quarter_residual_HOST_rational','HOST_argument_rational'):
        require(number(q[k])==0,'exact zero residual and argument')
    require(q['HOST_argument_uint64']==0 and type(q['HOST_argument_uint64']) is int,'canonical +0 argument')
    require(type(rot['angle_uint64']) is int and rot['angle_uint64']==0
            and allocation.canon(rot['coefficients'])==allocation.canon(profile),'pinned graph and profile')
    require(allocation.canon(rot['operations'])==allocation.canon(trace)
            and type(rot['RN64_operations']) is int and rot['RN64_operations']==26,'all exact retained graph identities')
    require(unit['unpermuted_unit_uint64']==[ONE,0],'unpermuted exact unit')
    words=permuted_zero(quarter)
    list(map(decode,unit['unit_uint64']))
    require(unit['unit_uint64']==words and unit['unit_rational']==list(map(lambda w:pair(decode(w)),words)),
            'exact quarter permutation and rational unit')
    require(unit['unit_uint32_little_endian']==[[w%2**32,w>>32] for w in words],'retained unit word ABI')
    for name,value in (('cos',F(1)),('sin',F(0))):
        t=rot['terms'][name]
        require(type(t['output_uint64']) is int and t['output_uint64']==(ONE if name=='cos' else 0),'term word identity')
        require(t['observed_rational']==t['exact_polynomial_oracle_rational']==pair(value),'term exact identity')
        for k in ('actual_polynomial_error_rational','polynomial_error_upper_rational','Taylor_remainder_upper_rational'):
            require(t[k]==[0,1],'retained zero error')
        require(all(v==[0,1] for v in t['error_charges_rational'].values()),'zero stage charges')
    return {'retained_graph_sha256':allocation.digest(unit),'identities_checked':26,
            'canonical_HOST_zero_not_IEEE_signed_zero_labels':mismatch,
            'exact_unit_uint64':words,'exact_unit_rational':list(map(lambda w:pair(decode(w)),words)),
            'new_RN_operations':0,'native_signed_zero_graph_equivalence_proved':False}

def restricted_zero_proof(domain,rect,unitrow,profile,cap):
    require(domain['restricted_coordinate_box_to_parameter_rectangle_proved'] is True,'restricted domain required')
    require(domain['retained_argument_rectangle_source_sha256']==allocation.digest(rect),'rectangle row pin')
    require(rect['argument_image_over_declared_rectangle_enclosed'] is True,'argument enclosure required')
    b=rect['parameter_branch'];im=rect['argument_image']
    zero_interval(im['argument_interval']);zero_interval(b['quarter_residual_interval'])
    require(number(b['ORIGINAL_quarter_residual'])==0,'ORIGINAL residual exactly zero')
    k=b['ORIGINAL_quarter_turn']
    require(type(k) is int and b['quarter_turn_endpoint_integers']==[k,k],'constant quarter branch')
    require(number(im['uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad'])==0
            and number(im['uniform_argument_error_bound_rad'])==0,'zero parameter/argument charge')
    require(domain['unchanged_original_phase_cap_rad']==rect['unchanged_original_phase_cap_rad']==cap,
            'same INPUT source cap')
    require(number(cap)==0 and domain['retained_unit_polynomial_charge_fits'] is False,
            'zero-cap refinement only; retain generic NONfit')
    points=[unitrow['ideal_ORIGINAL_unit_HOST']]+unitrow['encoded_corner_units_HOST']
    require(len(points)==5,'ORIGINAL plus four retained corners')
    graphs=[verify_zero_graph(p,profile,k) for p in points]
    return {'model':MODEL,'scope':'retained canonical-zero HOST graph over pinned restricted axial coordinate domain',
            'retained_scene_domain_source_sha256':allocation.digest(domain),
            'retained_rectangle_source_sha256':allocation.digest(rect),'retained_unit_source_sha256':allocation.digest(unitrow),
            'quarter_turn':k,'represented_argument_interval':[[0,1],[0,1]],
            'coefficient_profile_sha256':allocation.digest(profile),'graph_checks':graphs,
            'restricted_exact_unit_error_to_ORIGINAL_proved':True,'unit_L1_error_to_ORIGINAL_bound':[0,1],
            'additional_phase_bound_rad':[0,1],'unchanged_original_phase_cap_rad':deepcopy(cap),
            'exact_charge_fits_unchanged_cap':True,'retained_generic_polynomial_NONfit_unchanged':True,
            'Taylor_at_zero_identity':'sin(0)=0, cos(0)=1; fixed quarter permutation exact',
            'new_RN_encodings_or_old_producers_reexecuted':0,**dict.fromkeys(FALSE,False)}

def audit_zero_singleton_HOST(case_names,*,model):
    require(model==MODEL,'explicit canonical-zero HOST model')
    require(type(case_names) is list and 1<=len(case_names)<=64
            and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique case selection')
    packets,prior,rect,units,pins=load_retained()
    require(set(case_names)<=set(packets),'known retained cases')
    profile=profile_from_retained(units);cases={};proved=stops=nonzero=0
    for n in case_names:
        ctx=allocation.context_from_packet(packets[n],allocation.digest(packets[n]),model=allocation.MODEL)
        require(ctx==prior['cases'][n]['context']==rect['cases'][n]['context'],'fresh INPUT complete context')
        meta=allocation.parse(base64.b64decode(packets[n]['buffers_base64']['input_metadata_json'],validate=True))
        for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
            require(units[n][k]==ctx[k],'unit INPUT binding: '+k)
        ds=prior['cases'][n]['sources'];rs=rect['cases'][n]['sources'];us=units[n]['sources']
        require([s['source_id'] for s in ds]==[s['source_id'] for s in rs]
                ==[s['source_id'] for s in us]==ctx['source_order'],'all ordered sources')
        rows=[]
        for d,r,u,assignment in zip(ds,rs,us,ctx['assignments']):
            sid=d['source_id']
            require(u['phase_reference_id']==assignment['source_phase_reference_id']
                    and u['terminal_reference_id']==assignment['terminal_reference_id'],'original gauge binding')
            row={'source_id':sid,'retained_scene_domain_source_sha256':allocation.digest(d),
                 'retained_unit_polynomial_charge_fits':d['retained_unit_polynomial_charge_fits'],
                 'restricted_exact_unit_error_to_ORIGINAL_proved':False,**dict.fromkeys(FALSE,False)}
            if not d['restricted_coordinate_box_to_parameter_rectangle_proved']:
                stops+=1;row.update(status='STOP',reason=d['reason'],reason_provenance='unchanged_retained_unit_STOP')
            elif r['argument_image']['argument_interval']!=[[0,1],[0,1]]:
                nonzero+=1;row.update(status='STOP',reason='nonzero argument domain; zero theorem not applicable',
                                      reason_provenance='nonzero_domain_not_refined')
            else:
                proof=restricted_zero_proof(d,r,u,profile,meta['original_path_phase_caps'][sid]);proved+=1
                row.update(restricted_exact_unit_error_to_ORIGINAL_proved=True,proof=proof,status='STOP',
                           reason='restricted HOST unit only; source products/reduction/full pipeline still unproved',
                           reason_provenance='restricted_zero_unit_only_not_full_pipeline')
            rows.append(row)
        cases[n]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
            'restricted_zero_unit_proofs':proved,'retained_unit_STOPs':stops,'nonzero_domains_not_refined':nonzero,
            'new_RN_encodings_or_old_producers_reexecuted':0,**dict.fromkeys(FALSE,False)}
