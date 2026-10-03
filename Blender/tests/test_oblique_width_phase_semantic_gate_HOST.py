"""Independent metadata/AST oracle; never calls frozen numerical producers."""
from pathlib import Path
import sys,json,hashlib,ast,copy,base64,zlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import oblique_width_phase_semantic_gate_HOST_v1 as c
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-WIDTH-CONSUMER-CPU-001-CODEX.json"
PSHA="b9f8380cba629c5e4a6d5c120df89f087f2e5a717293d26500f97b2f7329c2ae"
CONTRACTS=[{"constants":{"INTENT":"VERTEX3_MINUS_END_GEOMETRIC_ONLY_NO_TOTAL_PHASE","MODEL":"precision-position-box-wavelength-budget-HOST-v1","PARENT":"coordinacion/respuestas/PRECISION-POSITION-PAIR-LENGTH-BOX-BUDGET-HOST-001-CODEX.json","PSHA":"0682fb6c82dcf1d6a20fedcd077c704be8b4d3f9c87881b710a3430c7f235022","REP":"CONDITIONAL_GEOMETRIC_TURNS_DECLARED_SOURCE_WAVELENGTH"},"doc":"Docs/EXP-005-PRECISION-POSITION-BOX-WAVELENGTH-BUDGET-HOST-001.md","doc_bytes":4279,"doc_sha":"f516fad1149d1ad5005dd9adf069775a33c9ade2a133c19e6d90a8163ef4151c","source":"Blender/benchmarks/capacity_audit/position_box_wavelength_budget_HOST_v1.py","source_bytes":5804,"source_sha":"528e2d70335306334d986c39148feccf69b10c79bc5e0bc89f2d38c82e78d1bd"},{"constants":{"INTENT":"CPU_NATIVE_TOTAL_PHASE_ONLY","MODEL":"precision-oblique-total-phase-pair64-CPU-v1","PARENT":"coordinacion/respuestas/PRECISION-OBLIQUE-SOURCE-MATERIAL-INTERVAL-HOST-001-CODEX.json","PSHA":"f7a5f99aa2d2f18d68b01ab9c4afe4b1db85bc78c7a6a9228809b3066e46a05b","REP":"TOTAL_DECLARED_PHASE_PAIR64_CPU_NOT_GPU_ABI"},"doc":"Docs/EXP-005-PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-CPU-001.md","doc_bytes":5380,"doc_sha":"2a142c949c53e5f582ff171498e3b4244b3b12864930cd8f3c8c85aa1a5b56b7","source":"Blender/benchmarks/capacity_audit/oblique_total_phase_pair64_CPU_v1.py","source_bytes":10363,"source_sha":"901a13357f36e4c37ebda32d4223c4e9d89516d868e42bf82e62635fdd54193d"},{"constants":{"INTENT":"ALL16_BYTES_THEN_CHARGED_SUM_COEFFICIENTS_HORNER26_NO_FMA","MODEL":"precision-position-phase-reference-unit-native-CPU-v1","PARENT":"coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-UNIT-BUDGET-HOST-001-CODEX.json","PSHA":"f83bd046776cafcf3fd7db70aa11978ce6e1e7119fe80fc79c513fbf912d6002","REP":"PARTIAL_CPU_RN64_RELATIVE_UNIT_EXPLICIT_CHARGED_SCALAR_NOT_PHYSICAL"},"doc":"Docs/EXP-005-PRECISION-POSITION-PHASE-REFERENCE-UNIT-NATIVE-CPU-001.md","doc_bytes":4592,"doc_sha":"b994dc3d2193f02f16e8330e0342dfe9d3abe79b34d7141de529f6920de2422f","source":"Blender/benchmarks/capacity_audit/position_phase_reference_unit_native_CPU_v1.py","source_bytes":8824,"source_sha":"74696907b72872998ad51606792aca82ec63b5733b2df3ee9a087ec42581f912"}]
ROLES=("VERTEX3_MINUS_END_BU","TWO_SOURCE_TOTAL_PHASE_CYCLES","RELATIVE_ANGLE_RADIANS")
REASONS=("WIDTH_IS_NOT_VERTEX3_MINUS_END","WIDTH_IS_NOT_TWO_SOURCE_TOTAL_PHASE","WIDTH_IS_NOT_RELATIVE_RADIANS")


def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()


def capture(a):
    b=zlib.decompress(base64.b64decode(a["stdout_zlib_base64"],validate=True))
    assert a["rc"]==0 and not a["timed_out"]and len(b)==a["stdout_bytes"]and hashlib.sha256(b).hexdigest()==a["stdout_sha256"]
    return json.loads(b)


def retained():
    b=(ROOT/PARENT).read_bytes();assert len(b)==163556 and hashlib.sha256(b).hexdigest()==PSHA
    r=json.loads(b);pins=dict(r["code_doc_sha256"]);assert len(pins)==315
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert capture(r["independent_pre"])["status"]=="PASS"
    records={x["id"]:x for x in capture(r["test_run"])["evidence"]["records"]}
    pins[PARENT]=PSHA
    for s in CONTRACTS:
        for a,h,n in (("source","source_sha","source_bytes"),("doc","doc_sha","doc_bytes")):
            b=(ROOT/s[a]).read_bytes();assert len(b)==s[n]and hashlib.sha256(b).hexdigest()==s[h]
            pins[s[a]]=s[h]
    return records,pins


def verify(d):
    records,pins=retained();assert d["pins"]==pins
    assert len(d["facts"])==3 and len(d["runs"])==48
    for i,f in enumerate(d["facts"]):
        assert f["spec"]==CONTRACTS[i]and f["expected_role"]==ROLES[i]and f["reason"]==REASONS[i]
        assert f["scope"]=="STATIC_SOURCE_CONTRACT_NOT_RUNTIME_OR_ADAPTER"
        text=(ROOT/f["spec"]["source"]).read_text(encoding="utf-8");tree=ast.parse(text);v={}
        for n in tree.body:
            if isinstance(n,ast.Assign):
                for t in n.targets:
                    if isinstance(t,ast.Name)and t.id in f["spec"]["constants"]:
                        v[t.id]=ast.literal_eval(n.value)
        if "INTENT"not in v:
            func=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=="selector")
            v["INTENT"]=next(ast.literal_eval(n.value)for n in ast.walk(func)if isinstance(n,ast.keyword)and n.arg=="intent")
        assert v==f["spec"]["constants"]
        assert len(f["anchors"])==3
        for a in f["anchors"]:
            matches=[dict(line=j+1,text=line)for j,line in enumerate(text.splitlines())if a["token"]in line]
            assert a["matches"]==matches and matches
    seen=set();eligible=stops=0
    def scope(r):
        assert r["phase_error_bound"]is None and r["phase_output"]is None
        for k in ("phase_certified","wavelength_known","physical_reference_certified","scene_engine_admitted",
                  "GPU_used","Bpy_used","foreign_modules_executed"):assert r[k]is False
        for k in ("new_RN","new_products","new_sqrt_calls","new_float_decodes","new_hex_decodes","retained_numeric_replays"):assert r[k]==0
        assert r["full_costs"]=="UNKNOWN_NOT_ZERO"
        assert r["promotion"]=="STOP_WIDTH_TO_PHASE_WITHOUT_SAME_SCENE_CONTRACT_AND_PHYSICAL_EVIDENCE"
    for a in d["runs"]:
        k,t=a["record_id"],a["target"];assert k in records and type(t)is int and 0<=t<3
        assert (k,t)not in seen;seen.add((k,t));x=records[k];q=a["request"];r=a["result"];scope(r)
        expected=dict(model=c.MODEL,record_id=k,target_model=CONTRACTS[t]["constants"]["MODEL"],
            parent_receipt_sha256=PSHA,width_record_sha256=digest(x),
            original_snapshot_sha256=x["request"]["original_snapshot_sha256"],
            original_query_sha256=x["request"]["original_query_sha256"],target_contract_sha256=digest(d["facts"][t]),
            intent="AUDIT_WIDTH_AS_PHASE_INPUT_NO_NUMERIC_EXECUTION")
        assert q==expected and r["upstream_status"]==x["result"]["status"]
        if x["result"]["status"]!="CPU64_SCENE_PAIR_WIDTH_HOST_BOUND_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"
            assert r["diagnostic"]is None and r["semantic_checks"]==0;stops+=1;continue
        assert r["status"]=="STOP_PHASE_SEMANTIC_JOIN"and r["reason"]==REASONS[t]and r["semantic_checks"]==1
        z=r["diagnostic"];assert z["contract"]==d["facts"][t]and z["target_role"]==ROLES[t]
        assert z["width_record_sha256"]==digest(x)and z["target_contract_sha256"]==digest(d["facts"][t])
        for k2 in ("original_snapshot_sha256","original_query_sha256"):assert z[k2]==q[k2]
        assert z["source_uncertainty_cancelled"]is False and z["retained_width_status"]==x["result"]["status"]
        assert z["evidence_scope"]=="STATIC_INCOMPATIBILITY_ONLY_NOT_PROOF_TARGET_RUNTIME_REJECTION"
        expected_offer=dict(role="ORIGINAL_LENGTH_BOUND_WIDTH",units="scene_length",pair_bytes=16,
            word_type="IEEE754_BINARY64",source="SOURCE0",detector="DETECTOR0",
            original_snapshot_sha256=q["original_snapshot_sha256"],phase_certified=False,
            wavelength_known=False,physical_reference_certified=False)
        assert z["offered"]==a["offered"]==expected_offer and set(z["offered"])==set(expected_offer)
        assert all(type(z["offered"][key])is type(value)for key,value in expected_offer.items())
        assert z["unresolved_same_scene_obligations"]==[
            "WIDTH_VS_PATH_REFERENCE_DIFFERENCE_DEFINITION",
            "SOURCE_WAVELENGTH_INTERVAL_AND_SCENE_UNIT_SCALE",
            "SOURCE_REFERENCE_PHASE_GAUGE_AND_MATERIAL",
            "ALL_REQUIRED_SOURCE_VISIBILITY_COMPLETENESS",
            "ORIGINAL_PHASE_CAP_AND_FULL_ERROR_COMPOSITION",
            "SCENE_WAVELENGTH_REFERENCE_AUTHENTICATION",
            "REAL_BACKEND_GUARD_SAME_WORK_OUTPUTS_FULL_COSTS"]
        assert z["offered"]["units"]=="scene_length"and type(z["offered"]["pair_bytes"])is int and z["offered"]["pair_bytes"]==16
        assert z["offered"]["source"]=="SOURCE0"and z["offered"]["detector"]=="DETECTOR0"
        assert z["offered"]["original_snapshot_sha256"]==q["original_snapshot_sha256"]
        eligible+=1
    assert (eligible,stops)==(6,42)
    assert len(d["invalid"])==len(d["aliases"])==8
    for group,reason in ((d["invalid"],"closed_selector"),(d["aliases"],"semantic_offer_NO_ALIAS_OR_CERT_INJECTION")):
        for a in group:
            scope(a["result"]);assert a["result"]["status"]=="STOP_INPUT"and a["result"]["reason"]==reason
            assert a["result"]["diagnostic"]is None and a["result"]["semantic_checks"]==0
    return dict(status="PASS",inherited_pins=len(pins),targets=3,distinct_scenes=16,width_eligible_scenes=2,
        eligible_semantic_joins_STOP=eligible,upstream_joins_STOP=stops,selector_rejections=8,semantic_alias_rejections=8,
        semantic_checks=6,new_RN=0,new_float_decodes=0,new_hex_decodes=0,retained_numeric_replays=0,
        phase_certified=False,full_costs="UNKNOWN_NOT_ZERO",runtime_adapter_tested=False)


def mutations(d):
    chosen=next(i for i,x in enumerate(d["runs"])if x["result"]["diagnostic"]is not None);count=0
    for i in range(8):
        a=copy.deepcopy(d);r=a["runs"][chosen]["result"];z=r["diagnostic"]
        if i==0:r["status"]="PASS_PHASE"
        elif i==1:r["phase_error_bound"]=[0,1]
        elif i==2:z["offered"]["units"]="rad"
        elif i==3:r["foreign_modules_executed"]=True
        elif i==4:z["source_uncertainty_cancelled"]=True
        elif i==5:a["facts"][0]["spec"]["constants"]["REP"]="ALIAS_WIDTH"
        elif i==6:z["contract"]["anchors"][0]["matches"][0]["line"]=0
        else:r["new_float_decodes"]=1
        try:verify(a)
        except (AssertionError,KeyError,TypeError,IndexError,ValueError):count+=1
        else:raise AssertionError("mutation_accepted:"+str(i))
    assert count==8;return count


def run():
    records,fs,pins=c.retained();runs=[]
    for k in records:
        for t in range(3):
            q=c.selector(k,t,records,fs);offer=c.offered(k,records)
            runs.append(dict(record_id=k,target=t,request=q,offered=offer,result=c._audit(q,offer,records,fs)))
    base=next(x for x in runs if x["result"]["diagnostic"]is not None)
    invalid=[]
    for key in ("model","parent_receipt_sha256","width_record_sha256","original_snapshot_sha256",
                "original_query_sha256","target_contract_sha256","intent","extra_key"):
        q=dict(base["request"]);q[key]="UNSEALED"
        invalid.append(dict(request=q,result=c._audit(q,base["offered"],records,fs)))
    aliases=[]
    changes=(("units","rad"),("role","TOTAL_PHASE"),("pair_bytes",8),("phase_certified",True),
             ("wavelength_BU",[1,1]),("source","SOURCE1"),("detector","DETECTOR1"),("original_snapshot_sha256","0"*64))
    for key,value in changes:
        offer=dict(base["offered"]);offer[key]=value
        aliases.append(dict(offered=offer,result=c._audit(base["request"],offer,records,fs)))
    d=dict(facts=fs,pins=pins,runs=runs,invalid=invalid,aliases=aliases)
    s=verify(d);s["mutations_rejected"]=mutations(d)
    print(json.dumps(dict(status="PASS",summary=s,evidence=d),sort_keys=True,separators=(",",":")))


if __name__=="__main__":run()
