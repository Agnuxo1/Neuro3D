"""Independent rational determinant/certificate oracle. No imports or calls to producer."""
import ast,base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001"
MODEL="precision-oblique-common-detector-length-CPU-v1"
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def rat(v):
    assert type(v)is list and len(v)==2 and all(type(x)is int for x in v)
    assert v[1]>0 and max(abs(v[0]).bit_length(),v[1].bit_length())<=128
    x=F(*v);assert abs(x)<=10**6;return x
def vec(v):
    assert type(v)is list and len(v)==3;return tuple(rat(x) for x in v)
def unbounded(v):return F(*v)
def V(v):return tuple(unbounded(x) for x in v)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def det(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-b[0]*(a[1]*c[2]-a[2]*c[1])+c[0]*(a[1]*b[2]-a[2]*b[1])
def normal(e,f):return (det((1,0,0),e,f),det((0,1,0),e,f),det((0,0,1),e,f))
def trace(o,d,tris,previous):
    candidates=[]
    for pid,a,e,f,n in tris:
        rhs=sub(a,o);ne=tuple(-x for x in e);nf=tuple(-x for x in f);D=det(d,ne,nf)
        if D==0:
            assert dot(sub(o,a),n)!=0
            continue
        t=det(rhs,ne,nf)/D;u=det(d,rhs,nf)/D;v=det(d,ne,rhs)/D
        if t<0 or min(u,v)<0 or u+v>1:continue
        if t==0:
            assert pid==previous
            continue
        candidates.append((t,pid,tuple(o[i]+t*d[i] for i in range(3)),n,(1-u-v,u,v)))
    assert candidates
    t=min(x[0] for x in candidates);nearest=[c for c in candidates if c[0]==t];assert len(nearest)==1
    return nearest[0]

def preflight(i):
    assert type(i["model"])is str and i["model"]==MODEL
    s=i["scene"];q=i["request"]
    assert type(s)is dict and set(s)=={"schema","units","triangles","sources"}
    assert s["schema"]=="precision-oblique-declared-scene-v1" and s["units"]=="BU"
    assert type(q)is dict and set(q)=={"original_scene_sha256","source_ids","root_primitive_id","detector_primitive_id","detector_point_BU",
        "lambda_BU","reference_BU","source_width_caps_rad","relative_width_cap_rad"}
    assert type(q["original_scene_sha256"])is str and q["original_scene_sha256"]==digest(s)
    assert type(q["source_ids"])is list and q["source_ids"]==["S0","S1"]
    assert all(type(q[k])is int for k in ("root_primitive_id","detector_primitive_id"))
    assert q["root_primitive_id"]!=q["detector_primitive_id"]
    target=vec(q["detector_point_BU"]);wave=rat(q["lambda_BU"]);ref=rat(q["reference_BU"]);assert wave>0
    assert type(q["source_width_caps_rad"])is list and len(q["source_width_caps_rad"])==2
    caps=[rat(x) for x in q["source_width_caps_rad"]];rcap=rat(q["relative_width_cap_rad"]);assert min(caps+[rcap])>=0
    assert type(s["triangles"])is list and 2<=len(s["triangles"])<=4
    tris=[];ids=[]
    for tr in s["triangles"]:
        assert type(tr)is dict and set(tr)=={"primitive_id","object_id","vertices_BU"}
        pid=tr["primitive_id"];assert type(pid)is int and 0<=pid<2**31 and pid not in ids;ids.append(pid)
        assert type(tr["object_id"])is str and 0<len(tr["object_id"])<=64
        assert type(tr["vertices_BU"])is list and len(tr["vertices_BU"])==3
        a,b,c=[vec(v) for v in tr["vertices_BU"]];e=sub(b,a);f=sub(c,a);n=normal(e,f);assert dot(n,n)>0
        tris.append((pid,a,e,f,n))
    assert q["root_primitive_id"]in ids and q["detector_primitive_id"]in ids
    assert type(s["sources"])is list and len(s["sources"])==2
    sources=[]
    for j,ss in enumerate(s["sources"]):
        assert type(ss)is dict and set(ss)=={"id","position_BU","direction"} and ss["id"]=="S"+str(j)
        o=vec(ss["position_BU"]);d=vec(ss["direction"]);assert dot(d,d)>0;sources.append((o,d))
    return s,q,target,wave,ref,caps,rcap,tris,sources

def bracket(interval,squared):
    lo,hi=[unbounded(x) for x in interval];grid=F(1,2**96)
    assert 0<=lo<=hi and lo*lo<=squared<=hi*hi
    assert (lo/grid).denominator==(hi/grid).denominator==1 and hi-lo<=grid
    if lo*lo==squared or hi*hi==squared:assert hi==lo
    else:assert hi-lo==grid
    return lo,hi

def expected(i,v):
    s,q,target,wave,ref,caps,rcap,tris,sources=preflight(i)
    cycles=[]
    for j,(o,d) in enumerate(sources):
        t,p,h,n,b=trace(o,d,tris,None);assert p==q["root_primitive_id"]
        reflected=tuple(d[z]-2*dot(d,n)*n[z]/dot(n,n) for z in range(3))
        t2,p2,h2,n2,b2=trace(h,reflected,tris,p)
        assert p2==q["detector_primitive_id"] and h2==target
        # Checks certificates in result, but derives rays/hits via a different solver.
        diag=v["diagnostics"][j]
        assert diag["source_id"]=="S"+str(j) and diag["primitive_ids"]==[p,p2]
        assert [unbounded(x) for x in diag["hit_parameters"]]==[t,t2]
        assert [V(x) for x in diag["hit_points_BU"]]==[h,h2]
        assert [V(x) for x in diag["barycentric"]]==[b,b2]
        assert V(diag["reflected_direction"])==reflected
        intervals=[]
        assert len(diag["segments"])==2
        for g,left,right in zip(diag["segments"],(o,h),(h,h2)):
            assert V(g["from_BU"])==left and V(g["to_BU"])==right
            sq=dot(sub(right,left),sub(right,left));assert unbounded(g["squared_BU2"])==sq
            intervals.append(bracket(g["length_interval_BU"],sq))
        lo=sum(x[0] for x in intervals);hi=sum(x[1] for x in intervals)
        assert [unbounded(x) for x in diag["length_interval_BU"]]==[lo,hi]
        cl=(lo-ref)/wave;ch=(hi-ref)/wave;cycles.append((cl,ch))
        assert [unbounded(x) for x in diag["geometric_cycles_interval"]]==[cl,ch]
        assert unbounded(diag["interval_width_bound_rad"])==8*(ch-cl)
        assert unbounded(diag["literal_cap_rad"])==caps[j]
    assert len(v["diagnostics"])==2
    rel=(cycles[0][0]-cycles[1][1],cycles[0][1]-cycles[1][0]);rd=v["relative_diagnostic"]
    assert tuple(unbounded(x) for x in rd["geometric_cycles_interval"])==rel
    assert unbounded(rd["interval_width_bound_rad"])==8*(rel[1]-rel[0]) and unbounded(rd["literal_cap_rad"])==rcap
    return all(8*(u-l)<=cap for (l,u),cap in zip(cycles,caps)) and 8*(rel[1]-rel[0])<=rcap

def main():
    receipt=json.loads((ROOT/("coordinacion/respuestas/"+ID+"-CODEX.json")).read_bytes())
    assert receipt["id"]==ID and receipt["status"]=="CPU_RATIONAL_GEOMETRY_ONLY"
    pins=receipt["code_doc_sha256"];assert len(pins)==83
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    t=receipt["test_run"];assert t["rc"]==0 and t["timed_out"]is False
    assert t["threads"]==t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail
    assert len(raw)==t["stdout_bytes"] and hashlib.sha256(raw).hexdigest()==t["stdout_sha256"]
    suite=json.loads(raw);assert suite["status"]=="PASS" and suite["tests"]==6;d=suite["data"]
    assert set(d["inputs"])==set(d["results"]) and len(d["results"])==28
    flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
           "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified","coherent_field_admission_allowed","interference_phase_certified")
    good=bad=0
    for name,i in d["inputs"].items():
        v=d["results"][name]
        assert all(v[k]is False for k in flags)
        assert v["detector_field"]is v["power"]is v["source_amplitude"]is v["source_phase"]is v["mirror_phase"]is None
        assert v["frozen_producer_replays"]==0 and v["full_costs"]=="UNMEASURED_NOT_ZERO"
        assert v["representation"]=="RATIONAL_INTERVAL_CPU_NOT_GPU_ABI"
        try:ok=expected(i,v)
        except (AssertionError,KeyError,TypeError,IndexError,ZeroDivisionError):ok=False
        if ok:
            good+=1;assert v["status"]=="CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY" and v["paths"]==v["diagnostics"],name
            assert v["sqrt_bits"]==96 and v["original_scene_sha256"]==digest(i["scene"]) and v["literal_request_sha256"]==digest(i["request"])
        else:
            bad+=1;assert v["status"]=="STOP" and v["paths"]==[],name
    assert (good,bad)==(4,24)
    # Require cap failures to have complete mathematically checked diagnostics, not empty evidence.
    for name in ("SOURCE0_cap_zero","SOURCE1_cap_zero","relative_cap_zero"):
        assert expected(d["inputs"][name],d["results"][name])is False
    for g in d["root_controls"].values():bracket(g["interval"],unbounded(g["squared"]))
    assert len(d["root_controls"])==6
    counters={k:sum(v["counters"][k] for v in d["results"].values()) for k in ("triangle_plane_tests","sqrt_brackets","exact_previous_zero_skips")}
    assert counters==dict(triangle_plane_tests=74,sqrt_brackets=30,exact_previous_zero_skips=16)
    tree=ast.parse((ROOT/"Blender/benchmarks/capacity_audit/oblique_common_detector_length_CPU_v1.py").read_text())
    assert not any(isinstance(n,ast.Constant) and type(n.value)is float for n in ast.walk(tree))
    imports=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
        if isinstance(n,ast.ImportFrom):imports.append(n.module)
    assert set(imports)=={"fractions","math","hashlib","json"}
    print(json.dumps({"status":"PASS","pins":83,"cases":28,"CPU_partial":good,"STOP":bad,"source_paths_emitted":8,
                     "square_controls":6,"determinant_reference":True,"counters":counters,"GPU_executed":False},sort_keys=True))
if __name__=="__main__":main()
