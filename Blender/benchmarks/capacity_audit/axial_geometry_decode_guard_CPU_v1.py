"""Opt-in fail-closed hi-lo record admission before any native CPU geometry decode."""
import base64,hashlib,math,struct
from copy import deepcopy
from fractions import Fraction as F
import axial_geometry_hi_lo_CPU_v1 as prior
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
original=prior.original
source=prior.source
FALSE=prior.FALSE
MODEL='axial-geometry-hilo-typed-RN-midpoint-admission-native-decode-CPU-v1'
FLAG='guarded_native_coordinate_decode_CPU_executed'
PREVIOUS='coordinacion/respuestas/AXIAL-GEOMETRY-HILO-CPU-001-CODEX.json'
PREVIOUS_SHA='818c3e26034bb7dcca90f2bc390497c86ee1625548c50e65e8966fa0e39c0f25'

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-GEOMETRY-HILO-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    raw=io.payload(r);old=raw['data']['audit'];controls=raw['data']['scalar_controls']
    packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases']),'complete cases')
    return packets,old,pins,controls

def bits(word,width,*,normal=True):
    require(type(width) is int and width in (32,64),'word width')
    require(type(word) is int and 0<=word<2**width,'typed unsigned IEEE word')
    frac,exp,bias=(23,8,127) if width==32 else (52,11,1023)
    e=(word>>frac)%(2**exp);m=word%(2**frac)
    require(e<2**exp-1,'finite IEEE word')
    require(not normal or e>0 or m==0,'normal-or-zero selected word')
    return (-1 if word>>(width-1) else 1)*F(m if e==0 else m+2**frac)*F(2)**((1 if e==0 else e)-bias-frac)

def check_RN(q,w,width,zero_sign):
    """Unique RN-even by adjacent-value midpoints, not producer replay."""
    value=bits(w,width);sign=w>>(width-1);magnitude=w%(2**(width-1))
    require(type(zero_sign) is int and zero_sign in (0,1),'zero sign')
    if q==0:
        require(magnitude==0 and sign==zero_sign,'exact-zero IEEE sign')
        return value
    require(sign==int(q<0),'RN sign')
    aq=abs(q)
    if magnitude==0:
        min_subnormal=F(2)**(-149 if width==32 else -1074)
        require(aq<=min_subnormal/2,'RN-zero midpoint')
        return value
    current=abs(value);lower=abs(bits(magnitude-1,width,normal=False))
    frac,exp=(23,8) if width==32 else (52,11)
    max_finite=((2**exp-2)<<frac)|(2**frac-1)
    upper=abs(bits(magnitude+1,width,normal=False)) if magnitude<max_finite else current+(current-lower)
    left,right=(lower+current)/2,(current+upper)/2
    even=magnitude%2==0
    require((aq>left or (even and aq==left)) and (aq<right or (even and aq==right)),'unique RN-even midpoint enclosure')
    return value

def rational(v):
    require(type(v) is list and len(v)==2 and all(type(x) is int for x in v),'typed rational')
    require(v[1]>0 and math.gcd(*v)==1,'canonical rational')
    return F(*v)

def validate_scalar(record,original_word):
    require(type(record) is dict,'scalar record')
    require(type(original_word) is int and record['original_uint64']==original_word,'original bit binding')
    q=bits(record['original_uint64'],64);hw=record['high_uint32'];lw=record['low_uint32']
    high=check_RN(q,hw,32,original_word>>63)
    exact_residual=q-high
    # subtraction is add(x,-high): only two negative zeros produce negative exact zero.
    residual_zero=int(q==high==0 and original_word>>63==1 and hw>>31==0)
    residual=check_RN(exact_residual,record['residual_uint64'],64,residual_zero)
    low=check_RN(residual,lw,32,record['residual_uint64']>>63)
    exact_sum=high+low
    decoded_zero=int(high==low==0 and hw>>31==1 and lw>>31==1)
    decoded=check_RN(exact_sum,record['decoded_uint64'],64,decoded_zero)
    expected={'residual_RN64_delta':residual-exact_residual,'represented_exact_sum':exact_sum,
        'encoding_error_abs':abs(exact_sum-q),'decode_RN64_delta':decoded-exact_sum,
        'decoded_coordinate_error_abs':abs(decoded-q)}
    for k,v in expected.items():require(rational(record[k])==v,'typed exact scalar ledger: '+k)
    return {'original_uint64':original_word,'high_uint32':hw,'residual_uint64':record['residual_uint64'],
        'low_uint32':lw,'decoded_uint64':record['decoded_uint64'],'RN_chain_midpoints_checked':4,
        'scope':'point record admission; no uniform/physical/GPU guard claim'}

def admit(snapshot,index,encoder):
    ps=prior.paths(snapshot,index)
    require(type(encoder) is dict and type(encoder['source_index']) is int and encoder['source_index']==index,'typed source index')
    require(type(encoder['transport_bytes']) is int and encoder['transport_bytes']==8*len(ps),'typed byte count')
    require(encoder['original_snapshot_digest']==digest(snapshot),'original snapshot digest')
    require(type(encoder['records']) is list and len(encoder['records'])==len(ps),'complete records')
    require(encoder['ordered_paths_sha256']==digest(ps),'ordered path digest')
    raw=base64.b64decode(encoder['transport_le_base64'],validate=True)
    require(len(raw)==encoder['transport_bytes'] and hashlib.sha256(raw).hexdigest()==encoder['transport_le_sha256'],'transport bytes/SHA')
    validations=[]
    for j,(p,r) in enumerate(zip(ps,encoder['records'])):
        require(type(r) is dict and type(r['path']) is list and len(r['path'])==len(p)
            and all(type(a) is type(b) and a==b for a,b in zip(r['path'],p)),'typed complete ordered path')
        w=source.word(prior.get(snapshot,p));v=validate_scalar(r,w)
        require(struct.unpack_from('<II',raw,8*j)==(v['high_uint32'],v['low_uint32']),'serialized limb binding')
        validations.append(v)
    return validations

def native_add(high_word,low_word):
    a,b=source.value(high_word,32),source.value(low_word,32)
    out=a+b;original.number(out)
    return out

def decode_guarded(snapshot,index,encoder):
    # Atomic preflight: all records valid BEFORE the first new native decode add.
    checks=admit(snapshot,index,encoder);out=deepcopy(snapshot);nodes=[]
    for p,v in zip(prior.paths(snapshot,index),checks):
        decoded=native_add(v['high_uint32'],v['low_uint32'])
        require(source.word(decoded)==v['decoded_uint64'],'native RN64 decode differs from admitted word STOP')
        nodes.append({'path':p,'input_uint32':[v['high_uint32'],v['low_uint32']],'output_uint64':source.word(decoded)})
        prior.put(out,p,decoded)
    return out,{'record_admission':checks,'native_decode_nodes':nodes,'all_records_admitted_before_first_native_add':True,
        'new_native_RN64_decode_adds':len(nodes),'new_encoding_casts_subtractions':0,'decoded_snapshot_digest':digest(out)}

def audit_guard_CPU(case_names,*,model):
    require(model==MODEL,'explicit guard model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,pins,_=load_retained();require(set(case_names)<=set(packets),'known cases')
    probe=prior.prior.runtime_probe();require(probe['PASS'] is True,'runtime guard FAIL before admission/decode')
    cases={};executed=stopped=nodes=0
    for name in case_names:
        packet=packets[name];ctx=allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context'],'same complete INPUT')
        snap,_=original.snapshot_from_packet(packet,ctx);rows=[]
        require([r['source_id'] for r in old['cases'][name]['sources']]==ctx['source_order'],'complete source order')
        for i,r in enumerate(old['cases'][name]['sources']):
            row={'source_id':r['source_id'],'status':'STOP',FLAG:False,'retained_geometry_row_sha256':digest(r),**dict.fromkeys(FALSE,False)}
            if not r[prior.FLAG]:
                stopped+=1;row.update(reason=r['reason'],reason_provenance='unchanged_retained_STOP')
            else:
                decoded,proof=decode_guarded(snap,i,r['encoder'])
                require(digest(decoded)==r['decoded_snapshot_digest'],'same honest decoded scene')
                row.update(guarded_decode=proof,transport_sha256=r['encoder']['transport_le_sha256'],**{FLAG:True},
                    reason='record admission and new native coordinate decode only; previous point bounds retained, not re-proved by native traversal')
                executed+=1;nodes+=len(proof['native_decode_nodes'])
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'runtime_probe':probe,'inherited_pins_verified':len(pins),
        'guarded_sources_executed':executed,'retained_sources_not_executed':stopped,'new_native_decode_adds':nodes,
        'new_encoder_casts_subtractions':0,'new_ray_argument_Horner_SOURCE_material_reduction_power_readout_executions':0,
        'previous_SOURCE_eight_bit_FAILs_preserved':True,'previous_SOURCE_twelve_zero_sign_mismatches_preserved':True,
        'native_ray_arithmetic_executed':False,'GPU_job_admission_guard':False,
        'cost_scope':'one RN64 native decode add per accepted coordinate; rational midpoint admission present/unmeasured; runtime6ops64+4casts32; IO/pins/setup/remaining UNMEASURED never zero',
        **dict.fromkeys(FALSE,False)}
