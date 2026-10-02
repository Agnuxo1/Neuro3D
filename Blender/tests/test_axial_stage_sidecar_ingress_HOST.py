"""Bounded wire tests, synthetic INPUT controls only, no old suites/producers."""
import base64,copy,json,sys,unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_stage_sidecar_ingress_HOST_v1 as core
DATA={}
def plan_input(packet):
    ctx=core.allocation.context_from_packet(packet,core.digest(packet),model=core.allocation.MODEL)
    cap=F(*ctx['unchanged_field_L1_cap']);sources=[{'source_id':sid,'cap_L1':core.prior.pair(cap/4),
        'stages_L1':dict.fromkeys(core.prior.STAGES,[1,10**14])} for sid in ctx['source_order']]
    groups=[]
    for port,g in ctx['groups']:
        count=sum(a['port']==port and a['coherence_group']==g for a in ctx['assignments'])
        groups.append({'port':port,'coherence_group':g,'reserves_L1':dict.fromkeys(core.prior.RESERVES,core.prior.pair((cap-count*cap/4)/2))})
    return {'model':core.prior.MODEL,'units':core.prior.UNITS,'context_sha256':core.digest(ctx),'sources':sources,'groups':groups}
def receipt(raw):return {'bytes':len(raw),'sha256':core.sha(raw)}
def wire(raw):return {'raw_base64':base64.b64encode(raw).decode(),'receipt':receipt(raw)}
class WireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.pins=cls.retained
        cls.plans={n:plan_input(cls.packets[n]) for n in ('nonexact_geometry_phase_PASS','thin_resolved','two_sources')}
    def test_a_roundtrip_and_missing(self):
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'compare_source',side_effect=AssertionError('no numerical charge comparison')),patch.object(core.prior,'audit_stage_allocation_HOST',side_effect=AssertionError('no old audit')):
            a=core.audit_ingress_HOST(self.old['case_order'],{},model=core.MODEL)
            DATA['real_missing']=a;self.assertEqual((a['missing_sidecars_STOP'],a['inherited_pins_verified']),(17,358))
            entries={};captured={}
            for n,p in self.plans.items():
                raw,r=core.serialize(self.packets[n],p,model=core.MODEL);entries[n]={'raw':raw,'receipt':r};captured[n]=wire(raw)
                b=core.receive(self.packets[n],raw,r,model=core.MODEL)
                self.assertTrue(b['allocation_INPUT']['allocation_INPUT_valid']);self.assertEqual(b['status'],'STOP')
            DATA['synthetic_wires']=captured;DATA['synthetic_INPUT_plans']=copy.deepcopy(self.plans)
            DATA['synthetic_ingress']=core.audit_ingress_HOST(list(entries),entries,model=core.MODEL)
        self.assertEqual(DATA['synthetic_ingress']['sidecar_INPUT_admitted'],3)
        self.assertEqual(DATA['synthetic_ingress']['numerical_charge_comparisons'],0)
        raw,_=core.serialize(self.packets['thin_resolved'],self.plans['thin_resolved'],model=core.MODEL)
        spaced=b' \r\n'+raw+b' \t';out=core.receive(self.packets['thin_resolved'],spaced,receipt(spaced),model=core.MODEL)
        DATA['whitespace_wire']={'wire':wire(spaced),'result':out}
        self.assertEqual(out['canonical_envelope_sha256'],core.sha(raw));self.assertNotEqual(core.sha(spaced),core.sha(raw))
    def test_b_receipt_syntax_and_plan_rejects(self):
        rejects=[];DATA['wire_rejections']=rejects
        packet=self.packets['thin_resolved'];raw,_=core.serialize(packet,self.plans['thin_resolved'],model=core.MODEL)
        def reject(label,b,r=None):
            rc=receipt(b) if r is None else r
            with self.assertRaises((ValueError,TypeError,KeyError,UnicodeError)) as cm:core.receive(packet,b,rc,model=core.MODEL)
            rejects.append({'label':label,'wire':wire(b),'submitted_receipt':rc,'reason':str(cm.exception)})
        bad=receipt(raw);bad['bytes']=True;reject('receipt_length_bool',raw,bad)
        bad=receipt(raw);bad['sha256']='0'*64;reject('receipt_SHA_mismatch',raw,bad)
        bad=receipt(raw);bad['sha256']=bad['sha256'].upper();reject('receipt_SHA_uppercase',raw,bad)
        bad=receipt(raw);bad['bytes']-=1;reject('receipt_length_mismatch',raw,bad)
        bad=receipt(raw);bad['GPU_job_admission']=True;reject('receipt_authority_injection',raw,bad)
        reject('duplicate_root_schema',raw.replace(b'"schema":',b'"schema":"foreign","schema":',1))
        target=b'"source_Horner_L1":[1,100000000000000]'
        self.assertIn(target,raw)
        reject('duplicate_nested_escaped_alias',raw.replace(target,target+b',"\\u0073ource_Horner_L1":[0,1]',1))
        for label,mut in [('wrong_schema',lambda e:e.__setitem__('schema','other')),('wrong_packet',lambda e:e.__setitem__('input_packet_sha256','0'*64)),('null_plan',lambda e:e.__setitem__('plan',None)),('unknown_envelope_flag',lambda e:e.__setitem__('accepted_full_field_pipeline',True)),('plan_context',lambda e:e['plan'].__setitem__('context_sha256','0'*64)),('stage_missing',lambda e:e['plan']['sources'][0]['stages_L1'].pop('ideal_material_L1')),('quota_bool',lambda e:e['plan']['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',[True,1])),('quota_noncanonical',lambda e:e['plan']['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',[2,2]))]:
            e=json.loads(raw);mut(e);reject(label,core.allocation.canon(e))
        reject('float_quota',raw.replace(target,b'"source_Horner_L1":1e-14',1))
        reject('nonfinite_quota',raw.replace(target,b'"source_Horner_L1":NaN',1))
        reject('trailing_JSON',raw+b'{}')
        reject('invalid_utf8',b'\xff'+raw)
        reject('BOM',b'\xef\xbb\xbf'+raw)
        reject('unpaired_surrogate',raw.replace(b'"schema":',b'"schema":"\\ud800","removed_schema":',1))
        reject('comment',raw+b'//note')
        reject('unclosed_container',raw[:-1])
    def test_c_resources_before_global_parse(self):
        rejected=[];DATA['resource_rejections']=rejected
        samples=[('depth',b'['*13+b'0'+b']'*13),('containers',b'['+b'[],'*2048+b'[]]'),
            ('integer_digits',b'['+b'9'*97+b']'),('string_UTF8',b'["'+b'x'*257+b'"]'),
            ('escaped_token',b'["'+b'\\u0078'*257+b'"]')]
        p=self.packets['thin_resolved']
        for label,raw in samples:
            with patch.object(core,'parse_unique',side_effect=AssertionError('resource bound BEFORE global parse')) as parse:
                with self.assertRaises((ValueError,UnicodeError)) as cm:core.receive(p,raw,receipt(raw),model=core.MODEL)
                self.assertEqual(parse.call_count,0)
            rejected.append({'label':label,'wire':wire(raw),'reason':str(cm.exception),'global_parse_calls':0})
        raw=b' '*65537
        with patch.object(core,'parse_unique',side_effect=AssertionError('oversize before parse')) as parse:
            with self.assertRaises(ValueError) as cm:core.receive(p,raw,receipt(raw),model=core.MODEL)
            self.assertEqual(parse.call_count,0)
        rejected.append({'label':'oversize','generator':'ASCII space repeated 65537','receipt':receipt(raw),'reason':str(cm.exception),'global_parse_calls':0})
        base,_=core.serialize(p,self.plans['thin_resolved'],model=core.MODEL);padded=base+b' '*(65536-len(base))
        result=core.receive(p,padded,receipt(padded),model=core.MODEL)
        DATA['byte_limit_boundary']={'base_wire':wire(base),'padding_spaces':65536-len(base),'receipt':receipt(padded),'result':result}
        controls={}
        for label,raw in [('depth12',b'['*12+b'0'+b']'*12),('integer96',b'['+b'9'*96+b']'),('string256',b'["'+b'x'*256+b'"]'),('quoted_brackets',b'{"x":"[{{\\\"}]]"}')]:
            _,stats=core.preflight(raw);controls[label]={'wire':wire(raw),'stats':stats}
        DATA['preflight_boundary_controls']=controls
    def test_d_atomic_failure_and_serializer(self):
        entries={}
        for n in ('nonexact_geometry_phase_PASS','thin_resolved'):
            raw,r=core.serialize(self.packets[n],self.plans[n],model=core.MODEL);entries[n]={'raw':raw,'receipt':r}
        entries['thin_resolved']['receipt']['sha256']='0'*64
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'compare_source',side_effect=AssertionError('no charge comparison')) as compare:
            with self.assertRaises(ValueError) as cm:core.audit_ingress_HOST(list(entries),entries,model=core.MODEL)
            self.assertEqual(compare.call_count,0)
        DATA['atomic_rejection']={'reason':str(cm.exception),'partial_results_returned':False,'numeric_comparisons':0}
        with self.assertRaises(ValueError) as cm:core.serialize(self.packets['thin_resolved'],None,model=core.MODEL)
        DATA['serialize_absent_rejection']=str(cm.exception)
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(WireTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
