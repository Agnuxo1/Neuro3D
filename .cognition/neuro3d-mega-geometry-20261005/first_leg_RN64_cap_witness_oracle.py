"""Independent algebraic cap witness checks. No project imports or roots."""
import ast,base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ID="PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-CAP-WITNESS-CPU-001"
r=json.loads((Path("coordinacion/respuestas")/(ID+"-CODEX.json")).read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def cap(c):
 assert c["rc"]==0 and c.get("timed_out",False)is False
 b=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True))
 assert len(b)==c["stdout_bytes"] and sha(b)==c["stdout_sha256"]
 d=json.loads(b);assert d["status"]=="PASS";return d
for p,h in r["code_doc_sha256"].items():assert sha(Path(p).read_bytes())==h
core=next(p for p in r["code_doc_sha256"]if "/capacity_audit/"in p)
tree=ast.parse(Path(core).read_text(encoding="utf-8"))
for node in ast.walk(tree):
 if isinstance(node,ast.Call):
  name=node.func.id if isinstance(node.func,ast.Name)else node.func.attr if isinstance(node.func,ast.Attribute)else ""
  assert name not in ("sqrt","isqrt","run_kernel","enclose_triangle")
data=cap(r["test_run"]);assert r["test_run"]["before_deadline"]is True and data["tests"]==4 and len(data["records"])==61
parents={}
for name,h in r["parent_receipts_sha256"].items():
 b=(Path("coordinacion/respuestas")/name).read_bytes();assert sha(b)==h
 parents[name]=cap(json.loads(b)["test_run"])
graphs=parents[next(n for n in parents if "GRAPH-HOST" in n)]
grows={digest(z["result"]):z["result"]for z in graphs["records"]if z["kind"]=="FIXED_GRAPH_OR_STOP"};assert len(grows)==28
inputs=parents[next(n for n in parents if "COMMON-DETECTOR" in n)]["data"]["inputs"]
counts=dict(exceeded=0,fits=0,upstream_STOP=0,ties=0)
ratios={}
selected={}
for z in data["records"]:
 if z["kind"]=="TIE_CONTROL":
  c=z["result"];q=F(*c["squared_input_BU2"]);lo,hi=map(lambda v:F(*v),c["adjacent_candidates_BU"])
  assert q==((lo+hi)/2)**2 and c["tie_to_even_applied"]is True
  e=lo.numerator.bit_length()-lo.denominator.bit_length()
  if lo<F(2)**e:e-=1
  index=lo/(F(2)**(e-52))
  assert index.denominator==1
  assert F(*c["selected_RN64_length_BU"])==(lo if index.numerator%2==0 else hi)
  counts["ties"]+=1;continue
 if z["kind"]!="FIXED_WITNESS_OR_STOP":continue
 o=z["result"];g=grows[o["captured_graph_row_sha256"]]
 assert o["case"]==g["case"]and o["source_id"]==g["source_id"]
 assert o["promotion"]=="STOP"and o["native_precision_certified"]is False and o["GPU_used"]is False
 assert o["SOURCE_merged"]is False and o["new_root_evaluations"]==0
 if o["status"]=="STOP_UPSTREAM_NO_CAP_WITNESS":
  assert g["status"]=="STOP_UPSTREAM_NO_FIRST_LEG_GRAPH";counts["upstream_STOP"]+=1;continue
 query=inputs[o["case"]]["request"];scene=inputs[o["case"]]["scene"]
 assert digest(query)==o["query_sha256"]==g["query_sha256"]and digest(scene)==o["scene_sha256"]
 c=o["selection"];q=F(*c["squared_input_BU2"]);lo,hi=map(lambda v:F(*v),c["adjacent_candidates_BU"])
 # Different lattice verification from producer integer successor.
 v=float(lo);assert F.from_float(v)==lo and F.from_float(math.nextafter(v,math.inf))==hi
 assert lo*lo<=q<=hi*hi
 midpoint=((lo+hi)/2)**2;assert midpoint==F(*c["squared_midpoint_BU2"])
 assert q!=midpoint and c["tie_to_even_applied"]is False
 rn=lo if q<midpoint else hi
 assert rn==F(*c["selected_RN64_length_BU"])
 geom_lo,geom_hi=map(lambda v:F(*v),g["captured_geometric_first_length_BU"])
 assert geom_lo*geom_lo<=q<=geom_hi*geom_hi
 delta=[F(*b[0])-F(*a[0])for a,b in zip(g["source_box_BU"],g["previous_P_box_BU"])]
 assert q==sum((v*v for v in delta),F(0))==F(*g["radicand_interval_BU2"][0])
 signed=(rn-geom_hi,rn-geom_lo)
 assert signed==tuple(F(*v)for v in o["signed_first_leg_discrepancy_BU"])
 low=F(0)if signed[0]<=0<=signed[1]else min(abs(v)for v in signed)
 high=max(abs(v)for v in signed)
 assert (low,high)==tuple(F(*v)for v in o["absolute_first_leg_discrepancy_BU"])
 wave=F(*query["lambda_BU"]);budget=F(*query["source_width_caps_rad"][query["source_ids"].index(o["source_id"])])
 phase=(6*low/wave,8*high/wave)
 assert phase==tuple(F(*v)for v in o["isolated_phase_term_error_rad"])
 assert budget==F(*o["original_SOURCE_cap_rad"])==F(1,2**80)
 assert o["total_path_cap_failure_proved"]is False and o["phase_certified"]is False
 assert o["native_SOURCE_ingress_error_bound_BU"]is None and o["first_leg_native_accuracy_budget_BU"]is None
 assert o["cancellation_with_other_terms_excluded"]is False
 assert o["original_cap_observable"]=="GEOMETRIC_INTERVAL_WIDTH_RAD_NOT_NATIVE_ACCURACY"
 assert o["original_width_contract_failure_proved"]is False
 assert o["modeled_RN_point_length_interval_BU"]==[c["selected_RN64_length_BU"]]*2
 assert o["modeled_RN_point_length_width_BU"]==[0,1]and o["formal_deterministic_term_uncertainty_width_rad"]==[0,1]
 assert o["modeled_pointwise_discrepancy_nonzero_proved"]is True and rn*rn!=q
 if phase[0]>budget:
  counts["exceeded"]+=1;assert o["status"]=="TERM_ERROR_ABOVE_LITERAL_WIDTH_SCALE"
  ratios[o["case"]+"/"+o["source_id"]]=[str((phase[0]/budget).numerator),str((phase[0]/budget).denominator)]
 else:
  counts["fits"]+=1;assert phase[1]<=budget and o["status"]=="TERM_ERROR_BOUND_WITHIN_LITERAL_WIDTH_SCALE"
 selected[o["case"]+"/"+o["source_id"]]=[str(rn.numerator),str(rn.denominator)]
assert counts==dict(exceeded=6,fits=2,upstream_STOP=20,ties=2)
m=r["frozen_manifest"];raw=Path(m["path"]).read_bytes();assert sha(raw)==m["sha256"]
c=json.loads(raw)["pinned_manifest_capture"];raw=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"]));assert sha(raw)==c["stdout_sha256"]
pins=json.loads(raw)["pins"];assert len(pins)==461 and all(sha(Path(p).read_bytes())==h for p,h in pins.items())
print(json.dumps(dict(status="PASS",counts=counts,frozen_pins_verified=461,selected_RN_lengths_decimal_integer_strings=selected,
 isolated_term_lower_bound_over_literal_width_scale_decimal_integer_strings=ratios,new_root_evaluations=0,
 total_path_cap_failure_proved=False,original_width_contract_failure_proved=False,native_precision_certified=False,GPU_used=False,full_costs="UNKNOWN_NOT_ZERO"),sort_keys=True))

