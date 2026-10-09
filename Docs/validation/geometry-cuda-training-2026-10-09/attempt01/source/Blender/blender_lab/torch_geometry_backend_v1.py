"""Torch coherent graph execution and own forward Jacobian on CPU or CUDA.

Exact represented geometry/affine phase arguments are prepared on CPU. Complex
phase evaluation, square roots, graph transport, power and manual chain rule
execute on the selected device. Autograd is a separate control, not training.
"""
from fractions import Fraction as F
import math


class TorchGeometryBackend:
    def __init__(self,network,device):
        import torch
        self.torch=torch;self.network=network;self.device=torch.device(device)
        self.edges=[];self.by_node=[[] for _ in network.graph['nodes']]
        for i,node in enumerate(network.graph['nodes']):
            for edge in node['edges']:
                k=len(self.edges);self.edges.append(edge);self.by_node[i].append((k,edge['target']))
        power=torch.tensor([float(e['power']) for e in self.edges],dtype=torch.float64,device=self.device)
        phase=torch.tensor([float(e['phase_rad']) for e in self.edges],dtype=torch.float64,device=self.device)
        quarter=torch.tensor([1j**e['quarter_turns'] for e in self.edges],dtype=torch.complex128,device=self.device)
        self.edge_coefficients=power.sqrt()*quarter*torch.complex(phase.cos(),phase.sin())

    def prepare(self,deltas):
        net=self.network;deltas=net._deltas(deltas);wavelength=F(net.graph['wavelength'])
        angles=[];jac=[];refs=[];refjac=[]
        def phase(base,jet,norm):
            parameter=F(base)+sum((a*b for a,b in zip(jet,deltas)),F(0))
            return 2*math.pi*float((parameter*norm/wavelength)%1),[2*math.pi*float(norm*a/wavelength) for a in jet]
        for i,node in enumerate(net.graph['nodes']):
            a,j=phase(node['segment_parameter'],net.segment_jets[i],net.norms[i]);angles.append(a);jac.append(j)
            a,j=phase(node.get('reference_parameter',0),net.reference_jets[i] or tuple(F(0) for _ in deltas),net.norms[i]);refs.append(a);refjac.append(j)
        return angles,jac,refs,refjac

    def upload(self,prepared):
        return tuple(self.torch.tensor(a,dtype=self.torch.float64,device=self.device) for a in prepared)

    def forward(self,inputs,packed,*,gradients=True):
        torch=self.torch;net=self.network;angles,jac,refs,refjac=packed
        if not torch.is_tensor(inputs):inputs=torch.tensor(inputs,dtype=torch.complex128,device=self.device)
        if inputs.device!=self.device or inputs.dtype!=torch.complex128 or inputs.ndim!=2 or inputs.shape[1]!=len(net.source_ids):
            raise ValueError('complete complex128 input on selected device required')
        if not torch.isfinite(inputs).all().item():
            raise ValueError('finite coherent input values required')
        batch=len(inputs)
        segment=torch.complex(angles.cos(),angles.sin());reference=torch.complex(refs.cos(),refs.sin())
        fields=torch.zeros((len(net.graph['nodes']),batch),dtype=torch.complex128,device=self.device)
        derivatives=torch.zeros((len(net.graph['nodes']),batch,net.count),dtype=torch.complex128,device=self.device) if gradients else None
        output=torch.zeros((batch,len(net.ports)),dtype=torch.complex128,device=self.device)
        outjac=torch.zeros((batch,len(net.ports),net.count),dtype=torch.complex128,device=self.device) if gradients else None
        for column,root in enumerate(net.graph['roots']):fields[root['node']]+=inputs[:,column]
        for i in net.graph['topological_order']:
            node=net.graph['nodes'][i];value=fields[i]*segment[i]
            derivative=derivatives[i]*segment[i]+value[:,None]*(1j*jac[i]) if gradients else None
            if 'terminal' in node:
                p=net.ports.index(node['terminal']);output[:,p]+=value*reference[i]
                if gradients:outjac[:,p]+=derivative*reference[i]+(value*reference[i])[:,None]*(1j*refjac[i])
            for k,target in self.by_node[i]:
                fields[target]+=value*self.edge_coefficients[k]
                if gradients:derivatives[target]+=derivative*self.edge_coefficients[k]
        powers=output.abs()**2
        pjac=2*(output.conj()[:,:,None]*outjac).real if gradients else None
        return {'fields':output,'powers':powers,'field_jacobian':outjac,'power_jacobian':pjac}

    def autograd_reference(self,inputs,packed,weights):
        """Independent functional accumulation/control for a weighted power loss."""
        torch=self.torch;net=self.network;angles,jac,refs,refjac=packed
        delta=torch.zeros(net.count,dtype=torch.float64,device=self.device,requires_grad=True)
        phase=angles+jac@delta;refphase=refs+refjac@delta
        segment=torch.complex(phase.cos(),phase.sin());reference=torch.complex(refphase.cos(),refphase.sin())
        incoming=[[] for _ in net.graph['nodes']];outputs=[[] for _ in net.ports]
        for column,root in enumerate(net.graph['roots']):incoming[root['node']].append(inputs[:,column])
        for i in net.graph['topological_order']:
            node=net.graph['nodes'][i];value=sum(incoming[i])*segment[i]
            if 'terminal' in node:outputs[net.ports.index(node['terminal'])].append(value*reference[i])
            for k,target in self.by_node[i]:incoming[target].append(value*self.edge_coefficients[k])
        fields=torch.stack([sum(v,torch.zeros_like(inputs[:,0])) for v in outputs],dim=1)
        loss=(fields.abs()**2*weights).sum();gradient=torch.autograd.grad(loss,delta)[0]
        return fields,gradient
