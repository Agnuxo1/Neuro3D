"""Opt-in CPU ideal -1 reflection of pinned guarded prefixes, NOT scene inference."""
import base64,struct
from copy import deepcopy
from fractions import Fraction as F
import axial_guarded_scene_source_CPU_v1 as prior
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
MODEL='axial-retained-guarded-prefix-ideal-minus-one-reflection-CPU-v1'
FLAG='ideal_reflection_CPU_executed'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-SCENE-SOURCE-CPU-001-CODEX.json'
PREVIOUS_SHA='8f4ea4cc5d35cb3f56d800837ff553c438f4e635d7e482b2a197a45651e59da8'
SIGN=1<<63
FALSE=tuple(k for k in prior.FALSE if k not in ('reflection_coefficient_applied','reflection_coefficient_executed_new'))
source=prior.source_stage.source

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-GUARDED-SCENE-SOURCE-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['audit'];packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases']),'complete cases')
    return packets,old,pins

def profile(snapshot,metadata,source_id,result):
    require(set(snapshot['objects'])=={'M','D'} and snapshot['undeclared_meshes']==[],'declared M/D only')
    require(metadata['object_ids']==['M','D'] and metadata['kinds']==['mirror','det'],'ordered owner kinds')
    require(snapshot['objects']['M']['kind']=='mirror' and snapshot['objects']['D']['kind']=='det','same ORIGINAL owner kinds')
    phase=snapshot['objects']['M']['phase_rad']
    require(type(phase) is float,'binary64 ORIGINAL phase')
    w=source.word(phase);require(w in (0,SIGN),'exact ORIGINAL +/-0 only, no rounding/FTZ to zero')
    for key in ('fixed_ORIGINAL_trace','decoded_trace'):
        t=result[key];require(t['source_id']==source_id,'same source trace')
        hs=t['hits'];require(type(hs) is list and len(hs)==2,'two retained events')
        require(all(type(h['owner']) is int and type(h['primitive_id']) is int for h in hs),'typed event identities')
        require([h['owner'] for h in hs]==[0,1] and all(F(*h['segment_BU'])>0 for h in hs),'positive M then D')
    require([(h['owner'],h['primitive_id']) for h in result['fixed_ORIGINAL_trace']['hits']]==
            [(h['owner'],h['primitive_id']) for h in result['decoded_trace']['hits']],'unchanged primitive/owner chain')
    return {'mirror_phase_ORIGINAL_uint64':w,'ideal_coefficient_exact_reim':[[-1,1],[0,1]],
        'coefficient_model':'fixed ideal -exp(i*ORIGINAL phase), exact +/-0; NOT Fresnel or physical material',
        'material_input':'pinned ORIGINAL scene JSON; no native material ABI buffer implemented',
        'new_coefficient_error_L1':[0,1]}

def native_negate(word):
    # Actual unary minus of decoded IEEE value; not synthetic output XOR.
    return source.word(-source.value(word,64))

def runtime_probe():
    words=[0,SIGN,0x3ff0000000000000,0xbff0000000000000]
    out=[native_negate(w) for w in words]
    return {'input_uint64':words,'output_uint64':out,'PASS':out==[w^SIGN for w in words],
        'new_CPU_unary_negations':4,'zero_canonicalization_performed':False}

def admit(packet,ctx,index,row):
    fresh=allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL)
    require(ctx==fresh,'same complete INPUT context')
    require(type(index) is int and 0<=index<len(ctx['source_order']),'source index')
    sid=ctx['source_order'][index];assignment=ctx['assignments'][index]
    require(row['source_id']==sid and row[prior.FLAG] is True,'retained guarded prefix eligibility')
    require(row['phase_reference_id']==assignment['source_phase_reference_id'] and
            row['terminal_reference_id']==assignment['terminal_reference_id'],'same source/terminal gauges')
    snap,meta=prior.original.snapshot_from_packet(packet,ctx);res=row['result']
    p=profile(snap,meta,sid,res)
    raw=base64.b64decode(packet['buffers_base64']['sources'],validate=True)
    require(packet['manifest']['layout']['sources']['stride_words']==32 and
            raw[128*index+112:128*index+128]==struct.pack('<dd',*snap['sources'][index]['field_reim']),'same source ABI words')
    prod=res['bare_source_prefix'];words=prod['product_uint64']
    require(type(words) is list and len(words)==2,'complex prefix words')
    for w in words:prior.guard.bits(w,64)
    charges={k:allocation.rational(v) for k,v in res['detailed_source_charges_L1'].items()}
    require(set(charges)=={'source_encoding_L1','source_decode_RN64_L1','source_Horner_L1',
            'source_decoded_argument_L1','source_geometry_reference_wavelength_L1','source_product_RN64_L1'},'six separate charges')
    total=allocation.rational(res['point_bare_source_to_fixed_ORIGINAL_bound_L1'])
    require(sum(charges.values(),F(0))==total==allocation.rational(prod['point_bare_source_to_ORIGINAL_bound_L1']),'charge conservation')
    # Complete INPUT has group caps but NO per-source amplitude allocation.
    require('source_amplitude_allocation' not in meta,'allocation INPUT extension unsupported; never silently ignore')
    budget=allocation.audit_allocation_HOST(packet,digest(packet),None,model=allocation.MODEL)['result']
    require(budget['allocation_INPUT_valid'] is False,'missing allowance remains missing')
    return {'context_sha256':digest(ctx),'retained_prefix_row_sha256':digest(row),'profile':p,
        'input_uint64':deepcopy(words),'charges_L1':deepcopy(res['detailed_source_charges_L1']),
        'point_reflected_source_to_fixed_ORIGINAL_bound_L1':pair(total),'allocation_gate':budget,
        'source_phase_reference_id':assignment['source_phase_reference_id'],
        'terminal_reference_id':assignment['terminal_reference_id']}

def execute(admission):
    words=admission['input_uint64'];nodes=[];out=[]
    for w in words:
        v=native_negate(w);require(v==w^SIGN,'CPU unary negation bit identity')
        out.append(v);nodes.append({'operation':'unary_minus_binary64','input_uint64':w,'output_uint64':v})
    return {**deepcopy(admission),'reflected_uint64':out,'nodes':nodes,
        'additional_reflection_rounding_error_L1':[0,1],'new_CPU_unary_negations':2,
        'error_rule':'L1(-prefix,-fixed ORIGINAL ideal field)=L1(prefix,fixed ORIGINAL ideal field); six nonzero charges preserved',
        FLAG:True,'reflection_coefficient_applied':True,'reflection_coefficient_executed_new':True,
        'zero_canonicalization_performed':False,**dict.fromkeys(FALSE,False)}

def audit_reflection_CPU(case_names,*,model):
    require(model==MODEL,'explicit retained-prefix ideal reflection CPU model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    # Admit every requested source before ANY stage/probe operation: no partial field/output.
    plans={};eligible=stopped=0
    for n in case_names:
        c=old['cases'][n];require([r['source_id'] for r in c['sources']]==c['context']['source_order'],'complete source order')
        plans[n]=[]
        for i,r in enumerate(c['sources']):
            if r[prior.FLAG]:plans[n].append(admit(packets[n],c['context'],i,r));eligible+=1
            else:plans[n].append(None);stopped+=1
    probe=runtime_probe();require(probe['PASS'] is True,'runtime FAIL before material outputs')
    cases={}
    for n in case_names:
        rows=[]
        for r,a in zip(old['cases'][n]['sources'],plans[n]):
            row={'source_id':r['source_id'],'status':'STOP',FLAG:False,
                'reflection_coefficient_applied':False,'reflection_coefficient_executed_new':False,**dict.fromkeys(FALSE,False)}
            if a is None:row.update(reason=r['reason'],reason_provenance='unchanged_retained_STOP')
            else:row.update(result=execute(a),**{FLAG:True,'reflection_coefficient_applied':True,'reflection_coefficient_executed_new':True},
                reason='CPU ideal -1 reflection executed on pinned retained prefix; missing explicit source L1 allocation, reduction/power/readout not executed')
            rows.append(row)
        cases[n]={'context':deepcopy(old['cases'][n]['context']),'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'runtime_probe':probe,
        'inherited_pins_verified':len(pins),'new_ideal_reflected_sources':eligible,'retained_sources_not_executed':stopped,
        'new_main_CPU_unary_negations':2*eligible,'new_probe_CPU_unary_negations':4,
        'new_geometry_argument_Horner_source_encoder_product_executions':0,'old_numeric_audits_suites_reexecuted':0,
        'new_reduction_power_readout_executions':0,'fresh_scene_inference_executed':False,
        'previous_SOURCE_eight_bit_FAILs_preserved':True,'previous_SOURCE_twelve_zero_sign_mismatches_preserved':True,
        'scope':'NEW CPU ideal reflection stage of RETAINED pinned prefix; NOT fresh scene inference, uniform/native-ray/physical/full field',
        'cost_scope':'main unary negations and probe counted separately; retained upstream cost NOT zero or measured here; IO/pins/setup/rational and remaining costs UNMEASURED',**dict.fromkeys(FALSE,False)}
