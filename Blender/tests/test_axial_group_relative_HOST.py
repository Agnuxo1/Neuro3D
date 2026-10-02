"""New relative-L1 tests; consume pinned fields/powers without numeric replay."""
from fractions import Fraction as F
import json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_group_relative_HOST_v1 as core
import axial_amplitude_allocation_HOST_v1 as allocation
DATA={}
V='explicit_synthetic_INPUT_controls'
def word(v):return struct.unpack('<Q',struct.pack('<d',v))[0]
class RelativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.fields,cls.powers,cls.pins=core.load_retained()
        cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        cls.names=list(cls.packets)
        for v in core.VARIANTS:
            names=cls.names if v in ('missing',V) else ['positive']
            DATA[v]=core.audit_group_relative_HOST(names,retained_variant=v,model=core.MODEL)
        DATA['primitives']=[];DATA['rejections']=[]
    def test_all_four_ORIGINAL_limits_only_at_retained_corners(self):
        d=DATA[V]
        self.assertEqual(d['inherited_pins_verified'],238)
        self.assertEqual(len(d['cases']),17)
        self.assertEqual(sum(c[core.FLAG] for c in d['cases'].values()),4)
        self.assertEqual(d['new_exact_relative_denominator_checks'],16)
        self.assertEqual(sum(len(c['retained_source_STOP_FAILs']) for c in d['cases'].values()),14)
        for n,c in d['cases'].items():
            for g,p in zip(c['groups'],self.powers[V][n]['groups']):
                if p[core.POWER_FLAG]:
                    self.assertTrue(g[core.FLAG]);self.assertTrue(g['absolute_field_gate'])
                    self.assertTrue(g['retained_absolute_relative_power_gates'])
                    self.assertEqual(len(g['field_relative_corners']),4)
                    self.assertEqual(g['unchanged_original_limits'],c['context']['unchanged_limits'])
                else:
                    self.assertEqual((g['status'],g['reason']),(p['status'],p['reason']))
                    self.assertFalse(g['field_relative_gate_evaluated']);self.assertNotIn('field_relative_corners',g)
        self.assertEqual(d['cases']['two_sources']['groups'][0]['blocked_source_ids'],['other'])
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
    def test_missing_power_plan_and_retained_FAIL_cannot_be_rescued_by_relative_PASS(self):
        d=DATA['missing']
        self.assertFalse(any(c[core.FLAG] for c in d['cases'].values()))
        self.assertEqual(d['new_exact_relative_denominator_checks'],16)
        self.assertEqual(sum(g['field_relative_gates_satisfied'] for c in d['cases'].values() for g in c['groups']),4)
        for v in core.VARIANTS:
            for n,c in DATA[v]['cases'].items():
                self.assertEqual(c['retained_source_STOP_FAILs'],self.powers[v][n]['retained_source_STOP_FAILs'])
                for g,p in zip(c['groups'],self.powers[v][n]['groups']):
                    if not p[core.POWER_FLAG]:
                        self.assertEqual((g['status'],g['reason']),(p['status'],p['reason']));self.assertFalse(g[core.FLAG])
        for v in ('zero_absolute','zero_relative'):
            g=DATA[v]['cases']['positive']['groups'][0]
            self.assertEqual(g['status'],'FAIL');self.assertTrue(g['field_relative_gates_satisfied'])
            self.assertFalse(g[core.FLAG]);self.assertFalse(g['retained_absolute_relative_power_gates'])
    def test_no_RN_replay_or_full_scene_native_authorization(self):
        for v in core.VARIANTS:
            d=DATA[v]
            for k in ('new_RN_operations','new_field_products','new_field_reductions','new_power_operations','new_trigonometry','new_ray_traces'):
                self.assertEqual(d[k],0)
            for flag in core.FALSE:self.assertIs(d[flag],False)
            for c in d['cases'].values():
                for flag in core.FALSE:self.assertIs(c[flag],False)
                for g in c['groups']:
                    for flag in core.FALSE:self.assertIs(g[flag],False)
        self.assertEqual(sum(DATA[v]['new_exact_relative_denominator_checks'] for v in core.VARIANTS),40)
    def test_L1_original_denominator_no_epsilon_signed_zero_and_subnormal(self):
        controls=[([word(3.),word(-4.)],[1,1],[1,6]),
                  ([word(3.),word(-4.)],[1,1],[1,7]),
                  ([0,1<<63],[0,1],[0,1]),
                  ([1,0],[0,1],[0,1]),
                  ([word(1.),0],[1,1],[1,1]),
                  ([word(-1.),word(1.)],[0,1],[0,1]),
                  ([1,0],[1,2**1075],[1,1]),
                  ([0,0],[1,1],[1,1]),
                  ([word(1.),0],[2,1],[1,1])]
        for words,b,cap in controls:
            DATA['primitives'].append(core.relative_bound_words(words,b,cap,model=core.MODEL))
        self.assertEqual([p['status'] for p in DATA['primitives']],
                         ['PASS_PARTIAL','FAIL','STOP','PASS_PARTIAL','STOP','PASS_PARTIAL','PASS_PARTIAL','STOP','STOP'])
        self.assertEqual(DATA['primitives'][0]['observed_field_L1_exact'],[7,1])
        self.assertEqual(DATA['primitives'][0]['ORIGINAL_field_L1_lower_bound'],[6,1])
        self.assertEqual(DATA['primitives'][0]['relative_field_L1_upper_bound'],[1,6])
        self.assertEqual(DATA['primitives'][6]['relative_field_L1_upper_bound'],[1,1])
    def test_z_exact_L1_diamond_reference_bound(self):
        rows=list(DATA['primitives'])
        for v in core.VARIANTS:
            rows.extend(r for c in DATA[v]['cases'].values() for g in c['groups'] for r in g.get('field_relative_corners',[]))
        # This final test includes scene receipts and the earlier synthetic primitives.
        checks=0
        for r in rows:
            x,y=map(core.decode,r['input_uint64']);b=allocation.rational(r['field_error_L1_to_ORIGINAL_bound'])
            lower=allocation.rational(r['ORIGINAL_field_L1_lower_bound'])
            for dx,dy in ((F(0),F(0)),(b,F(0)),(-b,F(0)),(F(0),b),(F(0),-b)):
                original=abs(x+dx)+abs(y+dy);actual=abs(dx)+abs(dy)
                self.assertGreaterEqual(original,lower);self.assertLessEqual(actual,b)
                if r['relative_field_L1_upper_bound'] is not None and original:
                    self.assertLessEqual(actual/original,allocation.rational(r['relative_field_L1_upper_bound']))
                checks+=1
        DATA['suite_diamond_reference_checks']=checks
    def test_primitive_and_selection_rejections_no_caller_caps(self):
        primitive=[([],[0,1],[0,1],'shape'),([True,0],[0,1],[0,1],'bool word'),
                   ([-1,0],[0,1],[0,1],'negative word'),([2**64,0],[0,1],[0,1],'range'),
                   ([0x7ff0000000000000,0],[0,1],[0,1],'Inf'),([0x7ff8000000000000,0],[0,1],[0,1],'NaN'),
                   ([0,0],[-1,1],[0,1],'negative bound'),([0,0],[0,2],[0,1],'noncanonical bound'),
                   ([0,0],[True,1],[0,1],'bool bound'),([0,0],[1,0],[0,1],'zero bound denominator'),
                   ([0,0],[0,1],[-1,1],'negative cap'),([0,0],[0,1],[0,2],'noncanonical cap'),
                   ([0,0],[0,1],[True,1],'bool cap'),([0,0],[0,1],[1,0],'zero cap denominator')]
        for w,b,cap,label in primitive:
            with self.assertRaises(ValueError) as caught:core.relative_bound_words(w,b,cap,model=core.MODEL)
            DATA['rejections'].append({'kind':'primitive','words':w,'bound':b,'cap':cap,'label':label,'reason':str(caught.exception)})
        for names,v,m,label in [([],V,core.MODEL,'empty'),(['positive','positive'],V,core.MODEL,'duplicate'),
                               (['unknown'],V,core.MODEL,'unknown'),(['positive'],'other',core.MODEL,'variant'),
                               (['positive'],V,'other','model'),(['positive']*65,V,core.MODEL,'bounded'),
                               ([True],V,core.MODEL,'bool name')]:
            with self.assertRaises(ValueError) as caught:core.audit_group_relative_HOST(names,retained_variant=v,model=m)
            DATA['rejections'].append({'kind':'selection','names':names,'variant':v,'model':m,'label':label,'reason':str(caught.exception)})
        with self.assertRaises(TypeError) as caught:
            core.audit_group_relative_HOST(['positive'],retained_variant=V,model=core.MODEL,relative_cap=[1,1])
        DATA['rejections'].append({'kind':'caller_cap','label':'injection','reason':str(caught.exception)})
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(RelativeTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
