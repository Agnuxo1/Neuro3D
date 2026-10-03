"""Opt-in read-only ABI evidence. No foreign execution or shader dispatch."""
from pathlib import Path
from fractions import Fraction as F
import ast,json,struct
import oblique_scalar32_consumer_gate_CPU_v1 as prior
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-consumer-ABI-static-v1"
POLICY="SEALED_SOURCE_FACTS_NO_IMPLICIT_ADAPTER_OR_ENGINE_ADMISSION"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SCALAR32-CONSUMER-GATE-CPU-001-CODEX.json"
PSHA="1f14029ecb7520b7ed3597c44828b29c6608a8562285a917855d0e99d5f111b9"
SOURCES={"Blender/benchmarks/capacity_audit/axial_common_detector_pair64_ingress_v1.comp":{"bytes":1667,"sha256":"f895fd0b33ad75bd779f929ad28680402386d43fec39bb6d8cb0bd18aca793b4"},"Blender/benchmarks/capacity_audit/oblique_pair64_raw_guard_v2.comp":{"bytes":2221,"sha256":"277a94ba2d223a2e2d06052037c6ef549b04270748a3678501ecd2da4446b70f"},"Blender/shaders/exp005_phase_compensated_probe.glsl":{"bytes":2367,"sha256":"d116b8c18d80dae32092aee453ecb0ff9523b8decf9fc5ef106e0ede9e23ed6c"},"Blender/shaders/exp005_shared_frontier.glsl":{"bytes":4930,"sha256":"914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1"},"Blender/tests/exp005_blender_gpu.py":{"bytes":9165,"sha256":"851f29f9b1fb9b22948f59597d40fa8a55828040673fe0050d24e077b57cf497"},"Blender/tests/exp005_gpu_pack.py":{"bytes":3803,"sha256":"5b8dbbe3673fc13ecf4b5a5ffaf100f3855de94c12cdebc3f1cebdc5e90d00c8"}}
require,sha,capture,digest,pair=prior.require,prior.sha,prior.capture,prior.digest,prior.pair
# Anchors are source evidence, not proof of runtime execution.
ANCHORS={
 "Blender/tests/exp005_blender_gpu.py": ["SHADER=", "def split_double(", "hi=struct.unpack(", "lo=struct.unpack(", "def texture_data(", "a,b=split_double(value)", "def native_shader(", "def dispatch(", "format='RGBA32F'"],
 "Blender/tests/exp005_gpu_pack.py": ["def pack_paths(", "distance = finite_number(hit['distance_BU']", "offset = finite_number(path.get('reference_offset_BU'"],
 "Blender/shaders/exp005_shared_frontier.glsl": ["dvec4 raw4(", "return dvec4(texelFetch(hi", "double length=ray.length+distance;"],
 "Blender/shaders/exp005_phase_compensated_probe.glsl": ["double length = packDouble2x32(words.xy);", "double wavelength = packDouble2x32(words.zw);", "length<0.0lf"],
 "Blender/benchmarks/capacity_audit/axial_common_detector_pair64_ingress_v1.comp": ["uvec4 pairWords[3];", "incoming.header,uvec4(COMMIT_TAG,1u,3u,16u)", "outgoing.pairWords[0]=staged0;"],
 "Blender/benchmarks/capacity_audit/oblique_pair64_raw_guard_v2.comp": ["src.words.length()!=12 || dst.words.length()!=8", "double ah=packDouble2x32", "double al=packDouble2x32", "double bh=packDouble2x32", "double bl=packDouble2x32", "precise dvec2 p=sum2(ah,-bh);", "precise dvec2 q=sum2(al,-bl);"]
}
FUNCTIONS={
 "Blender/tests/exp005_blender_gpu.py": ("split_double","texture_data","native_shader","dispatch"),
 "Blender/tests/exp005_gpu_pack.py": ("pack_paths",)
}
ROUTES=[
 dict(id="SHARED_FRONTIER_TEXTURE_HILO_F32_ADD_F64",gate="STOP_ADAPTER_AND_SCENE_PROVENANCE",
      ABI="two_float32_textures_not_raw_packet",pair_payload_bytes=8,
      operation="dvec4_high_plus_dvec4_low",root_packet_binding_proven=False,
      projection_loss="retained_RN64_loss_conditional_if_same_operands_bound",
      host_encoder="split_double_recalculates_low_from_scalar64",
      host_default_shader="exp005_blender_fields.glsl_NOT_frontier"),
 dict(id="PHASE_PROBE_SCALAR64",gate="STOP_ABI_BIT_MEANING",
      ABI="uvec4_two_scalar64_length_wavelength",scalar_bytes=8,sample_bytes=16,
      operation="packDouble2x32_words_xy_not_sum_of_float32",
      root_packet_binding_proven=False),
 dict(id="AXIAL_PAIR64_COPY16",gate="STOP_ABI_PAIR_WIDTH_AND_WORK",
      ABI="three_binary64_pairs_uvec4_each_plus_header",
      pair_payload_bytes=16,pairs=3,header_bytes=16,input_bytes=64,expected_bytes=48,output_bytes=64,
      operation="raw_copy_no_length_or_phase",root_packet_binding_proven=False),
 dict(id="OBLIQUE_PAIR64_RAW_GUARD16",gate="STOP_ABI_PAIR_WIDTH_AND_OPERATION",
      ABI="header_and_two_binary64_pairs_to_header_and_one_pair",
      pair_payload_bytes=16,input_bytes=48,output_bytes=32,
      operation="EFT_difference_candidate_not_scene_length_or_phase",
      root_packet_binding_proven=False)
]


def source_facts():
    out={}
    for path,seal in SOURCES.items():
        raw=(ROOT/path).read_bytes()
        require(len(raw)==seal["bytes"] and sha(raw)==seal["sha256"],"source_seal:"+path)
        text=raw.decode("utf-8");lines=text.splitlines();facts=[]
        for anchor in ANCHORS[path]:
            hits=[dict(line=i+1,text=v)for i,v in enumerate(lines)if anchor in v and not v.lstrip().startswith("//")]
            require(bool(hits),"missing_anchor:"+path+":"+anchor)
            facts.append(dict(anchor=anchor,hits=hits))
        funcs={}
        if path in FUNCTIONS:
            tree=ast.parse(text)
            for name in FUNCTIONS[path]:
                nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name]
                require(len(nodes)==1,"closed_function:"+name);n=nodes[0]
                funcs[name]=dict(line=n.lineno,end_line=n.end_lineno,
                    AST_sha256=sha(ast.dump(n,include_attributes=False).encode()))
        out[path]=dict(**seal,anchors=facts,functions=funcs)
    return out


def retained():
    raw=(ROOT/PARENT).read_bytes()
    require(len(raw)==214787 and sha(raw)==PSHA,"parent_seal")
    r=json.loads(raw);pins=dict(r["code_doc_sha256"])
    require(len(pins)==300,"parent_pins")
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    d=capture(r["test_run"])["evidence"];e={x["id"]:x for x in d["records"]}
    wire,ref,orig,_,_=prior.retained()
    require(set(e)==set(wire)==set(ref)==set(orig)and len(e)==16,"closed_records")
    facts=source_facts();pins[PARENT]=PSHA
    for p,s in SOURCES.items():pins[p]=s["sha256"]
    return e,wire,ref,orig,pins,d,facts


def selector(k,e,wire,ref,orig,facts):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),wire_record_sha256=digest(wire[k]),
        reference_record_sha256=digest(ref[k]),original_record_sha256=digest(o),
        original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(q),
        source_facts_sha256=digest(facts))


def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,
        byte_decode_calls=0,decoded_scalar64_components=0,
        RN64_adds=0,RN32_casts=0,new_products=0,new_sqrt_calls=0,retained_numeric_replays=0,
        native_length=None,phase_error_bound=None,scene_admitted=False,
        phase_certified=False,wavelength_known=False,physical_reference_certified=False,
        GPU_used=False,Bpy_used=False,shader_used=False,foreign_source_executed=False,
        source_uncertainty_cancelled=False,full_costs="UNKNOWN_NOT_ZERO",
        scope="STATIC_SOURCE_ABI_PLUS_CPU_WRONG_ALIAS_NOT_RUNTIME",
        promotion="STOP_REAL_ADAPTER_SCENE_GUARD_PHASE_AND_COSTS")


def _audit(q,e,wire,ref,orig,facts):
    out=baseline()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        k=q["record_id"]
        require(q==selector(k,e,wire,ref,orig,facts)and all(type(v)is str for v in q.values()),"closed_selector")
        p=e[k]["result"]
        out.update(request_sha256=digest(q),upstream_status=p["status"],
                   retained_canonical_status=p["retained_canonical_status"])
        if p["status"]!="STOP_SCALAR_PAIR_CONSUMPTION_LOSS":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued");return out
        require(ref[k]["result"]["diagnostic"]["original_scene"]==orig[k]["scene"],"original_scene")
        packets=[]
        for i,x in enumerate(p["diagnostic"]["attempts"]):
            r=x["result"];w=wire[k]["result"]["diagnostic"]["packets"][i]["result"]
            require(r["status"]=="STOP_PROJECTION_LOSS"and r["input_packet"]==w["packet_hex"],"retained_packet")
            packet=r["input_packet"];require(len(packet)==16 and bytes.fromhex(packet).hex()==packet,"packet8")
            # New CPU byte-alias diagnostic only: no float sum/cast/products/roots.
            value=struct.unpack("<d",bytes.fromhex(packet))[0]
            out["byte_decode_calls"]+=1;out["decoded_scalar64_components"]+=1
            alias=F.from_float(value);Q=F(*r["exact_pair_sum"])
            require(alias!=Q,"wrong_alias_expected_mismatch")
            packets.append(dict(bound=x["bound"],packet_hex=packet,packet_bytes=8,
                scalar64_alias_word=packet,CPU_scalar64_alias_value=pair(alias),
                retained_exact_pair_sum=r["exact_pair_sum"],alias_matches_pair=False,
                hypothetical_alias_length_negative=alias<0,
                retained_RN64_intermediate_error=r["HOST_signed_intermediate_error"],
                retained_projection_status=r["status"],retained_scalar_candidate=r["candidate_word32"]))
        require(len(packets)==2,"two_original_bounds")
        out.update(status="STATIC_CONSUMER_ABI_UNBOUND",reason="no_implicit_adapter_or_runtime_admission",
            diagnostic=dict(packets=packets,routes=ROUTES,original_snapshot_sha256=digest(orig[k]["scene"]),
                source="SOURCE0",detector="DETECTOR0",units="scene_length",
                original_record_sha256=digest(orig[k]),reference_record_sha256=digest(ref[k]),
                source_facts_sha256=digest(facts),retained_scalar_gate=p["status"]))
    except (ValueError,TypeError,KeyError,IndexError,OverflowError,struct.error)as ex:out["reason"]=str(ex)
    return out


def audit(q):
    try:
        e,wire,ref,orig,_,_,facts=retained()
        return _audit(q,e,wire,ref,orig,facts)
    except (ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]=str(ex);return out
