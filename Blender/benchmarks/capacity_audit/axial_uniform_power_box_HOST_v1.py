"""Opt-in HOST box theorem, not a continuous-scene or device certificate."""
from copy import deepcopy
from fractions import Fraction as F
import struct
import axial_stage_closure_HOST_v1 as retained
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation

MODEL='axial-uniform-power-encoded-box-RN64-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-STAGE-CLOSURE-HOST-001-CODEX.json'
PREVIOUS_SHA='dbdd33989b452690272a942c31214bf9ed9af0b577dac26b04c685fae2039e27'
VARIANTS=retained.VARIANTS
FALSE=retained.FALSE+('scene_image_enclosed','uniform_source_error_proved','ORIGINAL_global_reference_proved')
MAX=retained.decode(0x7fefffffffffffff)
U=F(1,2**53)
ETA=F(1,2**1075)

def require(ok,why):
    if not ok:raise ValueError(why)

def pair(x):return [x.numerator,x.denominator]

def number(v):
    require(type(v) is list and len(v)==2 and all(type(x) is int for x in v),'canonical rational pair')
    n,d=v
    require(d>0 and max(abs(n).bit_length(),d.bit_length())<=4096,'bounded rational')
    x=F(n,d);require(pair(x)==v,'reduced rational')
    return x

def box_values(box):
    require(type(box) is list and len(box)==2,'real and imaginary intervals')
    out=[]
    for interval in box:
        require(type(interval) is list and len(interval)==2,'ordered interval')
        lo,hi=map(number,interval)
        require(-MAX<=lo<=hi<=MAX,'finite ordered interval')
        out.append((lo,hi))
    return out

def rounding_charge(m):
    """For all finite exact |x|<=m: |RN64(x)-x|<=u*m+eta; exact zero special case."""
    require(0<=m<=MAX,'finite exact-operation range; overflow excluded')
    return U*m+ETA if m else F(0)

def uniform_box_bound(box,*,uniform_field_error_L1,model):
    """B is a SYNTHETIC uniform hypothesis, never a caller scene certificate."""
    require(model==MODEL,'explicit HOST box model')
    v=box_values(box)
    maxima=[max(abs(a),abs(b)) for a,b in v]
    minima=[F(0) if a<=0<=b else min(abs(a),abs(b)) for a,b in v]
    squares=[m*m for m in maxima]
    square_charges=[rounding_charge(m) for m in squares]
    add_max=sum(squares)+sum(square_charges)
    add_charge=rounding_charge(add_max)
    total=sum(square_charges)+add_charge
    lower_field=lower_power=prop=rel_field=rel_power=None
    if uniform_field_error_L1 is not None:
        b=number(uniform_field_error_L1);require(b>=0,'nonnegative uniform hypothesis')
        lower_field=max(F(0),sum(minima)-b)
        lower_power=max(F(0),max(minima)-b)**2
        prop=2*max(maxima)*b+b*b
        rel_field=b/lower_field if lower_field else None
        rel_power=(prop+total)/lower_power if lower_power else None
    result={'model':MODEL,'box':deepcopy(box),
            'max_abs_components':[pair(x) for x in maxima],
            'min_abs_components':[pair(x) for x in minima],
            'exact_square_max':[pair(x) for x in squares],
            'square_RN64_uniform_charges':[pair(x) for x in square_charges],
            'exact_add_input_max':pair(add_max),'add_RN64_uniform_charge':pair(add_charge),
            'power_RN64_uniform_charge':pair(total),
            'uniform_field_error_L1_hypothesis':deepcopy(uniform_field_error_L1),
            'ORIGINAL_field_L1_global_lower':pair(lower_field) if lower_field is not None else None,
            'ORIGINAL_power_global_lower':pair(lower_power) if lower_power is not None else None,
            'field_to_power_uniform_charge':pair(prop) if prop is not None else None,
            'relative_field_global_upper':pair(rel_field) if rel_field is not None else None,
            'relative_power_global_upper':pair(rel_power) if rel_power is not None else None,
            'uniform_RN_bound_for_declared_box_proved':True,
            'RN_graph':['RN64(real*real)','RN64(imag*imag)','RN64(square_real+square_imag)'],
            'arithmetic_model':'binary64 nearest-even gradual underflow, no FMA/FTZ; analytical HOST hypothesis',
            'scope':'all represented inputs in declared box; conditional ORIGINAL theorem if B uniform; not scene/device evidence',
            **dict.fromkeys(FALSE,False)}
    if uniform_field_error_L1 is None:
        result.update(status='STOP',reason='missing full-domain field/source error bound; corner B is not uniform B')
    elif rel_field is None or rel_power is None:
        result.update(status='STOP',reason='ORIGINAL global lower is zero; relative bound undefined, no epsilon')
    else:result.update(status='CONDITIONAL_SYNTHETIC_ONLY',reason='uniform B assumed, not certified for any scene')
    return result

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-STAGE-CLOSURE-HOST-001','predecessor task')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for path,h in pins.items():io.read(path,h)
    packets,relative,fields,powers,trees,_=retained.load_retained()
    return packets,relative,fields,powers,io.payload(r)['data'],pins

def audit_uniform_power_box_HOST(case_names,*,retained_variant,model):
    require(model==MODEL,'explicit box model')
    require(type(retained_variant) is str and retained_variant in VARIANTS,'pinned variant')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,relative,fields,powers,closure,pins=load_retained()
    selected=closure[retained_variant]['cases']
    require(set(case_names)<=set(selected),'known cases in selected variant')
    out={};computed=0
    for n in case_names:
        c=selected[n];r=relative[retained_variant]['cases'][n];p=powers[retained_variant]['cases'][n]
        f=fields[p['retained_variant']]['cases'][n]
        ctx=allocation.context_from_packet(packets[n],allocation.digest(packets[n]),model=allocation.MODEL)
        require(ctx==c['context']==r['context']==p['context']==f['context'],'same fresh six-buffer INPUT context')
        require(c['retained_case_sha256']==allocation.digest(r),'closure relative case diamond')
        require([s['source_id'] for s in f['sources']]==ctx['source_order'],'complete source order')
        require(all([[g['port'],g['coherence_group']] for g in x['groups']]==ctx['groups'] for x in (c,r,p,f)),
                'complete ordered groups')
        groups=[]
        for i,(cg,rg,pg,fg) in enumerate(zip(c['groups'],r['groups'],p['groups'],f['groups'])):
            require(cg['retained_relative_group_sha256']==allocation.digest(rg)
                    and rg['retained_field_group_sha256']==allocation.digest(fg)
                    and rg['retained_power_group_sha256']==allocation.digest(pg),'exact group diamonds')
            require(cg['source_order']==rg['source_order']==pg['source_order']==fg['source_order'],'same complete group sources')
            require(cg['stage_closure_proved'] is False,'no inherited full closure')
            row={'port':fg['port'],'coherence_group':fg['coherence_group'],'source_order':deepcopy(fg['source_order']),
                 'retained_closure_group_sha256':allocation.digest(cg),
                 'retained_field_group_sha256':allocation.digest(fg),'retained_power_group_sha256':allocation.digest(pg),
                 'retained_corner_limits_pass':cg['retained_corner_limits_pass'],
                 'retained_group_status':cg['status'],'retained_group_reason':cg['reason'],
                 'remaining_missing_stage_ids':deepcopy(cg['missing_stage_ids']),
                 'box_computed':False,**dict.fromkeys(FALSE,False)}
            if not fg['accepted_retained_corner_group_reduction_CPU_only']:
                row.update(status=cg['status'],reason=cg['reason'],reason_provenance='unchanged_retained_STOP_FAIL')
            else:
                # No foreign producer or inherited numeric audit runs here; only pinned sum words.
                corners=fg['corner_sums']
                require(type(corners) is list and len(corners)==4**len(fg['source_order']),'all retained encoded corners')
                values=[tuple(retained.decode(w) for w in t['sum_uint64']) for t in corners]
                require(all(len(v)==2 for v in values),'complex words')
                box=[[pair(min(v[j] for v in values)),pair(max(v[j] for v in values))] for j in (0,1)]
                theorem=uniform_box_bound(box,uniform_field_error_L1=None,model=model)
                plan=p['power_plan_result']
                cap=plan['groups'][i]['power_RN64_cap_abs'] if plan['power_INPUT_valid'] else None
                fits=number(theorem['power_RN64_uniform_charge'])<=number(cap) if cap is not None else False
                row.update(box_computed=True,box=box,
                           retained_field_corner_sha256=[allocation.digest(t) for t in corners],
                           retained_corner_error_NOT_uniform_B=deepcopy(fg['error_L1_to_ORIGINAL_group_corner_sum_bound']),
                           box_origin='hull of retained encoded field corners, not certified entire scene image',
                           box_theorem=theorem,unchanged_power_RN64_cap_abs=deepcopy(cap),
                           declared_box_RN_budget_evaluated=cap is not None,declared_box_RN_budget_fits=fits,
                           status=cg['status'] if cg['status']=='FAIL' else 'STOP',
                           reason=cg['reason'] if cg['status']=='FAIL' else theorem['reason'],
                           reason_provenance='unchanged_retained_FAIL' if cg['status']=='FAIL' else 'missing_scene_enclosure_and_uniform_source_B')
                computed+=1
            groups.append(row)
        out[n]={'context':ctx,'retained_variant':retained_variant,
                'retained_closure_case_sha256':allocation.digest(c),
                'groups':groups,'retained_source_STOP_FAILs':deepcopy(c['retained_source_STOP_FAILs']),
                **dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'retained_variant':retained_variant,'case_order':list(case_names),'cases':out,
            'inherited_pins_verified':len(pins),'boxes_computed':computed,'new_scene_RN_nodes':0,
            'new_scene_geometry_phase_field_power_computations':0,**dict.fromkeys(FALSE,False)}

def synthetic_power_samples(*,model):
    require(model==MODEL,'explicit synthetic model')
    # New bounded controls only, no retained scene replay.
    one=0x3ff0000000000000;half=0x3fe0000000000000;sign=1<<63
    words=[(0,0),(sign,0),(1,0),(1<<51,1),(half,half),(one+3,half+5),
           (one+7,one+9),(one|sign,half),(one,(one+11)|sign),
           (0x2000000000000000,0x2000000000000001),(0x5fe0000000000000,0),(half|sign,half|sign)]
    samples=[]
    for a,b in words:
        x,y=retained.decode(a),retained.decode(b)
        box=[[pair(x),pair(x)],[pair(y),pair(y)]]
        theorem=uniform_box_bound(box,uniform_field_error_L1=None,model=model)
        trace=[]
        for op,l,r in [('mul',a,a),('mul',b,b)]:
            exact=retained.decode(l)*retained.decode(r)
            w=struct.unpack('<Q',struct.pack('<d',float(exact)))[0]
            trace.append({'op':op,'left_uint64':l,'right_uint64':r,'output_uint64':w,
                          'exact_rational':pair(exact),'RN_error_abs':pair(abs(retained.decode(w)-exact))})
        l,r=[t['output_uint64'] for t in trace];exact=retained.decode(l)+retained.decode(r)
        w=struct.unpack('<Q',struct.pack('<d',float(exact)))[0]
        trace.append({'op':'add','left_uint64':l,'right_uint64':r,'output_uint64':w,
                      'exact_rational':pair(exact),'RN_error_abs':pair(abs(retained.decode(w)-exact))})
        actual=abs(retained.decode(w)-(x*x+y*y))
        require(actual<=number(theorem['power_RN64_uniform_charge']),'synthetic RN theorem containment')
        samples.append({'label':'SYNTHETIC_NOT_SCENE','input_uint64':[a,b],'box_theorem':theorem,
                        'trace':trace,'actual_power_error_abs':pair(actual)})
    return {'samples':samples,'new_synthetic_RN_nodes':3*len(samples),'new_scene_RN_nodes':0}
