"""Atomic JSON optimizer checkpoints; deterministic replay before state trust.

Hashes identify bytes, not authors. A fresh family proof and prefix replay are
required by the caller. File fsync/replace is not a host power-loss guarantee.
"""
import hashlib,json,os,uuid
from pathlib import Path


def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def state(values):return [float(v).hex() for v in values]


def atomic_write(path,identity,next_step,deltas,m,v,history):
    if type(next_step) is not int or next_step<1 or len(history)!=next_step:
        raise ValueError('complete advanced optimizer prefix required')
    payload={'identity':identity,'next_step':next_step,'deltas_hex':state(deltas),'m_hex':state(m),'v_hex':state(v),'history':history}
    document={'schema':'optic_neuro_blender.atomic_optimizer_checkpoint.v1','payload':payload,'payload_sha256':hashlib.sha256(canonical(payload)).hexdigest()}
    path=Path(path);temporary=path.with_name(path.name+'.pending-'+uuid.uuid4().hex)
    with temporary.open('xb') as stream:stream.write(canonical(document));stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)
    return document['payload_sha256']


def load(path,identity,total_steps,parameter_count):
    raw=Path(path).read_bytes()
    if len(raw)>16*2**20:raise ValueError('bounded checkpoint required')
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('duplicate checkpoint key')
            result[key]=value
        return result
    document=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite checkpoint')))
    if set(document)!={'schema','payload','payload_sha256'} or document['schema']!='optic_neuro_blender.atomic_optimizer_checkpoint.v1':raise ValueError('checkpoint schema mismatch')
    payload=document['payload']
    if set(payload)!={'identity','next_step','deltas_hex','m_hex','v_hex','history'} or payload['identity']!=identity:raise ValueError('checkpoint model/profile/source identity mismatch')
    if hashlib.sha256(canonical(payload)).hexdigest()!=document['payload_sha256']:raise ValueError('checkpoint integrity mismatch')
    n=payload['next_step']
    if type(n) is not int or not 1<=n<=total_steps or len(payload['history'])!=n:raise ValueError('checkpoint prefix extent mismatch')
    import math
    for key in ('deltas_hex','m_hex','v_hex'):
        values=payload[key]
        if len(values)!=parameter_count or any(not isinstance(s,str) or not math.isfinite(float.fromhex(s)) or float.fromhex(s).hex()!=s for s in values):raise ValueError('complete canonical finite optimizer state required')
    if any(float.fromhex(s)<0 for s in payload['v_hex']):raise ValueError('negative Adam variance')
    return payload


def replay(payload,initial_deltas,advance):
    """advance(d,m,v,step) returns next d/m/v and freshly verified row.

    Exact native coordinates and loss/gradient summaries must match the stored
    prefix. Stored audit labels are ignored; returned rows are freshly checked.
    """
    d=list(initial_deltas);m=[0.0]*len(d);v=[0.0]*len(d);verified=[]
    for step,stored in enumerate(payload['history']):
        if stored.get('step')!=step or state(stored['deltas_BU'])!=state(d):raise ValueError('checkpoint prefix coordinates mismatch')
        d,m,v,row=advance(d,m,v,step)
        if float(row['train_loss']).hex()!=float(stored['train_loss']).hex() or float(row['gradient_max_abs']).hex()!=float(stored['gradient_max_abs']).hex():raise ValueError('checkpoint prefix arithmetic mismatch')
        verified.append(row)
    if any(state(values)!=payload[key] for values,key in ((d,'deltas_hex'),(m,'m_hex'),(v,'v_hex'))):raise ValueError('checkpoint optimizer state differs from deterministic prefix')
    return d,m,v,verified
