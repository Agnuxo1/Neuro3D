"""Prepared raw-scene batch ABI only; NO GPU batch backend implemented here.

Shared immutable geometry/properties, distinct coherent source inputs.
No path list, transfer matrix, phase, reflection or intensity computations.
"""
from dataclasses import dataclass
from resident_frontier_gpu import SceneBinding


@dataclass(frozen=True)
class FrontierBatch:
    geometry: object
    optics: tuple
    sources: tuple  # input-major/source-major, eight scalars per source
    source_ids: tuple
    ports: tuple
    wavelength_BU: float
    input_count: int

    def estimated_texture_bytes(self):
        # Exact format footprint for proposed RGBA32F hi/lo transport and
        # outputs; NOT total allocation/VRAM usage incl driver/temporaries.
        padded=lambda n:max(256,((n+255)//256)*256)
        raw=2*4*sum(padded(len(x)) for x in (self.geometry.triangles,self.optics,self.sources))
        count=len(self.ports)
        outputs=self.input_count*16*(count*2+count*128+1)
        return raw+outputs


def pack_batch(snapshots,*,mode_cap=3):
    if not isinstance(snapshots,(list,tuple)) or not 1<=len(snapshots)<=32:
        raise ValueError('one to32 raw coherent inputs required')
    binding=SceneBinding(snapshots[0],mode_cap)
    batches=[binding.inputs(snapshot) for snapshot in snapshots]
    base=binding.batch
    return FrontierBatch(base.geometry,base.optics,tuple(v for b in batches for v in b.sources),
                         base.source_ids,base.ports,base.wavelength_BU,len(batches))
