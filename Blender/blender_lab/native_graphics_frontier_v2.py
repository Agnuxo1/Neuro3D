"""Own frontier traversal driven by native graphics surface candidates.

Only evaluated meshes and newly generated rays enter the native GPU backend.
CPU rational plane/Gram predicates and an independent exact square-perimeter coverage witness verify each candidate; an incorrect GPU candidate
produces an incomplete graph, never a CPU replacement hit. Coherent fields
use exact refined represented geometry and the established CPU phase rule.
"""
from collections import deque
from fractions import Fraction as F
import math,time
from Blender.benchmarks.capacity_audit import robust_multipath_v1 as base
from Blender.blender_lab.scene_capture_v1 import digest,need
from Blender.blender_lab.scalar_scene_ingress_v1 import rational_wire
from Blender.blender_lab.coherent_state_graph_v1 import optical_plane
from Tools.audit_coherent_state_graph_v1 import planar_objects,independent_nearest
from Tools.audit_captured_pilot_result_v1 import check_triangle,vec,dot
from Tools.audit_graph_neighborhood_v1 import square_neighborhood


class GraphicsCandidateVerifier:
    def __init__(self,scene,triangles,tolerance):
        self.objects=planar_objects(scene);self.byname={row[0]:row for row in self.objects};self.groups={}
        for triangle in triangles:self.groups.setdefault(triangle['object_id'],[]).append(triangle)
        self.tolerance=tolerance;self.stats={'queries':0,'verified_candidates':0,'rejected_candidates':0,'exact_verification_seconds':0.0}

    def __call__(self,node,candidate):
        self.stats['queries']+=1;start=time.perf_counter()
        try:
            need(candidate.get('status')=='GRAPHICS_SURFACE_CANDIDATE' and candidate.get('object') in self.groups,'Actual graphics surface required')
            name=candidate['object'];row=self.byname[name];normal,offset=row[2][1:]
            denominator=dot(normal,node['direction']);need(denominator!=0,'Selected transverse plane required')
            parameter=(offset-dot(normal,node['origin']))/denominator;need(parameter>0,'Selected positive exact distance required')
            point=tuple(o+parameter*d for o,d in zip(node['origin'],node['direction']))
            closed=[]
            for triangle in self.groups[name]:
                try:triangle_normal=check_triangle(point,triangle['vertices'])
                except ValueError:continue
                closed.append(dict(triangle,normal=triangle_normal))
            need(closed,'Graphics candidate requires exact closed support')
            witness=square_neighborhood([t['vertices'] for t in closed],point,normal)
            need(witness is not None,'Independent exact positive interior square required')
            hit={'status':'SELECT','t':parameter,'point':point,'selected':closed[0],'candidates':closed,'interior_neighborhood':witness}
            distance=float(hit['t'])*math.sqrt(float(base.dot(node['direction'],node['direction'])))
            need(abs(candidate['distance_BU']-distance)<=self.tolerance,'Graphics distance exceeds prospective candidate budget')
            need(candidate['primitive_id'] in {t['primitive_id'] for t in hit['candidates']},'Graphics primitive requires exact nearest closed support')
            proposed={'origin':node['origin'],'direction':node['direction'],'previous_plane':node['previous_plane'],
                      'hit_object':candidate['object'],'segment_parameter':hit['t'],'coincident_primitives':[t['primitive_id'] for t in hit['candidates']]}
            # Exhaustive independent planar predicates exclude all nearer competitors.
            independent_nearest(proposed,self.objects)
            self.stats['verified_candidates']+=1;return hit
        except ValueError:
            self.stats['rejected_candidates']+=1
            return {'status':'GRAPHICS_CANDIDATE_NOT_EXACTLY_VERIFIED'}
        finally:self.stats['exact_verification_seconds']+=time.perf_counter()-start


def build_graphics_graph(scene,backend,*,max_states=4096,distance_tolerance_BU=5e-5):
    need(type(max_states) is int and 0<max_states<=4096,'bounded state count required')
    wavelength,objects,triangles=base.geometry(scene)
    need(scene['sources'] and any(o['kind'] in ('det','escape') for o in objects.values()),'sources and declared terminals required')
    verifier=GraphicsCandidateVerifier(scene,triangles,distance_tolerance_BU)
    batches=[]
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
        frontier=[pending.popleft() for _ in range(len(pending))]
        queries=[]
        for node_id in frontier:
            node=nodes[node_id];previous=node['previous_plane']
            if previous is not None:
                need(base.dot(previous[1],node['origin'])==previous[2] and base.dot(previous[1],node['direction'])!=0,'Exact zero transverse previous contact required')
            queries.append({'origin':node['origin'],'direction':node['direction'],'previous_name':previous[0] if previous else None})
        observed=backend.query(queries)
        need(len(observed['rows'])==len(frontier),'Complete actual GPU frontier readback required')
        batches.append({'node_ids':frontier,'queries':queries,'readback':observed})
        for node_id,candidate in zip(frontier,observed['rows']):
            node=nodes[node_id]
            hit=verifier(node,candidate)
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
            'exact_zero_edges':zero_edges,'selection_statistics':verifier.stats,'graphics_frontier_batches':batches,
            'selection_backend':'NATIVE_GPU_RASTER_DEPTH_WITH_EXACT_CPU_VERIFICATION','selection_is_gpu':True,
            'graphics_candidate_fallback':False,
            'field_certified':False,'physical_optics_certified':False}
