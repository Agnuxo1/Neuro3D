"""Common declared reference cancellation for separated geometric source intervals."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,base64,zlib,math
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-common-reference-difference-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SIGNED-CYCLE-BRANCH-HOST-001-CODEX.json"
PSHA="0629340de0d391e0462fd612dc099604da6943ee2e5e5fc7931779c1bbde90f0"
SIGNED="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-REFERENCE-ARGUMENT-INTERVAL-HOST-001-CODEX.json"
SSHA="ac1addc257bb8efee5a43b30e499575faa50064fbd23f4237130feeb942ee87c"
FLAGS=("phase_certified","phase_accuracy_budget_admitted","reference_truth_verified",
 "gauge_provenance_verified","material_phase_verified","scene_authenticated","native_IEEE_RN_graph_certified",
 "GPU_used","Bpy_used","RT_used","physical_field_certified","exact_contact_allowed",
 "computed_hilo_collapse_allowed","SOURCE_merged")
def need(ok,s):
 if not ok:raise ValueError(s)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def pair(x):return [x.numerator,x.denominator]
def rat(v):
 need(type(v)is list and len(v)==2 and all(type(n)is int for n in v),"typed_rational")
 n,d=v;need(d>0 and math.gcd(n,d)==1 and max(abs(n).bit_length(),d.bit_length())<=128,"canonical_capacity128")
 return F(n,d)
def capture(w):
 need(w["rc"]==0 and w["timed_out"]is False,"complete_capture")
 b=zlib.decompress(base64.b64decode(w["stdout_zlib_base64"]))
 need(len(b)==w["stdout_bytes"]and hashlib.sha256(b).hexdigest()==w["stdout_sha256"],"capture_seal")
 return json.loads(b)
def retained():
 raw=(ROOT/PARENT).read_bytes();need(len(raw)==120568 and hashlib.sha256(raw).hexdigest()==PSHA,"branch_parent")
 p=json.loads(raw);pins=dict(p["code_doc_sha256"]);need(len(pins)==363 and pins[SIGNED]==SSHA,"pins363_signed")
 for s,h in pins.items():need(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h,"dependency:"+s)
 need(capture(p["independent_verification"])["status"]=="PASS","branch_oracle")
 d=capture(p["test_run"]);need(d["status"]=="PASS","branch_suite")
 e={x["id"]:x["result"]for x in d["evidence"]["positive"]+d["evidence"]["upstream"]}
 a={x["id"]for x in d["evidence"]["positive"]}
 sp=json.loads((ROOT/SIGNED).read_bytes());sd=capture(sp["test_run"])
 need(sd["status"]=="PASS"and capture(sp["independent_verification"])["status"]=="PASS","signed_captures")
 j={x["id"]:x["result"]for x in sd["evidence"]["positive"]}
 need(len(e)==44 and len(a)==6 and set(j)==a,"closed_same_cases")
 pins[PARENT]=PSHA;return e,a,j,pins
def base():
 r=dict(model=MODEL,status="STOP_INPUT",reason=None,HOST_relative_interval_verified=False,SOURCE_inputs=[],
  relative=None,new_length_endpoint_subtractions=0,new_relative_endpoint_divisions=0,
  new_signed_cycle_contrast_subtractions=0,old_numeric_replays=0,old_encoder_replays=0,
  old_geometry_replays=0,old_guard_replays=0,old_root_replays=0,new_input_word_decodes=0,
  RAD_conversion_performed=False,pi_trig_used=False,phase_error_bound=None,full_costs="UNKNOWN_NOT_ZERO")
 r.update({k:False for k in FLAGS});return r
def relative(lengths,reference,wavelength,r,correlation="DECLARED_SAME_R"):
 need(type(correlation)is str and correlation=="DECLARED_SAME_R","explicit_common_reference")
 need(type(lengths)is tuple and len(lengths)==2 and all(type(v)is tuple and len(v)==2 for v in lengths),"typed_length_intervals")
 need(type(reference)is tuple and len(reference)==2 and all(type(x)is F for x in lengths[0]+lengths[1]+reference),"typed_Fraction_intervals")
 need(type(wavelength)is F and wavelength>0,"positive_singleton_lambda")
 need(all(F(0)<=v[0]<=v[1]for v in lengths)and reference[0]<=reference[1],"ordered_BU_intervals")
 need(all(max(abs(x.numerator).bit_length(),x.denominator.bit_length())<=512 and abs(x)<=2**64 for x in lengths[0]+lengths[1]+reference+(wavelength,)),"relative_capacity")
 r["new_length_endpoint_subtractions"]+=2
 dl=lengths[0][0]-lengths[1][1];dh=lengths[0][1]-lengths[1][0]
 r["new_relative_endpoint_divisions"]+=2;cl=dl/wavelength;ch=dh/wavelength
 need(cl<=ch and ch-cl==((lengths[0][1]-lengths[0][0])+(lengths[1][1]-lengths[1][0]))/wavelength,"sum_separate_length_widths")
 return dict(unit="CYCLES",source_order=["S0","S1"],definition="C0_minus_C1",
  signed_length_difference_BU=[pair(dl),pair(dh)],closed_signed_relative_cycles=[pair(cl),pair(ch)],
  interval_width_cycles=pair(ch-cl),common_reference_BU=[pair(x)for x in reference],lambda_BU=pair(wavelength),
  common_reference_symbol=correlation,common_reference_cancellation="SYMBOLIC_SAME_R_ONLY",
  reference_contribution_cycles=[0,1],SOURCE_fields_combined=False,phase_error_bound=None,
  phase_accuracy_budget_admitted=False,interpretation="DECLARED_GEOMETRIC_DIFFERENCE_NOT_PHASE_ERROR_RAD")
def selector(k,e,j):
 return dict(model=MODEL,case=k,source_ids=["S0","S1"],branch_result_sha256=digest(e[k]),
  signed_result_sha256=digest(j[k])if k in j else None,parent_receipt_sha256=PSHA,signed_receipt_sha256=SSHA)
def evaluate(k,q,e,a,j,received=None):
 r=base()
 try:
  need(type(k)is str and k in e,"known_case");expected=selector(k,e,j)
  need(type(q)is dict and set(q)==set(expected),"closed_selector")
  for key,v in expected.items():
   need(type(q[key])is type(v),"typed_selector")
   if type(v)is str:need(len(q[key])<=512,"bounded_selector")
  need(digest(q)==digest(expected),"original_selector")
  if k not in a:r.update(status="STOP_UPSTREAM",retained_status=e[k]["retained_status"]);return r
  ref=dict(branch=e[k],signed=j[k]);bundle=ref if received is None else received
  need(type(bundle)is dict and set(bundle)==set(ref)and digest(bundle)==digest(ref),"sealed_same_original_bundle")
  br=bundle["branch"];s=bundle["signed"]
  need(br["HOST_branch_verified"]is True and br["status"]=="HOST_UNIQUE_SOURCE_CYCLE_BRANCHES_ONLY"and s["argument_interval_enclosure_verified"]is True,"retained_arithmetic_only")
  need(all(v[t]is False for v in (br,s)for t in FLAGS)and br["phase_error_bound"]is None and s["phase_error_bound"]is None,"retain_no_physical_phase_contact")
  need(br["signed_result_sha256"]==digest(s),"signed_branch_join")
  for key in ("scene_sha256","query_sha256","input_buffer_sha256","geometry_record_sha256","length_result_sha256","geometry_packet_sha256","geometry_receipt_sha256","original_input_descriptors"):
   need(br[key]==s[key],"same:"+key)
  need(s["reference_is_shared_declared_scalar"]is True and br["shared_reference_only_declared"]is True and s["cap_used_for_cycles_or_phase"]is False and br["cap_used_for_cycles_or_phase"]is False,"common_declared_reference_only")
  ss=s["SOURCE_results"];bs=br["SOURCE_results"]
  need(type(ss)is list and type(bs)is list and len(ss)==len(bs)==2 and [x["source_id"]for x in ss]==[x["source_id"]for x in bs]==["S0","S1"],"SOURCE_order")
  args=[v["argument"]for v in ss]
  need(args[0]["reference_BU"]==args[1]["reference_BU"]and args[0]["lambda_BU"]==args[1]["lambda_BU"],"same_SOURCE_lambda_reference")
  reference=tuple(rat(x)for x in args[0]["reference_BU"]);wavelength=rat(args[0]["lambda_BU"])
  need(len(reference)==2 and reference[0]==reference[1]and wavelength>0,"original_singletons")
  desc=s["original_input_descriptors"];need(type(desc)is list and len(desc)==2,"original_input_descriptors")
  for path,val in (("query/lambda_BU",wavelength),("query/reference_BU",reference[0])):
   found=[v for v in desc if v["path"]==path];need(len(found)==1,"unique_original_scalar")
   v=found[0];need(v["unit"]=="BU"and v["conversion_abs_error_BU"]==[0,1]and rat(v["original_rational"])==rat(v["decoded_rational"])==val,"exact_original_scalar_BU")
  lengths=[];inputs=[]
  for i,v in enumerate(ss):
   vv=args[i];bb=bs[i]
   need(v["coverage"]==bb["coverage"]and v["coverage"]["source_id"]==v["source_id"]and v["original_cap_rad_HOST_only"]==bb["original_cap_rad_HOST_only"],"SOURCE_coverage_caps")
   need(vv["phase_error_bound"]is None and vv["phase_accuracy_budget_admitted"]is False and v["cap_used_for_cycles_or_phase"]is False and v["exact_contact_allowed"]is False,"SOURCE_no_phase_contact")
   need(bb["branch"]["closed_signed_interval"]==vv["signed_cycles"]and bb["branch"]["branch_unique"]is True,"retained_SOURCE_branch")
   lengths.append(tuple(rat(x)for x in vv["length_BU"]))
   inputs.append(dict(source_id=v["source_id"],length_BU=vv["length_BU"],signed_cycles=vv["signed_cycles"],coverage=v["coverage"],original_cap_rad_HOST_only=v["original_cap_rad_HOST_only"],reference_BU=vv["reference_BU"],lambda_BU=vv["lambda_BU"],branch=bb["branch"],cap_used_for_cycles_or_phase=False))
  z=relative(tuple(lengths),reference,wavelength,r)
  cs=[tuple(rat(x)for x in vv["signed_cycles"])for vv in args]
  r["new_signed_cycle_contrast_subtractions"]+=2;contrast=(cs[0][0]-cs[1][1],cs[0][1]-cs[1][0])
  need(z["closed_signed_relative_cycles"]==[pair(x)for x in contrast],"length_vs_signed_cycle_contrast")
  r.update(status="HOST_DECLARED_COMMON_REFERENCE_DIFFERENCE_ONLY",HOST_relative_interval_verified=True,relative=z,SOURCE_inputs=inputs,
   branch_result_sha256=digest(br),signed_result_sha256=digest(s),parent_receipt_sha256=PSHA,signed_receipt_sha256=SSHA,
   scene_sha256=s["scene_sha256"],query_sha256=s["query_sha256"],input_buffer_sha256=s["input_buffer_sha256"],
   geometry_record_sha256=s["geometry_record_sha256"],original_relative_cap_rad_HOST_only=s["original_relative_cap_rad_HOST_only"],
   cap_used_for_cycles_or_phase=False,relative_branch_not_certified=True,physical_reference_truth_not_proved=True)
 except(ValueError,KeyError,TypeError,IndexError,OverflowError,RecursionError)as ex:
  r.update(status="STOP_INPUT",reason=str(ex),HOST_relative_interval_verified=False,SOURCE_inputs=[],relative=None)
 return r
def run(k,q,received=None):
 try:e,a,j,pins=retained();return evaluate(k,q,e,a,j,received)
 except(OSError,ValueError,KeyError,TypeError,RecursionError)as ex:
  r=base();r.update(status="STOP_DEPENDENCY",reason=str(ex));return r
