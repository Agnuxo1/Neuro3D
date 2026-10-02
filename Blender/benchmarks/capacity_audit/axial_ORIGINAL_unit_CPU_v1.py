"""Opt-in fresh ORIGINAL reference to CPU Horner26, point error ledger only."""
from copy import deepcopy
from fractions import Fraction as F
import math
import axial_ORIGINAL_argument_CPU_v1 as original
io=original.io
allocation=original.allocation
require=original.require
digest=original.digest
pair=original.pair
source=original.prior.source
MODEL='axial-ORIGINAL-reference-RN64-Horner26-point-CPU-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-ORIGINAL-ARGUMENT-CPU-001-CODEX.json'
PREVIOUS_SHA='702cf4c070b7184d0e177d107a081a6eba8b373afa2668e1fec485af96409469'
UNIFORM=original.prior.UNIFORM
SOURCE_REPORT='coordinacion/respuestas/AXIAL-SOURCE-FLOAT64-STAGE-CPU-001-CODEX.json'
FALSE=original.FALSE
FLAG='fresh_ORIGINAL_reference_unit_CPU_executed'
LABELS=original.prior.LABELS
MIN_NORMAL=F(1,2**1022)

def load_retained():
    receipt=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(receipt['task_id']=='AXIAL-ORIGINAL-ARGUMENT-CPU-001','predecessor identity')
    pins=io.pins_from(receipt);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(receipt)['data']['audit']
    profile=data(UNIFORM)['data']['audit']['coefficient_profile']
    failures=data(SOURCE_REPORT)['data']['audit']
    require(failures['point_graphs_bits_FAIL']==8 and failures['point_graphs_bits_MATCH']==0,'retained SOURCE FAILs intact')
    require(sum(n['zero_sign_only_mismatch'] for c in failures['cases'].values() for s in c['sources'] for p in s.get('points',[]) for n in p['nodes'])==12,'retained twelve zero signs')
    packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases']),'complete cases')
    return packets,old,profile,pins

def validate_profile(profile):
    require(type(profile) is dict and set(profile)=={'cos','sin'},'fixed coefficient terms')
    vals={}
    for name,odd in (('cos',0),('sin',1)):
        require(type(profile[name]) is list and len(profile[name])==7,'seven coefficients')
        vals[name]=[]
        for j,c in enumerate(profile[name]):
            exact=F((-1)**j,math.factorial(2*j+odd))
            v=source.value(c['uint64'],64)
            require(c['exact_rational']==pair(exact) and c['error_rational']==pair(abs(F.from_float(v)-exact)),'fixed Taylor encoding ledger')
            vals[name].append(v)
    return vals

def execute_unit(angle_word,quadrant,profile):
    """New graph primitive with no retained angle/output/operation references."""
    require(type(quadrant) is int and 0<=quadrant<4,'strict quadrant')
    x=source.value(angle_word,64);X=abs(F.from_float(x))
    require(MIN_NORMAL<=X<=1,'selected nonzero normal argument in [-1,1]')
    coeff=validate_profile(profile);nodes=[]
    def op(a,b,kind,label):
        v=a*b if kind=='mul' else a+b
        require(math.isfinite(v) and abs(F.from_float(v))>=MIN_NORMAL,'selected nonnormal result STOP')
        exact=F.from_float(a)*F.from_float(b) if kind=='mul' else F.from_float(a)+F.from_float(b)
        delta=F.from_float(v)-exact
        nodes.append({'label':label,'op':kind,'input_uint64':[source.word(a),source.word(b)],
            'output_uint64':source.word(v),'observed_delta_rational':pair(delta)})
        return v,abs(delta)
    z,ez=op(x,x,'mul','square');Z=abs(F.from_float(z));terms={};words=[]
    for name,odd in (('cos',0),('sin',1)):
        exact=[F((-1)**j,math.factorial(2*j+odd)) for j in range(7)]
        h=coeff[name][6];ideal=exact[6]
        ec=abs(F.from_float(h)-ideal);es=er=F(0)
        for j in range(5,-1,-1):
            p,em=op(h,z,'mul',name+'.mul'+str(j))
            h,ea=op(p,coeff[name][j],'add',name+'.add'+str(j))
            ec=Z*ec+abs(F.from_float(coeff[name][j])-exact[j])
            es=Z*es+abs(ideal)*ez;er=Z*er+em+ea
            ideal=ideal*F.from_float(x)**2+exact[j]
        if odd:
            h,ef=op(h,x,'mul','sin.final')
            ec*=X;es*=X;er=er*X+ef;ideal*=F.from_float(x)
        actual=F.from_float(h);polynomial=ec+es+er
        require(abs(actual-ideal)<=polynomial,'actual ideal Taylor error enclosed')
        remainder=X**(14+odd)/math.factorial(14+odd)
        terms[name]={'coefficient_charge_L1':pair(ec),'square_charge_L1':pair(es),
            'RN_node_charge_L1':pair(er),'Taylor_remainder_L1':pair(remainder),
            'ideal_Taylor_rational':pair(ideal),'observed_Taylor_error_L1':pair(abs(actual-ideal)),
            'term_error_bound_L1':pair(polynomial+remainder)}
        words.append(source.word(h))
    B=sum(F(*t['term_error_bound_L1']) for t in terms.values())
    require(0<B<F(1,2) and [n['label'] for n in nodes]==LABELS,'small bound and Horner26 graph')
    a,b=words;sign=1<<63
    unit=[a,b] if quadrant==0 else ([b^sign,a] if quadrant==1 else ([a^sign,b^sign] if quadrant==2 else [b,a^sign]))
    return {'argument_uint64':angle_word,'quadrant_mod4':quadrant,'coefficient_profile_sha256':digest(profile),
        'nodes':nodes,'unpermuted_unit_uint64':words,'unit_uint64':unit,'terms':terms,
        'point_polynomial_L1_to_ideal_represented_angle_bound':pair(B),
        'point_polynomial_phase_bound_rad':pair(B/(1-B)),
        'new_CPU_float64_RN_nodes_executed':26,'retained_angle_or_result_substitution':False,
        'zero_canonicalization_performed':False,'scope':'new CPU Horner26 point, not SOURCE/material/reduction or whole-domain proof'}

def compose_charges(argument,unit,cap):
    delta=F(*argument['phase_error_bound_rad'])
    require(delta>=0 and delta==sum(F(*v) for v in argument['phase_error_charges_rad'].values()),'separate nonnegative argument charges')
    B=F(*unit['point_polynomial_L1_to_ideal_represented_angle_bound'])
    require(0<B<F(1,2) and F(*unit['point_polynomial_phase_bound_rad'])==B/(1-B),'phase radius theorem')
    require(cap==[1,10**12],'unchanged ORIGINAL phase cap')
    phase=B/(1-B)+delta;amplitude=B+2*delta
    return {'point_unit_L1_to_ORIGINAL_bound':pair(amplitude),'point_phase_to_ORIGINAL_bound_rad':pair(phase),
        'argument_phase_bound_rad':pair(delta),'polynomial_phase_bound_rad':pair(B/(1-B)),
        'unchanged_phase_cap_rad':deepcopy(cap),'phase_charge_fits_unchanged_cap':phase<=F(*cap),
        'rule':'L1 <= B+2*delta; angle <= B/(1-B)+delta; exact same quarter rotation',
        'scope':'fixed ORIGINAL point only, no encoded or physical uncertainty or whole-domain admission'}

def audit_ORIGINAL_unit_CPU(case_names,*,model):
    require(model==MODEL,'explicit fresh ORIGINAL point CPU model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique case names')
    packets,old,profile,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    probe=source.runtime_probe();require(probe['PASS'] is True,'runtime probe FAIL before scene/Horner')
    validate_profile(profile);cases={};executed=stopped=0
    for name in case_names:
        packet=packets[name];ctx=allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context'],'same fresh complete INPUT')
        snap,meta=original.snapshot_from_packet(packet,ctx);olds=old['cases'][name]['sources']
        require([s['source_id'] for s in olds]==ctx['source_order'],'all ordered sources')
        rows=[]
        for i,prior in enumerate(olds):
            row={'source_id':prior['source_id'],'status':'STOP',FLAG:False,'retained_argument_row_sha256':digest(prior),**dict.fromkeys(FALSE,False)}
            if not prior[original.FLAG]:
                stopped+=1;row.update(reason=prior['reason'],reason_provenance='unchanged_retained_STOP')
            else:
                # Derive every numerical input afresh from the fixed ORIGINAL snapshot.
                trace=original.trace_original(snap,i);arg=original.argument_from_trace(trace)
                require(trace==prior['trace'] and arg==prior['argument'],'fresh computation cross-check AFTER execution')
                unit=execute_unit(arg['argument_uint64'],trace['quadrant_mod4'],profile)
                cap=meta['original_path_phase_caps'][prior['source_id']]
                require(cap==prior['unchanged_phase_cap_rad'],'same ORIGINAL source cap')
                composition=compose_charges(arg,unit,cap);executed+=1
                row.update(trace=trace,argument=arg,unit=unit,composition=composition,**{FLAG:True},
                    phase_reference_id=ctx['assignments'][i]['source_phase_reference_id'],
                    terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],
                    reason='fresh restricted ORIGINAL reference to CPU unit only; SOURCE FAILs/material/allocations/encoded backend/complete pipeline remain STOP')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'coefficient_profile':profile,'runtime_probe':probe,
        'inherited_pins_verified':len(pins),'fresh_ORIGINAL_unit_sources_executed':executed,
        'retained_sources_not_executed':stopped,'new_CPU_Horner_RN_nodes_executed':26*executed,
        'new_CPU_argument_casts':executed,'new_CPU_argument_multiplies':executed,
        'new_SOURCE_material_reduction_executions':0,'previous_SOURCE_eight_bit_FAILs_preserved':True,
        'previous_SOURCE_twelve_signed_zero_mismatches_preserved':True,
        'encoded_hi_lo_backend_executed':False,'uniform_backend_domain_admitted':False,
        'cost_scope':'exact rational scene/reference/selector, 26 Horner nodes+1 cast+1 mul per source, six probes; IO/pins/coeffloads/setup/rational-bound work/remaining costs UNMEASURED not zero',
        **dict.fromkeys(FALSE,False)}
