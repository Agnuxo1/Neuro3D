"""Own new gate tests: reuse retained bounds, never execute numeric producers."""
import base64
from copy import deepcopy
import hashlib,json,sys,unittest,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_source_budget_gate_HOST_v1 as core
import axial_amplitude_allocation_HOST_v1 as allocation
RESULTS={}
class BudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.old,cls.pins=core.load_retained()
        cls.prev=core.payload(allocation.parse(core.read(core.PREVIOUS,core.PREVIOUS_SHA)))
        cls.names=list(cls.packets);cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        RESULTS['missing']=core.audit_retained_product_budget_HOST(cls.names,dict.fromkeys(cls.names),model=core.MODEL)
        RESULTS['controls']={}
        for label,name in [('positive','positive'),('two_sources','two_sources'),('explicit_zero_caps','positive')]:
            RESULTS['controls'][label]=core.audit_retained_product_budget_HOST([name],{name:cls.prev['plans'][label]},model=core.MODEL)
        RESULTS['rejections']=[]
    def reject(self,names,plans,model,label):
        before=allocation.digest(plans)
        with self.assertRaises((ValueError,TypeError,KeyError)) as caught:
            core.audit_retained_product_budget_HOST(names,plans,model=model)
        self.assertEqual(before,allocation.digest(plans))
        RESULTS['rejections'].append({'label':label,'names':names,'plans':plans,'model':model,
                                       'type':type(caught.exception).__name__,'reason':str(caught.exception)})
    def test_17_cases_19_sources_14_STOP_5_missing_not_zero(self):
        rows=[s for v in RESULTS['missing']['cases'].values() for s in v['sources']]
        self.assertEqual(len(rows),19);self.assertEqual(len(RESULTS['missing']['cases']),17)
        self.assertEqual(sum(s['source_product_evaluated'] for s in rows),5)
        for n,v in RESULTS['missing']['cases'].items():
            for s,old in zip(v['sources'],self.old[n]['sources']):
                self.assertEqual(s['status'],'STOP');self.assertFalse(s['source_budget_evaluated'])
                self.assertFalse(s[core.FLAG])
                if not old['source_product_evaluated']:
                    self.assertEqual(s['reason'],old['reason'])
                else:
                    self.assertIn('no default split/zero',s['reason'])
                    self.assertNotIn('source_cap_L1',s)
    def test_positive_static_quarter_accepts_ONLY_retained_partial_bound(self):
        v=RESULTS['controls']['positive']['cases']['positive']
        self.assertTrue(v[core.FLAG]);self.assertTrue(v['sources'][0]['source_budget_evaluated'])
        self.assertEqual(v['sources'][0]['status'],'PASS_PARTIAL')
        self.assertTrue(v['groups'][0][core.FLAG])
    def test_two_sources_never_promote_blocked_other_or_group(self):
        v=RESULTS['controls']['two_sources']['cases']['two_sources']
        self.assertTrue(v['allocation_result']['allocation_INPUT_valid'])
        self.assertTrue(v['sources'][0][core.FLAG]);self.assertFalse(v['sources'][1][core.FLAG])
        self.assertEqual(v['sources'][1]['reason'],self.old['two_sources']['sources'][1]['reason'])
        self.assertEqual(v['sources'][1]['status'],'STOP')
        self.assertFalse(v[core.FLAG]);self.assertFalse(v['groups'][0][core.FLAG])
    def test_zero_cap_valid_INPUT_but_nonzero_product_error_FAIL(self):
        v=RESULTS['controls']['explicit_zero_caps']['cases']['positive']
        self.assertTrue(v['allocation_result']['allocation_INPUT_valid'])
        s=v['sources'][0]
        self.assertEqual(s['source_cap_L1'],[0,1]);self.assertGreater(s['product_error_L1_to_ORIGINAL_bound'][0],0)
        self.assertEqual(s['status'],'FAIL');self.assertFalse(s[core.FLAG])
        self.assertEqual(s['unchanged_original_phase_cap_rad'],[0,1])
        self.assertFalse(v[core.FLAG])
    def test_invalid_selection_coverage_context_outputs_and_missing_units(self):
        p=self.prev['plans']['positive']
        for names,plans,model,label in [
            ([],{},core.MODEL,'empty selection'),
            (['positive','positive'],{'positive':p},core.MODEL,'duplicate selection'),
            (['unknown'],{'unknown':None},core.MODEL,'unknown receipt'),
            (['positive'],{},core.MODEL,'absent allocation mapping'),
            (['positive'],{'positive':p,'negative':None},core.MODEL,'extra mapping'),
            (['positive'],{'positive':p},'foreign','foreign model'),
            (['two_sources'],{'two_sources':self.prev['plans']['synthetic_two_groups']},core.MODEL,'changed group INPUT not matching product receipt')]:
            self.reject(names,deepcopy(plans),model,label)
        for label,key,value in [('external numeric output','product_error_L1_to_ORIGINAL_bound',[0,1]),
                                ('caller context','context',{}),('units phase substitution','units','rad'),
                                ('context rehash','context_sha256','0'*64)]:
            q=deepcopy(p);q[key]=value
            self.reject(['positive'],{'positive':q},core.MODEL,label)
    def test_full_flags_FALSE_no_numeric_reexecution_original_inputs_immutable(self):
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
        for result in [RESULTS['missing'],*RESULTS['controls'].values()]:
            self.assertEqual(result['new_numeric_products'],0);self.assertEqual(result['new_trigonometry_evaluations'],0)
            self.assertEqual(result['inherited_pins_verified'],213)
            for k in core.FALSE_FLAGS:
                self.assertIs(result[k],False)
            for v in result['cases'].values():
                self.assertEqual(v['numerical_evidence'],'retained_no_numerical_reexecution')
                for k in core.FALSE_FLAGS:
                    self.assertIs(v[k],False)
                    for s in v['sources']:
                        self.assertIs(s[k],False)
                for g in v['groups']:
                    self.assertIs(g['remaining_stages_error_proved'],False)
                    self.assertIs(g['accepted_full_field_pipeline'],False)
if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BudgetTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'results':RESULTS},sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
