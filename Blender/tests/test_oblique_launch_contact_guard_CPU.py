"""Exact independent Cramer oracle and explicit synthetic launch controls."""
from pathlib import Path
from fractions import Fraction as Q
import sys,json,copy,collections
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_launch_contact_guard_CPU_v1 as m
def f(x):return Q(*x)
def p(x):return [x.numerator,x.denominator]
def vv(v):return tuple(map(f,v))
def minus(a,b):return tuple(x-y for x,y in zip(a,b))
def det(cols):
 a,b,c=cols
 return a[0]*(b[1]*c[2]-b[2]*c[1])-b[0]*(a[1]*c[2]-a[2]*c[1])+c[0]*(a[1]*b[2]-a[2]*b[1])
def cramer(origin,end,tri):
 a,b,c=map(vv,tri["vertices_BU"]);o=vv(origin);d=minus(vv(end),o)
 cols=[minus(b,a),minus(c,a),tuple(-x for x in d)]
 D=det(cols)
 if D==0:return None
 rhs=minus(o,a);sol=[]
 for j in range(3):
  replaced=list(cols);replaced[j]=rhs;sol.append(det(replaced)/D)
 u,w,t=sol
 if not(0<=t<=1 and u>=0 and w>=0 and u+w<=1):return dict(hit=False,t=p(t))
 return dict(hit=True,t=p(t),barycentric=list(map(p,(1-u-w,u,w))),
     point_BU=[p(o[j]+t*d[j])for j in range(3)])
def verify(origin,end,tri,result):
 ref=cramer(origin,end,tri)
 if ref is None:
  assert not result["exclusion_allowed"];return
 if not ref["hit"]:
  assert result["status"]=="CPU_DECLARED_NO_CONTACT_ONLY"and not result["exclusion_allowed"];return
 assert result["contact"]==dict(primitive_id=tri["primitive_id"],t=ref["t"],
         point_BU=ref["point_BU"],barycentric=ref["barycentric"])
 if result["exclusion_allowed"]:
  assert ref["t"]==[0,1]and result["action"]=="EXCLUDE_THIS_ZERO_POINT_ONLY"
 else:assert result["action"]=="KEEP_CONTACT_FOR_DOWNSTREAM"
 assert all(result[k]is False for k in ("object_wide_skip","SOURCE_shared_token","scene_authenticated",
      "phase_certified","physical_field_certified","GPU_used","Bpy_used","full_visibility_certified","native_hit_coverage_certified"))
 assert result["phase_error_bound"]is None and result["epsilon_BU"]==result["t_min"]==[0,1]

def suite():
 e,pins=m.retained();records=[];upstream=[];census=collections.Counter()
 for k,x in e.items():
  if x["result"]["status"]!="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY":
   pid=x["scene"]["triangles"][0]["primitive_id"];q=m.selector(k,"S0",pid,e);r=m.evaluate(k,q,e)
   assert r["status"]=="STOP_UPSTREAM"and r["geometry_evaluations"]==0
   upstream.append(dict(id=k,result=r));continue
  for source in ("S0","S1"):
   token,s,prev=m.launch(x,source)
   for tri in x["scene"]["triangles"]:
    pid=tri["primitive_id"];q=m.selector(k,source,pid,e);r=m.evaluate(k,q,e)
    verify(s["from_BU"],s["to_BU"],tri,r);census[r["status"]]+=1
    if pid==token["previous_primitive_id"]:assert r["exclusion_allowed"]is True
    else:assert r["exclusion_allowed"]is False
    records.append(dict(id=k,source_id=source,primitive_id=pid,request=q,result=r))
 assert len(upstream)==38 and len(records)==28
 controls=[];replays=[]
 for k in ("oblique","tiny_gap_2m60"):
  x=e[k]
  for source in ("S0","S1"):
   token,s,prev=m.launch(x,source);o=s["from_BU"];end=s["to_BU"]
   cases=[]
   # Distinct primitive touching zero on the SAME object must be kept.
   adjacent=copy.deepcopy(prev);adjacent["primitive_id"]=200
   cases.append(("adjacent_same_object_at_zero",o,end,adjacent,"KEEP_CONTACT_FOR_DOWNSTREAM"))
   # Explicit NEW SYNTHETIC translation along x; t=2^-60, no original scene changes.
   near=copy.deepcopy(prev);near["primitive_id"]=201
   tx=f(o[0])+Q(1,2**60)*(f(end[0])-f(o[0]))
   for v in near["vertices_BU"]:v[0]=p(tx)
   cases.append(("near_same_object_t2m60",o,end,near,"KEEP_CONTACT_FOR_DOWNSTREAM"))
   # Even a supplied previous primitive id does not authorize positive t exclusion.
   forged_face=copy.deepcopy(near);forged_face["primitive_id"]=prev["primitive_id"]
   cases.append(("positive_t_with_previous_id",o,end,forged_face,"KEEP_CONTACT_FOR_DOWNSTREAM"))
   copend=copy.deepcopy(o);copend[1]=p(f(o[1])+Q(1,4))
   cases.append(("coplanar_departure_no_point_exemption",o,copend,prev,"DO_NOT_EXCLUDE"))
   for name,origin,finish,tri,action in cases:
    r=m.guard(origin,finish,tri,token,token)
    assert r["action"]==action and not r["exclusion_allowed"]
    if name.startswith("coplanar"):assert r["status"]=="STOP_COPLANAR"
    else:
     verify(origin,finish,tri,r)
     assert f(r["contact"]["t"])==(Q(0)if name.startswith("adjacent")else Q(1,2**60))
    controls.append(dict(case=k,source_id=source,label="NEW_CPU_SYNTHETIC_CONTROL_NOT_RETAINED_SCENE",
        name=name,origin_BU=origin,end_BU=finish,triangle=tri,result=r,
        displacement_x_BU=None if name.startswith("coplanar")else p(f(tri["vertices_BU"][0][0])-f(o[0]))))
   other="S1"if source=="S0"else"S0";foreign=m.launch(x,other)[0]
   q=m.selector(k,source,prev["primitive_id"],e);r=m.evaluate(k,q,e,foreign)
   assert r["status"]=="STOP_INPUT"and r["geometry_evaluations"]==0
   replays.append(dict(case=k,receiving_SOURCE=source,credential_SOURCE=other,result=r))
 invalid=[]
 x=e["oblique"];token,s,prev=m.launch(x,"S0");q=m.selector("oblique","S0",prev["primitive_id"],e)
 for key,value in (("source_id","SOURCE0"),("segment",True),("primitive_id",True),("scene_sha256","0"*64),
      ("policy","OBJECT_SKIP"),("epsilon_BU",[1,1000]),("t_min",[1,2**60]),("object_wide_skip",True)):
  bad=dict(q);bad[key]=value;r=m.evaluate("oblique",bad,e)
  assert r["status"]=="STOP_INPUT"and r["geometry_evaluations"]==0
  invalid.append(dict(field=key,result=r))
 tokens=[]
 for key,val in (("source_id","S1"),("segment",True),("previous_primitive_id",True),
    ("scene_sha256","0"*64),("query_sha256","0"*64),("path_sha256","0"*64),
    ("launch_point_BU",[[0,1]]*3),("previous_barycentric",[[1,1],[0,1],[0,1]]),
    ("launch_point_BU",[[True,1],[1,1],[1,4]])):
  forged=copy.deepcopy(token);forged[key]=val;r=m.guard(s["from_BU"],s["to_BU"],prev,forged,token)
  assert r["status"]=="STOP_INPUT"and r["geometry_evaluations"]==0
  tokens.append(dict(field=key,result=r))
 shifted=copy.deepcopy(s["from_BU"]);shifted[0]=p(f(shifted[0])+Q(1,2**100))
 shifted_r=m.guard(shifted,s["to_BU"],prev,token,token)
 assert shifted_r["status"]=="STOP_INPUT"and shifted_r["reason"]=="exact_launch_origin"
 shifted_record=dict(label="NEW_SYNTHETIC_SHIFT_NOT_ORIGINAL_MODIFICATION",origin_BU=shifted,result=shifted_r)
 api=[m.run("oblique",{**q,"source_id":"SOURCE0"})]
 reader=m.retained
 try:
  def missing():raise OSError("SIMULATED_MISSING_DEPENDENCY")
  def drift():raise ValueError("SIMULATED_SHA_DRIFT")
  for replacement in (missing,drift):
   m.retained=replacement;api.append(m.run("oblique",q))
 finally:m.retained=reader
 assert api[0]["status"]=="STOP_INPUT"and all(z["geometry_evaluations"]==0 for z in api)
 assert all(z["status"]=="STOP_DEPENDENCY"for z in api[1:])
 summary=dict(retained_records=44,upstream_stops_preserved=38,positive_scene_packets=6,guard_queries=28,
     census=dict(census),new_synthetic_contact_controls=16,SOURCE_replay_rejections=4,
     invalid_selectors=8,invalid_tokens=9,shifted_origin_rejections=1,API_negative=3,
     dependency_pins=len(pins),new_native_RN=0,new_root_calls=0,old_numeric_replays=0,
     full_costs="UNKNOWN_NOT_ZERO",runtime_seconds_are_QA_not_benchmark=True,
     GPU_used=False,phase_certified=False,native_hit_coverage_certified=False)
 return dict(status="PASS",evidence=dict(records=records,upstream=upstream,synthetic_controls=controls,
     SOURCE_replays=replays,invalid_selectors=invalid,invalid_tokens=tokens,shifted_origin=shifted_record,API_negative=api),
     summary=summary)

if __name__=="__main__":print(json.dumps(suite(),sort_keys=True,separators=(",",":"),allow_nan=False))
