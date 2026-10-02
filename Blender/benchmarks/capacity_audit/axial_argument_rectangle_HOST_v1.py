"""Declared encoded parameter rectangle -> quarter/RN angle enclosure, not full scene."""
from copy import deepcopy
from fractions import Fraction as F
import axial_uniform_unit_HOST_v1 as unit
import axial_uniform_power_box_HOST_v1 as box
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-parameter-rectangle-quarter-RN-monotone-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-UNIFORM-UNIT-HOST-001-CODEX.json'
PREVIOUS_SHA='0ab0e6d7236cc215f53034b35bb4d89d9dce37cfe133e0287e66f8dc2ed17eac'
ARGUMENT='coordinacion/respuestas/AXIAL-NATIVE-ARGUMENT-HOST-001-CODEX.json'
QUARTER='coordinacion/respuestas/AXIAL-QUARTER-ARGUMENT-HOST-001-CODEX.json'
FALSE=unit.FALSE+('whole_scene_parameter_enclosure_proved','native_argument_implemented')
require=box.require
pair=box.pair
decode=box.retained.decode
SIGN=1<<63
MIN_NORMAL=F(1,2**1022)

def signed512(words):
    require(type(words) is list and len(words)==16 and all(type(w) is int and 0<=w<2**32 for w in words),
            '16 strict uint32 signed512 limbs')
    n=sum(w<<(32*i) for i,w in enumerate(words))
    return n-2**512 if words[15]&0x80000000 else n

def fraction(v):
    x=box.number(v);require(max(abs(x.numerator).bit_length(),x.denominator.bit_length())<=512,'bounded rational')
    return x

def rectangle_branches(length_interval,wavelength_interval,original_length,original_wavelength,*,model):
    """Explicit mathematical parameter domain, never a caller scene certificate."""
    require(model==MODEL,'explicit parameter rectangle model')
    require(type(length_interval) is list and len(length_interval)==2
            and type(wavelength_interval) is list and len(wavelength_interval)==2,'two interval endpoints')
    llo,lhi=map(fraction,length_interval);wlo,whi=map(fraction,wavelength_interval)
    L=fraction(original_length);W=fraction(original_wavelength)
    require(llo<=lhi and 0<wlo<=whi and W>0,'ordered length and strictly positive wavelength')
    corners=[l/w for l in (llo,lhi) for w in (wlo,whi)]
    qlo,qhi=min(corners),max(corners);original=L/W
    jlo=(qlo+F(1,2))//1;jhi=(qhi+F(1,2))//1;jo=(original+F(1,2))//1
    result={'model':MODEL,'length_interval':deepcopy(length_interval),'wavelength_interval':deepcopy(wavelength_interval),
            'ORIGINAL_length':deepcopy(original_length),'ORIGINAL_wavelength':deepcopy(original_wavelength),
            'quotient_corner_rationals':list(map(pair,corners)),'quotient_interval':[pair(qlo),pair(qhi)],
            'ORIGINAL_quotient':pair(original),'centered_turn_endpoint_integers':[jlo,jhi],
            'ORIGINAL_centered_turn':jo,'centered_branch_over_rectangle_proved':False,
            'quarter_branch_over_rectangle_proved':False,'parameter_rectangle_only':True,**dict.fromkeys(FALSE,False)}
    if jlo!=jhi or jlo!=jo:
        return dict(result,status='STOP',reason='centered branch crosses half turn or differs from ORIGINAL; no epsilon/snapping')
    rlo,rhi=qlo-jlo,qhi-jlo;ro=original-jo
    require(-F(1,2)<=rlo<=rhi<F(1,2),'entire centered interval')
    klo=(4*rlo+F(1,2))//1;khi=(4*rhi+F(1,2))//1;ko=(4*ro+F(1,2))//1
    result.update(centered_branch_over_rectangle_proved=True,centered_residual_interval=[pair(rlo),pair(rhi)],
                  quarter_turn_endpoint_integers=[klo,khi],ORIGINAL_quarter_turn=ko)
    if klo!=khi or klo!=ko:
        return dict(result,status='STOP',reason='quarter branch crosses eighth turn or differs from ORIGINAL; no epsilon/snapping')
    tlo,thi=rlo-F(klo,4),rhi-F(klo,4)
    require(-F(1,8)<=tlo<=thi<F(1,8),'entire quarter interval')
    result.update(quarter_branch_over_rectangle_proved=True,quarter_residual_interval=[pair(tlo),pair(thi)],
                  ORIGINAL_quarter_residual=pair(ro-F(ko,4)),
                  uniform_upstream_phase_to_fixed_ORIGINAL_rad=pair(8*max(abs(qlo-original),abs(qhi-original))),
                  status='PROVED_PARAMETER_BRANCH_ONLY',reason='exact quotient extrema and monotone selectors on declared rectangle')
    return result

def rn_cell_contains(exact,word):
    """Check a retained endpoint by rounding-cell membership, not by executing RN."""
    exact=F(exact);value=decode(word)
    require(abs(value)<box.MAX,'finite interior RN cell')
    if not value:
        require((word==0 and exact>=0) or (word==SIGN and exact<0),'canonical exact/underflow zero sign')
        previous,following=-F(1,2**1074),F(1,2**1074)
    elif value>0:previous,following=decode(word-1),decode(word+1)
    else:previous,following=decode(word+1),decode(word-1)
    lower=(previous+value)/2;upper=(value+following)/2;even=(word&1)==0
    require((lower<exact<upper) or (even and exact in (lower,upper)),'RN-even endpoint cell mismatch')
    return {'output_uint64':word,'exact_input':pair(exact),'cell_interval':[pair(lower),pair(upper)],
            'ties_to_even_output':even,'rounding_cell_membership_proved':True,'new_RN_executed':0}

def monotone_image(branch,quarter_corners):
    require(branch['quarter_branch_over_rectangle_proved'] is True,'stable exact parameter branch')
    require(type(quarter_corners) is list and len(quarter_corners)==4,'four retained quarter endpoints')
    j=branch['ORIGINAL_centered_turn'];k=branch['ORIGINAL_quarter_turn'];qs=list(map(lambda v:F(*v),branch['quotient_corner_rationals']))
    casts=[];angles=[];certificates=[]
    pi_words={v['TWO_PI_uint64'] for v in quarter_corners};pi_bounds={tuple(v['TWO_PI_error_bound_rad']) for v in quarter_corners}
    require(len(pi_words)==len(pi_bounds)==1,'same fixed pi INPUT words/error bound')
    p=decode(next(iter(pi_words)));bp=F(*next(iter(pi_bounds)));require(p>0 and bp>=0,'positive represented 2pi')
    for q,c in zip(qs,quarter_corners):
        r=q-j;t=r-F(k,4)
        require(c['original_residual_cycles_rational']==pair(r) and c['quarter_turns_HOST']==k
                and c['quarter_residual_HOST_rational']==pair(t),'corner branch/rational identity')
        require(F(signed512(c['numerator_words']),signed512(c['denominator_words']))==r,'quarter raw signed512 INPUT')
        cast=decode(c['HOST_cast_uint64']);arg=decode(c['HOST_argument_uint64'])
        require(c['HOST_cast_rational']==pair(cast) and c['HOST_argument_rational']==pair(arg),'retained decoded words')
        certificates.append({'cast':rn_cell_contains(t,c['HOST_cast_uint64']),
                             'multiply':rn_cell_contains(cast*p,c['HOST_argument_uint64'])})
        casts.append(cast);angles.append(arg)
    tlo,thi=map(lambda v:F(*v),branch['quarter_residual_interval'])
    lo=qs.index(min(qs));hi=qs.index(max(qs))
    require(casts[lo]==min(casts) and casts[hi]==max(casts)
            and angles[lo]==min(angles) and angles[hi]==max(angles),'monotone extrema consistency')
    clo,chi=min(casts),max(casts);alo,ahi=min(angles),max(angles)
    require(-1<=alo<=ahi<=1,'unchanged Horner domain')
    def normal_or_zero_interval(a,b):
        return a==b==0 or a>=MIN_NORMAL or b<=-MIN_NORMAL
    defined=normal_or_zero_interval(clo,chi) and normal_or_zero_interval(alo,ahi)
    ec=box.rounding_charge(max(abs(tlo),abs(thi)))
    em=box.rounding_charge(p*max(abs(clo),abs(chi)))
    constant=max(abs(tlo),abs(thi))*bp;extra=p*ec+em+constant
    upstream=F(*branch['uniform_upstream_phase_to_fixed_ORIGINAL_rad'])
    return {'retained_endpoint_cell_certificates':certificates,
            'cast_interval':[pair(clo),pair(chi)],'argument_interval':[pair(alo),pair(ahi)],
            'retained_extrema_corner_indices':[lo,hi],'TWO_PI_uint64':next(iter(pi_words)),
            'TWO_PI_error_bound_rad':[next(iter(pi_bounds))[0],next(iter(pi_bounds))[1]],
            'uniform_argument_charges_rad':{'cast':pair(p*ec),'constant_2pi':pair(constant),'multiply':pair(em)},
            'uniform_argument_error_bound_rad':pair(extra),
            'uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad':pair(upstream+extra),
            'argument_image_over_declared_rectangle_enclosed':True,
            'old_argument_RN_graph_defined_over_declared_rectangle':defined,
            'reason':'RN is monotone, fixed positive 2pi; endpoints validated by exact cells; no geometric scene proof',
            'new_RN_casts_or_multiplies':0,**dict.fromkeys(FALSE,False)}

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA));require(r['task_id']=='AXIAL-UNIFORM-UNIT-HOST-001','previous task')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    argument=io.payload(allocation.parse(io.read(ARGUMENT,pins[ARGUMENT])))['cases']
    quarter=io.payload(allocation.parse(io.read(QUARTER,pins[QUARTER])))['cases']
    packets,units,_=unit.load_retained()
    return packets,units,argument,quarter,io.payload(r)['data']['audit'],pins

def audit_argument_rectangle_HOST(case_names,*,model):
    require(model==MODEL,'explicit argument rectangle model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,units,argument,quarter,uniform,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    out={};proved=stops=0
    for n in case_names:
        a=argument[n];q=quarter[n];u=units[n];ru=uniform['cases'][n]
        ctx=allocation.context_from_packet(packets[n],allocation.digest(packets[n]),model=allocation.MODEL)
        require(ctx==ru['context'],'same previous fresh context')
        for old in (a,q,u,a['upstream'],a['upstream']['upstream']):
            for key in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
                require(old[key]==ctx[key],'same INPUT lineage: '+key)
            require([s['source_id'] for s in old['sources']]==ctx['source_order'],'ordered complete sources')
        rows=[]
        for i,(us,qs,rs) in enumerate(zip(u['sources'],q['sources'],ru['sources'])):
            row={'source_id':us['source_id'],'retained_uniform_unit_source_sha256':allocation.digest(rs),
                 'retained_partial_unit_phase_pass':us['accepted_unit_phase_bound_CPU_only'],
                 'argument_image_over_declared_rectangle_enclosed':False,'rectangle_evaluated':False,
                 'retained_unit_polynomial_charge_fits':rs.get('polynomial_charge_alone_fits_unchanged_phase_cap'),
                 **dict.fromkeys(FALSE,False)}
            if not us['accepted_unit_phase_bound_CPU_only']:
                row.update(status='STOP',reason=us['reason'],reason_provenance='unchanged_retained_unit_STOP');stops+=1
            else:
                cyc=a['upstream']['sources'][i];ref=a['upstream']['upstream']['sources'][i]['reference']
                require(qs==us['upstream_quarter_proof'],'quarter/unit exact source diamond')
                require(all(c['quarter_argument']==v for c,v in zip(us['encoded_corner_units_HOST'],qs['encoded_corner_quarter_arguments'])),
                        'all unit angle corners linked')
                lw=ref['effective_reference_length_interval_words'];ww=ref['wavelength_interval_words']
                ls=list(map(signed512,lw));ws=list(map(signed512,ww));original=cyc['original_ideal_cycles']
                corners=cyc['encoded_enclosure_corner_cycles']
                require(len(corners)==4 and [(v['length_words'],v['wavelength_words']) for v in corners]
                        ==[(l,w) for l in lw for w in ww],'exact full parameter rectangle, not corner hull fabrication')
                branch=rectangle_branches([pair(F(v)) for v in ls],[pair(F(v)) for v in ws],
                    pair(F(signed512(original['length_words']))),pair(F(signed512(original['wavelength_words']))),model=model)
                require(branch['quarter_branch_over_rectangle_proved'],'retained eligible branch must be stable')
                image=monotone_image(branch,qs['encoded_corner_quarter_arguments'])
                interval=rs['interval_theorem']['declared_angle_interval']
                lo,hi=map(lambda v:F(*v),interval);alo,ahi=map(lambda v:F(*v),image['argument_interval'])
                covered=lo<=alo<=ahi<=hi
                cap=us['unchanged_original_phase_cap_rad'];total=F(*image['uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad'])
                require(cap==qs['unchanged_original_phase_cap_rad']==a['sources'][i]['unchanged_original_phase_cap_rad'],
                        'unchanged ORIGINAL phase caps')
                row.update(rectangle_evaluated=True,parameter_branch=branch,argument_image=image,
                           retained_reference_sha256=allocation.digest(ref),retained_cycle_source_sha256=allocation.digest(cyc),
                           retained_quarter_source_sha256=allocation.digest(qs),argument_image_over_declared_rectangle_enclosed=True,
                           retained_uniform_unit_interval_covers_argument_image=covered,
                           unchanged_original_phase_cap_rad=deepcopy(cap),
                           uniform_parameter_phase_alone_fits_unchanged_cap=total<=F(*cap),
                           status='STOP',reason='parameter rectangle mapped and bounded; whole-scene parameter enclosure and source/full pipeline still missing',
                           reason_provenance='missing_whole_scene_parameter_certificate')
                proved+=1
            rows.append(row)
        out[n]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':list(case_names),'cases':out,'inherited_pins_verified':len(pins),
            'declared_rectangle_images_proved':proved,'retained_unit_STOPs':stops,
            'new_RN_casts_or_multiplies':0,'previous_producers_reexecuted':False,**dict.fromkeys(FALSE,False)}
