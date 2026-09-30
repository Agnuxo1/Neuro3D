"""Opt-in coordinate transport prototype; never activated by a GPU runner.

Translation of every source, triangle and terminal reference together. Does not
trace rays, change optical coefficients, compute phase or supply cached outputs.
The returned metadata must accompany evidence: local coordinates are NOT raw
Blender world coordinates. Float64 export loss cannot be recovered here.
"""
import copy
from frontier_inputs import pack_frontier


def local_frame(snapshot, *, mode_cap=3):
    # Both original and translated ABI bounds must hold; do not expand limits.
    pack_frontier(snapshot, mode_cap=mode_cap)
    origin = tuple(snapshot['sources'][0]['position_BU'])
    result = copy.deepcopy(snapshot)
    def point(values): return [x-y for x, y in zip(values, origin)]
    for source in result['sources']:
        source['position_BU'] = point(source['position_BU'])
    for obj in result['objects'].values():
        obj['vertices_world_BU'] = [point(v) for v in obj['vertices_world_BU']]
        if obj['kind'] in ('det', 'escape'):
            obj['mode_origin_BU'] = point(obj['mode_origin_BU'])
    pack_frontier(result, mode_cap=mode_cap)
    return result, {'origin_BU': list(origin), 'kind': 'translation_only_transport_prototype',
                    'preserved': 'wavelength, directions, fields, optics, IDs, faces',
                    'scope': 'CPU export/frame conversion, NOT GPU inference or Blender mutation'}
