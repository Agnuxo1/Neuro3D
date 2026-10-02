"""New exact mirror-zero tests; only pinned retained products, no producers."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import json,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_mirror_zero_HOST_v1 as core
import axial_source_budget_gate_HOST_v1 as retained
import axial_amplitude_allocation_HOST_v1 as allocation
DATA={}
class MirrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.products,_=retained.load_retained()
        cls.names=list(cls.packets)
        prev=retained.payload(allocation.parse(retained.read(retained.PREVIOUS,retained.PREVIOUS_SHA)))
        cls.plans=prev['plans'];cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        DATA['missing']=core.audit_retained_mirror_zero_HOST(cls.names,dict.fromkeys(cls.names),model=core.MODEL)
        DATA['controls']={}
        for label,name in [('positive','positive'),('two_sources','two_sources'),('explicit_zero_caps','positive')]:
            DATA['controls'][label]=core.audit_retained_mirror_zero_HOST([name],{name:cls.plans[label]},model=core.MODEL)
        e=retained.payload(allocation.parse(retained.read(core.EVENTS,retained.pins_from(allocation.parse(retained.read(core.PREVIOUS,core.PREVIOUS_SHA)))[core.EVENTS])))
        cls.event=e['cases']['positive']['sources'][0]
        cls.meta=allocation.parse(base64.b64decode(cls.packets['positive']['buffers_base64']['input_metadata_json']))
        cls.snap=allocation.parse(base64.b64decode(cls.packets['positive']['buffers_base64']['original_scene_json']))
        DATA['primitive_controls']=[];DATA['profile_controls']=[];DATA['rejections']=[]
    def test_17_cases_same_STOP_and_five_original_mirror0_sources(self):
        rows=[s for v in DATA['missing']['cases'].values() for s in v['sources']]
        self.assertEqual(len(rows),19)
        self.assertEqual(sum(s['reflection_coefficient_applied_HOST'] for s in rows),5)
        self.assertEqual(DATA['missing']['HOST_corner_reflections'],20)
        self.assertEqual(DATA['missing']['HOST_signbit_XORs'],40)
        for n,v in DATA['missing']['cases'].items():
            for s,p in zip(v['sources'],self.products[n]['sources']):
                self.assertEqual(s['status'],'STOP');self.assertFalse(s[core.FLAG])
                if not p['source_product_evaluated']:
                    self.assertEqual(s['reason'],p['reason'])
                    self.assertFalse(s['reflection_coefficient_applied_HOST'])
                    self.assertNotIn('reflected_corner_products_HOST',s)
                else:
                    self.assertEqual(s['reflected_source_error_L1_to_ORIGINAL_bound'],p['product_error_L1_to_ORIGINAL_bound'])
                    self.assertIn('no default split/zero',s['reason'])
    def test_exact_negation_preserves_L1_charges_caps_reference(self):
        for result in [DATA['missing'],*DATA['controls'].values()]:
            for name,v in result['cases'].items():
                for s,old in zip(v['sources'],self.products[name]['sources']):
                    if not s['reflection_coefficient_applied_HOST']:continue
                    self.assertEqual(s['phase_reference_id'],old['phase_reference_id'])
                    self.assertEqual(s['terminal_reference_id'],old['terminal_reference_id'])
                    self.assertEqual(s['coefficient_error_L1'],[0,1])
                    for a,p in zip(s['reflected_corner_products_HOST'],old['encoded_corner_products']):
                        self.assertEqual(a['reflected_uint64'],[w^(1<<63) for w in p['product_uint64']])
                        self.assertEqual(a['reflected_rational'],[[ -r[0],r[1]] for r in p['product_rational']])
                        self.assertEqual(a['charges_L1_unchanged'],p['charges_L1'])
                        self.assertEqual(a['error_L1_to_ORIGINAL_reflected_source_ideal_unit_bound'],p['error_L1_to_original_source_times_ideal_unit_bound'])
    def test_budget_missing_zero_FAIL_other_STOP_never_promote(self):
        p=DATA['controls']['positive']['cases']['positive'];self.assertTrue(p[core.FLAG])
        z=DATA['controls']['explicit_zero_caps']['cases']['positive']
        self.assertFalse(z[core.FLAG]);self.assertEqual(z['sources'][0]['status'],'FAIL')
        self.assertEqual(z['sources'][0]['source_cap_L1'],[0,1])
        t=DATA['controls']['two_sources']['cases']['two_sources']
        self.assertFalse(t[core.FLAG]);self.assertTrue(t['sources'][0][core.FLAG])
        self.assertEqual(t['sources'][1]['reason'],self.products['two_sources']['sources'][1]['reason'])
        for r in [DATA['missing'],*DATA['controls'].values()]:
            self.assertEqual(r['inherited_pins_verified'],218)
            self.assertEqual(r['new_products'],0);self.assertEqual(r['new_RN64_operations'],0)
            for k in core.FALSE:
                self.assertIs(r[k],False)
                for v in r['cases'].values():
                    self.assertIs(v[k],False)
                    for s in v['sources']:self.assertIs(s[k],False)
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
    def test_word_primitive_signed_zeros_subnormals_extremes_finite(self):
        for words in [[0,1<<63],[1,(1<<63)|1],[(2046<<52)|((1<<52)-1),1<<52],
                      [0x3ff0000000000000,0xbff0000000000000],[0x3fb999999999999a,0],[(1<<63)|1,0]]:
            v=core.negate_product_words(words,model=core.MODEL);DATA['primitive_controls'].append(v)
            self.assertEqual(v['reflected_uint64'],[w^(1<<63) for w in words])
            self.assertEqual([core.decode64(w) for w in v['reflected_uint64']],[-core.decode64(w) for w in words])
        for words in [[True,0],[0x7ff0000000000000,0],[0x7ff0000000000001,0],[-1,0],[1<<64,0],[0]]:
            with self.assertRaises(ValueError):core.negate_product_words(words,model=core.MODEL)
            DATA['rejections'].append({'kind':'primitive','words':words,'model':core.MODEL})
    def test_ORIGINAL_nonzero_underflow_not_zero_and_event_owner_departure(self):
        for phase in [0.0,-0.0]:
            s=deepcopy(self.snap);s['objects']['M']['phase_rad']=phase
            v=core.mirror_zero_profile(s,self.meta,self.event)
            DATA['profile_controls'].append({'snapshot':s,'metadata':self.meta,'event':self.event,'profile':v})
            self.assertEqual(v['mirror_phase_ORIGINAL_uint64'],struct.unpack('<Q',struct.pack('<d',phase))[0])
        # NEW input-only negative controls. Small ORIGINAL phase would round float32 to zero.
        for label,phase in [('tiny_nonzero',2.0**-200),('least_binary64_subnormal',2.0**-1074),('general_phase',0.1),('missing_phase',None),('bool_phase',False)]:
            s=deepcopy(self.snap);s['objects']['M']['phase_rad']=phase
            with self.assertRaises(ValueError):core.mirror_zero_profile(s,self.meta,self.event)
            DATA['rejections'].append({'kind':'profile','label':label,'snapshot':s,'metadata':self.meta,'event':self.event})
        for label,key,value in [('wrong_first_owner','mirror_owner',1),('absent_event_admission','accepted_axial_two_event_geometry_CPU_only',False),('wrong_terminal','terminal_owner',0)]:
            e=deepcopy(self.event);e[key]=value
            with self.assertRaises(ValueError):core.mirror_zero_profile(self.snap,self.meta,e)
            DATA['rejections'].append({'kind':'profile','label':label,'snapshot':self.snap,'metadata':self.meta,'event':e})
        e=deepcopy(self.event);e['departure_certificate']['source_id']='other'
        with self.assertRaises(ValueError):core.mirror_zero_profile(self.snap,self.meta,e)
        DATA['rejections'].append({'kind':'profile','label':'departure_source_swap','snapshot':self.snap,'metadata':self.meta,'event':e})
    def test_public_cannot_inject_coeff_or_event_or_foreign_context(self):
        for label,plans,model in [('foreign_model',{'positive':self.plans['positive']},'foreign'),
                                  ('output_coefficient',{'positive':{**self.plans['positive'],'coefficient':[-1,0]}},core.MODEL),
                                  ('output_event',{'positive':{**self.plans['positive'],'event':self.event}},core.MODEL),
                                  ('foreign_group_context',{'positive':self.plans['synthetic_two_groups']},core.MODEL)]:
            with self.assertRaises(ValueError):core.audit_retained_mirror_zero_HOST(['positive'],plans,model=model)
            DATA['rejections'].append({'kind':'public','label':label,'names':['positive'],'plans':plans,'model':model})
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MirrorTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
