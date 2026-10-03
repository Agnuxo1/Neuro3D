"""Independent stdlib wire oracle: no codec/producer imports, no native float arithmetic."""
from fractions import Fraction as F
from pathlib import Path
import base64, hashlib, json, re, zlib
ROOT=Path(__file__).resolve().parents[2]
RECEIPT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PAIR64-WIRE-HOST-001-CODEX.json"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-TWOFOLD-CPU-001-CODEX.json"
PARENT_SHA="f1dbec5a319c80cc0457d0e32f848641bf752329ccb3e9db687c9cf3c9520b6b"
MODEL="precision-axial-common-detector-pair64-wire-HOST-v1"
ABI="HOST_LE_U32_PAIR64_PHASE_V1_NOT_GPU_ABI"
FLAGS=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
       "coherent_field_admission_allowed","interference_phase_certified")
KEYS={"case","result_sha256","original_scene_sha256","literal_request_sha256","abi","units"}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(value):return sha(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def demand(ok,label):
    if not ok:raise AssertionError(label)
def rational(value):
    demand(type(value)is list and len(value)==2 and all(type(x)is int for x in value) and value[1]>0,"rational")
    return F(*value)
def pair(value):return [value.numerator,value.denominator]
def ieee(word):
    demand(type(word)is int and 0<=word<2**64,"IEEE word")
    sign=-1 if word>>63 else 1
    exponent=(word>>52)&2047; mantissa=word&((1<<52)-1)
    demand(exponent!=2047,"nonfinite")
    if exponent==0:return F(sign*mantissa,1<<1074)
    power=exponent-1075
    return F(sign*((1<<52)+mantissa))*(F(1<<power) if power>=0 else F(1,1<<(-power)))
def captured(run,expected_status,tests):
    demand(run["timed_out"] is False and run["threads"]==1 and run["affinity_mask"]==1
           and run["hard_child_timeout_seconds"]==60,"bounded CPU")
    stream=zlib.decompressobj()
    raw=stream.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
    demand(len(raw)<=1024*1024 and stream.eof and not stream.unused_data and not stream.unconsumed_tail,"closed capture")
    demand(sha(raw)==run["stdout_sha256"] and len(raw)==run["stdout_bytes"],"capture identity")
    value=json.loads(raw);demand(value["status"]==expected_status and value["tests"]==tests,"suite verdict")
    demand(run["rc"]==(0 if expected_status=="PASS" else 1),"suite rc")
    return value["data"]
def pins(receipt,expected):
    demand(len(receipt["code_doc_sha256"])==expected,"pins count")
    for p,h in receipt["code_doc_sha256"].items():demand(sha((ROOT/p).read_bytes())==h,"pin "+p)
def selector(data,name):
    q=data["requests"][name];v=data["results"][name]
    return {"case":name,"result_sha256":digest(v),"original_scene_sha256":q.get("original_scene_sha256"),
            "literal_request_sha256":q.get("literal_request_sha256"),"abi":ABI,"units":"cycles/rad"}
def selected(q,model,data):
    if model!=MODEL or type(model)is not str or type(q)is not dict or set(q)!=KEYS:return None
    if not all(type(x)is str for x in q.values()) or q["abi"]!=ABI or q["units"]!="cycles/rad":return None
    if q["case"] not in data["results"]:return None
    old=data["results"][q["case"]];request=data["requests"][q["case"]]
    if q["result_sha256"]!=digest(old) or q["original_scene_sha256"]!=request.get("original_scene_sha256")        or q["literal_request_sha256"]!=request.get("literal_request_sha256"):return None
    if old["status"]!="CPU_DECLARED_TWOFOLD_PHASE_BOUND_ONLY":return None
    demand(old["literal_request_sha256"]==q["literal_request_sha256"],"parent literal")
    demand(old["representation"]=="PAIR_FLOAT64_CPU_NOT_GPU_ABI" and all(old[k]is False for k in FLAGS),"parent flags")
    demand([(x["source_id"],x["branch_id"]) for x in old["rows"]]==[("S0","S0/mirror"),("S1","S1/mirror")]
           and old["emitted_sources"]==old["rows"] and old["relative"]["source_order"]==["S0","S1"],"parent coverage")
    for row in old["rows"]+[old["relative"]]:
        h,l=row["pair_uint64"];represented=ieee(h)+ieee(l);bound=rational(row["total_cycle_error_bound"])
        demand(bound>=0 and rational(row["represented_cycles"])==represented
               and abs(represented-rational(row["original_declared_cycles"]))<=bound,"parent bound")
        demand(rational(row["total_phase_bound_rad"])==8*bound
               and 8*bound<=rational(row["budget_rad"]) and row["budget_fits"]is True,"parent caps")
    return old
def envelope(q,old):
    words=[w for row in old["rows"]+[old["relative"]] for w in row["pair_uint64"]]
    raw=b"".join(w.to_bytes(8,"little") for w in words)
    return {"abi":ABI,"model":MODEL,"parent_receipt_sha256":PARENT_SHA,"result_sha256":q["result_sha256"],
            "parent_request_sha256":old["request_sha256"],"literal_request_sha256":q["literal_request_sha256"],
            "original_scene_sha256":q["original_scene_sha256"],"units":"cycles/rad","endian":"little",
            "record_count":3,"record_stride_bytes":16,"payload_bytes":48,"record_ids":["S0","S1","S0-minus-S1"],
            "branch_ids":["S0/mirror","S1/mirror","relative"],"word_layout":["hi.lo32","hi.hi32","lo.lo32","lo.hi32"],
            "phase_contract_sha256":digest({"rows":old["rows"],"relative":old["relative"]}),
            "payload_hex":raw.hex(),"payload_sha256":sha(raw)}
def admissible(e,want):
    if type(e)is not dict or set(e)!=set(want):return False
    if not all(type(e[k])is int for k in ("record_count","record_stride_bytes","payload_bytes")):return False
    excluded={"payload_hex","payload_sha256"}
    if digest({k:v for k,v in e.items() if k not in excluded})!=digest({k:v for k,v in want.items() if k not in excluded}):return False
    if type(e["payload_hex"])is not str or re.fullmatch("[0-9a-f]{96}",e["payload_hex"])is None:return False
    raw=bytes.fromhex(e["payload_hex"])
    if type(e["payload_sha256"])is not str or e["payload_sha256"]!=sha(raw):return False
    words=[int.from_bytes(raw[i:i+8],"little") for i in range(0,48,8)]
    if any(((w>>52)&2047)==2047 for w in words):return False
    return e["payload_hex"]==want["payload_hex"]
def checked_output(out,accepted,operation):
    demand(out["model"]==MODEL and out["abi"]==ABI and out["operation"]==operation,"output contract")
    demand(all(out[k]is False for k in FLAGS) and out["phase_arithmetic_RN_executed"]==0
           and out["producer_replays"]==0 and out["parameter_encoder_replays"]==0,"no arithmetic/replay/promotion")
    demand(out["detector_complex_field"]is None and out["detector_power"]is None and out["source_amplitude"]is None
           and out["full_costs"]=="UNMEASURED_NOT_ZERO","no fabricated field/costs")
    if accepted:
        demand(out["reason"]is None and out["HOST_contract_certified"]is True and out["transport_error_cycles"]==[0,1],"accepted")
        demand(out["status"]==("HOST_PAIR64_WIRE_PACK_ONLY" if operation=="pack" else "HOST_PAIR64_WIRE_ROUNDTRIP_ONLY"),"status")
    else:
        demand(out["status"]=="STOP" and type(out["reason"])is str and out["reason"]
               and out["HOST_contract_certified"]is False and out["envelope"]is None and out["decoded_rows"]==[]
               and out["transport_error_cycles"]is None,"atomic STOP")
def main():
    receipt=json.loads((ROOT/RECEIPT).read_bytes())
    pins(receipt,67)
    demand(receipt["parent_sha256"]==PARENT_SHA,"new parent binding")
    parent_raw=(ROOT/PARENT).read_bytes();demand(sha(parent_raw)==PARENT_SHA,"sealed parent")
    parent=json.loads(parent_raw);pins(parent,62)
    old=captured(parent["test_run"],"PASS",7)
    initial=captured(receipt["retained_initial_failure"],"FAIL",8)
    demand("KeyError" in receipt["retained_initial_failure"]["stderr"]
           and "literal_request_sha256" in receipt["retained_initial_failure"]["stderr"],"preserved selector failure")
    new=captured(receipt["test_run"],"PASS",8)
    previous=captured(receipt["retained_first_passing_suite"],"PASS",8)
    failed_oracle=receipt["retained_oracle_initial_failure"]
    demand(failed_oracle["rc"]==1 and failed_oracle["timed_out"]is False
           and "AssertionError: selector wrong_model" in failed_oracle["stderr"],"preserved oracle registry collision")
    demand(previous["selectors"]["wrong_model"]!=selector(old,"wrong_model"),"collision fact preserved")
    demand(set(new["pack_results"])==set(old["results"]) and len(old["results"])==30,"all30")
    packed=0;pack_stop=0;decoded=0;consume_stop=0;byte_total=0
    for name,out in new["pack_results"].items():
        q=new["pack_selectors"][name];demand(q==selector(old,name),"selector "+name)
        v=selected(q,MODEL,old);ok=v is not None;checked_output(out,ok,"pack")
        if ok:
            demand(out["envelope"]==envelope(q,v) and out["decoded_rows"]==[],"exact pack "+name)
            packed+=1;byte_total+=48
        else:pack_stop+=1
    demand(packed==11 and pack_stop==19,"pack totals")
    demand(set(new["consume_results"])==set(new["consume_inputs"])==set(new["consume_models"]),"complete consume inputs")
    for name,out in new["consume_results"].items():
        q=new["selectors"][name];v=selected(q,new["consume_models"][name],old)
        ok=v is not None and admissible(new["consume_inputs"][name],envelope(q,v))
        checked_output(out,ok,"consume")
        if ok:
            want=envelope(q,v);raw=bytes.fromhex(new["consume_inputs"][name]["payload_hex"]);rows=[]
            for i,row in enumerate(v["rows"]+[v["relative"]]):
                h=int.from_bytes(raw[16*i:16*i+8],"little");l=int.from_bytes(raw[16*i+8:16*i+16],"little")
                rows.append({"record_id":want["record_ids"][i],"branch_id":want["branch_ids"][i],
                             "pair_uint64":[h,l],"represented_cycles":pair(ieee(h)+ieee(l)),
                             "original_declared_cycles":row["original_declared_cycles"],
                             "total_cycle_error_bound":row["total_cycle_error_bound"],
                             "total_phase_bound_rad":row["total_phase_bound_rad"],"budget_rad":row["budget_rad"]})
            demand(out["decoded_rows"]==rows and out["envelope"]is None,"exact decode "+name);decoded+=1
        else:consume_stop+=1
    control=new["controls"]["wrong_float64_add_decoder"]
    demand(control["exact_pair"]==pair(F(14)+F(1,2**56)) and control["collapsed_RN64"]==[14,1]
           and control["lost_cycles"]==[1,2**56] and control["synthetic_decoder_RN64_adds"]==1
           and control["production_decoder_RN64_adds"]==0,"lost low component control")
    demand(all(new["controls"][k]is True for k in ("bytes_payload_rejected","sealed_parent_dependency_rejection",
                                                  "returned_copy_no_parent_mutation")),"controls")
    demand(new["consume_results"]["second_source_bit_rehashed"]["decoded_rows"]==[]
           and new["consume_results"]["negative_zero_low_rehashed"]["status"]=="STOP","atomic/bit identity")
    print(json.dumps({"status":"PASS","pins":67,"pack_admitted":packed,"pack_STOP":pack_stop,
                      "consume_admitted":decoded,"consume_STOP":consume_stop,
                      "registered_main_pack_payload_bytes":byte_total,"decoded_records":3*decoded,
                      "producer_replays":0,"phase_RN_executed":0,"control_only_RN64_adds":1,
                      "initial_failure_preserved":True,"GPU_executed":False},sort_keys=True))
if __name__=="__main__":main()
