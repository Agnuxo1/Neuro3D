"""CPU rational backend tests; original captures are contrast only, never hit inputs."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_geometry32_trace_rational_CPU_v1 as m
def scope(r):
 assert all(r[k]is False for k in ("SOURCE_merged","native_IEEE32_ALU_certified","GPU_used","Bpy_used","RT_used",
  "physical_field_certified","scene_authenticated","phase_certified","computed_hilo_collapse_allowed",
  "material_phase_certified","full_path_visibility_certified"))
 assert r["phase_error_bound"]is None and r["old_numeric_replays"]==0 and r["full_costs"]=="UNKNOWN_NOT_ZERO"
def plane(x,pid,oid="oblique_common_fixture"):
 return dict(primitive_id=pid,object_id=oid,vertices_BU=[[[x.numerator,x.denominator],[0,1],[0,1]],[[x.numerator,x.denominator],[3,1],[0,1]],[[x.numerator,x.denominator],[0,1],[3,1]]])
def suite():
 e,a,packs,pins=m.retained();positive=[];up=[]
 for k,x in e.items():
  r=m.evaluate(k,m.selector(k,e),e,a,packs);scope(r)
  if k not in a:
   assert r["status"]=="STOP_UPSTREAM"and r["plane_tests"]==r["received_integer_word_decodes"]==0
   up.append(dict(id=k,result=r));continue
  assert r["status"]=="CPU_RATIONAL_DECLARED_TWO_SEGMENT_TRACE_ONLY",(k,r)
  assert len(r["source_results"])==2 and r["plane_tests"]==4*len(x["scene"]["triangles"])
  expected=x["parent_result"]["diagnostics"]
  for s,v in zip(r["source_results"],expected):
   assert s["source_id"]==v["source_id"] and s["primary_hit"]["point_BU"]==v["hit_points_BU"][0]
   assert s["primary_hit"]["parameter"]==v["hit_parameters"][0]
   assert s["reflected_direction"]==v["reflected_direction"]
   assert s["segment_endpoints_BU"][1:]==v["hit_points_BU"]
   assert s["segment_squared_BU2"]==[z["squared_BU2"]for z in v["segments"]]
   assert [z["primitive_id"]for z in s["primary_rows"]]==[t["primitive_id"]for t in x["scene"]["triangles"]]
   assert [z["primitive_id"]for z in s["secondary_rows"]]==[t["primitive_id"]for t in x["scene"]["triangles"]]
   assert [z["action"]for z in s["terminal_decisions"]].count("EXCLUDE_EXACT_PREVIOUS_POINT")==1
  positive.append(dict(id=k,result=r))
 assert len(positive)==6 and len(up)==38
 assert sum(z["result"]["plane_tests"]for z in positive)==56
 assert sum(z["result"]["received_integer_word_decodes"]for z in positive)==228
 controls=[]
 for name,case in (("primary_blocker","oblique"),("duplicate_root_tie","oblique"),("duplicate_detector_tie","oblique"),
   ("coplanar","oblique"),("degenerate","oblique"),("thin_gap_2m61","tiny_gap_2m60"),
   ("off_reflected_ray","oblique"),("zero_direction","oblique"),("source_start_contact","oblique"),
   ("lambda_reference_not_phase","oblique")):
  x=copy.deepcopy(e[case])
  if name=="primary_blocker":x["scene"]["triangles"].append(plane(F(1,2),20))
  elif name=="duplicate_root_tie":
   t=copy.deepcopy(x["scene"]["triangles"][1]);t["primitive_id"]=20;x["scene"]["triangles"].append(t)
  elif name=="duplicate_detector_tie":
   t=copy.deepcopy(x["scene"]["triangles"][0]);t["primitive_id"]=202;x["scene"]["triangles"].append(t)
  elif name=="coplanar":x["scene"]["triangles"].append(dict(primitive_id=20,object_id="oblique_common_fixture",vertices_BU=[[[0,1],[0,1],[1,4]],[[3,1],[0,1],[1,4]],[[0,1],[3,1],[1,4]]]))
  elif name=="degenerate":x["scene"]["triangles"].append(dict(primitive_id=20,object_id="oblique_common_fixture",vertices_BU=[[[0,1],[0,1],[0,1]]]*3))
  elif name=="thin_gap_2m61":x["scene"]["triangles"].append(plane(F(1,2**61),20))
  elif name=="off_reflected_ray":x["request"]["detector_point_BU"][1]=[3,2]
  elif name=="zero_direction":x["scene"]["sources"][0]["direction"]=[[0,1]]*3
  elif name=="source_start_contact":x["scene"]["sources"][0]["position_BU"]=[[1,1],[1,1],[1,4]]
  elif name=="lambda_reference_not_phase":x["request"].update(lambda_BU=[1,4],reference_BU=[4,1])
  x["request"]["original_scene_sha256"]=m.digest(x["scene"])
  producer=m.ingress.emit(x);assert producer["geometry_input_bytes_verified"],(name,producer)
  r=m.trace(producer["packet"],x);scope(r)
  if name=="lambda_reference_not_phase":assert r["declared_two_segment_trace_certified"]is True and r["phase_certified"]is False
  else:assert r["declared_two_segment_trace_certified"]is False,(name,r)
  controls.append(dict(name=name,label="NEW_SYNTHETIC_DECLARED_INPUT32_NOT_ORIGINAL_OR_PROMOTED",record=x,producer=producer,result=r))
 # Stage-only guards from freshly computed rational intersections, not saved hit outputs.
 stage=[]
 root=(F(1,2**60),F(1,2**60),F(1,4));target=(F(0),F(1,2**59),F(1,4));direction=m.sub(target,root)
 ts=[]
 for pid,xv in ((0,F(0)),(1,F(1,2**60)),(20,F(1,2**61))):
  t=plane(xv,pid);t["vertices"]=[tuple(F(*p)for p in v)for v in t.pop("vertices_BU")];ts.append(t)
 counter={"plane_tests":0};fresh=[m.intersect(root,direction,t,counter)for t in ts]
 prev=next(z for z in fresh if z["primitive_id"]==1)
 for name,rows,prev_id,prev_p,prev_bary,expected in (
  ("thin_absolute_2m61",fresh,1,root,prev["barycentric"],"STOP_BLOCKED"),
  ("exact_clear",fresh[:2],1,root,prev["barycentric"],"CPU_DECLARED_TERMINAL_CLEAR_ONLY"),
  ("wrong_previous_id",fresh[:2],9,root,prev["barycentric"],"STOP_BLOCKED"),
  ("wrong_previous_point",fresh[:2],1,(root[0],root[1]+F(1,2**61),root[2]),prev["barycentric"],"STOP_BLOCKED"),
  ("wrong_previous_barycentric",fresh[:2],1,root,[[0,1],[0,1],[1,1]],"STOP_BLOCKED")):
  status,decisions=m.terminal(rows,prev_id,prev_p,prev_bary,0,target);assert status==expected,(name,status)
  stage.append(dict(name=name,label="STAGE_ONLY_NEW_RATIONAL_INTERSECTIONS_NOT_FULL_BACKEND_ADMISSION",fresh_rows=rows,status=status,decisions=decisions))
 assert F(*fresh[2]["parameter"])==F(1,2)and F(*fresh[2]["point_BU"][0])==F(1,2**61)
 parent=json.loads((m.ROOT/m.PARENT).read_bytes());old=m.ingress.capture(parent["test_run"])["evidence"]
 packets_negative=[]
 for n in old["negative_packets"]:
  if "packet"not in n:continue
  r=m.trace(n["packet"],e["oblique"]);scope(r)
  assert not r["declared_two_segment_trace_certified"]and r["plane_tests"]==r["received_integer_word_decodes"]==0
  packets_negative.append(dict(name=n["name"],label="RETAINED_PACKET_MUTATION_DATA_ONLY_NO_PRODUCER_REPLAY",result=r))
 selectors=[]
 q=m.selector("oblique",e)
 for key,val in (("source_ids",["S1","S0"]),("case",True),("epsilon",[1,2**60]),("model","IEEE32"),
   ("parent_ingress_receipt_sha256","0"*64),("record_sha256",["nested"])):
  qq=copy.deepcopy(q);qq[key]=val;r=m.evaluate("oblique",qq,e,a,packs);scope(r);assert r["status"]=="STOP_INPUT"and r["plane_tests"]==0
  selectors.append(dict(field=key,result=r))
 api=[];reader=m.retained
 try:
  def missing():raise OSError("SIMULATED_MISSING_DEPENDENCY")
  def drift():raise ValueError("SIMULATED_SHA_DRIFT")
  for fn in (missing,drift):
   m.retained=fn;r=m.run("oblique",q);scope(r);assert r["status"]=="STOP_DEPENDENCY";api.append(r)
 finally:m.retained=reader
 summary=dict(positive_original=6,upstream_stops=38,original_new_plane_tests=56,original_word_decodes=228,
  original_ingress_parser_decodes=228,synthetic_controls=len(controls),synthetic_rejected=9,synthetic_trace_only_no_phase=1,
  stage_controls=len(stage),stage_new_plane_tests=counter["plane_tests"],negative_packets=len(packets_negative),
  selectors=len(selectors),API_simulated=len(api),dependency_pins=len(pins),old_numeric_replays=0,GPU_used=False,
  native_IEEE32_ALU_certified=False,phase_certified=False,full_costs="UNKNOWN_NOT_ZERO",QA_seconds_not_benchmark=True)
 return dict(status="PASS",summary=summary,evidence=dict(positive=positive,upstream=up,synthetic=controls,
  stage=stage,stage_new_plane_tests=counter["plane_tests"],negative_packets=packets_negative,selectors=selectors,API_negative=api))
if __name__=="__main__":print(json.dumps(suite(),sort_keys=True,separators=(",",":"),allow_nan=False))
