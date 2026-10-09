"""No native execution: byte pins, exact source anchors, and unknown preservation."""
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Blender.benchmarks.capacity_audit import first_leg_frozen_shader_static_audit_HOST_v1 as m

records = []


def negative(label, blobs):
    try:
        m.audit(blobs)
    except (ValueError, TypeError, KeyError) as ex:
        records.append(dict(kind="NEGATIVE", id=label, reason=str(ex)))
    else:
        raise AssertionError(label)


def test_source_mapping():
    result = m.run()
    assert result["status"] == "STATIC_SOURCE_PATH_DIFFERS_FROM_HYPOTHETICAL_ENDPOINT_NORM_GRAPH"
    assert not result["native_IEEE_graph_identity_verified"] and not result["phase_certified"]
    assert result["native_first_leg_error_bound_BU"] is None and result["promotion"] == "STOP"
    assert result["shader_compilations"] == result["geometry_evaluations"] == result["old_producer_replays"] == 0
    assert not result["GPU_used"] and not result["Bpy_used"] and not result["RT_used"]
    records.append(dict(kind="PINNED_STATIC_AUDIT", result=result))


def test_pin_and_shape_rejections():
    originals = {p: (m.ROOT/p).read_bytes() for p in m.PINS}
    for path in originals:
        changed = copy.deepcopy(originals); changed[path] += b"\n// changed\n"
        negative("changed_bytes:"+path, changed)
        changed = copy.deepcopy(originals); changed[path] = changed[path].decode("utf-8")
        negative("not_bytes:"+path, changed)
    changed = copy.deepcopy(originals); del changed[m.MODEL]
    negative("missing_model", changed)
    changed = copy.deepcopy(originals); changed["unrequested_backend"] = b"shader"
    negative("extra_backend", changed)
    changed = copy.deepcopy(originals)
    changed[m.SHADER] = changed[m.SHADER].replace(b"double length=ray.length+distance;", b"double length=length(point-ray.o);")
    negative("endpoint_norm_replacement_not_same_shader", changed)
    changed = copy.deepcopy(originals)
    changed[m.SHADER] = changed[m.SHADER].replace(b"best+=BIAS;", b"best+=0.0lf;")
    negative("BIAS_removal_not_same_shader", changed)


if __name__ == "__main__":
    test_source_mapping(); test_pin_and_shape_rejections()
    print(json.dumps(dict(status="PASS", tests=2, records=records), sort_keys=True, allow_nan=False))
