"""New RN64 quotient/residual stage on SHA-pinned retained hi-lo Xroot outputs."""
from copy import deepcopy
from fractions import Fraction as F
import axial_guarded_hilo_xroot_RN64_CPU_v1 as prior
guard=prior.guard
original=prior.original
source=prior.source
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
FALSE=prior.FALSE
MODEL='axial-retained-guarded-Xroot-new-RN64-quotient-HOST-quarter-CPU-residual-v1'
FLAG='guarded_quotient_quarter_RN64_CPU_executed'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-HILO-XROOT-RN64-CPU-001-CODEX.json'
PREVIOUS_SHA='9e8166babef7b1ba22a2d0b492a3950cf31127bfa2cfecbe35bb81b3be7f5e52'
CHARGES=('geometry_representation_cycles','Xroot_length_rounding_cycles','wavelength_representation_cycles')

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA));require(r['task_id']=='AXIAL-GUARDED-HILO-XROOT-RN64-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['audit'];packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases']),'complete cases')
    return packets,old,pins

def admit(snapshot,index,result,cap):
    require(type(cap) is list and cap==[1,10**12] and all(type(x) is int for x in cap),'unchanged phase cap')
    encoder=result['retained_geometry_encoder'];guard.admit(snapshot,index,encoder)
    decoded=result['decoded_snapshot']
    for r in encoder['records']:
        require(source.word(guard.prior.get(decoded,r['path']))==r['decoded_uint64'],'retained decoded input bits')
    require(result['guarded_decode']['decoded_snapshot_digest']==digest(decoded),'retained decoded snapshot digest')
    fixed=result['fixed_ORIGINAL_reference'];root=result['new_decoded_Xroot_result']
    require(fixed['source_id']==snapshot['sources'][index]['id'],'same source ORIGINAL')
    comp=prior.compose(fixed,root,int(snapshot['sources'][index]['direction'][0]),cap)
    require(comp==result['composition'],'retained composition binding')
    Lword=root['effective_reference_length_uint64'];Wword=source.word(decoded['lambda_BU'])
    L,W=guard.bits(Lword,64),guard.bits(Wword,64);require(L>0 and W>0,'positive retained length/wavelength')
    require(W==guard.rational(root['fixed_ORIGINAL_reference']['wavelength_BU']),'same decoded wavelength')
    charge={k:guard.rational(comp['cycle_charges_to_fixed_ORIGINAL'][k]) for k in CHARGES}
    require(all(v>=0 for v in charge.values()) and sum(charge.values(),F(0))==guard.rational(comp['cycles_to_fixed_ORIGINAL_bound']),'three upstream charges')
    Q0=guard.rational(fixed['exact_ORIGINAL_cycles']);k=fixed['quarter_index']
    require(type(k) is int and abs(k)<2**51 and k==(4*Q0+F(1,2))//1,'bounded ORIGINAL quarter index')
    return {'source_id':fixed['source_id'],'length_uint64':Lword,'wavelength_uint64':Wword,
        'exact_retained_length_over_decoded_wave':pair(L/W),'fixed_ORIGINAL_cycles':pair(Q0),'fixed_quarter_index':k,
        'upstream_cycle_charges':{n:pair(v) for n,v in charge.items()},'upstream_cycles_bound':pair(sum(charge.values(),F(0))),
        'unchanged_phase_cap_rad':deepcopy(cap),'retained_result_sha256':digest(result)}

def native_divide(a,b):return a/b
def native_quarter(k):return float(F(k,4))
def native_subtract(a,b):return a-b

def execute(admission):
    cap=admission['unchanged_phase_cap_rad']
    require(type(cap) is list and cap==[1,10**12] and all(type(x) is int for x in cap),'unchanged phase cap')
    Lw,Ww=admission['length_uint64'],admission['wavelength_uint64']
    L,W=guard.bits(Lw,64),guard.bits(Ww,64);require(L>0 and W>0,'positive denominator/numerator')
    exact=L/W
    require(guard.rational(admission['exact_retained_length_over_decoded_wave'])==exact,'retained quotient inputs')
    upstream={n:guard.rational(v) for n,v in admission['upstream_cycle_charges'].items()}
    require(set(upstream)==set(CHARGES) and all(v>=0 for v in upstream.values()),'typed upstream charges')
    require(guard.rational(admission['upstream_cycles_bound'])==sum(upstream.values(),F(0)),'upstream total')
    Q0=guard.rational(admission['fixed_ORIGINAL_cycles']);fixedk=admission['fixed_quarter_index']
    require(type(fixedk) is int and abs(fixedk)<2**51 and fixedk==(4*Q0+F(1,2))//1,'typed fixed quarter')
    observed=native_divide(source.value(Lw,64),source.value(Ww,64))
    qw=source.word(observed);Q=guard.check_RN(exact,qw,64,0);require(Q>0,'positive RN64 quotient')
    division=abs(Q-exact)
    E=sum(upstream.values(),F(0))+division
    require(abs(Q-Q0)<=E,'quotient bound toward ORIGINAL')
    # HOST integer/rational selection on observed RN64 quotient, no exact-reference fallback.
    k=(4*Q+F(1,2))//1
    require(type(k) is int and abs(k)<2**51 and k==admission['fixed_quarter_index'],'observed quarter agrees with fixed ORIGINAL')
    margin=F(1,8)-abs(Q0-F(k,4))-E
    require(margin>0,'ambiguous quarter interval STOP before residual')
    quarter=native_quarter(k);kw=source.word(quarter);K=guard.check_RN(F(k,4),kw,64,0 if k>=0 else 1)
    require(K==F(k,4),'quarter exactly represented')
    residual=native_subtract(observed,quarter);rw=source.word(residual)
    zero_sign=int(Q==K==0 and qw>>63==1 and kw>>63==0)
    R=guard.check_RN(Q-K,rw,64,zero_sign);require(abs(R)<F(1,8),'strict residual branch')
    subtraction=abs(R-(Q-K));total=E+subtraction
    require(abs(R-(Q0-F(k,4)))<=total,'residual error toward ORIGINAL')
    charges={**upstream,'quotient_RN64_cycles':division,'quarter_subtraction_RN64_cycles':subtraction}
    phase={n.replace('_cycles','_rad'):2*original.PI_UPPER*v for n,v in charges.items()}
    P=sum(phase.values(),F(0))
    return {'quotient_uint64':qw,'division_node':{'input_uint64':[Lw,Ww],'output_uint64':qw,'exact_quotient':pair(exact),'signed_RN64_delta_cycles':pair(Q-exact)},
        'HOST_quarter_index':k,'quarter_cast_node':{'input_exact_rational':pair(F(k,4)),'output_uint64':kw,'RN64_delta_cycles':[0,1]},
        'residual_subtraction_node':{'input_uint64':[qw,kw],'output_uint64':rw,'exact_subtraction_cycles':pair(Q-K),'signed_RN64_delta_cycles':pair(R-(Q-K))},
        'residual_uint64':rw,'fixed_ORIGINAL_residual_cycles':pair(Q0-F(k,4)),
        'cycle_charges_to_fixed_ORIGINAL':{n:pair(v) for n,v in charges.items()},'residual_to_fixed_ORIGINAL_bound_cycles':pair(total),
        'observed_residual_error_cycles':pair(abs(R-(Q0-F(k,4)))),'phase_charges_rad':{n:pair(v) for n,v in phase.items()},
        'phase_quotient_residual_only_bound_rad':pair(P),'unchanged_phase_cap_rad':admission['unchanged_phase_cap_rad'],
        'partial_phase_charge_fits_cap':P<=guard.rational(admission['unchanged_phase_cap_rad']),
        'quarter_margin_with_quotient_error_cycles':pair(margin),
        'new_RN64_divisions':1,'new_exact_quarter_RN64_casts':1,'new_RN64_subtractions':1,
        'quarter_selection_backend':'HOST exact integer/rational on observed CPU quotient, not native selector',
        'scope':'new CPU quotient/cast/residual from retained guarded Xroot length; no old root/decode replay or argument/unit/fullfield'}

def audit_quotient_CPU(case_names,*,model):
    require(model==MODEL,'explicit new quotient/residual model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    admitted=[]
    for name in case_names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context'],'same fresh INPUT')
        snap,meta=original.snapshot_from_packet(packets[name],ctx);rows=old['cases'][name]['sources']
        require(ctx['source_order']==[r['source_id'] for r in rows],'complete ordered sources')
        ads={i:admit(snap,i,r['result'],meta['original_path_phase_caps'][r['source_id']]) for i,r in enumerate(rows) if r[prior.FLAG]}
        admitted.append((name,ctx,ads))
    cases={};executed=stopped=0
    for name,ctx,ads in admitted:
        rows=[]
        for i,r in enumerate(old['cases'][name]['sources']):
            row={'source_id':r['source_id'],'status':'STOP',FLAG:False,'retained_row_sha256':digest(r),**dict.fromkeys(FALSE,False)}
            if i not in ads:stopped+=1;row.update(reason=r['reason'],reason_provenance='unchanged_retained_STOP')
            else:
                result=execute(ads[i]);executed+=1
                row.update(admission=ads[i],result=result,**{FLAG:True},phase_reference_id=ctx['assignments'][i]['source_phase_reference_id'],
                    terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],
                    reason='quotient/residual point only; argument/unit/amplitude budgets/native/full field STOP')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
        'new_point_sources_executed':executed,'retained_sources_not_executed':stopped,
        'new_RN64_divisions':executed,'new_exact_quarter_RN64_casts':executed,'new_RN64_subtractions':executed,
        'new_encoder_guard_decode_Xroot_reference_Horner_source_material_reduction_power_readout':0,
        'old_audits_suites_reexecuted':0,'native_quarter_selector_implemented':False,
        'cost_scope':'main CPU division1/exact cast1/subtraction1 per source; HOST index/proofs/admission/IO/pins/setup unmeasured; retained upstream costs not zero; no complete benchmark',
        **dict.fromkeys(FALSE,False)}
