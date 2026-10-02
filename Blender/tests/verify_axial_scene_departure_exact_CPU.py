"""Independent scalar x-plane verifier of retained exact CPU departure evidence; no producer imports/spawn."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
receipt=json.loads((ROOT/"coordinacion/respuestas/PRECISION-AXIAL-SCENE-DEPARTURE-CPU-001-CODEX.json").read_bytes())
for p,h in receipt["code_doc_sha256"].items(): assert sha((ROOT/p).read_bytes())==h,p
def unpack(run):
    assert run["threads"]==run["affinity_mask"]==1 and run["hard_child_timeout_seconds"]==60
    assert not run["timed_out"] and run["elapsed_seconds"]<60
    raw=zlib.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True))
    assert sha(raw)==run["stdout_sha256"] and len(raw)==run["stdout_bytes"]
    return json.loads(raw)
old=unpack(receipt["retained_initial_failure"]); assert old["status"]=="FAIL"
new=unpack(receipt["test_run"]); assert new["status"]=="PASS" and new["tests"]==6
assert receipt["retained_initial_failure"]["rc"]==1 and receipt["test_run"]["rc"]==0
initial=receipt["retained_initial_sources"]
core="Blender/benchmarks/capacity_audit/axial_scene_departure_exact_CPU_v1.py"
test="Blender/tests/test_axial_scene_departure_exact_CPU.py"
for p,row in initial.items():
    raw=base64.b64decode(row["base64"],validate=True); assert sha(raw)==row["sha256"]
    if p==core: assert (ROOT/p).read_bytes()==raw
    else:
        original=raw.decode().replace("\r\n","\n")
        expected=original.replace(
          'r=run("departure_band",scene([0,F(a.root.tie.TIE_BU),1],[(F(1,2),1)]))',
          'r=run("departure_band",scene([0,F(a.root.tie.TIE_BU),2],[(1,1)]))')
        assert original!=expected and (ROOT/p).read_text()==expected
assert set(initial)=={core,test}
assert old["data"]["results"]["departure_band"]["reason"] is None
scenes,reqs,rows=(new["data"][k] for k in ("scenes","requests","results"))
assert len(rows)==17 and set(scenes)==set(rows)==set(reqs)
flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated",
       "native_hit_coverage_certified","length_reference_phase_bound_certified",
       "full_field_certified","mirror_material_certified")
accepted=0; stopped=0; sources_checked=0; complete_queries=0
for name,out in rows.items():
    assert all(out[k] is False for k in flags)
    assert out["origin_bias_BU"]==[0,1] and out["branch_queries"]==0
    assert out["origin"]=="EXACT_RATIONAL_AXIAL_ONE_MIRROR_CPU_KINEMATICS"
    assert out["full_costs"]=="UNMEASURED_NOT_ZERO"
    scene=scenes[name]
    canonical=json.dumps(scene,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    binding=sha(canonical)
    if out["scene_sha256"] is not None: assert out["scene_sha256"]==binding
    xs=[]
    for i,tri in enumerate(scene["triangles"]):
        assert tri["primitive_id"]==i
        x=F(*tri["vertices_BU"][0][0]);xs.append(x)
        assert all(F(*v[0])==x for v in tri["vertices_BU"])
        assert [v[1:] for v in tri["vertices_BU"]]==[[[0,1],[0,1]],[[1,1],[0,1]],[[0,1],[1,1]]]
    sources={s["id"]:s for s in scene["sources"]}
    for d in out["departures"]:
        source=sources[d["source_id"]]; sign=F(*source["direction"][0])
        assert sign in (-1,1) and source["direction"][1:]==[[0,1],[0,1]]
        root_origin=F(*source["position_BU"][0])
        root_positive={i:(x-root_origin)/sign for i,x in enumerate(xs) if (x-root_origin)/sign>0}
        root_record=next(r for r in out["root_evidence"]["sources"] if r["source_id"]==d["source_id"])
        assert {r["primitive_id"]:F(*r["distance_rational_BU"]) for r in root_record["hits"]}==root_positive
        root_lo=min(root_positive.values())
        root_min=sorted(i for i,t in root_positive.items() if t==root_lo)
        assert root_record["exact_minimum_ids"]==root_min==root_record["float64_minimum_ids"]
        prior=d["previous_primitive_id"]; point=F(*d["origin_rational_BU"][0])
        assert prior==min(root_min)
        assert point==xs[prior] and d["origin_rational_BU"][1:]==source["position_BU"][1:]==[[1,4],[1,4]]
        assert d["direction_rational"]==[[-int(sign),1],[0,1],[0,1]]
        assert F(*d["root_distance_rational_BU"])==(point-F(*source["position_BU"][0]))/sign>0
        distances={i:(x-point)/(-sign) for i,x in enumerate(xs)}
        assert distances[prior]==0 and d["excluded_zero_ids"]==[prior]
        visited=[r["primitive_id"] for r in d["visited"]]
        assert visited==list(range(len(visited)))
        for hit in d["hits"]:
            assert F(*hit["distance_rational_BU"])==distances[hit["primitive_id"]]>0
            assert hit["distance_float64_BU"]==float(distances[hit["primitive_id"]])
            assert hit["normal_canonical"]==[1.,0.,0.]
        sources_checked+=1
        if name=="other_zero":
            assert any(t==0 and i!=prior for i,t in distances.items())
            assert out["reason"]=="different_primitive_zero_contact";continue
        assert len(visited)==len(xs);complete_queries+=1
        positive={i:t for i,t in distances.items() if t>0}
        assert {r["primitive_id"]:F(*r["distance_rational_BU"]) for r in d["hits"]}==positive
        if positive:
            lo=min(positive.values());flo=min(float(t) for t in positive.values())
            ex_min=sorted(i for i,t in positive.items() if t==lo)
            fp_min=sorted(i for i,t in positive.items() if float(t)==flo)
            ex_band=sorted(i for i,t in positive.items() if t-lo<=F(1e-9))
            fp_band=sorted(i for i,t in positive.items() if abs(float(t)-flo)<=1e-9)
            assert d["exact_minimum_ids"]==ex_min and d["float64_minimum_ids"]==fp_min
            assert d["exact_band_ids"]==ex_band and d["float64_band_ids"]==fp_band
    if out["status"]=="STOP":
        stopped+=1;assert out["emitted_paths"]==[] and out["reason"]
    else:
        accepted+=1
        assert out["status"]=="CPU_AXIAL_ONE_MIRROR_GEOMETRY_ONLY"
        assert len(out["emitted_paths"])==len(scene["sources"])==len(out["departures"])
        for path,d in zip(out["emitted_paths"],out["departures"]):
            assert path["scene_sha256"]==binding and path["source_id"]==d["source_id"]
            assert path["branch_id"]==path["source_id"]+"/mirror"
            prior,winner=path["primitive_ids"]
            assert prior==d["previous_primitive_id"] and winner==min(d["exact_minimum_ids"])
            a=F(*d["root_distance_rational_BU"]); b=abs(xs[winner]-xs[prior])
            assert path["segments_rational_BU"]==[[a.numerator,a.denominator],[b.numerator,b.denominator]]
            assert F(*path["length_rational_BU"])==a+b
            assert path["endpoint_rational_BU"]==[[xs[winner].numerator,xs[winner].denominator],[1,4],[1,4]]
assert (accepted,stopped)==(4,13)
for name in ("tiny_plus","tiny_minus"):
    assert rows[name]["emitted_paths"][0]["segments_rational_BU"]==[[1,2**57],[1,2**56]]
    assert rows[name]["departures"][0]["origin_rational_BU"][0]==[1,1]
assert rows["departure_collision"]["reason"]=="departure_float64_minimum_set_changed"
assert rows["departure_band"]["reason"]=="departure_float64_tie_band_changed"
assert rows["departure_ambiguous"]["reason"]=="departure_tie_policy:ambiguous_object_or_normal"
assert rows["second_SOURCE_miss"]["departure_queries"]==2
assert rows["root_zero"]["departure_queries"]==0
for name in ("bad_sha","bad_SOURCE","bad_event","extra_key","missing_SOURCE","wrong_model"):
    assert rows[name]["departure_queries"]==0 and rows[name]["root_evidence"] is None
print(json.dumps({"status":"PASS","pins":len(receipt["code_doc_sha256"]),"fresh_scenes":17,
 "accepted_reduced_CPU":accepted,"expected_STOP":stopped,"scalar_SOURCE_checks":sources_checked,
 "complete_departure_queries":complete_queries,"initial_failure_preserved_core_unchanged":True,
 "GPU_executed":False,"phase_native_certified":False},sort_keys=True))
