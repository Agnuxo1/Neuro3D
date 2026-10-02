"""Opt-in negative HOST proof: exact binary64 SOURCE witness, frozen guard rejection."""
from copy import deepcopy
from fractions import Fraction as F
import axial_SOURCE_uniform_hilo_decode_HOST_v1 as prior
import axial_geometry_decode_guard_CPU_v1 as guard
io,allocation,require,digest,pair=prior.io,prior.allocation,prior.require,prior.digest,prior.pair
domain=prior.prior
FALSE=prior.FALSE
MODEL='axial-SOURCE-box-frozen-guard-exact-counterexample-HOST-v1'
FLAG='whole_box_frozen_guard_admission_disproved_HOST'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-HILO-DECODE-HOST-001-CODEX.json'
PARENT_SHA='0c0bba56d7a617280bf7d8bce70b18fe201cccd86cb367adb5845b2997987602'
TINY=F(1,2**149)
CANDIDATES=((TINY,(1023-149)<<52,1),(-TINY,((1023-149)<<52)|(1<<63),1|(1<<31)))

def counterexample_HOST(box,anchor_words,*,model):
    require(type(model) is str and model==MODEL,'explicit frozen-guard counterexample model')
    intervals=domain.box_values(box)
    require(type(anchor_words) is list and len(anchor_words)==2,'two typed ORIGINAL anchor words')
    anchor=[guard.bits(w,64) for w in anchor_words]
    require(all(lo<=q<=hi for q,(lo,hi) in zip(anchor,intervals)),'same ORIGINAL anchor inside entire box')
    out={'model':MODEL,'box_reim':deepcopy(box),'ORIGINAL_anchor_uint64':deepcopy(anchor_words),
        FLAG:False,'witness':None,'frozen_guard_admission_for_entire_box_proved':False,
        'native_cast_executed':False,'SOURCE_graph_executed':False,'device_model_authenticated':False,
        'signed_zero_execution_policy_proved':False,'uniform_executed_SOURCE_error_L1':None,
        'uniform_SOURCE_enclosure_proved':False,'phase_bound_rad':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    for component,(lo,hi) in enumerate(intervals):
        for q,w64,w32 in CANDIDATES:
            if not lo<=q<=hi:continue
            words=deepcopy(anchor_words);words[component]=w64
            source_values=[guard.bits(w,64) for w in words]
            require(all(a<=x<=b for x,(a,b) in zip(source_values,intervals)),'complete finite normal-or-zero binary64 witness inside box')
            # Exact representability proves RN32 result without invoking a cast or producer.
            require(guard.bits(w64,64)==guard.bits(w32,32,normal=False)==q,'exact RN32 high-word witness')
            try:guard.check_RN(q,w32,32,w64>>63)
            except ValueError as e:
                require(str(e)=='normal-or-zero selected word','specific frozen selected-subnormal rejection')
                reason=str(e)
            else:raise ValueError('frozen guard unexpectedly admitted selected subnormal witness')
            out.update({FLAG:True,'witness':{'component':component,'SOURCE_input_uint64':words,
                'SOURCE_input_reim':list(map(pair,source_values)),'value':pair(q),'input_uint64':w64,
                'derived_RN32_high_uint32':w32,'RN32_conversion_exact_proved':True,
                'HOST_frozen_guard_check_rejected':True,'rejection_reason':reason,
                'rejection_scope':'selected high word; no native cast or complete SOURCE graph executed'}})
            return out
    out['reason']='no +/-2^-149 witness found; absence is NOT whole-box admission proof'
    return out

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA))
    require(r['task_id']=='AXIAL-SOURCE-UNIFORM-HILO-DECODE-HOST-001','parent task identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    packets,stage,data,oldpins=prior.load_retained()
    require(all(pins.get(p)==h for p,h in oldpins.items()),'same immutable domain/encoder graph')
    return packets,data,io.payload(r)['data'],pins

def audit_guard_counterexamples_HOST(variant,*,model):
    require(type(model) is str and model==MODEL and type(variant) is str and variant in prior.VARIANTS,'explicit variant and negative-proof model')
    packets,data,parent,pins=load_retained()
    old=data['synthetic_scene_domains'] if variant=='synthetic_domains' else data['real_missing']
    previous=parent[variant]
    require(previous['case_order']==old['case_order'],'complete retained domain case order')
    plans=data['synthetic_domain_INPUT_plans'] if variant=='synthetic_domains' else {}
    checked={}
    # ALL domain/context/complete-source/retained-certificate bindings before any witness checker.
    for name in old['case_order']:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context']==previous['cases'][name]['context'],'same ORIGINAL context')
        d=domain.validate_domain(packets[name],ctx,plans.get(name))
        require(digest(d)==digest(old['cases'][name]['domain_INPUT']),'exact typed retained domain')
        pc=previous['cases'][name]
        require(type(pc['domain_INPUT_valid']) is bool and pc['domain_INPUT_valid'] is d['domain_INPUT_valid'],'typed retained domain validity')
        if d['domain_INPUT_valid']:
            require(type(pc['sources']) is list and len(pc['sources'])==len(d['sources']),'complete retained encoder sources')
            for s,p in zip(d['sources'],pc['sources']):
                require(p['source_id']==s['source_id'] and p['domain_source_sha256']==digest(s) and
                        p['ORIGINAL_source_uint64']==s['ORIGINAL_source_uint64'],'retained SOURCE domain binding')
                b=p['bound']
                require(b['model']==prior.MODEL and b['box_reim']==s['box_reim'] and b[prior.FLAG] is True and
                        b['frozen_guard_admission_for_entire_box_proved'] is False,'separate analytic bound; NOT guard admission')
        else:require(pc['sources'] is None,'missing domain has no certificate')
        checked[name]=(ctx,d,pc)
    cases={};count=0
    for name,(ctx,d,pc) in checked.items():
        rows=None
        if d['domain_INPUT_valid']:
            rows=[]
            for s,p in zip(d['sources'],pc['sources']):
                proof=counterexample_HOST(s['box_reim'],s['ORIGINAL_source_uint64'],model=model)
                count+=int(proof[FLAG])
                rows.append({'source_id':s['source_id'],'domain_source_sha256':digest(s),
                    'retained_encoder_decode_bound_sha256':digest(p['bound']),'proof':proof})
        cases[name]={'context':ctx,'sources':rows,'domain_INPUT_valid':d['domain_INPUT_valid'],
            'group_phase_bound_rad':None,'group_field_bound_L1':None,'uniform_executed_SOURCE_error_L1':None,
            'uniform_SOURCE_enclosure_proved':False,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'case_order':deepcopy(old['case_order']),'cases':cases,
        'inherited_pins_verified':len(pins),'exact_guard_counterexamples':count,'new_native_operations':0,
        'old_suites_producers_reexecuted':0,'group_admissions':0,'frozen_guard_changed':False,
        'uniform_SOURCE_enclosure_proved':False,'cost_scope':'HOST negative domain proof only; full costs UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
