"""New native CPU Horner26 point on SHA-retained guarded scene argument."""
import math
from copy import deepcopy
from fractions import Fraction as F
import axial_guarded_residual_argument_RN64_CPU_v1 as prior
guard=prior.guard
original=prior.original
source=prior.source
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
FALSE=prior.FALSE
MODEL='axial-retained-guarded-argument-new-Horner26-unit-RN64-CPU-point-v1'
FLAG='guarded_argument_unit_RN64_CPU_executed'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-RESIDUAL-ARGUMENT-RN64-CPU-001-CODEX.json'
PREVIOUS_SHA='06a224643cc77a1e78f8526b719d5e208624b9aca81c901014f81cdb9f208679'
PROFILE='coordinacion/respuestas/AXIAL-UNIFORM-UNIT-HOST-001-CODEX.json'
PHASE_NAMES=tuple(n.replace('_cycles','_rad') for n in prior.CYCLE_CHARGES)+('constant_2pi_rad','argument_multiply_RN64_rad')
LABELS=['square']+[name+'.'+op+str(j) for name in ('cos','sin') for j in range(5,-1,-1) for op in ('mul','add')]+['sin.final']

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA));require(r['task_id']=='AXIAL-GUARDED-RESIDUAL-ARGUMENT-RN64-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['audit'];quot=data(prior.PREVIOUS)['data']['audit'];roots=data(prior.prior.PREVIOUS)['data']['audit']
    profile=data(PROFILE)['data']['audit']['coefficient_profile']
    packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases'])==set(quot['cases'])==set(roots['cases']),'complete cases')
    return packets,old,quot,roots,profile,pins

def validate_profile(profile):
    require(type(profile) is dict and set(profile)=={'cos','sin'},'fixed coefficient names');vals={}
    for name,odd in (('cos',0),('sin',1)):
        require(type(profile[name]) is list and len(profile[name])==7,'seven frozen coefficients');vals[name]=[]
        for j,c in enumerate(profile[name]):
            exact=F((-1)**j,math.factorial(2*j+odd))
            v=guard.check_RN(exact,c['uint64'],64,int(exact<0))
            require(guard.rational(c['exact_rational'])==exact and guard.rational(c['error_rational'])==abs(v-exact),'frozen exact coefficient ledger')
            vals[name].append(c['uint64'])
    return vals

def admit(snapshot,index,row,qr,rr,cap,profile):
    a=prior.admit(snapshot,index,qr,rr,cap);require(row['admission']==a,'same guarded scene argument admission')
    v=row['result'];C,lo,hi,ec=prior.constant(a['TWO_PI_uint64']);rw=a['residual_uint64'];R=guard.bits(rw,64)
    exact=C*R;aw=v['argument_uint64'];T=guard.check_RN(exact,aw,64,rw>>63)
    require(v['multiply_node']=={'input_uint64':[rw,prior.TWO_PI],'output_uint64':aw,'exact_product_rad':pair(exact),'signed_RN64_delta_rad':pair(T-exact)},'argument multiply ledger')
    charges={n.replace('_cycles','_rad'):hi*guard.rational(t) for n,t in a['upstream_cycle_charges'].items()}
    charges.update(constant_2pi_rad=abs(R)*ec,argument_multiply_RN64_rad=abs(T-exact));P=sum(charges.values(),F(0))
    R0=guard.rational(a['fixed_ORIGINAL_residual_cycles']);interval=sorted([lo*R0,hi*R0]);obs=max(abs(T-t) for t in interval)
    require(v['TWO_PI_uint64']==prior.TWO_PI and v['pi_enclosure_rad_per_cycle']==[pair(lo),pair(hi)] and v['constant_2pi_error_bound_rad_per_cycle']==pair(ec),'same constant enclosure')
    require(v['phase_charges_rad']=={n:pair(t) for n,t in charges.items()} and v['argument_to_fixed_ORIGINAL_bound_rad']==pair(P),'seven argument charges')
    require(v['fixed_ORIGINAL_argument_interval_rad']==[pair(t) for t in interval] and v['observed_argument_error_upper_rad']==pair(obs) and obs<=P,'same fixed ORIGINAL argument')
    require(abs(T)+P<1 and v['unchanged_phase_cap_rad']==cap and v['point_argument_phase_charge_fits_cap'] is (P<=guard.rational(cap)),'argument domain/cap')
    require(type(v['new_RN64_multiplies']) is int and v['new_RN64_multiplies']==1,'retained operation count')
    k=qr['result']['HOST_quarter_index'];require(type(k) is int,'fixed quarter index')
    validate_profile(profile)
    return {'source_id':a['source_id'],'argument_uint64':aw,'quadrant_mod4':k%4,
        'upstream_phase_charges_rad':{n:pair(t) for n,t in charges.items()},'upstream_phase_bound_rad':pair(P),
        'unchanged_phase_cap_rad':deepcopy(cap),'coefficient_profile_sha256':digest(profile),'retained_argument_row_sha256':digest(row)}

def native_multiply(a,b):return a*b
def native_add(a,b):return a+b

def execute(admission,profile):
    cap=admission['unchanged_phase_cap_rad'];require(type(cap) is list and cap==[1,10**12] and all(type(t) is int for t in cap),'unchanged phase cap')
    require(admission['coefficient_profile_sha256']==digest(profile),'same coefficient profile');coeff=validate_profile(profile)
    aw=admission['argument_uint64'];Xq=guard.bits(aw,64);X=abs(Xq);k=admission['quadrant_mod4']
    require(type(k) is int and 0<=k<4,'typed quadrant')
    up={n:guard.rational(t) for n,t in admission['upstream_phase_charges_rad'].items()};A=sum(up.values(),F(0))
    require(set(up)==set(PHASE_NAMES) and all(t>=0 for t in up.values()) and guard.rational(admission['upstream_phase_bound_rad'])==A,'seven upstream phase charges')
    require(X+A<1,'unchanged represented angle plus bound domain')
    nodes=[]
    def node(a,b,op,label):
        aq,bq=guard.bits(a,64),guard.bits(b,64);exact=aq*bq if op=='mul' else aq+bq
        zs=(a>>63)^(b>>63) if op=='mul' else int(aq==bq==0 and a>>63==b>>63==1)
        value=(native_multiply if op=='mul' else native_add)(source.value(a,64),source.value(b,64))
        w=source.word(value);q=guard.check_RN(exact,w,64,zs);e=abs(q-exact)
        nodes.append({'label':label,'op':op,'input_uint64':[a,b],'output_uint64':w,'exact_operation':pair(exact),'signed_RN64_delta':pair(q-exact)})
        return w,e
    zw,ez=node(aw,aw,'mul','square');Z=abs(guard.bits(zw,64));terms={};words=[]
    for name,odd in (('cos',0),('sin',1)):
        exacts=[F((-1)**j,math.factorial(2*j+odd)) for j in range(7)]
        hw=coeff[name][6];ideal=exacts[6];ec=abs(guard.bits(hw,64)-ideal);es=er=F(0)
        for j in range(5,-1,-1):
            pw,em=node(hw,zw,'mul',name+'.mul'+str(j));hw,ea=node(pw,coeff[name][j],'add',name+'.add'+str(j))
            ec=Z*ec+abs(guard.bits(coeff[name][j],64)-exacts[j]);es=Z*es+abs(ideal)*ez;er=Z*er+em+ea
            ideal=ideal*Xq*Xq+exacts[j]
        if odd:
            hw,ef=node(hw,aw,'mul','sin.final');ec*=X;es*=X;er=er*X+ef;ideal*=Xq
        observed=abs(guard.bits(hw,64)-ideal);require(observed<=ec+es+er,'point Horner error enclosed')
        rem=X**(14+odd)/math.factorial(14+odd)
        terms[name]={'coefficient_L1':pair(ec),'square_L1':pair(es),'RN_nodes_L1':pair(er),'Taylor_L1':pair(rem),
            'ideal_polynomial':pair(ideal),'observed_polynomial_error_L1':pair(observed),'term_total_L1':pair(ec+es+er+rem)}
        words.append(hw)
    poly={n:sum((guard.rational(t[n]) for t in terms.values()),F(0)) for n in ('coefficient_L1','square_L1','RN_nodes_L1','Taylor_L1')}
    B=sum(poly.values(),F(0));require(0<=B<F(1,2) and [n['label'] for n in nodes]==LABELS,'small point bound and Horner26 graph')
    a,b=words;sign=1<<63
    unit=[a,b] if k==0 else ([b^sign,a] if k==1 else ([a^sign,b^sign] if k==2 else [b,a^sign]))
    l1={**poly,**{n.replace('_rad','_L1'):2*t for n,t in up.items()}}
    phase={**up,**{n.replace('_L1','_phase_rad'):t/(1-B) for n,t in poly.items()}}
    P=sum(phase.values(),F(0));L=sum(l1.values(),F(0));require(P==B/(1-B)+A and L==B+2*A,'point unit composition')
    return {'argument_uint64':aw,'quadrant_mod4':k,'coefficient_profile_sha256':digest(profile),'nodes':nodes,
        'unpermuted_unit_uint64':words,'unit_uint64':unit,'terms':terms,'polynomial_charges_L1':{n:pair(t) for n,t in poly.items()},
        'point_polynomial_L1_bound':pair(B),'point_polynomial_phase_bound_rad':pair(B/(1-B)),
        'unit_L1_charges_to_FIXED_ORIGINAL':{n:pair(t) for n,t in l1.items()},'point_unit_L1_bound_to_FIXED_ORIGINAL':pair(L),
        'phase_charges_to_FIXED_ORIGINAL_rad':{n:pair(t) for n,t in phase.items()},'point_unit_phase_bound_to_FIXED_ORIGINAL_rad':pair(P),
        'unchanged_phase_cap_rad':deepcopy(cap),'point_unit_phase_charge_fits_cap':P<=guard.rational(cap),
        'new_RN64_horner_nodes':26,'quarter_bit_permutation_executed':True,'zero_canonicalization_performed':False,
        'scope':'new CPU Horner26 point on retained guarded scene argument; no SOURCE/material/budgets/full field/whole-domain/physical optics'}

def audit_unit_CPU(case_names,*,model):
    require(model==MODEL,'explicit scene-bound unit CPU model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,quot,roots,profile,pins=load_retained();require(set(case_names)<=set(packets),'known cases');validate_profile(profile);admitted=[]
    for name in case_names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context']==quot['cases'][name]['context']==roots['cases'][name]['context'],'same fresh INPUT')
        snap,meta=original.snapshot_from_packet(packets[name],ctx);rows=old['cases'][name]['sources'];qs=quot['cases'][name]['sources'];rs=roots['cases'][name]['sources']
        require(ctx['source_order']==[r['source_id'] for r in rows]==[r['source_id'] for r in qs]==[r['source_id'] for r in rs],'complete ordered sources')
        ads={}
        for i,row in enumerate(rows):
            require(type(row[prior.FLAG]) is bool and row[prior.FLAG] is qs[i][prior.prior.FLAG] is rs[i][prior.prior.prior.FLAG],'same eligibility')
            require(row['status']=='STOP' and all(row[n] is False for n in FALSE),'no broad predecessor promotion')
            if row[prior.FLAG]:
                require(row['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id'] and row['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id'],'same source gauges')
                ads[i]=admit(snap,i,row,qs[i],rs[i]['result'],meta['original_path_phase_caps'][row['source_id']],profile)
        admitted.append((name,ctx,ads))
    cases={};executed=stopped=0
    for name,ctx,ads in admitted:
        rows=[]
        for i,r in enumerate(old['cases'][name]['sources']):
            row={'source_id':r['source_id'],'status':'STOP',FLAG:False,'retained_row_sha256':digest(r),**dict.fromkeys(FALSE,False)}
            if i not in ads:stopped+=1;row.update(reason=r['reason'],reason_provenance='unchanged_retained_STOP')
            else:
                result=execute(ads[i],profile);executed+=1
                row.update(admission=ads[i],result=result,**{FLAG:True},phase_reference_id=ctx['assignments'][i]['source_phase_reference_id'],
                    terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],reason='CPU point unit only; source/material/INPUT allocations/native backend/full field STOP')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'coefficient_profile':deepcopy(profile),
        'inherited_pins_verified':len(pins),'new_point_sources_executed':executed,'retained_sources_not_executed':stopped,
        'new_RN64_horner_nodes':26*executed,'new_quarter_bit_permutations':executed,'old_native_stages_suites_reexecuted':0,
        'cost_scope':'26 new CPU RN nodes/point plus exact bit permutation; HOST ledger/Taylor/proofs/profile/pins/IO/setup unmeasured; upstream not zero/no equal-work benchmark',
        **dict.fromkeys(FALSE,False)}
