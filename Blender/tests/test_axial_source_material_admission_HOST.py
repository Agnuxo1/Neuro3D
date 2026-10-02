"""CPU1-thread HOST preflight controls. No previous producer suite replay."""
import copy,json,struct,sys,unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_source_material_admission_HOST_v1 as core
DATA={}
class MaterialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=core.load_retained();cls.retained=cls.loaded[0];cls.names=list(cls.retained[0])
        name='thin_resolved';r=cls.retained;cls.snapshot,cls.metadata=core.original.snapshot_from_packet(r[0][name],r[1]['cases'][name]['context'])
        rr=r[5]['cases'][name]['sources'][0]['result']
        cls.fixed=rr['fixed_ORIGINAL_reference'];cls.decoded=rr['new_decoded_Xroot_result']['fixed_ORIGINAL_reference']
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected STOP: '+label)
    def test_a_current_source(self):
        before=core.digest(self.loaded)
        with ExitStack() as stack:
            stack.enter_context(patch.object(core,'load_retained',return_value=self.loaded))
            for mod,key in ((core.bridge.prior,'execute'),(core.bridge.prior,'native_cast32'),
                            (core.bridge.prior,'native_add'),(core.bridge.prior.prior,'execute'),
                            (core.original,'trace_original')):
                stack.enter_context(patch.object(mod,key,side_effect=AssertionError('no old producer/native/retrace execution')))
            audit=core.audit_material_admission_HOST(self.names,model=core.MODEL)
        self.assertEqual(core.digest(self.loaded),before)
        self.assertEqual((audit['source_material_profiles_admitted_HOST_only'],audit['retained_sources_STOP']),(2,17))
        self.assertEqual(len(audit['cases']),17)
        self.assertTrue(all(v['status']=='STOP' and all(v[n] is False for n in core.FALSE) for v in audit['cases'].values()))
        for c in audit['cases'].values():
            for row in c['sources']:
                self.assertTrue(all(row[n] is False for n in core.FALSE))
                self.assertIs(row['material_executed'],False)
                self.assertIsNone(row['executed_material_charge_L1']);self.assertIsNone(row['executed_material_quota_fits'])
        DATA['audit']=audit
    def test_b_phase_owner_guards(self):
        controls=[]
        for w in (0,core.SIGN):
            s=copy.deepcopy(self.snapshot);s['objects']['M']['phase_rad']=struct.unpack('<d',struct.pack('<Q',w))[0]
            profile=core.material_profile(s,self.metadata,'s',self.fixed,self.decoded)
            self.assertEqual(profile['mirror_phase_ORIGINAL_uint64'],w);controls.append(profile)
        DATA['signed_zero_profile_controls']=controls
        rejects=[]
        for label,w in [('smallest_positive_subnormal',1),('negative_subnormal',core.SIGN|1),
                        ('smallest_normal',1<<52),('positive_nonzero',0x3ff0000000000000),
                        ('negative_nonzero',0xbff0000000000000),('positive_inf',0x7ff0000000000000),
                        ('nan',0x7ff8000000000000)]:
            s=copy.deepcopy(self.snapshot);s['objects']['M']['phase_rad']=struct.unpack('<d',struct.pack('<Q',w))[0]
            self.reject(label,lambda s=s:core.material_profile(s,self.metadata,'s',self.fixed,self.decoded),rejects)
        mutations=[
            ('phase_bool',lambda s,m,f,d:s['objects']['M'].__setitem__('phase_rad',False)),
            ('owner_map_reordered',lambda s,m,f,d:m.__setitem__('object_ids',['D','M'])),
            ('kind_wrong',lambda s,m,f,d:s['objects']['M'].__setitem__('kind','det')),
            ('extra_mesh',lambda s,m,f,d:s.__setitem__('undeclared_meshes',['foreign'])),
            ('bool_face_index',lambda s,m,f,d:s['objects']['M']['faces'][0].__setitem__(0,False)),
            ('degenerate_topology',lambda s,m,f,d:s['objects']['M']['faces'][0].__setitem__(1,0)),
            ('foreign_source',lambda s,m,f,d:d.__setitem__('source_id','foreign')),
            ('bool_owner',lambda s,m,f,d:f['hits'][0].__setitem__('owner',False)),
            ('bool_primitive',lambda s,m,f,d:f['hits'][0].__setitem__('primitive_id',True)),
            ('primitive_outside_map',lambda s,m,f,d:f['hits'][0].__setitem__('primitive_id',99)),
            ('mirror_primitive_on_detector',lambda s,m,f,d:f['hits'][0].__setitem__('primitive_id',2)),
            ('chain_mismatch',lambda s,m,f,d:d['hits'][0].__setitem__('primitive_id',1-d['hits'][0]['primitive_id'])),
            ('zero_segment',lambda s,m,f,d:d['hits'][0].__setitem__('segment_BU',[0,1])),
            ('negative_segment',lambda s,m,f,d:d['hits'][0].__setitem__('segment_BU',[-1,1])),
            ('bool_segment',lambda s,m,f,d:d['hits'][0].__setitem__('segment_BU',[True,1])),
        ]
        for label,fn in mutations:
            s,m,f,d=map(copy.deepcopy,(self.snapshot,self.metadata,self.fixed,self.decoded));fn(s,m,f,d)
            self.reject(label,lambda:core.material_profile(s,m,'s',f,d),rejects)
        self.assertEqual(len(rejects),22);DATA['profile_rejections']=rejects
    def test_c_atomic_preflight(self):
        names=['nonexact_geometry_phase_PASS','thin_resolved'];rejects=[]
        def source(r):return r[1]['cases']['thin_resolved']['sources'][0]
        def root(r):return r[5]['cases']['thin_resolved']['sources'][0]['result']
        changes=[
            ('second_context',lambda r:r[2]['cases']['thin_resolved']['context'].__setitem__('scene_binding_sha256','0'*64)),
            ('integer_eligibility',lambda r:source(r).__setitem__(core.bridge.prior.FLAG,1)),
            ('source_promotion',lambda r:source(r).__setitem__(core.FALSE[0],True)),
            ('second_foreign_root_source',lambda r:root(r)['fixed_ORIGINAL_reference'].__setitem__('source_id','foreign')),
            ('second_primitive_owner',lambda r:root(r)['new_decoded_Xroot_result']['fixed_ORIGINAL_reference']['hits'][0].__setitem__('primitive_id',2)),
            ('second_zero_segment',lambda r:root(r)['fixed_ORIGINAL_reference']['hits'][0].__setitem__('segment_BU',[0,1])),
        ]
        with patch.object(core,'admit_current_source',side_effect=AssertionError('ALL profiles before any proof')) as adm:
            for label,fn in changes:
                r=copy.deepcopy(self.retained);fn(r)
                with patch.object(core,'load_retained',return_value=(r,self.loaded[1])):
                    self.reject(label,lambda:core.audit_material_admission_HOST(names,model=core.MODEL),rejects)
            self.assertEqual(adm.call_count,0)
        for label,n,m in [('wrong_model',names,'foreign'),('empty',[],core.MODEL),('duplicates',names*2,core.MODEL),('foreign_case',['foreign'],core.MODEL)]:
            with patch.object(core,'load_retained',return_value=self.loaded):
                self.reject(label,lambda n=n,m=m:core.audit_material_admission_HOST(n,model=m),rejects)
        with patch.object(core,'PREVIOUS_SHA','0'*64):
            self.reject('parent_SHA',core.load_retained,rejects)
        # No partial admissions are returned after a later proof fails.
        r=copy.deepcopy(self.retained);row=source(r);row['result']['product_uint64'][0]+=1
        with patch.object(core,'load_retained',return_value=(r,self.loaded[1])):
            self.reject('second_current_source_word',lambda:core.audit_material_admission_HOST(names,model=core.MODEL),rejects)
        DATA['atomic_rejections']={'rows':rejects,'profile_guard_before_proof_calls':0}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(MaterialTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)
