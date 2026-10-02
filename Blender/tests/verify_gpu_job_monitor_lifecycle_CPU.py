"""Independent retained checker, no production imports or resource-policy replay."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((ROOT/"coordinacion/respuestas/GPU-JOB-MONITOR-LIFECYCLE-CPU-001-CODEX.json").read_bytes())
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
t=r["test_run"];assert t["rc"]==0 and not t["timed_out"] and t["threads"]==1 and t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60 and t["elapsed_seconds"]<60
raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True));assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==4
d=v["data"];assert d["synthetic_only"] is True
canonical=json.dumps(d["plan"],sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def scopes(o):
 for k in ("GPU_job_admission","GPU_executed","runtime_guard_implemented","telemetry_authenticated","reservation_authenticated","owned_child_control_implemented","thread_safe"):assert o[k] is False
def budget(a,o):
 b=o["policy_result"]["budget"];c=a["cells"]*max(1024,a["bytes_per_cell"])
 assert b["cell_bytes"]==c
 assert b["host_additional_peak_bytes"]==c+a["host_fixed_bytes"]+a["host_temporary_bytes"]+a["host_margin_bytes"]
 assert b["device_additional_peak_bytes"]==c+a["device_fixed_bytes"]+a["device_temporary_bytes"]+a["device_margin_bytes"]
 scopes(o)
first,second=d["progression"]
assert first["plan_sha256"]==second["plan_sha256"]==sha(canonical)
assert first["samples_evaluated"]==1 and second["samples_evaluated"]==2
for o in (first,second):
 assert o["state"]=="CONTINUE_SYNTHETIC_CONTROL";budget(d["plan"],o)
assert len(d["negative_controls"])==15
for c in d["negative_controls"]:
 scopes(c["initial"]);scopes(c["stopped"])
 assert c["initial"]["state"]=="CONTINUE_SYNTHETIC_CONTROL" and c["stopped"]["state"]=="STOP"
 assert c["stopped"]["reasons"] and c["stopped"]==c["after_healthy_retry"] and c["retry_collector_calls"]==0
names={c["name"] for c in d["negative_controls"]}
assert names=={"collector_error","collector_None","collector_not_callable","elapsed_false","monotonic_rollback","wall_rollback","sample_gap","clock_bool","plan_tamper","stale","foreign_job","lost_exclusive","hot","ram_budget_retained","vram_budget_retained"}
assert len(d["timeouts"])==2
for c in d["timeouts"]:
 assert c["timeout_s"]==(120 if c["pilot"] else 600)
 budget(c["plan"],c["first"]);budget(c["plan"],c["last"])
 assert c["last"]["state"]=="STOP" and c["last"]["reasons"]==["resource_policy:job_timeout"]
 assert c["last"]["samples_evaluated"]==c["timeout_s"]+1
 assert c["last"]==c["after"] and c["retry_collector_calls"]==0
assert len(d["initial_model_rejections"])==3
for o in d["initial_model_rejections"]:scopes(o);assert o["state"]=="STOP" and o["reasons"]==["invalid_constructor_INPUT"]
assert d["interrupt"]["stopped"]==d["interrupt"]["after"] and d["interrupt"]["retry_collector_calls"]==0
assert d["interrupt"]["stopped"]["reasons"]==["collector_error:KeyboardInterrupt"]
assert "SENSITIVE_RAW_TEXT" not in raw.decode()
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"sticky_STOP_controls":15,"timeouts_s":[120,600],"initial_model_rejections":3,"GPU_admission":False,"scope":"injected CPU clocks/collectors; no launch/termination/atomic reservation certificate"}))
