"""Scene/query/input-bound HOST cycle intervals; no physical phase or gauge certification."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,base64,zlib,struct,math
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-scene-reference-argument-interval-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-TRACE-ENDPOINT-LENGTH-ENCLOSURE-HOST-001-CODEX.json"
PSHA="1bf7f82103218e14d04eec0c630531bfe040f9978c843e7981a7bfb8b3502d9a"
GI="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"
GSHA="f4814286200766db8494df3f99ff7653d7cf038bd1f51cd34491206a0537016b"
def need(ok,s):
 if not ok:raise ValueError(s)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def pair(q):return [q.numerator,q.denominator]
def rat(v):
 need(type(v)is list and len(v)==2 and all(type(x)is int for x in v),"typed_rational")
 need(v[1]>0 and math.gcd(v[0],v[1])==1 and max(abs(v[0]).bit_length(),v[1].bit_length())<=128,"canonical_capacity")
 return F(*v)
def capture(w):
 need(w["rc"]==0 and w["timed_out"]is False,"capture_complete")
 b=zlib.decompress(base64.b64decode(w["stdout_zlib_base64"]));need(len(b)==w["stdout_bytes"]and hashlib.sha256(b).hexdigest()==w["stdout_sha256"],"capture_seal")
 return json.loads(b)
def retained():
 b=(ROOT/PARENT).read_bytes();need(len(b)==84909 and hashlib.sha256(b).hexdigest()==PSHA,"length_parent")
 p=json.loads(b);pins=dict(p["code_doc_sha256"]);need(len(pins)==355 and pins[GI]==GSHA,"pins355_GI")
 for s,h in pins.items():need(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h,"dependency:"+s)
 need(capture(p["independent_verification"])["status"]=="PASS","length_oracle")
 d=capture(p["test_run"]);need(d["status"]=="PASS","length_suite")
 e={v["id"]:v["result"]for v in d["evidence"]["positive"]+d["evidence"]["upstream"]}
 a={v["id"]for v in d["evidence"]["positive"]};need(len(e)==44 and len(a)==6,"closed_original_cases")
 gp=json.loads((ROOT/GI).read_bytes());gd=capture(gp["test_run"]);need(gd["status"]=="PASS","GI_suite")
 g={v["id"]:v["result"]["packet"]for v in gd["evidence"]["positive"]};need(set(g)==a,"matching_case_set")
 pins[PARENT]=PSHA;return e,a,g,pins
def selector(k,e,g):
 return dict(model=MODEL,case=k,source_ids=["S0","S1"],length_result_sha256=digest(e[k]),geometry_packet_sha256=digest(g[k])if k in g else None,parent_receipt_sha256=PSHA)
def base():
 return dict(model=MODEL,status="STOP_INPUT",reason=None,SOURCE_results=[],argument_interval_enclosure_verified=False,
  new_input_word_decodes=0,new_rational_endpoint_subtractions=0,new_rational_endpoint_divisions=0,
  old_numeric_replays=0,old_encoder_replays=0,old_geometry_replays=0,old_guard_replays=0,old_root_replays=0,
  exact_contact_allowed=False,phase_certified=False,phase_accuracy_budget_admitted=False,reference_truth_verified=False,
  gauge_provenance_verified=False,material_phase_verified=False,scene_authenticated=False,
  native_IEEE_RN_graph_certified=False,GPU_used=False,Bpy_used=False,RT_used=False,physical_field_certified=False,
  phase_error_bound=None,computed_hilo_collapse_allowed=False,SOURCE_merged=False,full_costs="UNKNOWN_NOT_ZERO")
def decode(w):
 need(type(w)is int and 0<=w<2**32,"word_integer")
 exp=(w>>23)&255;mant=w&((1<<23)-1);need(w==0 or exp not in (0,255),"normal_or_positive_zero_only")
 return F(0)if w==0 else (-1 if w>>31 else 1)*F((1<<23)+mant)*F(2)**(exp-150)
def optical_inputs(packet,r):
 m=packet["manifest"];b=bytes.fromhex(packet["buffer_hex"]);need(hashlib.sha256(b).hexdigest()==m["buffer_sha256"]and len(b)==m["buffer_bytes"],"input_wire_seal")
 need(packet["manifest_sha256"]==digest(m)and m["source_ids"]==["S0","S1"],"input_manifest_seal")
 need(m["computed_outputs_in_buffer"]is False and m["phase_bound_in_buffer"]is False,"input_only")
 values={};desc=[]
 for path in ("query/lambda_BU","query/reference_BU"):
  indices=[i for i,f in enumerate(m["fields"])if f["path"]==path];need(len(indices)==1,"unique_optical_input")
  i=indices[0];f=m["fields"][i];need(f["unit"]=="BU","original_BU_units")
  offset=m["scalar_payload_offset"]+4*i;need(type(offset)is int and 0<=offset<=len(b)-4,"scalar_offset")
  w=struct.unpack_from("<I",b,offset)[0];r["new_input_word_decodes"]+=1;v=decode(w);q=rat(f["original_rational"])
  need(v==q and abs(v)<=10**6,"zero_input_conversion_error")
  values[path]=v;desc.append(dict(path=path,unit="BU",offset=offset,word=w,decoded_rational=pair(v),original_rational=f["original_rational"],conversion_abs_error_BU=[0,1]))
 need(values["query/lambda_BU"]>0,"positive_lambda")
 return values["query/lambda_BU"],values["query/reference_BU"],desc
def argument(length,reference,wavelength,r):
 need(type(length)is tuple and type(reference)is tuple and len(length)==len(reference)==2 and all(type(x)is F for x in length+reference),"typed_intervals")
 need(type(wavelength)is F and wavelength>0,"positive_singleton_lambda")
 need(F(0)<=length[0]<=length[1] and reference[0]<=reference[1],"ordered_intervals")
 need(all(max(abs(x.numerator).bit_length(),x.denominator.bit_length())<=512 for x in length+reference+(wavelength,)),"argument_capacity")
 r["new_rational_endpoint_subtractions"]+=2;dl=length[0]-reference[1];dh=length[1]-reference[0]
 r["new_rational_endpoint_divisions"]+=2;cl=dl/wavelength;ch=dh/wavelength
 lw=length[1]-length[0];rw=reference[1]-reference[0]
 need(ch-cl==(lw+rw)/wavelength,"separate_width_attribution")
 return dict(length_BU=[pair(x)for x in length],reference_BU=[pair(x)for x in reference],lambda_BU=pair(wavelength),
  signed_displacement_BU=[pair(dl),pair(dh)],signed_cycles=[pair(cl),pair(ch)],interval_width_cycles=pair(ch-cl),
  contributions=dict(length_interval_width_BU=pair(lw),reference_interval_width_BU=pair(rw),
    length_interval_width_cycles=pair(lw/wavelength),reference_interval_width_cycles=pair(rw/wavelength),
    reference_input_conversion_abs_error_BU=[0,1],lambda_input_conversion_abs_error_BU=[0,1]),
  phase_accuracy_budget_admitted=False,phase_error_bound=None,
  interpretation="DECLARED_GEOMETRIC_ARGUMENT_INTERVAL_ONLY_NO_PHYSICAL_GAUGE_OR_REFERENCE_TRUTH")
def evaluate(k,q,e,a,g,received=None):
 r=base()
 try:
  need(type(k)is str and k in e,"known_case");expected=selector(k,e,g)
  need(type(q)is dict and set(q)==set(expected),"closed_selector")
  for key,val in expected.items():
   need(type(q[key])is type(val),"typed_selector")
   if type(val)is str:need(len(q[key])<=512,"bounded_selector")
   elif type(val)is list:need(q[key]==["S0","S1"],"SOURCE_order")
  need(digest(q)==digest(expected),"original_selector")
  if k not in a:r.update(status="STOP_UPSTREAM",retained_status=e[k]["retained_status"]);return r
  ref=dict(length=e[k],geometry=g[k]);bundle=ref if received is None else received
  need(type(bundle)is dict and set(bundle)==set(ref)and digest(bundle)==digest(ref),"sealed_same_original_bundle")
  length=bundle["length"];packet=bundle["geometry"];m=packet["manifest"]
  need(length["HOST_length_enclosure_verified"]is True and length["exact_contact_allowed"]is False,"retain_length_contact_STOP")
  need(m["case"]==k and m["source_ids"]==["S0","S1"]and [s["source_id"]for s in length["SOURCE_results"]]==["S0","S1"],"case_SOURCE_join")
  for key in ("scene_sha256","query_sha256"):need(length[key]==m[key],"join:"+key)
  need(length["input_buffer_sha256"]==m["buffer_sha256"],"join:original_input_bytes")
  wavelength,reference,desc=optical_inputs(packet,r);sources=[]
  for i,sid in enumerate(("S0","S1")):
   s=length["SOURCE_results"][i];l=tuple(rat(x)for x in s["total_length_BU"])
   z=argument(l,(reference,reference),wavelength,r)
   sources.append(dict(source_id=sid,argument=z,coverage=s["coverage"],original_cap_rad_HOST_only=m["source_width_caps_rad_HOST_only"][i],
    cap_used_for_cycles_or_phase=False,exact_contact_allowed=False))
  r.update(status="HOST_DECLARED_SIGNED_ARGUMENT_INTERVAL_ONLY",argument_interval_enclosure_verified=True,SOURCE_results=sources,
   original_input_descriptors=desc,scene_sha256=m["scene_sha256"],query_sha256=m["query_sha256"],input_buffer_sha256=m["buffer_sha256"],
   geometry_record_sha256=m["record_sha256"],length_result_sha256=digest(length),geometry_packet_sha256=digest(packet),
   parent_receipt_sha256=PSHA,geometry_receipt_sha256=GSHA,reference_is_shared_declared_scalar=True,modulo_or_pi_or_trig_used=False,
   original_relative_cap_rad_HOST_only=m["relative_width_cap_rad_HOST_only"],cap_used_for_cycles_or_phase=False)
 except(ValueError,KeyError,TypeError,IndexError,OverflowError,struct.error,RecursionError)as ex:
  r.update(status="STOP_INPUT",reason=str(ex),argument_interval_enclosure_verified=False,SOURCE_results=[])
 return r
def run(k,q,received=None):
 try:e,a,g,pins=retained();return evaluate(k,q,e,a,g,received)
 except(OSError,ValueError,KeyError,TypeError,RecursionError)as ex:
  r=base();r.update(status="STOP_DEPENDENCY",reason=str(ex));return r
