"""New HOST power tests only; all field computation reused as pinned receipts."""
from copy import deepcopy
from fractions import Fraction as F
import json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_group_power_HOST_v1 as core
import axial_amplitude_allocation_HOST_v1 as allocation
DATA={}
VARIANT='explicit_synthetic_INPUT_controls'
def word(x):return struct.unpack('<Q',struct.pack('<d',x))[0]
def plan(ctx,c,variant=VARIANT):
    cap=allocation.rational(ctx['unchanged_limits']['power'])
    return {'model':core.MODEL,'units':core.UNITS,'context_sha256':allocation.digest(ctx),'retained_variant':variant,
            'field_allocation_INPUT_sha256':c['allocation_result']['allocation_sha256'],
            'field_reduction_stage_INPUT_sha256':c['stage_result']['stage_plan_sha256'],
            'groups':[{'port':p,'coherence_group':g,'field_to_power_cap_abs':core.pair(cap/4),
                       'power_RN64_cap_abs':core.pair(cap/4),'other_power_stages_reserved_abs':core.pair(cap/2),
                       'relative_power_cap':deepcopy(ctx['unchanged_limits']['relative_power'])} for p,g in ctx['groups']]}
class PowerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.variants,cls.pins=core.load_retained();cls.names=list(cls.packets)
        cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        cls.plans={}
        for n in cls.names:
            ctx=allocation.context_from_packet(cls.packets[n],allocation.digest(cls.packets[n]),model=allocation.MODEL)
            cls.plans[n]=plan(ctx,cls.variants[VARIANT][n])
        DATA['power_INPUT_plans']=cls.plans
        DATA['missing']=core.audit_group_power_HOST(cls.names,dict.fromkeys(cls.names),retained_variant=VARIANT,model=core.MODEL)
        DATA['explicit_synthetic_INPUT_controls']=core.audit_group_power_HOST(cls.names,cls.plans,retained_variant=VARIANT,model=core.MODEL)
        DATA['primitives']=[];DATA['rejections']=[]
    def test_original_limits_separate_power_units_and_preserve_group_STOP(self):
        d=DATA['explicit_synthetic_INPUT_controls'];self.assertEqual(len(d['cases']),17)
        self.assertEqual(sum(c[core.FLAG] for c in d['cases'].values()),4)
        self.assertEqual(d['power_corner_evaluations'],16);self.assertEqual(d['new_RN64_power_operations'],48)
        self.assertEqual(sum(len(c['retained_source_STOP_FAILs']) for c in d['cases'].values()),14)
        for n,c in d['cases'].items():
            for g,old in zip(c['groups'],self.variants[VARIANT][n]['groups']):
                if old[core.FIELD_FLAG]:
                    self.assertTrue(g[core.FLAG]);self.assertEqual(len(g['power_corners']),4)
                    self.assertEqual(g['unchanged_original_limits'],c['context']['unchanged_limits'])
                else:
                    self.assertEqual(g['status'],'STOP');self.assertEqual(g['reason'],old['reason'])
                    self.assertFalse(g['power_evaluated_HOST']);self.assertNotIn('power_corners',g)
            self.assertFalse(DATA['missing']['cases'][n][core.FLAG])
        self.assertEqual(d['cases']['two_sources']['groups'][0]['blocked_source_ids'],['other'])
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
        self.assertEqual(d['inherited_pins_verified'],233)
    def test_only_partial_power_no_detector_or_field_replay(self):
        for d in (DATA['missing'],DATA['explicit_synthetic_INPUT_controls']):
            for flag in core.FALSE:self.assertIs(d[flag],False)
            self.assertIs(d['field_L1_reserve_used_as_power_budget'],False)
            for k in ('new_field_products','new_field_reductions','new_trigonometry','new_ray_traces'):self.assertEqual(d[k],0)
            for c in d['cases'].values():
                for flag in core.FALSE:self.assertIs(c[flag],False)
                for g in c['groups']:
                    for flag in core.FALSE:self.assertIs(g[flag],False)
                    if g['power_evaluated_HOST']:
                        for v in g['power_corners']:
                            self.assertEqual(v['RN64_operations'],3)
                            self.assertLessEqual(allocation.rational(v['actual_error_abs_to_represented_power']),
                                                 allocation.rational(v['power_RN64_error_abs_bound']))
        self.assertEqual(DATA['missing']['new_RN64_power_operations'],0)
    def test_explicit_zero_abs_and_relative_cups_FAIL_no_automatic_rescue(self):
        n='positive';ctx=self.variants[VARIANT][n]['context'];cap=ctx['unchanged_limits']['power']
        for mode in ('zero_absolute','zero_relative'):
            p=deepcopy(self.plans[n]);g=p['groups'][0]
            if mode=='zero_absolute':
                g['field_to_power_cap_abs']=[0,1];g['power_RN64_cap_abs']=[0,1];g['other_power_stages_reserved_abs']=cap
            else:g['relative_power_cap']=[0,1]
            DATA[mode+'_INPUT']=p
            DATA[mode]=core.audit_group_power_HOST([n],{n:p},retained_variant=VARIANT,model=core.MODEL)
            result=DATA[mode]['cases'][n]['groups'][0]
            self.assertEqual(result['status'],'FAIL');self.assertFalse(result[core.FLAG])
            if mode=='zero_absolute':self.assertFalse(result['absolute_power_gate'])
            else:self.assertFalse(result['relative_power_gate']);self.assertTrue(result['absolute_power_gate'])
    def test_primitive_underflow_signedzero_nonzero_field_error_and_zero_denominator(self):
        controls=[([word(.1),word(-.2)],[1,10**15]),
                  ([0,1<<63],[0,1]),([1,(1<<63)|1],[0,1]),
                  ([0x0010000000000000,0],[0,1]),([word(1e150),word(-1e150)],[0,1]),
                  ([word(1.0),word(1.0)],[1,1]),([word(3.0),word(-4.0)],[1,8])]
        for w,b in controls:
            result=core.measure_words(w,b,model=core.MODEL);DATA['primitives'].append(result)
            r,i=map(core.decode,w);bound=allocation.rational(b);prop=allocation.rational(result['field_to_power_error_abs_bound'])
            represented=r*r+i*i
            for dr,di in ((bound,F(0)),(-bound,F(0)),(F(0),bound),(F(0),-bound)):
                actual=abs((r+dr)**2+(i+di)**2-represented)
                self.assertLessEqual(actual,prop)
        self.assertEqual(DATA['primitives'][1]['observed_power_uint64'],0)
        self.assertIsNone(DATA['primitives'][1]['relative_power_error_bound'])
        self.assertIsNone(DATA['primitives'][5]['relative_power_error_bound'])
        self.assertGreater(allocation.rational(DATA['primitives'][2]['power_RN64_error_abs_bound']),0)
        self.assertEqual(DATA['primitives'][4]['power_RN64_error_abs_bound'],DATA['primitives'][4]['actual_error_abs_to_represented_power'])
    def test_power_INPUT_injection_binding_coverage_units_and_cap_rejections(self):
        n='positive'
        mutations=[(['model'],'other','model'),(['units'],'ORIGINAL-source-field-amplitude-L1','L1 not power'),
                   (['context_sha256'],'0'*64,'context'),(['retained_variant'],'missing','variant'),
                   (['field_allocation_INPUT_sha256'],'0'*64,'field source SHA'),
                   (['field_reduction_stage_INPUT_sha256'],'0'*64,'field reduction SHA'),
                   (['groups'],[],'missing groups'),(['groups',0,'port'],'X','port'),
                   (['groups',0,'coherence_group'],'X','coherence'),
                   (['groups',0,'field_to_power_cap_abs'],[True,1],'bool'),
                   (['groups',0,'power_RN64_cap_abs'],[0,2],'noncanonical'),
                   (['groups',0,'other_power_stages_reserved_abs'],[-1,1],'negative'),
                   (['groups',0,'power_RN64_cap_abs'],[1,1],'absolute overspend'),
                   (['groups',0,'relative_power_cap'],[1,1],'relative cap enlargement'),
                   (['observed_power'],0,'caller output'),
                   (['groups',0,'field_L1_reserve_used_as_power_budget'],True,'caller field reserve substitution')]
        for path,value,label in mutations:
            p=deepcopy(self.plans[n]);o=p
            for k in path[:-1]:o=o[k]
            o[path[-1]]=value
            with self.assertRaises((ValueError,KeyError,TypeError)) as caught:
                core.audit_group_power_HOST([n],{n:p},retained_variant=VARIANT,model=core.MODEL)
            DATA['rejections'].append({'kind':'plan','path':path,'value':value,'label':label,'reason':str(caught.exception)})
        for names,plans,variant,model,label in [
            ([n,n],{n:self.plans[n]},VARIANT,core.MODEL,'duplicate'),
            ([n],{},VARIANT,core.MODEL,'missing plan map'),
            (['unknown'],{'unknown':None},VARIANT,core.MODEL,'unknown case'),
            ([n],{n:None},'other',core.MODEL,'unknown variant'),
            ([n],{n:None},VARIANT,'other','missing opt-in model'),
            ([n],{n:self.plans[n]},'missing_stage',core.MODEL,'variant/upstream mismatch')]:
            with self.assertRaises(ValueError) as caught:core.audit_group_power_HOST(names,plans,retained_variant=variant,model=model)
            DATA['rejections'].append({'kind':'selection','label':label,'reason':str(caught.exception)})
    def test_nonfinite_overflow_word_shape_and_bound_rejections(self):
        for w,b,label in [([], [0,1],'shape'),([True,0],[0,1],'bool word'),([2**64,0],[0,1],'range'),
                          ([0x7ff0000000000000,0],[0,1],'inf'),([0x7ff8000000000000,0],[0,1],'NaN'),
                          ([0x7fefffffffffffff,0],[0,1],'square overflow'),([0,0],[-1,1],'negative bound'),
                          ([0,0],[0,2],'noncanonical bound'),([0,0],[True,1],'bool bound')]:
            with self.assertRaises(ValueError) as caught:core.measure_words(w,b,model=core.MODEL)
            DATA['rejections'].append({'kind':'primitive','words':w,'bound':b,'label':label,'reason':str(caught.exception)})
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(PowerTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
