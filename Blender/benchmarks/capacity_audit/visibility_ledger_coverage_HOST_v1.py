"""Exact ledger-grid coverage; proposed matching rows remain HOST UNATTESTED."""
from pathlib import Path
import base64,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-visibility-ledger-coverage-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SEGMENT-VISIBILITY-CPU-001-CODEX.json"
PSHA="caeb7f11a25812dee86041a10b74f68adf7330d2a40724258bf71c15f25f19f5"
INTENT="HOST_UNATTESTED_VISIBILITY_LEDGER_ONLY"
FIELDS={"source_id","segment","primitive_id","t","barycentric","classification"}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def cap(t):
    b=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    need(t["rc"]==0 and not t["timed_out"]and len(b)==t["stdout_bytes"]and sha(b)==t["stdout_sha256"],"capture_integrity")
    return json.loads(b)
def load_evidence():
    b=(ROOT/PARENT).read_bytes();need(sha(b)==PSHA,"parent_identity");r=json.loads(b)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin")
    need(cap(r["independent_pre"])["status"]=="PASS","parent_independent_capture")
    return {run["id"]:run for run in cap(r["test_run"])["runs"]}
def selector(case):return dict(case=case,receipt_sha256=PSHA,intent=INTENT)
def baseline():
    return dict(model=MODEL,status="STOP",reason=None,verified_rows=0,expected_rows=None,
        expected_grid_sha256=None,proposed_rows_sha256=None,source_segment_counts=None,
        promotion="STOP",ledger_authenticated=False,scene_authenticated=False,
        GPU_launch_allowed=False,GPU_executed=False,physical_field_certified=False,
        producer_replays=0,RN64_operations=0,compiler_calls=0,full_costs="UNMEASURED_NOT_ZERO")
def keys(rows):
    need(type(rows)is list and len(rows)<=16,"bounded_ledger_list")
    result=[]
    for row in rows:
        need(type(row)is dict and set(row)==FIELDS,"closed_row")
        need(type(row["source_id"])is str and row["source_id"]in("S0","S1"),"typed_SOURCE")
        need(type(row["segment"])is int and row["segment"]in(0,1),"typed_segment")
        need(type(row["primitive_id"])is int and 0<=row["primitive_id"]<2**31,"typed_primitive")
        result.append((row["source_id"],row["segment"],row["primitive_id"]))
    return result
def _validate(model,request,ledger,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"model")
        need(type(request)is dict and set(request)=={"case","receipt_sha256","intent"},"closed_selector")
        need(type(request["case"])is str and request==selector(request["case"]),"selector_identity")
        need(request["case"]in e,"case");run=e[request["case"]];r=run["result"]
        need(r["status"]=="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY","parent_STOP:"+str(r["reason"]))
        ids=[tr["primitive_id"]for tr in run["scene"]["triangles"]]
        need(2<=len(ids)<=4 and all(type(v)is int for v in ids)and len(set(ids))==len(ids),"sealed_primitive_grid")
        grid=[(s,j,pid)for s in("S0","S1")for j in(0,1)for pid in ids]
        sealed=r["visibility_rows"]
        need(keys(sealed)==grid and r["diagnostics"]==sealed and r["SOURCE_segments_admitted"]==4,"sealed_exact_grid")
        out.update(expected_rows=len(grid),expected_grid_sha256=sha(canonical(grid)))
        proposed=keys(ledger)
        need(len(proposed)==len(grid),"ALL_rows_count")
        need(len(set(proposed))==len(grid),"unique_SOURCE_segment_primitive")
        need(set(proposed)==set(grid),"complete_SOURCE_segment_primitive")
        need(proposed==grid,"ordered_SOURCE_segment_primitive")
        out["proposed_rows_sha256"]=sha(canonical(ledger))
        need(canonical(ledger)==canonical(sealed),"sealed_numeric_rows_exact")
        out.update(status="HOST_UNATTESTED_VISIBILITY_LEDGER_MATCH",verified_rows=len(grid),
            source_segment_counts={s:[sum(a==s and b==j for a,b,pid in proposed)for j in(0,1)]for s in("S0","S1")})
    except(ValueError,KeyError,TypeError,IndexError)as ex:out["reason"]=str(ex)
    return out
def validate(model,request,ledger):
    try:e=load_evidence()
    except(ValueError,KeyError,TypeError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _validate(model,request,ledger,e)
