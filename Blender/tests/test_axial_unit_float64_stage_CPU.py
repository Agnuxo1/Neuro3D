"""Own bounded CPU stage tests; previous scientific producers never replayed."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_unit_float64_stage_CPU_v1 as core
DATA={}
class UnitStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained()
        cls.packets,cls.old,cls.uniform,cls.units,cls.previous,cls.pins=cls.retained
        cls.n='thin_resolved';cls.ctx=cls.old['cases'][cls.n]['context']
        cls.cert=cls.old['cases'][cls.n]['sources'][0]
        cls.u=cls.uniform['cases'][cls.n]['sources'][0];cls.q=cls.units[cls.n]['sources'][0]
        cls.profile=cls.uniform['coefficient_profile']
    def test_complete_partial_execution(self):
        with patch.object(core,'load_retained',return_value=self.retained):
            a=core.audit_unit_float64_stage_CPU(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a
        self.assertEqual((a['executed_source_fixture_sets'],a['retained_sources_not_executed'],a['new_CPU_float64_RN_nodes_executed']),(2,17,208))
        self.assertEqual(a['point_graphs_bits_MATCH']+a['point_graphs_bits_FAIL'],8)
        self.assertEqual(a['inherited_pins_verified'],313)
        self.assertTrue(a['previous_SOURCE_eight_bit_FAILs_preserved'])
        self.assertFalse(a['backend_domain_admitted']);self.assertEqual(a['new_scene_selector_argument_encoder_executions'],0)
        found=[]
        for name,c in a['cases'].items():
            for s in c['sources']:
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
                if s[core.FLAG]:
                    found.append(name)
                    for point in s['points']:
                        self.assertEqual(len(point['nodes']),26)
                        self.assertEqual(point['node_word_mismatches'],[n['label'] for n in point['nodes'] if not n['word_match']])
                        self.assertFalse(point['zero_canonicalization_performed'])
        self.assertEqual(set(found),{'thin_resolved','nonexact_geometry_phase_PASS'})
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
    def test_binding_readonly_no_execution(self):
        before=core.digest((self.packets[self.n],self.ctx,self.cert,self.u,self.q,self.profile))
        with patch.object(core,'execute_horner',side_effect=AssertionError('no execution in binding')):
            points=core.bind_fixture(self.packets[self.n],self.ctx,0,self.cert,self.u,self.q,self.profile)
        self.assertEqual(len(points),4)
        self.assertEqual(before,core.digest((self.packets[self.n],self.ctx,self.cert,self.u,self.q,self.profile)))
    def test_mutations_rejected(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        mutations=[
          ('stale_INPUT',lambda x:x[0].__setitem__('input_packet_sha256','0'*64)),
          ('source_ID',lambda x:x[3].__setitem__('source_id','other')),
          ('source_certificate_absent',lambda x:x[1].__setitem__(core.UNIT_FLAG,False)),
          ('promotion',lambda x:x[1]['proof'].__setitem__('native_kernel_implemented',True)),
          ('assignment_gauge_SHA',lambda x:x[1]['proof'].__setitem__('ORIGINAL_assignment_sha256','0'*64)),
          ('uniform_row_SHA',lambda x:x[1]['proof'].__setitem__('retained_uniform_unit_row_sha256','0'*64)),
          ('quarter_row_SHA',lambda x:x[2].__setitem__('retained_unit_source_sha256','0'*64)),
          ('coefficient_profile_SHA',lambda x:x[1]['proof'].__setitem__('coefficient_profile_sha256','0'*64)),
          ('source_gauge',lambda x:x[3].__setitem__('phase_reference_id','other')),
          ('terminal_gauge',lambda x:x[3].__setitem__('terminal_reference_id','other')),
          ('phase_cap',lambda x:x[3].__setitem__('unchanged_original_phase_cap_rad',[1,1])),
          ('witness_removed',lambda x:x[3]['encoded_corner_units_HOST'].pop()),
          ('quarter_bool',lambda x:x[3]['encoded_corner_units_HOST'][0]['quarter_argument'].__setitem__('quadrant_mod4',True)),
          ('angle_substitution',lambda x:x[3]['encoded_corner_units_HOST'][0]['rotation_RN64'].__setitem__('angle_uint64',0)),
          ('coefficient_changed',lambda x:x[4]['cos'][0].__setitem__('uint64',0))]
        for label,mut in mutations:
            x=copy.deepcopy([self.ctx,self.cert,self.u,self.q,self.profile]);mut(x)
            reject(label,lambda x=x:core.bind_fixture(self.packets[self.n],x[0],0,x[1],x[2],x[3],x[4]))
        corner=self.q['encoded_corner_units_HOST'][0]
        for label,mut in [
          ('FMA_graph',lambda c:c['rotation_RN64']['operations'][1].__setitem__('op','fma')),
          ('node_order',lambda c:c['rotation_RN64']['operations'][1].__setitem__('label','other')),
          ('operand_substitution',lambda c:c['rotation_RN64']['operations'][0].__setitem__('inputs_rational',[[0,1],[0,1]])),
          ('nonfinite_angle',lambda c:c['rotation_RN64'].__setitem__('angle_uint64',0x7ff0000000000000)),
          ('angle_outside',lambda c:c['rotation_RN64'].__setitem__('angle_uint64',0x4000000000000000)),
          ('bool_quarter',lambda c:c['quarter_argument'].__setitem__('quadrant_mod4',True))]:
            c=copy.deepcopy(corner);mut(c);reject(label,lambda c=c:core.execute_horner(c))
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,n,m in [('wrong_model',[self.n],'wrong'),('empty',[],core.MODEL),('duplicate',[self.n,self.n],core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda n=n,m=m:core.audit_unit_float64_stage_CPU(n,model=m))
            with patch.object(core.source,'runtime_probe',return_value={'PASS':False}),patch.object(core,'execute_horner',side_effect=AssertionError('guard must prevent execution')):
                reject('runtime_probe_FAIL',lambda:core.audit_unit_float64_stage_CPU([self.n],model=core.MODEL))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_reference_mismatch_FAIL_not_repaired(self):
        corner=copy.deepcopy(self.q['encoded_corner_units_HOST'][0])
        corner['rotation_RN64']['operations'][-1]['output_uint64']^=1
        actual=core.execute_horner(corner)
        self.assertEqual(actual['status'],'FAIL_RETAINED_NODE_BITS')
        self.assertEqual(actual['node_word_mismatches'],['sin.final'])
        self.assertTrue(actual['retained_final_unit_bits_match'])
        DATA['last_node_mutation']={'corner':corner,'actual':actual,'scope':'synthetic tampered reference control only, not backend/scene admission'}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(UnitStageTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
