"""New allocation INPUT tests; no numerical products, old suites or GPU loads."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib,json,sys,unittest,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_amplitude_allocation_HOST_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
SHA='04390dac11ab3d7b2a785542bc9b7c94a0f447686b777def0cdeb0a3dceca1b3'
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert t['rc']==0 and len(b)==t['stdout_bytes'] and hashlib.sha256(b).hexdigest()==t['stdout_sha256']
    return json.loads(b)
def pins_from(r):
    if 'code_doc_sha256' in r:
        return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];raw=(ROOT/d['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==d['sha256']
    p=pins_from(json.loads(raw));p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def plan(ctx,fractions,reserves):
    # Explicit NEW synthetic INPUT policy before checks; NOT automatic production allocation.
    cap=F(*ctx['unchanged_field_L1_cap'])
    return {'model':core.MODEL,'units':core.UNITS,'context_sha256':core.digest(ctx),
            'sources':[{'source_id':s,'cap_L1':core.pair(cap*f)} for s,f in zip(ctx['source_order'],fractions)],
            'groups':[{'port':g[0],'coherence_group':g[1],'remaining_stages_reserved_L1':core.pair(cap*f)} for g,f in zip(ctx['groups'],reserves)]}
class AllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/PREVIOUS).read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA
        r=json.loads(raw);cls.pins=pins_from(r);cls.pins[PREVIOUS]=SHA
        for p,h in cls.pins.items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
        cls.products=payload(r)['cases']
        cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        controls=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json').read_bytes()))['synthetic_controls']
        cls.packets.update({n:v['parent'] for n,v in controls.items()})
        cls.before={n:core.digest(p) for n,p in cls.packets.items()}
        cls.contexts={n:core.context_from_packet(p,core.digest(p),model=core.MODEL) for n,p in cls.packets.items()}
        cls.missing={n:core.audit_allocation_HOST(p,core.digest(p),None,model=core.MODEL) for n,p in cls.packets.items()}
        cls.plans={'positive':plan(cls.contexts['positive'],[F(1,4)],[F(3,4)]),
                   'two_sources':plan(cls.contexts['two_sources'],[F(1,4),F(1,4)],[F(1,2)]),
                   'explicit_zero_caps':plan(cls.contexts['positive'],[F(0)],[F(1)])}
        # NEW INPUT-only coherence hypothesis, no scene/cap change or physical claim.
        p=deepcopy(cls.packets['two_sources'])
        meta=core.parse(base64.b64decode(p['buffers_base64']['input_metadata_json']))
        meta['explicit_group_contract']['assignments'][1]['coherence_group']='g2'
        b=core.canon(meta);p['buffers_base64']['input_metadata_json']=base64.b64encode(b).decode()
        p['manifest']['buffers']['input_metadata_json']={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
        cls.synthetic_packet=p
        ctx=core.context_from_packet(p,core.digest(p),model=core.MODEL)
        cls.plans['synthetic_two_groups']=plan(ctx,[F(1,4),F(1,4)],[F(3,4),F(3,4)])
        cls.valid={}
        for n,a in cls.plans.items():
            p=cls.synthetic_packet if n=='synthetic_two_groups' else cls.packets['positive' if n=='explicit_zero_caps' else n]
            cls.valid[n]=core.audit_allocation_HOST(p,core.digest(p),a,model=core.MODEL)
        cls.rejections=[]
    def reject(self,p,a,label):
        before=core.digest(p)
        try:
            core.audit_allocation_HOST(p,before,a,model=core.MODEL)
        except (ValueError,KeyError,TypeError) as e:
            self.rejections.append({'label':label,'packet':deepcopy(p),'allocation':deepcopy(a),'reason':str(e),'type':type(e).__name__})
        else:
            self.fail('invalid allocation accepted '+label)
        self.assertEqual(core.digest(p),before)
    def test_all_original_INPUT_missing_NOT_zero_or_automatic_split(self):
        self.assertEqual(len(self.missing),17)
        for n,v in self.missing.items():
            self.assertFalse(v['result']['allocation_INPUT_valid'])
            self.assertEqual(v['result']['source_order'],self.contexts[n]['source_order'])
            self.assertIn('no default split/zero',v['result']['reason'])
            self.assertEqual(core.digest(self.packets[n]),self.before[n])
    def test_context_from_original_same_units_limits_assignments_gauges(self):
        for n,c in self.contexts.items():
            p=self.packets[n];m=core.parse(base64.b64decode(p['buffers_base64']['input_metadata_json']))
            self.assertEqual(c['assignments'],m['explicit_group_contract']['assignments'])
            self.assertEqual(c['unchanged_limits'],m['explicit_group_contract']['limits'])
            self.assertEqual(c['unchanged_field_L1_cap'],m['explicit_group_contract']['limits']['field_L1'])
            self.assertEqual(c['original_group_contract_sha256'],core.digest(m['explicit_group_contract']))
            self.assertEqual(c['units'],core.UNITS)
    def test_explicit_synthetic_INPUT_accounting_and_group_not_global_limit(self):
        for n,v in self.valid.items():
            self.assertTrue(v['result']['allocation_INPUT_valid'])
            for g in v['result']['groups']:
                self.assertEqual(F(*g['source_caps_sum_L1'])+F(*g['remaining_stages_reserved_L1'])+F(*g['unallocated_L1']),F(*g['unchanged_group_field_L1_cap']))
        self.assertEqual(len(self.valid['synthetic_two_groups']['result']['groups']),2)
        self.assertEqual(self.valid['explicit_zero_caps']['result']['source_caps_L1']['s'],[0,1])
    def test_reject_missing_duplicate_swap_units_noncanonical_binding_outputs(self):
        p=self.packets['two_sources'];good=self.plans['two_sources'];bad=[]
        v=deepcopy(good);v['sources'].pop();bad.append(('missing_source',v))
        v=deepcopy(good);v['sources'][1]['source_id']='s';bad.append(('duplicate_source',v))
        v=deepcopy(good);v['sources'].reverse();bad.append(('swap_source',v))
        v=deepcopy(good);v['units']='rad';bad.append(('rad_not_L1',v))
        v=deepcopy(good);v['sources'][0]['cap_L1']=[True,1];bad.append(('bool_cap',v))
        v=deepcopy(good);v['sources'][0]['cap_L1']=[2,2];bad.append(('noncanonical_cap',v))
        v=deepcopy(good);v['sources'][0]['cap_L1']=[-1,1];bad.append(('negative_cap',v))
        v=deepcopy(good);v['sources'][0]['cap_L1']=[1,0];bad.append(('zero_den',v))
        v=deepcopy(good);v['sources'][0]['cap_L1']=None;bad.append(('absent_not_zero',v))
        v=deepcopy(good);v['groups']=[];bad.append(('missing_reservation',v))
        v=deepcopy(good);v['groups'][0]['port']='other';bad.append(('wrong_port',v))
        v=deepcopy(good);v['groups'][0]['coherence_group']='g2';bad.append(('wrong_group',v))
        v=deepcopy(good);v['context_sha256']='0'*64;bad.append(('wrong_binding',v))
        v=deepcopy(good);v['expected_output']=[0,0];bad.append(('output_in_INPUT',v))
        v=deepcopy(good);v['model']='other';bad.append(('wrong_model',v))
        for label,a in bad:
            self.reject(p,a,label)
    def test_no_each_source_spends_full_group_budget_no_unreserved_remainder(self):
        p=self.packets['two_sources']
        c=self.contexts['two_sources']
        self.reject(p,plan(c,[F(1),F(1)],[F(0)]),'each_source_full_group_cap')
        self.reject(p,plan(c,[F(1,4),F(1,4)],[F(3,4)]),'reserve_overspend')
        good=deepcopy(self.plans['positive']);good['groups'][0].pop('remaining_stages_reserved_L1')
        self.reject(self.packets['positive'],good,'absent_reserve_not_zero')
    def test_source_product_STOPs_not_revived_by_valid_allocation(self):
        rows=[r for c in self.products.values() for r in c['sources']]
        self.assertEqual(sum(not r['source_product_evaluated'] for r in rows),14)
        self.assertFalse(self.products['two_sources']['sources'][1]['source_product_evaluated'])
        self.assertTrue(self.valid['two_sources']['result']['allocation_INPUT_valid'])
        self.assertFalse(self.valid['two_sources']['amplitude_budget_accepted'])
    def test_no_auth_remaining_stage_proof_amplitude_or_field_gate(self):
        for v in list(self.valid.values())+list(self.missing.values()):
            for k in ('amplitude_budget_accepted','source_product_gate_evaluated','remaining_stages_error_proved','field_values_computed','detector_evaluated','coherence_authenticated','execution_authenticated','accepted_full_field_pipeline','GPU_executed'):
                self.assertIs(v[k],False)
calls=[]
if __name__=='__main__':
    original=core.audit_allocation_HOST
    def capture(*args,**kwargs):
        try:
            v=original(*args,**kwargs)
        except (ValueError,KeyError,TypeError):
            raise
        calls.append(deepcopy(v));return v
    core.audit_allocation_HOST=capture
    run=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AllocationTests))
    print(json.dumps({'PASS':run.wasSuccessful(),'tests':run.testsRun,'pins':getattr(AllocationTests,'pins',{}),'contexts':getattr(AllocationTests,'contexts',{}),'missing':getattr(AllocationTests,'missing',{}),'plans':getattr(AllocationTests,'plans',{}),'valid':getattr(AllocationTests,'valid',{}),'synthetic_packet':getattr(AllocationTests,'synthetic_packet',{}),'rejections':getattr(AllocationTests,'rejections',[]),'calls':calls,'GPU_executed':False},sort_keys=True,separators=(',',':')))
    raise SystemExit(0 if run.wasSuccessful() else 1)
