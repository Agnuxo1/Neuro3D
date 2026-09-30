"""Independent retained EXR decoding + pinned pure RT-CAP-003 gate replay.

No Blender/GPU launch, peer imports, peer main or peer writers. Runtime guard
termination/deadline enforcement is not certified by pure-function checks.
"""
import argparse
import ast
import builtins
import copy
import datetime as dt
import hashlib
import json
import math
import struct
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parents[2]
PEER = Path('D:/PROJECTS/.cognition/neuro3d/rt_cap002')
RESPONSE002 = 'f42978a4142b8785d3c21f12979555a8fedadd96f46f8fcf703943466dd4ed89'
RESPONSE003 = '26815689760cf4ff989ef049efae26d44d19340c279d8f6989d09db7a50d02fb'


def load_pinned(path, expected, hashes):
    raw = path.read_bytes(); sha = hashlib.sha256(raw).hexdigest()
    if sha != expected: raise ValueError('retained artifact changed: ' + str(path))
    hashes[str(path)] = sha
    return raw


def pure_bundle(source, names, namespace):
    """Extract reviewed pure functions only, not a general untrusted sandbox."""
    tree = ast.parse(source); nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in nodes} != set(names): raise ValueError('pure ABI changed')
    calls = set(names) | {'isinstance','math.isfinite','ValueError','any','all','len','range','list','abs','round','math.hypot','centre','grid'}
    for n in nodes:
        if n.decorator_list: raise ValueError('decorator not reviewed')
        for item in ast.walk(n):
            if isinstance(item, (ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal)): raise ValueError('side effect in pure bundle')
            if isinstance(item, ast.Call):
                target = ast.unparse(item.func)
                if target not in calls and not target.endswith(('.append','.items','.total_seconds')):
                    raise ValueError('call not reviewed: ' + target)
    allowed = ('isinstance','int','float','bool','dict','list','tuple','ValueError','any','all','len','range','abs','round')
    ns = {'__builtins__':{k:getattr(builtins,k) for k in allowed}, 'math':math, **namespace}
    exec(compile(ast.Module(body=nodes,type_ignores=[]), '<pinned pure bundle>', 'exec'),ns)
    return ns


def decode_exr(raw):
    """Narrow 8x8 scanline FLOAT/NONE named-channel decoder, not general EXR.

    Layout verified against https://openexr.com/en/latest/OpenEXRFileLayout.html.
    Reject tiles/deep/multipart/subsampling/compression/HALF and bad blocks.
    Returned arrays have EXR y=0 first (top); caller explicitly flips to Bpy.
    """
    if len(raw)<8 or struct.unpack_from('<II',raw) != (20000630,2): raise ValueError('unsupported EXR version/flags')
    def string(data,at):
        end=data.index(b'\0',at)
        return data[at:end].decode('ascii'),end+1
    at=8; attrs={}
    while True:
        name,at=string(raw,at)
        if not name: break
        kind,at=string(raw,at); size=struct.unpack_from('<i',raw,at)[0]; at+=4
        if size<0 or at+size>len(raw) or name in attrs: raise ValueError('bad EXR attribute')
        attrs[name]=(kind,raw[at:at+size]); at+=size
    if attrs.get('compression') != ('compression',b'\0'): raise ValueError('NONE compression required')
    if attrs.get('dataWindow') != ('box2i',struct.pack('<4i',0,0,7,7)): raise ValueError('8x8 data window required')
    if attrs.get('channels',('',))[0] != 'chlist': raise ValueError('channel list required')
    ch=attrs['channels'][1]; k=0; names=[]
    while True:
        name,k=string(ch,k)
        if not name: break
        pixel,linear,reserved,xs,ys=struct.unpack_from('<iB3sii',ch,k); k+=16
        if pixel!=2 or xs!=1 or ys!=1 or linear not in (0,1) or reserved!=b'\0'*3 or name in names: raise ValueError('FLOAT full-sampled unique channels required')
        names.append(name)
    if k!=len(ch) or not 1<=len(names)<=4 or names!=sorted(names): raise ValueError('bad channel list')
    table_end=at+8*8
    if table_end>len(raw): raise ValueError('short line offset table')
    offsets=struct.unpack_from('<8Q',raw,at); arrays={n:np.empty((8,8),dtype=np.float32) for n in names}; rows=set(); spans=[]
    for off in offsets:
        if off<table_end or off+8>len(raw): raise ValueError('bad scanline offset')
        y,size=struct.unpack_from('<ii',raw,off); begin=off+8; end=begin+size
        if y not in range(8) or y in rows or size!=8*4*len(names) or end>len(raw): raise ValueError('bad scanline block')
        rows.add(y); spans.append((off,end))
        values=np.frombuffer(raw,dtype='<f4',count=8*len(names),offset=begin).reshape(len(names),8)
        for i,name in enumerate(names): arrays[name][y,:]=values[i]
    ordered=sorted(spans)
    if len(rows)!=8 or any(a[1]>b[0] for a,b in zip(ordered,ordered[1:])): raise ValueError('overlapping/partial scanlines')
    return arrays


def independent_gate(m, aov, depth, position):
    n = m['res']
    if aov.shape != (n,n) or depth.shape != (n,n) or position.shape != (n,n,3): raise ValueError('EXR shape mismatch')
    # All actual retained values are finite, including their recorded miss sentinels.
    if not all(np.isfinite(x).all() for x in (aov,depth,position)): raise ValueError('nonfinite EXR')
    ids = np.asarray(m['expected_id_grid_row0_bottom']); hit = ids >= 0
    if not np.all(aov[~hit] == 0): raise ValueError('miss AOV nonzero')
    id_error = float(np.max(np.abs(aov[hit].astype(np.float64) - (ids[hit]+1))))
    if id_error > 1e-4 or not np.array_equal(np.rint(aov[hit]).astype(int),ids[hit]+1): raise ValueError('wrong hit ID')
    lookup = {t['id']:t for t in m['triangles']}
    z_error = pz_error = xy_max = 0.0
    for r,c in zip(*np.where(hit)):
        z_error = max(z_error,abs(float(depth[r,c])-m['expected_t_grid'][r][c]))
        pz_error = max(pz_error,abs(float(position[r,c,2])-lookup[int(ids[r,c])]['vertices_f32'][0][2]))
        xy_max = max(xy_max,math.hypot(float(position[r,c,0])-(c+.5)/n,float(position[r,c,1])-(r+.5)/n))
    if z_error > 1e-6 or pz_error > 1e-6 or xy_max > .03: raise ValueError('frozen diagnostic gate failed')
    return {'hits':int(hit.sum()),'misses':int((~hit).sum()),'id_abs_max':id_error,
        'z_abs_max_BU':z_error,'pz_abs_max_BU':pz_error,'xy_offset_max_BU':xy_max}


def audit():
    hashes = {}; r2_path = ROOT/'coordinacion/respuestas/RT-CAP-002-CLAUDE.json'; r3_path = ROOT/'coordinacion/respuestas/RT-CAP-003-CLAUDE.json'
    r2 = json.loads(load_pinned(r2_path,RESPONSE002,hashes)); r3 = json.loads(load_pinned(r3_path,RESPONSE003,hashes))
    source = {}
    for name,sha in r3['revision_11_17_utc']['new_sha256'].items(): source[name] = load_pinned(PEER/name,sha,hashes).decode('utf-8-sig')
    captures = []
    for size in (2,32):
        name = f'manifest_T{size}.json'; m = json.loads(load_pinned(PEER/name,r2['artifact_sha256'][name],hashes))
        for dev in ('cpu','gpu'):
            key = f'T{size}_{dev}'; info = r2['results'][key]; directory = PEER/f'out_{key}'
            cap = json.loads(load_pinned(directory/f'capture_{key}.json',info['capture_json_sha256'],hashes))
            if cap['manifest_sha256_body'] != m['manifest_sha256_body']: raise ValueError('capture manifest mismatch')
            decoded = {}
            for kind in ('tid','depth','position'):
                p = directory/f'{kind}_0001.exr'
                channels = decode_exr(load_pinned(p,info['files_sha256'][kind],hashes))
                if kind=='position':
                    if set(channels)!=set('XYZ'): raise ValueError('XYZ position channels required')
                    decoded[kind]=np.stack([channels[k][::-1] for k in 'XYZ'],axis=-1)
                else:
                    if len(channels)!=1: raise ValueError('single scalar channel required')
                    decoded[kind]=next(iter(channels.values()))[::-1].copy()
            raw = cap['raw']
            for kind,field in (('tid','tid'),('depth','z'),('position','pos')):
                if not np.array_equal(decoded[kind],np.asarray(raw[field],dtype=np.float32)): raise ValueError('EXR vs peer JSON mismatch: '+key+'/'+kind)
            gate = independent_gate(m,decoded['tid'],decoded['depth'],decoded['position'])
            captures.append({'fixture':key,'independent_gate_pass':True,'EXR_equals_JSON_exactly':True,**gate})

    policy = next(ast.literal_eval(n.value) for n in ast.parse(source['guard_v2.py']).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POLICY' for t in n.targets))
    g = pure_bundle(source['guard_v2.py'],('_num','validate_budget','validate_telemetry','decide','during_breach'),{'POLICY':policy})
    raw_source = load_pinned(PEER/'rtcap.py',r2['artifact_sha256']['rtcap.py'],hashes).decode('utf-8-sig')
    thresholds = next(ast.literal_eval(n.value) for n in ast.parse(raw_source).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='THRESHOLDS' for t in n.targets))
    checker = pure_bundle(source['rtcap_v2.py'],('_finite','check_capture_v2'),{'THRESHOLDS':thresholds,'centre':lambda r,c:((c+.5)/8,(r+.5)/8)})
    cap = json.loads((PEER/'out_T32_gpu/capture_T32_gpu.json').read_text()); m = json.loads((PEER/'manifest_T32.json').read_text())
    rejected = []
    for field,component in (('z',None),('pos',0),('pos',2),('tid',None)):
        raw = copy.deepcopy(cap['raw'])
        if component is None: raw[field][0][0] = float('nan')
        else: raw[field][0][0][component] = float('nan')
        failed = not checker['check_capture_v2'](m,raw['tid'],raw['z'],raw['pos'])['pass']
        if not failed: raise ValueError('v2 nonfinite accepted')
        rejected.append(field+str(component))
    now = dt.datetime(2026,9,30,12,tzinfo=dt.timezone.utc); deadline = now+dt.timedelta(minutes=5)
    good = {'ram_free_gib':8.,'vram_used_gib':1.,'vram_total_gib':24.,'temp_c':30.}
    if g['decide'](good,1.5,1.,60.,now,deadline): raise ValueError('valid guard control blocked')
    guard_rejected = []
    for kind in ('ram_budget_nan','vram_budget_negative','ram_telemetry_nan','temperature_inf','deadline_expired'):
        t = dict(good); ram=1.5; vram=1.; dl=deadline
        if kind=='ram_budget_nan': ram=float('nan')
        if kind=='vram_budget_negative': vram=-2.
        if kind=='ram_telemetry_nan': t['ram_free_gib']=float('nan')
        if kind=='temperature_inf': t['temp_c']=float('inf')
        if kind=='deadline_expired': dl=now-dt.timedelta(seconds=1)
        try: failed=bool(g['decide'](t,ram,vram,60.,now,dl))
        except ValueError: failed=True
        if not failed: raise ValueError('invalid guard input accepted')
        guard_rejected.append(kind)
    if g['during_breach']({**good,'ram_free_gib':4.}): raise ValueError('exact floor blocked')
    if 'ram_floor_during' not in g['during_breach']({**good,'ram_free_gib':3.9}): raise ValueError('lowered floor')
    return {'schema':'exp005-rt-readback-review-cpu-v1','input_sha256':hashes,'captures':captures,
        'pure_checker_invalids_rejected':rejected,'pure_guard_invalids_rejected':guard_rejected,
        'during_RAM_floor_4_verified':True,'decoder':'own narrow uncompressed FLOAT EXR, named channels','numpy_version':np.__version__,
        'scope':'CPU readback of retained EXR + pure gate functions; not historical watchdog certification',
        'launch_approved':False,'C3':'BLOCKED','rt_hardware_certified':False,'no_jev_aval':True,
        'remaining_review':['guard.run uses wall-clock time and blocking telemetry timeout10; strict child120/deadline may overrun',
            'exception after spawning child reaches ERROR/finally without guaranteed child cleanup',
            'peer runtime guard tests not executed: writers and subprocess launches intentionally excluded']}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); args=p.parse_args(); report=audit()
    report['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in (Path(__file__),Path(__file__).with_name('test_exp005_rt_readback_review.py'))}
    with args.output.open('x',encoding='utf-8') as f: f.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'captures_pass':len(report['captures']),'EXR_files':12,'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__': main()
