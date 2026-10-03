"""Closed HOST semantic gate: sealed geometry WIDTH is not a phase input."""
from pathlib import Path
import ast,json,hashlib,base64,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-width-phase-semantic-gate-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-WIDTH-CONSUMER-CPU-001-CODEX.json"
PSHA="b9f8380cba629c5e4a6d5c120df89f087f2e5a717293d26500f97b2f7329c2ae"
PBYTES=163556
CONTRACTS=[{"constants":{"INTENT":"VERTEX3_MINUS_END_GEOMETRIC_ONLY_NO_TOTAL_PHASE","MODEL":"precision-position-box-wavelength-budget-HOST-v1","PARENT":"coordinacion/respuestas/PRECISION-POSITION-PAIR-LENGTH-BOX-BUDGET-HOST-001-CODEX.json","PSHA":"0682fb6c82dcf1d6a20fedcd077c704be8b4d3f9c87881b710a3430c7f235022","REP":"CONDITIONAL_GEOMETRIC_TURNS_DECLARED_SOURCE_WAVELENGTH"},"doc":"Docs/EXP-005-PRECISION-POSITION-BOX-WAVELENGTH-BUDGET-HOST-001.md","doc_bytes":4279,"doc_sha":"f516fad1149d1ad5005dd9adf069775a33c9ade2a133c19e6d90a8163ef4151c","source":"Blender/benchmarks/capacity_audit/position_box_wavelength_budget_HOST_v1.py","source_bytes":5804,"source_sha":"528e2d70335306334d986c39148feccf69b10c79bc5e0bc89f2d38c82e78d1bd"},{"constants":{"INTENT":"CPU_NATIVE_TOTAL_PHASE_ONLY","MODEL":"precision-oblique-total-phase-pair64-CPU-v1","PARENT":"coordinacion/respuestas/PRECISION-OBLIQUE-SOURCE-MATERIAL-INTERVAL-HOST-001-CODEX.json","PSHA":"f7a5f99aa2d2f18d68b01ab9c4afe4b1db85bc78c7a6a9228809b3066e46a05b","REP":"TOTAL_DECLARED_PHASE_PAIR64_CPU_NOT_GPU_ABI"},"doc":"Docs/EXP-005-PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-CPU-001.md","doc_bytes":5380,"doc_sha":"2a142c949c53e5f582ff171498e3b4244b3b12864930cd8f3c8c85aa1a5b56b7","source":"Blender/benchmarks/capacity_audit/oblique_total_phase_pair64_CPU_v1.py","source_bytes":10363,"source_sha":"901a13357f36e4c37ebda32d4223c4e9d89516d868e42bf82e62635fdd54193d"},{"constants":{"INTENT":"ALL16_BYTES_THEN_CHARGED_SUM_COEFFICIENTS_HORNER26_NO_FMA","MODEL":"precision-position-phase-reference-unit-native-CPU-v1","PARENT":"coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-UNIT-BUDGET-HOST-001-CODEX.json","PSHA":"f83bd046776cafcf3fd7db70aa11978ce6e1e7119fe80fc79c513fbf912d6002","REP":"PARTIAL_CPU_RN64_RELATIVE_UNIT_EXPLICIT_CHARGED_SCALAR_NOT_PHYSICAL"},"doc":"Docs/EXP-005-PRECISION-POSITION-PHASE-REFERENCE-UNIT-NATIVE-CPU-001.md","doc_bytes":4592,"doc_sha":"b994dc3d2193f02f16e8330e0342dfe9d3abe79b34d7141de529f6920de2422f","source":"Blender/benchmarks/capacity_audit/position_phase_reference_unit_native_CPU_v1.py","source_bytes":8824,"source_sha":"74696907b72872998ad51606792aca82ec63b5733b2df3ee9a087ec42581f912"}]
ROLES=("VERTEX3_MINUS_END_BU","TWO_SOURCE_TOTAL_PHASE_CYCLES","RELATIVE_ANGLE_RADIANS")
REASONS=("WIDTH_IS_NOT_VERTEX3_MINUS_END","WIDTH_IS_NOT_TWO_SOURCE_TOTAL_PHASE","WIDTH_IS_NOT_RELATIVE_RADIANS")
ANCHORS=(("difference_interval_BU","wavelength_BU","DECLARED_SOURCE_WAVELENGTH_GEOMETRIC_ONLY"),
         ("phase_interval_cycles","rows[:2]","CPU_NATIVE_TOTAL_PHASE_ONLY"),
         ("typed_16_byte_frame","input_pair_exact_rad_HOST","same_original_phase_budget"))


def need(x,msg):
    if not x:raise ValueError(msg)


def sha(b):return hashlib.sha256(b).hexdigest()


def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())


def capture(c):
    need(c["rc"]==0 and not c["timed_out"],"successful_capture")
    b=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True))
    need(len(b)==c["stdout_bytes"]and sha(b)==c["stdout_sha256"],"capture_seal")
    return json.loads(b)


def facts():
    result=[]
    for i,spec in enumerate(CONTRACTS):
        b=(ROOT/spec["source"]).read_bytes();db=(ROOT/spec["doc"]).read_bytes()
        need(sha(b)==spec["source_sha"]and len(b)==spec["source_bytes"],"source_seal")
        need(sha(db)==spec["doc_sha"]and len(db)==spec["doc_bytes"],"doc_seal")
        text=b.decode("utf-8");tree=ast.parse(text);values={}
        for n in tree.body:
            if isinstance(n,ast.Assign):
                for t in n.targets:
                    if isinstance(t,ast.Name)and t.id in ("MODEL","REP","INTENT","PARENT","PSHA"):
                        values[t.id]=ast.literal_eval(n.value)
        if "INTENT"not in values:
            f=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=="selector")
            values["INTENT"]=next(ast.literal_eval(n.value)for n in ast.walk(f)
                                  if isinstance(n,ast.keyword)and n.arg=="intent")
        need(values==spec["constants"],"AST_contract_literals")
        anchors=[]
        for a in ANCHORS[i]:
            matches=[dict(line=j+1,text=line)for j,line in enumerate(text.splitlines())if a in line]
            need(matches,"source_anchor:"+a);anchors.append(dict(token=a,matches=matches))
        result.append(dict(spec=spec,expected_role=ROLES[i],reason=REASONS[i],anchors=anchors,
                           scope="STATIC_SOURCE_CONTRACT_NOT_RUNTIME_OR_ADAPTER"))
    return result


def retained():
    b=(ROOT/PARENT).read_bytes();need(len(b)==PBYTES and sha(b)==PSHA,"width_parent_seal")
    r=json.loads(b);pins=dict(r["code_doc_sha256"]);need(len(pins)==315,"width_parent_pins")
    for p,h in pins.items():need(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    need(capture(r["independent_pre"])["status"]=="PASS","width_parent_oracle")
    d=capture(r["test_run"]);need(d["status"]=="PASS","width_capture")
    records={x["id"]:x for x in d["evidence"]["records"]}
    need(len(records)==16 and d["summary"]["scene_width_exact"]==2 and d["summary"]["upstream_STOP"]==14,"closed_width_registry")
    fs=facts();pins[PARENT]=PSHA
    for f in fs:
        s=f["spec"];pins[s["source"]]=s["source_sha"];pins[s["doc"]]=s["doc_sha"]
    return records,fs,pins


def selector(k,t,records,fs):
    x=records[k]
    return dict(model=MODEL,record_id=k,target_model=fs[t]["spec"]["constants"]["MODEL"],
        parent_receipt_sha256=PSHA,width_record_sha256=digest(x),
        original_snapshot_sha256=x["request"]["original_snapshot_sha256"],
        original_query_sha256=x["request"]["original_query_sha256"],
        target_contract_sha256=digest(fs[t]),intent="AUDIT_WIDTH_AS_PHASE_INPUT_NO_NUMERIC_EXECUTION")


def offered(k,records):
    x=records[k]
    return dict(role="ORIGINAL_LENGTH_BOUND_WIDTH",units="scene_length",pair_bytes=16,
        word_type="IEEE754_BINARY64",source="SOURCE0",detector="DETECTOR0",
        original_snapshot_sha256=x["request"]["original_snapshot_sha256"],
        phase_certified=False,wavelength_known=False,physical_reference_certified=False)


def baseline():
    return dict(model=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,phase_error_bound=None,
        phase_output=None,phase_certified=False,wavelength_known=False,physical_reference_certified=False,
        scene_engine_admitted=False,GPU_used=False,Bpy_used=False,foreign_modules_executed=False,
        new_RN=0,new_products=0,new_sqrt_calls=0,new_float_decodes=0,new_hex_decodes=0,
        retained_numeric_replays=0,semantic_checks=0,full_costs="UNKNOWN_NOT_ZERO",
        promotion="STOP_WIDTH_TO_PHASE_WITHOUT_SAME_SCENE_CONTRACT_AND_PHYSICAL_EVIDENCE")


def _audit(q,offer,records,fs):
    out=baseline()
    try:
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in records,"closed_record")
        k=q["record_id"]
        targets=[i for i,f in enumerate(fs)if q.get("target_model")==f["spec"]["constants"]["MODEL"]]
        need(len(targets)==1,"closed_target");t=targets[0]
        need(q==selector(k,t,records,fs)and all(type(v)is str for v in q.values()),"closed_selector")
        x=records[k];out["upstream_status"]=x["result"]["status"]
        if x["result"]["status"]!="CPU64_SCENE_PAIR_WIDTH_HOST_BOUND_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued");return out
        expected=offered(k,records)
        need(type(offer)is dict and set(offer)==set(expected)and offer==expected
            and all(type(offer[a])is type(v)for a,v in expected.items()),"semantic_offer_NO_ALIAS_OR_CERT_INJECTION")
        need(x["result"]["scene_engine_admitted"]is False and x["result"]["phase_error_bound"]is None,
             "retained_width_scope")
        z=x["result"]["diagnostic"];need(z["source"]=="SOURCE0"and z["detector"]=="DETECTOR0"
            and z["source_uncertainty_cancelled"]is False,"retained_separate_source_detector")
        out["semantic_checks"]=1
        out["diagnostic"]=dict(width_record_sha256=digest(x),target_contract_sha256=digest(fs[t]),
            original_snapshot_sha256=q["original_snapshot_sha256"],original_query_sha256=q["original_query_sha256"],
            offered=expected,target_role=fs[t]["expected_role"],contract=fs[t],
            retained_width_status=x["result"]["status"],source_uncertainty_cancelled=False,
            unresolved_same_scene_obligations=[
                "WIDTH_VS_PATH_REFERENCE_DIFFERENCE_DEFINITION",
                "SOURCE_WAVELENGTH_INTERVAL_AND_SCENE_UNIT_SCALE",
                "SOURCE_REFERENCE_PHASE_GAUGE_AND_MATERIAL",
                "ALL_REQUIRED_SOURCE_VISIBILITY_COMPLETENESS",
                "ORIGINAL_PHASE_CAP_AND_FULL_ERROR_COMPOSITION",
                "SCENE_WAVELENGTH_REFERENCE_AUTHENTICATION",
                "REAL_BACKEND_GUARD_SAME_WORK_OUTPUTS_FULL_COSTS"],
            evidence_scope="STATIC_INCOMPATIBILITY_ONLY_NOT_PROOF_TARGET_RUNTIME_REJECTION")
        out.update(status="STOP_PHASE_SEMANTIC_JOIN",reason=fs[t]["reason"])
    except (ValueError,TypeError,KeyError,IndexError,OSError,StopIteration)as ex:out["reason"]=str(ex)
    return out


def audit(request,offered_semantics):
    try:records,fs,_=retained();return _audit(request,offered_semantics,records,fs)
    except (ValueError,TypeError,KeyError,IndexError,OSError,StopIteration)as ex:
        out=baseline();out["reason"]="integrity:"+str(ex);return out
