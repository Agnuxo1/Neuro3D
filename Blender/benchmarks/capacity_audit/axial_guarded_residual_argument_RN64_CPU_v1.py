"""Opt-in new CPU argument multiply on retained guarded scene quotient/residual."""
from copy import deepcopy
from fractions import Fraction as F
import axial_guarded_quotient_quarter_RN64_CPU_v1 as prior
guard=prior.guard
original=prior.original
source=prior.source
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
FALSE=prior.FALSE
MODEL='axial-retained-guarded-residual-new-2pi-argument-RN64-CPU-point-v1'
FLAG='guarded_residual_argument_RN64_CPU_executed'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-QUOTIENT-QUARTER-RN64-CPU-001-CODEX.json'
PREVIOUS_SHA='d24b3ec22d6aceea7f7bb01ba509459dafd450260c0b87c9039f322c835e017d'
TWO_PI=0x401921fb54442d18
CYCLE_CHARGES=prior.CHARGES+('quotient_RN64_cycles','quarter_subtraction_RN64_cycles')

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA));require(r['task_id']=='AXIAL-GUARDED-QUOTIENT-QUARTER-RN64-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['audit'];roots=data(prior.PREVIOUS)['data']['audit']
    packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases'])==set(roots['cases']),'complete cases')
    return packets,old,roots,pins

def constant(word):
    require(type(word) is int and word==TWO_PI,'fixed 2pi word')
    lo,hi=2*original.PI_LOWER,2*original.PI_UPPER
    require(F(6)<lo<hi<F(7),'pinned mathematical pi enclosure')
    C=guard.check_RN(lo,word,64,0);guard.check_RN(hi,word,64,0)
    return C,lo,hi,max(abs(C-lo),abs(C-hi))

def admit(snapshot,index,row,root_result,cap):
    a=prior.admit(snapshot,index,root_result,cap);require(row['admission']==a,'retained admission scene binding')
    v=row['result'];L=guard.bits(a['length_uint64'],64);W=guard.bits(a['wavelength_uint64'],64);x=L/W
    qw=v['quotient_uint64'];Q=guard.check_RN(x,qw,64,0);require(Q>0,'positive quotient')
    require(v['division_node']=={'input_uint64':[a['length_uint64'],a['wavelength_uint64']],'output_uint64':qw,'exact_quotient':pair(x),'signed_RN64_delta_cycles':pair(Q-x)},'division ledger')
    k=v['HOST_quarter_index'];Q0=guard.rational(a['fixed_ORIGINAL_cycles'])
    require(type(k) is int and abs(k)<2**51 and k==a['fixed_quarter_index']==(4*Q+F(1,2))//1,'same observed quarter')
    cast=v['quarter_cast_node'];kw=cast['output_uint64'];K=guard.check_RN(F(k,4),kw,64,0 if k>=0 else 1)
    require(K==F(k,4) and cast=={'input_exact_rational':pair(F(k,4)),'output_uint64':kw,'RN64_delta_cycles':[0,1]},'exact quarter ledger')
    rw=v['residual_uint64'];R=guard.check_RN(Q-K,rw,64,0);require(abs(R)<F(1,8),'strict residual branch')
    require(v['residual_subtraction_node']=={'input_uint64':[qw,kw],'output_uint64':rw,'exact_subtraction_cycles':pair(Q-K),'signed_RN64_delta_cycles':pair(R-(Q-K))},'residual ledger')
    charges={n:guard.rational(t) for n,t in a['upstream_cycle_charges'].items()}
    charges.update(quotient_RN64_cycles=abs(Q-x),quarter_subtraction_RN64_cycles=abs(R-(Q-K)))
    require(v['cycle_charges_to_fixed_ORIGINAL']=={n:pair(t) for n,t in charges.items()},'five retained charges')
    E=sum(charges.values(),F(0));R0=Q0-F(k,4)
    margin=F(1,8)-abs(R0)-(E-charges['quarter_subtraction_RN64_cycles'])
    require(margin>0 and v['quarter_margin_with_quotient_error_cycles']==pair(margin),'strict quarter margin')
    phase={n.replace('_cycles','_rad'):2*original.PI_UPPER*t for n,t in charges.items()};P=sum(phase.values(),F(0))
    require(v['residual_to_fixed_ORIGINAL_bound_cycles']==pair(E) and v['fixed_ORIGINAL_residual_cycles']==pair(R0),'retained total/reference')
    require(v['observed_residual_error_cycles']==pair(abs(R-R0)) and abs(R-R0)<=E,'retained observed error')
    require(v['phase_charges_rad']=={n:pair(t) for n,t in phase.items()} and v['phase_quotient_residual_only_bound_rad']==pair(P),'retained phase ledger')
    require(v['unchanged_phase_cap_rad']==cap and v['partial_phase_charge_fits_cap'] is (P<=guard.rational(cap)),'retained cap binding')
    require(v['new_RN64_divisions']==v['new_exact_quarter_RN64_casts']==v['new_RN64_subtractions']==1,'retained operation counts')
    constant(TWO_PI)
    return {'source_id':a['source_id'],'residual_uint64':rw,'fixed_ORIGINAL_residual_cycles':pair(R0),
        'upstream_cycle_charges':{n:pair(t) for n,t in charges.items()},'upstream_cycles_bound':pair(E),
        'unchanged_phase_cap_rad':deepcopy(cap),'TWO_PI_uint64':TWO_PI,'retained_quotient_row_sha256':digest(row)}

def native_multiply(a,b):return a*b

def execute(admission):
    cap=admission['unchanged_phase_cap_rad'];require(type(cap) is list and cap==[1,10**12] and all(type(t) is int for t in cap),'unchanged phase cap')
    C,lo,hi,ec=constant(admission['TWO_PI_uint64'])
    rw=admission['residual_uint64'];R=guard.bits(rw,64);require(abs(R)<F(1,8),'strict residual before multiply')
    R0=guard.rational(admission['fixed_ORIGINAL_residual_cycles']);require(abs(R0)<F(1,8),'strict ORIGINAL residual')
    upstream={n:guard.rational(t) for n,t in admission['upstream_cycle_charges'].items()}
    require(set(upstream)==set(CYCLE_CHARGES) and all(t>=0 for t in upstream.values()),'five typed nonnegative charges')
    E=sum(upstream.values(),F(0));require(guard.rational(admission['upstream_cycles_bound'])==E and abs(R-R0)<=E,'upstream bound and total')
    observed=native_multiply(source.value(rw,64),source.value(TWO_PI,64));ow=source.word(observed)
    exact=C*R;T=guard.check_RN(exact,ow,64,rw>>63);em=abs(T-exact)
    phases={n.replace('_cycles','_rad'):hi*t for n,t in upstream.items()}
    phases.update(constant_2pi_rad=abs(R)*ec,argument_multiply_RN64_rad=em);P=sum(phases.values(),F(0))
    interval=sorted([lo*R0,hi*R0]);observed_bound=max(abs(T-t) for t in interval)
    require(observed_bound<=P,'argument error toward fixed ORIGINAL pi enclosure')
    require(abs(T)+P<F(1),'point argument plus bound inside unchanged +/-1rad domain')
    return {'TWO_PI_uint64':TWO_PI,'pi_enclosure_rad_per_cycle':[pair(lo),pair(hi)],
        'constant_2pi_error_bound_rad_per_cycle':pair(ec),'multiply_node':{'input_uint64':[rw,TWO_PI],'output_uint64':ow,
          'exact_product_rad':pair(exact),'signed_RN64_delta_rad':pair(T-exact)},
        'argument_uint64':ow,'fixed_ORIGINAL_argument_interval_rad':[pair(t) for t in interval],
        'phase_charges_rad':{n:pair(t) for n,t in phases.items()},'argument_to_fixed_ORIGINAL_bound_rad':pair(P),
        'observed_argument_error_upper_rad':pair(observed_bound),'unchanged_phase_cap_rad':deepcopy(cap),
        'point_argument_phase_charge_fits_cap':P<=guard.rational(cap),'new_RN64_multiplies':1,
        'scope':'CPU point argument multiply only; retained guarded scene/residual; no quarter/trace/decode replay, Horner/source/fullfield or physical uncertainty'}

def audit_argument_CPU(case_names,*,model):
    require(model==MODEL,'explicit new scene-bound CPU argument model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,roots,pins=load_retained();require(set(case_names)<=set(packets),'known cases');admitted=[]
    for name in case_names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context']==roots['cases'][name]['context'],'same fresh INPUT')
        snap,meta=original.snapshot_from_packet(packets[name],ctx);rows=old['cases'][name]['sources'];rs=roots['cases'][name]['sources']
        require(ctx['source_order']==[r['source_id'] for r in rows]==[r['source_id'] for r in rs],'complete ordered sources')
        ads={}
        for i,row in enumerate(rows):
            require(type(row[prior.FLAG]) is bool and row[prior.FLAG] is rs[i][prior.prior.FLAG],'same retained eligibility')
            require(all(row[k] is False for k in FALSE) and row['status']=='STOP','no broad promotion from predecessor')
            if row[prior.FLAG]:
                require(row['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id'] and row['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id'],'source gauge binding')
                ads[i]=admit(snap,i,row,rs[i]['result'],meta['original_path_phase_caps'][row['source_id']])
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
                    terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],reason='CPU point argument only; native backend/unit/amplitude budgets/full field STOP')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
        'new_point_sources_executed':executed,'retained_sources_not_executed':stopped,'new_RN64_multiplies':executed,
        'old_native_stages_suites_reexecuted':0,'native_quarter_ray_backend_implemented':False,
        'cost_scope':'1 new CPU multiplication/source; HOST pi/retained admission/proofs/pins/IO/setup unmeasured; upstream not zero/no equal-work benchmark',
        **dict.fromkeys(FALSE,False)}
