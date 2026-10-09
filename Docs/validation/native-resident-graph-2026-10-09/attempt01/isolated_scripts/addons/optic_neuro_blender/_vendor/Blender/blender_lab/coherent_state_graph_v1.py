"""Finite exact geometric state quotient and coherent scalar propagation.

Merge only identical represented origin/direction/previous optical plane. The
incoming complex field is referenced to that origin; the future operator is
identical. Every nonzero outgoing branch remains an edge. Cycles, resource caps
and unresolved selections yield INCOMPLETE with null fields, never ray pruning.
This quotient changes representation, not optics; native fields are estimates.
"""
from collections import deque
from fractions import Fraction as F
import cmath
import math

from optic_neuro_blender._vendor.Blender.benchmarks.capacity_audit import robust_multipath_v1 as base
from optic_neuro_blender._vendor.Blender.benchmarks.capacity_audit.exact_object_index_v1 import ExactObjectIndex
from .scene_capture_v1 import digest,need
from .scalar_scene_ingress_v1 import rational_wire


def optical_plane(triangle):
    if triangle is None:
        return None
    normal=base.cross(base.sub(triangle['vertices'][1],triangle['vertices'][0]),
                      base.sub(triangle['vertices'][2],triangle['vertices'][0]))
    pivot=next(v for v in normal if v)
    canonical=tuple(v/pivot for v in normal)
    return triangle['object_id'],canonical,base.dot(canonical,triangle['vertices'][0])


def segment_cycles(parameter,norm_squared,wavelength):
    n=F(norm_squared)
    a,b=math.isqrt(n.numerator),math.isqrt(n.denominator)
    if a*a==n.numerator and b*b==n.denominator:
        return F(parameter)*F(a,b)/F(wavelength)
    return None


def segment_coefficient(parameter,direction,wavelength):
    norm2=base.dot(direction,direction)
    cycles=segment_cycles(parameter,norm2,wavelength)
    angle=2*math.pi*float(cycles%1) if cycles is not None else 2*math.pi*float(parameter)*math.sqrt(float(norm2))/float(wavelength)
    return cmath.exp(1j*angle)


def build_graph(scene,*,max_states=4096):
    need(type(max_states) is int and 0<max_states<=4096,'bounded state count required')
    wavelength,objects,triangles=base.geometry(scene)
    need(scene['sources'] and any(o['kind'] in ('det','escape') for o in objects.values()),'sources and declared terminals required')
    index=ExactObjectIndex(triangles)
    nodes=[]
    keys={}
    pending=deque()
    roots=[]
    unresolved=[]
    zero_edges=0
    def admit(origin,direction,previous):
        plane=optical_plane(previous)
        key=(origin,direction,plane)
        if key not in keys:
            if len(nodes)>=max_states:
                return None
            keys[key]=len(nodes)
            nodes.append({'id':len(nodes),'origin':origin,'direction':direction,
                          'previous_plane':plane,'previous':previous,'edges':[]})
            pending.append(keys[key])
        return keys[key]
    seen=set()
    for source in scene['sources']:
        sid=source['id']
        need(sid not in seen and sid,'unique source IDs required')
        seen.add(sid)
        origin,direction=base.vector(source['position_BU']),base.vector(source['direction'])
        need(direction!=(0,0,0),'nonzero source direction required')
        node_id=admit(origin,direction,None)
        if node_id is None:
            unresolved.append({'status':'STATE_LIMIT','source_id':sid})
        else:
            roots.append({'source_id':sid,'node':node_id})
    while pending:
        node=nodes[pending.popleft()]
        hit=index(node['origin'],node['direction'],triangles,node['previous'])
        node['selection_status']=hit['status']
        if hit['status']!='SELECT':
            unresolved.append({'status':hit['status'],'node':node['id']})
            continue
        selected=hit['selected']
        name=selected['object_id']
        obj=objects[name]
        point=hit['point']
        node.update(hit_object=name,primitive_id=selected['primitive_id'],point=point,
                    segment_parameter=hit['t'],coincident_primitives=[r['primitive_id'] for r in hit['candidates']])
        if obj['kind'] in ('det','escape'):
            if not base.parallel(node['direction'],obj['axis']) or base.dot(node['direction'],obj['axis'])<=0:
                unresolved.append({'status':'MODE_MISMATCH','node':node['id']})
            else:
                node['terminal']=name
                norm2=base.dot(node['direction'],node['direction'])
                node['reference_parameter']=base.dot(node['direction'],base.sub(obj['reference'],point))/norm2
            continue
        reflection=base.reflected(node['direction'],selected['normal'])
        need(base.dot(reflection,reflection)==base.dot(node['direction'],node['direction']),'exact reflection norm invariant')
        branches=([('mirror',reflection,F(1),2,obj['phase'])] if obj['kind']=='mirror' else
                  [('t',node['direction'],obj['tau'],0,F(0)),('r',reflection,1-obj['tau'],1,F(0))])
        for event,direction,power,turn,phase in branches:
            if power==0:
                zero_edges+=1
                continue
            target=admit(point,direction,selected)
            if target is None:
                unresolved.append({'status':'STATE_LIMIT','node':node['id'],'event':event})
            else:
                node['edges'].append({'event':event,'target':target,'power':power,'quarter_turns':turn,'phase_rad':phase})
    degree=[0]*len(nodes)
    for node in nodes:
        for edge in node['edges']:
            degree[edge['target']]+=1
    ready=deque(i for i,n in enumerate(degree) if n==0)
    order=[]
    while ready:
        node_id=ready.popleft()
        order.append(node_id)
        for edge in nodes[node_id]['edges']:
            degree[edge['target']]-=1
            if degree[edge['target']]==0:
                ready.append(edge['target'])
    if len(order)!=len(nodes):
        unresolved.append({'status':'CYCLE','nodes_not_in_topological_order':len(nodes)-len(order)})
    for node in nodes:
        node.pop('previous')
    return {'schema':'optic_neuro_blender.coherent_state_graph.v1','backend':'CPU_FRACTION_STATE_GRAPH',
            'scene_sha256':digest(rational_wire(scene)),'status':'INCOMPLETE' if unresolved else 'COMPLETE',
            'nodes':nodes,'roots':roots,'topological_order':order,'unresolved':unresolved,
            'wavelength':wavelength,'ports':[n for n,o in objects.items() if o['kind'] in ('det','escape')],
            'exact_zero_edges':zero_edges,'selection_statistics':index.stats,
            'field_certified':False,'physical_optics_certified':False}


def propagate_graph(graph,fields):
    need(graph['status']=='COMPLETE' and not graph['unresolved'],'complete acyclic graph required')
    ids={root['source_id'] for root in graph['roots']}
    need(isinstance(fields,dict) and set(fields)==ids,'complete explicit source fields required')
    incoming=[[] for _ in graph['nodes']]
    for root in graph['roots']:
        pair=fields[root['source_id']]
        need(isinstance(pair,(list,tuple)) and len(pair)==2,'explicit real/imag input required')
        value=complex(*(float(base.rational(x)) for x in pair))
        need(math.isfinite(value.real) and math.isfinite(value.imag),'finite source field required')
        incoming[root['node']].append(value)
    outputs={p:[] for p in graph['ports']}
    count=[0]*len(incoming)
    for root in graph['roots']:
        count[root['node']]+=1
    for node_id in graph['topological_order']:
        node=graph['nodes'][node_id]
        values=incoming[node_id]
        merged=complex(math.fsum(v.real for v in values),math.fsum(v.imag for v in values))
        propagated=merged*segment_coefficient(node['segment_parameter'],node['direction'],graph['wavelength'])
        if 'terminal' in node:
            value=propagated*segment_coefficient(node['reference_parameter'],node['direction'],graph['wavelength'])
            outputs[node['terminal']].append(value)
        for edge in node['edges']:
            coefficient=math.sqrt(float(edge['power']))*(1j**edge['quarter_turns'])*cmath.exp(1j*float(edge['phase_rad']))
            incoming[edge['target']].append(propagated*coefficient)
            count[edge['target']]+=count[node_id]
    fields={p:complex(math.fsum(v.real for v in a),math.fsum(v.imag for v in a)) for p,a in outputs.items()}
    return {'fields':fields,'powers':{p:abs(v)**2 for p,v in fields.items()},
            'represented_terminal_paths':sum(count[n['id']] for n in graph['nodes'] if 'terminal' in n),
            'field_certified':False,'physical_optics_certified':False}
