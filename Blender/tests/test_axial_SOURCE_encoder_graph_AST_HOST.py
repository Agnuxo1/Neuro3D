"""Own static tests; never import the frozen encoder or any upstream producer."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'Blender/benchmarks/capacity_audit/axial_SOURCE_encoder_graph_AST_HOST_v1.py'
spec=importlib.util.spec_from_file_location('own_static_AST',PATH)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA={}

def reject(call):
    try:
        call()
    except ValueError as error:
        return str(error)
    raise AssertionError('expected fail-closed rejection')

class StaticTests(unittest.TestCase):
    def test_01_retained_and_formatting(self):
        before=set(sys.modules)
        data=m.audit_retained_AST_HOST(model=m.MODEL)
        self.assertTrue(data['match'][m.FLAG])
        self.assertEqual(data['inherited_pins_verified'],493)
        self.assertEqual(len(data['match']['regions']),6)
        self.assertTrue(all(v is False for v in data['proof_scope'].values()))
        self.assertEqual(data['group_admissions'],0)
        self.assertIsNone(data['uniform_executed_SOURCE_error_L1'])
        self.assertFalse(any('axial_guarded_source_product' in n or 'axial_ORIGINAL' in n for n in set(sys.modules)-before))
        text,plans,_,_=m.load_retained()
        self.assertTrue(m.inspect_AST('# formatting-only control\n'+text+'\n')[m.FLAG])
        DATA['audit']=data
        DATA['formatting_only_control']=m.inspect_AST('# formatting-only control\n'+text+'\n')

    def test_02_AST_mutations(self):
        text,_,_,_=m.load_retained()
        changes=[
          ('cast_wrapper','transport.cast32(v)','transport.cast64(v)'),
          ('subtract_wrapper','def native_subtract(a,b):return a-b','def native_subtract(a,b):return a+b'),
          ('add_wrapper','def native_add(a,b):return a+b','def native_add(a,b):return a*b'),
          ('high_operand','_,hw=native_cast32(source.value(w,64))','_,hw=native_cast32(source.value(hw,64))'),
          ('residual_width','source.value(hw,32)))','source.value(hw,64)))'),
          ('residual_operation','rw=source.word(native_subtract(','rw=source.word(native_add('),
          ('zero_sign_rule','hw>>31==0)','hw>>31==1)'),
          ('low_operand','_,lw=native_cast32(source.value(rw,64))','_,lw=native_cast32(source.value(w,64))'),
          ('limb_order','limbs.extend([hw,lw])','limbs.extend([lw,hw])'),
          ('wire_endianness',"raw=struct.pack('<IIII',*limbs)","raw=struct.pack('>IIII',*limbs)"),
          ('zero_canonicalization',"'new_RN64_subtractions':2,'zero_canonicalization_performed':False","'new_RN64_subtractions':2,'zero_canonicalization_performed':True"),
          ('guard_before_casts','originals=[guard.bits(w,64) for w in words]','originals=[F(0) for w in words]'),
          ('widening_width','lw=[source.word(source.value(w,32)) for w in limbs]','lw=[source.word(source.value(w,64)) for w in limbs]'),
          ('decode_operand',"a=node(lw[0],lw[1],'add','decode0')","a=node(lw[0],lw[2],'add','decode0')"),
          ('decode_dispatch','native_multiply if op==\'mul\' else native_add','native_multiply if op==\'mul\' else native_subtract'),
          ('decode_operation',"a=node(lw[0],lw[1],'add','decode0')","a=node(lw[0],lw[1],'mul','decode0')"),
          ('decorator','def encode_source(words):','@evil\ndef encode_source(words):')]
        controls=[]
        for name,old,new in changes:
            self.assertIn(old,text)
            candidate=text.replace(old,new,1)
            controls.append({'label':name,'candidate_text':candidate,'candidate_sha256':m.sha(candidate.encode()),
                             'rejection':reject(lambda:m.inspect_AST(candidate))})
        for name,suffix in [
          ('top_level_poison',"\nraise RuntimeError('NEVER EXECUTE THIS CANDIDATE')\n"),
          ('late_rebinding',"\nnative_add = native_subtract\n"),
          ('duplicate_definition',"\ndef native_add(a,b):return a+b\n")]:
            candidate=text+suffix
            controls.append({'label':name,'candidate_text':candidate,'candidate_sha256':m.sha(candidate.encode()),
                             'rejection':reject(lambda:m.inspect_AST(candidate))})
        self.assertEqual(len(controls),20)
        DATA['AST_rejection_controls']=controls

    def test_03_graph_mutations(self):
        text,plans,_,_=m.load_retained()
        graphs=[]
        for name,mutate in [
          ('component_order',lambda g:g['component_order'].reverse()),
          ('limb_order',lambda g:g['limb_order'].reverse()),
          ('residual_RN32',lambda g:g['nodes_per_component'][1].__setitem__(1,'RN32-sub')),
          ('ABI',lambda g:g.__setitem__('limb_wire_abi','4x uint32 big-endian')),
          ('signed_zero',lambda g:g.__setitem__('signed_zero','canonicalize all zeros')),
          ('FMA',lambda g:g['nodes_per_component'].append(['decode','FMA'])),
          ('typed_operand',lambda g:g['nodes_per_component'][0].__setitem__(2,True))]:
            altered=copy.deepcopy(plans)
            mutate(altered['two_sources']['encoder_graph'])
            with mock.patch.object(m,'inspect_AST',side_effect=AssertionError('ANY AST before ALL graphs')):
                error=reject(lambda:m.audit_plans(text,altered,model=m.MODEL))
            graphs.append({'label':name,'plans':altered,'rejection':error,'AST_inspections':0})
        DATA['graph_rejection_controls']=graphs

    def test_04_types_and_syntax(self):
        text,plans,_,_=m.load_retained()
        controls=[]
        for name,call in [
          ('bytes',lambda:m.inspect_AST(text.encode())),
          ('None',lambda:m.inspect_AST(None)),
          ('bool',lambda:m.inspect_AST(True)),
          ('empty',lambda:m.inspect_AST('')),
          ('oversize',lambda:m.inspect_AST('#'*(262144+1))),
          ('syntax',lambda:m.inspect_AST('def !')),
          ('wrong_model',lambda:m.audit_plans(text,plans,model='implicit')),
          ('wrong_plans_type',lambda:m.audit_plans(text,[],model=m.MODEL))]:
            controls.append({'label':name,'rejection':reject(call)})
        DATA['type_model_rejections']=controls

    def test_05_late_binding_failclosed(self):
        text,plans,_,_=m.load_retained()
        controls=[]
        for name,mutate in [
          ('path',lambda p:p['two_sources'].__setitem__('encoder_program_path','unsealed.py')),
          ('SHA',lambda p:p['two_sources'].__setitem__('encoder_program_sha256','0'*64)),
          ('coverage',lambda p:p.pop('two_sources'))]:
            altered=copy.deepcopy(plans);mutate(altered)
            with mock.patch.object(m,'inspect_AST',side_effect=AssertionError('inspection before batch acceptance')):
                error=reject(lambda:m.audit_plans(text,altered,model=m.MODEL))
            controls.append({'label':name,'plans':altered,'rejection':error,'AST_inspections':0})
        DATA['batch_binding_rejections']=controls

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(StaticTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
