"""Independent sealed-source AST/line and IEEE bit proof, no foreign source execution."""
from pathlib import Path
from fractions import Fraction as F
import ast,json,hashlib,copy,runpy,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
old=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_scalar32_consumer_gate_CPU.py"))
capture,digest,pair,pf,p32=(old[n]for n in ("capture","digest","pair","pf","p32"))
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SCALAR32-CONSUMER-GATE-CPU-001-CODEX.json"
PSHA="1f14029ecb7520b7ed3597c44828b29c6608a8562285a917855d0e99d5f111b9"
SEALS={"Blender/benchmarks/capacity_audit/axial_common_detector_pair64_ingress_v1.comp":{"bytes":1667,"sha256":"f895fd0b33ad75bd779f929ad28680402386d43fec39bb6d8cb0bd18aca793b4"},"Blender/benchmarks/capacity_audit/oblique_pair64_raw_guard_v2.comp":{"bytes":2221,"sha256":"277a94ba2d223a2e2d06052037c6ef549b04270748a3678501ecd2da4446b70f"},"Blender/shaders/exp005_phase_compensated_probe.glsl":{"bytes":2367,"sha256":"d116b8c18d80dae32092aee453ecb0ff9523b8decf9fc5ef106e0ede9e23ed6c"},"Blender/shaders/exp005_shared_frontier.glsl":{"bytes":4930,"sha256":"914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1"},"Blender/tests/exp005_blender_gpu.py":{"bytes":9165,"sha256":"851f29f9b1fb9b22948f59597d40fa8a55828040673fe0050d24e077b57cf497"},"Blender/tests/exp005_gpu_pack.py":{"bytes":3803,"sha256":"5b8dbbe3673fc13ecf4b5a5ffaf100f3855de94c12cdebc3f1cebdc5e90d00c8"}}
MODEL="oblique-consumer-ABI-static-v1"
POLICY="SEALED_SOURCE_FACTS_NO_IMPLICIT_ADAPTER_OR_ENGINE_ADMISSION"
# Independent fixed expected ABI schema.
EXPECTED=[
 dict(id="SHARED_FRONTIER_TEXTURE_HILO_F32_ADD_F64",gate="STOP_ADAPTER_AND_SCENE_PROVENANCE",
      ABI="two_float32_textures_not_raw_packet",pair_payload_bytes=8,
      operation="dvec4_high_plus_dvec4_low",root_packet_binding_proven=False,
      projection_loss="retained_RN64_loss_conditional_if_same_operands_bound",
      host_encoder="split_double_recalculates_low_from_scalar64",
      host_default_shader="exp005_blender_fields.glsl_NOT_frontier"),
 dict(id="PHASE_PROBE_SCALAR64",gate="STOP_ABI_BIT_MEANING",
      ABI="uvec4_two_scalar64_length_wavelength",scalar_bytes=8,sample_bytes=16,
      operation="packDouble2x32_words_xy_not_sum_of_float32",root_packet_binding_proven=False),
 dict(id="AXIAL_PAIR64_COPY16",gate="STOP_ABI_PAIR_WIDTH_AND_WORK",
      ABI="three_binary64_pairs_uvec4_each_plus_header",
      pair_payload_bytes=16,pairs=3,header_bytes=16,input_bytes=64,expected_bytes=48,output_bytes=64,
      operation="raw_copy_no_length_or_phase",root_packet_binding_proven=False),
 dict(id="OBLIQUE_PAIR64_RAW_GUARD16",gate="STOP_ABI_PAIR_WIDTH_AND_OPERATION",
      ABI="header_and_two_binary64_pairs_to_header_and_one_pair",
      pair_payload_bytes=16,input_bytes=48,output_bytes=32,
      operation="EFT_difference_candidate_not_scene_length_or_phase",root_packet_binding_proven=False)
]
NAMES={"Blender/tests/exp005_blender_gpu.py":("split_double","texture_data","native_shader","dispatch"),
       "Blender/tests/exp005_gpu_pack.py":("pack_paths",)}
# Independently closed anchors, not accepted from arbitrary reported facts.
ANCHORS={
 "Blender/tests/exp005_blender_gpu.py": ["SHADER=", "def split_double(", "hi=struct.unpack(", "lo=struct.unpack(", "def texture_data(", "a,b=split_double(value)", "def native_shader(", "def dispatch(", "format='RGBA32F'"],
 "Blender/tests/exp005_gpu_pack.py": ["def pack_paths(", "distance = finite_number(hit['distance_BU']", "offset = finite_number(path.get('reference_offset_BU'"],
 "Blender/shaders/exp005_shared_frontier.glsl": ["dvec4 raw4(", "return dvec4(texelFetch(hi", "double length=ray.length+distance;"],
 "Blender/shaders/exp005_phase_compensated_probe.glsl": ["double length = packDouble2x32(words.xy);", "double wavelength = packDouble2x32(words.zw);", "length<0.0lf"],
 "Blender/benchmarks/capacity_audit/axial_common_detector_pair64_ingress_v1.comp": ["uvec4 pairWords[3];", "incoming.header,uvec4(COMMIT_TAG,1u,3u,16u)", "outgoing.pairWords[0]=staged0;"],
 "Blender/benchmarks/capacity_audit/oblique_pair64_raw_guard_v2.comp": ["src.words.length()!=12 || dst.words.length()!=8", "double ah=packDouble2x32", "double al=packDouble2x32", "double bh=packDouble2x32", "double bl=packDouble2x32", "precise dvec2 p=sum2(ah,-bh);", "precise dvec2 q=sum2(al,-bl);"]
}


def source_proof(facts):
    assert set(facts)==set(SEALS)
    for path,s in SEALS.items():
        raw=(ROOT/path).read_bytes();assert len(raw)==s["bytes"] and hashlib.sha256(raw).hexdigest()==s["sha256"]
        v=facts[path];assert set(v)=={"sha256","bytes","anchors","functions"}
        assert v["sha256"]==s["sha256"]and v["bytes"]==s["bytes"]
        lines=raw.decode().splitlines()
        expected=[]
        for anchor in ANCHORS[path]:
            hits=[dict(line=i+1,text=line)for i,line in enumerate(lines)if anchor in line and not line.lstrip().startswith("//")]
            assert hits;expected.append(dict(anchor=anchor,hits=hits))
        assert v["anchors"]==expected
        funcs={}
        if path in NAMES:
            tree=ast.parse(raw.decode())
            for name in NAMES[path]:
                nn=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name];assert len(nn)==1
                n=nn[0];funcs[name]=dict(line=n.lineno,end_line=n.end_lineno,
                    AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest())
            if "split_double"in NAMES[path]:
                n=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=="split_double")
                assert [a.arg for a in n.args.args]==["value"]
                assert any(isinstance(x,ast.BinOp)and isinstance(x.op,ast.Sub)
                           and isinstance(x.left,ast.Name)and x.left.id=="value"
                           and isinstance(x.right,ast.Name)and x.right.id=="hi"for x in ast.walk(n))
                shader=next(n for n in tree.body if isinstance(n,ast.Assign)
                    and any(isinstance(t,ast.Name)and t.id=="SHADER"for t in n.targets))
                assert "exp005_blender_fields.glsl"in [x.value for x in ast.walk(shader)if isinstance(x,ast.Constant)]
        assert v["functions"]==funcs


def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==214787 and hashlib.sha256(raw).hexdigest()==PSHA
    receipt=json.loads(raw);pins=dict(receipt["code_doc_sha256"]);assert len(pins)==300
    for path,h in pins.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    d=capture(receipt["test_run"])["evidence"]
    wire,ref,orig,_,_=old["retained"]()
    pins[PARENT]=PSHA
    for path,s in SEALS.items():pins[path]=s["sha256"]
    return {x["id"]:x for x in d["records"]},wire,ref,orig,pins,d


def selector(k,e,wire,ref,orig,facts):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),wire_record_sha256=digest(wire[k]),
        reference_record_sha256=digest(ref[k]),original_record_sha256=digest(o),
        original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(q),
        source_facts_sha256=digest(facts))


def scope(r):
    assert r["backend"]==MODEL and r["scope"]=="STATIC_SOURCE_ABI_PLUS_CPU_WRONG_ALIAS_NOT_RUNTIME"
    assert r["promotion"]=="STOP_REAL_ADAPTER_SCENE_GUARD_PHASE_AND_COSTS"and r["full_costs"]=="UNKNOWN_NOT_ZERO"
    assert r["native_length"]is None and r["phase_error_bound"]is None
    for key in ("scene_admitted","phase_certified","wavelength_known","physical_reference_certified",
                "GPU_used","Bpy_used","shader_used","foreign_source_executed","source_uncertainty_cancelled"):
        assert r[key]is False,key
    for key in ("RN64_adds","RN32_casts","new_products","new_sqrt_calls","retained_numeric_replays"):assert r[key]==0,key


def verify_capture(d,verify_parent=True):
    e,wire,ref,orig,pins,parent=retained()
    if verify_parent:old["verify_capture"](parent)
    assert d["pins"]==pins
    source_proof(d["source_facts"]);facts=d["source_facts"]
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(e)
    eligible=stops=decodes=negative=0;meta=[]
    for rec in d["records"]:
        k=rec["id"];q=selector(k,e,wire,ref,orig,facts)
        assert rec["request"]==q;r=rec["result"];scope(r);p=e[k]["result"]
        assert r["request_sha256"]==digest(q)
        assert r["upstream_status"]==p["status"]and r["retained_canonical_status"]==p["retained_canonical_status"]
        if p["status"]!="STOP_SCALAR_PAIR_CONSUMPTION_LOSS":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"and r["diagnostic"]is None
            assert r["byte_decode_calls"]==r["decoded_scalar64_components"]==0;stops+=1;continue
        eligible+=1
        assert r["status"]=="STATIC_CONSUMER_ABI_UNBOUND"and r["reason"]=="no_implicit_adapter_or_runtime_admission"
        z=r["diagnostic"];assert z["routes"]==EXPECTED
        assert z["source_facts_sha256"]==digest(facts)and z["retained_scalar_gate"]==p["status"]
        assert (z["source"],z["detector"],z["units"])==("SOURCE0","DETECTOR0","scene_length")
        assert z["original_snapshot_sha256"]==digest(orig[k]["scene"])
        assert z["original_record_sha256"]==digest(orig[k])and z["reference_record_sha256"]==digest(ref[k])
        assert ref[k]["result"]["diagnostic"]["original_scene"]==orig[k]["scene"]
        assert ref[k]["result"]["diagnostic"]["original_query"]==orig[k]["scene_query"]
        assert len(z["packets"])==2
        for i,v in enumerate(z["packets"]):
            r0=p["diagnostic"]["attempts"][i]["result"];w=wire[k]["result"]["diagnostic"]["packets"][i]["result"]
            packet=w["packet_hex"];assert packet==r0["input_packet"]
            alias=pf(packet);Q=p32(packet[:8])+p32(packet[8:]) # Independent integer/rational IEEE proof.
            assert alias!=Q and pair(Q)==r0["exact_pair_sum"]
            expected=dict(bound=("lower","upper")[i],packet_hex=packet,packet_bytes=8,scalar64_alias_word=packet,
                CPU_scalar64_alias_value=pair(alias),retained_exact_pair_sum=pair(Q),alias_matches_pair=False,
                hypothetical_alias_length_negative=alias<0,
                retained_RN64_intermediate_error=r0["HOST_signed_intermediate_error"],
                retained_projection_status="STOP_PROJECTION_LOSS",retained_scalar_candidate=r0["candidate_word32"])
            assert v==expected;negative+=alias<0
            meta.append(dict(record_id=k,bound=v["bound"],packet=packet,
                             alias_scalar64=str(alias),pair_sum=str(Q),hypothetical_negative=alias<0))
        assert r["byte_decode_calls"]==r["decoded_scalar64_components"]==2;decodes+=2
    assert (eligible,stops,decodes)==(2,14,4)
    assert len(d["invalid"])==8
    for x in d["invalid"]:
        r=x["result"];scope(r)
        assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"and r["diagnostic"]is None
        assert r["byte_decode_calls"]==r["decoded_scalar64_components"]==0
    return dict(status="PASS",eligible_scenes=eligible,upstream_STOP=stops,scene_admitted=0,
        routes=4,source_files=6,byte_decode_calls=decodes,alias_mismatches=4,hypothetical_negative_aliases=negative,
        selectors_rejected=8,inherited_pins=len(pins),new_RN_operations=0,new_products=0,new_sqrt_calls=0,
        retained_numeric_replays=0,GPU_used=False,foreign_source_executed=False,by_packet=meta)


def mutations(d):
    k=next(i for i,x in enumerate(d["records"])if x["result"]["diagnostic"]is not None)
    rejected=0
    for n in range(8):
        a=copy.deepcopy(d);r=a["records"][k]["result"];z=r["diagnostic"]
        path="Blender/tests/exp005_blender_gpu.py"
        if n==0:a["source_facts"][path]["sha256"]="0"*64
        elif n==1:a["source_facts"][path]["anchors"][0]["hits"][0]["line"]+=1
        elif n==2:a["source_facts"][path]["functions"]["split_double"]["AST_sha256"]="0"*64
        elif n==3:z["packets"][0]["CPU_scalar64_alias_value"]=z["packets"][0]["retained_exact_pair_sum"]
        elif n==4:z["routes"][0]["root_packet_binding_proven"]=True
        elif n==5:z["routes"][2]["pair_payload_bytes"]=8
        elif n==6:r["phase_certified"]=True
        else:r["GPU_used"]=True
        try:verify_capture(a,verify_parent=False)
        except (AssertionError,ValueError,KeyError,TypeError,IndexError):rejected+=1
        else:raise AssertionError("mutation_accepted:"+str(n))
    return rejected


def run():
    import oblique_consumer_ABI_static_v1 as c
    e,wire,ref,orig,pins,_,facts=c.retained();records=[]
    for k in e:
        q=c.selector(k,e,wire,ref,orig,facts)
        records.append(dict(id=k,request=q,result=c._audit(q,e,wire,ref,orig,facts)))
    k=next(x["id"]for x in records if x["result"]["diagnostic"]is not None)
    q=c.selector(k,e,wire,ref,orig,facts);invalid=[]
    for n in range(8):
        bad=dict(q)
        key=("policy","backend","parent_record_sha256","wire_record_sha256","source_facts_sha256",
             "original_snapshot_sha256","original_query_sha256","reference_record_sha256")[n]
        bad[key]="unsealed_or_implicit_adapter"
        invalid.append(dict(request=bad,result=c._audit(bad,e,wire,ref,orig,facts)))
    d=dict(records=records,invalid=invalid,pins=pins,source_facts=facts)
    summary=verify_capture(d);summary["mutations_rejected"]=mutations(d)
    assert summary["mutations_rejected"]==8
    print(json.dumps(dict(status="PASS",summary=summary,evidence=d),sort_keys=True,separators=(",",":")))


if __name__=="__main__":run()
