"""New bounded scene-domain/mirror isometry tests, without RN or old producer replay."""
import base64,copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_reflected_source_domain_HOST_v1 as core
DATA={}
class ReflectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.old,cls.mirror,cls.events,cls.zero,cls.domains,cls.pins=core.load_retained()
        cls.n='positive';cls.ctx=cls.old['cases'][cls.n]['context']
        cls.s=cls.old['cases'][cls.n]['sources'][0];cls.m=cls.mirror[cls.n]['sources'][0]
        cls.e=cls.events[cls.n]['sources'][0];cls.z=cls.zero['cases'][cls.n]['sources'][0];cls.d=cls.domains['cases'][cls.n]['sources'][0]
        cls.snap=core.allocation.parse(base64.b64decode(cls.packets[cls.n]['buffers_base64']['original_scene_json'],validate=True))
        cls.meta=core.allocation.parse(base64.b64decode(cls.packets[cls.n]['buffers_base64']['input_metadata_json'],validate=True))
    def test_audit(self):
        a=core.audit_reflected_source_domain_HOST(self.old['case_order'],model=core.MODEL);DATA['audit']=a
        self.assertEqual((a['restricted_ideal_reflected_source_domains_proved'],a['retained_unit_STOPs'],a['nonzero_domains_not_refined']),(3,14,2))
        self.assertEqual(a['inherited_pins_verified'],278)
        xors=0
        for c in a['cases'].values():
            for s in c['sources']:
                for k in core.FALSE:self.assertIs(s[k],False)
                self.assertEqual(s['status'],'STOP')
                if 'proof' in s:
                    p=s['proof'];self.assertEqual(p['uniform_ideal_reflected_source_L1_error_to_fixed_ORIGINAL_bound'],[1,2**55])
                    self.assertTrue(p['nonzero_encoding_error_preserved']);self.assertTrue(p['missing_source_allocation_NOT_promoted'])
                    self.assertEqual(p['retained_mirror_source_status'],'STOP')
                    self.assertIn('missing explicit',p['retained_mirror_source_reason'])
                    xors+=sum(v['retained_sign_XOR_identities_checked'] for v in p['retained_corner_identities'])
                    for v in p['retained_corner_identities']:self.assertEqual(v['reflected_uint64'][1],core.SIGN)
        self.assertEqual(xors,24)
    def test_phase_profiles(self):
        DATA['SYNTHETIC_fixed_phase_controls']=[]
        for phase in (0.0,-0.0):
            snap=copy.deepcopy(self.snap);snap['objects']['M']['phase_rad']=phase
            p=core.fixed_ideal_profile(snap,self.meta,self.e,self.d)
            self.assertEqual(p['ideal_coefficient_exact_reim'],[[-1,1],[0,1]])
            DATA['SYNTHETIC_fixed_phase_controls'].append(p)
        self.assertEqual(DATA['SYNTHETIC_fixed_phase_controls'][1]['fixed_ORIGINAL_mirror_phase_uint64'],core.SIGN)
    def test_reflected_word_identity(self):
        v=core.reflected_identity(self.m['reflected_corner_products_HOST'][0],self.s['proof']['graph_checks'][0])
        DATA['single_retained_identity']=v
        self.assertEqual(v['uniform_reflected_source_error_L1'],[1,2**55])
        self.assertEqual(v['additional_rounding_error_L1'],[0,1])
    def test_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        for label,n,m in [('model',['positive'],'wrong'),('empty',[],core.MODEL),('duplicate',['positive','positive'],core.MODEL),
                          ('boolcase',[True],core.MODEL),('tuple',('positive',),core.MODEL),('unknown',['other'],core.MODEL)]:
            reject(label,lambda n=n,m=m:core.audit_reflected_source_domain_HOST(n,model=m))
        for label,phase in [('phase_int',0),('phase_bool',False),('phase_tiny',1e-300),('phase_subnormal',1e-320),
                            ('phase_nonzero',0.5),('phase_inf',float('inf')),('phase_nan',float('nan'))]:
            snap=copy.deepcopy(self.snap);snap['objects']['M']['phase_rad']=phase
            reject(label,lambda snap=snap:core.fixed_ideal_profile(snap,self.meta,self.e,self.d))
        for label,mut in [
            ('event_acceptance',lambda e:e.__setitem__('accepted_axial_two_event_geometry_CPU_only',False)),
            ('event_owner',lambda e:e.__setitem__('mirror_owner',1)),
            ('event_owner_bool',lambda e:e['segments'][1].__setitem__('owner',True)),
            ('event_primitive',lambda e:e['segments'][0].__setitem__('primitive_id',0)),
            ('event_missing_segment',lambda e:e['segments'].pop()),
            ('departure_caller',lambda e:e['departure_certificate'].__setitem__('origin','caller')),
            ('departure_source',lambda e:e['departure_certificate'].__setitem__('source_id','other'))]:
            e=copy.deepcopy(self.e);mut(e);reject(label,lambda e=e:core.fixed_ideal_profile(self.snap,self.meta,e,self.d))
        for label,mut in [
            ('domain_absent',lambda d:d.__setitem__('restricted_coordinate_box_to_parameter_rectangle_proved',False)),
            ('uniform_selector_absent',lambda d:d['restricted_domain_proof']['uniform_affine_selector_proof'].__setitem__('restricted_shared_plane_selector_proved',False)),
            ('uniform_clearance_absent',lambda d:d['restricted_domain_proof']['uniform_affine_selector_proof'].__setitem__('mirror_first_uniform_clearance',False)),
            ('departure_earlyskip',lambda d:d['restricted_domain_proof']['uniform_affine_selector_proof'].__setitem__('skip_previous_owner_permitted_only_after_first_root',False)),
            ('projection_changed',lambda d:d['restricted_domain_proof']['fixed_YZ_projection_checks'][1].__setitem__('primitive_id',0))]:
            d=copy.deepcopy(self.d);mut(d);reject(label,lambda d=d:core.fixed_ideal_profile(self.snap,self.meta,self.e,d))
        corner=self.m['reflected_corner_products_HOST'][0];g=self.s['proof']['graph_checks'][0]
        for label,mut in [
            ('reflected_sign',lambda c:c['reflected_uint64'].__setitem__(0,c['input_uint64'][0])),
            ('reflected_zero_sign',lambda c:c['reflected_uint64'].__setitem__(1,0)),
            ('reflected_bool',lambda c:c['reflected_uint64'].__setitem__(1,False)),
            ('original_gauge_ref',lambda c:c.__setitem__('reflected_rational',c['input_rational'])),
            ('hidden_error',lambda c:c.__setitem__('error_L1_to_ORIGINAL_reflected_source_ideal_unit_bound',[0,1])),
            ('hidden_charge',lambda c:c['charges_L1_unchanged'].__setitem__('source_encoding',[0,1])),
            ('new_RN',lambda c:c.__setitem__('new_RN64_operations',1)),
            ('RN_bool',lambda c:c.__setitem__('new_RN64_operations',False)),
            ('product_SHA',lambda c:c.__setitem__('retained_corner_product_sha256','0'*64))]:
            c=copy.deepcopy(corner);mut(c);reject(label,lambda c=c:core.reflected_identity(c,g))
        for label,mut in [
            ('mirror_event_SHA',lambda m:m.__setitem__('retained_event_row_sha256','0'*64)),
            ('mirror_product_SHA',lambda m:m.__setitem__('retained_product_row_sha256','0'*64)),
            ('mirror_phase_receipt',lambda m:m['mirror_profile'].__setitem__('mirror_phase_ORIGINAL_uint64',core.SIGN)),
            ('mirror_gauge',lambda m:m.__setitem__('terminal_reference_id','other')),
            ('mirror_missing_corner',lambda m:m['reflected_corner_products_HOST'].pop()),
            ('mirror_nonzero_coefferror',lambda m:m.__setitem__('coefficient_error_L1',[1,2]))]:
            m=copy.deepcopy(self.m);mut(m)
            reject(label,lambda m=m:core.reflected_domain_proof(self.packets[self.n],self.ctx,0,self.s,m,self.e,self.z,self.d))
        target=core.io.ROOT/core.PREVIOUS;read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',lambda:core.load_retained())
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReflectionTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
