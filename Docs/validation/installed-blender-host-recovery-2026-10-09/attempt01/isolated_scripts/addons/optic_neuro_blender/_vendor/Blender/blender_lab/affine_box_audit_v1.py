"""Independent conditional translation-box proof, with exact affine ranges.

No producer jets, intersections or path enumeration are imported. The family
translates represented surfaces; native transform and physical errors remain
outside this conditional certificate. Unproved competitors return UNKNOWN.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from optic_neuro_blender._vendor.Tools.audit_captured_pilot_result_v1 import need,vec,dot,cross,sub
from optic_neuro_blender._vendor.Tools.audit_coherent_state_graph_v1 import planar_objects
from optic_neuro_blender._vendor.Tools.audit_graph_neighborhood_v1 import square_neighborhood
from optic_neuro_blender._vendor.Blender.benchmarks.capacity_audit.rational_interval_v1 import Interval as I
from optic_neuro_blender._vendor.Blender.blender_lab.state_graph_enclosure_v1 import tight_sincos,cmultiply,component
from optic_neuro_blender._vendor.Blender.benchmarks.capacity_audit.rational_interval_v1 import pi_interval


@dataclass(frozen=True)
class Affine:
    base: F
    coefficients: tuple
    def __add__(self,other):
        return Affine(self.base+other.base,tuple(a+b for a,b in zip(self.coefficients,other.coefficients)))
    def __sub__(self,other):return self+other.scale(-1)
    def scale(self,value):return Affine(self.base*F(value),tuple(c*F(value) for c in self.coefficients))
    def bounds(self,box):
        need(len(box)==len(self.coefficients),'Complete ordered parameter box required')
        low=high=self.base
        for coefficient,(a,b) in zip(self.coefficients,box):
            need(a<=b,'Ordered parameter interval required')
            x,y=coefficient*F(a),coefficient*F(b);low+=min(x,y);high+=max(x,y)
        return I(low,high)
    def identically_zero(self):return self.base==0 and not any(self.coefficients)


def adot(normal,point):
    value=point[0].scale(normal[0])
    for n,p in zip(normal[1:],point[1:]):value=value+p.scale(n)
    return value


class IndependentAffineBox:
    def __init__(self,scene,graph,parameters):
        self.scene=scene;self.graph=graph;self.count=len(parameters)
        self._proved_boxes=set()
        self._box_phases={}
        need(graph['status']=='COMPLETE' and self.count>0,'Complete independently audited base graph required')
        zero=(F(0),)*self.count
        constant=lambda value:Affine(F(value),zero)
        self.objects=planar_objects(scene);byname={row[0]:row for row in self.objects}
        shifts={name:tuple(constant(0) for _ in range(3)) for name in scene['objects']};used=set()
        for j,parameter in enumerate(parameters):
            need(set(parameter)=={'id','objects'} and parameter['objects'],'Explicit affine mirror translation family required')
            for name,direction in parameter['objects'].items():
                need(name in shifts and scene['objects'][name]['kind']=='mirror' and name not in used,'Unique translated mirror binding required');used.add(name)
                need(len(direction)==3 and any(direction),'Nonzero three-dimensional translation required')
                shifts[name]=tuple(Affine(F(0),tuple(F(d) if k==j else F(0) for k in range(self.count))) for d in direction)
        self.shifts=shifts;nodes=graph['nodes'];origin=[None]*len(nodes);self.points=[None]*len(nodes);self.segments=[None]*len(nodes);self.references=[None]*len(nodes)
        for root in graph['roots']:origin[root['node']]=tuple(constant(v) for v in nodes[root['node']]['origin'])
        for i in graph['topological_order']:
            node=nodes[i];need(origin[i] is not None,'Reachable affine origins required')
            row=byname[node['hit_object']];normal,offset=row[2][1:];direction=vec(node['direction']);denominator=dot(normal,direction)
            need(denominator!=0,'Unsupported tangent selected affine hit')
            parameter=(constant(offset)+adot(normal,shifts[row[0]])-adot(normal,origin[i])).scale(1/denominator)
            point=tuple(o+parameter.scale(d) for o,d in zip(origin[i],direction))
            need(parameter.base==node['segment_parameter'] and tuple(p.base for p in point)==tuple(node['point']),'Independent base affine hit disagrees')
            self.segments[i]=parameter;self.points[i]=point
            if 'terminal' in node:
                modal=tuple(constant(v)+s for v,s in zip(scene['objects'][row[0]]['mode_origin_BU'],shifts[row[0]]))
                reference=adot(direction,tuple(m-p for m,p in zip(modal,point))).scale(1/dot(direction,direction))
                need(reference.base==node['reference_parameter'],'Independent terminal reference disagrees');self.references[i]=reference
            for edge in node['edges']:
                target=edge['target'];need(origin[target] is None or origin[target]==point,'Merge differs across continuous translation family');origin[target]=point
        self.origins=origin

    def prove_box(self,box):
        need(len(box)==self.count,'Complete conditional parameter box required')
        byname={r[0]:r for r in self.objects};issues=[];proofs=[]
        for i,node in enumerate(self.graph['nodes']):
            selected=byname[node['hit_object']];segment=self.segments[i].bounds(box);proof={'node':i,'objects_checked':len(self.objects),'competitor_exclusions':{}}
            if segment.lo<=0:issues.append({'node':i,'reason':'SELECTED_POSITIVE_DISTANCE_UNPROVED'})
            triangles=[v for primitive,v,n in selected[3] if primitive in node['coincident_primitives']]
            witness=square_neighborhood(triangles,vec(node['point']),selected[2][1]);need(witness is not None,'Independent base interior witness required')
            radius=F(*witness['projected_radius']);local=tuple(p-s for p,s in zip(self.points[i],self.shifts[selected[0]]))
            displacement=[(local[k]-Affine(F(node['point'][k]),(F(0),)*self.count)).bounds(box) for k in witness['projection_keeps']]
            if any(v.max_abs()>radius for v in displacement):issues.append({'node':i,'reason':'SELECTED_SURFACE_UNION_SUPPORT_UNPROVED'})
            proof['selected_square_radius']=[radius.numerator,radius.denominator]
            origin=self.origins[i];direction=vec(node['direction'])
            for row in self.objects:
                name,obj,plane,faces,*_=row
                if name==selected[0]:continue  # Whole plane is one optical object; union support proved separately.
                normal,offset=plane[1:];denominator=dot(normal,direction)
                zero=(F(0),)*self.count
                numerator=Affine(offset,zero)+adot(normal,self.shifts[name])-adot(normal,origin)
                reason=None
                if denominator!=0:
                    parameter=numerator.scale(1/denominator)
                    previous=node['previous_plane']
                    if parameter.identically_zero() and previous is not None and previous[0]==name and vec(previous[1])==normal and previous[2]==offset:
                        reason='EXACT_PREVIOUS_PLANE_ZERO_CONTACT_EXCLUDED'
                    elif parameter.bounds(box).hi<0:reason='STRICTLY_BEHIND'
                    elif (parameter-self.segments[i]).bounds(box).lo>0:reason='STRICTLY_AFTER_SELECTED'
                    else:
                        point=tuple(o+parameter.scale(d)-s for o,d,s in zip(origin,direction,self.shifts[name]))
                        outside=True
                        for primitive,vertices,n in faces:
                            slacks=[]
                            for j,a in enumerate(vertices):
                                edge=sub(vertices[(j+1)%3],a);inward=cross(n,edge)
                                slack=adot(inward,tuple(p-Affine(v,zero) for p,v in zip(point,a))).bounds(box)
                                slacks.append(slack)
                            if not any(v.hi<0 for v in slacks):outside=False;break
                        if outside:reason='EVERY_CLOSED_TRIANGLE_STRICTLY_OUTSIDE'
                elif not numerator.bounds(box).contains(0):reason='PARALLEL_SEPARATED'
                else:
                    # Potential coplanarity: exclude triangle hits over the entire
                    # conservative time range [0, selected.upper], not samples.
                    relative=tuple(o-s for o,s in zip(origin,self.shifts[name]));outside=True
                    for primitive,vertices,n in faces:
                        slacks=[]
                        for j,a in enumerate(vertices):
                            inward=cross(n,sub(vertices[(j+1)%3],a))
                            slack=adot(inward,tuple(p-Affine(v,zero) for p,v in zip(relative,a))).bounds(box)+dot(inward,direction)*I(0,max(F(0),segment.hi))
                            slacks.append(slack)
                        if not any(v.hi<0 for v in slacks):outside=False;break
                    if outside:reason='COPLANAR_TIME_SEGMENT_ALL_TRIANGLES_EXCLUDED'
                if reason:proof['competitor_exclusions'][reason]=proof['competitor_exclusions'].get(reason,0)+1
                else:issues.append({'node':i,'object':name,'reason':'POTENTIAL_EARLIER_OR_COINCIDENT_HIT_UNPROVED'})
            proofs.append(proof)
        if not issues:self._proved_boxes.add(tuple((F(a),F(b)) for a,b in box))
        return {'status':'PROVED_CONTINUOUS_AFFINE_BOX_TOPOLOGY' if not issues else 'UNKNOWN_TOPOLOGY_NOT_PROVED','states':len(proofs),'issues':issues,'proofs':proofs,
                'scope':'Every point of the declared represented translation box; excludes independent triangle-plane competitors; coincident primitive identity may vary within the proved selected surface union'}

    def enclose_fields(self,box,inputs):
        key=tuple((F(a),F(b)) for a,b in box)
        need(key in self._proved_boxes,'Continuous topology proof required before field enclosure')
        need(set(inputs)=={r['source_id'] for r in self.graph['roots']},'Complete interval coherent sources required')
        if key not in self._box_phases:
            phases=[]
            for i,node in enumerate(self.graph['nodes']):
                norm=I(dot(vec(node['direction']),vec(node['direction']))).sqrt()
                row=[]
                for parameter in (self.segments[i],self.references[i]):
                    if parameter is None:row.append(None);continue
                    sine,cosine=tight_sincos(2*pi_interval()*parameter.bounds(box)*norm/I(F(self.graph['wavelength'])))
                    row.append((cosine,sine))
                phases.append(row)
            self._box_phases[key]=phases
        incoming=[[] for _ in self.graph['nodes']];outputs={p:[] for p in self.graph['ports']}
        for root in self.graph['roots']:incoming[root['node']].append(inputs[root['source_id']])
        for i in self.graph['topological_order']:
            node=self.graph['nodes'][i];merged=tuple(sum((v[k] for v in incoming[i]),I(0)) for k in (0,1))
            value=cmultiply(merged,self._box_phases[key][i][0])
            if 'terminal' in node:outputs[node['terminal']].append(cmultiply(value,self._box_phases[key][i][1]))
            for edge in node['edges']:incoming[edge['target']].append(cmultiply(value,component(F(edge['power']),edge['quarter_turns'],F(edge['phase_rad']))))
        return {p:tuple(sum((v[k] for v in values),I(0)) for k in (0,1)) for p,values in outputs.items()}
