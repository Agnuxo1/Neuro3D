"""Sealed pair64 frames -> native CPU64 straight segment length, conditional only."""
from pathlib import Path
from fractions import Fraction as F
import math,json,copy
import oblique_pair64_interval_consumer_CPU_v1 as ingress
import oblique_finite_interval_HOST_v1 as host
import oblique_finite_interval_CPU64_v1 as cpu
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-pair64-segment-length-CPU-v1"
POLICY="DISJOINT_ONLY_ALL_RADII_NATIVE_SQUARE_SQRT_OUTWARD"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-INTERVAL-CPU-001-CODEX.json"
PSHA="bf34de7e81a004bf602437ab260e88060f7d36f899c5862bcd3c1d652f1bd354"
require,sha,capture=ingress.require,ingress.sha,ingress.capture
pair,word=cpu.pair,cpu.word

def retained():
    raw=(ROOT/PARENT).read_bytes();require(len(raw)==124987 and sha(raw)==PSHA,"parent_seal")
    r=json.loads(raw);require(len(r["code_doc_sha256"])==264,"parent_pins")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(capture(r["independent_pre"])["status"]=="PASS","sealed_parent_oracle")
    d=capture(r["test_run"])["evidence"];e={x["id"]:x for x in d["records"]}
    require(len(e)==16 and sum(x["result"]["status"]=="CPU64_DECLARED_BOX_DISJOINT"for x in e.values())==2,"closed_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins

def selector(record,e):
    x=e[record];r=x["result"];f=r["frame"]
    return dict(backend=MODEL,policy=POLICY,record_id=record,parent_receipt_sha256=PSHA,
        parent_record_sha256=host.digest(x),upstream_request_sha256=host.digest(x["request"]),
        frame_sha256=host.digest(f),output_packet_sha256=x["request"]["output_packet_sha256"])

class LengthOutward(cpu.Outward):
    def __init__(self):
        super().__init__();self.sqrt_ledger=[];self.sqrt_calls=0;self.zero_square_theorems=0
    def square(self,a):
        require(a[0]<=a[1],"ordered_square_interval")
        lower=[self.arithmetic(v,v,"mul","lo")for v in a]
        upper=[self.arithmetic(v,v,"mul","hi")for v in a]
        if a[0]<=0<=a[1]:
            lo=0.0;self.zero_square_theorems+=1
        else:lo=min(lower)
        return lo,max(upper)
    def sqrt(self,s,direction):
        require(direction in ("lo","hi")and cpu.normal_zero(s)and s>=0,"sqrt_nonnegative_normal_zero_input")
        self.sqrt_calls+=1;rn=math.sqrt(s)
        entry=dict(index=len(self.sqrt_ledger),op="sqrt",radicand_word=word(s),direction=direction,
            RN_word=word(rn),output_word=None,nextafter=False,neighbor_words=None,
            midpoint_squares=None,status="STOP",reason=None)
        self.sqrt_ledger.append(entry)
        try:
            require(cpu.normal_zero(rn)and (rn!=0 or s==0)and rn>=0,"sqrt_RN_domain_STOP")
            r=F.from_float(rn);v=F.from_float(s)
            if s:
                a,b=math.nextafter(rn,-math.inf),math.nextafter(rn,math.inf);self.nextafter_calls+=2
                require(cpu.normal_zero(a)and cpu.normal_zero(b)and a>=0,"sqrt_neighbor_domain_STOP")
                lower=((F.from_float(a)+r)/2)**2;upper=((F.from_float(b)+r)/2)**2
                entry.update(neighbor_words=[word(a),word(b)],midpoint_squares=[pair(lower),pair(upper)])
                even=int.from_bytes(bytes.fromhex(word(rn)),"little")%2==0
                require(lower<=v<=upper and (even or v not in (lower,upper)),"sqrt_not_nearest_even_STOP")
            out=rn
            if (direction=="lo"and r*r>v)or(direction=="hi"and r*r<v):
                out=math.nextafter(rn,-math.inf if direction=="lo"else math.inf)
                self.nextafter_calls+=1;entry["nextafter"]=True
            require(cpu.normal_zero(out)and out>=0,"sqrt_outward_domain_STOP")
            z=F.from_float(out)
            require(z*z<=v if direction=="lo"else z*z>=v,"sqrt_enclosure_STOP")
            entry.update(output_word=word(out),status="PASS")
            return out
        except ValueError as ex:
            entry["reason"]=str(ex);raise
    def costs(self):
        r=super().costs();r.update(native_sqrt=self.sqrt_calls,zero_square_theorems=self.zero_square_theorems)
        return r

def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,scene=None,trace=None,ledger=[],sqrt_ledger=[],
        costs=LengthOutward().costs(),packet_bytes=0,word_decodes=0,exact_pair_decodes=0,
        upstream_status=None,upstream_reason=None,new_transport_graph_calls=0,new_predicate_calls=0,
        retained_suite_replays=0,CPU_binary64_executed=False,EPS_used=False,FMA_used=False,
        source_uncertainty_cancelled=False,physical_visibility_certified=False,scene_authenticated=False,
        optical_length_certified=False,optical_reference_certified=False,phase_certified=False,GPU_used=False,
        full_costs="UNKNOWN_NOT_ZERO",promotion="STOP_PHYSICAL_PHASE_GPU",
        scope="DECLARED_STRAIGHT_SOURCE0_DETECTOR0_LENGTH_NOT_OPTICAL_REFERENCE",
        parent_costs="RETAINED_NONZERO_NOT_REPLAYED_NOT_END_TO_END_MEASUREMENT")

def _evaluate(q,e):
    out=baseline();arith=LengthOutward()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e)
        require(set(q)==set(expected)and all(type(v)is str for v in q.values())and q==expected,"closed_selector")
        x=e[q["record_id"]];prior=x["result"]
        out.update(parent_record_sha256=host.digest(x),parent_receipt_sha256=PSHA,
            request_sha256=host.digest(q),upstream_status=prior["status"],upstream_reason=prior["reason"])
        if prior["status"]!="CPU64_DECLARED_BOX_DISJOINT":
            out.update(status="STOP_UPSTREAM",reason="non_disjoint_parent_not_rescued");return out
        require(prior["source_uncertainty_cancelled"]is False and prior["phase_certified"]is False
            and prior["GPU_used"]is False and prior["predicate_calls"]==1,"upstream_scope")
        frame=prior["frame"];s=frame["scene"];boxes=host.validate(s,frame["scene_query"])
        text=x["request"]["output_packet_hex"];raw=bytes.fromhex(text)
        require(len(raw)==240 and sha(raw)==q["output_packet_sha256"],"ALL240bytes")
        decode=[]
        for i in range(15):
            n,j=host.POINTS[i//3],i%3;hw=raw[16*i:16*i+8].hex();lw=raw[16*i+8:16*i+16].hex()
            v=ingress.decode_pair(hw,lw);rad=s["points"][n]["radius"][j]
            require(pair(v)==s["points"][n]["nominal"][j],"pair_frame_identity")
            decode.append(dict(point=n,axis=j,hi_word=hw,lo_word=lw,decoded=pair(v),radius=rad))
        require(decode==frame["decode_ledger"]and host.digest(s)==frame["snapshot_sha256"],"ALL15radius_frame_identity")
        out.update(scene=copy.deepcopy(s),scene_query=frame["scene_query"],packet_bytes=240,word_decodes=30,
            exact_pair_decodes=15,frame_sha256=q["frame_sha256"],decode_ledger=decode,CPU_binary64_executed=True)
        actual={n:[(arith.cast(a,"lo"),arith.cast(b,"hi"))for a,b in boxes[n]]for n in ("origin","detector")}
        delta=[arith.sub(b,a)for a,b in zip(actual["origin"],actual["detector"])]
        squares=[arith.square(v)for v in delta]
        squared=arith.add(arith.add(squares[0],squares[1]),squares[2])
        length=arith.sqrt(squared[0],"lo"),arith.sqrt(squared[1],"hi")
        out.update(status="CPU64_DECLARED_SEGMENT_LENGTH_ONLY",reason="native_squared_root_enclosure",
            trace=dict(input_boxes={n:[list(map(word,v))for v in vec]for n,vec in actual.items()},
                delta=[list(map(word,v))for v in delta],squares=[list(map(word,v))for v in squares],
                squared=list(map(word,squared)),length=list(map(word,length))))
    except(ValueError,TypeError,KeyError,IndexError,OverflowError,OSError)as ex:
        out.update(status="STOP_ARITHMETIC"if arith.ledger or arith.sqrt_ledger else"STOP_INPUT",reason=str(ex))
    out.update(ledger=arith.ledger,sqrt_ledger=arith.sqrt_ledger,costs=arith.costs())
    return out

def classify(q):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _evaluate(q,e)
