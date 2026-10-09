"""Read emitted CPU words by integer IEEE decoding; no normalization replay."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
r=json.loads(Path("coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-NORMALIZATION-CPU64-001-CODEX.json").read_bytes())
for path,pin in r["pins"].items():
 raw=Path(path).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==pin["sha256"] and len(raw)==pin["bytes"],path
def payload(c):
 raw=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"]))
 assert hashlib.sha256(raw).hexdigest()==c["stdout_sha256"] and len(raw)==c["stdout_bytes"]
 assert c["rc"]==0 and not c["timed_out"]
 return json.loads(raw)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def decode(w):
 assert len(w)==16 and all(c in "0123456789abcdef" for c in w)
 b=int(w,16); sign=-1 if b>>63 else 1; e=(b>>52)&2047; f=b&((1<<52)-1)
 assert e!=2047
 if e==0: return sign*F(f)*F(2)**(-1074)
 return sign*F((1<<52)+f)*F(2)**(e-1023-52)
qa=payload(r["test_run"])
assert qa["status"]=="PASS" and qa["tests"]==3 and len(qa["records"])==20
lit=json.loads(Path("coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json").read_bytes())
inputs=payload(lit["test_run"])["data"]["inputs"]
rows=[x for x in qa["records"] if x["kind"]=="CPU64_SOURCE_WORD_CAPTURE"]
assert len(rows)==8
defects=set()
for case in ("oblique","direction_scaled","shared_ref1000","tiny_gap_2m60"):
 item=inputs[case]
 records=[x for x in rows if x["case"]==case]
 assert [x["source_id"] for x in records]==["S0","S1"]
 assert digest(item["scene"])==item["request"]["original_scene_sha256"]
 for row,s in zip(records,item["scene"]["sources"],strict=True):
  assert row["scene_sha256"]==digest(item["scene"]) and row["query_sha256"]==digest(item["request"])
  p=list(map(decode,row["position_words_hex"]));d=list(map(decode,row["direction_input_words_hex"]))
  assert p==[F(*v) for v in s["position_BU"]] and d==[F(*v) for v in s["direction"]]
  graph={k:decode(v) for k,v in row["scalar_graph_words_hex"].items()}
  assert graph["xx"]==d[0]**2 and graph["yy"]==d[1]**2 and graph["zz"]==d[2]**2
  assert graph["xy"]==graph["xx"]+graph["yy"] and graph["squared"]==graph["xy"]+graph["zz"]
  assert graph["sqrt"]>0 and graph["sqrt"]**2!=graph["squared"]
  unit=list(map(decode,row["normalized_direction_words_hex"]))
  assert unit[0]==unit[1]>0 and unit[2]==0
  delta=F(1)-sum(u*u for u in unit)
  assert delta!=0 and F(*map(int,row["one_minus_exact_word_norm_squared"]))==delta
  defects.add(str(delta))
  assert row["SOURCE_position_input_loss_BU"]==["0","1"]
scopes=[x for x in qa["records"] if x["kind"]=="CASE_SCOPE"]
assert len(scopes)==4 and sum(x["root_calls"] for x in scopes)==8
for x in scopes:
 assert not x["GPU_used"] and not x["native_GPU_precision_certified"] and x["native_phase_bound_rad"] is None
 assert not x["original_pointwise_budget_certified"] and not x["current_GPU_admission"]
 assert x["ideal_direction_error_bound"] is None and x["runtime"]["implementation"]=="cpython"
stops=[x for x in qa["records"] if x["kind"].endswith("STOP")]
assert len(stops)==8
assert all(x["status"]=="STOP" and x["records"]==[] and x["root_calls"]==0 for x in stops)
manifest=payload(json.loads(Path("coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json").read_bytes())["pinned_manifest_capture"])
assert len(manifest["pins"])==461
for path,h in manifest["pins"].items(): assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
print(json.dumps(dict(status="PASS",word_rows=8,exact_nonzero_defects=sorted(defects),
 input_pins=len(r["pins"]),frozen_pins=461,negative_preflight_no_roots=8,
 sqrt_calls_replayed=0,normalization_replayed=False,native_phase_certified=False,GPU_used=False)))
