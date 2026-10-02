"""Scene-bound scalar hi-lo CPU transport audit; exact-point opt-in, NEVER native admission."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib,importlib.util,json,struct
from pathlib import Path
import axial_scene_departure_exact_CPU_v1 as departure
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-axial-scene-transport-CPU-v1"
ENCODER="Blender/tests/exp005_blender_gpu.py"
ENCODER_SHA="851f29f9b1fb9b22948f59597d40fa8a55828040673fe0050d24e077b57cf497"
def sha(v):return hashlib.sha256(v).hexdigest()
def word(x,width):return int.from_bytes(struct.pack("<f" if width==32 else "<d",x),"little")
def pair(x):return [x.numerator,x.denominator]
class TransportStop(ValueError):pass

def audit(scene, requests, *, model):
    out={"model":MODEL,"status":"STOP","reason":None,"original_scene_sha256":None,
         "decoded_scene_sha256":None,"decoded_scene":None,"scalars":[],"original_geometry":None,
         "decoded_geometry":None,"emitted_paths":[],"new_RN32_casts":0,"new_RN64_subtractions":0,
         "new_CPU_RN64_decode_additions":0,"GPU_executed":False,"native_promotion_allowed":False,
         "physical_scene_authenticated":False,"native_hit_coverage_certified":False,
         "length_reference_phase_bound_certified":False,"full_field_certified":False,
         "mirror_material_certified":False,"full_costs":"UNMEASURED_NOT_ZERO",
         "origin":"RATIONAL_SCENE_REAL_HOST_SPLIT_CPU_DECODE_NOT_GPU_ABI",
         "exact_point_profile":True}
    try:
        if type(model) is not str or model!=MODEL:raise TransportStop("explicit_model_required")
        scene,requests=deepcopy(scene),deepcopy(requests)
        original=departure.prepare_departures(scene,requests,model=departure.MODEL)
        out["original_geometry"]=original
        out["original_scene_sha256"]=original["scene_sha256"]
        if original["status"]=="STOP":raise TransportStop("original_geometry_STOP:"+original["reason"])
        raw=(ROOT/ENCODER).read_bytes()
        if sha(raw)!=ENCODER_SHA:raise TransportStop("frozen_encoder_identity_changed")
        # Only inspected pure split_double(). No main(), dispatch(), texture_data(), Bpy or GPU.
        spec=importlib.util.spec_from_file_location("frozen_cpu_split_for_new_scene",ROOT/ENCODER)
        encoder=importlib.util.module_from_spec(spec)
        exec(compile(raw,str(ROOT/ENCODER),"exec"),encoder.__dict__) # Execute the SAME verified bytes; no reread race.
        decoded=deepcopy(scene)
        def scalar(row,key,component,path):
            q=F(*row[key][component]);first=float(q);qfirst=F(first)
            high,low=encoder.split_double(first);h,l=F(high),F(low)
            decoded_float=float(high)+float(low);value=F(decoded_float)
            efirst=abs(qfirst-q);ehilo=abs(h+l-qfirst);edecode=abs(value-h-l)
            bound=efirst+ehilo+edecode
            if abs(value-q)>bound:raise TransportStop("scalar_error_enclosure_failed")
            out["scalars"].append({"path":path,"original_rational":pair(q),
                "first_float64_uint64":word(first,64),"first_rational":pair(qfirst),
                "high_uint32":word(high,32),"low_uint32":word(low,32),
                "decoded_uint64":word(decoded_float,64),"decoded_rational":pair(value),
                "first_cast_error_abs":pair(efirst),"hilo_encoding_error_abs":pair(ehilo),
                "CPU_decode_add_error_abs":pair(edecode),"total_point_bound_abs":pair(bound),
                "observed_point_error_abs":pair(abs(value-q)),
                "hilo_le_hex":struct.pack("<ff",high,low).hex()})
            out["new_RN32_casts"]+=2;out["new_RN64_subtractions"]+=1
            out["new_CPU_RN64_decode_additions"]+=1
            row[key][component]=pair(value)
        for i,tri in enumerate(decoded["triangles"]):
            # scalar helper takes vector container; original still comes from deepcopied unmodified component.
            for j,vertex in enumerate(tri["vertices_BU"]):
                holder={"vector":vertex}
                for k in range(3):scalar(holder,"vector",k,["triangles",i,"vertices_BU",j,k])
        for i,source in enumerate(decoded["sources"]):
            for key in ("position_BU","direction"):
                for k in range(3):scalar(source,key,k,["sources",i,key,k])
        decoded_sha=departure.root.bound_scene(decoded)[0]
        out["decoded_scene"],out["decoded_scene_sha256"]=decoded,decoded_sha
        # Rebind reconstructed scene explicitly; never label decoded as ORIGINAL.
        decoded_requests=[{"scene_sha256":decoded_sha,"source_id":s["id"],"departure_event":"mirror"}
                          for s in decoded["sources"]]
        decoded_geometry=departure.prepare_departures(decoded,decoded_requests,model=departure.MODEL)
        out["decoded_geometry"]=decoded_geometry
        # Audit keeps transformed geometry evidence even when exact-point prerequisite failed.
        if any(F(*s["first_cast_error_abs"])!=0 for s in out["scalars"]):
            raise TransportStop("ORIGINAL_rational_to_float64_loss")
        if any(F(*s["observed_point_error_abs"])!=0 for s in out["scalars"]):
            raise TransportStop("HOST_hilo_CPU_decode_point_loss")
        if decoded_geometry["status"]=="STOP":
            raise TransportStop("decoded_geometry_STOP:"+decoded_geometry["reason"])
        def paths(g):
            return [(p["source_id"],p["primitive_ids"],p["segments_rational_BU"],
                     p["endpoint_rational_BU"],p["length_rational_BU"]) for p in g["emitted_paths"]]
        if paths(original)!=paths(decoded_geometry):raise TransportStop("exact_point_path_identity_changed")
        # All scalars, SOURCE and paths passed; conditional CPU point equivalence only.
        out["emitted_paths"]=[{"original_scene_sha256":out["original_scene_sha256"],
              "decoded_scene_sha256":decoded_sha,"path":deepcopy(p)} for p in decoded_geometry["emitted_paths"]]
        out["status"]="CPU_EXACT_POINT_TRANSPORT_ONLY"
    except (ValueError,TypeError,KeyError,OverflowError,struct.error) as exc:
        out["reason"]=str(exc) if isinstance(exc,TransportStop) else "transport_INPUT:"+type(exc).__name__
    return out
