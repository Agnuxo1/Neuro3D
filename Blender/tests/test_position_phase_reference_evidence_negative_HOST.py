"""Negative evidence regression, no old producers or native scene tests."""
import copy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_phase_reference_evidence_negative_HOST_v1 as m

def main():
    ctx=m.retained();original_rows={k:m.digest(x)for k,x in ctx["rows"].items()};v=m.variants(ctx);runs=[]
    for i,x in enumerate(v["controls"]):
        for strict in(False,True):
            out=m.evaluate(x,ctx,strict=strict);assert out["verdict"]=="ACCEPTED_HOST_EVIDENCE_ONLY"
            runs.append(dict(label="control:"+str(i),base_sha256=m.digest(x),record_sha256=m.digest(x),result=out))
    expected_aliases={"bool_zero_rational","float_word_count","float_zero_rational","bool_reference_point",
                      "bool_positive_sign","extra_trace_metadata","extra_result_claim"}
    for x in v["mutations"]:
        for strict in(False,True):
            out=m.evaluate(x["record"],ctx,strict=strict)
            want="REJECTED" if strict or x["label"]not in expected_aliases else "ACCEPTED_HOST_EVIDENCE_ONLY"
            assert out["verdict"]==want,(x["label"],strict,out)
            runs.append(dict(label=x["label"],base_id=x["base_id"],base_sha256=x["base_sha256"],
                record_sha256=m.digest(x["record"]),result=out))
    assert len(v["mutations"])==26 and len(runs)==56
    assert set(x["label"]for x in runs if not x["result"]["strict"] and x["result"]["verdict"]=="ACCEPTED_HOST_EVIDENCE_ONLY"
               and not x["label"].startswith("control:"))==expected_aliases
    assert all(x["result"]["verdict"]=="REJECTED"for x in runs if x["result"]["strict"]and not x["label"].startswith("control:"))
    assert all(x["result"]["GPU_executed"]is False and x["result"]["CPU_native_executed"]is False
               and x["result"]["producer_replays"]==x["result"]["parent_suites_replayed"]==0
               and x["result"]["promotion"]=="STOP" for x in runs)
    assert original_rows=={k:m.digest(x)for k,x in ctx["rows"].items()}
    # Output retains mutated copies and both verdicts; no hidden replacement of old acceptances.
    print(json.dumps(dict(status="PASS",scope="HOST_NEGATIVE_EVIDENCE_ONLY_NOT_GPU_AUTHENTICATION",
        census=dict(main=56,controls=4,mutations=26,frozen_semantic_rejections=19,frozen_type_metadata_acceptances=7,
                    strict_rejections=26,old_records_replayed=0,parent_suites_replayed=0,CPU_native_calls=0,GPU_calls=0),
        data=dict(runs=runs,variants=v,source_sha256=ctx["source_sha256"],extracted_definitions=ctx["extracted_definitions"],
                  pins=len(ctx["pins"])),full_costs="UNMEASURED_NOT_ZERO"),sort_keys=True))
if __name__=="__main__":main()
