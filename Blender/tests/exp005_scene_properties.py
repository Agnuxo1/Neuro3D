"""EXP-005 scene-property contract; synthetic CPU validation only.

Consumes a snapshot supplied AFTER a future Blender readback. This module does
not load Blender, generate paths or qualify as an independent scene oracle.
Field propagation here is explicitly Python digital arithmetic.
"""
from dataclasses import dataclass
import cmath
import math
from numbers import Real
from types import MappingProxyType


def finite_number(value, label, *, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f'{label}: numeric value required')
    value = float(value)
    if not math.isfinite(value) or (positive and value <= 0) or (nonnegative and value < 0):
        raise ValueError(f'{label}: invalid finite value')
    return value


@dataclass(frozen=True)
class SceneOptics:
    wavelength_BU: float
    kinds: object
    phases_rad: object
    transmittance: object


def decode_scene(snapshot):
    """No default wavelength or mirror phase, and no fallback to a fixture."""
    wavelength = finite_number(snapshot['lambda_BU'], 'lambda_BU', positive=True)
    objects = snapshot['objects']
    if not isinstance(objects, dict) or not objects:
        raise ValueError('nonempty object map required')
    schema = snapshot.get('schema', 'exp005-readback-v1')
    if schema not in ('exp005-readback-v1','exp005-readback-v2'):
        raise ValueError('unsupported optical readback schema')
    kinds, phases, transmittance = {}, {}, {}
    for name, record in objects.items():
        if not isinstance(name, str) or not name:
            raise ValueError('object identifier required')
        kind = record['kind']
        if kind not in ('mirror', 'bs', 'det', 'escape'):
            raise ValueError(f'unknown optical kind: {name}')
        kinds[name] = kind
        if kind == 'bs':
            if schema == 'exp005-readback-v2':
                value=finite_number(record['power_transmittance'],f'{name}.power_transmittance',nonnegative=True)
                if value>1: raise ValueError('power transmittance must be <=1')
                transmittance[name]=value
            else:
                if 'power_transmittance' in record:
                    raise ValueError('variable splitter requires explicit readback-v2')
                transmittance[name]=.5  # V1 contract is explicitly ideal 50/50.
        if kind == 'mirror':
            phases[name] = finite_number(record['phase_rad'], f'{name}.phase_rad')
    return SceneOptics(wavelength, MappingProxyType(kinds), MappingProxyType(phases),
                       MappingProxyType(transmittance))


def field_for_path(optics, hits, initial_field=1+0j, *, reference_offset_BU=0):
    """Trace coefficients and fields for ONE supplied path, without summing paths.

    Each distance is measured from the previous hit/source to this hit in BU.
    Supported events: t/r on a splitter, mirror, then terminal detect/escape.
    Escape is a declared readout boundary, NOT optical absorption. Its supplied
    distance must reach that boundary; ray generation/oracle remain external.
    """
    field = complex(initial_field)
    if not math.isfinite(field.real) or not math.isfinite(field.imag):
        raise ValueError('finite initial field required')
    if not hits or len(hits) > 64:
        raise ValueError('path must have 1..64 hits')
    trace = []
    length = 0.0
    for index, hit in enumerate(hits):
        name, event = hit['object_id'], hit['event']
        kind = optics.kinds[name]  # unknown object fails, never silently ignored
        distance = finite_number(hit['distance_BU'], 'distance_BU', nonnegative=True)
        if kind == 'bs' and event in ('t', 'r'):
            tau=optics.transmittance[name]
            coefficient = math.sqrt(tau) if event=='t' else 1j*math.sqrt(1-tau)
        elif kind == 'mirror' and event == 'mirror':
            coefficient = -cmath.exp(1j*optics.phases_rad[name])
        elif kind == 'det' and event == 'detect' and index == len(hits)-1:
            coefficient = 1+0j
        elif kind == 'escape' and event == 'escape' and index == len(hits)-1:
            coefficient = 1+0j
        else:
            raise ValueError(f'incompatible event or nonterminal detector: {name}')
        incoming = field * cmath.exp(2j*math.pi*distance/optics.wavelength_BU)
        field = incoming * coefficient
        length += distance
        trace.append({'object_id': name, 'event': event, 'distance_BU': distance,
                      'coefficient': coefficient, 'field_at_hit': incoming,
                      'field_out': field})
    if hits[-1]['event'] not in ('detect','escape'):
        raise ValueError('incomplete path; explicit terminal channel required')
    offset = finite_number(reference_offset_BU, 'reference_offset_BU')
    field *= cmath.exp(2j*math.pi*offset/optics.wavelength_BU)
    return {'field': field, 'length_BU': length, 'reference_offset_BU': offset,
            'hits': trace}


def sum_declared_channels(optics, paths):
    """Coherent ledger, without renormalization or claims of channel orthogonality.

    Caller must demonstrate that each declared terminal represents one common
    phase-reference mode and that distinct channels are orthogonal. That is a
    pending geometry/oracle gate, not something channel names prove.
    Every record needs an explicit initial_field and a complete supplied path.
    """
    if not paths:
        raise ValueError('nonempty path set required')
    # A declared port can be exactly dark because no path reaches it. Keep it
    # explicit; visited-only maps are not a complete transfer-operator readback.
    fields = {name:0j for name,kind in optics.kinds.items() if kind in ('det','escape')}
    counts = {name:0 for name in fields}
    for path in paths:
        result = field_for_path(optics, path['hits'], path['initial_field'],
                                reference_offset_BU=path.get('reference_offset_BU',0))
        name = path['hits'][-1]['object_id']
        fields[name] = fields.get(name, 0j) + result['field']
        counts[name] = counts.get(name, 0) + 1
    powers = {name: abs(field)**2 for name,field in fields.items()}
    return {'fields': fields, 'powers': powers, 'path_counts': counts,
            'detected_power': sum(p for n,p in powers.items() if optics.kinds[n] == 'det'),
            'escape_power': sum(p for n,p in powers.items() if optics.kinds[n] == 'escape')}
