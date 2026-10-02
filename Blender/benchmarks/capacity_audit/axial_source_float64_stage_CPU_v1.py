"""Opt-in actual CPU float64 SOURCE-stage fixture execution, NOT scene inference."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import math
import platform
import struct
import sys
import axial_nonzero_source_domain_HOST_v1 as prev
io=prev.io
allocation=prev.allocation
require=io.require
digest=allocation.digest
MODEL='axial-pinned-SOURCE-stage-CPU-float64-noFMA-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-NONZERO-SOURCE-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='d0157a47b48bf999a80aecefecef10600a1193a5374845c61088ec2382dfe9ad'
FALSE=prev.FALSE
FLAG='CPU_float64_SOURCE_stage_fixture_executed'
LABELS=['decode0','decode1','ac','bd','ad','bc','real','imag']

def word(v):return struct.unpack('<Q',struct.pack('<d',v))[0]

def value(w,width):
    require(type(w) is int and width in (32,64) and 0<=w<2**width,'strict float word')
    mb,eb=(23,8) if width==32 else (52,11)
    exponent=(w>>mb)%2**eb;mantissa=w%2**mb
    require(exponent<2**eb-1 and (exponent!=0 or mantissa==0),'fixture finite normal-or-zero; no FTZ/clamp')
    return struct.unpack('<f' if width==32 else '<d',struct.pack('<I' if width==32 else '<Q',w))[0]

def runtime_probe():
    """Six observed arithmetic probes, not universal environment authentication."""
    require(sys.float_info.radix==2 and sys.float_info.mant_dig==53 and sys.float_info.max_exp==1024,'binary64 runtime description')
    one=1.0;half=math.ldexp(1.0,-53);odd=value(0x3ff0000000000001,64)
    tiny=struct.unpack('<d',struct.pack('<Q',1))[0]
    zero=0.0;negative_one=-1.0;negative_zero=value(1<<63,64)
    results=[('tie_even_one',one+half,0x3ff0000000000000),
             ('tie_even_odd',odd+half,0x3ff0000000000002),
             ('gradual_product',math.ldexp(1.0,-1022)*0.5,1<<51),
             ('gradual_add',tiny+tiny,2),('negative_zero_product',zero*negative_one,1<<63),
             ('opposite_zeros_add',negative_zero+zero,0)]
    checks=[{'label':label,'actual_uint64':word(v),'expected_uint64':expected,'PASS':word(v)==expected}
            for label,v,expected in results]
    return {'checks':checks,'PASS':all(v['PASS'] for v in checks),'new_CPU_float64_probe_operations':6,
        'python':sys.version,'machine':platform.machine(),'platform':platform.system(),
        'scope':'observed local probes only; not GPU, execution/coherence authentication or whole-domain theorem'}

def execute_graph(limbs,unitwords,reference_ops):
    """Partial fixture primitive; operands are explicit and NOT caller scene evidence.

    Each multiplication/addition is a separate Python binary64 operation. No FMA,
    zero canonicalization or reference-output substitution is performed.
    """
    require(type(limbs) is list and len(limbs)==4 and type(unitwords) is list and len(unitwords)==2,'SOURCE4/unit2 fixture words')
    vals=[value(w,32) for w in limbs];c,d=[value(w,64) for w in unitwords]
    require(type(reference_ops) is list and len(reference_ops)==8 and [v['label'] for v in reference_ops]==LABELS,'reference graph labels')
    require([v['op'] for v in reference_ops]==['add','add','mul','mul','mul','mul','add','add'],'reference graph operations')
    nodes=[]
    def op(x,y,kind,label):
        expected=reference_ops[len(nodes)]
        require(expected['inputs']==[prev.unit.pair(F.from_float(x)),prev.unit.pair(F.from_float(y))],'same exact numerical operands: '+label)
        z=x*y if kind=='mul' else x+y
        require(math.isfinite(z),'nonfinite CPU result; fail closed')
        actual=word(z);ref=expected['output_uint64']
        require(type(ref) is int and 0<=ref<2**64,'strict reference uint64')
        delta=F.from_float(z)-(F.from_float(x)*F.from_float(y) if kind=='mul' else F.from_float(x)+F.from_float(y))
        nodes.append({'label':label,'op':kind,'input_uint64':[word(x),word(y)],
            'output_uint64':actual,'reference_output_uint64':ref,'word_match':actual==ref,
            'zero_sign_only_mismatch':actual!=ref and actual%2**63==ref%2**63==0,
            'observed_delta_rational':prev.unit.pair(delta)})
        return z
    a=op(vals[0],vals[1],'add','decode0');b=op(vals[2],vals[3],'add','decode1')
    ac=op(a,c,'mul','ac');bd=op(b,d,'mul','bd')
    ad=op(a,d,'mul','ad');bc=op(b,c,'mul','bc')
    real=op(ac,-bd,'add','real');imag=op(ad,bc,'add','imag')
    mismatches=[n['label'] for n in nodes if not n['word_match']]
    return {'nodes':nodes,'product_uint64':[word(real),word(imag)],'node_word_mismatches':mismatches,
        'exact_retained_node_bits_match':not mismatches,'new_CPU_float64_RN_nodes_executed':8,
        'status':'POINT_BITS_MATCH' if not mismatches else 'FAIL_RETAINED_NODE_BITS',
        'zero_canonicalization_performed':False,'old_numeric_producers_reexecuted':0}

def load_retained():
    receipt=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(receipt['task_id']=='AXIAL-NONZERO-SOURCE-DOMAIN-HOST-001','SOURCE domain predecessor identity')
    pins=io.pins_from(receipt);pins[PREVIOUS]=PREVIOUS_SHA
    for path,h in pins.items():io.read(path,h)
    previous=io.payload(receipt)['data']['audit']
    products=io.payload(allocation.parse(io.read(io.PRODUCT,pins[io.PRODUCT])))['cases']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    require(set(packets)==set(products)==set(previous['cases']),'complete prior cases')
    return packets,previous,products,pins

def bind_fixture(packet,ctx,index,certificate,productrow):
    require(ctx==allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL),'fresh complete INPUT context')
    require(type(index) is int and 0<=index<len(ctx['source_order']),'valid ordered source index')
    sid=ctx['source_order'][index];assign=ctx['assignments'][index]
    require(certificate[prev.FLAG] is True and certificate['source_id']==productrow['source_id']==sid,'restricted SOURCE certificate')
    p=certificate['proof']
    require(p[prev.FLAG] is True and p['model']==prev.MODEL and all(p[k] is False for k in FALSE),'no inherited promotion')
    require(p['original_input_packet_sha256']==digest(packet) and p['ORIGINAL_assignment_sha256']==digest(assign),'INPUT/gauge binding')
    require(p['retained_product_row_sha256']==digest(productrow),'same exact retained product witnesses')
    words=prev.source.fixed_source_words(packet,ctx,index)
    require(words==p['fixed_original_source_uint64']==productrow['original_source_uint64'],'same ORIGINAL SOURCE bits')
    require(productrow['phase_reference_id']==assign['source_phase_reference_id'] and productrow['terminal_reference_id']==assign['terminal_reference_id'],'source/terminal gauge')
    corners=productrow['encoded_corner_products'];require(len(corners)==4,'four retained point witnesses; not interpolation')
    for corner in corners:
        enc=corner['source_encoder'];blob=base64.b64decode(enc['source_hilo_le_base64'],validate=True)
        require(enc['original_source_uint64']==words and len(blob)==16
            and list(struct.unpack('<4I',blob))==enc['source_limb_uint32']==p['source_hilo_uint32'],'pinned encoded SOURCE capsule')
        require(digest(enc)==p['retained_encoder_sha256'],'same retained encoder, no reencoding')
        # Only a binding validation. No new unit/scene/Horner/encoder operations.
        list(map(lambda w:value(w,32),enc['source_limb_uint32']))
        list(map(lambda w:value(w,64),corner['unit_uint64']))
    return corners

def audit_source_float64_stage_CPU(case_names,*,model):
    require(model==MODEL,'explicit CPU float64 SOURCE stage, not scene inference')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
        and len(set(case_names))==len(case_names),'bounded unique case names')
    packets,previous,products,pins=load_retained();require(set(case_names)<=set(packets),'known retained cases')
    probe=runtime_probe();require(probe['PASS'] is True,'local CPU rounding/subnormal/zero probe failed; no stage execution')
    cases={};executed=nodes=matched=failed=stops=0
    for n in case_names:
        ctx=allocation.context_from_packet(packets[n],digest(packets[n]),model=allocation.MODEL)
        require(ctx==previous['cases'][n]['context'],'complete fresh retained INPUT')
        pp=products[n]
        for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):require(pp[k]==ctx[k],'product INPUT '+k)
        cs=previous['cases'][n]['sources'];ps=pp['sources']
        require([s['source_id'] for s in cs]==[s['source_id'] for s in ps]==ctx['source_order'],'complete source coverage/order')
        rows=[]
        for i,(certificate,pr) in enumerate(zip(cs,ps)):
            row={'source_id':certificate['source_id'],'retained_source_certificate_sha256':digest(certificate),
                FLAG:False,'status':'STOP','bare_source_values_computed_new':False,**dict.fromkeys(FALSE,False)}
            if not certificate[prev.FLAG]:
                stops+=1;row.update(reason=certificate['reason'],reason_provenance=certificate['reason_provenance'])
            else:
                corners=bind_fixture(packets[n],ctx,i,certificate,pr);points=[]
                for j,corner in enumerate(corners):
                    v=execute_graph(corner['source_encoder']['source_limb_uint32'],corner['unit_uint64'],corner['operations'])
                    v.update(witness_index=j,retained_corner_product_sha256=digest(corner),
                             source_encoder_sha256=digest(corner['source_encoder']),unit_uint64=deepcopy(corner['unit_uint64']))
                    nodes+=8;matched+=int(v['exact_retained_node_bits_match']);failed+=int(not v['exact_retained_node_bits_match']);points.append(v)
                executed+=1;row.update(points=points,bare_source_values_computed_new=True,
                    exact_all_fixture_node_bits_match=all(v['exact_retained_node_bits_match'] for v in points),
                    reason='partial CPU SOURCE fixture execution only; unit/path/scene execution, material/allocation/backend-domain theorem remain absent',**{FLAG:True})
            rows.append(row)
        cases[n]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'runtime_probe':probe,
        'inherited_pins_verified':len(pins),'executed_source_fixture_sets':executed,'retained_sources_not_executed':stops,
        'new_CPU_float64_RN_nodes_executed':nodes,'point_graphs_bits_MATCH':matched,'point_graphs_bits_FAIL':failed,
        'old_numeric_producers_reexecuted':0,'source_encoder_executed_new':False,'unit_or_scene_inference_executed_new':False,
        'stage_inputs':'retained encoded SOURCE capsule plus retained propagation-unit words; explicit partial stage, not raw-scene inference',
        'cost_scope':'SOURCE-stage node counts plus six runtime-probe operations only; pins/context/encoder/unit/material/reduction/transfer/setup costs not measured',
        **dict.fromkeys(FALSE,False)}
