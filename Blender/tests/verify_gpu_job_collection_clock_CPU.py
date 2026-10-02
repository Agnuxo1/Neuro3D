"""Independent retained endpoint controls verifier. No production imports or spawn."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((ROOT/"coordinacion/respuestas/GPU-JOB-COLLECTION-CLOCK-CPU-001-CODEX.json").read_bytes())
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
repair=r["format_review_repair"]
assert repair["initial_git_review"]["exit_code"]==1
for p,encoded in repair["original_sources_base64"].items():
 original=base64.b64decode(encoded,validate=True)
 assert sha(original)==repair["original_pins"][p]
 if p!="Blender/tests/verify_gpu_job_collection_clock_CPU.py":
  current=(ROOT/p).read_bytes()
  assert original.replace(b"\r\n",b"\n").rstrip(b"\n")==current.replace(b"\r\n",b"\n").rstrip(b"\n"),p
t=r["test_run"]
assert t["rc"]==0 and not t["timed_out"] and t["threads"]==t["affinity_mask"]==1
assert t["hard_child_timeout_seconds"]==60 and t["elapsed_seconds"]<60
raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==7
d=v["data"];assert d["no_live_resources"] is True
rows={row["name"]:row for row in d["controls"]}
assert len(rows)==16 and len(d["controls"])==16
flags=("GPU_job_admission","GPU_executed","live_resource_telemetry","runtime_GPU_guard",
       "reservation_authenticated","clock_pair_atomic_authenticated","arbitrary_callback_timeout_implemented")
for name,row in rows.items():
 out=row["result"]
 assert all(out[key] is False for key in flags)
 if name in ("valid_endpoint","real_OS_clock"):assert out["state"]=="CONTINUE_SYNTHETIC_CONTROL"
 else:assert out["state"]=="STOP"
 if name.startswith("pre_") or name=="invalid_model":assert out["collector_calls"]==0
 else:assert out["collector_calls"]==1
ce=d["counterexample"]
assert ce["preonly_frozen"]["state"]=="CONTINUE_SYNTHETIC_CONTROL"
assert ce["endpoint"]["reasons"]==["elapsed_monotonic_mismatch"]
assert ce["retry"]==ce["endpoint"] and ce["snapshot_unchanged"] is True
assert ce["endpoint"]["collection_ns"]==100000000
assert ce["endpoint"]["after"]["monotonic_ns"]-ce["endpoint"]["before"]["monotonic_ns"]==100000000
assert rows["stale"]["result"]["reasons"]==["resource_policy:telemetry_stale_or_future"]
assert "resource_policy:new_job_deadline_required" in rows["expired"]["result"]["reasons"]
real=rows["real_OS_clock"]
assert real["clock_origin"]=="OS_CLOCK_SYNTHETIC_SNAPSHOT"
assert real["result"]["collection_ns"]>=0
plan=d["new_synthetic_plan"]
assert plan["job_id"]=="CPU-ENDPOINT-SYNTHETIC" and plan["deadline_utc_s"]==plan["issued_utc_s"]+300
children=d["actual_CPU_children"];assert len(children)==1
child=children[0]
assert child["status"]=="TIMEOUT" and child["timeout_s"]==0.25
assert child["process_started"] and child["own_process_terminated"] and child["cleanup_confirmed"]
assert type(child["own_pid"]) is int and child["own_pid"]>0 and child["returncode"]!=0
assert child["origin"]=="SYNTHETIC_CONTROL_NOT_LIVE_TELEMETRY"
for key in ("GPU_job_admission","GPU_executed","live_telemetry_collected","foreign_processes_touched"):assert child[key] is False
for stream in ("stdout","stderr"):
 out=zlib.decompress(base64.b64decode(child[stream+"_zlib_base64"],validate=True))
 assert len(out)==child[stream+"_bytes"] and sha(out)==child[stream+"_sha256"]
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"controls":len(rows),
 "actual_own_CPU_children":1,"old_preonly_control":"CONTINUE","new_endpoint_control":"STOP",
 "GPU_job_admission":False,"scope":"OS clocks, synthetic resources only"},sort_keys=True))
