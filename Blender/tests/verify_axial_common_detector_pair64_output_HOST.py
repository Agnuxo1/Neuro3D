"""Independent stdlib receipt oracle. Never imports/runs a producer, shader, comparator or compiler."""
import ast,base64,hashlib,json,re,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-AXIAL-COMMON-DETECTOR-PAIR64-OUTPUT-HOST-001"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PAIR64-INGRESS-SHADERC-001-CODEX.json"
PARENT_SHA="54321d7fc359b9734274b7c0181a0c0f849b58c634d5c7bfb93e2ec2d8ea48ae"
MODEL="precision-axial-common-detector-pair64-output-HOST-v1"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def unpack(t):
    assert t["rc"]==0 and t["timed_out"]is False
    assert t["threads"]==1 and t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail
    assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
    v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==7
    return v["data"]

def expected_ok(i,parent):
    q=i["selector"];o=i["observation"]
    if type(i["model"])is not str or i["model"]!=MODEL:return False
    if type(q)is not dict or set(q)!={"case","prepare_result_sha256","packet_sha256","intent"}:return False
    if not all(type(v)is str for v in q.values()) or q["intent"]!="COMPARE_UNATTESTED_OUTPUT_ONLY":return False
    if type(o)is not dict or set(o)!={"origin","output_hex"}:return False
    if type(o["origin"])is not str or o["origin"]!="UNATTESTED_BYTES_NOT_GPU_READBACK":return False
    hx=o["output_hex"]
    if type(hx)is not str or re.fullmatch("[0-9a-f]{128}",hx)is None:return False
    if q["case"]not in parent["prepares"]:return False
    v=parent["prepares"][q["case"]];p=v["packet"]
    if q["prepare_result_sha256"]!=digest(v) or q["packet_sha256"]!=digest(p):return False
    if v["status"]!="CPU_PAIR64_INGRESS_PACKET_ONLY" or p is None:return False
    raw=bytes.fromhex(hx)
    if raw[:16]!=bytes.fromhex("3134365003000000ffffffff01000000"):return False
    if raw[16:]!=bytes.fromhex(p["expected_hex"]):return False
    # Inspect the two uint64 exponent fields of each row, not float arithmetic.
    return all(((int.from_bytes(raw[j:j+8],"little")>>52)&2047)!=2047 for j in range(16,64,8))

def main():
    r=json.loads((ROOT/("coordinacion/respuestas/"+ID+"-CODEX.json")).read_bytes())
    assert r["id"]==ID and r["model"]==MODEL and r["status"]=="CPU_HOST_ONLY"
    pins=r["code_doc_sha256"];assert len(pins)==78
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    raw=(ROOT/PARENT).read_bytes();assert sha(raw)==PARENT_SHA
    pr=json.loads(raw);assert len(pr["code_doc_sha256"])==73
    assert all(pins[p]==h for p,h in pr["code_doc_sha256"].items())
    d=unpack(r["test_run"]);parent=unpack(pr["test_run"])
    assert len(parent["prepares"])==39 and sum(v["packet"]is not None for v in parent["prepares"].values())==11
    assert set(d["inputs"])==set(d["results"])
    forbidden=("GPU_executed","GPU_job_admission","actual_GPU_readback_available","GPU_semantics_certified",
               "execution_authenticated","freshness_authenticated","host_completion_barrier_certified",
               "resource_guard_certified","physical_scene_authenticated","native_hit_coverage_certified",
               "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
               "coherent_field_admission_allowed","interference_phase_certified","native_promotion_allowed")
    good=bad=0
    for name,i in d["inputs"].items():
        v=d["results"][name];ok=expected_ok(i,parent)
        assert all(v[k]is False for k in forbidden),name
        assert v["field"]is v["power"]is v["amplitude"]is None
        assert v["new_phase_RN_operations"]==v["producer_replays"]==v["new_compiler_calls"]==0
        assert v["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert v["copied_or_stale_CPU_bytes_can_match"]is True and v["same_value_slot_permutation_detectable"]is False
        if not ok:
            bad+=1;assert v["status"]=="STOP" and v["rows"]==[] and v["HOST_bitwise_match_certified"]is False,name
            continue
        good+=1;assert v["status"]=="HOST_OUTPUT_BITWISE_MATCH_NOT_EXECUTION_EVIDENCE" and v["HOST_bitwise_match_certified"]is True
        q=i["selector"];p=parent["prepares"][q["case"]]["packet"];raw=bytes.fromhex(i["observation"]["output_hex"])
        words=struct.unpack("<16I",raw)
        assert len(v["rows"])==3 and v["output_bytes"]==64
        assert v["request_sha256"]==digest(q) and v["packet_sha256"]==digest(p)
        assert v["observation_sha256"]==sha(raw) and v["parent_receipt_sha256"]==PARENT_SHA and v["pins_verified"]==73
        assert v["parent_envelope_sha256"]==p["parent_envelope_sha256"] and v["shader_sha256"]==p["shader_sha256"]
        for n,(rid,bid) in enumerate((("S0","S0/mirror"),("S1","S1/mirror"),("S0-minus-S1","relative"))):
            assert v["rows"][n]==dict(record_id=rid,branch_id=bid,hi_lo_uint32=list(words[4+4*n:8+4*n]),
                original_scene_sha256=p["original_scene_sha256"],literal_request_sha256=p["literal_request_sha256"])
    # The whole recorded parent corpus and each of the sixteen uint32 mutations must be present.
    assert all("parent_"+k in d["results"] for k in parent["prepares"])
    assert all(d["results"]["word_"+str(i)]["status"]=="STOP" for i in range(16))
    assert good==13 and bad==93,(good,bad)
    assert all(d["controls"][k]is True for k in ("changed_parent_rejected","read_denied_rejected","same_value_permutation_not_detectable"))
    assert d["controls"]["parent_producer_compiler_replays"]==0
    source=(ROOT/"Blender/benchmarks/capacity_audit/axial_common_detector_pair64_output_HOST_v1.py").read_text()
    tree=ast.parse(source)
    imports=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
        if isinstance(n,ast.ImportFrom):imports.append(n.module)
    assert set(imports)=={"base64","hashlib","json","re","struct","zlib","pathlib"}
    print(json.dumps({"status":"PASS","pins":78,"parent_prepares":39,"comparisons":good+bad,
                     "HOST_matches":good,"STOPs":bad,"rows_emitted":good*3,
                     "CPU_ONLY":True,"GPU_executed":False,"compiler_replays":0},sort_keys=True))
if __name__=="__main__":main()
