"""Opt-in analytical bare SOURCE bound over pinned nonzero axial domains; HOST only."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import math
import struct
import axial_nonzero_unit_domain_HOST_v1 as unit
import axial_zero_source_domain_HOST_v1 as source
io=unit.io
allocation=unit.allocation
require=io.require
digest=allocation.digest
MODEL='axial-nonzero-fixed-source-uniform-product-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-NONZERO-UNIT-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='c48285861cbfffbc191e4c52796c60b7879e0cced34e15272b2c264aa75572b2'
FLAG='restricted_nonzero_bare_source_error_to_fixed_ORIGINAL_bound_proved'
FALSE=unit.FALSE
HYPOTHESIS='binary64 nearest-even gradual underflow; fixed retained coefficients, Horner26, no FMA'

def decimal(v):
    return [str(v.numerator),str(v.denominator)]

def rational(v):
    require(type(v) is list and len(v)==2 and all(type(x) is str for x in v),'exact decimal rational strings')
    require(all(x==str(int(x)) for x in v),'canonical decimal integer strings')
    n,d=map(int,v);require(d>0 and math.gcd(n,d)==1,'reduced rational, positive denominator')
    return F(n,d)

def load_retained():
    receipt=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(receipt['task_id']=='AXIAL-NONZERO-UNIT-DOMAIN-HOST-001','nonzero predecessor identity')
    pins=io.pins_from(receipt);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    previous=io.payload(receipt)['data']['audit']
    products=io.payload(allocation.parse(io.read(io.PRODUCT,pins[io.PRODUCT])))['cases']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    require(set(packets)==set(previous['cases'])==set(products),'complete retained case coverage')
    return packets,previous,products,pins

def encoder_identity(productrow,words):
    """Fixed source/decode identities only, not an encoder or point RN execution."""
    corners=productrow['encoded_corner_products'];require(len(corners)==4,'four retained product graph witnesses')
    enc=corners[0]['source_encoder']
    require(all(c['source_encoder']==enc for c in corners),'one fixed encoder across domain witnesses')
    require(enc['original_source_uint64']==words,'fixed ORIGINAL source words')
    original=list(map(source.decode64,words));limbs=enc['source_limb_uint32']
    require(type(limbs) is list and len(limbs)==4,'four SOURCE hi-lo32 words')
    values=list(map(source.decode32,limbs));sums=[values[0]+values[1],values[2]+values[3]]
    raw=struct.pack('<IIII',*limbs)
    require(base64.b64decode(enc['source_hilo_le_base64'],validate=True)==raw
            and hashlib.sha256(raw).hexdigest()==enc['source_hilo_le_sha256'],'source transport bytes/SHA')
    require(enc['source_exact_limb_sum_rational']==list(map(unit.pair,sums)),'exact hi-lo sums')
    err=sum((abs(o-v) for o,v in zip(original,sums)),F(0));norm=sum(map(abs,original),F(0))
    require(unit.number(enc['source_encoding_error_L1'])==err and unit.number(enc['source_norm_L1'])==norm,'nonzero encoding ledger')
    require(len(enc['HOST_trace'])==2,'two component encoder traces')
    for i,t in enumerate(enc['HOST_trace']):
        require(t['original']==unit.pair(original[i]) and t['high']==unit.pair(values[2*i])
            and t['high_uint32']==limbs[2*i] and t['low_uint32']==limbs[2*i+1]
            and t['HOST_exact_residual']==unit.pair(original[i]-values[2*i])
            and t['represented']==unit.pair(sums[i])
            and t['encoding_error']==unit.pair(abs(original[i]-sums[i])),'exact encoder trace identity')
    labels=['decode0','decode1','ac','bd','ad','bc','real','imag']
    for corner in corners:
        require(corner['model']=='axial-source-hilo32-decode-RN64-product-HOST-v1','fixed noFMA product graph model')
        ops=corner['operations'];require(len(ops)==8 and [v['label'] for v in ops]==labels,'complete decode2/product6 graph')
        require([v['op'] for v in ops]==['add','add','mul','mul','mul','mul','add','add'],'fixed graph operations')
        for i,op in enumerate(ops[:2]):
            require(op['inputs']==[unit.pair(values[2*i]),unit.pair(values[2*i+1])]
                and source.decode64(op['output_uint64'])==sums[i] and unit.number(op['delta'])==0,'exact SOURCE decode identity')
        require(corner['source_decoded_RN64']==list(map(unit.pair,sums)),'fixed decoded source')
    return original,sums,err,enc

def product_majorants(a,b,M):
    """New uniform rational majorants for four multiply/two add nodes; no RN replay."""
    require(1<=M<2,'small represented unit component bound')
    def E(v):
        require(0<=v<=unit.MAX/2,'overflow-safe uniform operation magnitude')
        return v/F(2**53)+F(1,2**1075) if v else F(0)
    magnitudes=[abs(a)*M,abs(b)*M,abs(a)*M,abs(b)*M]
    errors=list(map(E,magnitudes))
    nodes=[{'label':label,'exact_abs_upper_decimal':decimal(m),'RN_error_abs_decimal':decimal(e)}
           for label,m,e in zip(['ac','bd','ad','bc'],magnitudes,errors)]
    for label,i,j in [('real',0,1),('imag',2,3)]:
        m=magnitudes[i]+magnitudes[j]+errors[i]+errors[j];e=E(m)
        nodes.append({'label':label,'exact_abs_upper_decimal':decimal(m),'RN_error_abs_decimal':decimal(e)})
    return sum((rational(n['RN_error_abs_decimal']) for n in nodes),F(0)),nodes

def prove_source(packet,ctx,index,unitrow,productrow):
    require(ctx==allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL),'fresh complete INPUT context')
    sid=ctx['source_order'][index];assignment=ctx['assignments'][index]
    require(unitrow['source_id']==productrow['source_id']==sid,'complete ordered SOURCE identity')
    require(unitrow[unit.FLAG] is True,'pinned restricted nonzero unit proof required')
    p=unitrow['proof']
    require(p[unit.FLAG] is True and p['model']==unit.MODEL and p['source_id']==sid,'conditional unit proof identity')
    require(all(p[k] is False for k in FALSE),'no upstream promotion')
    require(p['ORIGINAL_assignment_sha256']==digest(assignment),'same fixed ORIGINAL gauges')
    require(p['arithmetic_hypothesis']==HYPOTHESIS and p['restricted_Horner26_nodes_normal_proved'] is True,'retained HOST graph hypothesis')
    B=rational(p['polynomial_unit_L1_bound_decimal']);delta=unit.number(p['composed_parameter_argument_phase_bound_rad'])
    U=rational(p['uniform_unit_L1_to_fixed_ORIGINAL_bound_decimal'])
    require(0<B<F(1,2) and delta>=0 and U==B+2*delta and 0<U<1,'retained ORIGINAL unit composition')
    require(delta==unit.number(p['parameter_phase_bound_rad'])+unit.number(p['argument_phase_bound_rad']),'separate phase charges')
    meta=allocation.parse(base64.b64decode(packet['buffers_base64']['input_metadata_json'],validate=True))
    cap=meta['original_path_phase_caps'][sid]
    require(cap==p['unchanged_original_phase_cap_rad']==[1,10**12]
        and rational(p['uniform_phase_to_fixed_ORIGINAL_bound_decimal'])==B/(1-B)+delta
        and B/(1-B)+delta<=unit.number(cap),'unchanged phase cap, not amplitude allocation')
    require(productrow['phase_reference_id']==assignment['source_phase_reference_id']
        and productrow['terminal_reference_id']==assignment['terminal_reference_id'],'source/terminal reference identity')
    words=source.fixed_source_words(packet,ctx,index)
    require(productrow['source_product_evaluated'] is True and productrow['original_source_uint64']==words,'retained source word/graph witness')
    original,decoded,err,enc=encoder_identity(productrow,words)
    M=1+U;L=2+U;RN,nodes=product_majorants(*decoded,M)
    # Complex L1 is submultiplicative. |u_ideal|_L1<=2; each component<=1.
    # Decode is exactly representable for the retained fixed limbs. Add-node charges
    # include incoming multiply errors; no cancellation/signed-zero optimization assumed.
    charges={'source_encoding':decimal(err*L),'source_decode_RN64':decimal(F(0)),
             'unit_to_fixed_ORIGINAL':decimal(sum(map(abs,original),F(0))*U),'product_RN64':decimal(RN)}
    total=sum(map(rational,charges.values()),F(0))
    return {'model':MODEL,FLAG:True,'source_id':sid,'retained_unit_row_sha256':digest(unitrow),
        'retained_product_row_sha256':digest(productrow),'retained_encoder_sha256':digest(enc),
        'original_input_packet_sha256':digest(packet),'ORIGINAL_assignment_sha256':digest(assignment),
        'fixed_original_source_uint64':words,'fixed_original_source_rational':list(map(unit.pair,original)),
        'source_hilo_uint32':deepcopy(enc['source_limb_uint32']),'decoded_source_rational':list(map(unit.pair,decoded)),
        'nonzero_encoding_error_L1':unit.pair(err),'unit_L1_error_to_fixed_ORIGINAL_decimal':decimal(U),
        'represented_unit_component_abs_upper_decimal':decimal(M),'represented_unit_norm_L1_upper_decimal':decimal(L),
        'product_RN_nodes':nodes,'charges_L1_decimal':charges,
        'uniform_bare_source_L1_error_to_fixed_ORIGINAL_bound_decimal':decimal(total),
        'unchanged_original_phase_cap_rad':deepcopy(cap),
        'unchanged_global_field_L1_cap_NOT_source_allocation':deepcopy(ctx['unchanged_field_L1_cap']),
        'units':'ORIGINAL-source-field-amplitude-L1','arithmetic_hypothesis':HYPOTHESIS+'; decode2/product6 RN64, no FMA',
        'material_reflection_charge_included':False,'new_RN_or_old_producer_executions':0,
        'status':'STOP','reason':'conditional restricted bare SOURCE bound only; material/reduction/INPUT allocations/executed backend remain absent',
        **dict.fromkeys(FALSE,False)}

def audit_nonzero_source_domain_HOST(case_names,*,model):
    require(model==MODEL,'explicit restricted nonzero SOURCE HOST model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
        and len(set(case_names))==len(case_names),'bounded unique case names')
    packets,prior,products,pins=load_retained();require(set(case_names)<=set(packets),'known retained cases')
    cases={};proved=stops=zeros=0
    for n in case_names:
        ctx=allocation.context_from_packet(packets[n],digest(packets[n]),model=allocation.MODEL)
        require(ctx==prior['cases'][n]['context'],'fresh retained complete INPUT')
        pp=products[n]
        for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
            require(pp[k]==ctx[k],'product INPUT binding: '+k)
        us=prior['cases'][n]['sources'];ps=pp['sources']
        require([s['source_id'] for s in us]==[s['source_id'] for s in ps]==ctx['source_order'],'ordered complete sources')
        rows=[]
        for i,(u,p) in enumerate(zip(us,ps)):
            row={'source_id':u['source_id'],'retained_unit_row_sha256':digest(u),'status':'STOP',FLAG:False,**dict.fromkeys(FALSE,False)}
            if u[unit.FLAG] is not True:
                reason=u['reason_provenance'];stops+=int(reason=='unchanged_retained_unit_STOP');zeros+=int(reason=='outside_nonzero_scope')
                require(reason in ('unchanged_retained_unit_STOP','outside_nonzero_scope'),'retained STOP provenance')
                row.update(reason=u['reason'],reason_provenance=reason)
            else:
                proof=prove_source(packets[n],ctx,i,u,p);proved+=1
                row.update(proof=proof,reason=proof['reason'],**{FLAG:True})
            rows.append(row)
        cases[n]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
        'restricted_nonzero_bare_source_bounds_proved':proved,'retained_unit_STOPs':stops,'zero_domains_outside_scope':zeros,
        'new_RN_or_old_producer_executions':0,**dict.fromkeys(FALSE,False)}
