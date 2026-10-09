"""Own forward derivatives for translations of a captured planar optical graph.

The affine hit/segment jets are derived from represented plane intersections,
not a learned/analytic transfer matrix. A merge is admitted only when every
incoming affine origin is identical. Translation family validity requires an
independent exact geometry audit at each evaluated optimizer state.
"""
import copy
import cmath
from fractions import Fraction as F
import math
import numpy as np

from optic_neuro_blender._vendor.Tools.audit_captured_pilot_result_v1 import vec,dot,cross,sub,need


class AffineGeometryNetwork:
    def __init__(self,scene,graph,parameters):
        need(graph['status']=='COMPLETE' and not graph['unresolved'],'complete geometric graph required')
        need(parameters and len({p['id'] for p in parameters})==len(parameters),'unique translation parameters required')
        self.scene,self.graph=copy.deepcopy(scene),copy.deepcopy(graph)
        self.parameters=copy.deepcopy(parameters)
        self.parameter_ids=[p['id'] for p in parameters]
        self.source_ids=[r['source_id'] for r in graph['roots']]
        self.ports=list(graph['ports']);self.count=len(parameters)
        zero=tuple(F(0) for _ in parameters)
        zero_vector=tuple(zero for _ in range(3))
        shifts={name:zero_vector for name in scene['objects']}
        for j,parameter in enumerate(parameters):
            need(set(parameter)=={'id','objects'} and parameter['objects'],'closed translation parameter definition required')
            for name,value in parameter['objects'].items():
                need(name in shifts and scene['objects'][name]['kind']=='mirror','translations restricted to declared mirrors')
                displacement=vec(value)
                need(any(displacement),'nonzero parameter displacement required')
                shifts[name]=tuple(tuple(shifts[name][k][i]+(displacement[k] if i==j else 0) for i in range(self.count)) for k in range(3))
        self.shifts=shifts
        self.origin_jets=[None]*len(graph['nodes'])
        self.point_jets=[None]*len(graph['nodes'])
        self.segment_jets=[None]*len(graph['nodes'])
        self.reference_jets=[None]*len(graph['nodes'])
        self.norms=[]
        for node in graph['nodes']:
            n2=dot(vec(node['direction']),vec(node['direction']))
            a,b=math.isqrt(n2.numerator),math.isqrt(n2.denominator)
            need(a*a==n2.numerator and b*b==n2.denominator,'rational direction norm required by affine phase compiler')
            self.norms.append(F(a,b))
        for root in graph['roots']:
            self.origin_jets[root['node']]=zero_vector
        for i in graph['topological_order']:
            node=graph['nodes'][i];origin=self.origin_jets[i]
            need(origin is not None,'reachable affine origins required')
            obj=scene['objects'][node['hit_object']]
            vertices=[vec(obj['vertices_world_BU'][k]) for k in obj['faces'][0]]
            normal=cross(sub(vertices[1],vertices[0]),sub(vertices[2],vertices[0]))
            direction=vec(node['direction']);denominator=dot(normal,direction)
            need(denominator!=0,'transverse fixed-normal hit required')
            shift=shifts[node['hit_object']]
            dt=tuple(sum((normal[k]*(shift[k][j]-origin[k][j]) for k in range(3)),F(0))/denominator for j in range(self.count))
            point=tuple(tuple(origin[k][j]+direction[k]*dt[j] for j in range(self.count)) for k in range(3))
            self.segment_jets[i],self.point_jets[i]=dt,point
            if 'terminal' in node:
                self.reference_jets[i]=tuple(sum((direction[k]*(shift[k][j]-point[k][j]) for k in range(3)),F(0))/dot(direction,direction) for j in range(self.count))
            for edge in node['edges']:
                target=edge['target'];previous=self.origin_jets[target]
                need(previous is None or previous==point,'merged geometric states have different affine origins; unsupported family')
                self.origin_jets[target]=point

    def _deltas(self,deltas):
        need(len(deltas)==self.count,'complete translation values required')
        values=tuple(F(float(d)) for d in deltas)
        need(all(math.isfinite(float(v)) for v in values),'finite translation values required')
        return values

    def _phase(self,base,jet,norm,deltas):
        wavelength=F(self.graph['wavelength'])
        parameter=F(base)+sum((a*b for a,b in zip(jet,deltas)),F(0))
        cycles=parameter*norm/wavelength
        coefficient=cmath.exp(2j*math.pi*float(cycles%1))
        derivative=np.asarray([float(2*norm*j/wavelength)*math.pi for j in jet])
        return coefficient,derivative

    def forward(self,inputs,deltas,*,gradients=True):
        inputs=np.asarray(inputs,dtype=np.complex128)
        need(inputs.ndim==2 and inputs.shape[1]==len(self.source_ids) and np.isfinite(inputs).all(),'finite complete coherent input batch required')
        deltas=self._deltas(deltas);batch=len(inputs)
        fields=np.zeros((len(self.graph['nodes']),batch),dtype=np.complex128)
        jac=np.zeros((len(self.graph['nodes']),batch,self.count),dtype=np.complex128) if gradients else None
        outputs=np.zeros((batch,len(self.ports)),dtype=np.complex128)
        outjac=np.zeros((batch,len(self.ports),self.count),dtype=np.complex128) if gradients else None
        for column,root in enumerate(self.graph['roots']):fields[root['node']]+=inputs[:,column]
        for i in self.graph['topological_order']:
            node=self.graph['nodes'][i]
            coefficient,angle_jac=self._phase(node['segment_parameter'],self.segment_jets[i],self.norms[i],deltas)
            value=fields[i]*coefficient
            deriv=coefficient*jac[i]+value[:,None]*(1j*angle_jac) if gradients else None
            if 'terminal' in node:
                coefficient,angle_jac=self._phase(node['reference_parameter'],self.reference_jets[i],self.norms[i],deltas)
                port=self.ports.index(node['terminal']);outputs[:,port]+=value*coefficient
                if gradients:outjac[:,port]+=coefficient*deriv+(value*coefficient)[:,None]*(1j*angle_jac)
            for edge in node['edges']:
                coefficient=math.sqrt(float(edge['power']))*(1j**edge['quarter_turns'])*cmath.exp(1j*float(edge['phase_rad']))
                target=edge['target'];fields[target]+=value*coefficient
                if gradients:jac[target]+=deriv*coefficient
        powers=np.abs(outputs)**2
        power_jac=2*np.real(np.conjugate(outputs)[:,:,None]*outjac) if gradients else None
        return {'fields':outputs,'powers':powers,'field_jacobian':outjac,'power_jacobian':power_jac}

    def cross_entropy(self,inputs,labels,deltas,detectors,temperature):
        need(temperature>0 and len(set(detectors))==len(detectors) and set(detectors)<=set(self.ports),'fixed detector subset and positive loss temperature required')
        columns=[self.ports.index(p) for p in detectors]
        result=self.forward(inputs,deltas);scores=result['powers'][:,columns]/temperature
        labels=np.asarray(labels);need(labels.shape==(len(scores),) and np.issubdtype(labels.dtype,np.integer) and np.all((labels>=0)&(labels<len(columns))),'valid training labels required')
        shifted=scores-scores.max(axis=1,keepdims=True)
        exponents=np.exp(shifted);prob=exponents/exponents.sum(axis=1,keepdims=True)
        loss=float(np.mean(np.log(exponents.sum(axis=1))-shifted[np.arange(len(scores)),labels]))
        weights=prob.copy();weights[np.arange(len(scores)),labels]-=1
        gradient=np.einsum('nc,ncp->p',weights/(len(scores)*temperature),result['power_jacobian'][:,columns,:])
        return loss,gradient,result

    def materialize(self,deltas):
        """Exact translated represented geometry/graph for separate validity audit."""
        deltas=self._deltas(deltas);scene,graph=copy.deepcopy(self.scene),copy.deepcopy(self.graph)
        def evaluate(jet):return tuple(sum((a*b for a,b in zip(row,deltas)),F(0)) for row in jet)
        for name,obj in scene['objects'].items():
            change=evaluate(self.shifts[name])
            obj['vertices_world_BU']=[tuple(F(v)+d for v,d in zip(vertex,change)) for vertex in obj['vertices_world_BU']]
            if 'mode_origin_BU' in obj:obj['mode_origin_BU']=tuple(F(v)+d for v,d in zip(obj['mode_origin_BU'],change))
        for i,node in enumerate(graph['nodes']):
            node['origin']=tuple(F(v)+d for v,d in zip(node['origin'],evaluate(self.origin_jets[i])))
            node['point']=tuple(F(v)+d for v,d in zip(node['point'],evaluate(self.point_jets[i])))
            node['segment_parameter']=F(node['segment_parameter'])+sum((a*b for a,b in zip(self.segment_jets[i],deltas)),F(0))
            if 'terminal' in node:node['reference_parameter']=F(node['reference_parameter'])+sum((a*b for a,b in zip(self.reference_jets[i],deltas)),F(0))
            if node['previous_plane'] is not None:
                name,normal,offset=node['previous_plane']
                node['previous_plane']=(name,normal,F(offset)+dot(vec(normal),evaluate(self.shifts[name])))
        graph['translation_family_scope']='Materialized exact virtual translations; new Blender recapture required for native saved geometry'
        return scene,graph
