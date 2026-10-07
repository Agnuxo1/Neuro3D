"""Pinned source-text audit; never compile, import a runner, or infer native error."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ID = "PRECISION-FIRST-LEG-FROZEN-SHADER-STATIC-AUDIT-HOST-001"
PINS = {
    "Blender/shaders/exp005_shared_frontier.glsl": "914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1",
    "Blender/benchmarks/capacity_audit/shared_frontier_gpu.py": "f38a93ae116be66284062297a31aa4dac37c40f7d9eefcf77fc4c146aca23c6b",
    "Blender/benchmarks/capacity_audit/original_SOURCE_first_leg_RN64_graph_HOST_v1.py": "d4e1de31d00cc4767725ccad0120ac59875e788c24d6ec0911dc4350857f38d6",
}
SHADER, RUNNER, MODEL = tuple(PINS)
# Exact code lines in these pinned sources, not a generalized GLSL parser.
ANCHORS = {
    SHADER: {
        "origin_shift": "dvec3 biased=origin+d*BIAS;",
        "intersection_parameter": "double t=dot(e2,q)/det;",
        "select_parameter": "if(t<best-1.0e-9lf) { best=t;object=int(a.w);normal=n;ambiguous=false; }",
        "bias_restore": "best+=BIAS;",
        "source_direction": "stack[0]=Ray(a.xyz,normalize(b.xyz),dvec2(a.w,b.w),0.0lf,0);",
        "returned_distance": "nearest(ray.o,ray.d,distance,object,normal,ambiguous);",
        "endpoint": "dvec3 point=ray.o+ray.d*distance;",
        "length_accumulate": "double length=ray.length+distance;",
        "reference_projection": "double effective=length+dot(ray.d,reference-point);",
        "wavelength_decode": "dvec2 field=rotated(ray.a,TAU*effective/(double(wavelength_hi)+double(wavelength_lo)));",
        "phase_float32": "float angle=float(phase-TAU*floor(phase/TAU+0.5));",
    },
    RUNNER: {
        "shader_path": "SHADER=Path(__file__).parents[2]/'shaders'/'exp005_shared_frontier.glsl'",
        "shader_source_binding": "info.local_group_size(1,1,1); info.compute_source(SHADER.read_text(encoding='utf-8'))",
    },
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def audit(blobs):
    need(type(blobs) is dict and set(blobs) == set(PINS), "complete_pinned_source_set")
    evidence = {}
    for path, expected in PINS.items():
        raw = blobs[path]
        need(type(raw) is bytes and len(raw) <= 16384 and hashlib.sha256(raw).hexdigest() == expected,
             "pinned_source:"+path)
        lines = raw.decode("utf-8").splitlines()
        refs = {}
        for role, code in ANCHORS.get(path, {}).items():
            positions = [i for i, line in enumerate(lines, 1) if line.strip() == code]
            need(len(positions) == 1, "unique_exact_code_anchor:"+role)
            refs[role] = dict(line=positions[0], code=code)
        evidence[path] = dict(sha256=expected, bytes=len(raw), anchors=refs)
    # Read a literal graph declaration using AST; no importing the modeled evaluator.
    tree = ast.parse(blobs[MODEL])
    graph = [n.value.value for n in tree.body if isinstance(n, ast.Assign) and
             any(isinstance(t, ast.Name) and t.id == "GRAPH" for t in n.targets) and
             isinstance(n.value, ast.Constant) and type(n.value.value) is str]
    need(graph == ["sub_xyz; square_xyz; add_xy; add_z; correctly_rounded_sqrt"], "hypothetical_graph_literal")
    a = evidence[SHADER]["anchors"]
    need(a["origin_shift"]["line"] < a["intersection_parameter"]["line"] < a["select_parameter"]["line"] <
         a["bias_restore"]["line"] < a["returned_distance"]["line"] < a["endpoint"]["line"] <
         a["length_accumulate"]["line"] < a["reference_projection"]["line"], "source_text_order")
    return dict(id=ID, status="STATIC_SOURCE_PATH_DIFFERS_FROM_HYPOTHETICAL_ENDPOINT_NORM_GRAPH",
                evidence=evidence, hypothetical_length_graph=graph[0],
                frozen_length_source_path="biased_ray_triangle_parameter; selected_t_plus_BIAS; accumulated_distance",
                scope="PINNED_SOURCE_TEXT_ONLY_NOT_COMPILED_NATIVE_GRAPH_OR_NUMERICAL_FAILURE",
                no_endpoint_norm_call_on_selected_length_source_path=True,
                builtin_normalize_rounding_and_compiler_lowering="UNKNOWN_NOT_CORRECT_RN_ASSUMED",
                semantic_equivalence_or_nonequivalence_in_exact_geometry="NOT_PROVED_BY_TEXT_AUDIT",
                native_IEEE_graph_identity_verified=False, native_first_leg_error_bound_BU=None,
                native_SOURCE_ingress_error_bound_BU=None, native_phase_error_bound_rad=None,
                phase_certified=False, promotion="STOP", GPU_used=False, Bpy_used=False, RT_used=False,
                shader_compilations=0, geometry_evaluations=0, old_producer_replays=0,
                full_costs="UNKNOWN_NOT_ZERO", JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")


def run():
    return audit({path: (ROOT/path).read_bytes() for path in PINS})


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, allow_nan=False))
