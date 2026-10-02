"""New readout-boundary contract tests; old producers and suites are not executed."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_HOST_readout_contract_v1 as core
DATA={}
class ReadoutContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit,cls.pins=core.load_retained()
        cls.plan=core.make_proposed_contract(cls.audit)
    def test_contract_and_stops(self):
        DATA['proposed_contract']=self.plan
        result=core.validate_contract(self.plan,model=core.MODEL);DATA['audit']=result
        self.assertTrue(result['contract_schema_valid'])
        self.assertEqual((result['restricted_power_receipts_available'],result['upstream_unproved_groups'],
                          result['all_readouts_stopped']),(2,15,17))
        self.assertEqual((result['retained_unit_STOPs'],result['nonzero_domains_not_refined']),(14,2))
        self.assertEqual(result['unmeasured_cost_stages'],list(core.STAGES))
        self.assertEqual(result['inherited_pins_verified'],293)
        for row in result['outputs']:
            self.assertEqual(row['readout_status'],'STOP')
            for key in core.FALSE:self.assertIs(row[key],False)
        self.assertEqual(result['retained_zero_budget_FAIL_controls'],self.audit['retained_zero_budget_FAIL_controls'])
    def test_no_partial_two_sources(self):
        out=next(o for o in self.plan['outputs'] if o['case_name']=='two_sources')
        self.assertEqual(out['complete_source_order'],['s','other'])
        row=next(r for r in DATA['audit']['outputs'] if r['case_name']=='two_sources')
        self.assertFalse(row['restricted_power_proof_available'])
        self.assertIsNone(row['retained_power_uint64_decimal'])
    def test_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        for label,mut in [
            ('missing_output',lambda p:p['outputs'].pop()),
            ('duplicated_output',lambda p:p['outputs'].__setitem__(0,copy.deepcopy(p['outputs'][1]))),
            ('partial_sources',lambda p:next(o for o in p['outputs'] if o['case_name']=='two_sources')['complete_source_order'].pop()),
            ('case_order',lambda p:p['case_order'].reverse()),
            ('source_order',lambda p:p['outputs'][0]['input_binding']['source_order'].append('other')),
            ('snapshot',lambda p:p['outputs'][0]['input_binding'].__setitem__('original_snapshot_sha256','0'*64)),
            ('ABI',lambda p:p['outputs'][0]['input_binding'].__setitem__('word_ABI_sha256','0'*64)),
            ('scene',lambda p:p['outputs'][0]['input_binding'].__setitem__('scene_binding_sha256','0'*64)),
            ('group_contract',lambda p:p['outputs'][0]['input_binding'].__setitem__('original_group_contract_sha256','0'*64)),
            ('packet',lambda p:p['outputs'][0]['input_binding'].__setitem__('input_packet_sha256','0'*64)),
            ('caps',lambda p:p['outputs'][0]['input_binding']['unchanged_limits'].__setitem__('power',[1,1])),
            ('port',lambda p:p['outputs'][0].__setitem__('port','other')),
            ('coherence_merge',lambda p:p['outputs'][0].__setitem__('group_combination','sum_groups')),
            ('terminal_reference',lambda p:p['outputs'][0]['references'][0].__setitem__('terminal_reference_id','other')),
            ('source_phase_reference',lambda p:p['outputs'][0]['references'][0].__setitem__('source_phase_reference_id','other')),
            ('rebase_gauge',lambda p:p['outputs'][0]['references'][0].__setitem__('rebase_cycles',[1,1])),
            ('power_sha',lambda p:p['outputs'][0].__setitem__('retained_power_row_sha256','0'*64)),
            ('units_watts',lambda p:p['outputs'][0].__setitem__('units','watts')),
            ('units_joules',lambda p:p['outputs'][0].__setitem__('units','joules')),
            ('detector_observable',lambda p:p['outputs'][0].__setitem__('observable','physical_detector')),
            ('new_rounding',lambda p:p['outputs'][0].__setitem__('readout_operation','float32')),
            ('budget_injected',lambda p:p['outputs'][0].__setitem__('budget_allocation_INPUT',[1,1])),
            ('gain',lambda p:p['outputs'][0].__setitem__('gain',[1,1])),
            ('exposure',lambda p:p['outputs'][0].__setitem__('exposure',[1,1])),
            ('area',lambda p:p['outputs'][0].__setitem__('area_integration',[1,1])),
            ('calibration',lambda p:p['outputs'][0].__setitem__('calibration','physical')),
            ('offset',lambda p:p['outputs'][0].__setitem__('offset',[0,1])),
            ('quantization',lambda p:p['outputs'][0].__setitem__('quantization','uint16')),
            ('bool_index',lambda p:p['outputs'][0].__setitem__('group_index',False)),
            ('extra_output_key',lambda p:p['outputs'][0].__setitem__('native',True)),
            ('old_scene_provenance',lambda p:p.__setitem__('provenance','INPUT')),
            ('report_sha',lambda p:p['retained_power_report'].__setitem__('sha256','0'*64)),
            ('hidden_download',lambda p:p['cost_ledger'].pop()),
            ('fake_zero_cost',lambda p:p['cost_ledger'][0].update(status='MEASURED',seconds=0,bytes=0)),
            ('equivalence_claim',lambda p:p['comparison_contract'].__setitem__('same_work_and_outputs_authenticated',True)),
            ('guard_injection',lambda p:p['comparison_contract'].__setitem__('guard_and_exclusive_job_receipt','unverified')),
            ('admission',lambda p:p.__setitem__('GPU_job_admission',True)),
            ('physical_claim',lambda p:p.__setitem__('physical_detector_calibrated',True)),
            ('fullpipeline_claim',lambda p:p.__setitem__('accepted_full_field_pipeline',True)),
            ('unknown_key',lambda p:p.__setitem__('secret',1))]:
            plan=copy.deepcopy(self.plan);mut(plan)
            reject(label,lambda plan=plan:core.validate_contract(plan,model=core.MODEL))
        reject('model',lambda:core.validate_contract(self.plan,model='wrong'))
        reject('not_object',lambda:core.validate_contract([],model=core.MODEL))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_sha',core.load_retained)
    def test_proposal_is_not_INPUT_or_execution(self):
        self.assertEqual(self.plan['provenance'],'SYNTHETIC proposed INPUT; absent from retained scene')
        self.assertTrue(all(o['budget_allocation_INPUT'] is None for o in self.plan['outputs']))
        for k in core.FALSE:self.assertIs(self.plan[k],False)
        # A caller cannot mutate the pinned audit through the proposed deep copies.
        self.plan['outputs'][0]['input_binding']['source_order'].append('bad')
        self.assertNotIn('bad',self.audit['cases'][self.audit['case_order'][0]]['context']['source_order'])
        self.plan['outputs'][0]['input_binding']['source_order'].pop()
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReadoutContractTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
