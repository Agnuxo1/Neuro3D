"""Independent continuous box/lattice certificates vs sealed native length; no producer replay."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,copy,runpy,itertools
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-LENGTH-CPU-001-CODEX.json"
PSHA="1de93e48c76b96904d17d0ccfa994c992fa7bbb69deefe0f7fa3f4dd354ad94d"
ORIGINAL="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-CPU-001-CODEX.json"
OSHA="813fd728006a90adb40f99d1eb49aa3523f8f63bf61edca7775e332dc57106ea"
MODEL="oblique-pair64-length-reference-HOST-v1"
POLICY="SAME_ORIGINAL_ALL_RADII_CONTINUOUS_BOX_FIXED96_ONLY"
ROOTSHA="f510517d0c91c45e9ebaadfe593a4c8116e4587bb3eb4d06be7a0ab651079c49"
prior=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_pair64_segment_length_CPU64.py"))
digest,pair,capture,frac=map(prior.get,("digest","pair","capture","frac"))
def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==193411 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);assert len(pins)==268;pins[PARENT]=PSHA
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    d=capture(r["test_run"])["evidence"];assert capture(r["independent_pre"])["status"]=="PASS"
    raw=(ROOT/ORIGINAL).read_bytes();assert len(raw)==84149 and hashlib.sha256(raw).hexdigest()==OSHA
    o=capture(json.loads(raw)["test_run"])["evidence"]
    orig={"scene:"+x["name"]:x for x in o["records"]};orig["native_inexact"]=o["inexact"]
    orig.update({"input:"+x["name"]:x for x in o["invalid"]})
    e={x["id"]:x for x in d["records"]};assert set(e)==set(orig)and len(e)==16
    return r,e,orig,pins,d
def selector(k,e,orig):
    x,o=e[k],orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        original_receipt_sha256=OSHA,original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),
        original_query_sha256=digest(q),length_frame_sha256=digest(x["result"].get("scene")),root_algorithm_sha256=ROOTSHA)
def scope(r):
    assert r["backend"]==MODEL and r["root_bits"]==96 and r["promotion"]=="STOP_PHYSICAL_PHASE_GPU"
    assert r["comparison_scope"]=="SAME_ORIGINAL_DECLARED_STRAIGHT_BOX_ONLY_NOT_OPTICAL_REFERENCE"
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO"and r["parent_native_costs"]=="RETAINED_NONZERO_NOT_REPLAYED"
    assert r["native_root_calls"]==r["new_transport_graph_calls"]==r["new_predicate_calls"]==r["retained_suite_replays"]==0
    for k in ("CPU_native_executed","source_uncertainty_cancelled","correlation_assumed","phase_certified",
        "optical_reference_certified","physical_visibility_certified","scene_authenticated","GPU_used"):assert r[k]is False
def extrema(s,z):
    boxes={}
    for n in ("origin","detector"):
        boxes[n]=[(F(*v)-F(*rad),F(*v)+F(*rad))for v,rad in zip(s["points"][n]["nominal"],s["points"][n]["radius"])]
    delta=[(b[0]-a[1],b[1]-a[0])for a,b in zip(boxes["origin"],boxes["detector"])]
    squares=[(F(0)if a<=0<=b else min(a*a,b*b),max(a*a,b*b))for a,b in delta]
    sl,sh=map(sum,zip(*squares))
    assert z["delta"]==[[pair(v)for v in iv]for iv in delta]and z["squares"]==[[pair(v)for v in iv]for iv in squares]
    assert z["squared"]==[pair(sl),pair(sh)]
    for key,value in (("lower_witness",sl),("upper_witness",sh)):
        witness=[[F(*v)for v in vec]for vec in z[key]]
        assert len(witness)==2 and all(len(v)==3 for v in witness)
        for n,vec in zip(("origin","detector"),witness):
            assert all(a<=v<=b for v,(a,b)in zip(vec,boxes[n]))
        assert sum((b-a)**2 for a,b in zip(*witness))==value
    for choice in itertools.product((0,1),repeat=6):
        a=[boxes["origin"][j][choice[j]]for j in range(3)];b=[boxes["detector"][j][choice[j+3]]for j in range(3)]
        v=sum((y-x)**2 for x,y in zip(a,b));assert sl<=v<=sh
    return sl,sh
def root(v,z):
    a,b=map(lambda p:F(*p),z);step=F(1,2**96)
    assert a>=0 and(a*2**96).denominator==1 and a*a<=v<(a+step)**2
    assert b==(a if a*a==v else a+step)and b*b>=v
    return a,b
def verify_capture(d):
    _,e,orig,pins,old=retained();assert d["pins"]==pins
    assert prior["verify_capture"](old)["status"]=="PASS" # rational/bit ledger checks only
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(e)
    counts={};ratios={};roots=words=0
    for x in d["records"]:
        k=x["id"];q=x["request"];r=x["result"];scope(r);p=e[k]["result"];o=orig[k]
        assert q==selector(k,e,orig)and r["request_sha256"]==digest(q)
        assert r["parent_record_sha256"]==digest(e[k])and r["original_record_sha256"]==digest(o)
        assert r["upstream_status"]==p["status"]and r["upstream_reason"]==p["reason"]
        counts[r["status"]]=counts.get(r["status"],0)+1
        if p["status"]!="CPU64_DECLARED_SEGMENT_LENGTH_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_length_STOP_not_rescued"and r["diagnostic"]is None
            assert r["HOST_root_calls"]==r["HOST_word_decodes"]==r["HOST_box_extrema"]==r["HOST_exact_divisions"]==0
            continue
        assert r["status"]=="HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY"and r["reason"]=="fixed96_extrema_and_native_width_comparison"
        z=r["diagnostic"];s=o["scene"];local=p["scene"];f=o["result"]["frame"]
        assert z["original_scene"]==s and z["original_query"]==o["scene_query"]and z["original_snapshot_sha256"]==digest(s)
        assert z["local_scene_sha256"]==digest(local)and f["scene"]==local and p["scene_query"]==f["scene_query"]
        text=f["output_packet_hex"];assert len(text)==480 and hashlib.sha256(bytes.fromhex(text)).hexdigest()==e[k]["request"]["output_packet_sha256"]
        for i in range(15):
            n,j=("origin","detector","A","B","C")[i//3],i%3;v=frac(text[32*i:32*i+16])+frac(text[32*i+16:32*i+32])
            assert v==F(*local["points"][n]["nominal"][j])==F(*s["points"][n]["nominal"][j])-F(*s["points"]["origin"]["nominal"][j])
            assert local["points"][n]["radius"][j]==s["points"][n]["radius"][j]
        a,b=extrema(s,z["extrema"]);aa,bb=extrema(local,z["shifted_extrema"]);assert(a,b)==(aa,bb)
        for key in ("delta","squares","squared"):assert z["extrema"][key]==z["shifted_extrema"][key]
        lower,_=root(a,z["roots"][0]);_,upper=root(b,z["roots"][1]);roots+=2
        assert z["reference_interval"]==[pair(lower),pair(upper)]and lower<upper
        nl,nu=map(frac,p["trace"]["length"]);assert z["native_words"]==p["trace"]["length"]
        assert z["native_interval"]==[pair(nl),pair(nu)]and nl<=lower<=upper<=nu
        width=upper-lower;ratio=(nu-nl)/width
        assert z["reference_width"]==pair(width)and z["native_width"]==pair(nu-nl)
        assert z["outward_excess"]==[pair(lower-nl),pair(nu-upper)]and z["native_width_over_reference"]==pair(ratio)
        assert z["comparison_units"]=="scene_length"and z["SOURCE"]=="SOURCE0"and z["DETECTOR"]=="DETECTOR0"
        assert r["HOST_root_calls"]==2 and r["HOST_word_decodes"]==32 and r["HOST_box_extrema"]==2 and r["HOST_exact_divisions"]==1
        words+=32;ratios[k]=pair(ratio)
    assert counts==dict(HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY=2,STOP_UPSTREAM=14)
    names=("backend","policy","parent_receipt_sha256","parent_record_sha256","original_record_sha256","original_query_sha256","root_algorithm_sha256","extra_SOURCE")
    assert tuple(x["id"]for x in d["invalid"])==names
    k=next(k for k in e if e[k]["result"]["status"]=="CPU64_DECLARED_SEGMENT_LENGTH_ONLY")
    for x in d["invalid"]:
        q=selector(k,e,orig)
        if x["id"]=="extra_SOURCE":q["SOURCE"]="SOURCE1"
        else:q[x["id"]]="wrong"
        assert x["request"]==q;r=x["result"];scope(r)
        assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"and r["diagnostic"]is None
        assert r["HOST_root_calls"]==r["HOST_word_decodes"]==r["HOST_box_extrema"]==r["HOST_exact_divisions"]==0
    return dict(status="PASS",references=2,upstream_STOP=14,invalid=8,inherited_pins=len(pins),
        HOST_root_calls=roots,HOST_word_decodes=words,attainable_extrema_witnesses=8,
        corner_checks=256,native_replay=0,GPU_calls=0,ratios=ratios)
def mutations(d):
    names=("SOURCE_zero","root_grid_nonminimal","missing_radius_witness","ratio_wrong","rescue_STOP","fake_native","fake_phase","wrong_original_query")
    first=next(i for i,x in enumerate(d["records"])if x["result"]["status"]=="HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY")
    blocked=next(i for i,x in enumerate(d["records"])if x["result"]["status"]=="STOP_UPSTREAM")
    rejected=[]
    for name in names:
        x=copy.deepcopy(d);r=x["records"][first]["result"];z=r["diagnostic"]
        if name=="SOURCE_zero":z["original_scene"]["points"]["origin"]["radius"][0]=[0,1]
        elif name=="root_grid_nonminimal":
            v=F(*z["roots"][0][0])-F(1,2**96);z["roots"][0][0]=pair(v)
        elif name=="missing_radius_witness":z["extrema"]["upper_witness"][0][0]=[0,1]
        elif name=="ratio_wrong":z["native_width_over_reference"]=[1,1]
        elif name=="rescue_STOP":x["records"][blocked]["result"]["status"]="HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY"
        elif name=="fake_native":r["CPU_native_executed"]=True
        elif name=="fake_phase":r["phase_certified"]=True
        else:x["records"][first]["request"]["original_query_sha256"]="wrong"
        try:verify_capture(x);raise RuntimeError("accepted_mutation:"+name)
        except(AssertionError,ValueError,TypeError,KeyError,IndexError):rejected.append(name)
    assert rejected==list(names);return dict(status="PASS",rejected=8,names=rejected)
def run():
    import oblique_pair64_length_reference_HOST_v1 as core
    e,orig,pins=core.retained()
    records=[dict(id=k,request=core.selector(k,e,orig),result=core._audit(core.selector(k,e,orig),e,orig))for k in e]
    k=next(k for k in e if e[k]["result"]["status"]=="CPU64_DECLARED_SEGMENT_LENGTH_ONLY");invalid=[]
    for name in ("backend","policy","parent_receipt_sha256","parent_record_sha256","original_record_sha256","original_query_sha256","root_algorithm_sha256","extra_SOURCE"):
        q=core.selector(k,e,orig)
        if name=="extra_SOURCE":q["SOURCE"]="SOURCE1"
        else:q[name]="wrong"
        invalid.append(dict(id=name,request=q,result=core._audit(q,e,orig)))
    d=dict(pins=pins,records=records,invalid=invalid);s=verify_capture(d);s["mutations"]=mutations(d)
    print(json.dumps(dict(summary=s,evidence=d),sort_keys=True,separators=(",",":"),allow_nan=False))
if __name__=="__main__":run()
