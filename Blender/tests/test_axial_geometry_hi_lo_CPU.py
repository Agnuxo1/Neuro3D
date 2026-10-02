"""Own bounded tests for opt-in CPU geometry transport, no previous scientific producers."""
import copy,json,math,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_geometry_hi_lo_CPU_v1 as core
DATA={}
class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.retained=core.load_retained();cls.packets,cls.old,cls.pins=cls.retained
    def test_a_geometry_points(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'audit_ORIGINAL_source_CPU',side_effect=AssertionError('old producer forbidden')),patch.object(core.prior,'encode_source',side_effect=AssertionError('SOURCE forbidden')),patch.object(core.prior.unit,'execute_unit',side_effect=AssertionError('Horner forbidden')):
            a=core.audit_geometry_CPU(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a;self.assertEqual(core.digest(self.retained),before)
        self.assertEqual((a['decoded_geometry_sources_executed'],a['retained_sources_not_executed'],a['inherited_pins_verified']),(2,17,333))
        self.assertEqual((a['coordinate_scalars_encoded'],a['new_RN32_casts'],a['new_RN64_subtractions'],a['new_RN64_decode_adds']),(76,152,76,76))
        found=[]
        for name,c in a['cases'].items():
            for r in c['sources']:
                self.assertEqual(r['status'],'STOP')
                for k in core.FALSE:self.assertFalse(r[k])
                if r[core.FLAG]:
                    found.append(name);self.assertEqual(r['encoder']['transport_bytes'],304)
                    self.assertTrue(r['composition']['point_charge_fits_unchanged_cap'])
                    self.assertGreater(F(*r['composition']['point_argument_to_fixed_ORIGINAL_phase_bound_rad']),0)
        self.assertEqual(set(found),{'thin_resolved','nonexact_geometry_phase_PASS'})
        self.assertEqual(a['cases']['thin_resolved']['sources'][0]['composition']['first_root_BU'],[1,2**30])
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
    def test_b_scalar_controls(self):
        controls=[core.scalar(x) for x in (-0.0,0.0,0.1,-0.25)]
        DATA['scalar_controls']=controls
        self.assertEqual(controls[0]['high_uint32'],0x80000000)
        self.assertEqual(controls[0]['residual_uint64'],0)
        self.assertEqual(controls[2]['decoded_coordinate_error_abs'],[1,2**55])
        self.assertEqual(controls[3]['decoded_coordinate_error_abs'],[0,1])
    def test_c_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        for label,x in [('bool',True),('nan',float('nan')),('infinity',float('inf')),('subnormal64',math.ldexp(1.0,-1074)),('overflow32',1e40),('subnormal_hi32',1e-40),('subnormal_lo32',math.ldexp(1.0,-120)+math.ldexp(1.0,-146))]:
            reject(label,lambda x=x:core.scalar(x))
        name='thin_resolved';snap,_=core.original.snapshot_from_packet(self.packets[name],self.old['cases'][name]['context'])
        row=DATA['audit']['cases'][name]['sources'][0];enc=row['encoder']
        for label,mut in [('transport_SHA',lambda e:e.__setitem__('transport_le_sha256','0'*64)),('transport_bytes',lambda e:e.__setitem__('transport_le_base64','AAAA')),('path_missing',lambda e:e['records'].pop()),('path_duplicate',lambda e:e['records'][1].__setitem__('path',e['records'][0]['path'])),('snapshot_digest',lambda e:e.__setitem__('original_snapshot_digest','0'*64)),('coordinate_charge',lambda e:e['records'][0].__setitem__('decoded_coordinate_error_abs',[0,1])),('limb_bool',lambda e:e['records'][0].__setitem__('high_uint32',True))]:
            e=copy.deepcopy(enc);mut(e);reject(label,lambda e=e:core.decode_geometry(snap,0,e))
        for label,mut in [('contact',lambda s:[v.__setitem__(0,s['sources'][0]['position_BU'][0]) for v in s['objects']['M']['vertices_world_BU']]),('boundary',lambda s:s['sources'][0]['position_BU'].__setitem__(1,0.0)),('tie',lambda s:s['objects']['M']['faces'].append(s['objects']['M']['faces'][1])),('nonpositive_wave',lambda s:s.__setitem__('lambda_BU',0.0))]:
            s=copy.deepcopy(snap);mut(s);reject(label,lambda s=s:core.original.trace_original(s,0))
        original=self.old['cases'][name]['sources'][0]['trace']
        reject('cap_inflation',lambda:core.compose(original,row['decoded_trace'],row['decoded_argument'],1,[1,1]))
        t=copy.deepcopy(row['decoded_trace']);t['quarter_index']+=1
        reject('quarter_changed',lambda:core.compose(original,t,row['decoded_argument'],1,[1,10**12]))
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,ns,m in [('model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda ns=ns,m=m:core.audit_geometry_CPU(ns,model=m))
            with patch.object(core.prior,'runtime_probe',return_value={'PASS':False}),patch.object(core,'encode_geometry',side_effect=AssertionError('guard before encoder')):
                reject('guard_FAIL',lambda:core.audit_geometry_CPU(['thin_resolved'],model=core.MODEL))
        old=copy.deepcopy(self.old);old['cases'][name]['context']['input_packet_sha256']='0'*64
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.pins)):
            reject('stale_INPUT',lambda:core.audit_geometry_CPU([name],model=core.MODEL))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_d_decoded_snapshot_binding(self):
        name='thin_resolved';snapshot,_=core.original.snapshot_from_packet(self.packets[name],self.old['cases'][name]['context'])
        row=DATA['audit']['cases'][name]['sources'][0];decoded=core.decode_geometry(snapshot,0,row['encoder'])
        self.assertEqual(core.digest(decoded),row['decoded_snapshot_digest'])
        self.assertEqual(snapshot['objects']['M']['faces'],decoded['objects']['M']['faces'])
        self.assertEqual(snapshot['sources'][0]['field_reim'],decoded['sources'][0]['field_reim'])
        self.assertEqual(F(*row['composition']['observed_effective_delta_BU']),F(1,2**55))
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(GeometryTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
