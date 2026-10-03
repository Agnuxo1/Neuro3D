"""Own visibility suite over sealed captures and explicit new synthetic obstacles."""
import copy,json,sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks/capacity_audit"))
import oblique_segment_visibility_CPU_v1 as m
def enc(v):return [[x.numerator,x.denominator]for x in map(F,v)]
def run():
    e=m.load_evidence();runs=[]
    def add(id,s,q,r,expected,reason=None,public=False):
        out=m.audit(m.MODEL,m.selector(id))if public else m._audit(s,q,r)
        assert out["status"]==expected,(id,out)
        if reason is not None:assert out["reason"]==reason,(id,out["reason"])
        assert not out["GPU_launch_allowed"]and not out["GPU_executed"]and not out["scene_authenticated"]
        assert not out["physical_field_certified"]and out["producer_replays"]==out["RN64_operations"]==out["compiler_calls"]==0
        if expected=="STOP":assert out["visibility_rows"]==[]and out["SOURCE_segments_admitted"]==0
        runs.append(dict(id=id,scene=s,request=q,parent_result=r,result=out))
    good=[k for k,r in e["results"].items()if r["status"]!="STOP"]
    assert len(e["inputs"])==28 and len(good)==4
    for k,inp in e["inputs"].items():
        expected="STOP"if e["results"][k]["status"]=="STOP"else"CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY"
        add(k,inp["scene"],inp["request"],e["results"][k],expected,public=k=="oblique")
    for base in("oblique","tiny_gap_2m60"):
        for kind in("interior_same_object","vertex_contact","other_zero_contact","duplicate_endpoint","outside_segment","coplanar"):
            inp=copy.deepcopy(e["inputs"][base]);s=inp["scene"];q=inp["request"];r=copy.deepcopy(e["results"][base])
            gap=m.f(s["triangles"][1]["vertices_BU"][0][0]);x=gap/2;y=gap/2;z=F(1,4)
            verts=[(x,y-gap/8,F(1,8)),(x,y+gap/8,F(1,8)),(x,y,F(3,8))]
            if kind=="vertex_contact":verts=[(x,y,z),(x,y+gap/8,F(1,8)),(x,y+gap/8,F(3,8))]
            if kind=="other_zero_contact":
                x=gap/4;y=gap/4;verts=[(x,y-gap/8,F(1,8)),(x,y+gap/8,F(1,8)),(x,y,F(3,8))]
            if kind=="duplicate_endpoint":verts=[tuple(m.vec(v))for v in s["triangles"][1]["vertices_BU"]]
            if kind=="outside_segment":verts=[(2*gap,0,0),(2*gap,3,0),(2*gap,0,3)]
            if kind=="coplanar":verts=[(0,0,z),(3,0,z),(0,3,z)]
            s["triangles"].append(dict(primitive_id=2,object_id=s["triangles"][1]["object_id"],vertices_BU=[enc(v)for v in verts]))
            q["original_scene_sha256"]=m.digest(s);r["original_scene_sha256"]=m.digest(s);r["literal_request_sha256"]=m.digest(q)
            # Explicit NEW declared synthetic scene; copied candidate paths are NOT a native replay/certificate.
            reason="coplanar_ambiguity"if kind=="coplanar"else"unexpected_segment_contact"
            expected="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY"if kind=="outside_segment"else"STOP"
            add(base+"/"+kind,s,q,r,expected,None if kind=="outside_segment"else reason)
    for kind in("broken_continuity","wrong_squared","stale_scene","zero_SOURCE_cap"):
        inp=copy.deepcopy(e["inputs"]["oblique"]);s=inp["scene"];q=inp["request"];r=copy.deepcopy(e["results"]["oblique"])
        reason={"broken_continuity":"continuity","wrong_squared":"positive_segment_squared","stale_scene":"scene_binding","zero_SOURCE_cap":"SOURCE_cap"}[kind]
        if kind=="broken_continuity":r["paths"][0]["segments"][1]["from_BU"][0]=[2,1]
        if kind=="wrong_squared":r["paths"][0]["segments"][0]["squared_BU2"]=[1,1]
        if kind=="stale_scene":s["triangles"][0]["object_id"]="changed"
        if kind=="zero_SOURCE_cap":
            q["source_width_caps_rad"][0]=[0,1];r["literal_request_sha256"]=m.digest(q)
        add(kind,s,q,r,"STOP",reason)
    negatives=[]
    for label,model,q in(("wrong_model","wrong",m.selector("oblique")),
        ("extra_selector",m.MODEL,dict(m.selector("oblique"),epsilon=1)),
        ("stale_selector",m.MODEL,dict(m.selector("oblique"),parent_sha256="0"*64)),
        ("unknown_case",m.MODEL,m.selector("unknown"))):
        out=m.audit(model,q);assert out["status"]=="STOP"and out["visibility_rows"]==[]
        negatives.append(dict(id=label,model=model,request=q,result=out))
    assert len(runs)==44 and sum(v["result"]["status"]!="STOP"for v in runs)==6
    print(json.dumps(dict(status="PASS",groups=4,runs=runs,selector_negatives=negatives,
        census=dict(runs=44,admitted=6,STOP=38,selector_STOP=4,sealed_parent_STOP=24,
        synthetic_new_scenes=12,GPU_launch_allowed=False,producer_replays=0,RN64_operations=0)),sort_keys=True))
if __name__=="__main__":run()
