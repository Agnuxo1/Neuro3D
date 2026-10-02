import struct
"""Independent integer IEEE RN64 oracle; no production imports or float arithmetic replay."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-GEOMETRY-DECODE-GUARD-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-GEOMETRY-HILO-CPU-001-CODEX.json'
PREVIOUS_SHA='818c3e26034bb7dcca90f2bc390497c86ee1625548c50e65e8966fa0e39c0f25'
FLAG='guarded_native_coordinate_decode_CPU_executed'
SOURCE_FLAG='restricted_nonzero_bare_source_error_to_fixed_ORIGINAL_bound_proved'
MODEL='axial-geometry-hilo-typed-RN-midpoint-admission-native-decode-CPU-v1'
LABELS=['decode0','decode1','ac','bd','ad','bc','real','imag']
SIGN=2**63
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(path,h):
    raw=(ROOT/path).read_bytes();assert sha(raw)==h,path;return json.loads(raw)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def payload(r):
    t=r['test_run'];assert t['rc']==0
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def pair(q):return [q.numerator,q.denominator]
def rational(v):
    assert type(v) is list and len(v)==2 and all(type(x) is int for x in v)
    assert v[1]>0 and math.gcd(*v)==1;return F(*v)
def bits(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)%2048;m=w%2**52;assert e<2047
    return (-1 if w&SIGN else 1)*F(m if e==0 else m+2**52)*F(2)**((1 if e==0 else e)-1075)
def lift32(w):
    assert type(w) is int and 0<=w<2**32
    sign=(w>>31)<<63;e=(w>>23)%256;m=w%2**23
    assert e<255 and (e or m==0)
    return sign if e==0 else sign|((e+896)<<52)|(m<<29)
def round64(q,zero_sign):
    if q==0:return zero_sign
    sign=SIGN if q<0 else 0;n,d=abs(q.numerator),q.denominator
    e=n.bit_length()-d.bit_length()
    if (n<d<<e if e>=0 else n<<-e<d):e-=1
    assert e<=1023
    grid=max(e,-1022)-52
    nn,dd=(n,d<<grid) if grid>=0 else (n<<-grid,d)
    m,rem=divmod(nn,dd);m+=int(2*rem>dd or (2*rem==dd and m&1))
    if m==0:return sign
    if e<-1022:
        assert m<=2**52
        return sign|m  # m==2^52 correctly reaches smallest normal
    if m==2**53:m>>=1;e+=1
    assert e<=1023 and 2**52<=m<2**53
    return sign|((e+1023)<<52)|(m-2**52)
def operation(x,y,kind):
    a,b=bits(x),bits(y);q=a*b if kind=='mul' else a+b
    if kind=='mul':zs=(x^y)&SIGN
    else:zs=SIGN if a==b==0 and x&SIGN and y&SIGN else 0
    return round64(q,zs),q

def round32(q,zero_sign):
    if q==0:return zero_sign
    sign=(1<<31) if q<0 else 0;n,d=abs(q.numerator),q.denominator
    e=n.bit_length()-d.bit_length()
    if (n<d<<e if e>=0 else n<<-e<d):e-=1
    assert e<=127
    grid=max(e,-126)-23
    nn,dd=(n,d<<grid) if grid>=0 else (n<<-grid,d)
    m,rem=divmod(nn,dd);m+=int(2*rem>dd or (2*rem==dd and m&1))
    if m==0:return sign
    if e<-126:
        assert m<=2**23;return sign|m
    if m==2**24:m>>=1;e+=1
    assert e<=127 and 2**23<=m<2**24
    return sign|((e+127)<<23)|(m-2**23)

def word(v):return struct.unpack('<Q',struct.pack('<d',v))[0]
def verify_scalar(t,w):
    q=bits(w);hw=round32(q,(w>>32)&(1<<31))
    residual,rexact=operation(w,lift32(hw)^SIGN,'add')
    lw=round32(bits(residual),(residual>>32)&(1<<31))
    dec,decexact=operation(lift32(hw),lift32(lw),'add')
    expected={'original_uint64':w,'high_uint32':hw,'residual_uint64':residual,'low_uint32':lw,'decoded_uint64':dec,
        'residual_RN64_delta':pair(bits(residual)-rexact),'represented_exact_sum':pair(decexact),
        'encoding_error_abs':pair(abs(decexact-q)),'decode_RN64_delta':pair(bits(dec)-decexact),
        'decoded_coordinate_error_abs':pair(abs(bits(dec)-q))}
    assert t==expected
    return dec,hw,lw

def get(obj,path):
    for k in path:obj=obj[k]
    return obj
def put(obj,path,value):
    for k in path[:-1]:obj=obj[k]
    obj[path[-1]]=value
def expected_paths(snapshot,index):
    ps=[]
    for name in ('M','D'):
        ps.extend([['objects',name,'vertices_world_BU',j,k] for j in range(len(snapshot['objects'][name]['vertices_world_BU'])) for k in range(3)])
    ps.extend([['sources',index,key,k] for key in ('position_BU','direction') for k in range(3)])
    ps.extend([['objects','D',key,k] for key in ('mode_origin_BU','mode_direction') for k in range(3)])
    return ps+[['lambda_BU'],['objects','M','phase_rad']]
def decode(snapshot,index,enc):
    ps=expected_paths(snapshot,index);assert len(ps)==38
    assert enc['source_index']==index and enc['original_snapshot_digest']==digest(snapshot)
    assert enc['ordered_paths_sha256']==digest(ps) and [t['path'] for t in enc['records']]==ps
    dec=json.loads(json.dumps(snapshot));limbs=[]
    for p,t in zip(ps,enc['records']):
        s={k:v for k,v in t.items() if k!='path'}
        w,h,l=verify_scalar(s,word(get(snapshot,p)));limbs.extend((h,l))
        put(dec,p,struct.unpack('<d',struct.pack('<Q',w))[0])
    raw=struct.pack('<'+'I'*len(limbs),*limbs)
    assert enc['transport_bytes']==len(raw)==304
    assert enc['transport_le_sha256']==sha(raw) and enc['transport_le_base64']==base64.b64encode(raw).decode()
    assert enc['new_RN32_casts']==76 and enc['new_RN64_subtractions']==enc['new_RN64_decode_adds']==38
    return dec

def allfalse(v):
    for k in false:assert v[k] is False,k
def capture(t):
    raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert sha(raw)==t['stdout_sha256'] and len(raw)==t['stdout_bytes']
    assert t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and not t['timed_out'] and t['elapsed_seconds']<60
    return json.loads(raw)
def validation(record):
    return {k:record[k] for k in ('original_uint64','high_uint32','residual_uint64','low_uint32','decoded_uint64')}|{
        'RN_chain_midpoints_checked':4,'scope':'point record admission; no uniform/physical/GPU guard claim'}

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-GEOMETRY-DECODE-GUARD-CPU-001'
assert r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r);assert len(pins)==342 and len(r['own_code_doc_sha256'])==4
for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
prev=read(PREVIOUS,PREVIOUS_SHA);false=tuple(prev['proof_scope']);allfalse(r['proof_scope'])
pr=payload(prev);old=pr['data']['audit']
def data(p):return payload(read(p,pins[p]))
legacy=data('coordinacion/respuestas/AXIAL-SOURCE-FLOAT64-STAGE-CPU-001-CODEX.json')['data']['audit']
assert legacy['point_graphs_bits_FAIL']==8 and legacy['point_graphs_bits_MATCH']==0
assert sum(n['zero_sign_only_mismatch'] for c in legacy['cases'].values() for s in c['sources'] for p in s.get('points',[]) for n in p['nodes'])==12
packets=data('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json')['packets']
packets.update({n:v['parent'] for n,v in data('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json')['synthetic_controls'].items()})
raw=capture(r['test_run']);assert r['test_run']['rc']==0 and raw['PASS'] is True and raw['tests']==4
a=raw['data']['audit'];allfalse(a);assert a['model']==MODEL and a['case_order']==old['case_order'] and len(a['cases'])==17
assert a['runtime_probe']==old['runtime_probe'] and a['runtime_probe']['PASS'] is True
ex=stop=adds=0
for name in a['case_order']:
    case=a['cases'][name];allfalse(case);ctx=case['context'];p=packets[name]
    assert ctx==old['cases'][name]['context'] and digest(p)==ctx['input_packet_sha256']
    b={k:base64.b64decode(v,validate=True) for k,v in p['buffers_base64'].items()}
    for k,v in b.items():assert p['manifest']['buffers'][k]=={'bytes':len(v),'sha256':sha(v)}
    assert sha(b['original_scene_json'])==ctx['original_snapshot_sha256']
    snap=json.loads(b['original_scene_json'])
    assert [s['id'] for s in snap['sources']]==ctx['source_order']==[s['source_id'] for s in case['sources']]
    for i,(row,prior) in enumerate(zip(case['sources'],old['cases'][name]['sources'])):
        allfalse(row);assert row['status']=='STOP' and row['retained_geometry_row_sha256']==digest(prior)
        if not prior['decoded_geometry_point_CPU_executed']:
            stop+=1;assert row[FLAG] is False and 'guarded_decode' not in row
            assert row['reason']==prior['reason'] and row['reason_provenance']=='unchanged_retained_STOP';continue
        assert row[FLAG] is True
        enc=prior['encoder'];dec=decode(snap,i,enc);v=row['guarded_decode']
        assert digest(dec)==prior['decoded_snapshot_digest']==v['decoded_snapshot_digest']
        assert row['transport_sha256']==enc['transport_le_sha256']
        assert v['record_admission']==[validation(t) for t in enc['records']]
        assert v['all_records_admitted_before_first_native_add'] is True
        assert v['new_encoding_casts_subtractions']==0 and v['new_native_RN64_decode_adds']==len(v['native_decode_nodes'])==38
        for t,n in zip(enc['records'],v['native_decode_nodes']):
            out,_=operation(lift32(t['high_uint32']),lift32(t['low_uint32']),'add')
            assert n=={'path':t['path'],'input_uint32':[t['high_uint32'],t['low_uint32']],'output_uint64':out}
            assert out==t['decoded_uint64']
        ex+=1;adds+=len(v['native_decode_nodes'])
assert (ex,stop,adds)==(2,17,76) and a['inherited_pins_verified']==338
assert a['guarded_sources_executed']==2 and a['retained_sources_not_executed']==17 and a['new_native_decode_adds']==76
assert a['new_encoder_casts_subtractions']==a['new_ray_argument_Horner_SOURCE_material_reduction_power_readout_executions']==0
assert a['native_ray_arithmetic_executed'] is a['GPU_job_admission_guard'] is False
assert a['previous_SOURCE_eight_bit_FAILs_preserved'] is a['previous_SOURCE_twelve_zero_sign_mismatches_preserved'] is True

# Forgery is internally ledger-consistent, but NOT RN64; old honest point proof remains unchanged.
control=raw['data']['forged_decode_control'];enc=control['encoder']
honest=old['cases']['thin_resolved']['sources'][0]['encoder'];assert enc.keys()==honest.keys()
expected=json.loads(json.dumps(honest));t=expected['records'][0];t['decoded_uint64']+=1
q=bits(t['original_uint64']);sm=rational(t['represented_exact_sum']);dq=bits(t['decoded_uint64'])
t['decode_RN64_delta']=pair(dq-sm);t['decoded_coordinate_error_abs']=pair(abs(dq-q))
assert enc==expected
true_word,_=operation(lift32(t['high_uint32']),lift32(t['low_uint32']),'add')
assert true_word!=t['decoded_uint64']
snap=json.loads(base64.b64decode(packets['thin_resolved']['buffers_base64']['original_scene_json']))
for t in enc['records']:put(snap,t['path'],struct.unpack('<d',struct.pack('<Q',t['decoded_uint64']))[0])
assert digest(snap)==control['forged_decoded_snapshot_digest']
assert control['old_deserializer_accepted'] is control['old_point_audit_not_reexecuted_or_invalidated'] is control['new_guard_rejected'] is True
assert control['new_native_adds_before_rejection']==0 and 'RN-even' in control['reason']
controls=raw['data']['scalar_admission_controls'];assert len(controls)==4
for c,prior in zip(controls,pr['data']['scalar_controls']):
    assert c['record']==prior and c['validation']==validation(prior);verify_scalar(prior,prior['original_uint64'])
rejects=raw['data']['rejections'];assert len(rejects)==len({v['label'] for v in rejects})==26
assert all(v['native_adds_before_rejection']==0 for v in rejects)
assert {'last_record_forged','runtime_FAIL','stale_INPUT','predecessor_SHA','path_bool','charge_bool'}<={v['label'] for v in rejects}
mid=raw['data']['midpoint_controls'];assert mid['even_tie_accepted'] is mid['odd_tie_rejected'] is True
assert [v['label'] for v in mid['rejects']]==['tie_odd','zero_wrong_sign','zero_above_midpoint']
assert round32(F(1)+F(1,2**24),0)==0x3f800000
first=r['preserved_initial_test_failure']['run'];assert first['rc']==1 and 'forge' in first['stderr'] and 'normal-or-zero' in first['stderr']
failed=capture(first);assert failed['PASS'] is False and failed['tests']==4
assert failed['data']['audit']==a and failed['data']['forged_decode_control']==control and failed['data']['rejections']==[]
assert r['preserved_initial_test_failure']['production_changed_to_fix_failure'] is False
print(json.dumps({'PASS':True,'pins':342,'guarded_sources':2,'native_decode_adds_checked':76,
    'retained_sources_not_executed':17,'self_consistent_forgery_rejected_before_any_add':True,
    'atomic_rejections':26,'midpoint_rejections':3,'signed_zero_scalar_controls':4,
    'initial_fixture_failure_preserved':True,'legacy_8_FAIL_12_signs_preserved':True,
    'new_ray_Horner_SOURCE_GPU_executions':0},sort_keys=True))
