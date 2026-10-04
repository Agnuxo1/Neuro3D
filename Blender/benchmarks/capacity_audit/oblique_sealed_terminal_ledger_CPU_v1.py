"""Opt-in consumer of complete sealed launch-guard ledgers. No intersection replay.
Only two declared CPU SOURCE terminal segments; not full paths/native/physical phase.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,zlib,base64
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-sealed-terminal-ledger-CPU-v1"
POLICY="ALL_ORIGINAL_PRIMITIVES_EXACT_ZERO_POINT_ONLY_UNIQUE_DETECTOR_AT_ONE"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-LAUNCH-CONTACT-GUARD-CPU-001-CODEX.json"
PSHA="9f8a54dc298e7765ff22d8485de2be9ff213948b83674e99b74ede53ca9d7d88"
VIS="coordinacion/respuestas/PRECISION-OBLIQUE-SEGMENT-VISIBILITY-CPU-001-CODEX.json"
VSHA="caeb7f11a25812dee86041a10b74f68adf7330d2a40724258bf71c15f25f19f5"
EXCLUDE="CPU_DECLARED_EXACT_LAUNCH_EXCLUSION_ONLY"
KEEP="CPU_DECLARED_KEEP_CONTACT_ONLY"
MISS="CPU_DECLARED_NO_CONTACT_ONLY"
TOKEN_KEYS={"version","scene_sha256","query_sha256","path_sha256","source_id","segment",
 "previous_primitive_id","launch_point_BU","previous_barycentric","scope"}

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def rat(p):
 need(type(p)is list and len(p)==2 and all(type(v)is int for v in p)and p[1]>0,"typed_rational")
 need(max(abs(v).bit_length()for v in p)<=128,"bounded_rational")
 v=F(*p);need([v.numerator,v.denominator]==p,"canonical_rational");return v
def vec(v):
 need(type(v)is list and len(v)==3,"vector3");a=tuple(map(rat,v))
 need(all(abs(x)<=10**6 for x in a),"coordinate_bound");return a
def bary(v):
 need(type(v)is list and len(v)==3,"barycentric3");b=list(map(rat,v))
 need(min(b)>=0 and sum(b)==1,"barycentric_simplex");return b
def capture(c):
 need(c["rc"]==0 and c["timed_out"]is False,"successful_capture")
 z=zlib.decompressobj();b=z.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),4194305)
 need(len(b)<=4194304 and z.eof and not z.unconsumed_tail and not z.unused_data,"bounded_capture")
 need(sha(b)==c["stdout_sha256"]and len(b)==c["stdout_bytes"],"capture_seal");return json.loads(b)
def retained():
 b=(ROOT/PARENT).read_bytes();need(sha(b)==PSHA and len(b)==121289,"parent_seal")
 p=json.loads(b);pins=dict(p["code_doc_sha256"]);need(len(pins)==335,"closed_parent_pins")
 for path,h in pins.items():need(sha((ROOT/path).read_bytes())==h,"dependency:"+path)
 need(capture(p["independent_pre"])["status"]=="PASS","parent_oracle")
 c=capture(p["test_run"]);need(c["status"]=="PASS","parent_suite")
 need(pins[VIS]==VSHA,"visibility_pin")
 v=json.loads((ROOT/VIS).read_bytes());d=capture(v["test_run"])
 need(d["status"]=="PASS","retained_visibility_capture")
 e={x["id"]:x for x in d["runs"]};need(len(e)==len(d["runs"])==44,"closed44")
 rows=c["evidence"]["records"];need(len(rows)==28,"closed_guard28")
 pins[PARENT]=PSHA;return e,rows,c["evidence"]["synthetic_controls"],pins

def selector(k,e):
 x=e[k];return dict(model=MODEL,policy=POLICY,case=k,source_ids=["S0","S1"],segment=1,
  scene_sha256=digest(x["scene"]),query_sha256=digest(x["request"]),record_sha256=digest(x),
  parent_receipt_sha256=PSHA,visibility_receipt_sha256=VSHA)
def baseline():
 return dict(model=MODEL,status="STOP_INPUT",reason=None,source_decisions=[],contacts_kept=[],
  declared_terminal_clear=False,full_path_visibility_certified=False,scene_authenticated=False,
  native_hit_coverage_certified=False,phase_certified=False,physical_field_certified=False,
  phase_error_bound=None,GPU_used=False,Bpy_used=False,epsilon_BU=[0,1],t_min=[0,1],
  object_wide_skip=False,SOURCE_merged=False,new_intersections=0,new_guard_calls=0,
  new_root_calls=0,new_native_RN=0,old_numeric_replays=0,
  ledger_rows_audited=0,full_costs="UNKNOWN_NOT_ZERO")

def packet(x,source,rows):
 """Build internally from pinned original scene, query, path and captured guard rows."""
 scene=x["scene"];q=x["request"];r=x["parent_result"]
 need(x["result"]["status"]=="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY","upstream_visibility")
 need(r["status"]=="CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY","upstream_length")
 need(q["source_ids"]==[s["id"]for s in scene["sources"]]==["S0","S1"],"ALL_SOURCE_order")
 need([p["source_id"]for p in r["paths"]]==["S0","S1"],"ALL_SOURCE_paths")
 need(digest(scene)==q["original_scene_sha256"]==r["original_scene_sha256"],"original_scene")
 need(digest(q)==r["literal_request_sha256"],"literal_query")
 need(source in ("S0","S1"),"SOURCE_identity")
 p=r["paths"][("S0","S1").index(source)];s=p["segments"]
 need(len(s)==2 and s[0]["to_BU"]==s[1]["from_BU"]==p["hit_points_BU"][0],"launch_continuity")
 need(s[0]["from_BU"]==scene["sources"][("S0","S1").index(source)]["position_BU"],"SOURCE_origin")
 need(s[1]["to_BU"]==q["detector_point_BU"]==p["hit_points_BU"][1],"detector_endpoint")
 need(p["primitive_ids"]==[q["root_primitive_id"],q["detector_primitive_id"]],"original_primitive_path")
 triangles=scene["triangles"];ids=[t["primitive_id"]for t in triangles]
 need(all(type(i)is int and 0<=i<2**31 for i in ids)and len(set(ids))==len(ids),"unique_typed_primitives")
 token=dict(version=1,scene_sha256=digest(scene),query_sha256=digest(q),path_sha256=digest(p),
  source_id=source,segment=1,previous_primitive_id=q["root_primitive_id"],
  launch_point_BU=s[1]["from_BU"],previous_barycentric=p["barycentric"][0],
  scope="DECLARED_SYNTHETIC_LAUNCH_NOT_PHYSICAL")
 out=dict(scope="ORIGINAL_DECLARED_CPU_CAPTURE_ONLY",case=x["id"],source_id=source,segment=1,
  scene_sha256=digest(scene),query_sha256=digest(q),path_sha256=digest(p),record_sha256=digest(x),token=token,
  from_BU=s[1]["from_BU"],to_BU=s[1]["to_BU"],target_primitive_id=q["detector_primitive_id"],
  triangles=triangles,rows=rows)
 return out

def consume(plan,expected_sha256):
 """Internal closed-ledger decision; expected seal comes from pinned capture, not caller."""
 out=baseline()
 try:
  need(type(plan)is dict and digest(plan)==expected_sha256,"closed_packet_seal")
  need(set(plan)=={"scope","case","source_id","segment","scene_sha256","query_sha256","path_sha256",
       "record_sha256","token","from_BU","to_BU","target_primitive_id","triangles","rows"},"closed_packet")
  need(plan["scope"]in ("ORIGINAL_DECLARED_CPU_CAPTURE_ONLY","NEW_SYNTHETIC_DECISION_CONTROL_ONLY"),"scope")
  need(plan["source_id"]in ("S0","S1")and type(plan["segment"])is int and plan["segment"]==1,"SOURCE_segment")
  tok=plan["token"];need(type(tok)is dict and set(tok)==TOKEN_KEYS,"closed_token")
  need(type(tok["version"])is int and tok["version"]==1 and type(tok["segment"])is int and tok["segment"]==1,"typed_token")
  need(type(tok["previous_primitive_id"])is int and 0<=tok["previous_primitive_id"]<2**31,"token_primitive")
  need(tok["scope"]=="DECLARED_SYNTHETIC_LAUNCH_NOT_PHYSICAL","token_scope")
  need(tok["source_id"]==plan["source_id"]and all(tok[k]==plan[k]for k in ("scene_sha256","query_sha256","path_sha256")),"token_binding")
  need(all(type(plan[k])is str and len(plan[k])==64 and all(c in "0123456789abcdef"for c in plan[k])
       for k in ("scene_sha256","query_sha256","path_sha256","record_sha256")),"typed_hashes")
  o=vec(plan["from_BU"]);end=vec(plan["to_BU"]);need(o!=end,"positive_segment")
  need(vec(tok["launch_point_BU"])==o,"launch_origin");pb=bary(tok["previous_barycentric"])
  triangles=plan["triangles"];need(type(triangles)is list and 1<=len(triangles)<=64,"bounded_triangles")
  ids=[t["primitive_id"]for t in triangles]
  need(all(type(i)is int and 0<=i<2**31 for i in ids)and len(ids)==len(set(ids)),"unique_primitive_ids")
  target=plan["target_primitive_id"]
  need(type(target)is int and target in ids and tok["previous_primitive_id"]in ids and target!=tok["previous_primitive_id"],"target_previous")
  verts={}
  for tri in triangles:
   need(set(tri)=={"primitive_id","object_id","vertices_BU"}and type(tri["object_id"])is str,"closed_triangle")
   need(type(tri["vertices_BU"])is list and len(tri["vertices_BU"])==3,"triangle3")
   verts[tri["primitive_id"]]=list(map(vec,tri["vertices_BU"]))
  prevv=verts[tok["previous_primitive_id"]]
  need(tuple(sum(pb[j]*prevv[j][i]for j in range(3))for i in range(3))==o,"previous_point")
  rows=plan["rows"];need(type(rows)is list and len(rows)==len(ids),"ALL_primitive_row_count")
  seen=set();kept=[];excluded=[];unresolved=[]
  for row in rows:
   need(type(row)is dict and set(row)=={"id","source_id","primitive_id","request","result"},"closed_row")
   pid=row["primitive_id"];need(type(pid)is int and pid in ids and pid not in seen,"ALL_unique_primitive_rows");seen.add(pid)
   need(row["id"]==plan["case"]and row["source_id"]==plan["source_id"],"row_case_SOURCE")
   res=row["result"]
   # Captured original rows carry immutable request, token and scene/query binding.
   if plan["scope"]=="ORIGINAL_DECLARED_CPU_CAPTURE_ONLY":
    rq=row["request"]
    need(rq["case"]==plan["case"]and rq["source_id"]==plan["source_id"]and type(rq["segment"])is int and rq["segment"]==1
         and type(rq["primitive_id"])is int and rq["primitive_id"]==pid,"request_identity")
    need(all(rq[k]==plan[k]==res[k]for k in ("scene_sha256","query_sha256")),"row_hash_binding")
    need(res["case"]==plan["case"]and res["source_id"]==plan["source_id"],"result_identity")
    # Serialized identity is typed: Python True==1 is not credential identity.
    need(digest(res["launch_credential"])==digest(tok)==res["launch_credential_sha256"],"result_token")
    expected_request=dict(model="oblique-launch-contact-guard-CPU-v1",
     policy="EXCLUDE_ONLY_CERTIFIED_PREVIOUS_PRIMITIVE_POINT_AT_EXACT_ZERO_KEEP_ALL_OTHER_CONTACT",
     case=plan["case"],source_id=plan["source_id"],segment=1,primitive_id=pid,
     scene_sha256=plan["scene_sha256"],query_sha256=plan["query_sha256"],
     record_sha256=plan["record_sha256"],
     parent_receipt_sha256="b799a6a17bb59561bf7a90e78189b6db821c82dcbd1119b784c9efa0a55f8e03",
     visibility_receipt_sha256=VSHA)
    need(digest(rq)==digest(expected_request),"closed_guard_selector")
   need(res["model"]=="oblique-launch-contact-guard-CPU-v1","guard_model")
   need(all(res[k]is False for k in ("object_wide_skip","SOURCE_shared_token","scene_authenticated",
          "full_visibility_certified","native_hit_coverage_certified","phase_certified",
          "physical_field_certified","GPU_used","Bpy_used")),"scope_not_promoted")
   need(res["phase_error_bound"]is None and res["epsilon_BU"]==res["t_min"]==[0,1],"no_bias_phase")
   rat(res["epsilon_BU"]);rat(res["t_min"])
   out["ledger_rows_audited"]+=1
   st=res["status"]
   if st not in (EXCLUDE,KEEP,MISS):
    need(res["exclusion_allowed"]is False,"unresolved_not_excluded");unresolved.append(dict(primitive_id=pid,status=st));continue
   if st==MISS:
    need(res["action"]=="NO_CONTACT"and res["contact"]is None and res["exclusion_allowed"]is False,"no_contact");continue
   c=res["contact"];need(set(c)=={"primitive_id","t","point_BU","barycentric"},"closed_contact")
   need(type(c["primitive_id"])is int and c["primitive_id"]==pid,"contact_primitive")
   t=rat(c["t"]);need(0<=t<=1,"closed_segment_t");h=vec(c["point_BU"]);b=bary(c["barycentric"])
   need(h==tuple(o[i]+t*(end[i]-o[i])for i in range(3)),"point_on_segment")
   need(h==tuple(sum(b[j]*verts[pid][j][i]for j in range(3))for i in range(3)),"point_on_primitive")
   if st==EXCLUDE:
    need(res["action"]=="EXCLUDE_THIS_ZERO_POINT_ONLY"and res["exclusion_allowed"]is True,"point_exclusion_action")
    need(pid==tok["previous_primitive_id"]and t==0 and h==o and b==pb,"exact_previous_zero_only")
    excluded.append(pid)
   else:
    need(res["action"]=="KEEP_CONTACT_FOR_DOWNSTREAM"and res["exclusion_allowed"]is False,"keep_contact")
    kept.append(c)
  need(seen==set(ids),"ALL_primitive_coverage")
  out["contacts_kept"]=kept
  if unresolved:out.update(status="STOP_UNRESOLVED_CONTACT",reason="coplanar_or_other_guard_STOP",unresolved=unresolved);return out
  need(excluded==[tok["previous_primitive_id"]],"one_exact_launch_exclusion")
  hits=sorted(kept,key=lambda c:(rat(c["t"]),c["primitive_id"]))
  terminal=[c for c in hits if c["primitive_id"]==target and rat(c["t"])==1 and vec(c["point_BU"])==end]
  if len(terminal)!=1:out.update(status="STOP_TARGET_MISSING",reason="unique_exact_target_endpoint_required");return out
  blockers=[c for c in hits if c["primitive_id"]!=target or rat(c["t"])!=1]
  if blockers:
   out.update(status="STOP_BLOCKED_TERMINAL",reason="retained_contact_at_or_before_target",blockers=blockers,nearest_blocker=blockers[0]);return out
  out.update(status="CPU_DECLARED_TERMINAL_CLEAR_ONLY",reason="ALL_original_primitives_unique_target_at_one",
    declared_terminal_clear=True,target_contact=terminal[0],excluded_previous_primitive_id=excluded[0])
 except(ValueError,KeyError,TypeError,IndexError,ZeroDivisionError)as ex:
  out.update(status="STOP_INPUT",reason=str(ex),declared_terminal_clear=False)
 return out

def evaluate(k,q,e,rows):
 out=baseline()
 try:
  need(k in e and type(q)is dict and q==selector(k,e)and set(q)==set(selector(k,e)),"closed_selector")
  need(type(q["segment"])is int and q["segment"]==1,"typed_selector_segment")
  x=e[k]
  if x["result"]["status"]!="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY":
   out.update(status="STOP_UPSTREAM",reason=x["result"].get("reason"),retained_status=x["result"]["status"]);return out
  decisions=[]
  for source in ("S0","S1"):
   candidates=[v for v in rows if v["id"]==k and v["source_id"]==source]
   plan=packet(x,source,candidates);r=consume(plan,digest(plan))
   decisions.append(dict(source_id=source,packet_sha256=digest(plan),plan=plan,result=r))
  out.update(source_decisions=decisions,ledger_rows_audited=sum(d["result"]["ledger_rows_audited"]for d in decisions))
  if all(d["result"]["declared_terminal_clear"]is True for d in decisions):
   out.update(status="CPU_DECLARED_BOTH_SOURCE_TERMINAL_CLEAR_ONLY",declared_terminal_clear=True,reason="separate_S0_S1_closed_ledgers")
  else:out.update(status="STOP_SOURCE_TERMINAL",reason="at_least_one_SOURCE_not_clear")
 except(ValueError,KeyError,TypeError,IndexError,ZeroDivisionError)as ex:out["reason"]=str(ex)
 return out

def run(k,q):
 try:e,rows,controls,pins=retained();return evaluate(k,q,e,rows)
 except(OSError,ValueError,KeyError,TypeError)as ex:
  out=baseline();out.update(status="STOP_DEPENDENCY",reason=str(ex));return out
