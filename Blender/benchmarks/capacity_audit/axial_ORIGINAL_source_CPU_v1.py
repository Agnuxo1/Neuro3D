"""Opt-in ORIGINAL CPU bare source prefix; IEEE signed zeros, no legacy promotion."""
import base64,hashlib,math,struct
from copy import deepcopy
from fractions import Fraction as F
import axial_ORIGINAL_unit_CPU_v1 as unit
io=unit.io
allocation=unit.allocation
require=unit.require
digest=unit.digest
pair=unit.pair
original=unit.original
source=unit.source
MODEL='axial-ORIGINAL-source-hi-lo32-IEEE-RN64-prefix-CPU-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-ORIGINAL-UNIT-CPU-001-CODEX.json'
PREVIOUS_SHA='0132858e34ca29a91ae8f91974531c706f7d973e0bbbeab1dba04f544f3c9fe3'
FALSE=unit.FALSE
FLAG='fresh_ORIGINAL_bare_source_prefix_CPU_executed'
LABELS=['decode0','decode1','ac','bd','ad','bc','real','imag']

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-ORIGINAL-UNIT-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['audit']
    failures=data(unit.SOURCE_REPORT)['data']['audit']
    require(failures['point_graphs_bits_FAIL']==8 and failures['point_graphs_bits_MATCH']==0,'historical SOURCE bit FAILs preserved')
    require(sum(n['zero_sign_only_mismatch'] for c in failures['cases'].values() for s in c['sources'] for p in s.get('points',[]) for n in p['nodes'])==12,'historical twelve signed zeros preserved')
    packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases']),'complete retained sources/cases')
    return packets,old,pins

def cast32(v):
    require(type(v) is float and math.isfinite(v),'finite binary64 cast input')
    try:raw=struct.pack('<f',v)
    except (OverflowError,struct.error) as e:raise ValueError('binary32 cast overflow STOP') from e
    w=struct.unpack('<I',raw)[0];require((w>>23)%256<255,'finite binary32 cast')
    return struct.unpack('<f',raw)[0],w

def runtime_probe():
    fp64=source.runtime_probe()
    inputs=[1.0000000596046448,1.0000001788139343,math.ldexp(1.0,-149),-0.0]
    expected=[0x3f800000,0x3f800002,1,0x80000000]
    checks=[]
    for label,v,w in zip(('tie_even_one32','tie_even_odd32','gradual_cast32','negative_zero32'),inputs,expected):
        _,out=cast32(v);checks.append({'label':label,'actual_uint32':out,'expected_uint32':w,'PASS':out==w})
    return {'binary64':fp64,'binary32_cast_checks':checks,'PASS':fp64['PASS'] and all(c['PASS'] for c in checks),
        'CPU_binary64_probe_ops':6,'CPU_binary32_probe_casts':4,
        'scope':'local observed probes, not execution/coherence authentication or backend theorem'}

def encode_source(field):
    """Fresh hi=RN32(x), residual=RN64(x-hi), lo=RN32(residual); no zero canonicalization."""
    require(type(field) is list and len(field)==2,'two complex ORIGINAL components')
    traces=[];limbs=[];sums=[];error=F(0)
    for x in field:
        original.number(x)
        hi,hw=cast32(x);source.value(hw,32)
        residual=x-hi
        require(math.isfinite(residual),'finite residual')
        lo,lw=cast32(residual);source.value(lw,32)
        exact_residual=F.from_float(x)-F.from_float(hi)
        represented=F.from_float(hi)+F.from_float(lo)
        err=abs(represented-F.from_float(x));error+=err;sums.append(represented)
        traces.append({'original_uint64':source.word(x),'high_uint32':hw,'residual_uint64':source.word(residual),'low_uint32':lw,
            'exact_residual_rational':pair(exact_residual),'residual_RN64_delta':pair(F.from_float(residual)-exact_residual),
            'low_cast_error_abs':pair(abs(F.from_float(lo)-F.from_float(residual))),
            'represented_exact_sum':pair(represented),'encoding_error_abs':pair(err)})
        limbs.extend((hw,lw))
    raw=struct.pack('<IIII',*limbs)
    return {'ORIGINAL_source_uint64':[source.word(x) for x in field],'source_limb_uint32':limbs,
        'source_hilo_le_base64':base64.b64encode(raw).decode(),'source_hilo_le_sha256':hashlib.sha256(raw).hexdigest(),
        'components':traces,'exact_source_limb_sums':list(map(pair,sums)),'source_encoding_error_L1':pair(error),
        'new_RN32_casts':4,'new_RN64_subtractions':2,'signed_zero_policy':'IEEE native signs at each node; never canonicalize',
        'scope':'fresh source amplitude limbs only, not encoded geometry or physical amplitude uncertainty'}

def product_prefix(encoder,unitwords,unit_bound):
    require(type(unitwords) is list and len(unitwords)==2,'two unit words')
    require(type(encoder) is dict and type(encoder['source_limb_uint32']) is list and len(encoder['source_limb_uint32'])==4,'four SOURCE limbs')
    U=F(*unit_bound);require(0<=U<1,'small point unit L1 error')
    limbs=encoder['source_limb_uint32'];vals=[source.value(w,32) for w in limbs]
    originals=[source.value(w,64) for w in encoder['ORIGINAL_source_uint64']]
    raw=struct.pack('<IIII',*limbs)
    require(encoder['source_hilo_le_base64']==base64.b64encode(raw).decode()
        and encoder['source_hilo_le_sha256']==hashlib.sha256(raw).hexdigest(),'source bytes/SHA')
    sums=[F.from_float(vals[0])+F.from_float(vals[1]),F.from_float(vals[2])+F.from_float(vals[3])]
    enc=sum((abs(F.from_float(x)-s) for x,s in zip(originals,sums)),F(0))
    require(encoder['source_encoding_error_L1']==pair(enc) and encoder['exact_source_limb_sums']==list(map(pair,sums)),'source encoding ledger')
    c,d=[source.value(w,64) for w in unitwords];nodes=[]
    def op(a,b,kind,label):
        out=a*b if kind=='mul' else a+b
        require(math.isfinite(out) and (out==0 or abs(out)>=math.ldexp(1.0,-1022)),'selected normal-or-zero RN64 result')
        exact=F.from_float(a)*F.from_float(b) if kind=='mul' else F.from_float(a)+F.from_float(b)
        nodes.append({'label':label,'op':kind,'input_uint64':[source.word(a),source.word(b)],'output_uint64':source.word(out),
            'observed_delta_rational':pair(F.from_float(out)-exact)})
        return out
    a=op(vals[0],vals[1],'add','decode0');b=op(vals[2],vals[3],'add','decode1')
    ac=op(a,c,'mul','ac');bd=op(b,d,'mul','bd');ad=op(a,d,'mul','ad');bc=op(b,c,'mul','bc')
    re=op(ac,-bd,'add','real');im=op(ad,bc,'add','imag')
    decode=sum((abs(F(*n['observed_delta_rational'])) for n in nodes[:2]),F(0))
    RN=sum((abs(F(*n['observed_delta_rational'])) for n in nodes[2:]),F(0))
    L=abs(F.from_float(c))+abs(F.from_float(d));S=sum((abs(F.from_float(x)) for x in originals),F(0))
    charges={'source_encoding_L1':enc*L,'source_decode_RN64_L1':decode*L,'unit_to_ORIGINAL_L1':S*U,'product_RN64_L1':RN}
    bound=sum(charges.values(),F(0))
    ideal_decoded=[F.from_float(a)*F.from_float(c)-F.from_float(b)*F.from_float(d),
        F.from_float(a)*F.from_float(d)+F.from_float(b)*F.from_float(c)]
    observed=sum((abs(F.from_float(v)-q) for v,q in zip((re,im),ideal_decoded)),F(0))
    require(observed<=RN,'observed product errors enclosed')
    return {'nodes':nodes,'unit_uint64':deepcopy(unitwords),'decoded_source_uint64':[source.word(a),source.word(b)],
        'product_uint64':[source.word(re),source.word(im)],'observed_product_only_error_L1':pair(observed),
        'represented_unit_norm_L1':pair(L),'ORIGINAL_source_norm_L1':pair(S),'point_unit_error_L1':pair(U),
        'bare_source_error_charges_L1':{k:pair(v) for k,v in charges.items()},'point_bare_source_to_ORIGINAL_bound_L1':pair(bound),
        'new_CPU_RN64_nodes_executed':8,'signed_zero_policy':'IEEE per-node signs; old HOST canonical-zero graph NOT reclassified',
        'zero_canonicalization_performed':False,'source_amplitude_budget_admitted':False,
        'source_phase_bound_proved':False,'rule':'E <= (Eencoding+Edecode)*|uCPU|L1 + |sORIGINAL|L1*Eunit + Eproduct',
        'scope':'bare source-times-unit PREFIX only, no mirror coefficient, field reduction/detector or physical amplitude'}

def audit_ORIGINAL_source_CPU(case_names,*,model):
    require(model==MODEL,'explicit fresh source-prefix CPU model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    probe=runtime_probe();require(probe['PASS'] is True,'runtime guard FAIL before reference/encoder/product')
    profile=old['coefficient_profile'];unit.validate_profile(profile);cases={};executed=stopped=0
    for name in case_names:
        packet=packets[name];ctx=allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context'],'same fresh complete INPUT')
        snap,meta=original.snapshot_from_packet(packet,ctx);rows=[]
        require([s['source_id'] for s in old['cases'][name]['sources']]==ctx['source_order'],'complete ordered sources')
        for i,prior in enumerate(old['cases'][name]['sources']):
            row={'source_id':prior['source_id'],'status':'STOP',FLAG:False,'retained_unit_row_sha256':digest(prior),**dict.fromkeys(FALSE,False)}
            if not prior[unit.FLAG]:
                stopped+=1;row.update(reason=prior['reason'],reason_provenance='unchanged_retained_STOP')
            else:
                trace=original.trace_original(snap,i);arg=original.argument_from_trace(trace)
                u=unit.execute_unit(arg['argument_uint64'],trace['quadrant_mod4'],profile)
                comp=unit.compose_charges(arg,u,meta['original_path_phase_caps'][prior['source_id']])
                require(trace==prior['trace'] and arg==prior['argument'] and u==prior['unit'] and comp==prior['composition'],'fresh reference/unit cross-check AFTER execution')
                field=snap['sources'][i]['field_reim']
                require(packet['manifest']['layout']['sources']['stride_words']==32,'source INPUT stride')
                raw=base64.b64decode(packet['buffers_base64']['sources'],validate=True)
                require(len(raw)==128*len(ctx['source_order']) and raw[128*i+112:128*i+128]==struct.pack('<dd',*field),'ORIGINAL complex words in same INPUT ABI')
                encoder=encode_source(field);product=product_prefix(encoder,u['unit_uint64'],comp['point_unit_L1_to_ORIGINAL_bound'])
                executed+=1
                row.update(trace=trace,argument=arg,unit=u,composition=comp,encoder=encoder,bare_source_prefix=product,**{FLAG:True},
                    phase_reference_id=ctx['assignments'][i]['source_phase_reference_id'],terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],
                    reason='fresh CPU bare source prefix only; historical SOURCE FAILs and missing material/allocations/encoded geometry/full pipeline intact')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'coefficient_profile':profile,'runtime_probe':probe,
        'inherited_pins_verified':len(pins),'fresh_ORIGINAL_bare_source_prefixes_executed':executed,'retained_sources_not_executed':stopped,
        'new_CPU_Horner_nodes':26*executed,'new_CPU_argument_casts':executed,'new_CPU_argument_multiplies':executed,
        'new_CPU_source_RN32_casts':4*executed,'new_CPU_source_RN64_subtractions':2*executed,'new_CPU_source_decode_product_nodes':8*executed,
        'previous_SOURCE_eight_bit_FAILs_preserved':True,'previous_SOURCE_twelve_zero_sign_mismatches_preserved':True,
        'encoded_hi_lo_geometry_executed':False,'uniform_source_backend_domain_admitted':False,
        'new_material_reduction_power_readout_executions':0,
        'cost_scope':'main per source exact scene/reference/selector +1cast1mul argument +26Horner +4RN32cast2RN64sub source +8decode/product; probes6ops64+4casts32; IO/pins/snapshot/setup/rational work/remaining costs UNMEASURED never zero',
        **dict.fromkeys(FALSE,False)}
