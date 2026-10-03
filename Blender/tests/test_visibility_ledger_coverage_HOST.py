"""Mutation witnesses for missing coverage, with legacy block frozen and explicit."""
from pathlib import Path
import copy,importlib.util,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks/capacity_audit"))
import visibility_ledger_coverage_HOST_v1 as m
def run():
    e=m.load_evidence();runs=[];witnesses=[]
    op=Path(__file__).with_name("verify_oblique_segment_visibility_CPU.py")
    spec=importlib.util.spec_from_file_location("frozen_row_reader",op);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    # Use only old row_check and the old admitted-row block. Never main(), cap override, file write or producer.
    for case,entry in e.items():
        actual=entry["result"];ledger=copy.deepcopy(actual["visibility_rows"])
        result=m.validate(m.MODEL,m.selector(case),ledger)if case=="oblique"else m._validate(m.MODEL,m.selector(case),ledger,e)
        expected="STOP"if actual["status"]=="STOP"else"HOST_UNATTESTED_VISIBILITY_LEDGER_MATCH"
        assert result["status"]==expected
        if expected=="STOP":assert result["verified_rows"]==0 and result["reason"]=="parent_STOP:"+str(actual["reason"])
        runs.append(dict(id=case+"/sealed",case=case,ledger=ledger,result=result))
        if expected=="STOP":continue
        first=next(i for i,row in enumerate(ledger)if row["source_id"]=="S0"and row["segment"]==1 and row["classification"]=="EXPECTED_ENDPOINT")
        missing=next(i for i,row in enumerate(ledger)if row["source_id"]=="S1"and row["segment"]==1 and row["classification"]=="EXPECTED_ENDPOINT")
        mutated=copy.deepcopy(ledger);mutated[missing]=copy.deepcopy(mutated[first])
        for row in mutated:old.row_check(entry,row)
        assert len(mutated)==4*len(entry["scene"]["triangles"])
        assert sum(row["classification"]=="EXPECTED_ENDPOINT"for row in mutated)==4
        assert sum(row["classification"]=="EXACT_PREVIOUS_ZERO"for row in mutated)==2
        assert len({(row["source_id"],row["segment"],row["primitive_id"])for row in mutated})==len(mutated)-1
        witnesses.append(dict(case=case,label="LEGACY_ADMITTED_ROW_BLOCK_ACCEPTED_COUNTEREXAMPLE",
            scope="FROZEN_PER_ROW_NUMERICS_PLUS_COUNTS_NOT_FULL_RECEIPT_ORACLE_OR_CORE",
            legacy_sufficiency="FAIL",rows=mutated,unique_keys=len(mutated)-1,total_rows=len(mutated),
            missing_key=[ledger[missing][k]for k in("source_id","segment","primitive_id")],
            duplicated_key=[ledger[first][k]for k in("source_id","segment","primitive_id")]))
        for kind in("duplicate_omit_SOURCE1","remove_row","reverse_rows","wrong_primitive","wrong_t","scaled_denominator","bool_segment","extra_field","empty","dict_not_list"):
            rows=copy.deepcopy(ledger)
            if kind=="duplicate_omit_SOURCE1":rows=mutated
            if kind=="remove_row":rows.pop()
            if kind=="reverse_rows":rows.reverse()
            if kind=="wrong_primitive":rows[0]["primitive_id"]=99
            if kind=="wrong_t":rows[first]["t"]=[0,1]
            if kind=="scaled_denominator":rows[first]["t"]=[2,2]
            if kind=="bool_segment":rows[0]["segment"]=False
            if kind=="extra_field":rows[0]["epsilon"]=0
            if kind=="empty":rows=[]
            if kind=="dict_not_list":rows={}
            out=m._validate(m.MODEL,m.selector(case),rows,e)
            assert out["status"]=="STOP"and out["verified_rows"]==0,(case,kind,out)
            runs.append(dict(id=case+"/"+kind,case=case,ledger=rows,result=out))
    negatives=[]
    for label,model,q in(("wrong_model","wrong",m.selector("oblique")),
        ("extra_selector",m.MODEL,dict(m.selector("oblique"),override=True)),
        ("stale_selector",m.MODEL,dict(m.selector("oblique"),receipt_sha256="0"*64)),
        ("unknown_case",m.MODEL,m.selector("unknown"))):
        out=m._validate(model,q,[],e);assert out["status"]=="STOP"and out["verified_rows"]==0
        negatives.append(dict(id=label,model=model,request=q,result=out))
    assert len(runs)==104 and len(witnesses)==6 and len(negatives)==4
    for item in runs+negatives:
        out=item["result"]
        assert out["promotion"]=="STOP"and out["ledger_authenticated"]is False and out["GPU_launch_allowed"]is False
        assert out["RN64_operations"]==out["producer_replays"]==out["compiler_calls"]==0
    print(json.dumps(dict(status="PASS",groups=3,runs=runs,selector_negatives=negatives,legacy_witnesses=witnesses,
        census=dict(sealed=44,sealed_matches=6,parent_STOP=38,mutation_STOP=60,selector_STOP=4,
        legacy_sufficiency_FAIL=6,whole_receipt_oracle_tested=False,GPU_launch_allowed=False)),sort_keys=True))
if __name__=="__main__":run()
