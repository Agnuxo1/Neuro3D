"""Independent receipt arithmetic, no adapter/producers imported."""
import base64
from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import zlib

ROOT = Path("D:/PROJECTS/9_NEBULA_NEW")
ID = "PRECISION-ORIGINAL-SOURCE-CANDIDATE-TOTAL-PHASE-HOST-001"
def sha(b): return hashlib.sha256(b).hexdigest()
def dg(v): return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def read(name): return json.loads((ROOT/"coordinacion/respuestas"/name).read_bytes())
def captured(r):
    t=r["test_run"]
    assert type(t["rc"]) is int and t["rc"]==0 and t.get("timed_out",False) is False
    if "before_deadline" in t: assert t["before_deadline"] is True
    raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
    d=json.loads(raw); assert d["status"]=="PASS"
    return d
r=read(ID+"-CODEX.json")
for p,h in r["code_doc_sha256"].items(): assert sha((ROOT/p).read_bytes())==h
d=captured(r)
parent_names={
"PRECISION-ORIGINAL-SOURCE-CANDIDATE-PATH-CYCLES-HOST-001-CODEX.json":"53b739dcaaf08e2bbce9ca81ce7a24b98bc53074357720a4bc9aaaf317aae1fe",
"PRECISION-OBLIQUE-SOURCE-MATERIAL-INTERVAL-HOST-001-CODEX.json":"f7a5f99aa2d2f18d68b01ab9c4afe4b1db85bc78c7a6a9228809b3066e46a05b",
"PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json":"139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"}
pdat={}
for name,h in parent_names.items():
    raw=(ROOT/"coordinacion/respuestas"/name).read_bytes(); assert sha(raw)==h
    pdat[name]=captured(json.loads(raw))
cd=pdat[next(n for n in pdat if "CANDIDATE-PATH-CYCLES" in n)]
old=pdat[next(n for n in pdat if "SOURCE-MATERIAL-INTERVAL" in n)]["data"]["runs"]
geom=pdat[next(n for n in pdat if "COMMON-DETECTOR-LENGTH" in n)]["data"]["inputs"]
candidate=[x["result"] for x in cd["records"] if x["kind"]=="FIXED_PATH_OR_STOP"]
assert len(candidate)==28 and sum(x["cycles_interval"] is not None for x in candidate)==8
fixed=[x for x in d["records"] if x["kind"]=="FIXED_JOIN"]
assert len(fixed)==8
statuses=Counter(); corners=0; ratios={}
for run in fixed:
    out=run["result"]; statuses[out["status"]]+=1
    assert out["promotion"]=="STOP" and out["phase_certified"] is False
    assert out["GPU_launch_allowed"] is False and out["native_phase_error_bound"] is None
    assert out["original_scene_phase_status"]=="UNKNOWN_NOT_ZERO"
    if run["mode"]=="ORIGINAL_UNKNOWN":
        assert out["status"]=="STOP_ORIGINAL_PHASE_UNKNOWN" and out["rows"]==[] and out["diagnostics"]==[]
        continue
    case=run["case"]; query=geom[case]["request"]
    rows=sorted([x for x in candidate if x["case"]==case and x["cycles_interval"] is not None],key=lambda x:x["source_id"])
    assert out["SOURCE_row_sha256s"]==[dg(x) for x in rows]
    overlay=next(x["request"] for x in old if x["id"]=="parent_"+case)
    assert out["overlay_sha256"]==dg(overlay)
    assert out["query_sha256"]==dg(query)
    p=[[F(*v) for v in x["cycles_interval"]] for x in rows]
    g=[[F(*v) for v in x["phase_interval_cycles"]] for x in overlay["sources"]]
    mu=[F(*v) for v in overlay["material"]["phase_interval_cycles"]]
    endpoints=[]
    for j in range(2):
        vals=[a+b+c for a,b,c in itertools.product(p[j],g[j],mu)]
        corners+=len(vals); endpoints.append([min(vals),max(vals)])
    vals=[a-b+c-dd for a,b,c,dd in itertools.product(*p,*g)]
    corners+=len(vals); endpoints.append([min(vals),max(vals)])
    caps=[F(*v) for v in (*query["source_width_caps_rad"],query["relative_width_cap_rad"])]
    for iv,cap,diag in zip(endpoints,caps,out["diagnostics"]):
        assert [F(*v) for v in diag["interval_cycles"]]==iv
        assert F(*diag["HOST_midpoint_cycles"])==sum(iv)/2
        bound=4*(iv[1]-iv[0])
        assert F(*diag["conditional_HOST_radius_bound_rad"])==bound
        assert F(*diag["literal_cap_rad"])==cap and diag["fits"]==(bound<=cap)
    assert out["old_ideal_relative_interval_used"] is False
    if case=="tiny_gap_2m60":
        assert all(x["fits"] for x in out["diagnostics"]) and len(out["rows"])==3
    else:
        assert not any(x["fits"] for x in out["diagnostics"][:2]) and out["rows"]==[]
    q=4*(p[0][1]-p[0][0])/caps[0]
    ratios[case]=[q.numerator,q.denominator]
for rec in d["records"]:
    if rec["kind"] in ("INPUT_NEG","OUTPUT_CAPACITY512_STOP"):
        assert rec["result"]["status"]=="STOP_INPUT" and rec["result"]["rows"]==[]
    if rec["kind"]=="COMMON_MATERIAL_ALL_SOURCE_STOP":
        o=rec["result"]; assert o["rows"]==[] and o["diagnostics"][2]["fits"] is True
    if rec["kind"]=="INCLUSIVE_SOURCE_CAP_RELATIVE_STOP":
        o=rec["result"]; assert o["status"]=="STOP_RELATIVE_DIAGNOSTIC_CAP"
        assert o["rows"]==[] and all(x["fits"] for x in o["diagnostics"][:2])
pin_name="GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json"
raw=(ROOT/"coordinacion/respuestas"/pin_name).read_bytes()
assert sha(raw)=="172576dd8a38cf8119f2a1a3d229b534a7e77fdbde2632e2ef967b10e2d6e9f4"
c=json.loads(raw)["pinned_manifest_capture"]
raw=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"]))
assert sha(raw)==c["stdout_sha256"]
pins=json.loads(raw)["pins"]; assert len(pins)==461
for p,h in pins.items(): assert sha((ROOT/p).read_bytes())==h
counts=Counter(x["kind"] for x in d["records"])
print(json.dumps(dict(id=ID,status="PASS",tests=d["tests"],records=len(d["records"]),groups=dict(counts),
fixed_statuses=dict(statuses),new_total_phase_corner_combinations=corners,
SOURCE_HOST_radius_to_literal_cap_ratios=ratios,pinned_files_intact=len(pins),
candidate_rows=28,upstream_STOP_preserved=20,old_geometry_queries=0,
root_evaluations=0,frozen_producer_replays=0,GPU_used=False,phase_certified=False),sort_keys=True))
