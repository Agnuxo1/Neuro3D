"""CPU synthetic policy controls. No live telemetry, queue operation, GPU or launch."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import gpu_job_resource_policy_HOST_v1 as p
NOW=1790978400  # 2026-10-02 22:00 UTC
P={"job_id":"SYNTHETIC-NO-RESERVATION","kernel":"CONTROL","cells":1024,
 "bytes_per_cell":1024,"host_fixed_bytes":64,"host_temporary_bytes":4096,"host_margin_bytes":4096,
 "device_fixed_bytes":128,"device_temporary_bytes":4096,"device_margin_bytes":4096,
 "pilot":True,"timeout_s":120,"issued_utc_s":NOW-1,"deadline_utc_s":NOW+180}
S={"job_id":P["job_id"],"sampled_utc_s":NOW,"ram_available_bytes":8*p.GIB,
 "device_used_bytes":p.GIB,"device_total_bytes":24*p.GIB,"temperature_millic":80000,
 "elapsed_s":0,"gpuq_job_id":P["job_id"],"claude_job_id":P["job_id"],
 "process_scan_job_id":P["job_id"],**{k:True for k in p.BOOL_KEYS}}
DATA={"synthetic_only":True,"controls":[]}
def evaluate(a,b,model=p.MODEL):return p.evaluate(a,b,now_utc_s=NOW,model=model)
class Tests(unittest.TestCase):
 def record(self,name,a,b,reason):
  out=evaluate(a,b);self.assertEqual(out["status"],"STOP");self.assertIn(reason,out["reasons"])
  self.assertFalse(out["GPU_job_admission"]);DATA["controls"].append({"name":name,"expected_reason":reason,"plan":a,"snapshot":b,"result":out})
 def test_baseline_does_not_authorize(self):
  out=evaluate(P,S);self.assertEqual(out["status"],"CONDITIONAL_POLICY_FIT")
  self.assertEqual(out["budget"]["cell_bytes"],1048576)
  for k in ("GPU_job_admission","GPU_executed","telemetry_authenticated","reservation_authenticated","guard_implemented","near_limit_headroom_proved"):
   self.assertIs(out[k],False)
  DATA.update(plan=P,snapshot=S,result=out)
 def test_limits_and_bindings(self):
  cases=[("cells",0,"unknown_or_zero_cells"),("bytes_per_cell",1023,"cell_budget_below_1024"),
   ("kernel","MLP32768","forbidden_MLP32768"),("timeout_s",121,"child_timeout_policy"),
   ("timeout_s",0,"child_timeout_policy"),("issued_utc_s",p.HISTORICAL_DEADLINE,"new_job_deadline_required"),
   ("issued_utc_s",NOW+1,"new_job_deadline_required"),("deadline_utc_s",NOW,"new_job_deadline_required"),
   ("deadline_utc_s",NOW+179,"deadline_shutdown_margin")]
  for k in ("host_temporary_bytes","host_margin_bytes","device_temporary_bytes","device_margin_bytes"):
   cases.append((k,0,"explicit_positive_temporaries_and_margins_required"))
  for k,v,reason in cases:
   a=copy.deepcopy(P);a[k]=v;self.record("plan:"+k+":"+str(v),a,copy.deepcopy(S),reason)
  cases=[("sampled_utc_s",NOW-6,"telemetry_stale_or_future"),("sampled_utc_s",NOW+1,"telemetry_stale_or_future"),
         ("elapsed_s",120,"job_timeout"),("temperature_millic",80001,"temperature_80C_cap"),
         ("ram_available_bytes",4*p.GIB,"ram_floor_after_budget"),("device_used_bytes",18*p.GIB,"device_18GiB_cap"),
         ("device_total_bytes",p.GIB,"physical_device_memory")]
  for k in ("job_id","gpuq_job_id","claude_job_id","process_scan_job_id"):cases.append((k,"foreign","job_binding_"+k))
  for k in sorted(p.BOOL_KEYS):cases.append((k,False,"missing_"+k))
  for k,v,reason in cases:
   b=copy.deepcopy(S);b[k]=v;self.record("snapshot:"+k+":"+str(v),copy.deepcopy(P),b,reason)
  a=copy.deepcopy(P);a.update(pilot=False,timeout_s=601,deadline_utc_s=NOW+700)
  self.record("nonpilot601",a,copy.deepcopy(S),"child_timeout_policy")
 def test_closed_typed_INPUT(self):
  count=0
  for side,fixture in (("plan",P),("snapshot",S)):
   for key in fixture:
    a,b=copy.deepcopy(P),copy.deepcopy(S);del (a if side=="plan" else b)[key]
    self.assertEqual(evaluate(a,b)["reasons"],["invalid_or_missing_INPUT"]);count+=1
  for key in ("cells","bytes_per_cell","timeout_s","deadline_utc_s"):
   for v in (None,True,1.0,float("nan"),float("inf"),-1,2**63,"1024"):
    a=copy.deepcopy(P);a[key]=v
    self.assertIsNone(evaluate(a,S)["budget"]);count+=1
  for v in (None,False,"legacy"):
   out=evaluate(P,S,v);self.assertEqual(out["reasons"],["invalid_or_missing_INPUT"]);count+=1
  for side in ("plan","snapshot"):
   a,b=copy.deepcopy(P),copy.deepcopy(S);(a if side=="plan" else b)["extra"]=True
   self.assertEqual(evaluate(a,b)["reasons"],["invalid_or_missing_INPUT"]);count+=1
  DATA["typed_missing_closed_rejections"]=count
 def test_boundary_and_monitor_budget_not_dropped(self):
  a,b=copy.deepcopy(P),copy.deepcopy(S);base=evaluate(a,b)["budget"]
  b["ram_available_bytes"]=p.RAM_FLOOR+base["host_additional_peak_bytes"]
  b["device_used_bytes"]=p.VRAM_CAP-base["device_additional_peak_bytes"]
  out=evaluate(a,b);self.assertEqual(out["status"],"CONDITIONAL_POLICY_FIT")
  DATA["boundary"]={"plan":a,"snapshot":copy.deepcopy(b),"result":out}
  b["elapsed_s"]=1;b["ram_available_bytes"]-=1
  self.record("monitor_budget_retained_one_byte_ram",a,b,"ram_floor_after_budget")
  a,b=copy.deepcopy(P),copy.deepcopy(S);a.update(pilot=False,timeout_s=600,deadline_utc_s=NOW+660)
  out=evaluate(a,b);self.assertEqual(out["status"],"CONDITIONAL_POLICY_FIT")
  DATA["nonpilot600"]={"plan":a,"snapshot":b,"result":out}
if __name__=="__main__":
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"data":DATA},sort_keys=True))
 raise SystemExit(0 if result.wasSuccessful() else 1)
