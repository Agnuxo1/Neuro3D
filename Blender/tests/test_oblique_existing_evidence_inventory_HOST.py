"""Inventory checks only. Synthetic text/JSON mentions never become admission."""
from pathlib import Path
import sys,json,copy,base64,zlib,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_existing_evidence_inventory_HOST_v1 as m
def safe(r):
 assert all(r[k]is False for k in ("GPU_launch_allowed","GPU_used","Bpy_used","RT_used","physical_phase_admitted","reference_truth_verified","gauge_provenance_verified","material_phase_verified","native_IEEE_RN_graph_certified","exact_contact_allowed","SOURCE_merged","repo_wide_absence_claim","live_gpu_telemetry_checked"))
 assert r["phase_error_bound"]is None and r["new_numeric_operations"]==r["old_numeric_replays"]==r["foreign_writer_executions"]==0
def main():
 r=m.run();safe(r);assert r["inventory_complete"]is True and len(r["artifacts"])==14
 assert r["historical_rt006"]["reported_status"]=="COMPLETE_SUCCESS"and r["historical_rt006"]["attachments_hash_verified"]==5
 assert r["historical_rt006"]["override_reuse_allowed"]is False and r["historical_rt006"]["fresh_job_admitted"]is False
 a=r["anchor_cases"];ev={"original":r,"synthetic":[],"capacities":[],"dependency_API":[]}
 exact=dict(scene_sha256=a[0]["scene_sha256"],query_sha256=a[0]["query_sha256"],input_buffer_sha256=a[0]["input_buffer_sha256"],source_ids=["S0","S1"],status="COMPLETE_SUCCESS",phase_certified=True)
 stages=[
  ("literal_exact_success",exact,1,"SCENE_QUERY_INPUT_LITERAL_MATCH"),
  ("without_input",{k:v for k,v in exact.items()if k!="input_buffer_sha256"},1,"SCENE_QUERY_LITERAL_MATCH_NO_INPUT_JOIN"),
  ("other_query",dict(exact,query_sha256="0"*64),0,None),
  ("SOURCE_reversed",dict(exact,source_ids=["S1","S0"]),1,"SCENE_QUERY_INPUT_LITERAL_MATCH"),
  ("nested_pointer",{"a/b":[{"~":exact}]},1,"SCENE_QUERY_INPUT_LITERAL_MATCH"),
  ("string_not_object",json.dumps(exact),0,None)]
 for label,doc,n,kind in stages:
  report=m.scan(doc,a);assert report["native_or_physical_admission"]is False and len(report["co_located_join_mentions"])==n
  if n:assert report["co_located_join_mentions"][0]["kind"]==kind and report["co_located_join_mentions"][0]["native_or_physical_proof"]is False
  ev["synthetic"].append(dict(id=label,label="SYNTHETIC_LOCATOR_ONLY_NOT_BACKEND_OR_SCENE_ADMISSION",document=doc,report=report))
 raw=b'{"status":"PASS"}'
 w=dict(rc=0,timed_out=False,stdout_bytes=len(raw),stdout_sha256=hashlib.sha256(raw).hexdigest(),stdout_zlib_base64=base64.b64encode(zlib.compress(raw)).decode())
 assert m.capture(w)=={"status":"PASS"}
 for label,edit in (("hash",lambda x:x.update(stdout_sha256="0"*64)),("bool_rc",lambda x:x.update(rc=False)),("oversize",lambda x:x.update(stdout_bytes=m.MAX_CAPTURE+1)),("trailing_zlib",lambda x:x.update(stdout_zlib_base64=base64.b64encode(zlib.compress(raw)+b"extra").decode()))):
  x=copy.deepcopy(w);edit(x)
  try:m.capture(x)
  except(ValueError,KeyError,TypeError,zlib.error)as ex:reason=str(ex)
  else:raise AssertionError("capture STOP "+label)
  ev["capacities"].append(dict(id=label,status="STOP_INPUT",reason=reason))
 for label,raw in (("duplicate_key",b'{"x":1,"x":2}'),("NaN",b'{"x":NaN}'),("exponent_overflow",b'{"x":1e309}')):
  try:m.parse(raw)
  except(ValueError)as ex:reason=str(ex)
  else:raise AssertionError("JSON STOP "+label)
  ev["capacities"].append(dict(id=label,status="STOP_INPUT",reason=reason))
 x={};deep=x
 for i in range(66):deep["x"]={};deep=deep["x"]
 try:m.scan(x,a)
 except(ValueError)as ex:reason=str(ex)
 else:raise AssertionError("depth STOP")
 ev["capacities"].append(dict(id="depth",status="STOP_INPUT",reason=reason))
 targets=copy.deepcopy(a);targets[0]["scene_sha256"]=True
 try:m.scan({},targets)
 except(ValueError)as ex:reason=str(ex)
 else:raise AssertionError("target STOP")
 ev["capacities"].append(dict(id="bool_target",status="STOP_INPUT",reason=reason))
 original_read=m.read
 for label in ("missing_anchor","drift_selected"):
  def fake(path):
   if label=="missing_anchor"and path==m.PARENT:raise OSError("SIMULATED_missing_anchor")
   if label=="drift_selected"and path==m.SPECS[0]["path"]:return b"{}"
   return original_read(path)
  m.read=fake
  try:v=m.run()
  finally:m.read=original_read
  safe(v);assert v["inventory_complete"]is False and v["status"]=="STOP_DEPENDENCY"
  ev["dependency_API"].append(dict(id=label,label="SIMULATED_READ_FAILURE_OR_DRIFT_NO_FILE_CHANGED",result=v))
 summary=dict(files=14,anchor_cases=6,anchor_SOURCE_inputs=12,documents_scanned=r["documents_scanned"],sealed_capture_count=r["sealed_test_captures_decoded_as_DATA"],nodes=r["all_selected_nodes_scanned"],scene_query_joins=r["co_located_join_mention_count"],exact_input_joins=r["exact_input_join_mention_count"],synthetic_locators=6,capacity_stops=9,dependency_API_stops=2,new_numeric_operations=0,full_costs="UNKNOWN_NOT_ZERO")
 print(json.dumps(dict(status="PASS",summary=summary,evidence=ev),sort_keys=True,separators=(",",":"),allow_nan=False))
if __name__=="__main__":main()
