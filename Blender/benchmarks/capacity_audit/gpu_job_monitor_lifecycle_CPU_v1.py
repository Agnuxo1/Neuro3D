"""Single-thread CPU lifecycle control ONLY. No subprocess, GPU, queue, kill or permit."""
from copy import deepcopy
import hashlib,json
import gpu_job_resource_policy_HOST_v1 as policy
MODEL="gpu-job-monitor-lifecycle-CPU-v1"
MAX_MONITOR_GAP_NS=10**9  # NEW opt-in stricter cadence; no legacy change.
def digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

class Monitor:
 def __init__(self,plan,*,now_utc_s,monotonic_ns,model):
  self._state="CONTROL_READY";self._reasons=[];self._policy=None;self._samples=0
  self._plan=None;self._plan_sha=None;self._start_ns=None;self._last_ns=None;self._last_utc=None
  try:
   if type(model) is not str or model!=MODEL:raise ValueError("explicit CPU-control model")
   policy.integer(now_utc_s);policy.integer(monotonic_ns);policy.closed(plan,policy.PLAN_KEYS)
   self._plan=json.loads(json.dumps(plan,allow_nan=False));self._plan_sha=digest(self._plan)
   self._start_ns=self._last_ns=monotonic_ns;self._last_utc=now_utc_s
  except (ValueError,TypeError):
   self._stop(["invalid_constructor_INPUT"])
 def _stop(self,reasons):
  self._state="STOP";self._reasons=list(reasons)
  return self.view()
 def view(self):
  return deepcopy({"model":MODEL,"state":self._state,"reasons":self._reasons,
   "plan_sha256":self._plan_sha,"samples_evaluated":self._samples,"policy_result":self._policy,
   "GPU_job_admission":False,"GPU_executed":False,"runtime_guard_implemented":False,
   "telemetry_authenticated":False,"reservation_authenticated":False,
   "owned_child_control_implemented":False,"thread_safe":False,
   "scope":"CPU single-thread lifecycle with untrusted injected clocks/snapshots; NO launch permit"})
 def sample(self,read_snapshot,*,now_utc_s,monotonic_ns):
  # Terminal gate precedes clocks, plan inspection and ANY collector call. No reset API.
  if self._state=="STOP":return self.view()
  try:
   policy.integer(now_utc_s);policy.integer(monotonic_ns)
   if digest(self._plan)!=self._plan_sha:return self._stop(["plan_integrity_changed"])
   if monotonic_ns<self._last_ns:return self._stop(["monotonic_clock_rollback"])
   if now_utc_s<self._last_utc:return self._stop(["wall_clock_rollback"])
   if monotonic_ns-self._last_ns>MAX_MONITOR_GAP_NS:return self._stop(["monitor_sample_gap"])
   elapsed=(monotonic_ns-self._start_ns)//10**9
   if not callable(read_snapshot):return self._stop(["collector_not_callable"])
  except (ValueError,TypeError):
   return self._stop(["invalid_clock_INPUT"])
  try:
   snapshot=read_snapshot()
  except BaseException as exc:
   result=self._stop(["collector_error:"+type(exc).__name__])
   if not isinstance(exc,Exception):raise  # Preserve interrupt semantics, but STOP remains set.
   return result
  try:
   policy.closed(snapshot,policy.SNAP_KEYS)
   if type(snapshot["elapsed_s"]) is not int or snapshot["elapsed_s"]!=elapsed:
    return self._stop(["elapsed_monotonic_mismatch"])
   self._policy=policy.evaluate(self._plan,snapshot,now_utc_s=now_utc_s,model=policy.MODEL)
  except Exception as exc:
   return self._stop(["policy_error:"+type(exc).__name__])
  self._samples+=1;self._last_ns=monotonic_ns;self._last_utc=now_utc_s
  if self._policy["status"]!="CONDITIONAL_POLICY_FIT":
   return self._stop(["resource_policy:"+r for r in self._policy["reasons"]])
  self._state="CONTINUE_SYNTHETIC_CONTROL"
  return self.view()
