"""Common EXACT geometric frame on declared rational input; HOST prep + CPU64, not hi-lo."""
from fractions import Fraction as F
import copy
import oblique_finite_interval_HOST_v1 as host
import oblique_finite_interval_CPU64_v1 as cpu

MODEL="oblique-common-exact-frame-CPU64-v1"
POLICY="SAME_DECLARED_SOURCE0_NOMINAL_FOR_ALL5POINTS_NOT_PHASE_REFERENCE"

def pair(x):
    return [x.numerator,x.denominator]

def request(scene,scene_query):
    return dict(backend=MODEL,policy=POLICY,original_snapshot_sha256=host.digest(scene),
                original_scene_query=scene_query)

def classify(scene, q):
    output=dict(backend=MODEL,status="STOP_INPUT",reason=None,frame=None,
                native_result=None,HOST_exact_recenter_operations=0,
                physical_visibility_certified=False,phase_certified=False,
                scene_authenticated=False,GPU_used=False,native_hi_lo_transport=False,
                source_uncertainty_cancelled=False,promotion="STOP_PHYSICAL_GPU",
                full_costs="UNKNOWN_NOT_ZERO")
    try:
        host.keys(q,("backend","policy","original_snapshot_sha256","original_scene_query"))
        if q["backend"]!=MODEL or q["policy"]!=POLICY or q["original_snapshot_sha256"]!=host.digest(scene):
            raise ValueError("closed_common_frame_original_binding")
        host.validate(scene,q["original_scene_query"]) # pure schema/boxes, not HOST producer
        ref=[host.rational(x) for x in scene["points"]["origin"]["nominal"]]
        centered=copy.deepcopy(scene)
        centered["scene_id"]=scene["scene_id"]+"/COMMON-EXACT-FRAME"
        centered["context"]=scene["context"]+"/COMMON-EXACT-FRAME"
        ledger=[]
        for n in host.POINTS:
            for axis,(x,r) in enumerate(zip(scene["points"][n]["nominal"],ref)):
                exact=host.rational(x)-r
                ledger.append(dict(point=n,axis=axis,original=x,reference=pair(r),
                                   centered=pair(exact),radius=scene["points"][n]["radius"][axis]))
                centered["points"][n]["nominal"][axis]=pair(exact)
        output.update(HOST_exact_recenter_operations=15,original_snapshot_sha256=host.digest(scene),
                      request_sha256=host.digest(q))
        # Original coordinate/radius domain remains frozen: no widening of limits.
        cq=dict(q["original_scene_query"],snapshot_sha256=host.digest(centered),context=centered["context"])
        host.validate(centered,cq)
        native_request=dict(backend=cpu.MODEL,scene_query=cq,snapshot_sha256=host.digest(centered))
        result=cpu.classify(centered,native_request)
        output.update(status=result["status"],reason="common_exact_geometric_frame_conditional",
                      frame=dict(policy=POLICY,reference=[pair(x) for x in ref],
                                 reference_uncertainty="EXACT_CHOSEN_CONSTANT_NOT_ACTUAL_SOURCE_ERROR",
                                 geometric_NOT_optical=True,ledger=ledger,
                                 scene=centered,scene_query=cq,snapshot_sha256=host.digest(centered),
                                 native_request=native_request),
                      native_result=result)
    except (ValueError,TypeError,OverflowError) as exc:
        output["reason"]=str(exc)
    return output
