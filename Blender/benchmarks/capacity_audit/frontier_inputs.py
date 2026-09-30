"""CPU transport ABI only: raw scene sources/geometry/properties, no paths.

Not a GPU propagator. Explicit ideal v1 50/50 or mandatory scene-owned v2 T.
No import-time GPU, reflection, distance, phase or field computation.
"""
from dataclasses import dataclass
import math
from numbers import Real
from gpu_geometry_probe import GeometryBatch,pack_geometry,vector


def scalar(value):
    if isinstance(value,bool) or not isinstance(value,Real) or not math.isfinite(value):
        raise ValueError('finite real scene property required')
    return float(value)


@dataclass(frozen=True)
class FrontierInputs:
    geometry: GeometryBatch
    sources: tuple  # origin xyz, field real, raw direction xyz, field imag
    optics: tuple  # role/T/phase/port; reference xyz/0; raw mode direction xyz/0
    source_ids: tuple
    ports: tuple
    wavelength_BU: float


def pack_frontier(snapshot):
    if not 1<=len(snapshot['sources'])<=3: raise ValueError('pilot requires one to three sources')
    wavelength=scalar(snapshot['lambda_BU'])
    if wavelength<=0: raise ValueError('positive scene wavelength required')
    sources=[]; ids=[]; queries=[]
    for source in snapshot['sources']:
        sid=source['id']
        if not isinstance(sid,str) or not sid or sid in ids: raise ValueError('unique source IDs required')
        ids.append(sid); origin=vector(source['position_BU']); direction=vector(source['direction'])
        if math.hypot(*direction)==0: raise ValueError('nonzero source direction required')
        pair=source['field_reim']
        if len(pair)!=2: raise ValueError('explicit complex source field required')
        real,imag=map(scalar,pair)
        sources.extend((*origin,real,*direction,imag))
        queries.append({'origin_BU':origin,'direction':direction})
    geometry=pack_geometry(snapshot,queries)
    if geometry.triangle_count>64: raise ValueError('pilot triangle bound exceeded')
    ports=tuple(n for n,o in snapshot['objects'].items() if o['kind'] in ('det','escape'))
    if not 1<=len(ports)<=3: raise ValueError('pilot requires one to three terminal ports')
    optics=[]
    for name,obj in snapshot['objects'].items():
        kind=obj['kind']; code={'bs':0,'mirror':1,'det':2,'escape':3}[kind]
        tau=0.; phase=0.; port=-1.; reference=(0.,0.,0.); axis=(0.,0.,0.)
        if kind=='bs':
            if snapshot['schema']=='exp005-readback-v2': tau=scalar(obj['power_transmittance'])
            else:
                if 'power_transmittance' in obj: raise ValueError('variable splitter requires v2')
                tau=.5  # Explicit ideal v1 definition, not a missing-v2 fallback.
            if not 0<=tau<=1: raise ValueError('power transmittance must be in [0,1]')
        if kind=='mirror': phase=scalar(obj['phase_rad'])
        if kind in ('det','escape'):
            port=float(ports.index(name)); reference=vector(obj['mode_origin_BU']); axis=vector(obj['mode_direction'])
            if math.hypot(*axis)==0: raise ValueError('nonzero terminal direction required')
        optics.extend((float(code),tau,phase,port,*reference,0.,*axis,0.))
    return FrontierInputs(geometry,tuple(sources),tuple(optics),tuple(ids),ports,wavelength)
