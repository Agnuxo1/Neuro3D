"""Read exact saved CPU results; no triangle/helper/producer replay."""
from pathlib import Path
from fractions import Fraction as F
import base64, copy, hashlib, importlib.util, json, struct, zlib

ROOT = Path(__file__).resolve().parents[2]
PARENT = "coordinacion/respuestas/PRECISION-EXACT-PARAMETER-ORDER-CPU-001-CODEX.json"
PSHA = "a6d647eb6d803274e534def7780a81d9673db2b8561138215609e350e94a6a69"
CORE = "Blender/benchmarks/capacity_audit/oblique_exact_scalar_hilo32_CPU_v1.py"


def run():
    raw = (ROOT/PARENT).read_bytes()
    assert len(raw)==108943 and hashlib.sha256(raw).hexdigest()==PSHA
    parent = json.loads(raw);pins=dict(parent["code_doc_sha256"]);pins[PARENT]=PSHA
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    cap=parent["test_run"];d=zlib.decompressobj()
    b=d.decompress(base64.b64decode(cap["stdout_zlib_base64"],validate=True),1048577)
    assert len(b)<=1048576 and d.eof and not d.unused_data and not d.unconsumed_tail
    assert cap["rc"]==0 and not cap["timed_out"] and len(b)==cap["stdout_bytes"] and hashlib.sha256(b).hexdigest()==cap["stdout_sha256"]
    saved=json.loads(b)
    spec=importlib.util.spec_from_file_location("own_hilo32_cpu",ROOT/CORE)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    packets=[];collapse=0
    for entry in saved["evidence"]:
        result=entry["result"];i=result["candidate_index"]
        if i is None:continue
        fields=[("t",result["triangles"][i]["t"])] + [("p"+str(j),v)for j,v in enumerate(result["exact_candidate_point"])]
        for name,v in fields:
            packet=m.encode_scalar(v)
            assert packet["status"]=="EXACT_PAIR_CPU_ONLY" and packet["residual_exact"]==[0,1]
            assert F(*v)==m.decode32(packet["hi_word"])+m.decode32(packet["lo_word"])
            assert m.audit_packet(packet)==packet
            float_collapse=(F.from_float(float(F(*v)))!=F(*v))
            if name=="t" and entry["case"]in ("thin_gap_2^-60","half_ULP_2^-54_ties_even"):
                assert float_collapse
            else:assert not float_collapse
            collapse+=int(float_collapse)
            packets.append({"case":entry["case"],"rotation":entry["rotation"],"swap":entry["swap"],
                            "winding":entry["winding"],"field":name,
                            "source_raw_stage_sha256":result["raw_stage_sha256"],
                            "packet":packet,"diagnostic_binary64_collapse":float_collapse})
    controls=[]
    values=[F(0),F(1,3),F(-1,3),F(1,10),F(1,1<<140),F(1,1<<150),
            F(1,1<<126),F((1<<24)-1,1<<150),F(1)+F(1,1<<24),
            F(1)+F(1,1<<24)+F(1,1<<80),F(1)+F(1,1<<140)]
    for x in values:
        packet=m.encode_scalar(m.pair(x));assert m.audit_packet(packet)==packet
        assert x==m.decode32(packet["hi_word"])+m.decode32(packet["lo_word"])+F(*packet["residual_exact"])
        if x in (F(1,3),F(-1,3),F(1,10),F(1,1<<150),F((1<<24)-1,1<<150)):
            assert packet["status"]=="STOP_NONZERO_RESIDUAL"
        if x in (F(1,1<<140),F(1)+F(1,1<<140)):
            assert packet["status"]=="STOP_SUBNORMAL_COMPONENT"
        controls.append(packet)
    assert controls[8]["hi_word"]==0x3f800000
    assert controls[9]["hi_word"]==0x3f800001
    assert m.rn32(-F(1,1<<150))==0
    invalid=[None,(1,1),[1],[True,1],[1,True],[1,0],[1,-1],[2,2],[0,2],[1<<4097,1],[1000001,1]]
    for value in invalid:
        try:m.encode_scalar(value)
        except ValueError:pass
        else:raise AssertionError("invalid rational admitted")
    base=packets[0]["packet"];mutations=[]
    changes={"hi_word":True,"lo_word":0x7f800000,"wire_hex":"0000000000000000",
             "residual_exact":[1,1],"pair_sum_exact":[0,1],"status":"PASS",
             "GPU_launch_allowed":True,"launch_exclusion_allowed":True,
             "native_precision_certified":True,"phase_certified":True,
             "native_origin_box_bound":0,"phase_error_bound":0,"full_costs":0,
             "exact_input":[0,1],"schema":"GPU"}
    for key,v in changes.items():
        bad=copy.deepcopy(base);bad[key]=v;mutations.append(bad)
    bad=copy.deepcopy(base);bad.pop("lo_word");mutations.append(bad)
    bad=copy.deepcopy(base);bad["extra"]=0;mutations.append(bad)
    for bad in mutations:
        try:m.audit_packet(bad)
        except ValueError:pass
        else:raise AssertionError("mutated metadata admitted")
    detached=m.audit_packet(base);detached["exact_input"][0]=0
    assert m.audit_packet(base)["exact_input"]==base["exact_input"]
    assert len(packets)==144 and collapse==24
    return {"status":"PASS_CPU_HILO32_COMPONENTS_AND_RESIDUAL_ONLY_NO_NATIVE",
            "context_pins":pins,"packets":packets,"controls":controls,"packets_from_saved_CPU":144,
            "binary64_collapse_controls_retained":collapse,"numeric_boundary_controls":len(controls),
            "invalid_rational_rejections":len(invalid),"metadata_mutation_rejections":len(mutations),
            "prior_zero_error_gate":parent["prior_zero_error_gate"],
            "prior_scalar_errors":72,"prior_error_rows":16,"prior_contact_STOP":12,
            "original_scene_queries_replayed":0,"triangle_evaluations":0,
            "old_producer_executions":0,"GPU_used":False,"Bpy_used":False,"RT_used":False,
            "native_precision_certified":False,"launch_exclusion_allowed":False,
            "phase_error_bound":None,"full_costs":"UNKNOWN_NOT_ZERO"}

if __name__=="__main__":print(json.dumps(run(),sort_keys=True))
