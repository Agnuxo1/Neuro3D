"""Opt-in untrusted-output comparator. No GPU API, compiler, float or phase evaluation."""
import base64, hashlib, json, re, struct, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-axial-common-detector-pair64-output-HOST-v1"
INTENT="COMPARE_UNATTESTED_OUTPUT_ONLY"
ORIGIN="UNATTESTED_BYTES_NOT_GPU_READBACK"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PAIR64-INGRESS-SHADERC-001-CODEX.json"
PARENT_SHA="54321d7fc359b9734274b7c0181a0c0f849b58c634d5c7bfb93e2ec2d8ea48ae"
KEYS={"case","prepare_result_sha256","packet_sha256","intent"}
TAG=0x50363431

def require(ok,why):
    if not ok:raise ValueError(why)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(value):return sha(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode())

def capture(t):
    require(t["rc"]==0 and t["timed_out"]is False,"retained_PASS")
    z=zlib.decompressobj()
    raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1024*1024+1)
    require(len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail,"closed_capture")
    require(len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"],"capture_identity")
    v=json.loads(raw)
    require(v["status"]=="PASS" and v["tests"]==7,"specific_ingress_suite")
    return v["data"]

def retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,"specific_ingress_receipt")
    r=json.loads(raw);pins=r["code_doc_sha256"];require(len(pins)==73,"parent_pin_count")
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"parent_dependency:"+p)
    return capture(r["test_run"])

def selector(case="exact"):
    d=retained();result=d["prepares"][case]
    return {"case":case,"prepare_result_sha256":digest(result),"packet_sha256":digest(result["packet"]),"intent":INTENT}

def compare(q,observation,*,model):
    out={"model":MODEL,"status":"STOP","reason":None,"rows":[],
         "HOST_bitwise_match_certified":False,"GPU_executed":False,"GPU_job_admission":False,
         "actual_GPU_readback_available":False,"GPU_semantics_certified":False,
         "execution_authenticated":False,"freshness_authenticated":False,
         "host_completion_barrier_certified":False,"resource_guard_certified":False,
         "physical_scene_authenticated":False,"native_hit_coverage_certified":False,
         "length_reference_phase_bound_certified":False,"mirror_material_certified":False,
         "full_field_certified":False,"coherent_field_admission_allowed":False,
         "interference_phase_certified":False,"native_promotion_allowed":False,
         "field":None,"power":None,"amplitude":None,"new_phase_RN_operations":0,
         "producer_replays":0,"new_compiler_calls":0,"full_costs":"UNMEASURED_NOT_ZERO",
         "copied_or_stale_CPU_bytes_can_match":True,"same_value_slot_permutation_detectable":False}
    try:
        require(type(model)is str and model==MODEL,"explicit_comparison_model")
        require(type(q)is dict and set(q)==KEYS and all(type(v)is str for v in q.values()),"closed_typed_selector")
        require(q["intent"]==INTENT,"unattested_intent_only")
        require(type(observation)is dict and set(observation)=={"origin","output_hex"},"closed_unattested_observation")
        require(observation["origin"]==ORIGIN and type(observation["origin"])is str,"no_GPU_provenance_alias")
        hx=observation["output_hex"]
        require(type(hx)is str and re.fullmatch("[0-9a-f]{128}",hx)is not None,"canonical_exact64bytes")
        d=retained();require(q["case"]in d["prepares"],"case_identity")
        v=d["prepares"][q["case"]];p=v["packet"]
        require(q["prepare_result_sha256"]==digest(v) and q["packet_sha256"]==digest(p),"complete_result_packet_binding")
        require(v["status"]=="CPU_PAIR64_INGRESS_PACKET_ONLY" and p is not None,"parent_STOP_no_output")
        require(v["GPU_executed"]is False and v["native_promotion_allowed"]is False
                and v["phase_RN_executed"]==0 and v["producer_replays"]==0,"retained_CPU_only")
        require((p["input_bytes"],p["expected_bytes"],p["output_bytes"],p["total_SSBO_bytes"])==(64,48,64,176),"specific_SSBO_extents")
        a=bytes.fromhex(p["input_hex"]);reference=bytes.fromhex(p["expected_hex"])
        require(len(a)==64 and len(reference)==48 and a[:16]==struct.pack("<4I",TAG,1,3,16)
                and a[16:]==reference,"sealed_packet_consistency")
        raw=bytes.fromhex(hx);words=list(struct.unpack("<16I",raw))
        require(words[:4]==[TAG,3,0xffffffff,1],"ALL_commit_status")
        # ALL payload words and finite exponents BEFORE emitting any SOURCE/relative rows.
        require(raw[16:]==reference,"ALL_bitwise_payload_match")
        for offset in (5,7,9,11,13,15):
            require(((words[offset]>>20)&0x7ff)!=0x7ff,"finite_pair_words")
        rows=[]
        for i,(rid,bid) in enumerate((("S0","S0/mirror"),("S1","S1/mirror"),("S0-minus-S1","relative"))):
            rows.append({"record_id":rid,"branch_id":bid,"hi_lo_uint32":words[4+4*i:8+4*i],
                         "original_scene_sha256":p["original_scene_sha256"],
                         "literal_request_sha256":p["literal_request_sha256"]})
        out.update(status="HOST_OUTPUT_BITWISE_MATCH_NOT_EXECUTION_EVIDENCE",rows=rows,
                   HOST_bitwise_match_certified=True,observation_sha256=sha(raw),output_bytes=64,
                   request_sha256=digest(q),packet_sha256=digest(p),
                   parent_envelope_sha256=p["parent_envelope_sha256"],shader_sha256=p["shader_sha256"],
                   parent_receipt_sha256=PARENT_SHA,pins_verified=73)
    except (ValueError,TypeError,KeyError,OSError,zlib.error) as e:out["reason"]=str(e)
    return out
