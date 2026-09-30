"""Bounded raw-hit ABI for a future GPU consumer, no CPU field propagation.

Geometry remains external. Validation/packing copies distances and scene phases;
it does not compute coefficients, path phases, complex sums or intensities.
"""
from dataclasses import dataclass
import math
import struct

from exp005_scene_properties import decode_scene, finite_number

MAX_PATHS = 512
MAX_HITS_PER_PATH = 64
PATH_STRIDE = 8
HIT_STRIDE = 4


@dataclass(frozen=True)
class PackedPaths:
    ports: tuple
    wavelength: float
    paths: tuple
    hits: tuple

    @property
    def path_count(self):
        return len(self.paths) // PATH_STRIDE

    def buffers(self):
        return (struct.pack(f'<{len(self.paths)}d', *self.paths),
                struct.pack(f'<{len(self.hits)}d', *self.hits))


def finite_complex(value):
    if isinstance(value, (list, tuple)):
        if len(value) != 2:
            raise ValueError('complex pair requires exactly two values')
        value = complex(*(finite_number(v, 'field') for v in value))
    elif isinstance(value, bool) or not isinstance(value, (complex, int, float)):
        raise ValueError('complex field required')
    value = complex(value)
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise ValueError('finite complex field required')
    return value


def pack_paths(snapshot, paths):
    optics = decode_scene(snapshot)
    ports = tuple(name for name, kind in optics.kinds.items() if kind in ('det', 'escape'))
    if not ports or not 1 <= len(paths) <= MAX_PATHS:
        raise ValueError('bounded nonempty paths and declared ports required')
    sources = {source['id']: finite_complex(source['field_reim']) for source in snapshot['sources']}
    if len(sources) != len(snapshot['sources']):
        raise ValueError('duplicate source ID')
    metadata, events = [], []
    for path in paths:
        initial = finite_complex(path['initial_field'])
        if sources[path['source_id']] != initial:
            raise ValueError('path field differs from supplied source input')
        hits = path['hits']
        if not 1 <= len(hits) <= MAX_HITS_PER_PATH:
            raise ValueError('bounded complete hit history required')
        start = len(events) // HIT_STRIDE
        for index, hit in enumerate(hits):
            name, event = hit['object_id'], hit['event']
            kind = optics.kinds[name]
            distance = finite_number(hit['distance_BU'], 'distance_BU', nonnegative=True)
            phase,parameter = 0.0,0.0
            if kind == 'bs' and event in ('t', 'r'):
                if snapshot.get('schema')=='exp005-readback-v2':
                    code = 4 if event=='t' else 5
                    parameter=optics.transmittance[name]  # Raw property, NOT sqrt/field.
                else:
                    code = 1 if event == 't' else 2
            elif kind == 'mirror' and event == 'mirror':
                code, phase = 3, optics.phases_rad[name]
            elif kind in ('det', 'escape') and event == ('detect' if kind == 'det' else 'escape') and index == len(hits)-1:
                code = 0
            else:
                raise ValueError('incompatible event or nonterminal readout')
            events.extend((distance, phase, float(code), parameter))
        terminal = hits[-1]['object_id']
        if terminal not in ports or hits[-1]['event'] not in ('detect', 'escape'):
            raise ValueError('explicit terminal required')
        offset = finite_number(path.get('reference_offset_BU', 0), 'reference_offset_BU')
        metadata.extend((float(ports.index(terminal)), float(start), float(len(hits)),
                         initial.real, initial.imag, offset, 0.0, 0.0))
    return PackedPaths(ports, optics.wavelength_BU, tuple(metadata), tuple(events))
