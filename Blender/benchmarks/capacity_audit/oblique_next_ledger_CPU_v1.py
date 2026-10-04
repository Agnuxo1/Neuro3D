"""Opt-in comparison-only next-query ledger. No producer replay or GPU admission."""
from fractions import Fraction as F

def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def power2(exponent):
    return F(2**exponent) if exponent >= 0 else F(1, 2**(-exponent))


MAX64 = (2 - power2(-52)) * power2(1023)


def round_out(value, upper):
    """Directed finite binary64 value, derived with integers, not host floats."""
    require(type(value) is F and type(upper) is bool, "round_type")
    if value == 0:
        return F(0)
    require(abs(value) <= MAX64, "STOP_OVERFLOW")
    magnitude = abs(value)
    exponent = magnitude.numerator.bit_length() - magnitude.denominator.bit_length()
    if magnitude < power2(exponent):
        exponent -= 1
    step = power2(max(exponent - 52, -1074))
    scaled = value / step
    q, remainder = divmod(scaled.numerator, scaled.denominator)
    result = (q + int(upper and remainder != 0)) * step
    require(abs(result) <= MAX64, "STOP_OVERFLOW")
    return result


HIT = "CONDITIONAL_TRIANGLE_INTERIOR_HIT"
MISS = "CONDITIONAL_TRIANGLE_MISS"
CONTACT = "STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED"
DET_ZERO = "STOP_TRIANGLE_DETERMINANT_ZERO_POSSIBLE"


def interval(pair):
    require(type(pair) is tuple and len(pair) == 2 and all(type(x) is F for x in pair),
            "STOP_INTERVAL_TYPE")
    require(all(x.numerator.bit_length() <= 4096 and x.denominator.bit_length() <= 4096
                for x in pair), "STOP_INTERVAL_CAPACITY")
    require(pair[0] <= pair[1], "STOP_INTERVAL_REVERSED")
    require(all(round_out(x, False) == x == round_out(x, True) for x in pair),
            "STOP_INTERVAL_NOT_FINITE_BINARY64")
    return pair


def primitive_id(value):
    require(type(value) is int and 0 <= value < 2**32, "STOP_PRIMITIVE_ID")


def binding_key(binding):
    require(type(binding) is tuple and len(binding) == 4, "STOP_BINDING_SHAPE")
    for value in binding[:3]:
        require(type(value) is str and len(value) == 64
                and all(c in "0123456789abcdef" for c in value), "STOP_DIGEST")
    require(type(binding[3]) is str and binding[3] in ("S0", "S1"), "STOP_SOURCE")
    return binding


def classification(bounds):
    require(type(bounds) is tuple and len(bounds) in (1, 5), "STOP_SCALAR_GRID")
    values = tuple(interval(x) for x in bounds)
    if values[0][0] <= 0 <= values[0][1]:
        require(len(values) == 1, "STOP_DET_ZERO_EXTRA_SCALARS")
        return DET_ZERO
    require(len(values) == 5, "STOP_MISSING_SCALARS")
    det, tau, u, v, uv = values
    if tau[1] < 0 or u[1] < 0 or v[1] < 0 or uv[0] > 1:
        return MISS
    if tau[0] > 0 and u[0] > 0 and v[0] > 0 and uv[1] < 1:
        return HIT
    return CONTACT


def audit_source(binding, expected_ids, previous_id, rows):
    """Labels are not authentication. Every unresolved row blocks candidate output."""
    binding_key(binding)
    require(type(expected_ids) is tuple and 2 <= len(expected_ids) <= 4,
            "STOP_ORIGINAL_ID_TABLE_SHAPE")
    for value in expected_ids:
        primitive_id(value)
    require(len(set(expected_ids)) == len(expected_ids), "STOP_DUPLICATE_EXPECTED_ID")
    primitive_id(previous_id)
    require(previous_id in expected_ids, "STOP_PREVIOUS_ID_ABSENT")
    require(type(rows) is tuple and len(rows) == len(expected_ids), "STOP_ALL_ROWS_COUNT")
    hits, misses, stops, seen = [], [], [], []
    for row in rows:
        require(type(row) is tuple and len(row) == 4, "STOP_ROW_SHAPE")
        key, pid, status, bounds = row
        binding_key(key)
        require(key == binding, "STOP_CROSS_INPUT_SCENE_QUERY_SOURCE")
        primitive_id(pid)
        require(type(status) is str and status == classification(bounds),
                "STOP_CLASSIFICATION_MISMATCH")
        seen.append(pid)
        if status == HIT:
            hits.append((pid, bounds[1]))
        elif status == MISS:
            misses.append(pid)
        else:
            stops.append(pid)
    require(len(set(seen)) == len(seen), "STOP_DUPLICATE_ROW")
    require(tuple(seen) == expected_ids, "STOP_ALL_ORDERED_IDS")
    relations = []
    for index, (a, ai) in enumerate(hits):
        for b, bi in hits[index + 1:]:
            if ai[1] < bi[0]:
                rel = "A_STRICTLY_BEFORE_B"
            elif bi[1] < ai[0]:
                rel = "B_STRICTLY_BEFORE_A"
            else:
                rel = "STOP_OVERLAP_OR_TOUCH"
            relations.append(dict(a=a, b=b, relation=rel))
    candidate = None
    if stops:
        status = "STOP_UNRESOLVED_ALL_PRIMITIVES"
    elif not hits:
        status = "CONDITIONAL_NO_FORWARD_TRIANGLE_ON_DECLARED_LEDGER"
    else:
        candidates = [pid for pid, bounds in hits
                      if all(pid == other or bounds[1] < other_bounds[0]
                             for other, other_bounds in hits)]
        if len(candidates) == 1:
            candidate = candidates[0]
            status = "CONDITIONAL_UNIQUE_FIRST_ON_DECLARED_LEDGER"
        else:
            status = "STOP_FIRST_ORDER_UNRESOLVED"
    return dict(status=status, binding=list(binding), expected_ids=list(expected_ids),
                previous_primitive_id=previous_id, audited_rows=len(rows),
                conditional_first_id=candidate, interior_ids=[pid for pid, b in hits],
                conditional_miss_ids=misses, unresolved_ids=stops,
                interior_pair_relations=relations, ignored_primitive_ids=[],
                source_merged=False, origin_offset_applied=False,
                upstream_binding_authenticated=False, nearest_hit_certified=False,
                launch_exclusion_allowed=False, native_precision_certified=False,
                full_path_visibility_certified=False, phase_certified=False,
                phase_error_bound=None, GPU_used=False, GPU_launch_allowed=False,
                parameter_units="unnormalized_reflected_direction_parameter_NOT_BU_length",
                full_costs="UNKNOWN_NOT_ZERO", new_intersections=0,
                old_producer_replays=0)
