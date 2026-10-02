"""Exact reduced axial ROOT scene queries + float64 cast gate. CPU only, no native proof."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib, json, math
import history_lineage_cpu_v2 as geom
import primitive_tie_guard_v1 as tie
import branch_primitive_state_CPU_v1 as state
MODEL="precision-axial-scene-candidates-CPU-v1"
class CandidateStop(ValueError): pass
def closed(v,keys):
 if type(v) is not dict or set(v)!=set(keys):raise CandidateStop("closed_INPUT_required")
def rational(v):
 if type(v) is not list or len(v)!=2 or any(type(x) is not int for x in v):
  raise CandidateStop("exact_rational_pair_required")
 n,d=v
 if d<=0 or abs(n).bit_length()>2048 or d.bit_length()>2048:raise CandidateStop("rational_storage_bound")
 x=F(n,d)
 if abs(x)>10**6:raise CandidateStop("coordinate_bound")
 return x
def vector(v):
 if type(v) is not list or len(v)!=3:raise CandidateStop("exact_vector_required")
 return tuple(rational(x) for x in v)
def pair(x):return [x.numerator,x.denominator]
def bound_scene(scene):
 closed(scene,("schema","units","triangles","sources"))
 if scene["schema"]!=MODEL or scene["units"]!="BU":raise CandidateStop("explicit_reduced_model_units")
 if type(scene["triangles"]) is not list or not 1<=len(scene["triangles"])<=64:raise CandidateStop("triangle_bound")
 if type(scene["sources"]) is not list or not 1<=len(scene["sources"])<=5:raise CandidateStop("source_bound")
 triangles=[];manifest=[]
 for i,row in enumerate(scene["triangles"]):
  closed(row,("primitive_id","object_id","vertices_BU"))
  if type(row["primitive_id"]) is not int or row["primitive_id"]!=i:raise CandidateStop("explicit_ordered_global_ID")
  if type(row["object_id"]) is not str or not 1<=len(row["object_id"])<=128:raise CandidateStop("object_label")
  if type(row["vertices_BU"]) is not list or len(row["vertices_BU"])!=3:raise CandidateStop("triangle_vertices")
  tri=tuple(vector(v) for v in row["vertices_BU"])
  normal=geom.cross(geom.sub(tri[1],tri[0]),geom.sub(tri[2],tri[0]))
  if sum(x!=0 for x in normal)!=1:raise CandidateStop("nondegenerate_axial_plane_only")
  triangles.append(tri);manifest.append({"primitive_id":i,"object_id":row["object_id"]})
 sources=[];seen=set()
 for row in scene["sources"]:
  closed(row,("id","position_BU","direction"))
  sid=row["id"]
  if type(sid) is not str or not 1<=len(sid)<=64 or sid in seen:raise CandidateStop("unique_SOURCE_labels")
  origin,direction=vector(row["position_BU"]),vector(row["direction"])
  if sum(x!=0 for x in direction)!=1 or geom.dot(direction,direction)!=1:
   raise CandidateStop("exact_axis_unit_direction_only")
  seen.add(sid);sources.append((sid,origin,direction))
 # Includes explicit triangle/SOURCE list order and literal rational representation.
 body=json.dumps(scene,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
 return hashlib.sha256(body).hexdigest(),manifest,triangles,sources
def prepare(scene,*,model):
 out={"model":MODEL,"status":"STOP","reason":None,"scene_sha256":None,"manifest":None,"sources":[],
      "root_queries_computed":0,"branch_queries":0,"branch_results":[],
      "origin":"EXACT_RATIONAL_REDUCED_CPU_SCENE_NOT_BPY_GPU",
      "GPU_executed":False,"native_promotion_allowed":False,"physical_scene_authenticated":False,
      "native_hit_coverage_certified":False,"length_reference_phase_bound_certified":False,
      "full_field_certified":False,"full_costs":"UNMEASURED_NOT_ZERO"}
 try:
  if type(model) is not str or model!=MODEL:raise CandidateStop("explicit_model_required")
  scene=deepcopy(scene)
  sha,manifest,triangles,sources=bound_scene(scene)
  out["scene_sha256"]=sha;out["manifest"]=manifest
  for sid,o,d in sources:
   rows=[];visited=[]
   out["root_queries_computed"]+=1
   for pid,tri in enumerate(triangles):
    value=geom.intersection(o,d,tri) # Pure rational function ONLY; no nearest(), pack/readback or history replay.
    if value is None:
     visited.append({"primitive_id":pid,"classification":"miss"});continue
    t,n=value
    if t<0:
     visited.append({"primitive_id":pid,"classification":"behind_source"});continue
    if t==0:raise CandidateStop("source_zero_contact_no_departure")
    visited.append({"primitive_id":pid,"classification":"positive_hit"})
    normal=[float(x!=0) for x in n] # Canonical positive axis unit, no normal FP normalization.
    cast=float(t)
    rows.append({"primitive_id":pid,"distance_rational_BU":pair(t),"distance_float64_BU":cast,
                 "normal_rational":[pair(x) for x in n],"normal_canonical":normal})
   record={"source_id":sid,"origin_rational":[pair(x) for x in o],
           "direction_rational":[pair(x) for x in d],"visited":visited,"hits":rows}
   out["sources"].append(record)
   if not rows:raise CandidateStop("root_miss_NOT_certified")
   if any(not math.isfinite(x["distance_float64_BU"]) or x["distance_float64_BU"]<=0 for x in rows):
    raise CandidateStop("float64_positive_finite_required")
   exact_min=min(F(*x["distance_rational_BU"]) for x in rows)
   float_min=min(x["distance_float64_BU"] for x in rows)
   exact_ids=sorted(x["primitive_id"] for x in rows if F(*x["distance_rational_BU"])==exact_min)
   float_ids=sorted(x["primitive_id"] for x in rows if x["distance_float64_BU"]==float_min)
   exact_band=sorted(x["primitive_id"] for x in rows if F(*x["distance_rational_BU"])-exact_min<=F(tie.TIE_BU))
   float_band=sorted(x["primitive_id"] for x in rows if abs(x["distance_float64_BU"]-float_min)<=tie.TIE_BU)
   record.update(exact_minimum_ids=exact_ids,float64_minimum_ids=float_ids,
                 exact_band_ids=exact_band,float64_band_ids=float_band)
   if exact_ids!=float_ids:raise CandidateStop("float64_minimum_set_changed")
   if exact_band!=float_band:raise CandidateStop("float64_tie_band_changed")
   record["candidates"]=[{"primitive_id":x["primitive_id"],"distance_BU":x["distance_float64_BU"],
                          "normal":x["normal_canonical"]} for x in rows]
   policy=tie.resolve_candidates(snapshot_sha256=sha,manifest=manifest,candidates=record["candidates"],previous=None)
   record["root_tie_policy"]=policy
   if policy["action"]!="continue":raise CandidateStop("root_tie_policy:"+policy["reason"])
  out["status"]="CPU_AXIAL_ROOT_CANDIDATES_ONLY"
 except (ValueError,TypeError,KeyError,OverflowError) as exc:
  out["reason"]=str(exc) if isinstance(exc,CandidateStop) else "exact_geometry:"+type(exc).__name__
 return out
def query_sources(scene,*,model):
 out=prepare(scene,model=model)
 if out["status"]=="STOP":return out
 # All SOURCE geometry/cast/tie gates have passed before ANY branch query.
 for row in out["sources"]:
  branch=state.Branch(snapshot_sha256=out["scene_sha256"],manifest=out["manifest"],
                      source_id=row["source_id"],branch_id=row["source_id"]+"/root",model=state.MODEL)
  result=branch.query(snapshot_sha256=out["scene_sha256"],source_id=row["source_id"],
                      branch_id=row["source_id"]+"/root",candidates=row["candidates"])
  out["branch_queries"]+=1;out["branch_results"].append(result)
  if result["state"]!="HIT_PENDING_DEPARTURE":
   out["status"]="STOP";out["reason"]="branch_state_policy_STOP";break
 return out
