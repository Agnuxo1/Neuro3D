"""Independent retained IEEE/rational scalar + x-plane geometry verifier; no producer imports/spawn."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((ROOT/"coordinacion/respuestas/PRECISION-AXIAL-SCENE-TRANSPORT-CPU-001-CODEX.json").read_bytes())
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
t=r["test_run"];assert t["rc"]==0 and not t["timed_out"] and t["threads"]==t["affinity_mask"]==1
assert t["hard_child_timeout_seconds"]==60 and t["elapsed_seconds"]<60
raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
data=json.loads(raw);assert data["status"]=="PASS" and data["tests"]==6
def ieee(word,width):
    assert type(word) is int and 0<=word<2**width
    mb,eb,bias=(23,8,127) if width==32 else (52,11,1023)
    exp=(word>>mb)&(2**eb-1);mant=word%(2**mb)
    assert exp<2**eb-1
    return (-1 if word>>(width-1) else 1)*F(mant if exp==0 else mant+2**mb)*F(2)**((1 if exp==0 else exp)-bias-mb)
def rn(q,word,width):
    value=ieee(word,width);mag=word%(2**(width-1))
    if q==0:assert value==0;return value
    assert word>>(width-1)==int(q<0)
    a=abs(q);v=abs(value);mb,eb=(23,8) if width==32 else (52,11)
    if mag==0:
        assert a<=F(2)**(-150 if width==32 else -1075);return value
    lower=abs(ieee(mag-1,width));upper=abs(ieee(mag+1,width))
    left,right=(lower+v)/2,(v+upper)/2;even=mag%2==0
    assert (a>left or a==left and even) and (a<right or a==right and even)
    return value
def at(scene,path):
    node=scene
    for key in path:node=node[key]
    return F(*node)
def binding(scene):
    return sha(json.dumps(scene,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def verify_geometry(scene,g):
    assert g["scene_sha256"]==binding(scene)
    if g["status"]=="STOP":assert g["emitted_paths"]==[];return
    xs=[F(*tri["vertices_BU"][0][0]) for tri in scene["triangles"]]
    assert len(g["emitted_paths"])==len(scene["sources"])
    for source,path in zip(scene["sources"],g["emitted_paths"]):
        origin=F(*source["position_BU"][0]);direction=F(*source["direction"][0])
        assert direction in (-1,1) and source["direction"][1:]==[[0,1],[0,1]]
        assert source["position_BU"][1:]==[[1,4],[1,4]]
        positive={i:(x-origin)/direction for i,x in enumerate(xs) if (x-origin)/direction>0}
        root_min=min(positive.values());prior=min(i for i,t in positive.items() if t==root_min)
        reflected={i:(x-xs[prior])/(-direction) for i,x in enumerate(xs) if (x-xs[prior])/(-direction)>0}
        gap=min(reflected.values());winner=min(i for i,t in reflected.items() if t==gap)
        assert path["source_id"]==source["id"] and path["primitive_ids"]==[prior,winner]
        assert F(*path["segments_rational_BU"][0])==root_min and F(*path["segments_rational_BU"][1])==gap
        assert F(*path["length_rational_BU"])==root_min+gap
        assert F(*path["endpoint_rational_BU"][0])==xs[winner]
scenes,rows,requests=(data["data"][k] for k in ("scenes","results","requests"))
assert set(scenes)==set(rows)==set(requests) and len(rows)==13
flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated",
 "native_hit_coverage_certified","length_reference_phase_bound_certified","full_field_certified","mirror_material_certified")
accepted=stopped=scalars=0
for name,out in rows.items():
    assert all(out[f] is False for f in flags)
    assert out["full_costs"]=="UNMEASURED_NOT_ZERO" and out["exact_point_profile"] is True
    assert out["origin"]=="RATIONAL_SCENE_REAL_HOST_SPLIT_CPU_DECODE_NOT_GPU_ABI"
    scene=scenes[name];encoded=out["decoded_scene"]
    n=len(out["scalars"]);scalars+=n
    assert out["new_RN32_casts"]==2*n and out["new_RN64_subtractions"]==out["new_CPU_RN64_decode_additions"]==n
    if encoded is not None:
        assert out["original_scene_sha256"]==binding(scene) and out["decoded_scene_sha256"]==binding(encoded)
        expected=[["triangles",i,"vertices_BU",j,k] for i in range(len(scene["triangles"])) for j in range(3) for k in range(3)]
        expected += [["sources",i,key,k] for i in range(len(scene["sources"])) for key in ("position_BU","direction") for k in range(3)]
        assert [s["path"] for s in out["scalars"]]==expected
        # No IDs, units, order, object labels or SOURCE labels transformed.
        assert encoded["schema"]==scene["schema"] and encoded["units"]==scene["units"]
        assert [(x["primitive_id"],x["object_id"]) for x in encoded["triangles"]]==[(x["primitive_id"],x["object_id"]) for x in scene["triangles"]]
        assert [s["id"] for s in encoded["sources"]]==[s["id"] for s in scene["sources"]]
        for s in out["scalars"]:
            q=at(scene,s["path"]);assert F(*s["original_rational"])==q
            first=rn(q,s["first_float64_uint64"],64);h=rn(first,s["high_uint32"],32)
            # Difference between finite FP64 x and nearest FP32 h is exact FP64 (Sterbenz or h=0).
            residual=first-h
            l=rn(residual,s["low_uint32"],32);decoded=rn(h+l,s["decoded_uint64"],64)
            assert F(*s["first_rational"])==first and F(*s["decoded_rational"])==decoded==at(encoded,s["path"])
            a,b,c=abs(first-q),abs(h+l-first),abs(decoded-h-l)
            assert F(*s["first_cast_error_abs"])==a and F(*s["hilo_encoding_error_abs"])==b
            assert F(*s["CPU_decode_add_error_abs"])==c and F(*s["total_point_bound_abs"])==a+b+c
            assert F(*s["observed_point_error_abs"])==abs(decoded-q)<=a+b+c
            assert s["hilo_le_hex"]==(s["high_uint32"].to_bytes(4,"little")+s["low_uint32"].to_bytes(4,"little")).hex()
        verify_geometry(scene,out["original_geometry"]);verify_geometry(encoded,out["decoded_geometry"])
    if out["status"]=="STOP":
        stopped+=1;assert out["emitted_paths"]==[] and out["reason"]
    else:
        accepted+=1;assert out["status"]=="CPU_EXACT_POINT_TRANSPORT_ONLY"
        assert all(s["first_cast_error_abs"]==s["observed_point_error_abs"]==[0,1] for s in out["scalars"])
        assert len(out["emitted_paths"])==len(scene["sources"])
        for p in out["emitted_paths"]:
            assert p["original_scene_sha256"]==binding(scene) and p["decoded_scene_sha256"]==binding(encoded)
            assert p["path"] in out["decoded_geometry"]["emitted_paths"]
assert (accepted,stopped,scalars)==(4,9,228)
for name in ("world_thin","rational_tenth"):assert rows[name]["reason"]=="ORIGINAL_rational_to_float64_loss"
for name in ("FP64_input_hilo_loss","tiny_underflow_hilo","second_SOURCE_hilo_loss"):
    assert rows[name]["reason"]=="HOST_hilo_CPU_decode_point_loss"
for name in ("world_thin","tiny_underflow_hilo"):
    assert rows[name]["decoded_geometry"]["reason"]=="root_STOP:source_zero_contact_no_departure"
assert rows["noncanonical_literal"]["original_scene_sha256"]!=rows["noncanonical_literal"]["decoded_scene_sha256"]
for name in ("bad_SHA","wrong_model","original_zero","encoder_identity_STOP"):
    assert rows[name]["scalars"]==[] and rows[name]["decoded_geometry"] is None
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"fresh_scenes":13,"scalar_RN_error_checks":scalars,
 "accepted_exact_point_CPU":4,"expected_STOP":9,"new_RN32_casts":456,"GPU_executed":False,"native_phase_certified":False},sort_keys=True))
