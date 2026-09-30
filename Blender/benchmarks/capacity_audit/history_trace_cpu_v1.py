"""Bounded exact represented CPU traversal, never a native GPU path supplier.

Derive complete histories from snapshot sources/triangles/roles. No fixture
path input, epsilon, truncation, intensity pruning or fitted matrix. This
opt-in serializer rejects rational departures not exactly representable as
binary64; it does not snap them or claim a general geometry implementation.
"""
from fractions import Fraction as F
from history_lineage_cpu_v2 import scene_binding,triangles,nearest,vec,dot
from history_completeness_cpu_v1 import validate_complete_tree


def represented(v):
    out=[]
    for x in v:
        value=float(x)
        if F(value)!=x:raise ValueError('departure not exactly representable in binary64; no snapping')
        out.append(value)
    vec(out)  # Reuse the frozen coordinate/profile bounds.
    return out


def trace_scene(snapshot,*,record_cap=64,depth_cap=32):
    for name,cap,limit in (('record',record_cap,64),('depth',depth_cap,32)):
        if isinstance(cap,bool) or not isinstance(cap,int) or not 1<=cap<=limit:
            raise ValueError('explicit '+name+' cap within frozen CPU profile required')
    sha,packed=scene_binding(snapshot);geometry=triangles(packed)
    rows=[];queries=0
    def append(sid,parent,event,pid,o,d,depth):
        if len(rows)>=record_cap:raise ValueError('record cap reached; incomplete output forbidden')
        if depth>depth_cap:raise ValueError('depth cap reached; incomplete output forbidden')
        rows.append({'id':len(rows),'parent_id':parent,'source_id':sid,'snapshot_sha256':sha,
                     'depth':depth,'event':event,'primitive_id':pid,
                     'origin_BU':represented(o),'direction':represented(d)})
    for source in snapshot['sources']:
        append(source['id'],None,'source',None,vec(source['position_BU']),vec(source['direction']),0)
    i=0
    while i<len(rows):
        row=rows[i];i+=1
        if row['event'] in ('detect','escape'):continue
        o,d=vec(row['origin_BU']),vec(row['direction'])
        parameter,pid,owner,n=nearest(o,d,geometry,row['primitive_id']);queries+=1
        point=tuple(x+parameter*y for x,y in zip(o,d))
        kind=snapshot['objects'][packed.geometry.object_ids[owner]]['kind']
        events={'mirror':('mirror',),'bs':('t','r'),'det':('detect',),'escape':('escape',)}[kind]
        for event in events:
            direction=tuple(x-2*dot(d,n)*y/dot(n,n) for x,y in zip(d,n)) if event in ('mirror','r') else d
            append(row['source_id'],row['id'],event,pid,point,direction,row['depth']+1)
    checked=validate_complete_tree(snapshot,rows)
    return {'schema':'exp005-history-trace-CPU-v1','records':rows,'checks':checked,
            'nearest_queries':queries,'record_cap':record_cap,'depth_cap':depth_cap,
            'scope':'exact represented bounded CPU traversal; NOT GPU/Blender/RT/physical optics',
            'fields_computed':False,'native_backend_received_paths':False}
