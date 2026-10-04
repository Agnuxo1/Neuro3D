"""Opt-in signed CYCLES branch certificate. No RAD/physical-phase conversion."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,base64,zlib,math
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-signed-cycle-branch-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-REFERENCE-ARGUMENT-INTERVAL-HOST-001-CODEX.json"
PSHA="ac1addc257bb8efee5a43b30e499575faa50064fbd23f4237130feeb942ee87c"
FALSE_FLAGS=("phase_certified","phase_accuracy_budget_admitted","reference_truth_verified",
 "gauge_provenance_verified","material_phase_verified","scene_authenticated",
 "native_IEEE_RN_graph_certified","GPU_used","Bpy_used","RT_used","physical_field_certified",
 "exact_contact_allowed","computed_hilo_collapse_allowed","SOURCE_merged")
def need(ok,s):
 if not ok:raise ValueError(s)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def pair(x):return [x.numerator,x.denominator]
def capture(w):
 need(w["rc"]==0 and w["timed_out"]is False,"complete_capture")
 raw=zlib.decompress(base64.b64decode(w["stdout_zlib_base64"]))
 need(len(raw)==w["stdout_bytes"]and hashlib.sha256(raw).hexdigest()==w["stdout_sha256"],"sealed_capture")
 return json.loads(raw)
def retained():
 raw=(ROOT/PARENT).read_bytes()
 need(len(raw)==128963 and hashlib.sha256(raw).hexdigest()==PSHA,"signed_parent")
 p=json.loads(raw);pins=dict(p["code_doc_sha256"]);need(len(pins)==359,"pins359")
 for s,h in pins.items():need(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h,"dependency:"+s)
 need(capture(p["independent_verification"])["status"]=="PASS","parent_oracle")
 d=capture(p["test_run"]);need(d["status"]=="PASS","parent_suite")
 e={x["id"]:x["result"]for x in d["evidence"]["positive"]+d["evidence"]["upstream"]}
 a={x["id"]for x in d["evidence"]["positive"]};need(len(e)==44 and len(a)==6,"closed_cases")
 pins[PARENT]=PSHA;return e,a,pins
def base():
 r=dict(model=MODEL,status="STOP_INPUT",reason=None,SOURCE_results=[],HOST_branch_verified=False,
  new_integer_floor_evaluations=0,new_endpoint_translations=0,old_numeric_replays=0,
  old_encoder_replays=0,old_geometry_replays=0,old_guard_replays=0,old_root_replays=0,
  new_input_word_decodes=0,RAD_conversion_performed=False,pi_trig_used=False,
  phase_error_bound=None,full_costs="UNKNOWN_NOT_ZERO")
 r.update({k:False for k in FALSE_FLAGS});return r
def rat(v):
 need(type(v)is list and len(v)==2 and all(type(x)is int for x in v),"typed_rational")
 n,d=v;need(d>0 and math.gcd(n,d)==1 and max(abs(n).bit_length(),d.bit_length())<=128,"canonical_capacity128")
 q=F(n,d);need(abs(q)<=2**64,"cycle_magnitude_capacity");return q
def branch(packet,r):
 need(type(packet)is dict and set(packet)=={"unit","closed_interval"},"closed_cycle_packet")
 need(type(packet["unit"])is str and packet["unit"]=="CYCLES","unit_CYCLES_only")
 v=packet["closed_interval"];need(type(v)is list and len(v)==2,"closed_interval_pair")
 lo,hi=(rat(x)for x in v);need(lo<=hi,"ordered_interval")
 r["new_integer_floor_evaluations"]+=2
 il=lo.numerator//lo.denominator;ih=hi.numerator//hi.denominator
 need(il*lo.denominator<=lo.numerator<(il+1)*lo.denominator and ih*hi.denominator<=hi.numerator<(ih+1)*hi.denominator,"floor_certificate")
 z=dict(unit="CYCLES",closed_signed_interval=v,endpoint_floor_integers=[il,ih],
  branch_unique=il==ih,branch_integer=il if il==ih else None,closed_residual_interval=None,
  phase_error_bound=None,phase_accuracy_budget_admitted=False,
  interpretation="ARITHMETIC_BRANCH_ONLY_NO_PHYSICAL_PHASE")
 if il!=ih:z["status"]="STOP_BRANCH_CROSSING";return z
 r["new_endpoint_translations"]+=2;rl=lo-il;rh=hi-il
 need(F(0)<=rl<=rh<F(1)and rl+il==lo and rh+il==hi and rh-rl==hi-lo,"exact_branch_reconstruction")
 z.update(status="HOST_UNIQUE_CYCLE_BRANCH_ONLY",closed_residual_interval=[pair(rl),pair(rh)])
 return z
def selector(k,e):
 return dict(model=MODEL,case=k,source_ids=["S0","S1"],signed_result_sha256=digest(e[k]),parent_receipt_sha256=PSHA)
def evaluate(k,q,e,a,received=None):
 r=base()
 try:
  need(type(k)is str and k in e,"known_case");expected=selector(k,e)
  need(type(q)is dict and set(q)==set(expected),"closed_selector")
  for key,v in expected.items():
   need(type(q[key])is type(v),"typed_selector")
   if type(v)is str:need(len(q[key])<=512,"bounded_selector")
  need(digest(q)==digest(expected),"original_selector")
  if k not in a:
   r.update(status="STOP_UPSTREAM",retained_status=e[k]["retained_status"]);return r
  x=e[k]if received is None else received
  need(type(x)is dict and digest(x)==digest(e[k]),"sealed_same_signed_result")
  need(x["status"]=="HOST_DECLARED_SIGNED_ARGUMENT_INTERVAL_ONLY"and x["argument_interval_enclosure_verified"]is True,"argument_evidence")
  need(x["phase_error_bound"]is None and all(x[t]is False for t in FALSE_FLAGS),"retain_no_phase_or_contact")
  need(x["reference_is_shared_declared_scalar"]is True and x["cap_used_for_cycles_or_phase"]is False,"reference_not_physical_or_RAD_cap")
  ss=x["SOURCE_results"];need(type(ss)is list and len(ss)==2 and [s["source_id"]for s in ss]==["S0","S1"],"separate_SOURCE_order")
  out=[]
  for s in ss:
   v=s["argument"];need(v["phase_error_bound"]is None and v["phase_accuracy_budget_admitted"]is False and s["cap_used_for_cycles_or_phase"]is False and s["exact_contact_allowed"]is False,"SOURCE_no_phase_or_contact")
   need(s["coverage"]["source_id"]==s["source_id"],"SOURCE_coverage_join")
   z=branch(dict(unit="CYCLES",closed_interval=v["signed_cycles"]),r)
   out.append(dict(source_id=s["source_id"],branch=z,coverage=s["coverage"],original_cap_rad_HOST_only=s["original_cap_rad_HOST_only"],cap_used_for_cycles_or_phase=False,exact_contact_allowed=False))
  unique=all(s["branch"]["branch_unique"]for s in out)
  r.update(status="HOST_UNIQUE_SOURCE_CYCLE_BRANCHES_ONLY"if unique else "STOP_BRANCH_CROSSING",
   HOST_branch_verified=unique,SOURCE_results=out,parent_receipt_sha256=PSHA,
   signed_result_sha256=digest(x),scene_sha256=x["scene_sha256"],query_sha256=x["query_sha256"],
   input_buffer_sha256=x["input_buffer_sha256"],geometry_record_sha256=x["geometry_record_sha256"],
   length_result_sha256=x["length_result_sha256"],geometry_packet_sha256=x["geometry_packet_sha256"],
   geometry_receipt_sha256=x["geometry_receipt_sha256"],original_input_descriptors=x["original_input_descriptors"],
   original_relative_cap_rad_HOST_only=x["original_relative_cap_rad_HOST_only"],
   shared_reference_only_declared=True,common_reference_cancellation_performed=False,cap_used_for_cycles_or_phase=False)
 except(ValueError,KeyError,TypeError,IndexError,OverflowError,RecursionError)as ex:
  r.update(status="STOP_INPUT",reason=str(ex),HOST_branch_verified=False,SOURCE_results=[])
 return r
def run(k,q,received=None):
 try:e,a,pins=retained();return evaluate(k,q,e,a,received)
 except(OSError,ValueError,KeyError,TypeError,RecursionError)as ex:
  r=base();r.update(status="STOP_DEPENDENCY",reason=str(ex));return r
