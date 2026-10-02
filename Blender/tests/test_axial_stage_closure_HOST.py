"""Stage-closure regressions and explicit synthetic interior counterexamples."""
import json,sys,unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_stage_closure_HOST_v1 as core
import axial_amplitude_allocation_HOST_v1 as allocation
DATA={}
class ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.relative,cls.fields,cls.powers,cls.trees,cls.pins=core.load_retained()
        cls.names=list(cls.packets)
        cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        for v in core.VARIANTS:
            DATA[v]=core.audit_stage_closure_HOST(cls.names if v in core.VARIANTS[:2] else ['positive'],retained_variant=v,model=core.MODEL)
        DATA['counterexamples']=core.synthetic_domain_counterexamples(model=core.MODEL)
        DATA['reservations']=[];DATA['rejections']=[]
    def test_closure_blocked_even_for_four_partial_groups(self):
        d=DATA[core.VARIANTS[1]]
        self.assertEqual(len(d['cases']),17);self.assertEqual(d['inherited_pins_verified'],243)
        self.assertEqual(d['obligations_checked'],119)
        self.assertEqual(d['restricted_geometry_obligations_available'],8);self.assertEqual(d['missing_obligations'],111)
        self.assertEqual(sum(g['retained_corner_limits_pass'] for c in d['cases'].values() for g in c['groups']),4)
        self.assertEqual(sum(len(c['retained_source_STOP_FAILs']) for c in d['cases'].values()),14)
        for c in d['cases'].values():
            for g in c['groups']:
                self.assertEqual(g['status'],'STOP');self.assertFalse(g['stage_closure_proved'])
                self.assertGreaterEqual(len(g['missing_stage_ids']),6)
                self.assertEqual([x['stage_id'] for x in g['stage_obligations']],list(core.STAGES))
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
    def test_no_upstream_STOP_or_FAIL_erased_and_no_scene_replay(self):
        for v in core.VARIANTS:
            d=DATA[v]
            self.assertEqual(d['new_scene_RN_nodes'],0);self.assertEqual(d['new_scene_geometry_phase_field_power_computations'],0)
            for flag in core.FALSE:self.assertIs(d[flag],False)
            for n,c in d['cases'].items():
                r=self.relative[v]['cases'][n]
                self.assertEqual(c['retained_source_STOP_FAILs'],r['retained_source_STOP_FAILs'])
                for flag in core.FALSE:self.assertIs(c[flag],False)
                for g,rg in zip(c['groups'],r['groups']):
                    for flag in core.FALSE:self.assertIs(g[flag],False)
                    if not rg[core.PARTIAL]:self.assertEqual((g['status'],g['reason']),(rg['status'],rg['reason']))
        for v in core.VARIANTS[2:]:self.assertEqual(DATA[v]['cases']['positive']['groups'][0]['status'],'FAIL')
    def test_synthetic_exact_corners_do_not_bound_interior_RN_or_denominator(self):
        c=DATA['counterexamples'];self.assertEqual(c['synthetic_RN_nodes'],8)
        for k in ('sum','square'):
            r=c[k];self.assertEqual(r['label'],'SYNTHETIC_NOT_SCENE')
            self.assertTrue(all(x['RN_error_abs']==[0,1] for x in r['corners']))
            self.assertGreater(allocation.rational(r['interior']['RN_error_abs']),0)
        self.assertEqual(c['sum']['interior']['RN_error_abs'],[1,2**52])
        self.assertEqual(c['square']['interior']['RN_error_abs'],[1,2**104])
        self.assertEqual(c['reference']['entire_domain_original_lower'],[0,1])
        self.assertEqual(c['reference']['corner_ORIGINAL_lower'],[[1,1],[1,1]])
    def test_reserve_missing_zero_positive_never_counts_as_proof(self):
        for units in ('field_L1','power_abs'):
            for reserve in (None,[0,1],[1,10**12]):
                r=core.reserved_stage_obligation(reserve,units=units,model=core.MODEL)
                DATA['reservations'].append(r);self.assertFalse(r['proved']);self.assertEqual(r['reserved'],reserve)
        for b,u,m,label in [([-1,1],'field_L1',core.MODEL,'negative'),
                            ([0,2],'power_abs',core.MODEL,'noncanonical'),
                            ([True,1],'field_L1',core.MODEL,'bool'),
                            ([1,0],'power_abs',core.MODEL,'denominator'),
                            ([0,1],'radians',core.MODEL,'units'),([0,1],'field_L1','other','model')]:
            with self.assertRaises(ValueError) as caught:core.reserved_stage_obligation(b,units=u,model=m)
            DATA['rejections'].append({'kind':'reservation','reserve':b,'units':u,'model':m,'label':label,'reason':str(caught.exception)})
    def test_bad_selection_and_caller_promotions_rejected(self):
        v=core.VARIANTS[1]
        for names,variant,model,label in [([],v,core.MODEL,'empty'),(['positive','positive'],v,core.MODEL,'duplicate'),
                                         (['unknown'],v,core.MODEL,'unknown'),(['positive'],'other',core.MODEL,'variant'),
                                         (['positive'],v,'other','model'),([True],v,core.MODEL,'bool name'),
                                         (['positive']*65,v,core.MODEL,'bounded')]:
            with self.assertRaises(ValueError) as caught:core.audit_stage_closure_HOST(names,retained_variant=variant,model=model)
            DATA['rejections'].append({'kind':'selection','names':names,'variant':variant,'model':model,'label':label,'reason':str(caught.exception)})
        for k,value in [('stage_closure_proved',True),('reserved',[0,1]),('stage_ids',[]),('proofs',{})]:
            with self.assertRaises(TypeError) as caught:
                core.audit_stage_closure_HOST(['positive'],retained_variant=v,model=core.MODEL,**{k:value})
            DATA['rejections'].append({'kind':'caller_claim','key':k,'value':value,'reason':str(caught.exception)})
    def test_changed_receipt_bytes_rejected_without_filesystem_writes(self):
        original=Path.read_bytes
        targeted=core.io.ROOT/core.PREVIOUS
        for label in ('append_byte','promoted_full_pipeline'):
            raw=original(targeted)
            bad=raw+b' ' if label=='append_byte' else raw.replace(b'"accepted_full_field_pipeline": false',b'"accepted_full_field_pipeline": true',1)
            self.assertNotEqual(raw,bad)
            def fake(path):
                return bad if path==targeted else original(path)
            with patch.object(Path,'read_bytes',fake):
                with self.assertRaises(ValueError) as caught:
                    core.audit_stage_closure_HOST(['positive'],retained_variant=core.VARIANTS[1],model=core.MODEL)
            DATA['rejections'].append({'kind':'changed_report','label':label,'original_sha256':core.PREVIOUS_SHA,
                                       'changed_sha256':core.io.sha(bad) if hasattr(core.io,'sha') else __import__('hashlib').sha256(bad).hexdigest(),
                                       'reason':str(caught.exception)})
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ClosureTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
