"""New integer helper CPU mirror tests. Does not execute GLSL or old suites."""
import copy,hashlib,json,re,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_SOURCE_zero_aware_integer_HOST_v1 as c
DATA={}
CONTROL=[
 ('zero++',[0,0]),('zero-+',[0x80000000,0]),('zero+-',[0,0x80000000]),('zero--',[0x80000000,0x80000000]),
 ('unit_and_minus_zero',[0x3f800000,0x80000000]),('negative_unit',[0xbf800000,0]),
 ('cancel_positive_first',[0x3f800000,0xbf800000]),('cancel_negative_first',[0xbf800000,0x3f800000]),
 ('tie_even',[0x3f800000,0x25000000]),('tie_odd',[0x3f800000,0x25c00000]),
 ('sticky_above_tie',[0x3f800000,0x25000001]),('below_tie',[0x3f800000,0x24ffffff]),
 ('renormalize_to_one',[0x3f800000,0xa4800000]),('negative_renormalize',[0xbf800000,0x24800000]),
 ('two_max_normal',[0x7f7fffff,0x7f7fffff]),('two_negative_max',[0xff7fffff,0xff7fffff]),
 ('smallest_difference',[0x00800001,0x80800000]),('large_exponent_gap',[0x3f800000,0x00800000]),
 ('high_minuszero_low_unit',[0x80000000,0x3f800000]),('high_zero_low_negative_unit',[0,0xbf800000])]
def independent_value(w):
 e=(w>>23)&255;m=w&0x7fffff
 return (-1 if w>>31 else 1)*F(m+(1<<23) if e else m)*F(2)**((e or 1)-150)
def expected_words(limbs):
 a=sum(map(independent_value,limbs),F(0))
 if not a:return ((limbs[0]>>31)<<63) if all(w&0x7fffffff==0 for w in limbs) else 0
 sign=int(a<0);a=abs(a);e=a.numerator.bit_length()-a.denominator.bit_length()
 if a<F(2)**e:e-=1
 t=a/(F(2)**(e-52));m=t.numerator//t.denominator;rest=t-m
 if rest>F(1,2) or rest==F(1,2) and m&1:m+=1
 if m==1<<53:m>>=1;e+=1
 return sign<<63|(e+1023)<<52|(m-(1<<52))
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.loaded=c.load_retained()
  with patch.object(c,'load_retained',return_value=cls.loaded):cls.request=c.make_request()
 def test_integer_controls(self):
  out=[]
  for name,limbs in CONTROL:
   v=c.decode_words(limbs,model=c.MODEL);self.assertEqual(v['decoded_uint64'],expected_words(limbs),name)
   self.assertEqual(v['native_FP_operations'],0);self.assertFalse(v['GLSL_compiled']);out.append({'control':name,'result':v})
  self.assertTrue(out[12]['result']['rounding_detail']['renormalized'])
  self.assertTrue(out[9]['result']['rounding_detail']['round_up'])
  self.assertFalse(out[8]['result']['rounding_detail']['round_up'])
  self.assertEqual(out[1]['result']['decoded_uint64'],1<<63)
  self.assertEqual(out[6]['result']['decoded_uint64'],0)
  DATA['controls']=out
 def test_retained_scene_inputs(self):
  with patch.object(c,'load_retained',return_value=self.loaded):a=c.audit(copy.deepcopy(self.request),model=c.MODEL);missing=c.audit(None,model=c.MODEL)
  self.assertEqual(a['new_CPU_integer_decodes'],8);self.assertEqual(len(a['sources']),4)
  self.assertEqual(a['group_admissions'],0);self.assertTrue(all(v is False for v in a['proof_scope'].values()))
  self.assertFalse(a['scene_or_program_execution_authenticated']);self.assertFalse(a['shader_integrated_into_runner'])
  for row in a['sources']:
   for scalar in row['scalars']:self.assertEqual(scalar['decoded_uint64'],expected_words(scalar['limb_uint32']))
  self.assertEqual(missing['missing_sources'],19)
  DATA.update(request=self.request,audit=a,missing=missing)
 def test_atomic_input_rejections(self):
  cases=[]
  def change(label,fn):
   r=copy.deepcopy(self.request);fn(r);cases.append((label,r))
  change('GPU mirror alias',lambda r:r.update(execution_backend='GPU'))
  change('old decoder model',lambda r:r.update(model='axial-SOURCE-hilo-high-zero-sign-decoder-CPU-v1'))
  change('unsealed shader',lambda r:r.update(shader_sha256='0'*64))
  change('unsealed dependency',lambda r:r.update(signed512_shader_sha256='0'*64))
  change('late second SOURCE malformed',lambda r:r['upstream_transport_INPUT']['decoder_INPUT']['SOURCE_limb_records'][-1]['limb_uint32'].__setitem__(3,1))
  change('program selector changed',lambda r:r['upstream_transport_INPUT']['program_INPUT']['decoder_selection'].update(implementation_sha256='0'*64))
  change('late frame altered',lambda r:r['upstream_transport_INPUT']['frames'][-1].update(frame_base64='AA=='))
  change('quota addition',lambda r:r.update(cap_rad=[1,1]))
  out=[]
  for name,r in cases:
   with patch.object(c,'load_retained',return_value=self.loaded),patch.object(c,'decode_words',wraps=c.decode_words) as decoder:
    with self.assertRaises(ValueError):c.audit(r,model=c.MODEL)
    self.assertEqual(decoder.call_count,0);out.append({'control':name,'new_decode_calls':0,'rejected':True})
  DATA['input_rejections']=out
 def test_word_gate_before_decode(self):
  bad=[True,-1,1<<32,1.0,1,0x007fffff,0x80000001,0x7f800000,0x7fc00000,0xffc00000]
  out=[]
  for w in bad:
   for pos in (0,1):
    limbs=[0x3f800000,0];limbs[pos]=w
    with patch.object(c.prior,'decode_hilo',wraps=c.prior.decode_hilo) as decode:
     with self.assertRaises(ValueError):c.decode_words(limbs,model=c.MODEL)
     self.assertEqual(decode.call_count,0);out.append({'limbs':limbs,'frozen_decode_calls':0,'rejected':True})
  for m in (None,False,'legacy'):
   with self.assertRaises(ValueError):c.decode_words([0,0],model=m)
  DATA['word_rejections']=out;DATA['model_rejections']=3
 def test_source_and_range_gate(self):
  raw=(ROOT/c.SHADER).read_bytes();c.source_lock(raw)
  clean=re.sub(r'//[^\n]*','',raw.decode())
  self.assertIsNone(re.search(r'\b(half|fixed|short|long|unsigned|input|output)\b',clean))
  mutants=[raw.replace(b'top+874',b'top+873'),raw.replace(b'limbs.x&0x80000000u',b'limbs.y&0x80000000u'),raw.replace(b'(sig.x&1u)!=0u',b'true'),raw.replace(b'top>277',b'top>511'),raw.replace(b'guardBit',b'half')]
  for b in mutants:
   self.assertNotEqual(b,raw)
   with self.assertRaises(ValueError):c.source_lock(b)
  huge=[0]*16;huge[8]=1<<22
  with self.assertRaises(ValueError):c.round_mag(huge,0)
  for sign in (True,1,1<<32):
   with self.assertRaises(ValueError):c.round_mag([0]*16,sign)
  DATA['source_rejections']=[{'mutant_sha256':hashlib.sha256(v).hexdigest(),'rejected':True} for v in mutants];DATA['range_rejections']=4
if __name__=='__main__':
 r=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 print(json.dumps({'tests_run':r.testsRun,'errors':len(r.errors),'failures':len(r.failures),'data':DATA},sort_keys=True));sys.exit(not r.wasSuccessful())
