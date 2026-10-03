"""Opt-in closed evidence boundary around frozen pure integer-RNE64 proof definitions."""
from pathlib import Path
from fractions import Fraction as F
import ast,base64,copy,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[3]
PARENT="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-NATIVE-CPU-001-CODEX.json"
PSHA="317d58a77be135250954bef9ad4cf9f8669cb9604a968c3286d3f8029a42511d"
MODEL="precision-position-phase-reference-evidence-negative-HOST-v1"
DEFS={"sha","dg","pp","dw","rne","pv","flip","verify"}
def sha(v):return hashlib.sha256(v).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def need(v,msg):
    if not v:raise ValueError(msg)
def capture(t):
    z=zlib.decompressobj();b=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),2097153)
    need(len(b)<=2097152 and z.eof and not z.unconsumed_tail and not z.unused_data,"bounded_capture")
    need(t["rc"]==0 and not t["timed_out"] and sha(b)==t["stdout_sha256"] and len(b)==t["stdout_bytes"],"capture_identity")
    return json.loads(b)
def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==333604,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"frozen_pin:"+p)
    v=capture(r["independent_pre"]);need(v["status"]=="PASS" and v["pins"]==220,"retained_oracle_PASS")
    td=capture(r["test_run"])["data"];need(len(td["runs"])==482 and td["census"]["CPU_contrasts"]==39,"retained_grid")
    h="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-OVERLAY-HOST-001-CODEX.json"
    hraw=(ROOT/h).read_bytes();need(sha(hraw)==r["parent_receipt_sha256"],"HOST_parent_identity")
    pd=capture(json.loads(hraw)["test_run"])["data"];e={x["id"]:x for x in pd["runs"]}
    # Definitions only: NO original module main, loops, receipt I/O or 482-case replay.
    tree=ast.parse(r["independent_verifier_source"]);defs=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in DEFS]
    need({x.name for x in defs}==DEFS and len(defs)==len(DEFS),"closed_pure_definitions")
    flags=[x.value for x in tree.body if isinstance(x,ast.Assign) and len(x.targets)==1
           and isinstance(x.targets[0],ast.Name) and x.targets[0].id=="falseflags"]
    need(len(flags)==1,"closed_falseflags_literal")
    falseflags=ast.literal_eval(flags[0]);need(type(falseflags)is tuple and len(falseflags)==15
                                            and all(type(x)is str for x in falseflags),"typed_falseflags")
    ns=dict(F=F,pathlib=__import__("pathlib"),json=json,hashlib=hashlib,e=e,R=ROOT,H=h,
        MODEL="precision-position-phase-reference-native-CPU-v1",
        REP="CPU_RN64_PAIR_DECLARED_REFERENCE_CONTRAST_NOT_PHYSICAL_TOTAL",
        INTENT="ALL16_BYTES_BEFORE_ALU_ALL_FOUR_TERMS_ERROR_CHARGED",CAP=F(1,10000),
        natives=0,nodes=0,casts=0,flips=0,eft=0,nonzeroenc=0,nonzeroadd=0,falseflags=falseflags)
    exec(compile(ast.Module(body=defs,type_ignores=[]),"<pinned_integer_oracle_pure_defs>","exec"),ns)
    rows={x["id"]:x for x in td["runs"] if x["result"]["reference_contrast_conditional"]}
    need(len(rows)==39,"closed_admitted_rows")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return dict(rows=rows,ns=ns,pins=pins,source_sha256=sha(r["independent_verifier_source"].encode()),
                extracted_definitions=sorted(DEFS),old_records=482,old_records_replayed=0)

def shape(value,template,path="$"):
    need(type(value)is type(template),"typed_schema:"+path)
    if type(template)is dict:
        need(set(value)==set(template),"closed_keys:"+path)
        for k,t in template.items():shape(value[k],t,path+"."+k)
    elif type(template)is list:
        need(len(value)==len(template),"closed_extent:"+path)
        for i,(v,t) in enumerate(zip(value,template)):shape(v,t,path+"["+str(i)+"]")

def evaluate(record,ctx,*,strict):
    """HOST evidence test, not a scene/backend execution or authentication endpoint."""
    ns=ctx["ns"];before=ns["eft"]
    out=dict(verdict="REJECTED",reason=None,strict=strict,scope="IN_MEMORY_EVIDENCE_MUTATION_ONLY",
        GPU_executed=False,CPU_native_executed=False,producer_replays=0,parent_suites_replayed=0,
        promotion="STOP",full_costs="UNMEASURED_NOT_ZERO")
    try:
        need(type(record)is dict and type(record.get("id"))is str and record["id"] in ctx["rows"],"closed_retained_id")
        if strict:shape(record,ctx["rows"][record["id"]])
        ns["verify"](record);out["verdict"]="ACCEPTED_HOST_EVIDENCE_ONLY"
    except(ValueError,AssertionError)as ex:
        out["reason"]=type(ex).__name__+":"+str(ex)
    finally:out["EFT_checks_completed"]=ns["eft"]-before
    return out

def variants(ctx):
    rows=list(ctx["rows"].values())
    zero=next(x for x in rows if x["result"]["diagnostics"][0]["new_encoding_error_turns"]==[0,1]
              and x["result"]["diagnostics"][0]["new_addition_error_turns"]==[0,1])
    nonzero=next(x for x in rows if F(*x["result"]["diagnostics"][0]["new_encoding_error_turns"])>0
                 and F(*x["result"]["diagnostics"][0]["new_addition_error_turns"])>0)
    cases=[]
    def add(label,base,mutate):
        x=copy.deepcopy(base);mutate(x);cases.append(dict(label=label,base_id=base["id"],base_sha256=digest(base),record=x))
    add("parent_binding",nonzero,lambda x:x["request"].update(parent_record_sha256="wrong"))
    add("raw_geometry_bit",nonzero,lambda x:x.update(raw_hex=("01" if x["raw_hex"][:2]!="01" else "02")+x["raw_hex"][2:]))
    add("physical_claim",nonzero,lambda x:x["result"].update(total_phase_certified=True))
    add("scalar_claim",nonzero,lambda x:x["result"].update(native_scalar_phase_output=True))
    add("decoded_word_count",nonzero,lambda x:x["result"].update(decoded_term_words=0))
    add("node_count",nonzero,lambda x:x["result"].update(RN64_operations=103))
    add("cast_input",nonzero,lambda x:x["result"]["conversion_trace"][0].update(input_exact_HOST=[0,1]))
    add("cast_word",nonzero,lambda x:x["result"]["conversion_trace"][0].update(word_LE="0000000000000000"))
    add("omitted_reference",nonzero,lambda x:x["result"]["stages"].pop(1))
    add("wrong_reference_sign",nonzero,lambda x:x["result"]["stages"][1].update(signed_words_LE=x["result"]["stages"][1]["encoded_words_LE"]))
    ie=next(i for i,t in enumerate(nonzero["result"]["stages"]) if F(*t["encoding_error_turns"])>0)
    ia=next(i for i,t in enumerate(nonzero["result"]["stages"]) if F(*t["addition_error_turns"])>0)
    add("encoding_error_omitted",nonzero,lambda x:x["result"]["stages"][ie].update(encoding_error_turns=[0,1]))
    add("addition_error_omitted",nonzero,lambda x:x["result"]["stages"][ia].update(addition_error_turns=[0,1]))
    add("total_encoding_error_omitted",nonzero,lambda x:x["result"]["rows"][0].update(new_encoding_error_turns=[0,1]))
    add("total_addition_error_omitted",nonzero,lambda x:x["result"]["rows"][0].update(new_addition_error_turns=[0,1]))
    add("budget_forged_zero",nonzero,lambda x:x["result"].update(error_rad_upper=[0,1]))
    add("node_operator",nonzero,lambda x:x["result"]["trace"][0].update(op="-"))
    add("node_name",nonzero,lambda x:x["result"]["trace"][0].update(name="other"))
    add("node_operand",nonzero,lambda x:x["result"]["trace"][0].update(a="0000000000000000"))
    iz=next(i for i,t in enumerate(zero["result"]["trace"]) if t["y"]=="0000000000000080")
    add("signed_zero_erased",zero,lambda x:x["result"]["trace"][iz].update(y="0000000000000000"))
    # Equal mathematical values with incompatible JSON types / ignored extra metadata.
    add("bool_zero_rational",zero,lambda x:x["result"]["stages"][0].update(encoding_error_turns=[False,True]))
    add("float_word_count",zero,lambda x:x["result"].update(decoded_words=2.0))
    add("float_zero_rational",zero,lambda x:x["result"]["rows"][0].update(new_encoding_error_turns=[0.0,1.0]))
    add("bool_reference_point",zero,lambda x:x["result"]["stages"][1].update(point=True))
    add("bool_positive_sign",zero,lambda x:x["result"]["stages"][0].update(sign=True))
    add("extra_trace_metadata",zero,lambda x:x["result"]["trace"][0].update(unverified_gpu_claim=True))
    add("extra_result_claim",zero,lambda x:x["result"].update(unverified_gpu_claim=True))
    return dict(controls=[copy.deepcopy(zero),copy.deepcopy(nonzero)],mutations=cases,
        semantic_mutations=19,type_metadata_mutations=7)
