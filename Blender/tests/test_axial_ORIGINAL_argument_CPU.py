"""Bounded own ORIGINAL reference tests; no old selector/Horner/source writer replay."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_ORIGINAL_argument_CPU_v1 as core
DATA={}
class OriginalArgumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained()
        cls.packets,cls.old,cls.domain,cls.pins=cls.retained
        cls.n='thin_resolved';cls.ctx=cls.old['cases'][cls.n]['context']
        cls.snapshot,cls.meta=core.snapshot_from_packet(cls.packets[cls.n],cls.ctx)
    def test_fresh_scene_reference_argument(self):
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'execute_horner',side_effect=AssertionError('no old Horner execution')),patch.object(core.prior.source,'execute_graph',side_effect=AssertionError('no SOURCE execution')):
            a=core.audit_ORIGINAL_argument_CPU(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a
        self.assertEqual((a['fresh_ORIGINAL_sources_executed'],a['retained_sources_not_executed'],a['inherited_pins_verified']),(2,17,318))
        self.assertEqual((a['new_CPU_float64_casts'],a['new_CPU_float64_multiplies']),(2,2))
        self.assertFalse(a['encoded_hi_lo_backend_executed']);self.assertFalse(a['uniform_backend_domain_admitted'])
        found=[]
        for name,c in a['cases'].items():
            for s in c['sources']:
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
                if s[core.FLAG]:
                    found.append(name);self.assertTrue(s['point_reference_argument_charge_fits_unchanged_cap'])
                    self.assertEqual([v['primitive_id'] for v in s['trace']['hits']],[1,3])
                    self.assertEqual(len(s['trace']['root_projection_records']),8)
                    self.assertEqual(s['trace']['geometry_reference_rounding_error_BU'],[0,1])
                    self.assertFalse(s['argument']['retained_argument_or_result_substitution'])
        self.assertEqual(set(found),{'nonexact_geometry_phase_PASS','thin_resolved'})
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
    def test_thin_original_root_not_collapsed(self):
        t=core.trace_original(self.snapshot,0);a=core.argument_from_trace(t)
        gap=F.from_float(self.snapshot['objects']['M']['vertices_world_BU'][0][0])-F.from_float(self.snapshot['sources'][0]['position_BU'][0])
        self.assertGreater(gap,0);self.assertEqual(F(*t['hits'][0]['segment_BU']),gap)
        DATA['thin_positive_root_control']={'trace':t,'argument':a,'exact_gap_BU':core.pair(gap),'scope':'exact ORIGINAL reference only, not encoded traversal admission'}
    def test_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        changes=[
          ('undeclared_mesh',lambda s:s['undeclared_meshes'].append('extra')),
          ('unknown_owner',lambda s:s['objects'].__setitem__('other',copy.deepcopy(s['objects']['M']))),
          ('off_axis',lambda s:s['sources'][0]['direction'].__setitem__(1,0.5)),
          ('wrong_owner_kind',lambda s:s['objects']['M'].__setitem__('kind','det')),
          ('plane_not_shared',lambda s:s['objects']['M']['vertices_world_BU'][0].__setitem__(0,0.2)),
          ('invalid_face',lambda s:s['objects']['M']['faces'][0].__setitem__(0,True)),
          ('degenerate',lambda s:s['objects']['M']['faces'].__setitem__(0,[0,1,3])),
          ('boundary',lambda s:s['sources'][0]['position_BU'].__setitem__(2,0.0)),
          ('source_contact',lambda s:s['sources'][0]['position_BU'].__setitem__(0,s['objects']['M']['vertices_world_BU'][0][0])),
          ('nearest_tie',lambda s:s['objects']['M']['faces'].append([0,2,3])),
          ('mirror_behind',lambda s:s['sources'][0]['position_BU'].__setitem__(0,0.2)),
          ('bad_ref_direction',lambda s:s['objects']['D']['mode_direction'].__setitem__(0,1.0)),
          ('zero_wave',lambda s:s.__setitem__('lambda_BU',0.0)),
          ('nonfinite_wave',lambda s:s.__setitem__('lambda_BU',float('inf'))),
          ('subnormal_wave',lambda s:s.__setitem__('lambda_BU',float.fromhex('0x1p-1074'))),
          ('mirror_phase',lambda s:s['objects']['M'].__setitem__('phase_rad',0.1))]
        # Degenerate control must use three distinct collinear projected vertices.
        changes[6]=('degenerate',lambda s:s['objects']['M']['vertices_world_BU'].__setitem__(1,copy.deepcopy(s['objects']['M']['vertices_world_BU'][0])))
        for label,mut in changes:
            s=copy.deepcopy(self.snapshot);mut(s);reject(label,lambda s=s:core.trace_original(s,0))
        reject('bool_index',lambda:core.trace_original(self.snapshot,True))
        reject('quarter_boundary',lambda:core.argument_from_trace({'residual_cycles':[1,8]}))
        packet=copy.deepcopy(self.packets[self.n]);packet['manifest']['buffers']['sources']['sha256']='0'*64
        reject('packet_buffer_SHA',lambda:core.snapshot_from_packet(packet,self.ctx))
        ctx=copy.deepcopy(self.ctx);ctx['input_packet_sha256']='0'*64
        reject('stale_INPUT',lambda:core.snapshot_from_packet(self.packets[self.n],ctx))
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,n,m in [('wrong_model',[self.n],'wrong'),('empty',[],core.MODEL),('duplicate',[self.n,self.n],core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda n=n,m=m:core.audit_ORIGINAL_argument_CPU(n,model=m))
            with patch.object(core.prior.source,'runtime_probe',return_value={'PASS':False}),patch.object(core,'trace_original',side_effect=AssertionError('guard')):
                reject('runtime_probe_FAIL',lambda:core.audit_ORIGINAL_argument_CPU([self.n],model=core.MODEL))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_snapshot_binding_readonly(self):
        before=core.digest((self.packets[self.n],self.ctx))
        core.snapshot_from_packet(self.packets[self.n],self.ctx)
        self.assertEqual(before,core.digest((self.packets[self.n],self.ctx)))
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(OriginalArgumentTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
