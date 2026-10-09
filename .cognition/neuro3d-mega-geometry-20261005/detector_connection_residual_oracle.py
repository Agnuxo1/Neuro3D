"""Independent detector residual certificates and receipt binding, no producer imports."""
import base64
from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import zlib
ROOT=Path("D:/PROJECTS/9_NEBULA_NEW")
ID="PRECISION-ORIGINAL-SOURCE-DETECTOR-CONNECTION-RESIDUAL-HOST-001"
def sha(b):return hashlib.sha256(b).hexdigest()
def dg(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def read(name):return json.loads((ROOT/"coordinacion/respuestas"/name).read_bytes())
def captured(r):
 t=r["test_run"];assert type(t["rc"])is int and t["rc"]==0 and t.get("timed_out",False)is False
 if "before_deadline"in t:assert t["before_deadline"]is True
 raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
 assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
 d=json.loads(raw);assert d["status"]=="PASS";return d
r=read(ID+"-CODEX.json")
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h
d=captured(r)
parents={
"PRECISION-ORIGINAL-SOURCE-CANDIDATE-PATH-CYCLES-HOST-001-CODEX.json":"53b739dcaaf08e2bbce9ca81ce7a24b98bc53074357720a4bc9aaaf317aae1fe",
"PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json":"139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"}
pd={}
for name,h in parents.items():
 raw=(ROOT/"coordinacion/respuestas"/name).read_bytes();assert sha(raw)==h
 pd[name]=captured(json.loads(raw))
cd=pd[next(n for n in pd if "CANDIDATE-PATH-CYCLES"in n)]
candidates=[x["result"]for x in cd["records"]if x["kind"]=="FIXED_PATH_OR_STOP"]
geom=pd[next(n for n in pd if "COMMON-DETECTOR-LENGTH"in n)]["data"]["inputs"]
fixed=[x["result"]for x in d["records"]if x["kind"]=="FIXED_RESIDUAL_OR_STOP"]
assert len(fixed)==28
cmap={(x["case"],x["source_id"],x["primitive_id"]):x for x in candidates}
assert len(cmap)==28
counter=Counter();norms=0;certificates=0;corners=0;fixed_bounds={}
for rec in d["records"]:
 counter[rec["kind"]]+=1
 o=rec.get("result")
 if rec["kind"]=="FIXED_RESIDUAL_OR_STOP":
  c=cmap[(o["case"],o["source_id"],o["primitive_id"])]
  assert o["captured_SOURCE_row_sha256"]==dg(c)
  assert o["upstream_ledger_status"]=="STOP_UNRESOLVED_ALL_PRIMITIVES"
  assert o["parent_receipts_sha256"]==parents
  if c["cycles_interval"]is None:
   assert "residual"not in o and o["status"]=="STOP_UPSTREAM_NO_DETECTOR_RESIDUAL"
   assert o["costs"]["new_interval_segment_norms"]==o["costs"]["new_integer_root_certificates"]==0
   continue
  lit=geom[o["case"]]["request"]
  assert dg(lit)==o["query_sha256"]
  assert o["candidate_Q_box_BU"]==c["candidate_next_point_box_BU"]
  assert o["literal_detector_point_BU"]==lit["detector_point_BU"]
  assert o["wavelength_BU"]==[lit["lambda_BU"]]*2
  assert o["detector_point_in_candidate_box"]is True and o["ALL_candidate_box_points_equal_literal_detector"]is False
 if o is None or "residual"not in o:continue
 norms+=1
 q=[[F(*x)for x in axis]for axis in o["candidate_Q_box_BU"]]
 det=[F(*x)for x in o["literal_detector_point_BU"]]
 comps=[(a-t,b-t)for (a,b),t in zip(q,det)]
 sqlo=sum((F(0)if a<=0<=b else min(a*a,b*b)for a,b in comps),F(0))
 sqhi=sum((max(a*a,b*b)for a,b in comps),F(0))
 v=o["residual"];assert [F(*x)for x in v["squared_BU2"]]==[sqlo,sqhi]
 for name,sq in (("root_lower_certificate",sqlo),("root_upper_certificate",sqhi)):
  c=v[name];assert F(*c["squared"])==sq and c["fraction_bits"]==96
  n=c["floor_scaled_root"];scaled=sq.numerator<<192
  assert n*n*sq.denominator<=scaled<(n+1)**2*sq.denominator
  exact=n*n*sq.denominator==scaled
  assert F(*c["lower_BU"])==F(n,2**96)
  assert F(*c["upper_BU"])==F(n if exact else n+1,2**96)
  assert c["exact"]is exact;certificates+=1
 lo=F(*v["root_lower_certificate"]["lower_BU"]);hi=F(*v["root_upper_certificate"]["upper_BU"])
 assert [F(*x)for x in v["length_BU"]]==[lo,hi]
 for corner in itertools.product(*q):
  sq=sum(((a-b)**2 for a,b in zip(corner,det)),F(0))
  assert lo*lo<=sq<=hi*hi;corners+=1
 witness=[F(*x)for x in o["max_distance_box_witness_Q_BU"]]
 assert sum(((a-b)**2 for a,b in zip(witness,det)),F(0))==sqhi
 assert F(*o["max_distance_box_witness_squared_BU2"])==sqhi
 wlow=F(*o["wavelength_BU"][0]);assert wlow>0
 assert F(*o["conditional_Q_replacement_allowance_cycles"])==hi/wlow
 assert F(*o["conditional_Q_replacement_allowance_rad"])==8*hi/wlow
 assert o["original_detector_connection_budget_BU"]is None
 assert o["native_detector_error_bound_BU"]is None and o["native_phase_error_bound_rad"]is None
 assert o["detector_connection_certified"]is False and o["phase_certified"]is False
 assert o["actual_Q_replaced"]is False and o["cap_budget_admitted"]is False
 if rec["kind"]=="REVERSE_TRIANGLE_CONTROL":
  assert all(a==b for a,b in q);p=F(rec["P_BU"])
  assert abs(abs(q[0][0]-p)-abs(det[0]-p))<=hi
 if rec["kind"]=="FIXED_RESIDUAL_OR_STOP":fixed_bounds[o["case"]+"/"+o["source_id"]]=o["conditional_Q_replacement_allowance_rad"]
raw=(ROOT/"coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json").read_bytes()
assert sha(raw)=="172576dd8a38cf8119f2a1a3d229b534a7e77fdbde2632e2ef967b10e2d6e9f4"
pc=json.loads(raw)["pinned_manifest_capture"]
raw=zlib.decompress(base64.b64decode(pc["stdout_zlib_base64"]));assert sha(raw)==pc["stdout_sha256"]
pins=json.loads(raw)["pins"];assert len(pins)==461
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h
assert norms==19 and certificates==38 and corners==152
print(json.dumps(dict(id=ID,status="PASS",tests=d["tests"],records=len(d["records"]),groups=dict(counter),
fixed_new_norms=8,fixed_new_root_certificates=16,upstream_STOP_preserved=20,
captured_new_norms_verified=norms,captured_new_root_certificates_verified=certificates,
new_corner_combinations_verified=corners,additional_copy_control_norm_not_in_captured_results=1,
fixed_conditional_allowances_rad=fixed_bounds,pinned_files_intact=461,GPU_used=False,
native_detector_connection_certified=False,old_root_replays=0,frozen_producer_replays=0),sort_keys=True))
