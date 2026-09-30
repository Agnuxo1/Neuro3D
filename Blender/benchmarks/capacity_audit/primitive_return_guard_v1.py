"""CPU-only conservative candidate rule, not a native fix or exclusion filter.

After straight departure from an ideal static triangle, an immediate return to
that same triangle is numerically suspect. Abort, never silently skip it.
Different primitives of the SAME object are not excluded by this rule.
"""
from frontier_inputs import scalar


def primitive_id(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < 64:
        raise ValueError('explicit global pilot triangle ID in [0,64) required')
    return value


def classify_return(*, previous_primitive, candidate_primitive,
                    departure_event, distance_BU):
    candidate = primitive_id(candidate_primitive)
    distance = scalar(distance_BU)
    if distance <= 0:
        raise ValueError('positive finite candidate distance required')
    if previous_primitive is None:
        if departure_event is not None:
            raise ValueError('source ray has no previous departure event')
        return {'action': 'continue', 'reason': 'source_ray'}
    previous = primitive_id(previous_primitive)
    if departure_event not in ('mirror', 't', 'r'):
        raise ValueError('explicit ideal straight-ray departure event required')
    if previous == candidate:
        return {'action': 'abort', 'reason': 'immediate_same_triangle_return'}
    return {'action': 'continue', 'reason': 'different_triangle_not_excluded'}
