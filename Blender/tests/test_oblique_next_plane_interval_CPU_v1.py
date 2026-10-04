"""New plane arithmetic only; previous CPU captures are sealed input data."""
from pathlib import Path
from fractions import Fraction as F
import ast,base64,hashlib,importlib.util,json,struct,sys,traceback,zlib
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-FIRST-HIT-REFLECTION-INTERVAL-CPU-001-CODEX.json"
PSHA="8f288bc3ce76fa153243aa010f915a85b4fd1d32e27de963dfb812dbf21c6138"
PREVIOUS="Blender/benchmarks/capacity_audit/oblique_first_hit_reflection_interval_CPU_v1.py"
CORE="Blender/benchmarks/capacity_audit/oblique_next_plane_interval_CPU_v1.py"
GI="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"

def sha(b):return hashlib.sha256(b).hexdigest()
def capture(c):
    assert c["rc"]==0 and not c["timed_out"]
    decoder=zlib.decompressobj()
    raw=decoder.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),1048577)
    assert len(raw)<=1048576 and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data
    assert len(raw)==c["stdout_bytes"] and sha(raw)==c["stdout_sha256"]
    return json.loads(raw)
def pair(x):return tuple(F(*v) for v in x)
def boxes(v):return tuple(pair(x) for x in v)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return (a[0]*b[0]+a[1]*b[1])+a[2]*b[2]
def floats(words):return tuple(struct.unpack("<f",struct.pack("<I",w))[0] for w in words)

def run(report):
    raw=(ROOT/PARENT).read_bytes();assert sha(raw)==PSHA
    parent=json.loads(raw);pins=dict(parent["code_doc_sha256"]);pins[PARENT]=PSHA
    assert len(pins)==410
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    d=capture(parent["final_test_run_after_EOF_correction"])
    inputs={x["id"]:x["result"]["packet"] for x in capture(json.loads((ROOT/GI).read_bytes())["test_run"])["evidence"]["positive"]}
    names={"require","power2","MAX64","round_out","Interval","scalar32","sub","cross","dot","raw_vector"}
    def trees(path):
        result={}
        for n in ast.parse((ROOT/path).read_text(encoding="utf-8")).body:
            name=getattr(n,"name",None)
            if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name):name=n.targets[0].id
            if name in names:result[name]=ast.dump(n,include_attributes=False)
        return result
    assert trees(PREVIOUS)==trees(CORE) and len(trees(CORE))==10
    spec=importlib.util.spec_from_file_location("own_new_plane",ROOT/CORE)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    report.update(context_pins=pins,cases=[],prior_nonzero_error_rows_preserved=d["prior_nonzero_error_rows_preserved_as_data"])
    assert len(report["prior_nonzero_error_rows_preserved"])==16
    comparisons=[];stops={};contact=0
    for c in d["cases"]:
        packet=inputs[c["case"]];raw=bytes.fromhex(packet["buffer_hex"]);words=struct.unpack("<%dI"%(len(raw)//4),raw)
        assert sha(raw)==c["input_sha256"]==packet["manifest"]["buffer_sha256"]
        assert c["scene_sha256"]==packet["manifest"]["scene_sha256"] and c["query_sha256"]==packet["manifest"]["query_sha256"]
        n=words[4];base=10+n;ids=list(words[10:10+n]);assert len(ids)==len(set(ids))
        sources=[]
        for sid,s in enumerate(c["sources"]):
            assert s["source_id"]=="S"+str(sid)
            p=boxes(s["result"]["point_interval"]);r=boxes(s["result"]["reflected_direction_interval"])
            exact=lambda field:tuple(F(*x["exact"]) for x in s["CPU_new_graph_vs_exact"][field])
            candidate=lambda field:tuple(struct.unpack("<d",bytes.fromhex(x["candidate_binary64_le"]))[0] for x in s["CPU_new_graph_vs_exact"][field])
            pq,rq=exact("point"),exact("reflected_direction")
            pf,rf=candidate("point"),candidate("reflected_direction")
            rows=[]
            for index,pid in enumerate(ids):
                tri=tuple(tuple(words[base+12+9*index+j:base+15+9*index+j]) for j in (0,3,6))
                result=m.enclose_plane(p,r,tri);stops[result["status"]]=stops.get(result["status"],0)+1
                assert not result["triangle_hit_certified"] and not result["launch_exclusion_allowed"] and not result["ignored_primitive_ids"]
                af,bf,cf=[floats(v) for v in tri];a,b,cc=[tuple(F.from_float(x) for x in v) for v in (af,bf,cf)]
                nq=cross(sub(b,a),sub(cc,a));numer=dot(nq,sub(a,pq));denom=dot(nq,rq)
                ref=dict(numerator=[numer.numerator,numer.denominator],denominator=[denom.numerator,denom.denominator])
                if "numerator_interval" in result:
                    lo,hi=pair(result["numerator_interval"]);assert lo<=numer<=hi
                    lo,hi=pair(result["denominator_interval"]);assert lo<=denom<=hi
                if "parameter_interval" in result:
                    assert denom!=0
                    expected=numer/denom;nf=cross(sub(bf,af),sub(cf,af));numf=dot(nf,sub(af,pf));denf=dot(nf,rf)
                    assert denf!=0
                    value=numf/denf;candidate_q=F.from_float(value)
                    lo,hi=pair(result["parameter_interval"]);assert lo<=expected<=hi and lo<=candidate_q<=hi
                    error=candidate_q-expected;radius=max(abs(candidate_q-lo),abs(hi-candidate_q))
                    assert abs(error)<=radius
                    ref.update(parameter=[expected.numerator,expected.denominator],candidate_binary64_le=struct.pack("<d",value).hex(),
                               signed_error=[error.numerator,error.denominator],error_radius=[radius.numerator,radius.denominator])
                    comparisons.append(dict(case=c["case"],source_id=s["source_id"],primitive_id=pid,**ref))
                if pid==s["primitive_id"]:
                    assert result["status"]=="STOP_LAUNCH_OR_CONTACT_ZERO_POSSIBLE"
                    assert numer==0;contact+=1
                rows.append(dict(primitive_id=pid,triangle_words=tri,result=result,reference=ref))
            assert [x["primitive_id"] for x in rows]==ids
            sources.append(dict(source_id=s["source_id"],previous_primitive_id=s["primitive_id"],point_interval=s["result"]["point_interval"],
                                reflected_direction_interval=s["result"]["reflected_direction_interval"],rows=rows))
        report["cases"].append(dict(case=c["case"],input_sha256=c["input_sha256"],scene_sha256=c["scene_sha256"],query_sha256=c["query_sha256"],
                                   primitive_ids=ids,sources=sources,plane_rows_enumerated_only_NOT_ALL_triangle_hit_coverage=True))
    word=lambda x:struct.unpack("<I",struct.pack("<f",x))[0]
    vec=lambda v:tuple(word(x) for x in v)
    pt=lambda v:tuple((F(x),F(x)) for x in v)
    def tri_at(z):return tuple(vec(v) for v in ((-1,-1,z),(1,-1,z),(0,1,z)))
    point,direction=pt((0,0,0)),pt((0,0,1))
    controls={}
    for label,z in [("exact_self",0),("forward_tiny_gap_parameter",2**-60),("negative_plane",-1)]:
        controls[label]=m.enclose_plane(point,direction,tri_at(z))
    assert controls["exact_self"]["status"]=="STOP_LAUNCH_OR_CONTACT_ZERO_POSSIBLE"
    lo,hi=pair(controls["forward_tiny_gap_parameter"]["parameter_interval"]);assert 0<lo<=F(1,2**60)<=hi
    assert controls["negative_plane"]["status"].startswith("CONDITIONAL_NEGATIVE_")
    wide=((F(0),F(0)),(F(0),F(0)),(F(-1,2**59),F(1,2**59)))
    controls["gap_swallowed_by_point_uncertainty"]=m.enclose_plane(wide,direction,tri_at(2**-60))
    assert controls["gap_swallowed_by_point_uncertainty"]["status"]=="STOP_LAUNCH_OR_CONTACT_ZERO_POSSIBLE"
    controls["parallel"]=m.enclose_plane(point,pt((1,0,0)),tri_at(1))
    controls["coplanar"]=m.enclose_plane(point,pt((1,0,0)),tri_at(0))
    controls["direction_denominator_sign_uncertain"]=m.enclose_plane(point,((F(1),F(1)),(F(0),F(0)),(F(-1),F(1))),tri_at(1))
    controls["degenerate"]=m.enclose_plane(point,direction,(vec((0,0,0)),)*3)
    assert all(controls[x]["status"].startswith("STOP_") for x in ("parallel","coplanar","direction_denominator_sign_uncertain","degenerate"))
    report["fabricated_controls"]=dict(scope="FABRICATED_NOT_ORIGINAL_SCENE_OR_GPU",results=controls)
    bad=[("box_list",lambda:m.enclose_plane(list(point),direction,tri_at(0))),
         ("bool_endpoint",lambda:m.enclose_plane(((True,F(0)),)+point[1:],direction,tri_at(0))),
         ("reversed_box",lambda:m.enclose_plane(((F(1),F(0)),)+point[1:],direction,tri_at(0))),
         ("capacity",lambda:m.enclose_plane(((F(1,2**4097),F(1,2**4097)),)+point[1:],direction,tri_at(0))),
         ("nonbinary_endpoint",lambda:m.enclose_plane(((F(1,3),F(1,3)),)+point[1:],direction,tri_at(0))),
         ("zero_possible_direction",lambda:m.enclose_plane(point,pt((0,0,0)),tri_at(0))),
         ("triangle_shape",lambda:m.enclose_plane(point,direction,list(tri_at(0)))),
         ("bool_raw_word",lambda:m.enclose_plane(point,direction,((True,0,0),)*3)),
         ("nan_raw_word",lambda:m.enclose_plane(point,direction,((0x7fc00001,0,0),)*3)),
         ("subnormal_raw_word",lambda:m.enclose_plane(point,direction,((1,0,0),)*3)),
         ("negative_zero_word",lambda:m.enclose_plane(point,direction,((0x80000000,0,0),)*3)),
         ("raw_domain",lambda:m.enclose_plane(point,direction,((word(2**21),0,0),)*3))]
    report["negatives"]=[]
    for label,action in bad:
        try:action()
        except ValueError as e:report["negatives"].append(dict(id=label,reason=str(e)))
        else:raise AssertionError("accepted:"+label)
    report["comparisons"]=comparisons
    report["summary"]=dict(cases=len(report["cases"]),sources=12,plane_rows=sum(stops.values()),status_counts=stops,
                           parameter_comparisons=len(comparisons),new_nonzero_errors_preserved=sum(F(*x["signed_error"])!=0 for x in comparisons),
                           previous_contact_STOP=contact,prior_nonzero_rows_preserved=16,negatives=len(bad),fabricated_controls=len(controls),
                           context_pins=410,arithmetic_AST_copies=10,old_producer_executions=0,first_hit_replays=0,
                           triangle_barycentric_queries=0,compiler_calls=0,GPU_used=False,native_precision_certified=False,phase_error_bound=None)
    report["status"]="PASS_CPU_PLANE_ENCLOSURES_ONLY_CONTACT_TRIANGLE_NATIVE_PHASE_STOP"
if __name__=="__main__":
    report=dict(status="IN_PROGRESS",GPU_used=False,JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
    try:run(report)
    except Exception as e:
        report.update(status="FAIL_RETAINED",error=str(e),traceback=traceback.format_exc())
        print(json.dumps(report,allow_nan=False));sys.exit(1)
    print(json.dumps(report,allow_nan=False))
