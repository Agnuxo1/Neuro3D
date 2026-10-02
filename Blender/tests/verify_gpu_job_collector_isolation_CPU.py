"""Independent retained own-CPU collector checker; NO spawning or producer imports."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((ROOT/"coordinacion/respuestas/GPU-JOB-COLLECTOR-ISOLATION-CPU-001-CODEX.json").read_bytes())
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
assert sha(Path("C:/Python313/python.exe").read_bytes())==r["python_sha256"]
t=r["test_run"];assert t["rc"]==0 and not t["timed_out"] and t["threads"]==1 and t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60 and t["elapsed_seconds"]<60
raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True));assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==4
d=v["data"];assert d["synthetic_only"] is True
children=d["actual_CPU_children"];assert len(children)==8
counts={}
for child in children:
 assert child["process_started"] is True and type(child["own_pid"]) is int and child["own_pid"]>0 # PID reuse is possible; cleanup uses OWN Popen handle, not PID lookup.
 assert child["cleanup_confirmed"] is True and child["returncode"] is not None
 assert child["threads_compute"]==child["affinity_mask"]==1 and 0.05<=child["timeout_s"]<=1
 assert child["worker_sha256"]==r["worker_sha256"] and child["python_sha256"]==r["python_sha256"]
 assert child["origin"]=="SYNTHETIC_CONTROL_NOT_LIVE_TELEMETRY"
 for key in ("GPU_job_admission","GPU_executed","live_telemetry_collected","foreign_processes_touched"):assert child[key] is False
 for stream in ("stdout","stderr"):
  out=zlib.decompress(base64.b64decode(child[stream+"_zlib_base64"],validate=True))
  assert len(out)==child[stream+"_bytes"] and sha(out)==child[stream+"_sha256"]
 assert child["stdout_bytes"]<=8193 and child["stderr_bytes"]<=8192 # Fixed worker maximum, not arbitrary output safety.
 counts[child["status"]]=counts.get(child["status"],0)+1
 if child["status"]=="TIMEOUT":assert child["profile"]=="block" and child["own_process_terminated"] is True and child["returncode"]!=0
 else:assert child["own_process_terminated"] is False
 if child["status"]=="SYNTHETIC_PACKET":
  assert json.loads(zlib.decompress(base64.b64decode(child["stdout_zlib_base64"])))==child["packet"]
 if child["status"]=="OUTPUT_CAP":assert child["stdout_bytes"]==8193
assert counts=={"SYNTHETIC_PACKET":2,"TIMEOUT":2,"PACKET_INVALID":2,"OUTPUT_CAP":1,"CHILD_EXIT_ERROR":1}
assert len(d["prelaunch_rejections"])==16 and all(c["launch_calls"]==0 for c in d["prelaunch_rejections"])
assert sum(c["status"]=="PIN_MISMATCH" for c in d["prelaunch_rejections"])==1
i=d["integration"];assert i["first"]["state"]=="CONTINUE_SYNTHETIC_CONTROL" and i["stopped"]["state"]=="STOP"
assert i["stopped"]["reasons"]==["collector_error:CollectorFailure"] and i["stopped"]==i["retry"] and i["retry_launch_calls"]==0
for stage in ("first","stopped","retry"):
 assert i[stage]["GPU_job_admission"] is False and i[stage]["runtime_guard_implemented"] is False
assert r["actual_GPU_job_admission"] is False and r["live_telemetry_collected"] is False
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"own_CPU_children":8,"own_timeout_cleanup":2,"prelaunch_rejections":16,"retry_spawns":0,"GPU_admission":False,"scope":"fixed synthetic CPU worker only; no live telemetry/guard/atomic reservation proof"}))
