"""Order-independent nearest-hit specification and versioned shader composition.

CPU selection is a test specification only: no hit list is supplied to GPU.
GPU candidate discovers intersections twice from raw scene triangles. Existing
shared shader stays immutable. Bias/terminal-mode limitations are NOT repaired.
"""
from dataclasses import dataclass
import hashlib
import math
from pathlib import Path

BASE = Path(__file__).parents[2] / 'shaders' / 'exp005_shared_frontier.glsl'
PART = BASE.with_name('exp005_nearest_v2.glsl')
BASE_SHA = '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1'
TIE_BU = 1e-9
NORMAL_TOL = 1e-9


@dataclass(frozen=True)
class Candidate:
    distance_BU: float
    object_id: int
    normal: tuple


def select(candidates):
    """Exact global minimum first; inclusive tie band around THAT minimum.

Candidates belong to forward intersections after the unchanged ray bias.
Bad candidates reject the entire query, never disappear as a miss.
"""
    candidates = tuple(candidates)
    for item in candidates:
        if (isinstance(item.distance_BU, bool) or not isinstance(item.distance_BU, (int, float))
                or not math.isfinite(item.distance_BU) or item.distance_BU <= 1e-9
                or isinstance(item.object_id, bool) or not isinstance(item.object_id, int)
                or item.object_id < 0 or len(item.normal) != 3
                or any(isinstance(x, bool) or not isinstance(x, (int, float))
                       or not math.isfinite(x) for x in item.normal)
                or abs(math.hypot(*item.normal) - 1) > 1e-12):
            raise ValueError('valid finite forward hit, object ID and unit normal required')
    if not candidates:
        return None, False
    def canonical(normal):
        first = next(x for x in normal if x != 0)
        return tuple(-x for x in normal) if first < 0 else tuple(normal)
    # Equal-distance triangles of ONE object may have slightly different
    # normals. A canonical, winding-independent tie-break prevents even the
    # ambiguity decision from depending on which triangle appears first.
    winner = min(candidates, key=lambda h: (h.distance_BU, canonical(h.normal)))
    near = (h for h in candidates if abs(h.distance_BU - winner.distance_BU) <= TIE_BU)
    ambiguous = any(h.object_id != winner.object_id or
                    abs(sum(a*b for a, b in zip(h.normal, winner.normal))) < 1-NORMAL_TOL
                    for h in near)
    # When ambiguous, identity/normal must never be consumed as a valid hit.
    return winner, ambiguous


def shader_source():
    raw = BASE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASE_SHA:
        raise ValueError('immutable base shader changed; explicit new version required')
    source = raw.decode('utf-8')
    signature = 'void nearest(dvec3 origin,dvec3 d,out double best,out int object,out dvec3 normal,out bool ambiguous) {'
    if source.count(signature) != 1 or source.count('\nvoid main() {') != 1:
        raise ValueError('unrecognized frozen shader structure')
    start = source.index(signature)
    end = source.index('\nvoid main() {', start)
    return source[:start] + PART.read_text(encoding='utf-8') + source[end:]


def native_shader(gpu):
    """New opt-in compiled variant. Not called by any existing benchmark."""
    info = gpu.types.GPUShaderCreateInfo()
    for slot, name in enumerate(('geometry_hi', 'geometry_lo', 'sources_hi',
                                 'sources_lo', 'optics_hi', 'optics_lo')):
        info.sampler(slot, 'FLOAT_2D', name)
    for slot, name in enumerate(('fields_out', 'stats_out', 'ledger_out', 'work_out')):
        info.image(slot, 'RGBA32F', 'FLOAT_2D', name, qualifiers={'WRITE'})
    for name in ('triangle_count', 'source_count', 'port_count', 'max_steps', 'max_depth'):
        info.push_constant('INT', name)
    for name in ('wavelength_hi', 'wavelength_lo'):
        info.push_constant('FLOAT', name)
    info.local_group_size(1, 1, 1)
    info.compute_source(shader_source())
    return gpu.shader.create_from_info(info)
