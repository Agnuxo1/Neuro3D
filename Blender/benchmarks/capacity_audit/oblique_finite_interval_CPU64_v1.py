"""Opt-in actual CPU binary64 interval operations, outward proof ledger; not GPU/physical."""
from fractions import Fraction as F
import math
import struct
import oblique_finite_interval_HOST_v1 as host

MODEL = "oblique-finite-interval-CPU64-v1"
FLAGS = dict(physical_visibility_certified=False, phase_certified=False,
             GPU_used=False, scene_authenticated=False, GPU_backend_certified=False)

def word(x):
    return struct.pack("<d", x).hex()

def pair(x):
    return [x.numerator, x.denominator]

def normal_zero(x):
    return math.isfinite(x) and (x == 0 or abs(x) >= float.fromhex("0x1p-1022"))

class Outward:
    def __init__(self):
        self.ledger = []
        self.native_arithmetic = 0
        self.endpoint_casts = 0
        self.nextafter_calls = 0
        self.sign_flips = 0

    def rounded(self, exact, rn, direction, op, operands):
        entry = dict(index=len(self.ledger), op=op, operands=operands,
                     exact=pair(exact), direction=direction, RN_word=word(rn),
                     output_word=None, nextafter=False, status="STOP")
        self.ledger.append(entry)
        if not normal_zero(rn) or (rn == 0 and exact != 0):
            raise ValueError("RN_underflow_overflow_or_subnormal_STOP")
        if exact != 0:
            # Verify local binary64 RN ties-to-even, independently of float(exact).
            lower = math.nextafter(rn, -math.inf)
            upper = math.nextafter(rn, math.inf)
            self.nextafter_calls += 2
            if not normal_zero(lower) or not normal_zero(upper):
                raise ValueError("RN_neighbor_domain_STOP")
            fr = F.from_float(rn)
            distance = abs(exact-fr)
            for neighbor in (lower, upper):
                other = abs(exact-F.from_float(neighbor))
                bits = int.from_bytes(struct.pack("<d", rn), "little")
                if distance > other or (distance == other and bits & 1):
                    raise ValueError("RN_not_nearest_even_STOP")
        value = rn
        fr = F.from_float(rn)
        if (direction == "lo" and fr > exact) or (direction == "hi" and fr < exact):
            value = math.nextafter(rn, -math.inf if direction == "lo" else math.inf)
            self.nextafter_calls += 1
            entry["nextafter"] = True
        if not normal_zero(value):
            raise ValueError("outward_subnormal_or_overflow_STOP")
        if direction == "lo":
            assert F.from_float(value) <= exact
        else:
            assert F.from_float(value) >= exact
        entry.update(output_word=word(value), status="PASS")
        return value

    def cast(self, exact, direction):
        self.endpoint_casts += 1
        try:
            rn = float(exact)
        except OverflowError:
            rn = math.inf if exact > 0 else -math.inf
        return self.rounded(exact, rn, direction, "cast", [])

    def arithmetic(self, a, b, op, direction):
        if not normal_zero(a) or not normal_zero(b):
            raise ValueError("operand_domain_STOP")
        fa, fb = F.from_float(a), F.from_float(b)
        self.native_arithmetic += 1
        # Separate operators; no FMA or exact result substitution.
        if op == "add":
            exact, rn = fa+fb, a+b
        elif op == "sub":
            exact, rn = fa-fb, a-b
        elif op == "mul":
            exact, rn = fa*fb, a*b
        else:
            raise ValueError("closed_operator")
        return self.rounded(exact, rn, direction, op, [word(a), word(b)])

    def add(self, a, b):
        return (self.arithmetic(a[0],b[0],"add","lo"),
                self.arithmetic(a[1],b[1],"add","hi"))

    def sub(self, a, b):
        return (self.arithmetic(a[0],b[1],"sub","lo"),
                self.arithmetic(a[1],b[0],"sub","hi"))

    def mul(self, a, b):
        # Charge each of the four native products ONCE; outward endpoints share RN.
        lower, upper = [], []
        for x in a:
            for y in b:
                fa, fb = F.from_float(x), F.from_float(y)
                self.native_arithmetic += 1
                rn = x*y
                operands = [word(x),word(y)]
                lower.append(self.rounded(fa*fb,rn,"lo","mul",operands))
                upper.append(self.rounded(fa*fb,rn,"hi","mul_shared_RN",operands))
        return min(lower), max(upper)

    def neg(self, a):
        self.sign_flips += 2
        return -a[1], -a[0]

    def costs(self):
        return dict(native_arithmetic=self.native_arithmetic, endpoint_casts=self.endpoint_casts,
                    nextafter_calls=self.nextafter_calls, sign_flips=self.sign_flips,
                    exact_audit_fraction_operations="UNMEASURED_NOT_ZERO",
                    total_cost="UNKNOWN_NOT_ZERO")

def classify(scene, request):
    arithmetic = Outward()
    output = dict(backend=MODEL, status="STOP_INPUT", reason=None, trace=None,
                  coordinate_boxes=0, input_boxes=None, EPS_used=False,
                  division_operations=0, FMA_used=False, CPU_binary64_executed=False,
                  promotion="STOP_PHYSICAL_GPU", **FLAGS)
    try:
        host.keys(request, ("backend","scene_query","snapshot_sha256"))
        if request["backend"] != MODEL or request["snapshot_sha256"] != host.digest(scene):
            raise ValueError("explicit_CPU64_snapshot_required")
        boxes = host.validate(scene,request["scene_query"])  # schema only, NOT HOST.classify
        output.update(snapshot_sha256=host.digest(scene), query_sha256=host.digest(request),
                      parent_query_sha256=host.digest(request["scene_query"]),
                      coordinate_boxes=15, CPU_binary64_executed=True)
        vectors=[]
        for n in host.POINTS:
            vectors.append([(arithmetic.cast(x,"lo"),arithmetic.cast(y,"hi")) for x,y in boxes[n]])
        output["input_boxes"]={n:[list(map(word,box)) for box in v] for n,v in zip(host.POINTS,vectors)}
        o,e,a,b,c=vectors
        def vsub(v,w):return [arithmetic.sub(x,y) for x,y in zip(v,w)]
        def cross(v,w):
            return [arithmetic.sub(arithmetic.mul(v[j],w[k]),arithmetic.mul(v[k],w[j]))
                    for j,k in ((1,2),(2,0),(0,1))]
        def dot(v,w):
            terms=[arithmetic.mul(x,y) for x,y in zip(v,w)]
            return arithmetic.add(arithmetic.add(terms[0],terms[1]),terms[2])
        d,e1,e2,s=vsub(e,o),vsub(b,a),vsub(c,a),vsub(o,a)
        p,q=cross(d,e2),cross(s,e1)
        det,u,v,t=dot(e1,p),dot(s,p),dot(d,q),dot(e2,q)
        w,end_slack=arithmetic.sub(arithmetic.sub(det,u),v),arithmetic.sub(det,t)
        raw=dict(det=det,U=u,V=v,W=w,T=t,end_slack=end_slack)
        sign=1 if det[0]>0 else -1 if det[1]<0 else 0
        oriented={k:arithmetic.neg(x) if sign==-1 else x for k,x in raw.items()} if sign else None
        status="STOP_UNRESOLVED"
        if sign:
            if any(oriented[k][1]<0 for k in ("U","V","W","T","end_slack")):
                status="CPU64_DECLARED_BOX_DISJOINT"
            elif all(oriented[k][0]>0 for k in ("U","V","W","T","end_slack")):
                status="CPU64_DECLARED_BOX_INTERIOR_CROSS"
        output.update(status=status,reason="strict_outward_predicate" if status!="STOP_UNRESOLVED" else "boundary_or_det_zero",
                      trace={k:list(map(word,x)) for k,x in raw.items()},sign=sign,
                      oriented=None if oriented is None else {k:list(map(word,x)) for k,x in oriented.items()})
    except (ValueError, TypeError, OverflowError) as exc:
        output.update(status="STOP_INPUT" if not arithmetic.ledger else "STOP_ARITHMETIC",reason=str(exc))
    output.update(ledger=arithmetic.ledger,costs=arithmetic.costs())
    return output
