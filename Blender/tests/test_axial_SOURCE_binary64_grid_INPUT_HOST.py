"""Own grid INPUT binding regressions only; retained numerical witnesses never replayed."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_binary64_grid_INPUT_HOST_v1 as c
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=c.load_retained();cls.packets,cls.inputs,cls.retained,cls.pins=cls.loaded
        cls.names=cls.inputs['synthetic_valid']['case_order']
        cls.domains=cls.inputs['synthetic_domain_INPUT_plans']
        cls.plans={}
        for name in cls.names:
            ctx=cls.inputs['synthetic_valid']['cases'][name]['context'];dom=cls.inputs['synthetic_validated_domains'][name]
            cls.plans[name]={'model':c.MODEL,'grid':c.prior.GRID,'arithmetic_model':c.prior.ARITH,
                'packet_sha256':c.digest(cls.packets[name]),'context_sha256':c.digest(ctx),
                'original_snapshot_sha256':ctx['original_snapshot_sha256'],'domain_sha256':dom['domain_sha256'],
                'scope':c.domain.SCOPE,'encoder_program_path':c.PROGRAM,'encoder_program_sha256':c.PROGRAM_SHA,
                'encoder_graph':copy.deepcopy(c.GRAPH),
                'sources':[{**{k:src[k] for k in c.GAUGES},'domain_source_sha256':c.digest(src),
                    'ORIGINAL_source_uint64':copy.deepcopy(src['ORIGINAL_source_uint64'])} for src in dom['sources']]}
    def run_audit(self,names=None,domains=None,plans=None,packets=None):
        return c.audit_INPUT_HOST(self.names if names is None else names,self.domains if domains is None else domains,
            self.plans if plans is None else plans,self.packets if packets is None else packets,model=c.MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected rejection '+label)
    def test_a_missing(self):
        names=self.inputs['real_missing']['case_order']
        with patch.object(c.prior,'component_wordclasses_HOST',side_effect=AssertionError('no numeric predicate')),patch.object(c.prior,'audit_wordclasses_HOST',side_effect=AssertionError('no old audit')):
            a=self.run_audit(names,{},{});b=self.run_audit(names,{},dict.fromkeys(names,None))
            partial=self.run_audit(plans={})
        self.assertEqual(a['cases'],b['cases']);self.assertEqual(a['missing_INPUT_cases'],17);self.assertEqual(a['valid_INPUT_cases'],0)
        self.assertEqual(sum(len(x['context']['source_order']) for x in a['cases'].values()),19)
        self.assertTrue(all(x['INPUT']['sources'] is None for x in a['cases'].values()))
        self.assertEqual(partial['missing_INPUT_cases'],3)
        DATA['real_missing']=a;DATA['explicit_None_missing']=b;DATA['domain_present_grid_missing']=partial
    def test_b_explicit_synthetic(self):
        with patch.object(c.prior,'component_wordclasses_HOST',side_effect=AssertionError('no predicate even valid INPUT')),patch.object(c.prior,'audit_wordclasses_HOST',side_effect=AssertionError('no old audit')):
            a=self.run_audit()
        self.assertEqual(a['valid_INPUT_cases'],3);self.assertEqual(a['wordclass_predicate_assessments'],0)
        self.assertEqual(sum(len(x['INPUT']['sources']) for x in a['cases'].values()),4)
        for name,x in a['cases'].items():
            self.assertEqual(x['context'],self.inputs['synthetic_valid']['cases'][name]['context'])
            self.assertTrue(x['INPUT'][c.FLAG]);self.assertFalse(x['INPUT']['actual_scene_domain_grid_authenticated'])
            self.assertFalse(x['INPUT']['encoder_graph_execution_authenticated'])
            self.assertFalse(x['INPUT']['frozen_guard_admission_for_entire_box_proved'])
            self.assertTrue(all(x['INPUT'][k] is False for k in c.FALSE));self.assertIsNone(x['INPUT']['uniform_executed_SOURCE_error_L1'])
        DATA['synthetic_grid_INPUT_plans']=self.plans;DATA['synthetic_valid']=a
    def test_c_plan_graph_bindings(self):
        rows=[]
        changes=[('grid','all real continuum'),('arithmetic_model','FTZ'),('model','legacy'),
            ('packet_sha256','0'*64),('context_sha256','0'*64),('original_snapshot_sha256','0'*64),
            ('domain_sha256','0'*64),('scope','SOURCE-point-only'),('encoder_program_path','foreign.py'),
            ('encoder_program_sha256','0'*64)]
        for key,value in changes:
            plans=copy.deepcopy(self.plans);plans[self.names[-1]][key]=value
            self.reject(key,lambda:self.run_audit(plans=plans),rows)
        for label,mut in [
            ('authority_extra',lambda p:p.__setitem__('scene_authenticated',True)),
            ('graph_FMA',lambda p:p['encoder_graph']['nodes_per_component'][1].__setitem__(1,'FMA')),
            ('graph_reorder',lambda p:p['encoder_graph']['nodes_per_component'].reverse()),
            ('graph_zero_canonicalize',lambda p:p['encoder_graph'].__setitem__('signed_zero','canonicalize')),
            ('graph_endian',lambda p:p['encoder_graph'].__setitem__('limb_wire_abi','big-endian')),
            ('graph_product_substitute',lambda p:p['encoder_graph'].__setitem__('covered','full SOURCE')),
            ('graph_extra',lambda p:p['encoder_graph'].__setitem__('device_authentication',True))]:
            plans=copy.deepcopy(self.plans);mut(plans[self.names[-1]])
            self.reject(label,lambda:self.run_audit(plans=plans),rows)
        DATA['plan_graph_rejections']=rows
    def test_d_source_bindings(self):
        rows=[]
        changes=[('source_id','foreign'),('source_phase_reference_id','foreign'),('terminal_reference_id','foreign'),
                 ('common_terminal_reference_id','foreign'),('domain_source_sha256','0'*64),
                 ('ORIGINAL_source_uint64',[False,0]),('ORIGINAL_source_uint64',[1.0,0]),
                 ('ORIGINAL_source_uint64',[2**64,0]),('ORIGINAL_source_uint64',[1,0]),
                 ('ORIGINAL_source_uint64',[2047<<52,0])]
        for key,value in changes:
            plans=copy.deepcopy(self.plans);plans['two_sources']['sources'][-1][key]=value
            self.reject(key+str(len(rows)),lambda:self.run_audit(plans=plans),rows)
        for label,mut in [('coverage_missing',lambda p:p['sources'].pop()),
            ('coverage_order',lambda p:p['sources'].reverse()),
            ('signed_bits_changed',lambda p:p['sources'][-1]['ORIGINAL_source_uint64'].__setitem__(1,p['sources'][-1]['ORIGINAL_source_uint64'][1]^(1<<63))),
            ('row_authority',lambda p:p['sources'][-1].__setitem__('authenticated',True))]:
            plans=copy.deepcopy(self.plans);mut(plans['two_sources']);self.reject(label,lambda:self.run_audit(plans=plans),rows)
        DATA['source_rejections']=rows
    def test_e_batch_and_lineage(self):
        rows=[]
        with patch.object(c.prior,'component_wordclasses_HOST',side_effect=AssertionError('no predicate')) as spy:
            domains=copy.deepcopy(self.domains);domains['two_sources']['context_sha256']='0'*64
            self.reject('late_domain',lambda:self.run_audit(domains=domains),rows)
            self.reject('domain_absent_with_grid',lambda:self.run_audit(domains={}),rows)
            self.reject('case_order_duplicate',lambda:self.run_audit(names=self.names+[self.names[-1]]),rows)
            self.reject('unknown_plan_key',lambda:self.run_audit(plans={**self.plans,'foreign':None}),rows)
            packets=copy.deepcopy(self.packets);packets.pop('two_sources')
            self.reject('missing_packet',lambda:self.run_audit(packets=packets),rows)
            self.assertEqual(spy.call_count,0)
        with patch.object(c,'PARENT_SHA','0'*64):self.reject('parent_SHA',c.load_retained,rows)
        DATA['batch_lineage_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())
