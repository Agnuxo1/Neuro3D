"""Independent captured-graph verifier: no project-helper or test imports."""
import base64,copy,hashlib,itertools,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path

ID="PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-GRAPH-HOST-001"
R=Path("coordinacion/respuestas")/(ID+"-CODEX.json")
receipt=json.loads(R.read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def cap(c):
 assert c["rc"]==0 and c.get("timed_out",False)is False
 b=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True))
 assert len(b)==c["stdout_bytes"] and sha(b)==c["stdout_sha256"]
 return json.loads(b)
data=cap(receipt["test_run"])
assert receipt["test_run"]["before_deadline"]is True
assert data["status"]=="PASS" and data["tests"]==5 and len(data["records"])==93
for p,h in {**receipt["code_doc_sha256"],**receipt["pure_dependencies_sha256"]}.items():
 assert sha(Path(p).read_bytes())==h
parents={}
for name,h in receipt["parent_receipts_sha256"].items():
 b=(Path("coordinacion/respuestas")/name).read_bytes();assert sha(b)==h
 parents[name]=cap(json.loads(b)["test_run"])
cycle=parents[next(n for n in parents if "CANDIDATE-PATH-CYCLES" in n)]
oldrows={digest(r["result"]):r["result"]for r in cycle["records"]if r["kind"]=="FIXED_PATH_OR_STOP"}
geom=parents[next(n for n in parents if "COMMON-DETECTOR-LENGTH" in n)]["data"]["inputs"]
assert len(oldrows)==28
manifest=receipt["frozen_manifest"]
b=Path(manifest["path"]).read_bytes();assert sha(b)==manifest["sha256"]
c=json.loads(b)["pinned_manifest_capture"]
raw=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"]));assert sha(raw)==c["stdout_sha256"]
pins=json.loads(raw)["pins"];assert len(pins)==461
assert all(sha(Path(p).read_bytes())==h for p,h in pins.items())

def pp(q):return [q.numerator,q.denominator]
def iv(v):return tuple(F(*p)for p in v)
def direct(q,upper):
 # float conversion is only an initial candidate: exact rational comparisons
 # against adjacent binary64 lattice values certify directed rounding.
 v=float(q);f=F.from_float(v)
 if (upper and f<q)or(not upper and f>q):
  v=math.nextafter(v,math.inf if upper else -math.inf);f=F.from_float(v)
 adjacent=F.from_float(math.nextafter(v,-math.inf if upper else math.inf))
 assert (adjacent<q<=f)if upper and f!=q else ((f<=q<adjacent)if not upper and f!=q else f==q)
 return f
def out(lo,hi):return (direct(lo,False),direct(hi,True))
def even(q):return struct.unpack("<Q",struct.pack("<d",float(q)))[0]&1==0
def rn(q):
 lo,hi=out(q,q)
 if lo==hi:return lo
 return lo if q-lo<hi-q or(q-lo==hi-q and even(lo))else hi
def sqrt_rn(q):
 assert q>=0
 if not q:return F(0)
 e=q.numerator.bit_length()-q.denominator.bit_length()
 if q<F(2)**e:e-=1
 step=F(2)**max(e//2-52,-1074)
 scaled=q/(step*step)
 k=math.isqrt(scaled.numerator//scaled.denominator)
 lo=k*step;hi=lo if lo*lo==q else (k+1)*step
 assert lo*lo<=q<=hi*hi
 if lo==hi:return lo
 midpoint=(lo+hi)/2
 return lo if q<midpoint*midpoint or(q==midpoint*midpoint and even(lo))else hi
def cert(v):
 q=F(*v["squared"]);k=v["floor_scaled_root"];n=q.numerator<<192;d=q.denominator
 assert type(k)is int and k>=0 and v["fraction_bits"]==96
 assert v["scaled_numerator"]==n and v["scaled_denominator"]==d
 assert k*k*d<=n<(k+1)*(k+1)*d
 exact=k*k*d==n
 assert v["exact"]is exact
 assert v["lower_BU"]==pp(F(k,2**96))and v["upper_BU"]==pp(F(k+int(not exact),2**96))
 return q
newroots=oldroots=graphs=samples=stops=bindings=0
fixed_bounds={}
for r in data["records"]:
 if "result"not in r:continue
 g=r["result"]
 assert g["promotion"]=="STOP"and g["SOURCE_merged"]is False
 assert g["native_SOURCE_ingress_error_bound_BU"]is None
 assert g["native_first_leg_error_bound_BU"]is None and g["native_phase_error_bound_rad"]is None
 for k in ("GPU_used","Bpy_used","RT_used","native_precision_certified","first_leg_native_ALU_certified","phase_certified","scene_authenticated","GPU_launch_allowed"):
  assert g[k]is False
 if r["kind"]=="FIXED_GRAPH_OR_STOP":
  row=oldrows[g["captured_SOURCE_row_sha256"]];bindings+=1
  assert row["case"]==g["case"] and row["source_id"]==g["source_id"]
  assert digest(row)==g["captured_SOURCE_row_sha256"]
  for k in ("scene_sha256","query_sha256","input_sha256","source_record_sha256","CPU_packet_binding_sha256","primitive_id","previous_primitive_id"):
   assert row[k]==g[k]
  assert g["upstream_ledger_status"]==row["upstream_ledger_status"]=="STOP_UNRESOLVED_ALL_PRIMITIVES"
  if row["cycles_interval"]is None:
   stops+=1;assert g["status"]=="STOP_UPSTREAM_NO_FIRST_LEG_GRAPH"and g["costs"]["new_integer_root_certificates"]==0
   continue
  assert g["source_box_BU"]==row["source_origin_box_BU"] and g["previous_P_box_BU"]==row["previous_point_box_BU"]
  lit=geom[g["case"]];s=next(s for s in lit["scene"]["sources"]if s["id"]==g["source_id"])
  assert g["source_box_BU"]==[[v,v]for v in s["position_BU"]]
  assert digest(lit["scene"])==g["scene_sha256"] and digest(lit["request"])==g["query_sha256"]
  seg=row["new_first_segment"]
  for c in (seg["root_lower_certificate"],seg["root_upper_certificate"]):cert(c);oldroots+=1
  geo=iv(seg["length_BU"]);length=iv(g["modeled_length_interval_BU"])
  assert g["captured_geometric_first_length_BU"]==seg["length_BU"]
  assert F(*g["conditional_graph_vs_geometric_allowance_BU"])==max(abs(length[0]-geo[1]),abs(length[1]-geo[0]))
  fixed_bounds[g["case"]+"/"+g["source_id"]]=[str(v)for v in g["conditional_graph_vs_geometric_allowance_BU"]]
 graphs+=1
 a=[iv(v)for v in g["source_box_BU"]];b=[iv(v)for v in g["previous_P_box_BU"]]
 ds=[out(y[0]-x[1],y[1]-x[0])for x,y in zip(a,b)]
 assert [list(v)for v in ds]==[list(iv(v))for v in g["difference_intervals_BU"]]
 ss=[out(F(0)if l<=0<=h else min(l*l,h*h),max(l*l,h*h))for l,h in ds]
 assert ss==[iv(v)for v in g["squared_intervals_BU2"]]
 xy=out(ss[0][0]+ss[1][0],ss[0][1]+ss[1][1]);q=out(xy[0]+ss[2][0],xy[1]+ss[2][1])
 assert xy==iv(g["add_xy_interval_BU2"])and q==iv(g["radicand_interval_BU2"])
 low,high=g["root_lower_certificate"],g["root_upper_certificate"]
 assert cert(low)==q[0]and cert(high)==q[1];newroots+=2
 length=iv(g["modeled_length_interval_BU"])
 assert length==out(F(*low["lower_BU"]),F(*high["upper_BU"]))
 assert F(*g["modeled_length_width_BU"])==length[1]-length[0]
 assert g["costs"]==dict(new_integer_root_certificates=2,new_modeled_scalar_operations=9)
 assert g["candidate_cycles_replaced"]is False and g["phase_budget_transferred"]is False
 # Independent exact RN ties-even simulations of corners plus zero where present.
 axes=[sorted(set((l,h)+( (F(0),)if l<=0<=h else () )))for l,h in a+b]
 for pt in itertools.product(*axes):
  d=[rn(y-x)for x,y in zip(pt[:3],pt[3:])]
  squares=[rn(v*v)for v in d]
  xys=rn(squares[0]+squares[1]);rad=rn(xys+squares[2]);root=sqrt_rn(rad)
  assert all(l<=v<=h for(l,h),v in zip(ds,d))
  assert all(l<=v<=h for(l,h),v in zip(ss,squares))
  assert xy[0]<=xys<=xy[1]and q[0]<=rad<=q[1]and length[0]<=root<=length[1]
  samples+=1
assert (graphs,newroots,oldroots,stops,bindings)==(17,34,16,20,28)
print(json.dumps(dict(status="PASS",new_graphs_verified=graphs,new_root_certificates_verified=newroots,
 captured_old_root_certificates_verified_no_replay=oldroots,exact_RN_corner_zero_simulations=samples,
 retained_upstream_STOP=stops,SOURCE_context_bindings=bindings,frozen_pins_verified=461,
 fixed_conditional_allowances_BU_decimal_integer_strings=fixed_bounds,
 native_precision_certified=False,GPU_used=False,full_costs="UNKNOWN_NOT_ZERO"),sort_keys=True))

