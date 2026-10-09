"""Own coherent forward/Jacobian compiled from complete geometric path ledgers.

Geometry, source/detector modes and wavelength stay fixed during this phase/tau
training family. Every nonzero source is enumerated once. No learned transfer
matrix, label or analytic circuit is an input. This is a linear complex field
map followed by modal square-law detectors; no optical nonlinearity is claimed.
Native sin/cos/sqrt estimates are NOT error certificates or physical fidelity.
"""
import cmath
import copy
from fractions import Fraction as F
import math

from Blender.benchmarks.capacity_audit.exact_object_index_v1 import trace_scene_indexed
from .scene_capture_v1 import digest,need
from .scalar_scene_ingress_v1 import rational_wire


def finite_real(value):
    need(isinstance(value,(int,float,F)) and not isinstance(value,bool),'finite represented scalar required')
    result=float(value)
    need(math.isfinite(result),'finite represented scalar required')
    return result


def stable_propagation_phase(path,wavelength):
    """Reduce exact cycles before native trig when ray norm has a rational root."""
    norm=F(path['direction_norm_squared'])
    a,b=math.isqrt(norm.numerator),math.isqrt(norm.denominator)
    cycles=F(path['phase_length_numerator'])/F(wavelength)
    if a*a==norm.numerator and b*b==norm.denominator:
        return 2*math.pi*float((cycles/F(a,b))%1)
    return math.remainder(2*math.pi*float(cycles)/math.sqrt(float(norm)),2*math.pi)


class GeometricNetwork:
    """Fixed-geometry path operator; phase/tau controls preserve branch support."""
    def __init__(self,scene,*,phase_objects=(),tau_objects=(),max_rays=4096,max_depth=64):
        snapshot=copy.deepcopy(scene)
        need(snapshot.get('schema')=='exp005-readback-v2','explicit v2 optical coefficients required')
        self.scene_sha256=digest(rational_wire(snapshot))
        self.source_ids=tuple(s['id'] for s in snapshot['sources'])
        need(len(set(self.source_ids))==len(self.source_ids),'unique source IDs required')
        self.phase_objects=tuple(phase_objects)
        self.tau_objects=tuple(tau_objects)
        self.parameters=tuple('phase:'+n for n in self.phase_objects)+tuple('tau:'+n for n in self.tau_objects)
        need(len(set(self.parameters))==len(self.parameters),'unique parameter bindings required')
        self.initial={}
        for name in self.phase_objects:
            need(name in snapshot['objects'] and snapshot['objects'][name]['kind']=='mirror','phase must bind actual mirror')
            self.initial['phase:'+name]=finite_real(snapshot['objects'][name]['phase_rad'])
        for name in self.tau_objects:
            need(name in snapshot['objects'] and snapshot['objects'][name]['kind']=='bs','tau must bind actual splitter')
            tau=finite_real(snapshot['objects'][name]['power_transmittance'])
            need(0<tau<1,'trainable tau must preserve nonzero branch support')
            self.initial['tau:'+name]=tau
        # Compilation stimulus enumerates paths for every source, including a
        # source whose requested inference field is zero. It is not training data.
        for source in snapshot['sources']:
            source['field_reim']=[1,0]
        trace=trace_scene_indexed(snapshot,max_rays=max_rays,max_depth=max_depth)
        need(trace['status']=='COMPLETE','cannot compile incomplete traversal')
        self.paths=trace['paths']
        self.ports=tuple(trace['ports'])
        self.wavelength=snapshot['lambda_BU']
        self.objects=copy.deepcopy(snapshot['objects'])
        self.propagation_phases=tuple(stable_propagation_phase(p,self.wavelength) for p in self.paths)
        self.compilation={'scene_sha256':self.scene_sha256,'source_count':len(self.source_ids),
                          'path_count':len(self.paths),'rays':trace['rays'],
                          'selection_statistics':trace['selection_statistics'],
                          'geometry_fixed_during_training':True,'all_nonzero_branches_traversed':True,
                          'native_field_certified':False,'physical_optics_certified':False,
                          'capture_state_sha256':snapshot.get('blender_lab_ingress',{}).get('capture_state_sha256')}

    def validate_values(self,values):
        need(isinstance(values,dict) and set(values)==set(self.parameters),'complete explicit parameter mapping required')
        result={k:finite_real(v) for k,v in values.items()}
        need(all(0<result['tau:'+n]<1 for n in self.tau_objects),'tau updates must preserve nonzero branch support')
        return result

    def forward(self,fields,values=None,*,jacobian=False):
        need(isinstance(fields,dict) and set(fields)==set(self.source_ids),'complete explicit coherent fields required')
        amplitudes={}
        for sid,field in fields.items():
            need(isinstance(field,(list,tuple)) and len(field)==2,'explicit real/imag input field required')
            amplitudes[sid]=complex(finite_real(field[0]),finite_real(field[1]))
        parameters=self.validate_values(dict(self.initial) if values is None else values)
        contributions={p:[] for p in self.ports}
        derivatives={k:{p:[] for p in self.ports} for k in self.parameters} if jacobian else {}
        for path,propagation in zip(self.paths,self.propagation_phases):
            phase=propagation+path['quarter_turns']*math.pi/2
            power=F(1)
            phase_counts={}
            tau_counts={}
            for hit in path['hits']:
                name,event=hit['object_id'],hit['event']
                obj=self.objects[name]
                if event=='mirror':
                    key='phase:'+name
                    phase+=parameters[key] if name in self.phase_objects else finite_real(obj['phase_rad'])
                    if name in self.phase_objects:
                        phase_counts[key]=phase_counts.get(key,0)+1
                elif event in ('t','r'):
                    key='tau:'+name
                    tau=parameters[key] if name in self.tau_objects else F(obj['power_transmittance'])
                    power*=tau if event=='t' else 1-tau
                    if name in self.tau_objects:
                        counts=tau_counts.setdefault(key,[0,0])
                        counts[0 if event=='t' else 1]+=1
            coefficient=math.sqrt(float(power))*cmath.exp(1j*phase)
            value=amplitudes[path['source_id']]*coefficient
            port=path['terminal']
            contributions[port].append(value)
            if jacobian:
                for key,count in phase_counts.items():
                    derivatives[key][port].append(1j*count*value)
                for key,(nt,nr) in tau_counts.items():
                    tau=parameters[key]
                    derivatives[key][port].append((nt/(2*tau)-nr/(2*(1-tau)))*value)
        def coherent_sum(values):
            return complex(math.fsum(v.real for v in values),math.fsum(v.imag for v in values))
        outputs={p:coherent_sum(v) for p,v in contributions.items()}
        powers={p:abs(v)**2 for p,v in outputs.items()}
        result={'fields':outputs,'powers':powers,'field_certified':False,'physical_optics_certified':False}
        if jacobian:
            df={k:{p:coherent_sum(v) for p,v in ports.items()} for k,ports in derivatives.items()}
            dp={k:{p:2*(outputs[p].conjugate()*df[k][p]).real for p in self.ports} for k in self.parameters}
            result.update(field_jacobian=df,power_jacobian=dp)
        return result

    def power_mse(self,samples,values=None):
        """Fixed detector readout; no fitting of labels, encoders or matrix weights."""
        need(isinstance(samples,(list,tuple)) and samples,'nonempty declared training batch required')
        values=self.validate_values(dict(self.initial) if values is None else values)
        loss=0.0
        gradient={k:0.0 for k in self.parameters}
        count=0
        for fields,targets in samples:
            need(isinstance(targets,dict) and targets and set(targets)<=set(self.ports),'declared detector targets required')
            result=self.forward(fields,values,jacobian=True)
            for port,target in targets.items():
                target=finite_real(target)
                need(target>=0,'nonnegative detector target required')
                residual=result['powers'][port]-target
                loss+=residual*residual
                count+=1
                for key in self.parameters:
                    gradient[key]+=2*residual*result['power_jacobian'][key][port]
        return loss/count,{k:v/count for k,v in gradient.items()}
