"""Pure opt-in HOST resource-policy arithmetic. Not a runtime guard or permission."""
MODEL = "gpu-job-resource-policy-HOST-v1"
GIB = 2**30
MIN_CELL_BYTES = 1024
RAM_FLOOR = 4*GIB
VRAM_CAP = 18*GIB
TEMP_CAP_MILLIC = 80000
HISTORICAL_DEADLINE = 1790748000  # 2026-09-30 06:00:00 UTC; never extended.
MAX_SNAPSHOT_AGE_S = 5  # New opt-in conservative freshness limit, not legacy policy.
PLAN_KEYS = {"job_id","kernel","cells","bytes_per_cell","host_fixed_bytes",
 "host_temporary_bytes","host_margin_bytes","device_fixed_bytes","device_temporary_bytes",
 "device_margin_bytes","pilot","timeout_s","issued_utc_s","deadline_utc_s"}
SNAP_KEYS = {"job_id","sampled_utc_s","ram_available_bytes","device_used_bytes",
 "device_total_bytes","temperature_millic","elapsed_s","gpuq_job_id","claude_job_id",
 "process_scan_job_id","exclusive_gpu","gpuq_checked","claude_checked","processes_checked",
 "guard_fail_closed_checked","post_0x9f_headroom_checked"}
BOOL_KEYS = {"exclusive_gpu","gpuq_checked","claude_checked","processes_checked",
 "guard_fail_closed_checked","post_0x9f_headroom_checked"}

def integer(v):
 if type(v) is not int or not 0 <= v <= 2**63-1:
  raise ValueError("nonnegative bounded integer required; bool/float invalid")
 return v

def word(v):
 if type(v) is not str or not v or len(v)>128:
  raise ValueError("nonempty bounded job/kernel identifier required")
 return v

def closed(v,keys):
 if type(v) is not dict or set(v)!=keys:raise ValueError("closed schema required")

def evaluate(plan,snapshot,*,now_utc_s,model):
 reasons=[];budget=None
 try:
  if type(model) is not str or model!=MODEL:raise ValueError("explicit opt-in model")
  now=integer(now_utc_s);closed(plan,PLAN_KEYS);closed(snapshot,SNAP_KEYS)
  for k in PLAN_KEYS-{"job_id","kernel","pilot"}:integer(plan[k])
  for k in SNAP_KEYS-BOOL_KEYS-{"job_id","gpuq_job_id","claude_job_id","process_scan_job_id"}:
   integer(snapshot[k])
  for k in ("job_id","kernel"):word(plan[k])
  for k in ("job_id","gpuq_job_id","claude_job_id","process_scan_job_id"):word(snapshot[k])
  if type(plan["pilot"]) is not bool:raise ValueError("pilot bool required")
  for k in BOOL_KEYS:
   if type(snapshot[k]) is not bool:raise ValueError("checked bool required")
 except (ValueError,TypeError):
  reasons.append("invalid_or_missing_INPUT")
 else:
  if plan["cells"]==0:reasons.append("unknown_or_zero_cells")
  if plan["bytes_per_cell"]<MIN_CELL_BYTES:reasons.append("cell_budget_below_1024")
  if plan["kernel"].upper()=="MLP32768":reasons.append("forbidden_MLP32768")
  if not 0<plan["timeout_s"]<=(120 if plan["pilot"] else 600):reasons.append("child_timeout_policy")
  if not HISTORICAL_DEADLINE<plan["issued_utc_s"]<=now<plan["deadline_utc_s"]:
   reasons.append("new_job_deadline_required")
  if plan["deadline_utc_s"]-now<plan["timeout_s"]+60:reasons.append("deadline_shutdown_margin")
  age=now-snapshot["sampled_utc_s"]
  if not 0<=age<=MAX_SNAPSHOT_AGE_S:reasons.append("telemetry_stale_or_future")
  if snapshot["elapsed_s"]>=plan["timeout_s"]:reasons.append("job_timeout")
  for k in ("job_id","gpuq_job_id","claude_job_id","process_scan_job_id"):
   if snapshot[k]!=plan["job_id"]:reasons.append("job_binding_"+k)
  for k in sorted(BOOL_KEYS):
   if snapshot[k] is not True:reasons.append("missing_"+k)
  if not all(plan[k]>0 for k in ("host_temporary_bytes","host_margin_bytes",
                               "device_temporary_bytes","device_margin_bytes")):
   reasons.append("explicit_positive_temporaries_and_margins_required")
  cells=plan["cells"]*max(MIN_CELL_BYTES,plan["bytes_per_cell"])
  host=cells+sum(plan[k] for k in ("host_fixed_bytes","host_temporary_bytes","host_margin_bytes"))
  device=cells+sum(plan[k] for k in ("device_fixed_bytes","device_temporary_bytes","device_margin_bytes"))
  ram_after=snapshot["ram_available_bytes"]-host
  device_after=snapshot["device_used_bytes"]+device
  budget={"cell_bytes":cells,"host_additional_peak_bytes":host,
          "device_additional_peak_bytes":device,"ram_after_budget_bytes":ram_after,
          "device_total_after_budget_bytes":device_after}
  if ram_after<RAM_FLOOR:reasons.append("ram_floor_after_budget")
  if device_after>VRAM_CAP:reasons.append("device_18GiB_cap")
  if snapshot["device_used_bytes"]>snapshot["device_total_bytes"] or device_after>snapshot["device_total_bytes"]:
   reasons.append("physical_device_memory")
  if snapshot["temperature_millic"]>TEMP_CAP_MILLIC:reasons.append("temperature_80C_cap")
 return {"model":MODEL,"status":"CONDITIONAL_POLICY_FIT" if not reasons else "STOP",
         "reasons":reasons,"budget":budget,"GPU_job_admission":False,"GPU_executed":False,
         "telemetry_authenticated":False,"reservation_authenticated":False,
         "guard_implemented":False,"near_limit_headroom_proved":False,
         "full_costs":"UNMEASURED_NOT_ZERO",
         "scope":"untrusted declarations and conservative arithmetic only; no launch permit"}
