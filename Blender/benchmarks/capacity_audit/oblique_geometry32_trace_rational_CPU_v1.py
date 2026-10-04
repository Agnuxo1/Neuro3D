"""Opt-in exact rational CPU ray/segment backend from original binary32 inputs.
NOT IEEE32 ALU, GPU, RT, physical optics or phase/material certification.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,struct
import oblique_scene_geometry32_ingress_HOST_v1 as ingress
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-geometry32-trace-rational-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"
PSHA="f4814286200766db8494df3f99ff7653d7cf038bd1f51cd34491206a0537016b"
def need(ok,msg):
 if not ok:raise ValueError(msg)
def pair(v):return [v.numerator,v.denominator]
def vec(v):return [pair(x)for x in v]
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def scale(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def digest(x):return ingress.digest(x)
def retained():
 raw=(ROOT/PARENT).read_bytes();need(hashlib.sha256(raw).hexdigest()==PSHA and len(raw)==110790,"parent_seal")
 p=json.loads(raw);pins=dict(p["code_doc_sha256"]);need(len(pins)==343,"pins343")
 for s,h in pins.items():need(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h,"dependency:"+s)
 oracle=ingress.capture(p["independent_final_after_doc_pins"]);need(oracle["status"]=="PASS","parent_oracle")
 suite=ingress.capture(p["test_run"]);need(suite["status"]=="PASS","parent_suite")
 e,a,ip=ingress.retained();packets={v["id"]:v["result"]["packet"]for v in suite["evidence"]["positive"]}
 need(set(packets)==a and len(e)==44,"same_original_selection")
 pins[PARENT]=PSHA;return e,a,packets,pins
def selector(k,e):
 s=ingress.selector(k,e);s.update(model=MODEL,parent_ingress_receipt_sha256=PSHA);return s
def base():
 return dict(model=MODEL,status="STOP_INPUT",reason=None,source_results=[],plane_tests=0,
  received_integer_word_decodes=0,input_manifest_parser_word_decodes=0,
  SOURCE_merged=False,input32_value_exact=False,declared_two_segment_trace_certified=False,
  native_IEEE32_ALU_certified=False,GPU_used=False,Bpy_used=False,RT_used=False,
  physical_field_certified=False,scene_authenticated=False,phase_certified=False,
  phase_error_bound=None,computed_hilo_collapse_allowed=False,material_phase_certified=False,
  full_path_visibility_certified=False,old_numeric_replays=0,
  full_costs="UNKNOWN_NOT_ZERO",precision_model="EXACT_RATIONAL_CPU_FROM_ORIGINAL_BINARY32_WORDS")
def decoded_inputs(packet,x,result):
 validated=ingress.parse(packet,x);result["input_manifest_parser_word_decodes"]=validated["integer_word_decodes"]
 need(validated["geometry_input_bytes_verified"]is True,"input_packet:"+str(validated["reason"]))
 b=bytes.fromhex(packet["buffer_hex"]);meta=packet["manifest"];start=meta["scalar_payload_offset"]
 vals=[]
 for i in range(meta["scalar_count"]):
  vals.append(ingress.decode_word(struct.unpack_from("<I",b,start+4*i)[0]));result["received_integer_word_decodes"]+=1
 idx=0;sources=[]
 for sid in meta["source_ids"]:
  sources.append(dict(id=sid,position=tuple(vals[idx:idx+3]),direction=tuple(vals[idx+3:idx+6])));idx+=6
 tris=[]
 for pid,oid in zip(meta["primitive_ids"],meta["primitive_object_ids"]):
  verts=[tuple(vals[idx+j:idx+j+3])for j in (0,3,6)];idx+=9
  tris.append(dict(primitive_id=pid,object_id=oid,vertices=verts))
 detector=tuple(vals[idx:idx+3]);idx+=3
 lam,ref=vals[idx:idx+2];idx+=2
 need(idx==len(vals)and lam>0,"closed_input_cursor")
 result["input32_value_exact"]=True
 return sources,tris,detector,meta["root_primitive_id"],meta["detector_primitive_id"],lam,ref
def intersect(origin,direction,triangle,counter):
 counter["plane_tests"]+=1
 a,b,c=triangle["vertices"];u=sub(b,a);v=sub(c,a);n=cross(u,v);n2=dot(n,n)
 r=dict(primitive_id=triangle["primitive_id"],object_id=triangle["object_id"],kind="MISS",reason=None)
 if n2==0:r.update(kind="UNRESOLVED",reason="degenerate_triangle");return r
 den=dot(n,direction);height=dot(n,sub(a,origin))
 if den==0:
  r.update(kind="UNRESOLVED"if height==0 else "MISS",reason="coplanar"if height==0 else "parallel");return r
 t=height/den;p=add(origin,scale(direction,t));w=sub(p,a)
 uu=dot(u,u);uv=dot(u,v);vv=dot(v,v);wu=dot(w,u);wv=dot(w,v);gram=uu*vv-uv*uv
 need(gram>0,"positive_Gram")
 beta=(wu*vv-wv*uv)/gram;gamma=(wv*uu-wu*uv)/gram;alpha=1-beta-gamma
 if min(alpha,beta,gamma)<0:r["reason"]="outside_triangle";return r
 r.update(kind="HIT",parameter=pair(t),point_BU=vec(p),barycentric=[pair(alpha),pair(beta),pair(gamma)],normal=vec(n))
 return r
def fraction_vec(p):return tuple(F(*q)for q in p)
def terminal(rows,previous_id,previous_point,previous_bary,detector_id,detector_point):
 """Stage-only decision from freshly computed rows; not a public input/certificate API."""
 if any(r["kind"]=="UNRESOLVED"for r in rows):return "STOP_UNRESOLVED",[]
 targets=[];decisions=[]
 for r in rows:
  action="NO_CONTACT"
  if r["kind"]=="HIT":
   t=F(*r["parameter"]);p=fraction_vec(r["point_BU"])
   if r["primitive_id"]==previous_id and t==0 and p==previous_point and r["barycentric"]==previous_bary:action="EXCLUDE_EXACT_PREVIOUS_POINT"
   elif 0<=t<=1:
    if r["primitive_id"]==detector_id and t==1 and p==detector_point:targets.append(r);action="EXACT_TARGET"
    else:action="BLOCK"
  decisions.append(dict(primitive_id=r["primitive_id"],action=action))
 if any(d["action"]=="BLOCK"for d in decisions):return "STOP_BLOCKED",decisions
 if len(targets)!=1:return "STOP_TARGET",decisions
 return "CPU_DECLARED_TERMINAL_CLEAR_ONLY",decisions
def trace_source(source,tris,detector,root_id,det_id,counter):
 origin=source["position"];direction=source["direction"]
 out=dict(source_id=source["id"],status="STOP_INPUT",primary_rows=[],secondary_rows=[],terminal_decisions=[])
 need(dot(direction,direction)>0,"nonzero_source_direction")
 rows=[intersect(origin,direction,t,counter)for t in tris];out["primary_rows"]=rows
 if any(r["kind"]=="UNRESOLVED"for r in rows):out["status"]="STOP_PRIMARY_UNRESOLVED";return out
 if any(r["kind"]=="HIT"and F(*r["parameter"])==0 for r in rows):out["status"]="STOP_START_CONTACT";return out
 hits=[r for r in rows if r["kind"]=="HIT"and F(*r["parameter"])>0]
 if not hits:out["status"]="STOP_PRIMARY_MISS";return out
 nearest=min(F(*r["parameter"])for r in hits);close=[r for r in hits if F(*r["parameter"])==nearest]
 if len(close)!=1:out["status"]="STOP_PRIMARY_TIE";return out
 hit=close[0];out["primary_hit"]=hit
 if hit["primitive_id"]!=root_id:out["status"]="STOP_PRIMARY_BLOCKED";return out
 p=fraction_vec(hit["point_BU"]);n=fraction_vec(hit["normal"]);reflected=sub(direction,scale(n,2*dot(direction,n)/dot(n,n)))
 segment=sub(detector,p);out["reflected_direction"]=vec(reflected)
 if dot(segment,segment)==0 or cross(segment,reflected)!=(0,0,0)or dot(segment,reflected)<=0:
  out["status"]="STOP_DECLARED_DETECTOR_NOT_ON_REFLECTED_RAY";return out
 second=[intersect(p,segment,t,counter)for t in tris];out["secondary_rows"]=second
 status,decisions=terminal(second,root_id,p,hit["barycentric"],det_id,detector)
 out.update(status=status,terminal_decisions=decisions,segment_endpoints_BU=[vec(origin),vec(p),vec(detector)],
  segment_squared_BU2=[pair(dot(sub(p,origin),sub(p,origin))),pair(dot(segment,segment))])
 return out
def trace(packet,x):
 """Internal declared-scene backend: numerical geometry ONLY from validated input words."""
 r=base()
 try:
  sources,tris,detector,root_id,det_id,lam,ref=decoded_inputs(packet,x,r)
  r.update(scene_sha256=packet["manifest"]["scene_sha256"],query_sha256=packet["manifest"]["query_sha256"],
   input_buffer_sha256=packet["manifest"]["buffer_sha256"],original_lambda_BU=pair(lam),original_reference_BU=pair(ref))
  for s in sources:r["source_results"].append(trace_source(s,tris,detector,root_id,det_id,r))
  need([s["source_id"]for s in r["source_results"]]==["S0","S1"],"literal_sources")
  if all(s["status"]=="CPU_DECLARED_TERMINAL_CLEAR_ONLY"for s in r["source_results"]):
   r.update(status="CPU_RATIONAL_DECLARED_TWO_SEGMENT_TRACE_ONLY",declared_two_segment_trace_certified=True,reason="unique_primary_and_exact_terminal")
  else:r.update(status="STOP_TRACE",reason="SOURCE_trace_rejected")
 except(ValueError,KeyError,TypeError,IndexError,OverflowError,struct.error,RecursionError)as ex:r["reason"]=str(ex)
 return r
def evaluate(k,q,e,admitted,packets):
 r=base()
 try:
  expected=selector(k,e)
  need(type(q)is dict and set(q)==set(expected),"closed_selector_shape")
  for key,val in expected.items():
   need(type(q[key])is type(val),"typed_selector")
   if type(val)is str:need(len(q[key])<=512,"bounded_selector_string")
   else:need(type(q[key])is list and len(q[key])==2 and all(type(v)is str and len(v)<=8 for v in q[key]),"bounded_selector_SOURCE")
  need(digest(q)==digest(expected),"original_selector")
  if k not in admitted:r.update(status="STOP_UPSTREAM",retained_status=e[k]["result"]["status"],reason=e[k]["result"].get("reason"));return r
  return trace(packets[k],e[k])
 except(ValueError,KeyError,TypeError,IndexError,RecursionError)as ex:r["reason"]=str(ex);return r
def run(k,q):
 try:e,a,packets,pins=retained();return evaluate(k,q,e,a,packets)
 except(OSError,ValueError,KeyError,TypeError,RecursionError)as ex:
  r=base();r.update(status="STOP_DEPENDENCY",reason=str(ex));return r
