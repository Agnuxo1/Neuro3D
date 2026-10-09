"""Independent plane/Gram nearest-hit and branch audit; no producer imports.

Currently accepts planar optical objects only. A completed producer result must
retain every nearest closed triangle and all nonzero branches, root identities,
exact reflection/modes, acyclicity and reachability. Native fields are estimates.
"""
from fractions import Fraction as F
import math

from Tools.audit_captured_pilot_result_v1 import decode,need,vec,dot,cross,sub,check_triangle,finite


def canonical_plane(name,normal,vertex):
    pivot=next(v for v in normal if v)
    normal=tuple(v/pivot for v in normal)
    return name,normal,dot(normal,vertex)


def coplanar_first(origin,direction,vertices,normal):
    lower,upper=F(0),None
    for i,a in enumerate(vertices):
        edge=sub(vertices[(i+1)%3],a)
        slack=dot(cross(edge,sub(origin,a)),normal)
        slope=dot(cross(edge,direction),normal)
        if slope==0:
            if slack<0:
                return None
        elif slope>0:
            lower=max(lower,-slack/slope)
        else:
            limit=-slack/slope
            upper=limit if upper is None else min(upper,limit)
        if upper is not None and lower>upper:
            return None
    return lower


def planar_objects(scene):
    result=[]
    primitive=0
    for name,obj in scene['objects'].items():
        vertices=[vec(v) for v in obj['vertices_world_BU']]
        rows=[]
        for face in obj['faces']:
            a,b,c=[vertices[i] for i in face]
            normal=cross(sub(b,a),sub(c,a))
            need(dot(normal,normal)>0,'degenerate geometry')
            rows.append((primitive,(a,b,c),normal))
            primitive+=1
        need(rows,'empty optical surface')
        plane=canonical_plane(name,rows[0][2],rows[0][1][0])
        need(all(dot(plane[1],v)==plane[2] for v in vertices),'audit restricted to planar objects')
        result.append((name,obj,plane,rows,
                       tuple(min(v[k] for v in vertices) for k in range(3)),
                       tuple(max(v[k] for v in vertices) for k in range(3))))
    return result


def independent_nearest(node,objects):
    origin,direction=vec(node['origin']),vec(node['direction'])
    hits=[]
    for name,obj,plane,faces,lower,upper in objects:
        normal,offset=plane[1],plane[2]
        denominator=dot(normal,direction)
        numerator=offset-dot(normal,origin)
        if denominator==0:
            if numerator==0:
                for primitive,vertices,n in faces:
                    first=coplanar_first(origin,direction,vertices,n)
                    if first is not None:
                        hits.append((first,'coplanar',name,primitive))
            continue
        parameter=numerator/denominator
        if parameter<0:
            continue
        previous=node['previous_plane']
        if parameter==0 and previous is not None and (previous[0],vec(previous[1]),previous[2])==plane:
            continue
        point=tuple(o+parameter*d for o,d in zip(origin,direction))
        if any(not a<=p<=b for p,a,b in zip(point,lower,upper)):
            continue
        for primitive,vertices,_ in faces:
            try:
                check_triangle(point,vertices)
            except ValueError:
                continue
            hits.append((parameter,'closed',name,primitive))
    need(hits,'completed node has no independent hit')
    first=min(h[0] for h in hits)
    nearest=[h for h in hits if h[0]==first]
    need(first>0 and all(h[1]=='closed' for h in nearest),'unresolved contact or coplanar hit')
    need({h[2] for h in nearest}=={node['hit_object']},'nearest object tie/mismatch')
    need(first==node['segment_parameter'],'nearest segment parameter mismatch')
    need({h[3] for h in nearest}==set(node['coincident_primitives']),'nearest closed primitive set mismatch')
    return first


def audit_graph_result(scene_wire,result_wire):
    scene,result=decode(scene_wire),decode(result_wire)
    graph=result['graph']
    need(graph['schema']=='optic_neuro_blender.coherent_state_graph.v1' and
         graph['backend']=='CPU_FRACTION_STATE_GRAPH','unknown graph schema/backend')
    need(graph['field_certified'] is False and graph['physical_optics_certified'] is False,'unsupported certificate claim')
    need(graph['wavelength']==scene['lambda_BU'],'graph wavelength mismatch')
    if graph['status']=='INCOMPLETE':
        need(graph['unresolved'] and result['fields'] is None and result['powers'] is None,'incomplete graph requires reasons and null fields')
        return {'primary_metric':0,'status':'VALID_INCOMPLETE_GRAPH','unresolved_reasons':sorted({r['status'] for r in graph['unresolved']}),
                'field_certified':False,'nearest_hits_independently_verified':False}
    need(graph['status']=='COMPLETE' and not graph['unresolved'],'unknown graph status')
    objects=planar_objects(scene)
    byname={row[0]:row for row in objects}
    sources={s['id']:s for s in scene['sources']}
    need(len(sources)==len(scene['sources']) and len(graph['roots'])==len(sources),'root/source count mismatch')
    nodes=graph['nodes']
    need([n['id'] for n in nodes]==list(range(len(nodes))) and nodes,'consecutive node IDs required')
    order=graph['topological_order']
    need(len(order)==len(nodes) and set(order)==set(range(len(nodes))),'complete topological order required')
    position={n:i for i,n in enumerate(order)}
    root_ids=set()
    root_sources=set()
    for root in graph['roots']:
        sid=root['source_id']
        need(sid in sources and sid not in root_sources,'unique declared source root required')
        root_sources.add(sid)
        node=nodes[root['node']]
        need(vec(node['origin'])==vec(sources[sid]['position_BU']) and vec(node['direction'])==vec(sources[sid]['direction'])
             and node['previous_plane'] is None,'source root geometry mismatch')
        root_ids.add(node['id'])
    reached=set(root_ids)
    zero_edges=0
    for node_id in order:
        node=nodes[node_id]
        need(node_id in reached,'unreachable graph state')
        need(node['selection_status']=='SELECT','unresolved completed state')
        independent_nearest(node,objects)
        name=node['hit_object']
        obj,plane,faces=byname[name][1:4]
        primitive=node['primitive_id']
        need(primitive in node['coincident_primitives'],'selected primitive absent from nearest set')
        selected=next(row for row in faces if row[0]==primitive)
        origin,direction,point=vec(node['origin']),vec(node['direction']),vec(node['point'])
        t=node['segment_parameter']
        need(point==tuple(o+t*d for o,d in zip(origin,direction)),'ray point mismatch')
        normal=check_triangle(point,selected[1])
        if obj['kind'] in ('det','escape'):
            axis=vec(obj['mode_direction'])
            need(node.get('terminal')==name and not node['edges'],'terminal binding/leaf mismatch')
            need(cross(direction,axis)==(0,0,0) and dot(direction,axis)>0,'terminal mode mismatch')
            need(node['reference_parameter']==dot(direction,sub(vec(obj['mode_origin_BU']),point))/dot(direction,direction),
                 'terminal phase reference mismatch')
            continue
        coefficient=2*dot(direction,normal)/dot(normal,normal)
        reflected=tuple(d-coefficient*n for d,n in zip(direction,normal))
        if obj['kind']=='mirror':
            expected={'mirror':(reflected,F(1),2,obj['phase_rad'])}
        else:
            tau=obj['power_transmittance']
            need(0<=tau<=1,'splitter range')
            expected={}
            if tau:
                expected['t']=(direction,tau,0,F(0))
            else:
                zero_edges+=1
            if tau<1:
                expected['r']=(reflected,1-tau,1,F(0))
            else:
                zero_edges+=1
        need(len(node['edges'])==len(expected) and {e['event'] for e in node['edges']}==set(expected),'nonzero branch omitted or duplicated')
        for edge in node['edges']:
            target=edge['target']
            need(type(target) is int and 0<=target<len(nodes) and position[target]>position[node_id],'graph cycle/order violation')
            d,power,turn,phase=expected[edge['event']]
            successor=nodes[target]
            prev=successor['previous_plane']
            need(vec(successor['origin'])==point and vec(successor['direction'])==d and prev is not None
                 and (prev[0],vec(prev[1]),prev[2])==plane,'branch successor state mismatch')
            need(edge['power']==power and edge['quarter_turns']==turn and edge['phase_rad']==phase,'branch optical coefficient mismatch')
            reached.add(target)
    need(zero_edges==graph['exact_zero_edges'],'exact zero edge count mismatch')
    ports={n for n,o in scene['objects'].items() if o['kind'] in ('det','escape')}
    need(set(graph['ports'])==ports and set(result['fields'])==ports and set(result['powers'])==ports,'terminal output IDs mismatch')
    for p in ports:
        value=result['fields'][p]
        need(set(value)=={'real','imag'} and finite(value['real']) and finite(value['imag']) and finite(result['powers'][p])
             and result['powers'][p]>=0,'finite native estimates required')
    return {'primary_metric':1,'status':'VALID_COMPLETE_GRAPH','states':len(nodes),'sources':len(sources),
            'nearest_hits_independently_verified':True,'nonzero_branch_coverage_verified':True,
            'boundary_neighborhood_independently_verified':False,
            'field_certified':False,'physical_optics_certified':False}
