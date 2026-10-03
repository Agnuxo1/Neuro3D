"""Opt-in exact rational ray/triangle reference and squared-inequality length bounds.
No float, old producer, GPU, material phase or physical inference.
"""
from fractions import Fraction as F
from math import isqrt
import hashlib,json
MODEL="precision-oblique-common-detector-length-CPU-v1"
SCHEMA="precision-oblique-declared-scene-v1"
BITS=96
FLAGS=("GPU_executed","native_promotion_allowed","physical_scene_authenticated",
       "native_hit_coverage_certified","length_reference_phase_bound_certified",
       "mirror_material_certified","full_field_certified","coherent_field_admission_allowed",
       "interference_phase_certified")

def require(ok,msg):
    if not ok:raise ValueError(msg)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def pair(x):
    x=F(x);return [x.numerator,x.denominator]
def rational(v):
    require(type(v)is list and len(v)==2 and all(type(x)is int for x in v),"typed_rational")
    require(v[1]>0 and max(abs(v[0]).bit_length(),v[1].bit_length())<=128,"bounded_rational")
    x=F(*v);require(abs(x)<=10**6,"rational_magnitude");return x
def vector(v):
    require(type(v)is list and len(v)==3,"vector3");return tuple(rational(x) for x in v)
def enc(v):return [pair(x) for x in v]
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def mul(a,t):return tuple(x*t for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])

def fixture(gap=F(1)):
    gap=F(gap)
    return {"schema":SCHEMA,"units":"BU","triangles":[
        {"primitive_id":i,"object_id":"oblique_common_fixture","vertices_BU":[enc((x,0,0)),enc((x,3,0)),enc((x,0,3))]}
        for i,x in enumerate((F(0),gap))],
        "sources":[{"id":"S"+str(i),"position_BU":enc((x,x,F(1,4))),"direction":enc((1,1,0))}
                   for i,x in enumerate((gap/4,3*gap/4))]}

def request(scene):
    gap=rational(scene["triangles"][1]["vertices_BU"][0][0])
    return {"original_scene_sha256":digest(scene),"source_ids":["S0","S1"],"root_primitive_id":1,
            "detector_primitive_id":0,"detector_point_BU":enc((0,2*gap,F(1,4))),
            "lambda_BU":[1,8],"reference_BU":[0,1],"source_width_caps_rad":[pair(F(1,2**80))]*2,
            "relative_width_cap_rad":pair(F(1,2**80))}

def root_bracket(squared):
    require(type(squared)is F and squared>=0,"nonnegative_squared_length")
    scale=1<<BITS
    k=isqrt((squared.numerator<<(2*BITS))//squared.denominator)
    lo=F(k,scale);hi=lo if lo*lo==squared else F(k+1,scale)
    require(lo>=0 and lo*lo<=squared<=hi*hi and hi-lo<=F(1,scale),"squared_certificate")
    return lo,hi

def nearest(o,d,triangles,previous,counters):
    hits=[]
    for pid,a,b,c,n in triangles:
        counters["triangle_plane_tests"]+=1
        denom=dot(n,d);plane=dot(n,sub(a,o))
        if denom==0:
            require(plane!=0,"coplanar_ambiguity")
            continue
        t=plane/denom
        if t<0:continue
        h=add(o,mul(d,t));v0=sub(b,a);v1=sub(c,a);v2=sub(h,a)
        aa=dot(v0,v0);bb=dot(v0,v1);cc=dot(v1,v1);dd=dot(v2,v0);ee=dot(v2,v1)
        det=aa*cc-bb*bb
        u=(cc*dd-bb*ee)/det;v=(aa*ee-bb*dd)/det
        if u<0 or v<0 or u+v>1:continue
        if t==0:
            # Exact just-hit primitive only; no epsilon, no object-wide/global veto.
            require(pid==previous,"other_primitive_contact")
            counters["exact_previous_zero_skips"]+=1
            continue
        hits.append((t,pid,h,n,[pair(1-u-v),pair(u),pair(v)]))
    require(bool(hits),"no_positive_hit")
    minimum=min(h[0] for h in hits);chosen=[h for h in hits if h[0]==minimum]
    require(len(chosen)==1,"nearest_tie");return chosen[0]

def audit(scene,q,*,model):
    counters={"triangle_plane_tests":0,"exact_previous_zero_skips":0,"sqrt_brackets":0}
    out={"model":MODEL,"status":"STOP","reason":None,"paths":[],"diagnostics":[],
         "counters":counters,"phase_scope":"GEOMETRIC_PATH_CYCLES_ONLY_NO_MATERIAL",
         "representation":"RATIONAL_INTERVAL_CPU_NOT_GPU_ABI","detector_field":None,"power":None,
         "source_amplitude":None,"source_phase":None,"mirror_phase":None,
         "full_costs":"UNMEASURED_NOT_ZERO","frozen_producer_replays":0}
    out.update({k:False for k in FLAGS})
    try:
        require(type(model)is str and model==MODEL,"explicit_model")
        require(type(scene)is dict and set(scene)=={"schema","units","triangles","sources"}
                and scene["schema"]==SCHEMA and scene["units"]=="BU","closed_scene")
        keys={"original_scene_sha256","source_ids","root_primitive_id","detector_primitive_id","detector_point_BU",
              "lambda_BU","reference_BU","source_width_caps_rad","relative_width_cap_rad"}
        require(type(q)is dict and set(q)==keys,"closed_request")
        require(type(q["original_scene_sha256"])is str and q["original_scene_sha256"]==digest(scene),"original_binding")
        require(q["source_ids"]==["S0","S1"] and type(q["source_ids"])is list,"ALL_SOURCE_order")
        require(all(type(q[k])is int for k in ("root_primitive_id","detector_primitive_id"))
                and q["root_primitive_id"]!=q["detector_primitive_id"],"typed_primitive_path")
        detector=vector(q["detector_point_BU"]);wave=rational(q["lambda_BU"]);ref=rational(q["reference_BU"])
        require(wave>0,"positive_wavelength")
        require(type(q["source_width_caps_rad"])is list and len(q["source_width_caps_rad"])==2,"ALL_caps")
        caps=[rational(x) for x in q["source_width_caps_rad"]];rcap=rational(q["relative_width_cap_rad"])
        require(all(c>=0 for c in caps+[rcap]),"nonnegative_caps")
        ts=scene["triangles"];require(type(ts)is list and 2<=len(ts)<=4,"bounded_scene_2_to4_triangles")
        triangles=[];ids=[]
        for tri in ts:
            require(type(tri)is dict and set(tri)=={"primitive_id","object_id","vertices_BU"},"closed_triangle")
            pid=tri["primitive_id"]
            require(type(pid)is int and 0<=pid<2**31 and pid not in ids,"unique_primitive")
            require(type(tri["object_id"])is str and 0<len(tri["object_id"])<=64,"object_identity")
            vs=tri["vertices_BU"];require(type(vs)is list and len(vs)==3,"triangle_vertices")
            a,b,c=[vector(v) for v in vs];n=cross(sub(b,a),sub(c,a))
            require(dot(n,n)>0,"nondegenerate_triangle");triangles.append((pid,a,b,c,n));ids.append(pid)
        require(q["root_primitive_id"]in ids and q["detector_primitive_id"]in ids,"path_primitives_present")
        ss=scene["sources"];require(type(ss)is list and len(ss)==2,"exact_two_sources")
        sources=[]
        for i,s in enumerate(ss):
            require(type(s)is dict and set(s)=={"id","position_BU","direction"} and s["id"]=="S"+str(i),"SOURCE_identity")
            o=vector(s["position_BU"]);d=vector(s["direction"])
            require(dot(d,d)>0,"nonzero_direction");sources.append((s["id"],o,d))
        pending=[];cycles=[]
        for sid,o,d in sources:
            first=nearest(o,d,triangles,None,counters);t,pid,h,n,bary=first
            require(pid==q["root_primitive_id"],"root_path_mismatch")
            reflected=sub(d,mul(n,2*dot(d,n)/dot(n,n)))
            second=nearest(h,reflected,triangles,pid,counters);t2,pid2,h2,n2,bary2=second
            require(pid2==q["detector_primitive_id"] and h2==detector,"common_detector_path")
            segments=[]
            for left,right in ((o,h),(h,h2)):
                squared=dot(sub(right,left),sub(right,left));lo,hi=root_bracket(squared)
                counters["sqrt_brackets"]+=1
                segments.append({"from_BU":enc(left),"to_BU":enc(right),"squared_BU2":pair(squared),
                                 "length_interval_BU":[pair(lo),pair(hi)]})
            lo=sum(F(*g["length_interval_BU"][0]) for g in segments)
            hi=sum(F(*g["length_interval_BU"][1]) for g in segments)
            cl=(lo-ref)/wave;ch=(hi-ref)/wave;bound=8*(ch-cl)
            diagnostic={"source_id":sid,"primitive_ids":[pid,pid2],"hit_parameters":[pair(t),pair(t2)],
                "hit_points_BU":[enc(h),enc(h2)],"barycentric":[bary,bary2],"reflected_direction":enc(reflected),
                "segments":segments,"length_interval_BU":[pair(lo),pair(hi)],
                "geometric_cycles_interval":[pair(cl),pair(ch)],"interval_width_bound_rad":pair(bound),
                "literal_cap_rad":pair(caps[len(pending)])}
            pending.append(diagnostic);cycles.append((cl,ch));out["diagnostics"].append(diagnostic)
        # Common rational reference cancels algebraically, never erases individual errors/caps.
        relative=(cycles[0][0]-cycles[1][1],cycles[0][1]-cycles[1][0])
        rbound=8*(relative[1]-relative[0])
        out["relative_diagnostic"]={"geometric_cycles_interval":[pair(x) for x in relative],
                                   "interval_width_bound_rad":pair(rbound),"literal_cap_rad":pair(rcap)}
        require(all(F(*p["interval_width_bound_rad"])<=c for p,c in zip(pending,caps)),"SOURCE_width_cap")
        require(rbound<=rcap,"relative_width_cap")
        out.update(status="CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY",paths=pending,
                   original_scene_sha256=digest(scene),literal_request_sha256=digest(q),sqrt_bits=BITS)
    except (ValueError,TypeError,KeyError,OverflowError) as e:out["reason"]=str(e)
    return out
