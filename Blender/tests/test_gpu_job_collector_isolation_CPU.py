"""Real OWN fixed CPU child controls; no GPU/Blender/live telemetry/foreign writer."""
import base64,copy,hashlib,json,sys,unittest,zlib
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import gpu_job_collector_isolation_CPU_v1 as c
import gpu_job_monitor_lifecycle_CPU_v1 as m
parent="coordinacion/respuestas/GPU-JOB-MONITOR-LIFECYCLE-CPU-001-CODEX.json"
raw=(ROOT/parent).read_bytes();assert hashlib.sha256(raw).hexdigest()=="faef200a51db844c1a9c66c9d040777d156b2e2faa066603a19eb13a4aa57164"
r=json.loads(raw)
for p,h in r["code_doc_sha256"].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
t=r["test_run"];data_raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True));assert len(data_raw)==t["stdout_bytes"] and hashlib.sha256(data_raw).hexdigest()==t["stdout_sha256"]
fixture=json.loads(data_raw)["data"];P=fixture["plan"];S=fixture["snapshot"];NOW=1790978400;NS=10**12
DATA={"synthetic_only":True,"actual_CPU_children":[],"prelaunch_rejections":[]}
class Tests(unittest.TestCase):
 def test_valid_fixed_child(self):
  out=c.collect("valid",timeout_s=1,model=c.MODEL)
  self.assertEqual(out["status"],"SYNTHETIC_PACKET");self.assertEqual(out["packet"]["snapshot"],S)
  self.assertTrue(out["cleanup_confirmed"]);self.assertFalse(out["own_process_terminated"])
  self.assertFalse(out["live_telemetry_collected"]);self.assertFalse(out["GPU_job_admission"])
  DATA["actual_CPU_children"].append(out)
 def test_faults_cleanup_only_own_child(self):
  for profile,status in (("block","TIMEOUT"),("invalid_json","PACKET_INVALID"),("oversized","OUTPUT_CAP"),("exit_error","CHILD_EXIT_ERROR"),("bad_packet","PACKET_INVALID")):
   with self.assertRaises(c.CollectorFailure) as caught:c.collect(profile,timeout_s=0.25 if profile=="block" else 1,model=c.MODEL)
   out=caught.exception.report;self.assertEqual(out["status"],status);self.assertTrue(out["cleanup_confirmed"])
   self.assertFalse(out["foreign_processes_touched"])
   self.assertEqual(out["own_process_terminated"],profile=="block")
   DATA["actual_CPU_children"].append(out)
 def test_invalid_INPUT_and_identity_before_launch(self):
  cases=[("model",v) for v in (None,False,"GPU")]+[("profile",v) for v in (None,False,"foreign","valid;foreign")]+[("timeout",v) for v in (None,False,0,-1,1.1,float("nan"),float("inf"),"1")]
  for field,value in cases:
   args={"profile":"valid","timeout_s":1,"model":c.MODEL}
   args[{"timeout":"timeout_s"}.get(field,field)]=value
   with patch.object(c,"_launch",wraps=c._launch) as launch:
    with self.assertRaises(c.CollectorFailure) as caught:c.collect(**args)
    self.assertEqual(launch.call_count,0);self.assertEqual(caught.exception.report["status"],"INPUT_INVALID")
    DATA["prelaunch_rejections"].append({"field":field,"launch_calls":0,"status":"INPUT_INVALID"})
  with patch.object(c,"_read_worker",return_value=b"WRONG_CONTROL_SOURCE"),patch.object(c,"_launch",wraps=c._launch) as launch:
   with self.assertRaises(c.CollectorFailure) as caught:c.collect("valid",timeout_s=1,model=c.MODEL)
   self.assertEqual(launch.call_count,0);self.assertEqual(caught.exception.report["status"],"PIN_MISMATCH")
   DATA["prelaunch_rejections"].append({"field":"worker_identity","launch_calls":0,"status":"PIN_MISMATCH"})
 def test_monitor_integration_timeout_no_retry_spawn(self):
  mon=m.Monitor(P,now_utc_s=NOW,monotonic_ns=NS,model=m.MODEL)
  reports=[]
  def healthy():
   out=c.collect("valid",timeout_s=1,model=c.MODEL);reports.append(out);return out["packet"]["snapshot"]
  first=mon.sample(healthy,now_utc_s=NOW,monotonic_ns=NS)
  self.assertEqual(first["state"],"CONTINUE_SYNTHETIC_CONTROL")
  def blocked():
   try:return c.collect("block",timeout_s=0.25,model=c.MODEL)["packet"]["snapshot"]
   except c.CollectorFailure as exc:reports.append(exc.report);raise
  stopped=mon.sample(blocked,now_utc_s=NOW,monotonic_ns=NS)
  self.assertEqual(stopped["state"],"STOP");self.assertEqual(stopped["reasons"],["collector_error:CollectorFailure"])
  with patch.object(c,"_launch",wraps=c._launch) as launch:
   retry=mon.sample(healthy,now_utc_s=NOW,monotonic_ns=NS)
   self.assertEqual(launch.call_count,0);self.assertEqual(retry,stopped)
  DATA["actual_CPU_children"].extend(reports)
  DATA["integration"]={"first":first,"stopped":stopped,"retry":retry,"retry_launch_calls":0}
if __name__=="__main__":
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"data":DATA},sort_keys=True))
 raise SystemExit(0 if result.wasSuccessful() else 1)
