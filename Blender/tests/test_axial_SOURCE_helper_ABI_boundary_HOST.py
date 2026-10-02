"""Own static resolver and retained-probe tests; frozen code is data only."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'Blender/benchmarks/capacity_audit/axial_SOURCE_helper_ABI_boundary_HOST_v1.py'
s=importlib.util.spec_from_file_location('own_helper_boundary',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
DATA={}
def reject(call):
    try:call()
    except ValueError as e:return str(e)
    raise AssertionError('expected rejection')

class Tests(unittest.TestCase):
    def test_01_baseline(self):
        before=set(sys.modules)
        a=m.audit_helper_boundary_HOST(model=m.MODEL)
        self.assertEqual(len(a['audit']['bindings']),5)
        self.assertTrue(a['audit'][m.FLAG]);self.assertEqual(a['inherited_pins_verified'],498)
        self.assertTrue(all(v is False for v in a['proof_scope'].values()))
        self.assertFalse(a['audit']['boundary']['selected_guard_accepts_cast_subnormals'])
        self.assertEqual(a['probe']['retained_cast_checks'][2]['actual_uint32'],1)
        self.assertEqual(a['probe']['new_probe_casts'],0)
        self.assertEqual(a['probe']['new_probe_operations'],0)
        self.assertFalse(any(n.startswith('axial_') for n in set(sys.modules)-before))
        DATA['audit']=a

    def test_02_alias_and_function_mutations(self):
        texts,_,_,_=m.load_retained()
        mutations=[
          ('wrong_source',m.ENTRY,'source=prior.source','source=transport'),
          ('source_cycle',m.ENTRY,'source=prior.source','source=source'),
          ('dynamic_source',m.ENTRY,'source=prior.source','source=lookup()'),
          ('unknown_module',m.ENTRY,'import axial_ORIGINAL_source_CPU_v1 as transport','import axial_not_in_sealed_registry as transport'),
          ('cast_finite_gate','axial_ORIGINAL_source_CPU_v1',"(w>>23)%256<255","(w>>23)%256<254"),
          ('value_subnormal_gate','axial_source_float64_stage_CPU_v1','(exponent!=0 or mantissa==0)','True'),
          ('value_width_contract','axial_source_float64_stage_CPU_v1','type(w) is int and width in (32,64)','type(w) is int and type(width) is int and width in (32,64)'),
          ('word_endianness','axial_source_float64_stage_CPU_v1',"struct.unpack('<Q',struct.pack('<d',v))","struct.unpack('>Q',struct.pack('<d',v))"),
          ('guard_selected_default','axial_geometry_decode_guard_CPU_v1','def bits(word,width,*,normal=True):','def bits(word,width,*,normal=False):'),
          ('guard_zero_sign','axial_geometry_decode_guard_CPU_v1',"magnitude==0 and sign==zero_sign","magnitude==0")]
        rows=[]
        for label,module,old,new in mutations:
            self.assertIn(old,texts[module]);altered=dict(texts);altered[module]=texts[module].replace(old,new,1)
            rows.append({'label':label,'module':module,'candidate_text':altered[module],
                         'candidate_sha256':m.sha(altered[module].encode()),'rejection':reject(lambda:m.inspect_helpers(altered))})
        altered=dict(texts);altered[m.ENTRY]+='\nsource=transport\n'
        rows.append({'label':'duplicate_binding','module':m.ENTRY,'candidate_text':altered[m.ENTRY],
                     'candidate_sha256':m.sha(altered[m.ENTRY].encode()),'rejection':reject(lambda:m.inspect_helpers(altered))})
        self.assertEqual(len(rows),11);DATA['static_rejections']=rows

    def test_03_probe_lineage(self):
        _,probe,_,_=m.load_retained()
        rows=[]
        for label,change in [
          ('PASS_bool_int',lambda p:p.__setitem__('PASS',1)),
          ('subnormal_clipped',lambda p:p['binary32_cast_checks'][2].__setitem__('actual_uint32',0)),
          ('source_zero_sign',lambda p:p['binary32_cast_checks'][3].__setitem__('actual_uint32',0)),
          ('claimed_current',lambda p:p.__setitem__('current_runtime_authenticated',True))]:
            altered=copy.deepcopy(probe);change(altered)
            rows.append({'label':label,'probe':altered,'rejection':reject(lambda:m.retain_probe(altered))})
        DATA['probe_rejections']=rows

    def test_04_types_forms(self):
        rows=[]
        for label,call in [
          ('model',lambda:m.audit_helper_boundary_HOST(model='implicit')),
          ('registry_type',lambda:m.StaticResolver([])),
          ('module_unknown',lambda:m.StaticResolver({}).tree('axial_missing')),
          ('module_path_escape',lambda:m.StaticResolver({}).tree('../axial_missing')),
          ('syntax',lambda:m.StaticResolver({'axial_x':'def !'}).tree('axial_x')),
          ('empty_registry_binding',lambda:m.StaticResolver({'axial_x':''}).binding('axial_x','source')),
          ('unsupported_from_import',lambda:m.StaticResolver({'axial_x':'from axial_y import source'}).binding('axial_x','source')),
          ('annotated_binding',lambda:m.StaticResolver({'axial_x':'source: object = None'}).binding('axial_x','source'))]:
            rows.append({'label':label,'rejection':reject(call)})
        DATA['type_form_rejections']=rows

if __name__=='__main__':
    res=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'PASS':res.wasSuccessful(),'tests':res.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    sys.exit(0 if res.wasSuccessful() else 1)
