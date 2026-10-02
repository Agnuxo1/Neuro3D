"""Own endpoint-clock controls; CPU synthetic declarations, no hardware resource collection."""
import base64, copy, hashlib, json, sys, unittest, zlib
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Blender/benchmarks/capacity_audit"))
import gpu_job_collection_clock_CPU_v1 as a
import gpu_job_monitor_lifecycle_CPU_v1 as m
import gpu_job_collector_isolation_CPU_v1 as c
parent = "coordinacion/respuestas/GPU-JOB-MONITOR-LIFECYCLE-CPU-001-CODEX.json"
raw = (ROOT / parent).read_bytes()
assert hashlib.sha256(raw).hexdigest() == "faef200a51db844c1a9c66c9d040777d156b2e2faa066603a19eb13a4aa57164"
r = json.loads(raw)
t = r["test_run"]
out = zlib.decompress(base64.b64decode(t["stdout_zlib_base64"], validate=True))
assert hashlib.sha256(out).hexdigest() == t["stdout_sha256"]
fixture = json.loads(out)["data"]
P, S = fixture["plan"], fixture["snapshot"]
NOW, NS = 1790978400, 10**12
DATA = {"controls": [], "actual_CPU_children": [], "no_live_resources": True}
def token(utc=NOW, ns=NS):
    return {"utc_s": utc, "monotonic_ns": ns}
def retained(name, result, origin="MOCK_CLOCK_SYNTHETIC_SNAPSHOT"):
    DATA["controls"].append({"name": name, "clock_origin": origin, "result": result})
class Tests(unittest.TestCase):
    def test_endpoint_elapsed_counterexample(self):
        snapshot = copy.deepcopy(S)
        baseline = m.Monitor(P, now_utc_s=NOW, monotonic_ns=NS, model=m.MODEL)
        old = baseline.sample(lambda: snapshot, now_utc_s=NOW, monotonic_ns=NS+900000000)
        self.assertEqual(old["state"], "CONTINUE_SYNTHETIC_CONTROL")
        with patch.object(a, "stamp", side_effect=[token(), token(ns=NS+900000000), token(NOW+1,NS+10**9)]):
            mon = a.EndpointMonitor(P, model=a.MODEL)
            new = mon.sample(lambda: snapshot)
        self.assertEqual(new["reasons"], ["elapsed_monotonic_mismatch"])
        self.assertEqual(new["collection_ns"], 100000000)
        self.assertEqual(snapshot, S)  # Never overwrite declared elapsed.
        calls = new["collector_calls"]
        with patch.object(a, "stamp", side_effect=AssertionError("terminal read")):
            retry = mon.sample(lambda: self.fail("terminal collector"))
        self.assertEqual(new, retry)
        self.assertEqual(calls, 1)
        DATA["counterexample"] = {"preonly_frozen": old, "endpoint": new, "retry": retry,
                                 "snapshot_unchanged": snapshot == S}
        retained("elapsed_crosses_second", new)
    def test_postclock_faults_and_policy_uses_endpoint(self):
        cases = [
            ("gap", token(ns=NS+10**9+1), "postcollection_gap"),
            ("mono_rollback", token(ns=NS-1), "postcollection_monotonic_rollback"),
            ("wall_rollback", token(NOW-1), "postcollection_wall_rollback"),
            ("stale", token(NOW+6), "resource_policy:telemetry_stale_or_future"),
            ("expired", token(NOW+301), "resource_policy:new_job_deadline_required")]
        for name, end, reason in cases:
            with patch.object(a, "stamp", side_effect=[token(), token(), end]):
                mon=a.EndpointMonitor(P, model=a.MODEL)
                result=mon.sample(lambda: copy.deepcopy(S))
            self.assertEqual(result["state"], "STOP")
            self.assertIn(reason, result["reasons"])
            retained(name, result)
    def test_preclock_and_invalid_model_no_collect(self):
        for name, before, reason in [
            ("pre_gap",token(ns=NS+10**9+1),"precollection_gap"),
            ("pre_mono",token(ns=NS-1),"precollection_monotonic_rollback"),
            ("pre_wall",token(NOW-1),"precollection_wall_rollback")]:
            with patch.object(a,"stamp",side_effect=[token(),before]):
                mon=a.EndpointMonitor(P,model=a.MODEL)
                result=mon.sample(lambda:self.fail("must not collect"))
            self.assertEqual(result["collector_calls"],0)
            self.assertEqual(result["reasons"],[reason])
            retained(name,result)
        with patch.object(a,"stamp",side_effect=AssertionError("must not read")):
            mon=a.EndpointMonitor(P,model="GPU")
            result=mon.sample(lambda:self.fail("invalid constructor"))
        self.assertEqual(result["state"],"STOP");self.assertEqual(result["collector_calls"],0)
        retained("invalid_model",result)
    def test_clock_read_errors_and_interrupt_latch(self):
        with patch.object(a,"stamp",side_effect=[token(),OSError("not retained")]):
            mon=a.EndpointMonitor(P,model=a.MODEL)
            pre=mon.sample(lambda:self.fail("clock failed"))
        self.assertEqual(pre["reasons"],["precollection_error:OSError"])
        retained("pre_clock_error",pre)
        with patch.object(a,"stamp",side_effect=[token(),token(),OSError("not retained")]):
            mon=a.EndpointMonitor(P,model=a.MODEL)
            post=mon.sample(lambda:copy.deepcopy(S))
        self.assertEqual(post["reasons"],["postcollection_error:OSError"])
        retained("post_clock_error",post)
        with patch.object(a,"stamp",side_effect=[token(),token()]):
            mon=a.EndpointMonitor(P,model=a.MODEL)
            def interrupt():raise KeyboardInterrupt()
            with self.assertRaises(KeyboardInterrupt):mon.sample(interrupt)
        result=mon.view();self.assertEqual(result["reasons"],["collector_error:KeyboardInterrupt"])
        self.assertEqual(mon.sample(lambda:self.fail("retry")),result)
        retained("interrupt",result)
    def test_mock_valid_endpoint(self):
        with patch.object(a,"stamp",side_effect=[token(),token(ns=NS+100000000),token(ns=NS+500000000)]):
            mon=a.EndpointMonitor(P,model=a.MODEL)
            result=mon.sample(lambda:copy.deepcopy(S))
        self.assertEqual(result["state"],"CONTINUE_SYNTHETIC_CONTROL")
        self.assertEqual(result["collection_ns"],400000000)
        self.assertFalse(result["GPU_job_admission"])
        retained("valid_endpoint",result)
    def test_real_OS_clocks_synthetic_snapshot(self):
        current=a.stamp()  # New plan only; frozen P remains untouched.
        plan=copy.deepcopy(P);plan["job_id"]="CPU-ENDPOINT-SYNTHETIC"
        plan["issued_utc_s"]=current["utc_s"];plan["deadline_utc_s"]=current["utc_s"]+300
        snapshot=copy.deepcopy(S)
        for key in ("job_id","gpuq_job_id","claude_job_id","process_scan_job_id"):snapshot[key]=plan["job_id"]
        snapshot["sampled_utc_s"]=current["utc_s"]
        mon=a.EndpointMonitor(plan,model=a.MODEL)
        result=mon.sample(lambda:snapshot)
        self.assertEqual(result["state"],"CONTINUE_SYNTHETIC_CONTROL")
        self.assertGreaterEqual(result["collection_ns"],0)
        self.assertEqual(snapshot["elapsed_s"],0)
        retained("real_OS_clock",result,"OS_CLOCK_SYNTHETIC_SNAPSHOT")
        DATA["new_synthetic_plan"]=plan
    def test_real_bounded_own_collector_timeout(self):
        mon=a.EndpointMonitor(P,model=a.MODEL)
        def blocked():
            try:return c.collect("block",timeout_s=0.25,model=c.MODEL)["packet"]["snapshot"]
            except c.CollectorFailure as exc:
                DATA["actual_CPU_children"].append(exc.report);raise
        result=mon.sample(blocked)
        self.assertEqual(result["reasons"],["collector_error:CollectorFailure"])
        self.assertEqual(mon.sample(lambda:self.fail("retry")),result)
        self.assertTrue(DATA["actual_CPU_children"][0]["cleanup_confirmed"])
        retained("real_own_child_timeout",result,"OS_CLOCK_SYNTHETIC_WORKER")
if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"status":"PASS" if result.wasSuccessful() else "FAIL","tests":result.testsRun,"data":DATA},sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
