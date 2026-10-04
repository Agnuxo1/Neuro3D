"""New next-triangle computation only; retained scene/captures are data."""
from pathlib import Path
from fractions import Fraction as F
import ast,base64,hashlib,importlib.util,json,struct,sys,traceback,zlib
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-NEXT-PLANE-INTERVAL-CPU-001-CODEX.json"
PSHA="8f49e627a916aa01d874d5851107c1a5a95396e2c5073f2d1cd83822c3e5cf5d"
PREVIOUS="Blender/benchmarks/capacity_audit/oblique_next_plane_interval_CPU_v1.py"
CORE="Blender/benchmarks/capacity_audit/oblique_next_triangle_interval_CPU_v1.py"
REFLECTION="coordinacion/respuestas/PRECISION-FIRST-HIT-REFLECTION-INTERVAL-CPU-001-CODEX.json"
GI="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"
def sha(b):return hashlib.sha256(b).hexdigest()
def capture(c):
    assert c["rc"]==0 and not c["timed_out"]
    z=zlib.decompressobj();b=z.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),1048577)
    assert len(b)<=1048576 and z.eof and not z.unconsumed_tail and not z.unused_data
    assert len(b)==c["stdout_bytes"] and sha(b)==c["stdout_sha256"]
    return json.loads(b)
def pair(x):return tuple(F(*v) for v in x)
def boxes(v):return tuple(pair(x) for x in v)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return (a[0]*b[0]+a[1]*b[1])+a[2]*b[2]
def vals(words):return tuple(struct.unpack("<f",struct.pack("<I",w))[0] for w in words)
def mt(origin,direction,tri):
    a,b,c=tri;e1,e2=sub(b,a),sub(c,a);p=cross(direction,e2);det=dot(e1,p)
    if det==0:return dict(determinant=det)
    tvec=sub(origin,a);u=dot(tvec,p)/det;q=cross(tvec,e1);v=dot(direction,q)/det;t=dot(e2,q)/det
    return dict(determinant=det,parameter=t,u=u,v=v,uv=u+v)

def run(report):
    raw=(ROOT/PARENT).read_bytes();assert sha(raw)==PSHA
    parent=json.loads(raw);pins=dict(parent["code_doc_sha256"]);pins[PARENT]=PSHA
    assert len(pins)==414
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    prior=capture(parent["test_run"])
    rp=capture(json.loads((ROOT/REFLECTION).read_bytes())["final_test_run_after_EOF_correction"])
    reflections={x["case"]:x for x in rp["cases"]}
    inputs={x["id"]:x["result"]["packet"] for x in capture(json.loads((ROOT/GI).read_bytes())["test_run"])["evidence"]["positive"]}
    names={"require","power2","MAX64","round_out","Interval","scalar32","sub","cross","dot","raw_vector","box_vector"}
    def trees(path):
        result={}
        for n in ast.parse((ROOT/path).read_text(encoding="utf-8")).body:
            name=getattr(n,"name",None)
            if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name):name=n.targets[0].id
            if name in names:result[name]=ast.dump(n,include_attributes=False)
        return result
    assert trees(CORE)==trees(PREVIOUS) and len(trees(CORE))==11
    spec=importlib.util.spec_from_file_location("own_next_triangle",ROOT/CORE)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    report.update(context_pins=pins,cases=[],prior_nonzero_error_rows_preserved=prior["prior_nonzero_error_rows_preserved"])
    assert len(report["prior_nonzero_error_rows_preserved"])==16
    errors=[];stats={};comparisons=0;contacts=0
    for case in prior["cases"]:
        packet=inputs[case["case"]];raw=bytes.fromhex(packet["buffer_hex"]);w=struct.unpack("<%dI"%(len(raw)//4),raw)
        assert sha(raw)==case["input_sha256"]==packet["manifest"]["buffer_sha256"]
        assert case["primitive_ids"]==list(w[10:10+w[4]])
        assert case["scene_sha256"]==packet["manifest"]["scene_sha256"] and case["query_sha256"]==packet["manifest"]["query_sha256"]
        base=10+w[4];sources=[]
        for sid,s in enumerate(case["sources"]):
            previous=reflections[case["case"]]["sources"][sid]
            assert s["source_id"]==previous["source_id"]=="S"+str(sid)
            assert s["previous_primitive_id"]==previous["primitive_id"]
            assert s["point_interval"]==previous["result"]["point_interval"] and s["reflected_direction_interval"]==previous["result"]["reflected_direction_interval"]
            exact=lambda k:tuple(F(*x["exact"]) for x in previous["CPU_new_graph_vs_exact"][k])
            candidate=lambda k:tuple(struct.unpack("<d",bytes.fromhex(x["candidate_binary64_le"]))[0] for x in previous["CPU_new_graph_vs_exact"][k])
            oq,dq=exact("point"),exact("reflected_direction")
            of,df=candidate("point"),candidate("reflected_direction")
            rows=[]
            for index,oldrow in enumerate(s["rows"]):
                pid=oldrow["primitive_id"];assert pid==case["primitive_ids"][index]
                tri=tuple(tuple(w[base+12+9*index+j:base+15+9*index+j]) for j in (0,3,6))
                assert [list(v) for v in tri]==oldrow["triangle_words"]
                tf=tuple(vals(v) for v in tri);tq=tuple(tuple(F.from_float(x) for x in v) for v in tf)
                result=m.enclose_triangle(boxes(s["point_interval"]),boxes(s["reflected_direction_interval"]),tri)
                stats[result["status"]]=stats.get(result["status"],0)+1
                exact_result,control=mt(oq,dq,tq),mt(of,df,tf);refs={}
                for field,value in exact_result.items():
                    lo,hi=pair(result[field+"_interval"])
                    actual=F.from_float(control[field]);assert lo<=value<=hi and lo<=actual<=hi
                    err=actual-value;radius=max(abs(actual-lo),abs(hi-actual));assert abs(err)<=radius
                    refs[field]=dict(exact=[value.numerator,value.denominator],candidate_binary64_le=struct.pack("<d",control[field]).hex(),
                                     signed_error=[err.numerator,err.denominator],error_radius=[radius.numerator,radius.denominator])
                    comparisons+=1
                    if err:errors.append(dict(case=case["case"],source_id=s["source_id"],primitive_id=pid,field=field,signed_error=[err.numerator,err.denominator]))
                if "parameter" in exact_result:
                    assert exact_result["parameter"]==F(*oldrow["reference"]["parameter"])
                if result["status"]=="CONDITIONAL_TRIANGLE_INTERIOR_HIT":
                    assert exact_result["parameter"]>0 and exact_result["u"]>0 and exact_result["v"]>0 and exact_result["uv"]<1
                if result["status"]=="CONDITIONAL_TRIANGLE_MISS":
                    assert exact_result["parameter"]<0 or exact_result["u"]<0 or exact_result["v"]<0 or exact_result["uv"]>1
                if pid==s["previous_primitive_id"]:
                    assert result["status"]=="STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED"
                    assert exact_result["parameter"]==0;contacts+=1
                assert not result["launch_exclusion_allowed"] and not result["ignored_primitive_ids"] and not result["GPU_launch_allowed"]
                rows.append(dict(primitive_id=pid,triangle_words=tri,result=result,reference=refs,previous_plane_result=oldrow["result"]))
            assert [x["primitive_id"] for x in rows]==case["primitive_ids"]
            sources.append(dict(source_id=s["source_id"],previous_primitive_id=s["previous_primitive_id"],point_interval=s["point_interval"],
                                reflected_direction_interval=s["reflected_direction_interval"],rows=rows))
        report["cases"].append(dict(case=case["case"],input_sha256=case["input_sha256"],scene_sha256=case["scene_sha256"],query_sha256=case["query_sha256"],
                                   primitive_ids=case["primitive_ids"],sources=sources,complete_visibility_certified=False))
    word=lambda x:struct.unpack("<I",struct.pack("<f",x))[0]
    vec=lambda v:tuple(word(x) for x in v)
    pt=lambda v:tuple((F(x),F(x)) for x in v)
    tri_at=lambda z:tuple(vec(v) for v in ((-1,-1,z),(1,-1,z),(0,1,z)))
    point,direction=pt((0,0,0)),pt((0,0,1));controls={}
    controls["interior"]=m.enclose_triangle(point,direction,tri_at(1))
    controls["previous_zero_contact"]=m.enclose_triangle(point,direction,tri_at(0))
    controls["vertex"]=m.enclose_triangle(pt((-1,-1,0)),direction,tri_at(1))
    controls["edge"]=m.enclose_triangle(pt((0,-1,0)),direction,tri_at(1))
    controls["outside_triangle"]=m.enclose_triangle(pt((3,0,0)),direction,tri_at(1))
    controls["negative_t"]=m.enclose_triangle(point,direction,tri_at(-1))
    controls["tiny_forward"]=m.enclose_triangle(point,direction,tri_at(2**-60))
    controls["point_uncertainty_covers_gap"]=m.enclose_triangle(((F(0),F(0)),(F(0),F(0)),(F(-1,2**59),F(1,2**59))),direction,tri_at(2**-60))
    controls["uncertain_determinant"]=m.enclose_triangle(point,((F(1),F(1)),(F(0),F(0)),(F(-1),F(1))),tri_at(1))
    controls["parallel"]=m.enclose_triangle(point,pt((1,0,0)),tri_at(1))
    controls["coplanar"]=m.enclose_triangle(point,pt((1,0,0)),tri_at(0))
    controls["degenerate"]=m.enclose_triangle(point,direction,(vec((0,0,0)),)*3)
    t=tri_at(1);controls["triangle_reversal"]=m.enclose_triangle(point,direction,(t[0],t[2],t[1]))
    for label in ("interior","tiny_forward","triangle_reversal"):assert controls[label]["status"]=="CONDITIONAL_TRIANGLE_INTERIOR_HIT"
    for label in ("outside_triangle","negative_t"):assert controls[label]["status"]=="CONDITIONAL_TRIANGLE_MISS"
    for label in ("previous_zero_contact","vertex","edge","point_uncertainty_covers_gap","uncertain_determinant","parallel","coplanar","degenerate"):assert controls[label]["status"].startswith("STOP_")
    report["fabricated_controls"]=dict(scope="FABRICATED_NOT_ORIGINAL_SCENE_OR_GPU",results=controls)
    bad=[("box_list",lambda:m.enclose_triangle(list(point),direction,tri_at(1))),
         ("bool_endpoint",lambda:m.enclose_triangle(((True,F(0)),)+point[1:],direction,tri_at(1))),
         ("reversed_box",lambda:m.enclose_triangle(((F(1),F(0)),)+point[1:],direction,tri_at(1))),
         ("capacity",lambda:m.enclose_triangle(((F(1,2**4097),F(1,2**4097)),)+point[1:],direction,tri_at(1))),
         ("nonbinary_endpoint",lambda:m.enclose_triangle(((F(1,3),F(1,3)),)+point[1:],direction,tri_at(1))),
         ("zero_direction",lambda:m.enclose_triangle(point,pt((0,0,0)),tri_at(1))),
         ("triangle_shape",lambda:m.enclose_triangle(point,direction,list(tri_at(1)))),
         ("bool_word",lambda:m.enclose_triangle(point,direction,((True,0,0),)*3)),
         ("nan_word",lambda:m.enclose_triangle(point,direction,((0x7fc00001,0,0),)*3)),
         ("subnormal_word",lambda:m.enclose_triangle(point,direction,((1,0,0),)*3)),
         ("negative_zero_word",lambda:m.enclose_triangle(point,direction,((0x80000000,0,0),)*3)),
         ("domain_word",lambda:m.enclose_triangle(point,direction,((word(2**21),0,0),)*3)),
         ("word_over",lambda:m.enclose_triangle(point,direction,((2**32,0,0),)*3)),
         ("epsilon_override",lambda:m.enclose_triangle(point,direction,tri_at(1),epsilon=F(1,2**60))),
         ("primitive_ignore_override",lambda:m.enclose_triangle(point,direction,tri_at(1),ignored_primitive_id=1))]
    report["negatives"]=[]
    for label,action in bad:
        try:action()
        except (ValueError,TypeError) as e:report["negatives"].append(dict(id=label,error_type=type(e).__name__,reason=str(e)))
        else:raise AssertionError("accepted:"+label)
    report["new_nonzero_errors_preserved"]=errors
    report["summary"]=dict(cases=len(report["cases"]),sources=12,triangle_rows=sum(stats.values()),status_counts=stats,
                           scalar_comparisons=comparisons,new_nonzero_errors_preserved=len(errors),previous_contact_STOP=contacts,
                           prior_nonzero_rows_preserved=16,negatives=len(bad),fabricated_controls=len(controls),context_pins=414,
                           arithmetic_AST_copies=11,old_producer_executions=0,old_first_hit_replays=0,old_plane_replays=0,
                           new_next_triangle_queries=sum(stats.values()),compiler_calls=0,GPU_used=False,native_precision_certified=False,phase_error_bound=None)
    report["status"]="PASS_CPU_NEXT_TRIANGLE_ENCLOSURES_ONLY_CONTACT_NATIVE_PHASE_STOP"
if __name__=="__main__":
    report=dict(status="IN_PROGRESS",GPU_used=False,JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")
    try:run(report)
    except Exception as e:
        report.update(status="FAIL_RETAINED",error=str(e),traceback=traceback.format_exc())
        print(json.dumps(report,allow_nan=False));sys.exit(1)
    print(json.dumps(report,allow_nan=False))
