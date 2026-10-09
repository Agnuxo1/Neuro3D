"""Analytic controls for new retrospective checker math; not GPU evidence."""
from fractions import Fraction as F
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import certify_archived_iris_outputs_v1 as c

c.interval_math.BITS=256;c.interval_math.GRID=1<<256;c.pi_interval.cache_clear()
pi=c.pi_interval()
checks=[]
for multiplier,sine,cosine in [(F(0),0,1),(F(1,2),1,0),(F(1),0,-1),(F(2),0,1)]:
 s,k=c.sincos(pi*multiplier)
 assert s.contains(sine) and k.contains(cosine)
 assert max(s.width(),k.width())<F(1,10**30)
 checks.append('cardinal_'+str(multiplier))
assert c.exponent(F(0)).contains(1)
for x in [F(1),F(5),F(32)]:
 a=c.exponent(x);b=c.exponent(-x)
 assert (a*b).contains(1) and a.lo>=1 and 0<b.lo<=b.hi<=1
 checks.append('positive_tail_reciprocal_'+str(x))
t=c.I(F(1,2)).sqrt();T=(t,c.I(0));R=(c.I(0),t)
e1=c.ph(pi);e2=c.ph(c.I(0))
for ax,ay,expected_x,expected_y in [((c.I(1),c.I(0)),c.zero(),0,1),(c.zero(),(c.I(1),c.I(0)),-1,0)]:
 a1=c.mul(c.neg(c.add(c.mul(T,ax),c.mul(R,ay))),e1)
 a2=c.mul(c.neg(c.add(c.mul(R,ax),c.mul(T,ay))),e2)
 ox=c.add(c.mul(R,a1),c.mul(T,a2));oy=c.add(c.mul(T,a1),c.mul(R,a2))
 assert ox[0].contains(expected_x) and ox[1].contains(0)
 assert oy[0].contains(expected_y) and oy[1].contains(0)
 assert all(z.width()<F(1,10**30)for z in [*ox,*oy])
 checks.append('direct_splitter_mirror_cardinal_control')
for x in [F(33),F(-33)]:
 try:c.exponent(x)
 except ValueError:checks.append('reject_outside_exponent_domain')
 else:raise AssertionError('unbounded exp admitted')
for value,expected in [(F(-1),F(1)),(F(1,2),F(0)),(F(2),F(1))]:
 assert c.lower_error(value,c.I(0,1))==expected
 checks.append('exact_distance_to_reference_interval')
result={'status':'PASS_CPU_MATH_CONTROLS','checks':len(checks),'controls':checks,
        'GPU_executed':False,'H1_confirmatory':False,
        'source_hashes':{'control':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                         'checker':c.sha(Path(c.__file__)),'interval_math':c.sha(c.MATH)}}
path=Path(__file__).resolve().parents[1]/'Docs/research/retrospective_math_controls_v1.json'
path.write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps(result))
