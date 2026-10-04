"""New affine-box proof only. Frozen parent producers are never executed."""
from pathlib import Path
from fractions import Fraction as F
import ast, base64, hashlib, importlib.util, json, struct, zlib

ROOT = Path(__file__).resolve().parents[2]
PARENT = "coordinacion/respuestas/PRECISION-NEXT-LEDGER-CPU-001-CODEX.json"
PSHA = "5319af7a02502d5d4d3816ad897963919b0b5bb58bcf66393dfada1b61cba211"
TRI = "coordinacion/respuestas/PRECISION-NEXT-TRIANGLE-INTERVAL-CPU-001-CODEX.json"
GI = "coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"
CORE = "Blender/benchmarks/capacity_audit/oblique_origin_box_zero_CPU_v1.py"
PREVIOUS = "Blender/benchmarks/capacity_audit/oblique_next_triangle_interval_CPU_v1.py"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def capture(c):
    assert c["rc"] == 0 and c["timed_out"] is False
    d = zlib.decompressobj()
    b = d.decompress(base64.b64decode(c["stdout_zlib_base64"], validate=True), 1048577)
    assert len(b) <= 1048576 and d.eof and not d.unused_data and not d.unconsumed_tail
    assert len(b) == c["stdout_bytes"] and sha(b) == c["stdout_sha256"]
    return json.loads(b)


def boxes(value):
    out = []
    for p in value:
        assert type(p) is list and len(p) == 2
        vals = []
        for x in p:
            assert type(x) is list and len(x) == 2 and all(type(v) is int for v in x)
            assert x[1] > 0 and max(abs(v).bit_length() for v in x) <= 4096
            v = F(*x)
            assert x == [v.numerator, v.denominator]
            vals.append(v)
        out.append(tuple(vals))
    return tuple(out)


def json_box(box):
    return [[[x.numerator,x.denominator] for x in pair] for pair in box]


def run():
    raw = (ROOT/PARENT).read_bytes()
    assert sha(raw) == PSHA and len(raw) == 224367
    parent = json.loads(raw)
    pins = dict(parent["code_doc_sha256"])
    assert len(pins) == 421
    pins[PARENT] = PSHA
    for p, h in pins.items():
        assert sha((ROOT/p).read_bytes()) == h, p
    ledger = capture(parent["test_run"])
    tri_receipt = json.loads((ROOT/TRI).read_bytes())
    tri = capture(tri_receipt["test_run"])
    assert ledger["zero_error_gate"] == tri_receipt["zero_error_gate"] == parent["zero_error_gate"]
    assert ledger["new_nonzero_errors_preserved"] == tri["new_nonzero_errors_preserved"]
    assert ledger["prior_nonzero_error_rows_preserved"] == tri["prior_nonzero_error_rows_preserved"]
    inputs = {x["id"]:x["result"]["packet"] for x in
              capture(json.loads((ROOT/GI).read_bytes())["test_run"])["evidence"]["positive"]}
    names = {"require","power2","MAX64","round_out","sub","cross","dot"}
    def trees(path):
        out = {}
        for n in ast.parse((ROOT/path).read_text(encoding="utf-8")).body:
            name = getattr(n,"name",None)
            if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name):
                name = n.targets[0].id
            if name in names:
                out[name] = ast.dump(n,include_attributes=False)
        return out
    assert trees(CORE) == trees(PREVIOUS) and len(trees(CORE)) == 7
    spec = importlib.util.spec_from_file_location("own_origin_box_zero",ROOT/CORE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    evidence = []
    for case,lc in zip(tri["cases"],ledger["cases"]):
        assert case["case"] == lc["case"]
        packet = inputs[case["case"]]
        b = bytes.fromhex(packet["buffer_hex"])
        w = struct.unpack("<%dI"%(len(b)//4),b)
        base = 10+w[4]
        assert sha(b) == case["input_sha256"] == lc["input_sha256"] == packet["manifest"]["buffer_sha256"]
        assert case["scene_sha256"] == packet["manifest"]["scene_sha256"]
        assert case["query_sha256"] == packet["manifest"]["query_sha256"]
        assert case["primitive_ids"] == list(w[10:base]) == lc["primitive_ids"]
        assert [s["source_id"]for s in case["sources"]] == ["S0","S1"]
        for s,ls in zip(case["sources"],lc["sources"]):
            assert s["source_id"] == ls["source_id"]
            assert ls["result"]["status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES"
            assert ls["result"]["unresolved_ids"] == [s["previous_primitive_id"]]
            assert ls["result"]["conditional_first_id"] is None
            index = case["primitive_ids"].index(s["previous_primitive_id"])
            row = s["rows"][index]
            words = tuple(tuple(w[base+12+9*index+j:base+15+9*index+j]) for j in (0,3,6))
            assert row["triangle_words"] == [list(v)for v in words]
            assert row["result"]["status"] == "STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED"
            assert row["result"]["parameter_interval"] == [[0,1],[0,1]]
            point,direction = boxes(s["point_interval"]),boxes(s["reflected_direction_interval"])
            result = m.prove_previous_zero(point,direction,words)
            assert result["status"] == "CPU_DECLARED_ALL_BOX_ZERO_CONTACT_PROPERTY_ONLY"
            assert result["CPU_box_zero_contact_proved"] is True
            assert result["parameter_zero_range"] == [[0,1],[0,1]]
            for flag in ("launch_exclusion_allowed","native_precision_certified","GPU_launch_allowed",
                         "phase_certified","upstream_binding_authenticated","SOURCE_shared_token"):
                assert result[flag] is False
            assert result["phase_error_bound"] is None and result["ignored_primitive_ids"] == []
            evidence.append(dict(case=case["case"],source_id=s["source_id"],previous_primitive_id=s["previous_primitive_id"],
                                 input_sha256=case["input_sha256"],scene_sha256=case["scene_sha256"],query_sha256=case["query_sha256"],
                                 triangle_words=words,point_bounds=s["point_interval"],direction_bounds=s["reflected_direction_interval"],
                                 result=result,old_triangle_contact_row_retained=row["result"],
                                 old_ledger_SOURCE_decision_retained=ls["result"]))
    word = lambda x: struct.unpack("<I",struct.pack("<f",x))[0]
    words = lambda tri: tuple(tuple(word(x)for x in v)for v in tri)
    pt = lambda v: tuple((F(x),F(x))for x in v)
    triangle = words(((0,0,0),(4,0,0),(0,4,0)))
    point = ((F(1),F(9,8)),(F(1),F(9,8)),(F(0),F(0)))
    direction = ((F(0),F(0)),(F(0),F(0)),(F(1),F(2)))
    proved = "CPU_DECLARED_ALL_BOX_ZERO_CONTACT_PROPERTY_ONLY"
    plane = "STOP_ORIGIN_BOX_NOT_IDENTICALLY_ON_PLANE"
    parallel = "STOP_DIRECTION_POSSIBLE_PARALLEL_OR_COPLANAR"
    interior = "STOP_ORIGIN_BOX_NOT_STRICT_TRIANGLE_INTERIOR"
    controls = []
    def control(label,p,d,t,expected):
        result = m.prove_previous_zero(p,d,t)
        assert result["status"] == expected
        assert result["launch_exclusion_allowed"] is False
        controls.append(dict(label=label,point_bounds=json_box(p),direction_bounds=json_box(d),triangle_words=t,result=result))
    control("tangential_box_nonzero_width",point,direction,triangle,proved)
    control("reverse_normal",point,direction,(triangle[0],triangle[2],triangle[1]),proved)
    control("opposite_departure",point,pt((0,0,-1)),triangle,proved)
    control("uncertain_normal_coordinate",(*point[:2],(F(-1,2**59),F(1,2**59))),direction,triangle,plane)
    control("positive_contact_parameter_2^-60",pt((1,1,F(-1,2**60))),pt((0,0,1)),triangle,plane)
    control("negative_contact_parameter_2^-60",pt((1,1,F(1,2**60))),pt((0,0,1)),triangle,plane)
    control("possible_parallel_direction",point,((F(1),F(1)),(F(0),F(0)),(F(-1),F(1))),triangle,parallel)
    control("parallel_direction",point,pt((1,0,0)),triangle,parallel)
    control("vertex",pt((0,0,0)),direction,triangle,interior)
    control("edge",pt((0,1,0)),direction,triangle,interior)
    control("outside",pt((4,4,0)),direction,triangle,interior)
    control("degenerate",point,direction,words(((0,0,0),(1,0,0),(2,0,0))),"STOP_DEGENERATE_TRIANGLE")
    oblique = words(((0,0,0),(2,0,2),(0,2,2)))
    control("oblique_exact_point",pt((F(1,2),F(1,2),1)),pt((0,0,1)),oblique,proved)
    control("claimed_correlated_oblique_box_without_joint_proof",
            ((F(1,2),F(3,4)),(F(1,2),F(3,4)),(F(1),F(3,2))),pt((0,0,1)),oblique,plane)
    negatives = [
        ("list_point",lambda:m.prove_previous_zero(list(point),direction,triangle)),
        ("reversed_bounds",lambda:m.prove_previous_zero(((F(2),F(1)),*point[1:]),direction,triangle)),
        ("bool_endpoint",lambda:m.prove_previous_zero(((True,F(1)),*point[1:]),direction,triangle)),
        ("nonbinary_endpoint",lambda:m.prove_previous_zero(((F(1,3),F(1,3)),*point[1:]),direction,triangle)),
        ("capacity",lambda:m.prove_previous_zero(((F(1,2**5000),F(1,2**5000)),*point[1:]),direction,triangle)),
        ("overflow",lambda:m.prove_previous_zero(((F(2**1024),F(2**1024)),*point[1:]),direction,triangle)),
        ("zero_possible_direction",lambda:m.prove_previous_zero(point,((F(-1),F(1)),)*3,triangle)),
        ("triangle_shape",lambda:m.prove_previous_zero(point,direction,triangle[:2])),
        ("vertex_shape",lambda:m.prove_previous_zero(point,direction,(triangle[0][:2],*triangle[1:]))),
        ("bool_word",lambda:m.prove_previous_zero(point,direction,((True,0,0),*triangle[1:]))),
        ("NaN_word",lambda:m.prove_previous_zero(point,direction,((0x7fc00000,0,0),*triangle[1:]))),
        ("subnormal_word",lambda:m.prove_previous_zero(point,direction,((1,0,0),*triangle[1:]))),
        ("negative_zero_word",lambda:m.prove_previous_zero(point,direction,((0x80000000,0,0),*triangle[1:]))),
        ("uint32_overflow",lambda:m.prove_previous_zero(point,direction,((2**32,0,0),*triangle[1:]))),
        ("raw_domain",lambda:m.prove_previous_zero(point,direction,((word(2**21),0,0),*triangle[1:]))),
        ("epsilon_override",lambda:m.prove_previous_zero(point,direction,triangle,epsilon=F(1,1000))),
        ("previous_ID_skip",lambda:m.prove_previous_zero(point,direction,triangle,previous_primitive_id=1)),
    ]
    rejected = []
    for label,call in negatives:
        try:call()
        except (ValueError,TypeError)as ex:rejected.append(dict(label=label,error=str(ex)))
        else:raise AssertionError("negative accepted:"+label)
    assert len(evidence)==12 and len(controls)==14 and len(rejected)==17
    return dict(status="PASS_IDEAL_CPU_ALL_BOX_ZERO_PROPERTY_ONLY_NOT_LAUNCH_OR_NATIVE",
                context_pins=pins,original_evidence=evidence,fabricated_controls=controls,negatives=rejected,
                new_nonzero_errors_preserved=tri["new_nonzero_errors_preserved"],
                prior_nonzero_error_rows_preserved=tri["prior_nonzero_error_rows_preserved"],
                zero_error_gate=tri_receipt["zero_error_gate"],old_contact_STOP_count_retained=12,
                old_producer_replays=0,new_affine_property_evaluations=26,GPU_used=False,
                launch_exclusion_allowed=False,phase_certified=False,JEV="LOCAL_BLOCKED_NO_RETRY_NO_REMOTE_ENDORSEMENT")


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,ensure_ascii=True))
