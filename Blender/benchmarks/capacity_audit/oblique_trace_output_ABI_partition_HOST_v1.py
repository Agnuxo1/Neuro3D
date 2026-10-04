"""Exact retained HOST wire layout inspection, not geometry or native precision."""
from pathlib import Path
import json, hashlib, struct, base64, zlib, math
ROOT = Path(__file__).resolve().parents[3]
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-NATIVE-EVIDENCE-BINDING-HOST-001-CODEX.json"
PSHA = "699426a2a5e3e8521b031af00f531ad252025f2dbe0bb8f93e06abdb4a066297"
WIRE = "coordinacion/respuestas/PRECISION-OBLIQUE-TRACE-OUTPUT-HILO32-HOST-001-CODEX.json"
WSHA = "b62ddeca67ae4c9c8f37d50db1fbe9d53ca62e1fcae3bf0fc6e7a015aa092bfd"
HEADER = struct.Struct("<8s6I")
FALSE = ("GPU_used", "GPU_launch_allowed", "Bpy_used", "RT_used", "native_IEEE_RN_graph_certified",
         "scene_authenticated", "phase_certified", "physical_field_certified", "SOURCE_merged",
         "exact_contact_allowed", "computed_hilo_collapse_allowed", "guard_runtime_certified")
PARTITION = [{"source_id":"S0","offset_bytes":32,"length_bytes":168,"field_start":0,"field_count":21},
             {"source_id":"S1","offset_bytes":200,"length_bytes":168,"field_start":21,"field_count":21}]
MAX_JSON = 1024*1024

def need(ok, reason):
    if not ok: raise ValueError(reason)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def digest(v):
    return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())

def same(a,b,reason): need(digest(a)==digest(b),reason)

def parse(raw):
    need(type(raw)is bytes and len(raw)<=MAX_JSON,"JSON_capacity")
    def unique(items):
        d={}
        for k,v in items:
            need(k not in d,"duplicate_JSON_key");d[k]=v
        return d
    def finite(s):
        v=float(s);need(math.isfinite(v),"nonfinite_exponent");return v
    def constant(s): raise ValueError("nonfinite_JSON")
    return json.loads(raw,object_pairs_hook=unique,parse_float=finite,parse_constant=constant)

def capture(w):
    need(type(w["rc"])is int and w["rc"]==0 and w["timed_out"]is False,"captured_PASS")
    need(type(w["stdout_bytes"])is int and 0<=w["stdout_bytes"]<=MAX_JSON,"capture_size")
    z=zlib.decompressobj()
    raw=z.decompress(base64.b64decode(w["stdout_zlib_base64"],validate=True),MAX_JSON+1)
    need(z.eof and not z.unused_data and not z.unconsumed_tail,"capture_complete")
    need(len(raw)==w["stdout_bytes"]and sha(raw)==w["stdout_sha256"],"capture_seal")
    return parse(raw)

def load_context():
    raw=(ROOT/PARENT).read_bytes();need(len(raw)==182913 and sha(raw)==PSHA,"parent_seal")
    p=parse(raw);pins=dict(p["code_doc_sha256"]);need(len(pins)==388,"pins388")
    for name,h in pins.items():need(sha((ROOT/name).read_bytes())==h,"dependency:"+name)
    need(capture(p["independent_verification"])["status"]=="PASS","parent_oracle")
    targets=capture(p["test_run"])["evidence"]["original_plan"]["cases"]
    need(pins[WIRE]==WSHA,"wire_pin")
    w=parse((ROOT/WIRE).read_bytes());data=capture(w["test_run"])
    need(data["status"]=="PASS","wire_capture_PASS")
    originals={r["id"]:r["result"] for r in data["evidence"]["positive"]}
    need(len(originals)==6 and set(originals)=={v["case"]for v in targets},"original_case_set")
    for t in targets:
        meta=originals[t["case"]]["packet"]["manifest"]
        for key in ("scene_sha256","query_sha256","input_buffer_sha256","source_ids"):
            same(meta[key],t[key],"target_wire_join:"+key)
        need(originals[t["case"]]["exact_contact_allowed"]is False and
             originals[t["case"]]["exact_contact_status"]=="STOP_NONEXACT_TRACE_OUTPUT","retained_contact_STOP")
    pins[PARENT]=PSHA
    return originals,pins

def baseline():
    return dict(status="STOP_ABI",reason=None,layout_verified=False,phase_error_bound=None,
                old_numeric_replays=0,new_intersections=0,new_root_calls=0,new_phase_operations=0,
                new_word_classifications=0,full_costs="UNKNOWN_NOT_ZERO",**{k:False for k in FALSE})

def validate(case,packet,partition,original):
    """Caller packet checked against pinned recorded fixture. No old producer imports."""
    r=baseline()
    try:
        need(type(case)is str and type(packet)is dict and set(packet)=={"manifest","manifest_sha256","buffer_hex"},"closed_packet")
        same(partition,PARTITION,"header_and_SOURCE_partition")
        ref=original["packet"];meta=packet["manifest"]
        need(type(meta)is dict and type(packet["buffer_hex"])is str and len(packet["buffer_hex"])==736 and
             all(c in "0123456789abcdef"for c in packet["buffer_hex"]),"exact_wire_hex")
        b=bytes.fromhex(packet["buffer_hex"])
        need(len(b)==368 and HEADER.unpack_from(b)==(b"N3OH32V1",1,2,21,42,84,0),"closed_header")
        need(meta["case"]==case,"case_context")
        same(meta["source_ids"],["S0","S1"],"SOURCE_order")
        need(meta["endian"]=="little" and type(meta["header_bytes"])is int and meta["header_bytes"]==32,"header_metadata")
        for k,value in (("pair_field_count",42),("source_field_count",21),("word_count",84),("buffer_bytes",368)):
            need(type(meta[k])is int and meta[k]==value,"integer_metadata:"+k)
        need(meta["computed_hilo_collapse_allowed"]is False and meta["phase_bound_in_packet"]is False and
             meta["scene_authentication"]is False,"no_extra_admission")
        fs=meta["fields"];need(type(fs)is list and len(fs)==42,"fields42")
        sources=[]
        for part in PARTITION:
            sid=part["source_id"];start=part["field_start"]
            words=[];pairs=[]
            for i,f in enumerate(fs[start:start+21]):
                need(type(f["path"])is str and f["path"].startswith(sid+"/"),"field_SOURCE_partition")
                offset=part["offset_bytes"]+8*i
                wh,wl=struct.unpack_from("<2I",b,offset)
                need(type(f["word_pair"])is list and len(f["word_pair"])==2 and
                     all(type(v)is int and 0<=v<2**32 for v in f["word_pair"]),"typed_pair_words")
                same(f["word_pair"],[wh,wl],"metadata_raw_pair")
                for w in (wh,wl):
                    r["new_word_classifications"]+=1
                    exp=(w>>23)&255;frac=w&0x7fffff;sign=w>>31
                    need(exp!=255 and not(exp==0 and frac!=0) and not(sign and exp==0 and frac==0),"normal_or_positive_zero")
                words.extend((wh,wl));pairs.append({"path":f["path"],"offset_bytes":offset,"word_pair":[wh,wl],"unit":f["unit"]})
            segment=b[part["offset_bytes"]:part["offset_bytes"]+part["length_bytes"]]
            need(segment==struct.pack("<42I",*words),"source_raw_segment")
            sources.append(dict(part,raw_hex=segment.hex(),sha256=sha(segment),fields=pairs,
                                native_precision_certified=False,source_field_inferred=False))
        # Hashes plus exact retained content preserve radii/contact provenance, not physics.
        need(meta["buffer_sha256"]==sha(b),"raw_SHA")
        need(packet["manifest_sha256"]==digest(meta),"manifest_SHA")
        need(packet["buffer_hex"]==ref["buffer_hex"],"retained_HOST_raw_bytes")
        same(meta,ref["manifest"],"retained_HOST_metadata_error_provenance")
        need(original["exact_contact_allowed"]is False and original["exact_contact_status"]=="STOP_NONEXACT_TRACE_OUTPUT","retained_contact_STOP")
        r.update(status="HOST_ABI_PARTITION_ONLY_CONTACT_NATIVE_PHASE_STOP",layout_verified=True,case=case,
                 scene_sha256=meta["scene_sha256"],query_sha256=meta["query_sha256"],input_buffer_sha256=meta["input_buffer_sha256"],
                 output_buffer_sha256=sha(b),output_buffer_bytes=368,header_hex=b[:32].hex(),SOURCE_partitions=sources,
                 field_count=42,pair_word_count=84,retained_contact_status=original["exact_contact_status"],
                 retained_nonexact_fields=original["nonexact_fields"],origin="RECORDED_HOST_FIXTURE_DATA_NOT_NATIVE_EXECUTION")
    except(ValueError,KeyError,TypeError,struct.error,OverflowError)as ex:r["reason"]=str(ex)
    return r

def inspect(case,packet=None,partition=None):
    r=baseline()
    try:
        originals,pins=load_context()
        need(type(case)is str and case in originals,"closed_case")
        original=originals[case]
        received=original["packet"]if packet is None else packet
        layout=PARTITION if partition is None else partition
        r=validate(case,received,layout,original);r["dependency_pins"]=pins
    except(ValueError,KeyError,TypeError,OSError,zlib.error,RecursionError)as ex:
        r.update(status="STOP_DEPENDENCY",reason=str(ex),layout_verified=False)
    return r
