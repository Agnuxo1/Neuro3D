"""Synthetic clock/collector lifecycle tests; zero live telemetry or child processes."""
import base64,copy,hashlib,json,sys,unittest,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import gpu_job_monitor_lifecycle_CPU_v1 as m
PARENT="coordinacion/respuestas/GPU-JOB-RESOURCE-POLICY-HOST-001-CODEX.json"
PARENT_SHA="cca0a2387e1e7f9fc9155cff9226c42efdfe5af6fa6938d17bcf3fef21e1f62d"
parent_raw=(ROOT/PARENT).read_bytes();assert hashlib.sha256(parent_raw).hexdigest()==PARENT_SHA
r=json.loads(parent_raw)
for path,h in r["code_doc_sha256"].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
t=r["test_run"];raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
assert len(raw)==t["stdout_bytes"] and hashlib.sha256(raw).hexdigest()==t["stdout_sha256"]
retained=json.loads(raw)["data"];NOW=1790978400;BASE_NS=10**12
P=copy.deepcopy(retained["plan"]);P.update(job_id="CPU-LIFECYCLE-SYNTHETIC",deadline_utc_s=NOW+300)
S=copy.deepcopy(retained["snapshot"])
for key in ("job_id","gpuq_job_id","claude_job_id","process_scan_job_id"):S[key]=P["job_id"]
DATA={"synthetic_only":True,"plan":P,"snapshot":S,"negative_controls":[]}
def monitor(plan=None,model=m.MODEL):
 return m.Monitor(P if plan is None else plan,now_utc_s=NOW,monotonic_ns=BASE_NS,model=model)
def sample(mon,snapshot=None,utc=NOW,ns=BASE_NS):
 return mon.sample(lambda:copy.deepcopy(S if snapshot is None else snapshot),now_utc_s=utc,monotonic_ns=ns)
class Tests(unittest.TestCase):
 def negative(self,name,fn,expected):
  mon=monitor();initial=sample(mon);self.assertEqual(initial["state"],"CONTINUE_SYNTHETIC_CONTROL")
  out=fn(mon);self.assertEqual(out["state"],"STOP");self.assertIn(expected,out["reasons"])
  calls=[]
  recovered=mon.sample(lambda:calls.append(1) or copy.deepcopy(S),now_utc_s=NOW,monotonic_ns=BASE_NS)
  self.assertEqual(recovered,out);self.assertEqual(calls,[])
  DATA["negative_controls"].append({"name":name,"initial":initial,"stopped":out,"after_healthy_retry":recovered,"retry_collector_calls":0})
 def test_budget_plan_freeze_and_defensive_views(self):
  plan=copy.deepcopy(P);mon=monitor(plan);first=sample(mon)
  plan.update(cells=1,deadline_utc_s=NOW+10000)
  leaked=mon.view();leaked["policy_result"]["budget"]["host_additional_peak_bytes"]=0
  b=copy.deepcopy(S);b.update(elapsed_s=1,sampled_utc_s=NOW+1)
  second=sample(mon,b,utc=NOW+1,ns=BASE_NS+10**9)
  self.assertEqual(first["plan_sha256"],second["plan_sha256"]);self.assertEqual(second["samples_evaluated"],2)
  for key in ("cell_bytes","host_additional_peak_bytes","device_additional_peak_bytes"):
   self.assertEqual(first["policy_result"]["budget"][key],second["policy_result"]["budget"][key])
  self.assertFalse(second["GPU_job_admission"]);DATA["progression"]=[first,second]
 def test_faults_are_terminal_before_retry_collector(self):
  def bad_snapshot(key,value):
   b=copy.deepcopy(S);b[key]=value;return lambda mon:sample(mon,b)
  def error(mon):
   def fail():raise OSError("SENSITIVE_RAW_TEXT_MUST_NOT_LEAK")
   return mon.sample(fail,now_utc_s=NOW,monotonic_ns=BASE_NS)
  def timeout(mon):
   b=copy.deepcopy(S);b["elapsed_s"]=1
   # Caller falsely declares elapsed1 while monotonic elapsed0; never silently rewritten.
   return sample(mon,b)
  def tamper(mon):
   mon._plan["deadline_utc_s"]+=1000
   return sample(mon)
  cases=[
   ("collector_error",error,"collector_error:OSError"),
   ("collector_None",lambda mon:mon.sample(lambda:None,now_utc_s=NOW,monotonic_ns=BASE_NS),"policy_error:ValueError"),
   ("collector_not_callable",lambda mon:mon.sample(None,now_utc_s=NOW,monotonic_ns=BASE_NS),"collector_not_callable"),
   ("elapsed_false",timeout,"elapsed_monotonic_mismatch"),
   ("monotonic_rollback",lambda mon:sample(mon,ns=BASE_NS-1),"monotonic_clock_rollback"),
   ("wall_rollback",lambda mon:sample(mon,utc=NOW-1),"wall_clock_rollback"),
   ("sample_gap",lambda mon:sample(mon,ns=BASE_NS+10**9+1),"monitor_sample_gap"),
   ("clock_bool",lambda mon:sample(mon,ns=True),"invalid_clock_INPUT"),
   ("plan_tamper",tamper,"plan_integrity_changed"),
   ("stale",bad_snapshot("sampled_utc_s",NOW-6),"resource_policy:telemetry_stale_or_future"),
   ("foreign_job",bad_snapshot("gpuq_job_id","foreign"),"resource_policy:job_binding_gpuq_job_id"),
   ("lost_exclusive",bad_snapshot("exclusive_gpu",False),"resource_policy:missing_exclusive_gpu"),
   ("hot",bad_snapshot("temperature_millic",80001),"resource_policy:temperature_80C_cap"),
   ("ram_budget_retained",bad_snapshot("ram_available_bytes",4*2**30),"resource_policy:ram_floor_after_budget"),
   ("vram_budget_retained",bad_snapshot("device_used_bytes",18*2**30),"resource_policy:device_18GiB_cap")]
  for name,fn,expected in cases:self.negative(name,fn,expected)
  self.assertNotIn("SENSITIVE_RAW_TEXT",json.dumps(DATA))
 def test_elapsed_timeout_without_waiting(self):
  rows=[]
  for timeout,pilot in ((120,True),(600,False)):
   plan=copy.deepcopy(P);plan.update(timeout_s=timeout,pilot=pilot,deadline_utc_s=NOW+2*timeout+300)
   mon=monitor(plan);first=sample(mon)
   for elapsed in range(1,timeout+1):
    b=copy.deepcopy(S);b.update(elapsed_s=elapsed,sampled_utc_s=NOW+elapsed)
    out=sample(mon,b,utc=NOW+elapsed,ns=BASE_NS+elapsed*10**9)
    self.assertEqual(out["state"],"STOP" if elapsed==timeout else "CONTINUE_SYNTHETIC_CONTROL")
   self.assertIn("resource_policy:job_timeout",out["reasons"]);calls=[]
   after=mon.sample(lambda:calls.append(1) or S,now_utc_s=NOW+timeout,monotonic_ns=BASE_NS+timeout*10**9)
   self.assertEqual(calls,[]);self.assertEqual(after,out)
   rows.append({"timeout_s":timeout,"pilot":pilot,"plan":plan,"first":first,"last":out,"after":after,"retry_collector_calls":0})
  DATA["timeouts"]=rows
 def test_initial_invalid_and_interrupt_latch(self):
  records=[]
  for model in (None,False,"GPU"):
   mon=monitor(model=model);calls=[]
   out=mon.sample(lambda:calls.append(1) or S,now_utc_s=NOW,monotonic_ns=BASE_NS)
   self.assertEqual(out["reasons"],["invalid_constructor_INPUT"]);self.assertEqual(calls,[])
   records.append(out)
  mon=monitor()
  def interrupt():raise KeyboardInterrupt()
  with self.assertRaises(KeyboardInterrupt):mon.sample(interrupt,now_utc_s=NOW,monotonic_ns=BASE_NS)
  out=mon.view();self.assertEqual(out["reasons"],["collector_error:KeyboardInterrupt"])
  calls=[];after=mon.sample(lambda:calls.append(1) or S,now_utc_s=NOW,monotonic_ns=BASE_NS)
  self.assertEqual(after,out);self.assertEqual(calls,[])
  DATA["initial_model_rejections"]=records;DATA["interrupt"]={"stopped":out,"after":after,"retry_collector_calls":0}
if __name__=="__main__":
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"data":DATA},sort_keys=True))
 raise SystemExit(0 if result.wasSuccessful() else 1)
