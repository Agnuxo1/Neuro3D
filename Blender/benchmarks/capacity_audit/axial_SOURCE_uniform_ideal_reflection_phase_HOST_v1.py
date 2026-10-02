"""Uniform ideal -1 isometry and principal phase under conditional RN model; HOST ONLY."""
import struct
from copy import deepcopy
from fractions import Fraction as F
import axial_SOURCE_uniform_UNIT_ORIGINAL_link_HOST_v1 as prior
io,allocation,require,digest,pair=prior.io,prior.allocation,prior.require,prior.digest,prior.pair
domain,FALSE=prior.domain,prior.FALSE
original=domain.original
MODEL='axial-SOURCE-box-ideal-minus-one-principal-phase-conditional-HOST-v1'
FLAG='conditional_SOURCE_box_ideal_reflection_phase_HOST_proved'
MATERIAL_MODEL='exact ideal -1 sign reversal; L1 isometry; NOT physical material'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-UNIT-ORIGINAL-LINK-HOST-001-CODEX.json'
PARENT_SHA='2160956d3e6b9feaaabe70329698fdb4d5df177a1d9cf7a899fa65477dd6b34c'
MATERIAL='coordinacion/respuestas/AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001-CODEX.json'
CHARGES=('source_encoding_times_UNIT_L1','source_decode_times_UNIT_L1','product_six_RN64_nodes_L1')+tuple('source_unit_'+n for n in prior.producer.UNIT_NAMES)

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA));require(r['task_id']=='AXIAL-SOURCE-UNIFORM-UNIT-ORIGINAL-LINK-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded=prior.load_retained();require(all(pins.get(p)==h for p,h in loaded[-1].items()),'same immutable domain/SOURCE branches')
    mat=io.payload(allocation.parse(io.read(MATERIAL,pins[MATERIAL])))['data']['audit']
    return loaded[0],loaded[1],io.payload(r)['data'],mat,pins

def reflected_phase_HOST(box,charges,*,model,material_model):
    require(type(model) is str and model==MODEL and type(material_model) is str and material_model==MATERIAL_MODEL,'explicit conditional ideal model')
    intervals=domain.box_values(box)
    q=None if charges is None else {k:domain.rational(v) for k,v in charges.items()}
    if q is not None:require(type(charges) is dict and set(q)==set(CHARGES) and all(v>=0 for v in q.values()),'fourteen exact nonnegative retained charges')
    distances=[F(0) if lo<=0<=hi else min(abs(lo),abs(hi)) for lo,hi in intervals]
    m=max(distances);eps=None if q is None else sum(q.values(),F(0))
    out={'model':MODEL,'material_model':MATERIAL_MODEL,'box_reim':deepcopy(box),
        'component_min_abs':list(map(pair,distances)),'amplitude_modulus_lower_bound':pair(m),
        'fifteen_conditional_reflected_charges_L1':None if q is None else {**deepcopy(charges),'ideal_material_exact_model_L1':[0,1]},
        'conditional_reflected_RN_model_error_L1':None if eps is None else pair(eps),
        'conditional_principal_phase_bound_rad':None,'positive_radial_projection_lower_bound':None,FLAG:False,
        'reference':'variable ORIGINAL A times exp(i fixed ORIGINAL theta) times exact ideal -1',
        'material_error_zero_scope':'exact algebraic sign reversal ONLY; not an executed material charge',
        'material_executed':False,'executed_material_charge_L1':None,'physical_material_authenticated':False,
        'uniform_executed_SOURCE_error_L1':None,'uniform_SOURCE_enclosure_proved':False,
        'phase_INPUT_quota_fits':None,'unwrapped_phase_proved':False,'frozen_guard_admission_for_entire_box_proved':False,
        'status':'STOP',**dict.fromkeys(FALSE,False)}
    if eps is None:out['reason']='missing conditional uniform bare proof; None is not zero';return out
    if m<=0 or eps>=m:out['reason']='origin or non-strict radial margin; phase undefined/uncertified';return out
    gap=m-eps
    out.update({FLAG:True,'conditional_principal_phase_bound_rad':pair(eps/gap),
        'positive_radial_projection_lower_bound':pair(gap),
        'reason':'conditional RN ideal-minus-one isometry; |reference|>=m, radial>=m-epsilon>0, atan(epsilon/gap)<=epsilon/gap; guard execution STILL STOP'})
    return out

def audit_reflected_phase_HOST(variant,*,model,material_model):
    require(type(variant) is str and variant in prior.prior.encoder.VARIANTS and model==MODEL and material_model==MATERIAL_MODEL,'explicit retained variant/model')
    packets,data,certs,mat,pins=load_retained()
    old=data['synthetic_scene_domains'] if variant=='synthetic_domains' else data['real_missing']
    plans=data['synthetic_domain_INPUT_plans'] if variant=='synthetic_domains' else {};checked={}
    for name in old['case_order']:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        c=certs[variant]['cases'][name];mc=mat['cases'][name]
        require(ctx==old['cases'][name]['context']==c['context']==mc['context'],'same complete ORIGINAL SOURCE/material context')
        dom=domain.validate_domain(packets[name],ctx,plans.get(name));require(digest(dom)==digest(old['cases'][name]['domain_INPUT']),'unchanged typed domain INPUT')
        rows=None
        if dom['domain_INPUT_valid']:
            for v in (c,mc):require(type(v['sources']) is list and [s['source_id'] for s in v['sources']]==ctx['source_order'],'complete ordered SOURCE/material rows')
            snap,_=original.snapshot_from_packet(packets[name],ctx)
            phase=snap['objects']['M']['phase_rad']
            require(type(phase) is float,'binary64 ORIGINAL material phase')
            word=struct.unpack('<Q',struct.pack('<d',phase))[0];require(word in (0,1<<63),'exact +/-zero ORIGINAL mirror phase')
            rows=[]
            for src,cert,mr in zip(dom['sources'],c['sources'],mc['sources']):
                profile=mr['material_profile']
                require(src['source_id']==cert['source_id']==mr['source_id']==profile['source_id'] and cert['domain_source_sha256']==digest(src),'same SOURCE domain/material identity')
                require(mr['source_profile_admitted_HOST_only'] is True and profile['profile_admitted_HOST_only'] is True and
                    mr['material_executed'] is profile['material_executed'] is False and mr['executed_material_charge_L1'] is None,'retained HOST preflight not new material execution')
                require(type(profile['mirror_phase_ORIGINAL_uint64']) is int and profile['mirror_phase_ORIGINAL_uint64']==word and
                    digest(profile['ideal_coefficient_exact_reim'])==digest([[-1,1],[0,1]]),'same fixed exact ideal -1 coefficient')
                require(mr['retained_source_row_sha256']==cert['retained_bare_SOURCE_row_sha256'],'same retained bare SOURCE/material SHA')
                require(mr['phase_reference_id']==src['source_phase_reference_id'] and mr['terminal_reference_id']==src['terminal_reference_id']==src['common_terminal_reference_id'],'same fixed material/SOURCE gauges')
                require(cert['link'][prior.FLAG] is True and cert['whole_box_guard_admission_disproved'] is True and
                    cert['material_included'] is False and cert['uniform_executed_SOURCE_error_L1'] is None and all(cert[k] is False for k in FALSE),'typed conditional bare proof ONLY, guard negative preserved')
                require(cert['link']['box_reim']==src['box_reim'] and cert['link']['unit_input_scope']=='fixed ORIGINAL geometry/wavelength/path/gauges; SOURCE field reim only varies','same complete box/fixed geometry')
                q=cert['bare_charges_L1'];require(type(q) is dict and set(q)==set(CHARGES),'fourteen separate conditional bare charges')
                vals=[domain.rational(v) for v in q.values()]
                require(all(v>=0 for v in vals) and sum(vals,F(0))==domain.rational(cert['uniform_bare_RN_model_bound_to_A_times_ideal_UNIT_L1']),'exact unchanged bare total ONCE')
                rows.append((src,cert,mr))
        else:require(c['sources'] is None,'missing domain: no point numerical material/SOURCE inspection')
        checked[name]=(ctx,rows)
    cases={};count=0
    # ALL INPUT/material/certificate checks above before ANY new phase composition.
    for name,(ctx,rows) in checked.items():
        out=None
        if rows is not None:
            out=[]
            for src,cert,mr in rows:
                proof=reflected_phase_HOST(src['box_reim'],cert['bare_charges_L1'],model=model,material_model=material_model);count+=int(proof[FLAG])
                out.append({'source_id':src['source_id'],'domain_source_sha256':digest(src),
                    'retained_UNIT_link_SOURCE_sha256':digest(cert),'retained_material_admission_SOURCE_sha256':digest(mr),
                    'proof':proof,'whole_box_guard_admission_disproved':True})
        cases[name]={'context':ctx,'sources':out,'group_phase_bound_rad':None,'group_field_bound_L1':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'case_order':deepcopy(old['case_order']),'cases':cases,
        'inherited_pins_verified':len(pins),'conditional_reflected_phase_bounds':count,
        'new_native_operations':0,'old_suites_producers_reexecuted':0,'group_admissions':0,
        'uniform_SOURCE_enclosure_proved':False,'cost_scope':'HOST conditional mathematical reflection/phase; full costs UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
