"""Independent rational oracle and frozen/source ledger inspection; no production imports."""
import base64,hashlib,json,zlib,re
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=R/'coordinacion/respuestas/AXIAL-SOURCE-ZERO-AWARE-INTEGER-GLSL-001-CODEX.json'
def h(b):return hashlib.sha256(b).hexdigest()
def dig(v):return h(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def data(r):
 t=r['test_run'];s=t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']);b=zlib.decompress(base64.b64decode(s,validate=True))
 assert len(b)==t['stdout_bytes'] and h(b)==t['stdout_sha256'];v=json.loads(b);assert v['errors']==v['failures']==0;return v['data']
def value(w,width):
 assert type(w) is int and 0<=w<1<<width;mb,eb,bias=(23,8,127) if width==32 else (52,11,1023)
 e=w>>mb&((1<<eb)-1);m=w&((1<<mb)-1);assert e<(1<<eb)-1 and (e or m==0)
 return (-1 if w>>(width-1) else 1)*F(m+(1<<mb) if e else m)*F(2)**((e or 1)-bias-mb)
def check_scalar(s):
 limbs=s['limb_uint32'];exact=sum((value(w,32) for w in limbs),F(0));word=s['decoded_uint64'];rounded=value(word,64)
 assert s['decoded_low_high_uint32']==[word&0xffffffff,word>>32]
 assert s['native_FP_operations']==0 and s['GLSL_compiled'] is False and s['GPU_executed'] is False
 if all(w&0x7fffffff==0 for w in limbs):
  assert word==(limbs[0]>>31)<<63 and s['branch']=='BOTH_ZERO_HIGH_SIGN';return
 assert s['branch']=='INTEGER_RN_EVEN_TO_WORD64'
 if exact==0:assert word==0;return
 assert word>>63==int(exact<0)
 magnitude=word&((1<<63)-1)
 # Adjacent-value midpoints, a different oracle than production's guard/sticky graph.
 lower=(abs(value(magnitude-1,64))+abs(rounded))/2
 upper=(abs(value(magnitude+1,64))+abs(rounded))/2
 even=not magnitude&1;target=abs(exact)
 assert (target>lower or even and target==lower) and (target<upper or even and target==upper)
r=json.loads(P.read_bytes());pins=r['code_doc_sha256'];assert len(pins)==543
for p,s in pins.items():assert h((R/p).read_bytes())==s,p
d=data(r);a=d['audit'];assert a['new_CPU_integer_decodes']==8 and len(a['sources'])==4 and a['group_admissions']==0
assert len(a['proof_scope'])==38 and all(v is False for v in a['proof_scope'].values())
for k in ['GLSL_compiled','GPU_executed','scene_or_program_execution_authenticated','shader_integrated_into_runner']:assert a[k] is False
assert a['phase_bound_rad'] is None and a['phase_quota_fits'] is None and a['uniform_SOURCE_error_L1'] is None
parent=data(json.loads((R/'coordinacion/respuestas/AXIAL-TAGGED-SOURCE-UNIT-MATERIAL-LINK-HOST-001-CODEX.json').read_bytes()))
up=parent['request']['A_POINT_INPUT']['transport_INPUT'];old=parent['request']['A_POINT_INPUT']['transport_OUTPUT']
assert dig(d['request']['upstream_transport_INPUT'])==dig(up) and d['request']['execution_backend']=='CPU_UINT32_MIRROR_NOT_GLSL'
for i,row in enumerate(a['sources']):
 src=up['decoder_INPUT']['SOURCE_limb_records'][i]
 assert (row['case_name'],row['source_id'])==(src['case_name'],src['source_id'])
 assert row['encoder_row_sha256']==dig(src) and row['context_sha256']==src['context_sha256'] and row['frame_sha256']==old['sources'][i]['frame_sha256']
 assert [s['decoded_uint64'] for s in row['scalars']]==old['sources'][i]['decoded_SOURCE_uint64']
 for j,s in enumerate(row['scalars']):
  check_scalar(s);exact=sum((value(w,32) for w in s['limb_uint32']),F(0))
  assert s['limb_uint32']==src['limb_uint32'][2*j:2*j+2]
  assert F(*row['decoder_rounding_errors_abs'][j])==abs(value(s['decoded_uint64'],64)-exact)
for v in d['controls']:check_scalar(v['result'])
assert len(d['controls'])==20 and len(d['input_rejections'])==8 and len(d['word_rejections'])==20
assert all(x['rejected'] is True and x['new_decode_calls']==0 for x in d['input_rejections'])
assert all(x['rejected'] is True and x['frozen_decode_calls']==0 for x in d['word_rejections'])
assert len(d['source_rejections'])==5 and d['range_rejections']==4 and d['model_rejections']==3
raw=(R/'Blender/benchmarks/capacity_audit/axial_SOURCE_zero_aware_integer_v1.glsl').read_text()
clean=re.sub(r'//[^\n]*','',raw)
assert not re.search(r'\b(float|double|main|layout|packDouble2x32|unpackDouble2x32)\b',clean)
assert '#error frozen_signed512_header_required_first' in raw
assert raw.index('!exp005_source_word32_selected_v1(limbs.y)')<raw.index('exp005_decode_hilo512(limbs,sum)')
assert 'words=uvec2(0u,limbs.x&0x80000000u); return true;' in raw
assert 'guardBit && (sticky || (sig.x&1u)!=0u)' in raw
assert not re.search(r'\b(half|fixed|short|long|unsigned|input|output)\b',clean)
assert '(uint(top+874)<<20u)' in raw and 'if(top>277) return false;' in raw
print(json.dumps({'PASS':True,'pins':len(pins),'CPU_mirror_controls':20,'CPU_mirror_scene_scalars':8,'GLSL_compiled':False,'GPU_executed':False,'general_scene_admissions':0}))
