"""Opt-in retained guarded unit -> new source hi-lo and RN64 bare product CPU."""
import base64,hashlib,math,struct
from copy import deepcopy
from fractions import Fraction as F
import axial_guarded_argument_unit_RN64_CPU_v1 as prior
import axial_ORIGINAL_source_CPU_v1 as transport
guard=prior.guard
original=prior.original
source=prior.source
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
FALSE=prior.FALSE
validate_profile=prior.validate_profile
PHASE_NAMES=prior.PHASE_NAMES
LABELS=prior.LABELS
MODEL='axial-retained-guarded-unit-new-source-hilo-product-RN64-CPU-point-v1'
FLAG='guarded_source_product_RN64_CPU_executed'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-ARGUMENT-UNIT-RN64-CPU-001-CODEX.json'
PREVIOUS_SHA='e6d311ab43e94b1d94630873e80ade501379e78b13a5a753cb9e29be2f6f3424'
UNIT_NAMES=('coefficient_L1','square_L1','RN_nodes_L1','Taylor_L1')+tuple(n.replace('_rad','_L1') for n in PHASE_NAMES)

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA));require(r['task_id']=='AXIAL-GUARDED-ARGUMENT-UNIT-RN64-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['audit']
    packets,arg,quot,roots,profile,_=prior.load_retained()
    require(set(packets)==set(old['cases']) and profile==old['coefficient_profile'],'same complete retained unit cases')
    return packets,old,arg,quot,roots,profile,pins

def validate_retained_unit(admission,profile,retained):
    require(type(retained['new_RN64_horner_nodes']) is int and retained['new_RN64_horner_nodes']==26,'typed retained node count')
    require(retained['quarter_bit_permutation_executed'] is True and retained['zero_canonicalization_performed'] is False,'typed retained bit policies')
    require(type(retained['point_unit_phase_charge_fits_cap']) is bool,'typed retained phase flag')
    require(type(retained['unchanged_phase_cap_rad']) is list and all(type(t) is int for t in retained['unchanged_phase_cap_rad']),'typed retained cap')
    for name in ('unit_uint64','unpermuted_unit_uint64'):
        require(type(retained[name]) is list and len(retained[name])==2,'two typed retained unit words')
        for w in retained[name]:guard.bits(w,64)
    cap=admission['unchanged_phase_cap_rad'];require(type(cap) is list and cap==[1,10**12] and all(type(t) is int for t in cap),'unchanged phase cap')
    require(admission['coefficient_profile_sha256']==digest(profile),'same coefficient profile');coeff=validate_profile(profile)
    aw=admission['argument_uint64'];Xq=guard.bits(aw,64);X=abs(Xq);k=admission['quadrant_mod4']
    require(type(k) is int and 0<=k<4,'typed quadrant')
    up={n:guard.rational(t) for n,t in admission['upstream_phase_charges_rad'].items()};A=sum(up.values(),F(0))
    require(set(up)==set(PHASE_NAMES) and all(t>=0 for t in up.values()) and guard.rational(admission['upstream_phase_bound_rad'])==A,'seven upstream phase charges')
    require(X+A<1,'unchanged represented angle plus bound domain')
    nodes=[];given=retained['nodes'];require(type(given) is list and len(given)==26,'retained Horner26 length')
    def node(a,b,op,label):
        aq,bq=guard.bits(a,64),guard.bits(b,64);exact=aq*bq if op=='mul' else aq+bq
        zs=(a>>63)^(b>>63) if op=='mul' else int(aq==bq==0 and a>>63==b>>63==1)
        record=given[len(nodes)];w=record['output_uint64'];q=guard.check_RN(exact,w,64,zs);e=abs(q-exact)
        require(record=={'label':label,'op':op,'input_uint64':[a,b],'output_uint64':w,'exact_operation':pair(exact),'signed_RN64_delta':pair(q-exact)},'retained Horner node ledger')
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
    expected={'argument_uint64':aw,'quadrant_mod4':k,'coefficient_profile_sha256':digest(profile),'nodes':nodes,
        'unpermuted_unit_uint64':words,'unit_uint64':unit,'terms':terms,'polynomial_charges_L1':{n:pair(t) for n,t in poly.items()},
        'point_polynomial_L1_bound':pair(B),'point_polynomial_phase_bound_rad':pair(B/(1-B)),
        'unit_L1_charges_to_FIXED_ORIGINAL':{n:pair(t) for n,t in l1.items()},'point_unit_L1_bound_to_FIXED_ORIGINAL':pair(L),
        'phase_charges_to_FIXED_ORIGINAL_rad':{n:pair(t) for n,t in phase.items()},'point_unit_phase_bound_to_FIXED_ORIGINAL_rad':pair(P),
        'unchanged_phase_cap_rad':deepcopy(cap),'point_unit_phase_charge_fits_cap':P<=guard.rational(cap),
        'new_RN64_horner_nodes':26,'quarter_bit_permutation_executed':True,'zero_canonicalization_performed':False,
        'scope':'new CPU Horner26 point on retained guarded scene argument; no SOURCE/material/budgets/full field/whole-domain/physical optics'}
    require(retained==expected,'complete retained unit proof and charges')
    return deepcopy(expected)

def native_cast32(v):return transport.cast32(v)
def native_subtract(a,b):return a-b
def native_add(a,b):return a+b
def native_multiply(a,b):return a*b

def encode_source(words):
    require(type(words) is list and len(words)==2,'two ORIGINAL source words')
    originals=[guard.bits(w,64) for w in words] # ALL input words before first cast
    limbs=[];records=[];sums=[];enc=F(0)
    for w,x in zip(words,originals):
        _,hw=native_cast32(source.value(w,64));h=guard.check_RN(x,hw,32,w>>63)
        rw=source.word(native_subtract(source.value(w,64),source.value(hw,32)))
        exact=x-h;zs=int(x==h==0 and w>>63==1 and hw>>31==0)
        res=guard.check_RN(exact,rw,64,zs)
        _,lw=native_cast32(source.value(rw,64));low=guard.check_RN(res,lw,32,rw>>63)
        represented=h+low;e=abs(represented-x);enc+=e;sums.append(represented);limbs.extend([hw,lw])
        records.append({'original_uint64':w,'high_uint32':hw,'residual_uint64':rw,'low_uint32':lw,
          'exact_residual':pair(exact),'signed_residual_RN64_delta':pair(res-exact),
          'signed_low_RN32_delta':pair(low-res),'represented_sum':pair(represented),'encoding_error_L1':pair(e)})
    raw=struct.pack('<IIII',*limbs)
    return {'ORIGINAL_source_uint64':deepcopy(words),'limb_uint32':limbs,'records':records,
      'hilo_le_base64':base64.b64encode(raw).decode(),'hilo_le_sha256':hashlib.sha256(raw).hexdigest(),
      'exact_limb_sums':list(map(pair,sums)),'source_encoding_error_L1':pair(enc),
      'new_RN32_casts':4,'new_RN64_subtractions':2,'zero_canonicalization_performed':False}

def execute(admission):
    words=admission['ORIGINAL_source_uint64'];require(type(words) is list and len(words)==2,'two source components')
    sq=[guard.bits(w,64) for w in words]
    uw=admission['unit_uint64'];require(type(uw) is list and len(uw)==2,'two retained unit words');u=[guard.bits(w,64) for w in uw]
    charges={n:guard.rational(v) for n,v in admission['unit_L1_charges'].items()};U=sum(charges.values(),F(0))
    require(set(charges)==set(UNIT_NAMES) and all(v>=0 for v in charges.values()) and U==guard.rational(admission['unit_L1_bound']) and U<1,'eleven nonnegative retained unit charges')
    encoder=encode_source(words);limbs=encoder['limb_uint32'];nodes=[]
    def node(a,b,op,label):
        aq,bq=guard.bits(a,64),guard.bits(b,64);exact=aq*bq if op=='mul' else aq+bq
        zs=(a>>63)^(b>>63) if op=='mul' else int(aq==bq==0 and a>>63==b>>63==1)
        v=(native_multiply if op=='mul' else native_add)(source.value(a,64),source.value(b,64))
        w=source.word(v);q=guard.check_RN(exact,w,64,zs)
        nodes.append({'label':label,'op':op,'input_uint64':[a,b],'output_uint64':w,'exact_operation':pair(exact),'signed_RN64_delta':pair(q-exact)})
        return w
    lw=[source.word(source.value(w,32)) for w in limbs] # exact widening, not rounding nodes
    a=node(lw[0],lw[1],'add','decode0');b=node(lw[2],lw[3],'add','decode1')
    ac=node(a,uw[0],'mul','ac');bd=node(b,uw[1],'mul','bd')
    ad=node(a,uw[1],'mul','ad');bc=node(b,uw[0],'mul','bc')
    re=node(ac,bd^(1<<63),'add','real');im=node(ad,bc,'add','imag')
    E=guard.rational(encoder['source_encoding_error_L1']);D=sum((abs(guard.rational(n['signed_RN64_delta'])) for n in nodes[:2]),F(0))
    N=sum((abs(guard.rational(n['signed_RN64_delta'])) for n in nodes[2:]),F(0))
    L=sum(map(abs,u),F(0));S=sum(map(abs,sq),F(0))
    detailed={'source_encoding_L1':E*L,'source_decode_RN64_L1':D*L,**{'source_unit_'+n:S*v for n,v in charges.items()},'source_product_RN64_L1':N}
    B=sum(detailed.values(),F(0));require(B==(E+D)*L+S*U+N and len(detailed)==14,'fourteen source charges')
    ref=[sq[0]*u[0]-sq[1]*u[1],sq[0]*u[1]+sq[1]*u[0]]
    obs=abs(guard.bits(re,64)-ref[0])+abs(guard.bits(im,64)-ref[1])
    require(obs<=(E+D)*L+N,'source product toward ORIGINAL times represented retained unit')
    return {'source_encoder':encoder,'nodes':nodes,'unit_uint64':deepcopy(uw),'decoded_source_uint64':[a,b],
      'product_uint64':[re,im],'ORIGINAL_source_norm_L1':pair(S),'represented_unit_norm_L1':pair(L),
      'observed_error_to_ORIGINAL_times_represented_unit_L1':pair(obs),'detailed_source_charges_L1':{n:pair(v) for n,v in detailed.items()},
      'point_bare_source_bound_to_FIXED_ORIGINAL_L1':pair(B),'new_decode_product_RN64_nodes':8,
      'source_amplitude_budget_admitted':False,'source_phase_bound_proved':False,
      'material_applied':False,'zero_canonicalization_performed':False,
      'scope':'bare source point only; no source allocation/material/group/power/readout/full field/native GPU/RT/physical optics'}

def audit_source_CPU(case_names,*,model):
    require(model==MODEL,'explicit guarded source model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,arg,quot,roots,profile,pins=load_retained();require(set(case_names)<=set(packets),'known cases');admitted=[]
    for name in case_names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context']==arg['cases'][name]['context']==quot['cases'][name]['context']==roots['cases'][name]['context'],'same complete ORIGINAL INPUT')
        snap,meta=original.snapshot_from_packet(packets[name],ctx);rows=old['cases'][name]['sources'];ar=arg['cases'][name]['sources'];qs=quot['cases'][name]['sources'];rs=roots['cases'][name]['sources']
        require(ctx['source_order']==[r['source_id'] for r in rows]==[r['source_id'] for r in ar]==[r['source_id'] for r in qs]==[r['source_id'] for r in rs],'same ordered sources');ads={}
        raw=base64.b64decode(packets[name]['buffers_base64']['sources'],validate=True)
        require(packets[name]['manifest']['layout']['sources']['stride_words']==32 and len(raw)==128*len(rows),'same source INPUT ABI')
        for i,row in enumerate(rows):
            require(type(row[prior.FLAG]) is bool and row[prior.FLAG] is ar[i][prior.prior.FLAG],'same retained eligibility')
            require(row['status']=='STOP' and all(row[n] is False for n in FALSE),'no broad promotion')
            if row[prior.FLAG]:
                require(row['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id'] and row['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id'],'same source gauges')
                a=prior.admit(snap,i,ar[i],qs[i],rs[i]['result'],meta['original_path_phase_caps'][row['source_id']],profile)
                require(a==row['admission'] and row['retained_row_sha256']==digest(ar[i]),'same retained unit admission')
                v=validate_retained_unit(a,profile,row['result']);require(v['point_unit_phase_charge_fits_cap'] is True,'unchanged unit phase cap before source encode')
                field=snap['sources'][i]['field_reim'];require(type(field) is list and len(field)==2,'two ORIGINAL fields')
                for x in field:original.number(x)
                words=[source.word(x) for x in field]
                for w in words:guard.bits(w,64)
                require(raw[128*i+112:128*i+128]==struct.pack('<QQ',*words),'exact original field words/source ABI')
                ads[i]={'source_id':row['source_id'],'ORIGINAL_source_uint64':words,'unit_uint64':deepcopy(v['unit_uint64']),
                  'unit_L1_charges':deepcopy(v['unit_L1_charges_to_FIXED_ORIGINAL']),'unit_L1_bound':deepcopy(v['point_unit_L1_bound_to_FIXED_ORIGINAL']),
                  'retained_unit_row_sha256':digest(row),'phase_reference_id':row['phase_reference_id'],'terminal_reference_id':row['terminal_reference_id']}
        admitted.append((name,ctx,ads))
    cases={};executed=stopped=0
    for name,ctx,ads in admitted:
        rows=[]
        for i,r in enumerate(old['cases'][name]['sources']):
            row={'source_id':r['source_id'],'status':'STOP',FLAG:False,'retained_row_sha256':digest(r),**dict.fromkeys(FALSE,False)}
            if i not in ads:stopped+=1;row.update(reason=r['reason'],reason_provenance='unchanged_retained_STOP')
            else:
                result=execute(ads[i]);executed+=1
                row.update(admission=ads[i],result=result,**{FLAG:True},phase_reference_id=ads[i]['phase_reference_id'],terminal_reference_id=ads[i]['terminal_reference_id'],
                  reason='new source CPU point; INPUT allocations/material/group/power/readout/full field STOP')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
      'new_point_sources_executed':executed,'retained_sources_not_executed':stopped,
      'new_source_RN32_casts':4*executed,'new_source_RN64_subtractions':2*executed,'new_decode_product_RN64_nodes':8*executed,
      'old_native_stages_suites_reexecuted':0,'new_material_group_power_readout_executions':0,
      'cost_scope':'main source casts/subtractions/decode/products counted; HOST pure retained proof and IO/setup unmeasured; upstream retained not zero cost; no equal-work benchmark',
      **dict.fromkeys(FALSE,False)}
