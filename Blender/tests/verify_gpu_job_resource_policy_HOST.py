"""Independent stdlib retained policy oracle; no imports of production or old guard."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
r=json.loads((ROOT/"coordinacion/respuestas/GPU-JOB-RESOURCE-POLICY-HOST-001-CODEX.json").read_bytes())
sha=lambda b:hashlib.sha256(b).hexdigest()
for path,h in r["code_doc_sha256"].items():assert sha((ROOT/path).read_bytes())==h,path
t=r["test_run"];assert t["rc"]==0 and t["timed_out"] is False and t["threads"]==1 and t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60 and t["elapsed_seconds"]<60
raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True));assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
report=json.loads(raw);assert report["status"]=="PASS" and report["tests"]==4
d=report["data"];assert d["synthetic_only"] is True
def check(a,b,o):
 cells=a["cells"]*max(1024,a["bytes_per_cell"])
 host=cells+a["host_fixed_bytes"]+a["host_temporary_bytes"]+a["host_margin_bytes"]
 dev=cells+a["device_fixed_bytes"]+a["device_temporary_bytes"]+a["device_margin_bytes"]
 assert o["budget"]=={"cell_bytes":cells,"host_additional_peak_bytes":host,"device_additional_peak_bytes":dev,
   "ram_after_budget_bytes":b["ram_available_bytes"]-host,"device_total_after_budget_bytes":b["device_used_bytes"]+dev}
 for key in ("GPU_job_admission","GPU_executed","telemetry_authenticated","reservation_authenticated","guard_implemented","near_limit_headroom_proved"):assert o[key] is False
 assert o["full_costs"]=="UNMEASURED_NOT_ZERO"
check(d["plan"],d["snapshot"],d["result"]);assert d["result"]["status"]=="CONDITIONAL_POLICY_FIT"
for key in ("boundary","nonpilot600"):
 v=d[key];check(v["plan"],v["snapshot"],v["result"]);assert v["result"]["reasons"]==[]
assert d["boundary"]["result"]["budget"]["ram_after_budget_bytes"]==4*2**30
assert d["boundary"]["result"]["budget"]["device_total_after_budget_bytes"]==18*2**30
# Count coverage from the actual closed schemas, not a handwritten total.
typed_count=len(d["plan"])+len(d["snapshot"])+4*8+3+2
assert typed_count==67 and d["typed_missing_closed_rejections"]==typed_count
assert len(d["controls"])==32
def independent_reasons(a,b):
 now=1790978400;reasons=set()
 if a["cells"]==0:reasons.add("unknown_or_zero_cells")
 if a["bytes_per_cell"]<1024:reasons.add("cell_budget_below_1024")
 if a["kernel"].upper()=="MLP32768":reasons.add("forbidden_MLP32768")
 if not 1<=a["timeout_s"]<=(120 if a["pilot"] else 600):reasons.add("child_timeout_policy")
 if not 1790748000<a["issued_utc_s"]<=now<a["deadline_utc_s"]:reasons.add("new_job_deadline_required")
 if a["deadline_utc_s"]-now<a["timeout_s"]+60:reasons.add("deadline_shutdown_margin")
 if not 0<=now-b["sampled_utc_s"]<=5:reasons.add("telemetry_stale_or_future")
 if b["elapsed_s"]>=a["timeout_s"]:reasons.add("job_timeout")
 for key in ("job_id","gpuq_job_id","claude_job_id","process_scan_job_id"):
  if b[key]!=a["job_id"]:reasons.add("job_binding_"+key)
 for key in ("exclusive_gpu","gpuq_checked","claude_checked","processes_checked","guard_fail_closed_checked","post_0x9f_headroom_checked"):
  if b[key] is not True:reasons.add("missing_"+key)
 if any(a[key]<=0 for key in ("host_temporary_bytes","host_margin_bytes","device_temporary_bytes","device_margin_bytes")):
  reasons.add("explicit_positive_temporaries_and_margins_required")
 cell=a["cells"]*max(1024,a["bytes_per_cell"])
 host=cell+a["host_fixed_bytes"]+a["host_temporary_bytes"]+a["host_margin_bytes"]
 dev=cell+a["device_fixed_bytes"]+a["device_temporary_bytes"]+a["device_margin_bytes"]
 if b["ram_available_bytes"]-host<4*2**30:reasons.add("ram_floor_after_budget")
 if b["device_used_bytes"]+dev>18*2**30:reasons.add("device_18GiB_cap")
 if b["device_used_bytes"]>b["device_total_bytes"] or b["device_used_bytes"]+dev>b["device_total_bytes"]:reasons.add("physical_device_memory")
 if b["temperature_millic"]>80000:reasons.add("temperature_80C_cap")
 return reasons
for v in ({"plan":d["plan"],"snapshot":d["snapshot"],"result":d["result"]},d["boundary"],d["nonpilot600"]):
 assert independent_reasons(v["plan"],v["snapshot"])==set(v["result"]["reasons"])==set()
for c in d["controls"]:
 check(c["plan"],c["snapshot"],c["result"])
 assert c["result"]["status"]=="STOP" and c["expected_reason"] in c["result"]["reasons"]
 assert independent_reasons(c["plan"],c["snapshot"])==set(c["result"]["reasons"])
assert any(c["name"]=="monitor_budget_retained_one_byte_ram" and c["result"]["budget"]["ram_after_budget_bytes"]==4*2**30-1 for c in d["controls"])
assert r["historical_guard_sha256"]=="958163c3bba7f16d619c9788893771eaf7fc6a17b1e295eae8cf84b15bfcd818"
assert r["actual_GPU_job_admission"] is False and r["live_telemetry_collected"] is False
assert len(r["new_failures"])==1
failure=r["new_failures"][0];assert failure["run"]["rc"]==1 and "AssertionError" in failure["run"]["stderr"]
for path,record in failure["initial_sources"].items():
 original=zlib.decompress(base64.b64decode(record["source_zlib_base64"],validate=True))
 assert len(original)==record["bytes"] and sha(original)==record["sha256"]==failure["initial_pins"][path]
for path in ("Blender/benchmarks/capacity_audit/gpu_job_resource_policy_HOST_v1.py","Blender/tests/test_gpu_job_resource_policy_HOST.py"):
 assert failure["initial_sources"][path]["sha256"]==r["code_doc_sha256"][path] # Safety and test cases unchanged.
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"unsafe_controls":32,"typed_missing_closed":typed_count,"GPU_admission":False,"scope":"synthetic conservative arithmetic; runtime guard/reservation/headroom unproved"}))
