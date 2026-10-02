"""Static synthetic INPUT plans only, never adopted; no producer/suite replay."""
import copy,json,sys,unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_stage_allocation_HOST_v1 as core
DATA={}
def input_plan(packet):
    ctx=core.allocation.context_from_packet(packet,core.digest(packet),model=core.allocation.MODEL)
    cap=F(*ctx['unchanged_field_L1_cap']);sources=[{'source_id':sid,'cap_L1':core.pair(cap/4),
        'stages_L1':dict.fromkeys(core.STAGES,[1,10**14])} for sid in ctx['source_order']]
    groups=[]
    for port,group in ctx['groups']:
        members=sum(a['port']==port and a['coherence_group']==group for a in ctx['assignments'])
        reserve=(cap-members*cap/4)/2
        groups.append({'port':port,'coherence_group':group,'reserves_L1':dict.fromkeys(core.RESERVES,core.pair(reserve))})
    return {'model':core.MODEL,'units':core.UNITS,'context_sha256':core.digest(ctx),'sources':sources,'groups':groups}
class StageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.pins=cls.retained
        # Fixed quotas chosen from INPUT alone, before comparison. Not numerical-error fitting.
        cls.plans={n:input_plan(cls.packets[n]) for n in ('nonexact_geometry_phase_PASS','thin_resolved','two_sources')}
    def test_a_absent_real_inputs(self):
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core,'compare_source',side_effect=AssertionError('no plan no comparison')),patch.object(core.prior,'audit_reflection_CPU',side_effect=AssertionError('no old audit')),patch.object(core.prior,'native_negate',side_effect=AssertionError('no material replay')):
            a=core.audit_stage_allocation_HOST(self.old['case_order'],{},model=core.MODEL)
        DATA['real_absent']=a
        self.assertEqual((a['explicit_INPUT_plans_valid'],a['missing_INPUT_plans_STOP'],a['inherited_pins_verified']),(0,17,353))
        self.assertEqual(sum(len(c['sources']) for c in a['cases'].values()),19)
        for c in a['cases'].values():
            self.assertEqual(c['status'],'STOP')
            for k in core.FALSE:self.assertFalse(c[k])
    def test_b_static_synthetic_plans(self):
        before=core.digest(self.retained);plans=copy.deepcopy(self.plans);DATA['synthetic_INPUT_plans']=copy.deepcopy(plans)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'native_negate',side_effect=AssertionError('no native material')),patch.object(core.prior.prior,'execute_prefix',side_effect=AssertionError('no fresh inference')):
            a=core.audit_stage_allocation_HOST(list(plans),plans,model=core.MODEL)
        DATA['synthetic_comparisons']=a
        self.assertEqual(core.digest(self.retained),before);self.assertEqual(plans,self.plans)
        self.assertEqual((a['explicit_INPUT_plans_valid'],a['retained_point_source_stage_comparisons_fit']),(3,2))
        for n in ('nonexact_geometry_phase_PASS','thin_resolved'):
            self.assertTrue(a['cases'][n]['sources'][0]['retained_point_stage_budget_fits'])
            self.assertEqual(a['cases'][n]['status'],'STOP')
        self.assertFalse(a['cases']['two_sources']['sources'][1]['retained_point_stage_budget_fits'])
        for c in a['cases'].values():
            for row in c['sources']:
                for k in core.FALSE:self.assertFalse(row[k])
    def test_c_stage_overspend_not_hidden_by_total(self):
        plan=copy.deepcopy(self.plans['nonexact_geometry_phase_PASS']);plan['sources'][0]['stages_L1']['source_Horner_L1']=[0,1]
        with patch.object(core,'load_retained',return_value=self.retained):
            a=core.audit_stage_allocation_HOST(['nonexact_geometry_phase_PASS'],{'nonexact_geometry_phase_PASS':plan},model=core.MODEL)
        row=a['cases']['nonexact_geometry_phase_PASS']['sources'][0]
        self.assertTrue(row['total_charge_fits_source_cap']);self.assertFalse(row['stage_comparisons']['source_Horner_L1']['fits'])
        self.assertFalse(row['retained_point_stage_budget_fits'])
        DATA['stage_overspend_control']={'INPUT_plan':plan,'audit':a}
        zero=copy.deepcopy(self.plans['thin_resolved']);zero['sources'][0]['cap_L1']=[0,1];zero['sources'][0]['stages_L1']=dict.fromkeys(core.STAGES,[0,1])
        with patch.object(core,'load_retained',return_value=self.retained):
            z=core.audit_stage_allocation_HOST(['thin_resolved'],{'thin_resolved':zero},model=core.MODEL)
        self.assertTrue(z['cases']['thin_resolved']['allocation_INPUT']['allocation_INPUT_valid'])
        self.assertFalse(z['cases']['thin_resolved']['sources'][0]['retained_point_stage_budget_fits'])
        DATA['explicit_zero_FAIL']={'INPUT_plan':zero,'audit':z}
    def test_d_invalid_INPUT(self):
        rejects=[];DATA['rejections']=rejects
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejects.append({'label':label,'reason':str(cm.exception)})
        p=self.packets['thin_resolved'];plan=self.plans['thin_resolved']
        mutations=[
            ('model',lambda v:v.__setitem__('model','old')),('units_rad',lambda v:v.__setitem__('units','rad')),
            ('context',lambda v:v.__setitem__('context_sha256','0'*64)),('output_injection',lambda v:v.__setitem__('expected_output',[0,0])),
            ('source_missing',lambda v:v.__setitem__('sources',[])),('source_wrong',lambda v:v['sources'][0].__setitem__('source_id','other')),
            ('stage_missing',lambda v:v['sources'][0]['stages_L1'].pop('source_Horner_L1')),
            ('stage_alias',lambda v:v['sources'][0]['stages_L1'].__setitem__('power',[0,1])),
            ('quota_bool',lambda v:v['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',[True,1])),
            ('quota_negative',lambda v:v['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',[-1,1])),
            ('quota_noncanonical',lambda v:v['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',[2,2])),
            ('quota_den0',lambda v:v['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',[1,0])),
            ('quota_none',lambda v:v['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',None)),
            ('quota_float',lambda v:v['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',1e-14)),
            ('stage_sum_exceeds_source',lambda v:v['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',[1,10**12])),
            ('group_missing',lambda v:v.__setitem__('groups',[])),
            ('reserve_missing',lambda v:v['groups'][0]['reserves_L1'].pop('reduction_L1')),
            ('reserve_power_units',lambda v:v['groups'][0]['reserves_L1'].__setitem__('power',[0,1])),
            ('group_wrong',lambda v:v['groups'][0].__setitem__('coherence_group','foreign')),
            ('reserve_overspend',lambda v:v['groups'][0]['reserves_L1'].__setitem__('reduction_L1',[1,10**12]))]
        for label,mut in mutations:
            q=copy.deepcopy(plan);mut(q)
            reject(label,lambda q=q:core.validate_plan(p,core.digest(p),q,model=core.MODEL))
        reject('packet_SHA',lambda:core.validate_plan(p,'0'*64,plan,model=core.MODEL))
        with patch.object(core,'load_retained',return_value=self.retained):
            reject('unknown_case',lambda:core.audit_stage_allocation_HOST(['foreign'],{},model=core.MODEL))
            reject('unused_plan',lambda:core.audit_stage_allocation_HOST(['thin_resolved'],{'two_sources':plan},model=core.MODEL))
            reject('duplicate_case',lambda:core.audit_stage_allocation_HOST(['thin_resolved']*2,{},model=core.MODEL))
        bad=copy.deepcopy(self.plans);bad['thin_resolved']['context_sha256']='0'*64
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core,'compare_source',side_effect=AssertionError('no output comparison before ALL plans valid')) as compare:
            reject('atomic_second_plan',lambda:core.audit_stage_allocation_HOST(['nonexact_geometry_phase_PASS','thin_resolved'],{k:bad[k] for k in ('nonexact_geometry_phase_PASS','thin_resolved')},model=core.MODEL))
            self.assertEqual(compare.call_count,0)
        DATA['atomic_comparison_calls']=0
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(StageTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
