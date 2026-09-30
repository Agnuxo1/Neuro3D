"""Bounded exact CPU history verifier, NOT a GPU self-hit repair.

Reconstructs rays from sources and accepted parent events, never trusts a
claimed previous primitive or hashes alone. Partial history prefixes only;
no field/phase computation, native error bound or optical authenticity claim.
"""
from fractions import Fraction as F
import hashlib
import json
import math
from frontier_inputs import pack_frontier


def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def vec(v):
    if len(v)!=3: raise ValueError('three-vector required')
    result=[]
    for x in v:
        if isinstance(x,bool) or not isinstance(x,(int,float,F)) or abs(x)>1e6 or not math.isfinite(x):
            raise ValueError('bounded finite CPU coordinate required')
        result.append(F(x))
    return tuple(result)


def scene_binding(snapshot):
    packed=pack_frontier(snapshot)
    # Object order changes global primitive indices; sorted JSON alone misses it.
    value={'snapshot':snapshot,'object_order':list(packed.geometry.object_ids),
           'source_order':list(packed.source_ids)}
    body=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
    return hashlib.sha256(body.encode()).hexdigest(),packed


def triangles(packed):
    raw=packed.geometry.triangles
    return [(int(raw[i+3]),(vec(raw[i:i+3]),vec(raw[i+4:i+7]),vec(raw[i+8:i+11]))) for i in range(0,len(raw),12)]


def intersection(o,d,tri):
    a,b,c=tri; e1,e2=sub(b,a),sub(c,a); n=cross(e1,e2); h=cross(d,e2); det=dot(e1,h)
    if det==0:
        if dot(n,sub(o,a))==0: raise ValueError('coplanar ray outside this CPU contract')
        return None
    rel=sub(o,a); q=cross(rel,e1); u=dot(rel,h)/det; v=dot(d,q)/det
    if u<0 or v<0 or u+v>1: return None
    return dot(e2,q)/det,n


def nearest(o,d,geometry,previous_pid):
    hits=[]
    for pid,(owner,tri) in enumerate(geometry):
        value=intersection(o,d,tri)
        if value is None: continue
        t,n=value
        if t<0: continue
        if t==0:
            if previous_pid is None: raise ValueError('source contact has no established departure')
            old_owner,old_tri=geometry[previous_pid]; old_n=cross(sub(old_tri[1],old_tri[0]),sub(old_tri[2],old_tri[0]))
            if owner!=old_owner or cross(n,old_n)!=(0,0,0) or dot(old_n,sub(tri[0],old_tri[0]))!=0:
                raise ValueError('unproved zero contact on another surface')
            continue  # Proven exact CPU departure only; no positive cutoff or GPU omission.
        hits.append((t,pid,owner,n))
    if not hits: raise ValueError('history ray lost')
    first=min(hits,key=lambda h:(h[0],h[1])); t,pid,owner,n=first
    if any(h[0]==t and (h[2]!=owner or cross(h[3],n)!=(0,0,0)) for h in hits):
        raise ValueError('exact coincident hit ambiguous')
    return first


def validate_history(snapshot,records):
    binding,packed=scene_binding(snapshot); geom=triangles(packed)
    if not isinstance(records,list) or not 1<=len(records)<=64: raise ValueError('1..64 explicit CPU records required')
    sources={s['id']:s for s in snapshot['sources']}; accepted={}; roots=set(); branches=set(); rows=[]
    for record in records:
        keys={'id','parent_id','source_id','snapshot_sha256','depth','event','primitive_id','origin_BU','direction'}
        if not isinstance(record,dict) or set(record)!=keys: raise ValueError('complete explicit history schema required')
        rid=record['id']; parent_id=record['parent_id']; sid=record['source_id']; event=record['event']; depth=record['depth']; pid=record['primitive_id']
        if isinstance(rid,bool) or not isinstance(rid,int) or not 0<=rid<64 or rid in accepted: raise ValueError('unique bounded record ID required')
        if isinstance(depth,bool) or not isinstance(depth,int) or not 0<=depth<=32: raise ValueError('explicit depth <=32 required')
        if record['snapshot_sha256']!=binding or sid not in sources: raise ValueError('stale scene or undeclared source')
        observed_o,observed_d=vec(record['origin_BU']),vec(record['direction'])
        if dot(observed_d,observed_d)==0: raise ValueError('nonzero direction required')
        if parent_id is None:
            if event!='source' or pid is not None or depth!=0 or sid in roots: raise ValueError('unique source root required')
            expected_o,expected_d=vec(sources[sid]['position_BU']),vec(sources[sid]['direction'])
            if (observed_o,observed_d)!=(expected_o,expected_d): raise ValueError('root does not match declared source')
            roots.add(sid); expected_pid=None; parameter=None
        else:
            if isinstance(parent_id,bool) or not isinstance(parent_id,int) or parent_id not in accepted: raise ValueError('earlier accepted parent required')
            parent=accepted[parent_id]
            if parent['terminal'] or sid!=parent['source_id'] or depth!=parent['depth']+1: raise ValueError('invalid terminal/source/depth ancestry')
            if isinstance(pid,bool) or not isinstance(pid,int) or not 0<=pid<len(geom): raise ValueError('global primitive ID required')
            if (parent_id,event) in branches: raise ValueError('duplicate branch event')
            parameter,expected_pid,owner,normal=nearest(parent['origin'],parent['direction'],geom,parent['primitive_id'])
            if pid!=expected_pid: raise ValueError('claimed primitive is not the independently selected nearest')
            point=tuple(x+parameter*y for x,y in zip(parent['origin'],parent['direction']))
            name=packed.geometry.object_ids[owner]; kind=snapshot['objects'][name]['kind']
            roles={'mirror':('mirror',),'bs':('t','r'),'det':('detect',),'escape':('escape',)}
            if event not in roles[kind]: raise ValueError('event inconsistent with scene optical role')
            reflected=tuple(x-2*dot(parent['direction'],normal)*n/dot(normal,normal) for x,n in zip(parent['direction'],normal))
            expected_d=reflected if event in ('mirror','r') else parent['direction']; expected_o=point
            if (observed_o,observed_d)!=(expected_o,expected_d): raise ValueError('saved departure differs from exact CPU history; no snapping')
            branches.add((parent_id,event))
        accepted[rid]={'origin':expected_o,'direction':expected_d,'primitive_id':expected_pid,
                       'source_id':sid,'depth':depth,'terminal':event in ('detect','escape')}
        rows.append({'id':rid,'parent_id':parent_id,'source_id':sid,'primitive_id':expected_pid,'event':event,
                     't_parameter_exact':None if parameter is None else [parameter.numerator,parameter.denominator]})
    if roots!=set(sources): raise ValueError('one root per declared source required')
    return {'schema':'exp005-history-lineage-CPU-v1','scene_binding_sha256':binding,'records':rows,
            'scope':'exact represented CPU prefix; no native rounding/error bound or authenticated GPU ledger',
            'all_branches_proved_complete':False,'native_exemption_allowed':False,'fields_computed':False}
