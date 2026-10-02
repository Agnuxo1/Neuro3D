"""Conditional nonzero HOST unit bound over retained restricted axial scene domains."""
import base64,math
from copy import deepcopy
from fractions import Fraction as F
import axial_HOST_readout_contract_v1 as boundary
import axial_zero_singleton_unit_HOST_v1 as zero
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-nonzero-domain-Horner26-ORIGINAL-bound-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-HOST-READOUT-CONTRACT-001-CODEX.json'
PREVIOUS_SHA='51abb0abe0b462ed943a9115c93db70604c43a5246511cbe9b774b690dc9b8e6'
DOMAIN=zero.PREVIOUS
RECTANGLE=zero.RECTANGLE
UNIFORM='coordinacion/respuestas/AXIAL-UNIFORM-UNIT-HOST-001-CODEX.json'
FALSE=boundary.FALSE
FLAG='restricted_nonzero_unit_error_to_ORIGINAL_bound_proved'
require=io.require
number=zero.number
pair=zero.pair
decode=zero.decode
digest=allocation.digest
MIN_NORMAL=F(1,2**1022)
MAX=decode(0x7fefffffffffffff)

def compact(v):
    if type(v) is dict:
        return {('node_intervals_sha256' if k=='node_intervals' else k):
                (digest(x) if k=='node_intervals' else compact(x)) for k,x in v.items()}
    if type(v) is list:
        if len(v)==2 and all(type(x) is int for x in v) and max(abs(x).bit_length() for x in v)>256:
            return {'exact_rational_sha256':digest(v),'numerator_bits':abs(v[0]).bit_length(),
                    'denominator_bits':v[1].bit_length()}
        return [compact(x) for x in v]
    return v

def analytic_horner(interval,profile):
    """New rational interval reconstruction, no point polynomial/RN/cast execution."""
    require(type(interval) is list and len(interval)==2,'two canonical angle endpoints')
    lo,hi=map(number,interval);require(-1<=lo<=hi<=1,'unchanged Horner [-1,1] domain')
    require(lo>0 or hi<0,'nonzero interval only')
    require(set(profile)=={'cos','sin'},'fixed cos/sin profile')
    X=max(abs(lo),abs(hi));m=min(abs(lo),abs(hi));trace=[]
    def charge(v):
        require(0<=v<=MAX,'finite exact operation magnitude')
        return v/F(2**53)+F(1,2**1075) if v else F(0)
    ez=charge(X*X);z=[max(F(0),m*m-ez),X*X+ez];Z=max(map(abs,z))
    trace.append({'label':'square','op':'correlated_square','input_intervals':[interval],
                  'exact_interval':[pair(m*m),pair(X*X)],'rounding_charge_abs':pair(ez),
                  'output_interval':list(map(pair,z))})
    def node(a,b,op,label):
        vals=[x*y for x in a for y in b] if op=='mul' else [a[0]+b[0],a[1]+b[1]]
        exact=[min(vals),max(vals)];e=charge(max(map(abs,exact)))
        out=[exact[0]-e,exact[1]+e]
        trace.append({'label':label,'op':op,'input_intervals':[[pair(x) for x in a],[pair(x) for x in b]],
                      'exact_interval':list(map(pair,exact)),'rounding_charge_abs':pair(e),
                      'output_interval':list(map(pair,out))})
        return out,e
    terms={}
    for name,odd in [('cos',0),('sin',1)]:
        require(len(profile[name])==7,'fixed seven coefficients')
        exact=[F((-1)**j,math.factorial(2*j+odd)) for j in range(7)]
        encoded=[decode(c['uint64']) for c in profile[name]]
        for c,v,q in zip(profile[name],encoded,exact):
            require(number(c['exact_rational'])==q and number(c['error_rational'])==abs(v-q),'exact coefficient/encoding ledger')
        h=[encoded[6],encoded[6]];I=abs(exact[6]);ec=abs(encoded[6]-exact[6]);es=er=F(0)
        for j in range(5,-1,-1):
            p,em=node(h,z,'mul',name+'.mul'+str(j))
            h,ea=node(p,[encoded[j],encoded[j]],'add',name+'.add'+str(j))
            ec=Z*ec+abs(encoded[j]-exact[j]);es=Z*es+I*ez;er=Z*er+em+ea
            I=I*X*X+abs(exact[j])
        if odd:
            h,ef=node(h,[lo,hi],'mul','sin.final');ec*=X;es*=X;er=er*X+ef;I*=X
        terms[name]={'output_interval':list(map(pair,h)),
            'error_charges':{'coefficients':pair(ec),'square':pair(es),'RN_nodes':pair(er)},
            'polynomial_error_uniform_bound':pair(ec+es+er),
            'Taylor_uniform_remainder':pair(X**(14+odd)/math.factorial(14+odd)),
            'ideal_polynomial_abs_upper':pair(I)}
    total=sum(number(t['polynomial_error_uniform_bound'])+number(t['Taylor_uniform_remainder']) for t in terms.values())
    require(0<total<F(1,2),'nonzero finite small unit bound for angular inequality')
    require(len(trace)==26,'Horner26 analytical nodes')
    normal=[]
    for t in trace:
        a,b=map(number,t['output_interval'])
        require((MIN_NORMAL<=a<=b<=MAX) or (-MAX<=a<=b<=-MIN_NORMAL),'restricted all-node normal range')
        normal.append(t['label'])
    return total,terms,trace,normal

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-HOST-READOUT-CONTRACT-001','predecessor task')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(path):return io.payload(allocation.parse(io.read(path,pins[path])))['data']['audit']
    domain=data(DOMAIN);rect=data(RECTANGLE);uniform=data(UNIFORM)
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    packets.update({n:v['parent'] for n,v in io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls'].items()})
    require(set(packets)==set(domain['cases'])==set(rect['cases'])==set(uniform['cases']),'all retained sources/cases')
    return packets,domain,rect,uniform,pins

def compose_domain(ctx,d,r,u,profile,cap):
    require(d['restricted_coordinate_box_to_parameter_rectangle_proved'] is True,'restricted whole coordinate box required')
    require(d['retained_argument_rectangle_source_sha256']==digest(r),'same retained rectangle row')
    require(r['retained_uniform_unit_source_sha256']==digest(u),'same retained uniform unit row')
    require(d['source_id']==r['source_id']==u['source_id'],'same source identity')
    assignments=[a for a in ctx['assignments'] if a['source_id']==d['source_id']]
    require(len(assignments)==1,'one explicit source assignment')
    assignment=assignments[0]
    require(u['phase_reference_id']==assignment['source_phase_reference_id']
            and u['terminal_reference_id']==assignment['terminal_reference_id'],'same ORIGINAL source and terminal gauge')
    branch=r['parameter_branch'];im=r['argument_image'];cert=d['restricted_domain_proof']
    sel=cert['uniform_affine_selector_proof']
    require(cert['ORIGINAL_inside_coordinate_box'] is True and sel['mirror_first_uniform_clearance'] is True
            and sel['strict_positive_first_and_reflected_second'] is True,'ORIGINAL inclusion and uniform complete events')
    require(sel['effective_reference_length_interval']==branch['length_interval']
            and sel['wavelength_interval']==branch['wavelength_interval'],'same correlated scene length/wavelength rectangle')
    require(branch['centered_branch_over_rectangle_proved'] is True and branch['quarter_branch_over_rectangle_proved'] is True
            and branch['quarter_turn_endpoint_integers']==[branch['ORIGINAL_quarter_turn']]*2,'stable ORIGINAL quarter branch')
    require(r['argument_image_over_declared_rectangle_enclosed'] is True
            and im['argument_image_over_declared_rectangle_enclosed'] is True
            and im['old_argument_RN_graph_defined_over_declared_rectangle'] is True,'whole represented angle image')
    theorem=u['interval_theorem'];interval=theorem['declared_angle_interval']
    lo,hi=map(number,interval);alo,ahi=map(number,im['argument_interval'])
    require(lo<=alo<=ahi<=hi and (alo>0 or ahi<0),'nonzero image contained in retained polynomial interval')
    require(theorem['coefficient_profile_sha256']==digest(profile)
            and theorem['arithmetic_hypothesis']=='binary64 nearest-even gradual underflow; fixed retained coefficients, Horner26, no FMA'
            and theorem['inherited_runner_accepts_entire_interval'] is False,'conditional HOST graph, no inherited execution')
    B,terms,trace,normal=analytic_horner(interval,profile)
    phase=B/(1-B)
    require(theorem['terms']==compact(terms) and theorem['node_intervals_sha256']==digest(trace)
            and theorem['unit_L1_error_to_ideal_at_represented_angle_uniform_bound']==compact(pair(B))
            and theorem['additional_phase_uniform_bound_rad']==compact(pair(phase)),'retained analytical polynomial certificate exact')
    require(cap==d['unchanged_original_phase_cap_rad']==r['unchanged_original_phase_cap_rad']
            ==u['unchanged_original_phase_cap_rad'] and number(cap)==F(1,10**12),'same ORIGINAL INPUT cap, no enlargement')
    upstream=number(branch['uniform_upstream_phase_to_fixed_ORIGINAL_rad'])
    arg=number(im['uniform_argument_error_bound_rad']);delta=number(im['uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad'])
    require(upstream>=0 and arg>=0 and delta==upstream+arg,'separate ORIGINAL parameter and argument charges')
    require(r['retained_uniform_unit_interval_covers_argument_image'] is True,'retained interval coverage')
    require(d['retained_unit_polynomial_charge_fits'] is True and u['polynomial_charge_alone_fits_unchanged_phase_cap'] is True,'old necessary charge fit')
    require(phase+delta<=number(cap),'composed phase must fit unchanged cap; not budget admission')
    return {'model':MODEL,FLAG:True,'source_id':d['source_id'],
        'retained_domain_row_sha256':digest(d),'retained_rectangle_row_sha256':digest(r),
        'retained_uniform_unit_row_sha256':digest(u),'ORIGINAL_assignment_sha256':digest(assignment),
        'coefficient_profile_sha256':digest(profile),'retained_analytic_trace_sha256':digest(trace),
        'represented_argument_interval':deepcopy(im['argument_interval']),
        'polynomial_unit_L1_bound_decimal':[str(B.numerator),str(B.denominator)],
        'parameter_phase_bound_rad':pair(upstream),'argument_phase_bound_rad':pair(arg),
        'composed_parameter_argument_phase_bound_rad':pair(delta),
        'uniform_unit_L1_to_fixed_ORIGINAL_bound_decimal':[str((B+2*delta).numerator),str((B+2*delta).denominator)],
        'uniform_phase_to_fixed_ORIGINAL_bound_decimal':[str((phase+delta).numerator),str((phase+delta).denominator)],
        'unchanged_original_phase_cap_rad':deepcopy(cap),'phase_charge_fits_unchanged_cap':True,
        'restricted_Horner26_nodes_normal_proved':True,'normal_node_labels':normal,
        'unit_composition_rule':'L1 <= B + 2*delta; angle <= B/(1-B) + delta; same exact quarter permutation',
        'arithmetic_hypothesis':theorem['arithmetic_hypothesis'],
        'new_RN_or_scene_producer_executions':0,'status':'STOP',
        'reason':'conditional restricted HOST unit bound only; missing source/stage INPUT allocations and executed backend',
        **dict.fromkeys(FALSE,False)}

def audit_nonzero_unit_domain_HOST(case_names,*,model):
    require(model==MODEL,'explicit conditional nonzero HOST model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique case names')
    packets,domain,rect,uniform,pins=load_retained();require(set(case_names)<=set(packets),'known retained cases')
    cases={};proved=unitstops=outside=0
    for n in case_names:
        ctx=allocation.context_from_packet(packets[n],digest(packets[n]),model=allocation.MODEL)
        require(ctx==domain['cases'][n]['context']==rect['cases'][n]['context']==uniform['cases'][n]['context'],'same fresh complete INPUT')
        ds=domain['cases'][n]['sources'];rs=rect['cases'][n]['sources'];us=uniform['cases'][n]['sources']
        require([s['source_id'] for s in ds]==[s['source_id'] for s in rs]==[s['source_id'] for s in us]==ctx['source_order'],'complete ordered sources')
        meta=allocation.parse(base64.b64decode(packets[n]['buffers_base64']['input_metadata_json'],validate=True))
        rows=[]
        for d,r,u in zip(ds,rs,us):
            row={'source_id':d['source_id'],'status':'STOP',FLAG:False,
                 'retained_domain_row_sha256':digest(d),**dict.fromkeys(FALSE,False)}
            if d['restricted_coordinate_box_to_parameter_rectangle_proved'] is not True:
                unitstops+=1;row.update(reason=d['reason'],reason_provenance='unchanged_retained_unit_STOP')
            elif r['argument_image']['argument_interval']==[[0,1],[0,1]]:
                outside+=1;row.update(reason='exact-zero theorem previously retained; not recomputed or changed',reason_provenance='outside_nonzero_scope')
            else:
                proof=compose_domain(ctx,d,r,u,uniform['coefficient_profile'],meta['original_path_phase_caps'][d['source_id']])
                proved+=1;row.update(proof=proof,reason=proof['reason'],**{FLAG:True})
            rows.append(row)
        cases[n]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,
        'restricted_nonzero_source_unit_bounds_proved':proved,'retained_unit_STOPs':unitstops,
        'zero_domains_outside_scope':outside,'inherited_pins_verified':len(pins),
        'new_RN_or_scene_producer_executions':0,**dict.fromkeys(FALSE,False)}
