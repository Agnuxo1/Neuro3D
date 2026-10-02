"""Uniform box regressions: no old producer replay or scene promotion."""
import hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_uniform_power_box_HOST_v1 as core
import axial_amplitude_allocation_HOST_v1 as allocation
DATA={}
class BoxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.relative,cls.fields,cls.powers,cls.closure,cls.pins=core.load_retained()
        cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        for v in core.VARIANTS:
            names=list(cls.packets) if v in core.VARIANTS[:2] else ['positive']
            DATA[v]=core.audit_uniform_power_box_HOST(names,retained_variant=v,model=core.MODEL)
        DATA['samples']=core.synthetic_power_samples(model=core.MODEL)
        DATA['witnesses_reused']=cls.closure['counterexamples']
        DATA['primitives']=[];DATA['rejections']=[]
    def test_declared_boxes_without_promoting_source_or_scene(self):
        d=DATA[core.VARIANTS[1]]
        self.assertEqual(d['inherited_pins_verified'],248);self.assertEqual(d['boxes_computed'],4)
        self.assertEqual(sum(len(c['retained_source_STOP_FAILs']) for c in d['cases'].values()),14)
        for c in d['cases'].values():
            for g in c['groups']:
                self.assertEqual(g['status'],'STOP')
                if g['box_computed']:
                    t=g['box_theorem']
                    self.assertTrue(t['uniform_RN_bound_for_declared_box_proved'])
                    self.assertIsNone(t['uniform_field_error_L1_hypothesis'])
                    self.assertIsNone(t['ORIGINAL_power_global_lower'])
                    self.assertTrue(g['declared_box_RN_budget_fits'])
                for flag in core.FALSE:self.assertIs(g[flag],False)
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
    def test_preserved_upstream_and_variants(self):
        for v in core.VARIANTS:
            d=DATA[v]
            self.assertEqual(d['new_scene_RN_nodes'],0)
            for flag in core.FALSE:self.assertIs(d[flag],False)
            for n,c in d['cases'].items():
                old=self.closure[v]['cases'][n]
                self.assertEqual(c['retained_source_STOP_FAILs'],old['retained_source_STOP_FAILs'])
                for g,cg in zip(c['groups'],old['groups']):
                    if not g['box_computed'] or cg['status']=='FAIL':
                        self.assertEqual((g['status'],g['reason']),(cg['status'],cg['reason']))
                    self.assertEqual(g['remaining_missing_stage_ids'],cg['missing_stage_ids'])
        for v in core.VARIANTS[2:]:
            self.assertEqual(DATA[v]['cases']['positive']['groups'][0]['status'],'FAIL')
    def test_global_reference_crossing_zero_and_conditional_B(self):
        boxes=[([[[1,1],[2,1]],[[0,1],[0,1]]],[0,1]),
               ([[[-1,1],[1,1]],[[0,1],[0,1]]],[0,1]),
               ([[[2,1],[3,1]],[[4,1],[5,1]]],[1,2]),
               ([[[0,1],[0,1]],[[0,1],[0,1]]],None),
               ([[[1,1],[2,1]],[[0,1],[0,1]]],[2,1]),
               ([[[-3,1],[-2,1]],[[4,1],[5,1]]],[1,4])]
        for box,b in boxes:
            t=core.uniform_box_bound(box,uniform_field_error_L1=b,model=core.MODEL)
            DATA['primitives'].append(t)
        self.assertEqual(DATA['primitives'][0]['ORIGINAL_field_L1_global_lower'],[1,1])
        self.assertEqual(DATA['primitives'][1]['ORIGINAL_power_global_lower'],[0,1])
        self.assertEqual(DATA['primitives'][1]['status'],'STOP')
        self.assertEqual(DATA['primitives'][2]['ORIGINAL_field_L1_global_lower'],[11,2])
        self.assertEqual(DATA['primitives'][2]['ORIGINAL_power_global_lower'],[49,4])
        self.assertEqual(DATA['primitives'][4]['status'],'STOP')
        self.assertEqual(DATA['primitives'][3]['power_RN64_uniform_charge'],[0,1])
    def test_old_interior_witnesses_covered_without_replaying_them(self):
        w=DATA['witnesses_reused']
        for key in ('sum','square'):
            self.assertGreater(core.number(w[key]['interior']['RN_error_abs']),0)
            self.assertLessEqual(core.number(w[key]['interior']['RN_error_abs']),core.rounding_charge(F(4)))
        self.assertEqual(w['reference']['entire_domain_original_lower'],[0,1])
        self.assertEqual(w['synthetic_RN_nodes'],8) # inherited, not new
        self.assertEqual(DATA['samples']['new_synthetic_RN_nodes'],36)
        for sample in DATA['samples']['samples']:
            self.assertLessEqual(core.number(sample['actual_power_error_abs']),
                                 core.number(sample['box_theorem']['power_RN64_uniform_charge']))
    def test_malformed_overflow_and_caller_injections(self):
        valid=[[[0,1],[1,1]],[[0,1],[0,1]]]
        def reject(label,fn,exc=ValueError):
            with self.assertRaises(exc) as caught:fn()
            DATA['rejections'].append({'label':label,'reason':str(caught.exception)})
        for label,box in [('bool',[[[False,1],[1,1]],[[0,1],[0,1]]]),
                          ('unreduced',[[[0,2],[1,1]],[[0,1],[0,1]]]),
                          ('negative_denominator',[[[0,-1],[1,1]],[[0,1],[0,1]]]),
                          ('unordered',[[[2,1],[1,1]],[[0,1],[0,1]]]),
                          ('NaN',[[[float('nan'),1],[1,1]],[[0,1],[0,1]]]),
                          ('huge',[[[0,1],[2**4097,1]],[[0,1],[0,1]]]),
                          ('overflow_square',[[core.pair(core.MAX),core.pair(core.MAX)],[[0,1],[0,1]]]),
                          ('overflow_add',[[core.pair(F(2)**512)]*2,[core.pair(F(2)**512)]*2]),
                          ('wrong_shape',[valid[0]])]:
            reject(label,lambda box=box:core.uniform_box_bound(box,uniform_field_error_L1=None,model=core.MODEL))
        for b in ([-1,1],[True,1],[1,0],[2,4]):
            reject('bad_B_'+str(b),lambda b=b:core.uniform_box_bound(valid,uniform_field_error_L1=b,model=core.MODEL))
        reject('model',lambda:core.uniform_box_bound(valid,uniform_field_error_L1=None,model='other'))
        for names in ([],['positive','positive'],['unknown'],[True]):
            reject('names_'+str(names),lambda names=names:core.audit_uniform_power_box_HOST(names,retained_variant=core.VARIANTS[1],model=core.MODEL))
        reject('variant',lambda:core.audit_uniform_power_box_HOST(['positive'],retained_variant='other',model=core.MODEL))
        for key,value in [('box',valid),('uniform_field_error_L1',[0,1]),('cap',[1,1]),
                          ('scene_image_enclosed',True),('certificate',{})]:
            reject('caller_'+key,lambda key=key,value=value:core.audit_uniform_power_box_HOST(
                ['positive'],retained_variant=core.VARIANTS[1],model=core.MODEL,**{key:value}),TypeError)
    def test_changed_retained_bytes_rejected_before_coverage(self):
        target=core.io.ROOT/core.PREVIOUS;original=Path.read_bytes;raw=original(target);bad=raw+b' '
        with patch.object(Path,'read_bytes',lambda p:bad if p==target else original(p)):
            with self.assertRaises(ValueError) as caught:
                core.audit_uniform_power_box_HOST(['positive'],retained_variant=core.VARIANTS[1],model=core.MODEL)
        DATA['rejections'].append({'label':'changed_predecessor','reason':str(caught.exception),
                                   'changed_sha256':hashlib.sha256(bad).hexdigest()})
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(BoxTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
