"""Prospective CPU tie-set policy; consumes candidates, NOT a ray tracer.

IDs are snapshot-bound explicit labels, not candidate array positions. This
module does not establish snapshot authenticity or recover filtered-out hits.
No native runner imports it. 'continue' certifies only this policy.
"""
import math
import re
from frontier_inputs import scalar
from primitive_return_guard_v1 import primitive_id

TIE_BU = 1e-9
NORMAL_DOT_TOL = 1e-9


def snapshot_id(value):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('explicit lowercase snapshot SHA256 required')
    return value


def canonical_normal(value):
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise ValueError('three-component finite normal required')
    v = tuple(scalar(x) for x in value)
    length = math.hypot(*v)
    if not 0 < length < float('inf'):
        raise ValueError('finite nonzero normal required')
    n = tuple(x/length for x in v)
    for x in n:
        if x != 0:
            return tuple(-y for y in n) if x < 0 else n
    raise ValueError('nonzero normal required')


def resolve_candidates(*, snapshot_sha256, manifest, candidates, previous):
    """Exact min + inclusive BU band, then conservative immediate-return gate.

    Previous is None for a source, otherwise {snapshot_sha256, primitive_id,
    departure_event}. Candidates have explicit ID, distance_BU and normal.
    A same-previous hit anywhere in the final tie band aborts, NEVER skips.
    A previous hit strictly outside that band is not an immediate-return veto.
    """
    sha = snapshot_id(snapshot_sha256)
    if not isinstance(manifest, (tuple, list)) or not 1 <= len(manifest) <= 64:
        raise ValueError('pilot manifest requires 1..64 primitives')
    objects = {}
    for row in manifest:
        pid = primitive_id(row['primitive_id'])
        obj = row['object_id']
        if pid in objects or not isinstance(obj, str) or not obj:
            raise ValueError('unique primitive IDs and explicit object IDs required')
        objects[pid] = obj
    prior = None
    if previous is not None:
        if not isinstance(previous, dict) or snapshot_id(previous['snapshot_sha256']) != sha:
            raise ValueError('previous primitive belongs to another snapshot')
        prior = primitive_id(previous['primitive_id'])
        if prior not in objects or previous['departure_event'] not in ('mirror', 't', 'r'):
            raise ValueError('valid previous primitive and departure event required')
    if not isinstance(candidates, (tuple, list)) or len(candidates) > len(objects):
        raise ValueError('bounded explicit candidate list required')
    hits = []
    seen = set()
    for row in candidates:
        pid = primitive_id(row['primitive_id'])
        if pid not in objects or pid in seen:
            raise ValueError('candidate primitive must exist exactly once')
        seen.add(pid)
        distance = scalar(row['distance_BU'])
        if distance <= 0:
            raise ValueError('positive finite candidate distance required')
        hits.append((distance, canonical_normal(row['normal']), pid))
    if not hits:
        return {'action': 'miss', 'reason': 'no_candidates', 'selected_primitive': None,
                'minimum_distance_BU': None, 'tie_primitive_ids': []}
    best = min(h[0] for h in hits)
    # Only exact minima select the reference; the band does not move distance.
    winner = min(h for h in hits if h[0] == best)
    band = [h for h in hits if abs(h[0]-best) <= TIE_BU]
    result = {'selected_primitive': winner[2], 'minimum_distance_BU': best,
              'tie_primitive_ids': sorted(h[2] for h in band)}
    if prior in result['tie_primitive_ids']:
        return dict(result, action='abort', reason='previous_primitive_in_nearest_band')
    if any(objects[h[2]] != objects[winner[2]] or
           abs(sum(a*b for a, b in zip(h[1], winner[1]))) < 1-NORMAL_DOT_TOL
           for h in band):
        return dict(result, action='abort', reason='ambiguous_object_or_normal')
    return dict(result, action='continue', reason='tie_policy_only')
