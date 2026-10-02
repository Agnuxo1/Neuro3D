"""Fixed ORIGINAL complex source over a pinned restricted zero-unit domain; HOST only."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import struct
import axial_zero_singleton_unit_HOST_v1 as zero
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation

MODEL='axial-fixed-source-zero-unit-restricted-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-ZERO-SINGLETON-UNIT-HOST-001-CODEX.json'
PREVIOUS_SHA='a711ecbe215a05084c40318a84386a7b124875abc771542132029e7f5e7263cb'
PRODUCT=io.PRODUCT
FALSE=zero.FALSE+('amplitude_budget_accepted','reflection_coefficient_applied','field_values_computed',
                 'field_sum_computed','detector_evaluated','source_amplitude_uncertainty_enclosed')
require=io.require
pair=zero.pair
number=zero.number
decode64=zero.decode
digest=allocation.digest

def decode32(word):
    require(type(word) is int and 0<=word<2**32,'strict uint32')
    e=(word>>23)&255;m=word%2**23
    require(e<255 and (e!=0 or m==0),'finite normal-or-zero source limb; no FTZ')
    return (-1 if word>>31 else 1)*F((2**23+m) if e else 0)*F(2)**(e-150)

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-ZERO-SINGLETON-UNIT-HOST-001','zero-unit predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    old=io.payload(r)['data']['audit']
    products=io.payload(allocation.parse(io.read(PRODUCT,pins[PRODUCT])))['cases']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    require(set(packets)==set(old['cases'])==set(products),'complete inherited cases')
    return packets,old,products,pins

def fixed_source_words(packet,context,index):
    require(type(index) is int and 0<=index<len(context['source_order']),'valid ordered source index')
    fresh=allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL)
    require(context==fresh,'fresh INPUT context and caps; no caller context')
    raw=base64.b64decode(packet['buffers_base64']['sources'],validate=True)
    require(packet['manifest']['layout']['sources']['stride_words']==32 and len(raw)==128*len(context['source_order']),
            'fixed source INPUT stride')
    snapshot=allocation.parse(base64.b64decode(packet['buffers_base64']['original_scene_json'],validate=True))
    s=snapshot['sources'][index];sid=context['source_order'][index]
    require(s['id']==sid,'ordered ORIGINAL source identity')
    field=s['field_reim']
    require(type(field) is list and len(field)==2 and all(type(v) in (int,float) for v in field),'fixed complex ORIGINAL field')
    bits=raw[128*index+112:128*index+128]
    require(bits==struct.pack('<dd',*field),'ORIGINAL fixed complex field word identity')
    words=list(struct.unpack('<QQ',bits));list(map(decode64,words))
    return words

def verify_product_identity(product,original_words,unit_words):
    require(type(original_words) is list and len(original_words)==2,'two ORIGINAL words')
    original=list(map(decode64,original_words))
    require(unit_words==[zero.ONE,0],'restricted quarter-zero exact unit only')
    list(map(decode64,unit_words));list(map(decode64,product['unit_uint64']))
    require(product['unit_uint64']==unit_words,'retained unit words match zero proof')
    require(number(product['unit_error_L1_to_ORIGINAL_bound'])==0,'retained point unit error zero')
    enc=product['source_encoder']
    list(map(decode64,enc['original_source_uint64']))
    require(enc['original_source_uint64']==original_words,'encoder ORIGINAL word identity')
    limbs=enc['source_limb_uint32']
    require(type(limbs) is list and len(limbs)==4,'four retained hi-lo source words')
    values=list(map(decode32,limbs));represented=[values[0]+values[1],values[2]+values[3]]
    raw=struct.pack('<IIII',*limbs)
    require(base64.b64decode(enc['source_hilo_le_base64'],validate=True)==raw
            and enc['source_hilo_le_sha256']==hashlib.sha256(raw).hexdigest(),'encoder bytes and SHA')
    require(enc['source_exact_limb_sum_rational']==list(map(pair,represented)),'exact retained limb sums')
    require(len(enc['HOST_trace'])==2,'complete retained encoder trace')
    errors=[abs(o-v) for o,v in zip(original,represented)]
    for i,t in enumerate(enc['HOST_trace']):
        require(t['original']==pair(original[i]) and t['high']==pair(values[2*i])
                and t['high_uint32']==limbs[2*i] and t['low_uint32']==limbs[2*i+1],'encoder input/limb trace')
        require(t['HOST_exact_residual']==pair(original[i]-values[2*i])
                and t['represented']==pair(represented[i]) and t['encoding_error']==pair(errors[i]),'encoding error retained, not zeroed')
    eenc=sum(errors,F(0));require(number(enc['source_encoding_error_L1'])==eenc,'encoding error identity')
    require(number(enc['source_norm_L1'])==sum(map(abs,original),F(0)),'ORIGINAL source norm')
    ops=product['operations'];require(type(ops) is list and len(ops)==8,'decode2+complex product6 identities')
    a,b=represented
    expected=[('decode0','add',values[0],values[1]),('decode1','add',values[2],values[3]),
              ('ac','mul',a,F(1)),('bd','mul',b,F(0)),('ad','mul',a,F(0)),
              ('bc','mul',b,F(1)),('real','add',a,F(0)),('imag','add',F(0),b)]
    out=[]
    for op,(label,kind,x,y) in zip(ops,expected):
        require(op['label']==label and op['op']==kind
                and allocation.canon(op['inputs'])==allocation.canon([pair(x),pair(y)]),'exact graph label/operands')
        v=decode64(op['output_uint64']);exact=x*y if kind=='mul' else x+y
        require(v==exact and number(op['delta'])==0,'exact representability identity; no RN replay')
        require(v!=0 or op['output_uint64']==0,'retained canonical HOST +0')
        out.append(v)
    require(product['source_decoded_RN64']==list(map(pair,represented)),'retained decode result')
    list(map(decode64,product['product_uint64']))
    require(product['product_uint64']==[ops[6]['output_uint64'],ops[7]['output_uint64']]
            and product['product_rational']==list(map(pair,out[-2:])),'final product identity')
    require(product['exact_decoded_product']==list(map(pair,represented))
            and product['exact_original_times_represented_unit']==list(map(pair,original)),'complex reference ORIGINAL, not encoded nominal')
    observed=sum((abs(x-y) for x,y in zip(out[-2:],original)),F(0))
    require(observed==eenc and number(product['observed_error_to_original_times_represented_unit_L1'])==observed,
            'nonzero ORIGINAL source error retained')
    charges={'source_encoding':pair(eenc),'source_decode_RN64':[0,1],'unit_to_ORIGINAL':[0,1],'product_RN64':[0,1]}
    require(allocation.canon(product['charges_L1'])==allocation.canon(charges)
            and number(product['error_L1_to_original_source_times_ideal_unit_bound'])==eenc,'separate charges and unchanged total')
    return {'retained_product_sha256':digest(product),'retained_encoder_sha256':digest(enc),
            'retained_node_identities_checked':8,'fixed_original_source_uint64':deepcopy(original_words),
            'fixed_original_source_rational':list(map(pair,original)),'retained_hilo_source_uint32':deepcopy(limbs),
            'represented_source_rational':list(map(pair,represented)),'retained_product_uint64':deepcopy(product['product_uint64']),
            'bare_product_error_to_ORIGINAL_L1':pair(eenc),'charges_L1':charges,'new_RN_or_encoder_operations':0,
            'native_signed_zero_graph_equivalence_proved':False}

def fixed_source_domain_proof(packet,ctx,index,unitrow,productrow):
    require(unitrow['restricted_exact_unit_error_to_ORIGINAL_proved'] is True,'restricted zero-unit proof required')
    p=unitrow['proof']
    require(p['restricted_exact_unit_error_to_ORIGINAL_proved'] is True and number(p['unit_L1_error_to_ORIGINAL_bound'])==0
            and p['quarter_turn']==0 and type(p['quarter_turn']) is int,'zero-unit domain with quarter zero')
    words=fixed_source_words(packet,ctx,index)
    sid=ctx['source_order'][index];assignment=ctx['assignments'][index]
    require(unitrow['source_id']==productrow['source_id']==sid,'ordered source identity')
    require(productrow['phase_reference_id']==assignment['source_phase_reference_id']
            and productrow['terminal_reference_id']==assignment['terminal_reference_id'],'ORIGINAL phase and terminal gauge')
    require(productrow['original_source_uint64']==words and productrow['source_product_evaluated'] is True,
            'retained product SOURCE words/status')
    corners=productrow['encoded_corner_products'];require(len(corners)==4 and len(p['graph_checks'])==5,'complete retained corner coverage')
    checked=[]
    for old,g in zip(corners,p['graph_checks'][1:]):
        checked.append(verify_product_identity(old,words,g['exact_unit_uint64']))
    require(all(digest(c)==digest(corners[0]) for c in corners),'same constant source/unit graph at all corners')
    error=number(checked[0]['bare_product_error_to_ORIGINAL_L1'])
    require(number(productrow['product_error_L1_to_ORIGINAL_bound'])==error,'retained bound unchanged')
    return {'model':MODEL,'restricted_fixed_source_bare_product_error_to_ORIGINAL_proved':True,
            'scope':'pinned axial coordinate domain, fixed ORIGINAL complex SOURCE bits, canonical HOST zero unit; bare product only',
            'domain_argument':'zero unit is constant on entire inherited restricted domain; SOURCE bits and encoder graph fixed; not corner interpolation',
            'retained_zero_unit_row_sha256':digest(unitrow),'retained_source_product_row_sha256':digest(productrow),
            'original_input_packet_sha256':digest(packet),'source_phase_reference_id':assignment['source_phase_reference_id'],
            'terminal_reference_id':assignment['terminal_reference_id'],'graph_checks':checked,
            'uniform_bare_product_L1_error_to_fixed_ORIGINAL_bound':pair(error),'nonzero_encoding_error_preserved':error>0,
            'unchanged_original_phase_cap_rad':deepcopy(p['unchanged_original_phase_cap_rad']),
            'unchanged_global_field_L1_cap_NOT_a_source_allocation':deepcopy(ctx['unchanged_field_L1_cap']),
            'phase_cap_NOT_compared_to_amplitude':True,'new_RN_or_old_producers_reexecuted':0,
            **dict.fromkeys(FALSE,False)}

def audit_zero_source_domain_HOST(case_names,*,model):
    require(model==MODEL,'explicit restricted fixed-source HOST model')
    require(type(case_names) is list and 1<=len(case_names)<=64
            and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique case selection')
    packets,old,products,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    cases={};count=stops=nonzero=0
    for n in case_names:
        packet=packets[n];ctx=allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL)
        require(ctx==old['cases'][n]['context'],'fresh complete context')
        previous=products[n]
        for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
            require(previous[k]==ctx[k],'retained product INPUT binding: '+k)
        us=old['cases'][n]['sources'];ps=previous['sources']
        require([s['source_id'] for s in us]==[s['source_id'] for s in ps]==ctx['source_order'],'complete ordered sources')
        rows=[]
        for i,(u,p) in enumerate(zip(us,ps)):
            row={'source_id':u['source_id'],'retained_zero_unit_row_sha256':digest(u),
                 'retained_unit_polynomial_charge_fits':u['retained_unit_polynomial_charge_fits'],
                 'restricted_fixed_source_bare_product_error_to_ORIGINAL_proved':False,**dict.fromkeys(FALSE,False)}
            if not u['restricted_exact_unit_error_to_ORIGINAL_proved']:
                if u['reason_provenance']=='unchanged_retained_unit_STOP':stops+=1
                else:nonzero+=1
                row.update(status='STOP',reason=u['reason'],reason_provenance=u['reason_provenance'])
            else:
                proof=fixed_source_domain_proof(packet,ctx,i,u,p);count+=1
                row.update(restricted_fixed_source_bare_product_error_to_ORIGINAL_proved=True,proof=proof,status='STOP',
                           reason='restricted fixed-source bare product bounded; reflection/reduction/allocation/full pipeline remain unproved',
                           reason_provenance='restricted_bare_source_only_not_full_pipeline')
            rows.append(row)
        cases[n]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
            'restricted_fixed_source_domains_proved':count,'retained_unit_STOPs':stops,'nonzero_domains_not_refined':nonzero,
            'new_RN_or_old_producers_reexecuted':0,**dict.fromkeys(FALSE,False)}
