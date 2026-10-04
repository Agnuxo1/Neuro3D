"""Read-only sealed inventory. Hash mentions and historical SUCCESS never admit a job."""
from pathlib import Path
import json,hashlib,base64,zlib,math
ROOT=Path(__file__).resolve().parents[3]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-REFERENCE-DIFFERENCE-HOST-001-CODEX.json"
PSHA="3d08cc7966483a7930bca4be950871128fbbd855b9d35a0f3e2c042915250628"
SPECS=[{"path":"coordinacion/respuestas/PRECISION-COMPLETE-001-CLAUDE.json","sha256":"e146c62499472c26b2e657eb76f31d46a0260e43934a17624da5b5365e84abf6","bytes":6175,"format":"json","role":"CLAUDE_EXISTING_REPORT_ONLY"},{"path":"coordinacion/respuestas/PRECISION-005-CLAUDE.json","sha256":"aa463c7050b70b905ef58ead1852854d869027b7becce125341407b54e4fb0be","bytes":11014,"format":"json","role":"CLAUDE_EXISTING_REPORT_ONLY"},{"path":"coordinacion/respuestas/PRECISION-006-CLAUDE.json","sha256":"61f329183b9f6700308b53faea58d50cb8a0778571c1d109fa0e04ec8dc5802a","bytes":9126,"format":"json","role":"CLAUDE_EXISTING_REPORT_ONLY"},{"path":"coordinacion/respuestas/PRECISION-006-REDUCTION-CLAUDE.json","sha256":"0d1a1eaa981f2cb60261e3563c85a8721d499fd6967605025684c3b9903e9609","bytes":8276,"format":"json","role":"CLAUDE_EXISTING_REPORT_ONLY"},{"path":"coordinacion/respuestas/RT-EQUAL-001-CLAUDE.json","sha256":"008285cd623055e43a4d18645f16557cf861587ceea69ce78da0a6a62b65ed7e","bytes":6519,"format":"json","role":"CLAUDE_EXISTING_REPORT_ONLY"},{"path":"coordinacion/respuestas/RT-CAP-006-CLAUDE-FINAL.json","sha256":"c0ddeb2771b893bf5b346179743ffc26d8b5accd5517609bdf9f6b320456aa98","bytes":4587,"format":"json","role":"CLAUDE_EXISTING_REPORT_ONLY"},{"path":"coordinacion/respuestas/PHASE-SIGNED-CAPTURE-010-CLAUDE.json","sha256":"1725836b839713e160bb427af43ad98456202c5e6077c0969b21a5381bb1b76a","bytes":4860,"format":"json","role":"CLAUDE_EXISTING_REPORT_ONLY"},{"path":"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-SPIRV-GUARD-HOST-001-CODEX.json","sha256":"b4eacc9e5b7a3746669b7e834ec0888d32587025bb9e86e51e5d5cf8e8e141ed","bytes":32141,"format":"json","role":"CODEX_HOST_GUARD_REPORT_ONLY"},{"path":"coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-RAW-GUARD-SHADERC-001-CODEX.json","sha256":"3fd747841aaea192619df18add3a701a69cc0f20beed598497125d8202f252cf","bytes":59278,"format":"json","role":"CODEX_HOST_GUARD_REPORT_ONLY"},{"path":"D:/PROJECTS/.cognition/neuro3d/rt_cap002/guard_v4.py","sha256":"cf097276e040230d4d470e4648098b507aa4bc5f03b70c0a599d5ff2c591d820","bytes":11155,"format":"text","role":"CLAUDE_RT006_HISTORICAL_ATTACHMENT","report_sha256":"cf097276e040230d4d470e4648098b507aa4bc5f03b70c0a599d5ff2c591d820"},{"path":"D:/PROJECTS/.cognition/neuro3d/rt_cap002/pilot006_contract.json","sha256":"bcc04e6bf7c7df5f636e7bd14320a249e8f318d77d85b87f2ceb998d6a4dc672","bytes":2100,"format":"json","role":"CLAUDE_RT006_HISTORICAL_ATTACHMENT","report_sha256":"bcc04e6bf7c7df5f636e7bd14320a249e8f318d77d85b87f2ceb998d6a4dc672"},{"path":"D:/PROJECTS/.cognition/neuro3d/rt_cap002/pilot006_verdict.json","sha256":"dbf3b4c6a6bb70a8fba7263c7994838072559f25eba1efdf8e99b07788429765","bytes":8333,"format":"json","role":"CLAUDE_RT006_HISTORICAL_ATTACHMENT","report_sha256":"dbf3b4c6a6bb70a8fba7263c7994838072559f25eba1efdf8e99b07788429765"},{"path":"D:/PROJECTS/.cognition/neuro3d/rt_cap002/pilot006_envelope.json","sha256":"071763618ccef3780100490f2283643c9d89da1d020cbf5f2acb9327ace4aa8c","bytes":1410,"format":"json","role":"CLAUDE_RT006_HISTORICAL_ATTACHMENT","report_sha256":"071763618ccef3780100490f2283643c9d89da1d020cbf5f2acb9327ace4aa8c"},{"path":"D:/PROJECTS/.cognition/neuro3d/rt_cap002/manifest_T32_pilot006.json","sha256":"81b852f92a3ea6b6922fb1885474ccc39324f85c52eefe7390dac4d6967ccb07","bytes":20319,"format":"json","role":"CLAUDE_RT006_HISTORICAL_ATTACHMENT","report_sha256":"81b852f92a3ea6b6922fb1885474ccc39324f85c52eefe7390dac4d6967ccb07"}]
MAX_CAPTURE=4*1024*1024
CLAIM_KEYS={"status","scope","scope_inspected","GPU_executed","GPU_launch_allowed","promotion",
 "phase_certified","phase_error_bound","reference_truth_verified","gauge_provenance_verified",
 "material_phase_verified","native_IEEE_RN_graph_certified","full_costs","guard_rc","contract",
 "rt_hardware_evidence","ram_floor_GiB","ram_budget_GiB","original_floor_GiB","original_budget_GiB"}
def need(ok,s):
 if not ok:raise ValueError(s)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def parse(raw):
 def no_constant(x):raise ValueError("nonfinite_JSON:"+x)
 def finite_float(s):
  x=float(s);need(math.isfinite(x),"nonfinite_JSON_exponent");return x
 def unique(pairs):
  d={}
  for k,v in pairs:need(k not in d,"duplicate_JSON_key");d[k]=v
  return d
 return json.loads(raw,parse_constant=no_constant,parse_float=finite_float,object_pairs_hook=unique)
def read(path):return (ROOT/path).read_bytes()
def capture(w):
 need(type(w)is dict and w.get("rc")==0 and type(w.get("rc"))is int and w.get("timed_out")is False,"complete_capture")
 need(type(w["stdout_bytes"])is int and 0<=w["stdout_bytes"]<=MAX_CAPTURE,"bounded_capture")
 encoded=base64.b64decode(w["stdout_zlib_base64"],validate=True);de=zlib.decompressobj()
 raw=de.decompress(encoded,MAX_CAPTURE+1)
 need(de.eof and not de.unconsumed_tail and not de.unused_data and len(raw)<=MAX_CAPTURE,"bounded_complete_zlib")
 need(len(raw)==w["stdout_bytes"]and hashlib.sha256(raw).hexdigest()==w["stdout_sha256"],"capture_seal")
 return parse(raw)
def anchor():
 raw=read(PARENT);need(len(raw)==125857 and hashlib.sha256(raw).hexdigest()==PSHA,"anchor_receipt")
 p=parse(raw);pins=dict(p["code_doc_sha256"]);need(len(pins)==367,"anchor_pins367")
 for path,h in pins.items():need(hashlib.sha256(read(path)).hexdigest()==h,"dependency:"+path)
 need(capture(p["independent_verification"])["status"]=="PASS","anchor_oracle")
 d=capture(p["test_run"]);need(d["status"]=="PASS","anchor_suite")
 a=[]
 for x in d["evidence"]["positive"]:
  r=x["result"];need(r["phase_error_bound"]is None and r["SOURCE_merged"]is False and r["phase_certified"]is False,"anchor_NO_phase")
  need([v["source_id"]for v in r["SOURCE_inputs"]]==["S0","S1"],"anchor_SOURCE")
  a.append(dict(case=x["id"],scene_sha256=r["scene_sha256"],query_sha256=r["query_sha256"],input_buffer_sha256=r["input_buffer_sha256"],source_ids=["S0","S1"]))
 need(len(a)==6 and len({v["case"]for v in a})==6,"six_anchor_cases")
 pins[PARENT]=PSHA;return sorted(a,key=lambda v:v["case"]),pins
def pointer(path):return "/"+"/".join(str(v).replace("~","~0").replace("/","~1")for v in path)if path else ""
def walk(doc):
 stack=[((),doc,0)];nodes=0
 while stack:
  path,v,depth=stack.pop();nodes+=1;need(depth<=64 and nodes<=100000,"bounded_document_walk")
  yield path,v
  if type(v)is dict:stack.extend((path+(k,),x,depth+1)for k,x in v.items())
  elif type(v)is list:stack.extend((path+(i,),x,depth+1)for i,x in enumerate(v))
def scan(doc,anchors):
 need(type(anchors)is list and len(anchors)==6,"six_typed_targets")
 fields=("scene_sha256","query_sha256","input_buffer_sha256")
 for a in anchors:need(type(a)is dict and set(a)=={"case","source_ids",*fields}and a["source_ids"]==["S0","S1"]and all(type(a[k])is str and len(a[k])==64 and all(c in "0123456789abcdef"for c in a[k])for k in fields),"typed_target_hashes")
 mentions=[];joins=[];claims=[];nodes=0;claims_total=0
 for path,v in walk(doc):
  nodes+=1
  if type(v)is dict:
   for a in anchors:
    if all(v.get(k)==a[k]for k in fields[:2]):
     joins.append(dict(case=a["case"],pointer=pointer(path),kind="SCENE_QUERY_INPUT_LITERAL_MATCH"if v.get(fields[2])==a[fields[2]]else"SCENE_QUERY_LITERAL_MATCH_NO_INPUT_JOIN",native_or_physical_proof=False))
  elif type(v)is str:
   for a in anchors:
    for k in fields:
     if v==a[k]:mentions.append(dict(case=a["case"],field=k,pointer=pointer(path),proof=False))
  if path and type(path[-1])is str and path[-1]in CLAIM_KEYS and type(v)in(str,int,float,bool,type(None)):
   claims_total+=1
   if len(claims)<80:claims.append(dict(pointer=pointer(path),value=v[:600]if type(v)is str else v,field_claim_only_unverified=True))
 return dict(nodes=nodes,literal_hash_mentions=sorted(mentions,key=lambda v:(v["case"],v["field"],v["pointer"])),
  co_located_join_mentions=sorted(joins,key=lambda v:(v["case"],v["pointer"])),selected_scalar_claims=claims,
  claims_total=claims_total,claims_truncated=claims_total>80,native_or_physical_admission=False)
def base():
 return dict(status="STOP_DEPENDENCY",reason=None,inventory_complete=False,artifacts=[],anchor_cases=[],
  GPU_launch_allowed=False,GPU_used=False,Bpy_used=False,RT_used=False,physical_phase_admitted=False,
  reference_truth_verified=False,gauge_provenance_verified=False,material_phase_verified=False,
  native_IEEE_RN_graph_certified=False,exact_contact_allowed=False,SOURCE_merged=False,
  phase_error_bound=None,new_numeric_operations=0,old_numeric_replays=0,foreign_writer_executions=0,
  full_costs="UNKNOWN_NOT_ZERO",repo_wide_absence_claim=False,live_gpu_telemetry_checked=False)
def run():
 r=base()
 try:
  a,pins=anchor();docs={};rows=[];decoded=0;scanned=0
  for spec in SPECS:
   raw=read(spec["path"]);need(len(raw)==spec["bytes"]and hashlib.sha256(raw).hexdigest()==spec["sha256"],"artifact_seal:"+spec["path"])
   pins[spec["path"]]=spec["sha256"];row=dict(spec,documents=[],source_executed=False)
   if spec["format"]=="json":
    doc=parse(raw);docs[spec["path"]]=doc;row["documents"].append(dict(origin="RAW_JSON",report=scan(doc,a)));scanned+=1
    if type(doc)is dict and type(doc.get("test_run"))is dict and "stdout_zlib_base64"in doc["test_run"]:
     captured=capture(doc["test_run"]);row["documents"].append(dict(origin="SEALED_TEST_CAPTURE_DATA_ONLY",report=scan(captured,a)));decoded+=1;scanned+=1
   else:
    raw.decode("utf-8");row["text_scope"]="HASH_VERIFIED_TEXT_ONLY_NOT_IMPORTED_OR_RUNTIME_GUARD_VALIDATED"
   rows.append(row)
  rt=docs["coordinacion/respuestas/RT-CAP-006-CLAUDE-FINAL.json"]
  for spec in SPECS:
   if spec["role"]=="CLAUDE_RT006_HISTORICAL_ATTACHMENT":need(rt["artifact_sha256"][Path(spec["path"]).name]==spec["sha256"]==spec["report_sha256"],"RT006_attachment_report_hash")
  envelope=docs["D:/PROJECTS/.cognition/neuro3d/rt_cap002/pilot006_envelope.json"]
  r.update(status="AUDIT_COMPLETE_RETRIEVAL_ONLY_NO_ADMISSION",inventory_complete=True,artifacts=rows,anchor_cases=a,
   anchor_receipt_sha256=PSHA,sealed_test_captures_decoded_as_DATA=decoded,documents_scanned=scanned,
   all_selected_nodes_scanned=sum(x["report"]["nodes"]for row in rows for x in row["documents"]),
   co_located_join_mention_count=sum(len(x["report"]["co_located_join_mentions"])for row in rows for x in row["documents"]),
   exact_input_join_mention_count=sum(sum(v["kind"]=="SCENE_QUERY_INPUT_LITERAL_MATCH"for v in x["report"]["co_located_join_mentions"])for row in rows for x in row["documents"]),
   historical_rt006=dict(reported_status=rt["status"],reported_scope=rt["scope"],reported_device=rt["backend_reported"],
    retained_envelope_status=envelope["status"],retained_deadline_utc=envelope["deadline_utc"],
    override_disclosed=rt["override_disclosed"],override_reuse_allowed=False,fresh_job_admitted=False,
    attachments_hash_verified=5,rt_hardware_counter_certified=False,original_scene_equal_work_certified=False),
   query_scope="14_EXPLICIT_FILES_AND_ELIGIBLE_SEALED_TEST_CAPTURES_ONLY_NOT_ENTIRE_REPOSITORY",
   proof_request_not_satisfied_by_lexical_match=["same_scene_query_input_output_ABI_SOURCE_ALLprimitive",
    "native_fail_closed_guard_graph_runtime_raw_words","reference_gauge_material_authentication_and_length_phase_bound",
    "equal_work_same_outputs_and_complete_cost_breakdown","fresh_job_reservation_deadline_telemetry_and_current_safety_budget"],
   dependency_pins=pins)
 except(OSError,ValueError,KeyError,TypeError,IndexError,OverflowError,RecursionError,zlib.error)as ex:r.update(reason=str(ex))
 return r
