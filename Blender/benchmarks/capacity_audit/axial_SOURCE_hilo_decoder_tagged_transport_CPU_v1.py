"""New tagged in-memory SOURCE transport; legacy raw limbs never autodetect a decoder."""
import base64
import hashlib
import importlib.util
import json
import struct
import zlib
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL='axial-SOURCE-hilo-explicit-decoder-tagged-transport-CPU-v1'
FLAG='new_tagged_SOURCE_transport_CPU_executed'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-HILO-ZERO-AWARE-DECODER-CPU-001-CODEX.json'
PARENT_SHA='cdc087122428816680b9ebc98b02c51acab946bfe8682939f2fb6ce7b88800ba'
DECODER='Blender/benchmarks/capacity_audit/axial_SOURCE_hilo_zero_aware_decoder_CPU_v1.py'
DECODER_SHA='9f22f2c7709360b61a1d0765cf9776af47a2306efd8c1c61bfbd09a12077ef03'
MAGIC=b'N3DZAD01'
FRAME_BYTES=120
HEADER_BYTES=104
LAYOUT='LE-u32-realhigh-reallow-imaghigh-imaglow'
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def hash_bytes(v):
    require(type(v) is str and len(v)==64 and all(c in '0123456789abcdef' for c in v),'strict lowercase SHA256')
    return bytes.fromhex(v)
def canonical_base64(v):
    require(type(v) is str,'typed base64')
    try:b=base64.b64decode(v,validate=True)
    except (ValueError,base64.binascii.Error) as e:raise ValueError('strict base64') from e
    require(base64.b64encode(b).decode()==v,'canonical base64')
    return b
def sealed(p,h):
    b=(ROOT/p).read_bytes();require(sha(b)==h,'sealed '+p);return b
# Only our already-committed passive decoder module; no encoder/foreign writer import.
sealed(DECODER,DECODER_SHA)
spec=importlib.util.spec_from_file_location('own_zero_decoder_transport',ROOT/DECODER)
decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
def selection():
    return {'model':decoder.MODEL,'implementation_sha256':DECODER_SHA,'parent_receipt_sha256':PARENT_SHA,
            'payload_layout':LAYOUT,'envelope_magic_hex':MAGIC.hex()}
def payload(r):
    t=r['test_run'];v=t.get('stdout_zlib_base64')
    if v is None:v=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    require(len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'],'lossless retained payload')
    return json.loads(b)
def load_retained():
    parent=json.loads(sealed(PARENT,PARENT_SHA))
    require(parent['task_id']=='AXIAL-SOURCE-HILO-ZERO-AWARE-DECODER-CPU-001' and parent['model']==decoder.MODEL,'parent ID/model')
    pins={**parent['code_doc_sha256'],PARENT:PARENT_SHA}
    require(len(pins)==523 and pins[DECODER]==DECODER_SHA,'complete same decoder pins')
    for p,h in pins.items():sealed(p,h)
    data=payload(parent)['data'];false=parent['proof_scope']
    require(len(false)==38 and all(v is False for v in false.values()),'frozen general STOP')
    require(data['audit']['group_admissions']==0,'no parent admission')
    return data,pins,false
def frame_SOURCE(raw_payload,context_sha256,source_row_sha256):
    require(type(raw_payload) is bytes and len(raw_payload)==16,'strict sixteen-byte SOURCE payload')
    # Selected normal-or-zero limbs checked before creating a new frame.
    for w in struct.unpack('<IIII',raw_payload):decoder.word_value(w,32)
    return MAGIC+hash_bytes(DECODER_SHA)+hash_bytes(context_sha256)+hash_bytes(source_row_sha256)+raw_payload
def inspect_FRAME(frame,context_sha256,source_row_sha256):
    require(type(frame) is bytes and len(frame)==FRAME_BYTES,'strict tagged frame length; not legacy raw ABI')
    require(frame[:8]==MAGIC and frame[8:40]==hash_bytes(DECODER_SHA),'explicit zero-aware decoder tag and implementation SHA')
    require(frame[40:72]==hash_bytes(context_sha256) and frame[72:104]==hash_bytes(source_row_sha256),'same context/ORIGINAL SOURCE ledger')
    raw=frame[104:];words=struct.unpack('<IIII',raw)
    for w in words:decoder.word_value(w,32)
    return list(words)
def make_synthetic_request():
    data,_,_=load_retained();dinput=deepcopy(data['request'])
    program={'model':MODEL,'decoder_selection':selection(),'decoder_INPUT_sha256':digest(dinput)}
    frames=[]
    for row in dinput['SOURCE_limb_records']:
        raw=canonical_base64(row['hilo_le_base64'])
        frame=frame_SOURCE(raw,row['context_sha256'],digest(row))
        frames.append({'case_name':row['case_name'],'source_id':row['source_id'],
                       'frame_base64':base64.b64encode(frame).decode()})
    return {'model':MODEL,'program_INPUT':program,'decoder_INPUT':dinput,'frames':frames}
def prepare_all(request,data):
    require(type(request) is dict and set(request)=={'model','program_INPUT','decoder_INPUT','frames'},'exact transport request')
    require(type(request['model']) is str and request['model']==MODEL,'explicit transport MODEL')
    dinput=request['decoder_INPUT']
    require(type(dinput) is dict and digest(dinput)==digest(data['request']),'same complete retained scene/GRID/ORIGINAL decoder INPUT')
    expected={'model':MODEL,'decoder_selection':selection(),'decoder_INPUT_sha256':digest(dinput)}
    require(type(request['program_INPUT']) is dict and digest(request['program_INPUT'])==digest(expected),'explicit same decoder selection extension; no default/alias')
    frames=request['frames'];old=dinput['SOURCE_limb_records']
    require(type(frames) is list and len(frames)==len(old)==4,'complete ordered SOURCE frames')
    staged=[]
    for f,row in zip(frames,old):
        require(type(f) is dict and set(f)=={'case_name','source_id','frame_base64'},'strict frame record')
        require(type(f['case_name']) is str and type(f['source_id']) is str and
                (f['case_name'],f['source_id'])==(row['case_name'],row['source_id']),'ordered same SOURCE/frame identity')
        b=canonical_base64(f['frame_base64'])
        words=inspect_FRAME(b,row['context_sha256'],digest(row))
        raw=canonical_base64(row['hilo_le_base64'])
        require(b[104:]==raw and sha(raw)==row['hilo_le_sha256'] and digest(words)==digest(row['limb_uint32']),'unchanged complete payload/limbs')
        staged.append((deepcopy(row),b,words))
    return staged
def audit_transport_CPU(request,*,model):
    require(type(model) is str and model==MODEL,'explicit opt-in transport')
    data,pins,false=load_retained()
    if request is None:
        m=data['missing']
        return {'model':MODEL,FLAG:False,'missing_cases':m['missing_cases'],'missing_sources':m['missing_sources'],
                'frames_received':0,'native_RN64_adds':0,'zero_selections':0,'group_admissions':0,
                'phase_quota_fits':None,'uniform_executed_SOURCE_error_L1':None,'proof_scope':deepcopy(false),'status':'STOP'}
    staged=prepare_all(request,data) # ALL frames/INPUT/context/bytes BEFORE ANY scalar decode.
    outputs=[]
    for row,b,words in staged:
        scalars=[decoder.decode_scalar(*words[i:i+2]) for i in (0,2)]
        outputs.append({'case_name':row['case_name'],'source_id':row['source_id'],'frame_sha256':sha(b),
                        'encoder_row_sha256':digest(row),'payload_sha256':sha(b[104:]),'decoded_scalars':scalars,
                        'decoded_SOURCE_uint64':[s['decoded_uint64'] for s in scalars],
                        'retained_whole_box_guard_admission_disproved':row['retained_whole_box_guard_admission_disproved'],
                        'frozen_guard_admission_for_entire_box_proved':False,'status':'STOP'})
    return {'model':MODEL,FLAG:True,'request_sha256':digest(request),'program_INPUT_sha256':digest(request['program_INPUT']),
            'decoder_selection':selection(),'sources':outputs,'frames_received':len(outputs),
            'payload_bytes':16*len(outputs),'header_bytes':HEADER_BYTES*len(outputs),'wire_bytes':FRAME_BYTES*len(outputs),
            'native_RN64_adds':sum(s['new_native_RN64_adds'] for r in outputs for s in r['decoded_scalars']),
            'zero_selections':sum(s['new_zero_branch_selections'] for r in outputs for s in r['decoded_scalars']),
            'encoder_calls':0,'old_suites_or_producers_reexecuted':0,'inherited_pins_verified':len(pins),
            'group_admissions':0,'phase_quota_fits':None,'uniform_executed_SOURCE_error_L1':None,
            'actual_scene_authenticated':False,'frozen_GRID_program_changed':False,'legacy_decoder_equivalence_proved':False,
            'cost_scope':'new in-memory tagged CPU transport only; no GPU/network/files; IO/setup/upstream/full costs UNMEASURED',
            'proof_scope':deepcopy(false),'status':'STOP'}
