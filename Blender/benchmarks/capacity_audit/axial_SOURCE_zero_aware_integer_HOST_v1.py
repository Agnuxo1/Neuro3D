"""CPU uint32 mirror of new GLSL helper. Not compilation or GPU evidence."""
import base64,hashlib,importlib.util,json,zlib
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL='axial-SOURCE-zero-aware-integer-words-GLSL-v1'
SHADER='Blender/benchmarks/capacity_audit/axial_SOURCE_zero_aware_integer_v1.glsl'
SHADER_SHA='088c2b8716664494a6d4a8a6358279d017618f25ae03171608b95b1b8fb9242a'
DEP='Blender/benchmarks/capacity_audit/axial_native_signed512_v1.py'
DEP_SHA='6d77bcf7e440d8619b255660efb0117c3adc66d8e027fc6a331bc9558016104f'
DEP_GLSL='Blender/benchmarks/capacity_audit/axial_native_signed512_v1.glsl'
DEP_GLSL_SHA='e1f2ff0ca905ee29e8afa0440e9abdaa4a4127be23fe20d29e29c25af68f236f'
PARENT='coordinacion/respuestas/AXIAL-TAGGED-SOURCE-UNIT-MATERIAL-LINK-HOST-001-CODEX.json'
PARENT_SHA='277ac37756babcb917fe5d019ce5d86249f9280b7d8920f056815b5812222a44'
MASK=(1<<32)-1
def require(ok,msg):
    if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def source_lock(raw):
    require(type(raw) is bytes and sha(raw)==SHADER_SHA,'exact new shader source; NOT compiler proof')
for path,h in [(DEP,DEP_SHA),(DEP_GLSL,DEP_GLSL_SHA)]:require(sha((ROOT/path).read_bytes())==h,'frozen integer dependency')
spec=importlib.util.spec_from_file_location('_source_integer_frozen_word_core',ROOT/DEP)
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
# Only pure word decode/add/negate helpers below. No x_enclosures, old tests or producers.
def selected(w):
    require(type(w) is int and 0<=w<=MASK,'strict uint32')
    e=(w>>23)&255;m=w&0x7fffff
    require(e!=255 and (e!=0 or m==0),'finite normal-or-zero')
def bit(mag,pos):return (mag[pos//32]>>(pos%32))&1
def round_mag(mag,sign):
    prior.valid(mag);require(type(sign) is int and sign in (0,1<<31) and not prior.negative(mag),'nonnegative selected magnitude/sign')
    top=-1
    for pos in range(511,-1,-1):
        if bit(mag,pos):top=pos;break
    require(top<=277,'sum of two selected binary32 magnitude range')
    if top<0:return [0,sign],{'round_up':False,'renormalized':False,'top':-1}
    lo=hi=0
    for j in range(53):
        src=top-j;dst=52-j;b=bit(mag,src) if src>=0 else 0
        if dst<32:lo|=b<<dst
        else:hi|=b<<(dst-32)
    cut=top-52;up=False;renorm=False
    if cut>0:
        half=bool(bit(mag,cut-1));sticky=False
        for pos in range(cut-1):
            if bit(mag,pos):sticky=True
        up=half and (sticky or bool(lo&1))
    if up:
        old=lo;lo=(lo+1)&MASK
        if lo<old:hi=(hi+1)&MASK
        if hi&0x00200000:
            lo=((lo>>1)|(hi<<31))&MASK;hi>>=1;top+=1;renorm=True
    return [lo,sign|((top+874)<<20)|(hi&0xfffff)],{'round_up':up,'renormalized':renorm,'top':top}
def decode_words(limbs,*,model):
    require(type(model) is str and model==MODEL,'explicit NEW integer graph')
    require(type(limbs) is list and len(limbs)==2,'two limb words')
    for w in limbs:selected(w) # BOTH before any frozen decode.
    if all((w&0x7fffffff)==0 for w in limbs):
        words=[0,limbs[0]&0x80000000];detail={'round_up':False,'renormalized':False,'top':-1};branch='BOTH_ZERO_HIGH_SIGN'
    else:
        total=prior.decode_hilo(limbs);sign=(1<<31) if prior.negative(total) else 0
        mag=prior.negate_mod(total) if sign else total
        words,detail=round_mag(mag,sign);branch='INTEGER_RN_EVEN_TO_WORD64'
    return {'limb_uint32':deepcopy(limbs),'decoded_low_high_uint32':words,'decoded_uint64':words[0]|(words[1]<<32),
            'branch':branch,'rounding_detail':detail,'native_FP_operations':0,'GLSL_compiled':False,'GPU_executed':False}
def value(w,width):
    mb,eb,bias=(23,8,127) if width==32 else (52,11,1023)
    e=(w>>mb)&((1<<eb)-1);m=w&((1<<mb)-1)
    return (-1 if w>>(width-1) else 1)*F(m if e==0 else m+(1<<mb))*F(2)**((e or 1)-bias-mb)
def payload(r):
    t=r['test_run'];s=t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(s,validate=True));require(len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'],'lossless')
    return json.loads(b)['data']
def load_retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,'parent SHA')
    r=json.loads(raw);pins={**r['code_doc_sha256'],PARENT:PARENT_SHA}
    require(len(pins)==538,'full lineage')
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,'sealed '+p)
    source_lock((ROOT/SHADER).read_bytes())
    d=payload(r);a=d['request']['A_POINT_INPUT'];inp=a['transport_INPUT'];out=a['transport_OUTPUT']
    require(len(r['proof_scope'])==38 and all(v is False for v in r['proof_scope'].values()),'general STOP')
    return inp,out,pins,r['proof_scope']
def make_request():
    inp,_,_,_=load_retained()
    return {'model':MODEL,'shader_sha256':SHADER_SHA,'signed512_shader_sha256':DEP_GLSL_SHA,
            'execution_backend':'CPU_UINT32_MIRROR_NOT_GLSL','upstream_transport_INPUT':deepcopy(inp)}
def audit(request,*,model):
    require(type(model) is str and model==MODEL,'explicit integer helper')
    inp,out,pins,false=load_retained()
    if request is None:return {'model':MODEL,'sources':[],'missing_cases':17,'missing_sources':19,'group_admissions':0,'proof_scope':deepcopy(false),'GLSL_compiled':False,'GPU_executed':False,'status':'STOP'}
    require(type(request) is dict and set(request)=={'model','shader_sha256','signed512_shader_sha256','execution_backend','upstream_transport_INPUT'},'exact changed graph INPUT')
    require(request['model']==MODEL and request['shader_sha256']==SHADER_SHA and request['signed512_shader_sha256']==DEP_GLSL_SHA and request['execution_backend']=='CPU_UINT32_MIRROR_NOT_GLSL','new selector; not old CPU decoder/backend equivalence')
    require(digest(request['upstream_transport_INPUT'])==digest(inp),'same COMPLETE upstream program/context/ORIGINAL/gauges/frames')
    staged=inp['decoder_INPUT']['SOURCE_limb_records']
    require(len(staged)==len(out['sources'])==4,'complete SOURCE order')
    for row in staged:
        for w in row['limb_uint32']:selected(w)
    results=[]
    for row,old in zip(staged,out['sources']):
        limbs=row['limb_uint32'];scalars=[decode_words(limbs[i:i+2],model=MODEL) for i in (0,2)]
        words=[s['decoded_uint64'] for s in scalars]
        require(words==old['decoded_SOURCE_uint64'],'CPU integer mirror equals retained zero-aware OUTPUT bits, not GPU proof')
        errors=[abs(value(s['decoded_uint64'],64)-sum((value(w,32) for w in s['limb_uint32']),F(0))) for s in scalars]
        results.append({'case_name':row['case_name'],'source_id':row['source_id'],'encoder_row_sha256':digest(row),
                        'context_sha256':row['context_sha256'],'frame_sha256':old['frame_sha256'],'scalars':scalars,
                        'decoder_rounding_errors_abs':[[q.numerator,q.denominator] for q in errors],
                        'retained_zero_aware_OUTPUT_bits_match_CPU_mirror':True,
                        'whole_box_guard_admission_disproved':row['retained_whole_box_guard_admission_disproved'],'status':'STOP'})
    return {'model':MODEL,'sources':results,'request_sha256':digest(request),'inherited_pins_verified':len(pins),
            'new_CPU_integer_decodes':8,'native_FP_operations':0,'group_admissions':0,'proof_scope':deepcopy(false),
            'GLSL_compiled':False,'GPU_executed':False,'scene_or_program_execution_authenticated':False,
            'shader_integrated_into_runner':False,'phase_bound_rad':None,'phase_quota_fits':None,'uniform_SOURCE_error_L1':None,'status':'STOP'}
