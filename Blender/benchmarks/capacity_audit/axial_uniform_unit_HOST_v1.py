"""Uniform HOST Horner26 error over declared angle intervals; no scene enclosure."""
from copy import deepcopy
from fractions import Fraction as F
import math
import axial_uniform_power_box_HOST_v1 as box
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-uniform-Horner26-declared-angle-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-UNIFORM-POWER-BOX-HOST-001-CODEX.json'
PREVIOUS_SHA='a99e3fcf935adf47b05bd1416cb5d73db1b92c1ed568c52bde1592308e257983'
UNIT='coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json'
UNIT_SHA='9391669247fa4b6b3576ac640174f1cd853535c78591d67ae27adc72f19beaba'
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated',
       'coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission')
require=box.require
pair=box.pair
decode=box.retained.decode

def rational(v):
    x=box.number(v)
    require(max(abs(x.numerator).bit_length(),x.denominator.bit_length())<=256,'angle endpoints <=256 bits')
    return x

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-UNIFORM-POWER-BOX-HOST-001','previous task')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    require(pins[UNIT]==UNIT_SHA,'unit lineage')
    units=io.payload(allocation.parse(io.read(UNIT,UNIT_SHA)))['cases']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:c['parent'] for n,c in controls.items()})
    require(set(units)==set(packets),'complete cases')
    return packets,units,pins

def coefficient_profile(units):
    profile=deepcopy(units['positive']['sources'][0]['encoded_corner_units_HOST'][0]['rotation_RN64']['coefficients'])
    require(set(profile)=={'cos','sin'},'fixed coefficient names')
    for name,odd in [('cos',0),('sin',1)]:
        require(len(profile[name])==7,'seven coefficients')
        for j,c in enumerate(profile[name]):
            exact=F((-1)**j,math.factorial(2*j+odd))
            require(c['exact_rational']==pair(exact),'exact Taylor coefficient')
            require(c['error_rational']==pair(abs(decode(c['uint64'])-exact)),'fixed coefficient encoding error')
    for c in units.values():
        for s in c['sources']:
            if s['unit_HOST_evaluated']:
                for u in s['encoded_corner_units_HOST']:
                    require(u['rotation_RN64']['coefficients']==profile,'same retained coefficient words')
    return profile

def bounds(interval,profile):
    """Internal theorem: profile comes ONLY from pinned receipts, not caller claims."""
    require(type(interval) is list and len(interval)==2,'ordered angle interval')
    lo,hi=map(rational,interval);require(-1<=lo<=hi<=1,'angle interval inside [-1,1] rad')
    x=[lo,hi];X=max(map(abs,x));xmin=F(0) if lo<=0<=hi else min(map(abs,x))
    trace=[]
    def node(a,b,op,label):
        values=[v*w for v in a for w in b] if op=='mul' else [a[0]+b[0],a[1]+b[1]]
        exact=[min(values),max(values)]
        charge=box.rounding_charge(max(map(abs,exact)))
        rounded=[exact[0]-charge,exact[1]+charge]
        trace.append({'label':label,'op':op,'input_intervals':[[pair(v) for v in a],[pair(v) for v in b]],
                      'exact_interval':list(map(pair,exact)),'rounding_charge_abs':pair(charge),
                      'output_interval':list(map(pair,rounded))})
        return rounded,charge
    # Same-input square needs correlation, not an independent x*x interval.
    sq=[xmin*xmin,X*X];ez=box.rounding_charge(sq[1])
    z=[max(F(0),sq[0]-ez),sq[1]+ez]
    trace.append({'label':'square','op':'correlated_square','input_intervals':[list(map(pair,x))],
                  'exact_interval':list(map(pair,sq)),'rounding_charge_abs':pair(ez),'output_interval':list(map(pair,z))})
    Z=max(map(abs,z));terms={}
    for name,odd in [('cos',0),('sin',1)]:
        cs=[F((-1)**j,math.factorial(2*j+odd)) for j in range(7)]
        encoded=[decode(c['uint64']) for c in profile[name]]
        h=[encoded[-1],encoded[-1]];ideal_abs=abs(cs[-1])
        charges={'coefficients':abs(encoded[-1]-cs[-1]),'square':F(0),'RN_nodes':F(0)}
        for j in range(5,-1,-1):
            p,em=node(h,z,'mul',name+'.mul'+str(j))
            h,ea=node(p,[encoded[j],encoded[j]],'add',name+'.add'+str(j))
            charges={k:Z*v for k,v in charges.items()}
            charges['coefficients']+=abs(encoded[j]-cs[j])
            charges['square']+=ideal_abs*ez
            charges['RN_nodes']+=em+ea
            ideal_abs=ideal_abs*X*X+abs(cs[j])
        if odd:
            h,ef=node(h,x,'mul','sin.final')
            charges={k:X*v for k,v in charges.items()};charges['RN_nodes']+=ef
            ideal_abs*=X
        error=sum(charges.values());taylor=X**(14+odd)/math.factorial(14+odd)
        terms[name]={'output_interval':list(map(pair,h)),
                     'error_charges':{k:pair(v) for k,v in charges.items()},
                     'polynomial_error_uniform_bound':pair(error),'Taylor_uniform_remainder':pair(taylor),
                     'ideal_polynomial_abs_upper':pair(ideal_abs)}
    total=sum(F(*t['polynomial_error_uniform_bound'])+F(*t['Taylor_uniform_remainder']) for t in terms.values())
    phase=total/(1-total) if total<F(1,2) else None
    return {'model':MODEL,'declared_angle_interval':deepcopy(interval),
            'coefficient_profile_sha256':allocation.digest(profile),'x_abs_upper':pair(X),
            'square_RN_uniform_error':pair(ez),'terms':terms,'node_intervals':trace,'bounded_RN_nodes':len(trace),
            'unit_L1_error_to_ideal_at_represented_angle_uniform_bound':pair(total),
            'additional_phase_uniform_bound_rad':pair(phase) if phase is not None else None,
            'uniform_theorem_for_declared_angle_interval_proved':True,
            'arithmetic_hypothesis':'binary64 nearest-even gradual underflow; fixed retained coefficients, Horner26, no FMA',
            'inherited_runner_accepts_entire_interval':False,
            'scope':'declared represented angle interval only; not ORIGINAL scene/selector/transport or backend execution',
            **dict.fromkeys(FALSE,False)}

def uniform_unit_interval_HOST(interval,*,model):
    require(model==MODEL,'explicit uniform unit model')
    _,units,_=load_retained()
    return bounds(interval,coefficient_profile(units))

def audit_uniform_unit_HOST(case_names,*,model):
    require(model==MODEL,'explicit uniform unit model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,units,pins=load_retained();require(set(case_names)<=set(units),'known cases')
    profile=coefficient_profile(units);out={};computed=0;stops=0
    for n in case_names:
        old=units[n];ctx=allocation.context_from_packet(packets[n],allocation.digest(packets[n]),model=allocation.MODEL)
        for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
            require(old[k]==ctx[k],'fresh INPUT unit binding: '+k)
        require([s['source_id'] for s in old['sources']]==ctx['source_order'],'complete source order')
        rows=[]
        for s,assignment in zip(old['sources'],ctx['assignments']):
            require(s['phase_reference_id']==assignment['source_phase_reference_id']
                    and s['terminal_reference_id']==assignment['terminal_reference_id'],'unchanged gauges')
            row={'source_id':s['source_id'],'phase_reference_id':s['phase_reference_id'],
                 'terminal_reference_id':s['terminal_reference_id'],'retained_unit_source_sha256':allocation.digest(s),
                 'retained_partial_unit_phase_pass':s['accepted_unit_phase_bound_CPU_only'],
                 'theorem_computed':False,**dict.fromkeys(FALSE,False)}
            if not s['accepted_unit_phase_bound_CPU_only']:
                row.update(status='STOP',reason=s['reason'],reason_provenance='unchanged_retained_unit_STOP');stops+=1
            else:
                corners=s['encoded_corner_units_HOST'];require(len(corners)==4,'all four encoded angle corners')
                xs=[decode(c['quarter_argument']['HOST_argument_uint64']) for c in corners]
                interval=[pair(min(xs)),pair(max(xs))];t=bounds(interval,profile)
                cap=s['unchanged_original_phase_cap_rad'];p=t['additional_phase_uniform_bound_rad']
                fits=F(*p)<=F(*cap) if p is not None else False
                row.update(theorem_computed=True,interval_theorem=t,
                           retained_angle_corner_sha256=[allocation.digest(c) for c in corners],
                           unchanged_original_phase_cap_rad=deepcopy(cap),
                           polynomial_charge_alone_fits_unchanged_phase_cap=fits,
                           inherited_quarter_bound_NOT_uniform=deepcopy(s['inherited_quarter_phase_bound_rad']),
                           composed_ORIGINAL_uniform_error=None,
                           status='STOP',reason='missing full-domain angle enclosure and upstream ORIGINAL transport/selector proof',
                           reason_provenance='new_full_domain_requirement')
                computed+=1
            rows.append(row)
        out[n]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'cases':out,'case_order':list(case_names),'inherited_pins_verified':len(pins),
            'coefficient_profile':profile,'uniform_intervals_computed':computed,'retained_unit_STOPs':stops,
            'new_RN_casts_or_polynomial_evaluations':0,'new_scene_numeric_operations':0,
            'scope':'26 analytical interval nodes per eligible source, not 26 new point RN evaluations',
            **dict.fromkeys(FALSE,False)}
