"""New HOST link tests: sealed evidence, independent conservation, atomic rejects."""
import base64,copy,hashlib,json,sys,unittest,zlib
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_tagged_SOURCE_UNIT_material_link_HOST_v1 as c
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=c.load_retained()
        with patch.object(c,'load_retained',return_value=cls.loaded):cls.request=c.make_request()
    def test_link(self):
        with patch.object(c,'load_retained',return_value=self.loaded):out=c.audit(copy.deepcopy(self.request),model=c.MODEL)
        self.assertEqual(out['links'],2);self.assertEqual(len(out['sources']),4)
        self.assertEqual(out['group_admissions'],0);self.assertTrue(all(v is False for v in out['proof_scope'].values()))
        for row in out['sources']:
            if row['ledger'] is None:continue
            l=row['ledger'];self.assertEqual(len(l['charges']),15)
            self.assertEqual(sum((F(*v) for v in l['charges'].values()),F(0)),F(*l['total']))
            self.assertEqual(l['charges']['ideal_material_L1'],[0,1])
            self.assertIsNone(row['phase_bound_rad']);self.assertFalse(row['new_product_or_material_executed'])
        DATA['request']=self.request;DATA['audit']=out
    def test_atomic_rejections(self):
        cases=[]
        def mutation(label,fn):
            r=copy.deepcopy(self.request);fn(r);cases.append((label,r))
        mutation('cap alias',lambda r:r.update(cap_rad=[1,1]))
        mutation('wrong model',lambda r:r.update(model='legacy'))
        mutation('wrong reference',lambda r:r.update(reference='A only'))
        mutation('wrong parent',lambda r:r.update(parent_sha256='0'*64))
        mutation('late source change',lambda r:r['A_POINT_OUTPUT']['sources'][-1].update(source_id='s'))
        mutation('signed zero operand',lambda r:r['A_POINT_OUTPUT']['sources'][0]['proof']['decoded_uint64'].__setitem__(1,1<<63))
        mutation('radius fit to output',lambda r:r['A_POINT_OUTPUT']['sources'][0]['proof'].update(point_error_L1_bound=[0,1]))
        mutation('bool equals int',lambda r:r['A_POINT_OUTPUT']['sources'][0]['proof']['decoded_uint64'].__setitem__(1,False))
        mutation('UNIT bitchange',lambda r:r['bare_OUTPUT']['cases']['thin_resolved']['sources'][0]['result']['unit_uint64'].__setitem__(0,0))
        mutation('material change',lambda r:r['material_OUTPUT']['cases']['thin_resolved']['sources'][0]['result']['reflected_uint64'].__setitem__(0,0))
        mutation('missing last source',lambda r:r['A_POINT_INPUT']['transport_INPUT']['decoder_INPUT']['SOURCE_limb_records'].pop())
        mutation('gauge change',lambda r:r['material_OUTPUT']['cases']['thin_resolved']['context']['assignments'][0].update(terminal_reference_id='alien'))
        results=[]
        for label,r in cases:
            with patch.object(c,'load_retained',return_value=self.loaded),patch.object(c,'emit_link',wraps=c.emit_link) as emit:
                with self.assertRaises(ValueError):c.audit(r,model=c.MODEL)
                self.assertEqual(emit.call_count,0);results.append({'control':label,'emissions':0,'rejected':True})
        DATA['rejections']=results
    def test_missing_optin(self):
        with patch.object(c,'load_retained',return_value=self.loaded):
            v=c.audit(None,model=c.MODEL)
            self.assertEqual((v['missing_cases'],v['missing_sources'],v['links']),(17,19,0))
            for m in (None,False,'legacy'):
                with self.assertRaises(ValueError):c.audit(self.request,model=m)
        DATA['missing']=v
    def test_rational_gate(self):
        invalid=[[-1,1],[2,2],[True,1],[0,0],[1,1<<4097],(0,1),[0,1,2]]
        for v in invalid:
            with self.assertRaises(ValueError):c.q(v)
        for w in (True,-1,1,0x7ff0000000000000,1<<64):
            with self.assertRaises(ValueError):c.value(w)
        self.assertEqual(c.value(1<<63),0);DATA['typed_rejections']=len(invalid)+5
if __name__=='__main__':
    s=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);r=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(s)
    print(json.dumps({'tests_run':r.testsRun,'errors':len(r.errors),'failures':len(r.failures),'data':DATA},sort_keys=True))
    sys.exit(not r.wasSuccessful())
