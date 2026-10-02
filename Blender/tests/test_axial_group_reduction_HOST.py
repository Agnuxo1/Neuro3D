"""Only new reduction tests; no retained numerical producer or old suite execution."""
from copy import deepcopy
from fractions import Fraction as F
import json,sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_group_reduction_HOST_v1 as core
import axial_amplitude_allocation_HOST_v1 as allocation
DATA={}
def word(x):return struct.unpack('<Q',struct.pack('<d',x))[0]
def plans(ctx,zero=False):
    cap=allocation.rational(ctx['unchanged_field_L1_cap'])
    per=F(0) if zero else cap/4
    sources=[{'source_id':s,'cap_L1':core.pair(per)} for s in ctx['source_order']]
    groups=[];stages=[]
    for p,g in ctx['groups']:
        count=sum(a['port']==p and a['coherence_group']==g for a in ctx['assignments'])
        reserve=cap-per*count
        groups.append({'port':p,'coherence_group':g,'remaining_stages_reserved_L1':core.pair(reserve)})
        stages.append({'port':p,'coherence_group':g,'reduction_cap_L1':[0,1],
                       'other_stages_reserved_L1':core.pair(reserve)})
    source={'model':allocation.MODEL,'units':allocation.UNITS,'context_sha256':allocation.digest(ctx),'sources':sources,'groups':groups}
    stage={'model':core.MODEL,'units':allocation.UNITS,'context_sha256':allocation.digest(ctx),
           'source_allocation_sha256':allocation.digest(source),'groups':stages}
    return source,stage
class ReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.bare,cls.mirror,cls.tree,cls.pins=core.load_retained()
        cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        cls.names=list(cls.packets)
        cls.alloc={};cls.stage={}
        for n in cls.names:
            ctx=allocation.context_from_packet(cls.packets[n],allocation.digest(cls.packets[n]),model=allocation.MODEL)
            cls.alloc[n],cls.stage[n]=plans(ctx)
        DATA['source_INPUT_plans']=cls.alloc;DATA['stage_INPUT_plans']=cls.stage
        DATA['missing']=core.audit_group_reduction_HOST(cls.names,dict.fromkeys(cls.names),dict.fromkeys(cls.names),model=core.MODEL)
        DATA['explicit_synthetic_INPUT_controls']=core.audit_group_reduction_HOST(cls.names,cls.alloc,cls.stage,model=core.MODEL)
        DATA['rejections']=[];DATA['primitives']=[]
    def test_complete_sources_and_static_stage_budget(self):
        d=DATA['explicit_synthetic_INPUT_controls']
        self.assertEqual(len(d['cases']),17);self.assertEqual(d['retained_corner_sums'],16)
        self.assertEqual(d['new_RN64_additions'],0)
        self.assertEqual(sum(c[core.FLAG] for c in d['cases'].values()),4)
        self.assertEqual(sum(len(c['sources']) for c in d['cases'].values()),19)
        self.assertEqual(sum(v['reason_provenance']=='unchanged_retained_numerical_STOP'
                             for c in DATA['missing']['cases'].values() for v in c['sources']),14)
        g=d['cases']['two_sources']['groups'][0]
        self.assertEqual(g['blocked_source_ids'],['other']);self.assertNotIn('corner_sums',g)
        self.assertFalse(d['cases']['two_sources'][core.FLAG])
        for n in self.names:
            self.assertFalse(DATA['missing']['cases'][n][core.FLAG])
            self.assertEqual([s['source_id'] for s in d['cases'][n]['sources']],self.bare[n]['source_order'])
    def test_identity_and_bounds_no_full_pipeline(self):
        d=DATA['explicit_synthetic_INPUT_controls']
        for n,c in d['cases'].items():
            for flag in core.FALSE:self.assertIs(c[flag],False)
            for g in c['groups']:
                for flag in core.FALSE:self.assertIs(g[flag],False)
                if g['retained_corner_sum_computed']:
                    r=self.mirror[n]['sources'][0]
                    self.assertEqual(g['reduction_RN64_error_L1_bound'],[0,1])
                    self.assertEqual(g['source_errors_L1_sum'],r['reflected_source_error_L1_to_ORIGINAL_bound'])
                    for i,s in enumerate(g['corner_sums']):
                        self.assertEqual(s['sum_uint64'],r['reflected_corner_products_HOST'][i]['reflected_uint64'])
                        self.assertEqual(s['trace'],[])
        for flag in core.FALSE:self.assertIs(d[flag],False)
        for key in ('new_products','new_trigonometry','new_ray_traces','old_numeric_suites_executed'):self.assertEqual(d[key],0)
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
    def test_missing_stage_zero_source_FAIL_and_missing_source(self):
        n='positive'
        DATA['missing_stage']=core.audit_group_reduction_HOST([n],{n:self.alloc[n]},{n:None},model=core.MODEL)
        self.assertIn('missing explicit reduction-stage',DATA['missing_stage']['cases'][n]['groups'][0]['reason'])
        a,s=plans(DATA['missing']['cases'][n]['context'],zero=True)
        DATA['zero_source_INPUT']={'source':a,'stage':s}
        DATA['zero_source']=core.audit_group_reduction_HOST([n],{n:a},{n:s},model=core.MODEL)
        self.assertEqual(DATA['zero_source']['cases'][n]['sources'][0]['status'],'FAIL')
        self.assertNotIn('corner_sums',DATA['zero_source']['cases'][n]['groups'][0])
    def test_new_multisource_primitives_cancellation_ties_signedzero_subnormal(self):
        cases=[
            [[word(2**53),0],[word(1.0),0],[word(-2**53),0]],
            [[word(1.0),word(-1.0)],[word(2**-53),word(-2**-53)]],
            [[word(1.0+2**-52),0],[word(2**-53),0]],
            [[core.SIGN,core.SIGN],[core.SIGN,core.SIGN]],
            [[1,core.SIGN|1],[1,core.SIGN|1]],
            [[word(.1),0],[word(-.1),0]],
            [[core.SIGN,1]],
        ]
        for w in cases:DATA['primitives'].append(core.reduce_words(w,model=core.MODEL))
        self.assertEqual(DATA['primitives'][0]['sum_uint64'],[0,0])
        self.assertEqual(DATA['primitives'][0]['rounding_error_L1_bound'],[1,1])
        self.assertEqual(DATA['primitives'][3]['sum_uint64'],[core.SIGN,core.SIGN])
        self.assertEqual(DATA['primitives'][4]['sum_uint64'],[2,core.SIGN|2])
        self.assertEqual(DATA['primitives'][6]['RN64_additions'],0)
    def test_reject_injected_or_incomplete_stage_INPUT(self):
        n='positive'
        mutations=[
            (['model'],'other','wrong model'),(['units'],'phase-rad','wrong units'),
            (['context_sha256'],'0'*64,'swapped INPUT'),
            (['source_allocation_sha256'],'0'*64,'swapped source plan'),
            (['groups'],[],'missing groups'),
            (['groups',0,'port'],'other','wrong port'),
            (['groups',0,'coherence_group'],'other','wrong coherence group'),
            (['groups',0,'reduction_cap_L1'],[True,1],'bool cap'),
            (['groups',0,'reduction_cap_L1'],[0,2],'noncanonical cap'),
            (['groups',0,'reduction_cap_L1'],[-1,1],'negative cap'),
            (['groups',0,'reduction_cap_L1'],[1,1],'reserve overspend'),
            (['groups',0,'other_stages_reserved_L1'],[1,0],'zero denominator'),
            (['GPU_executed'],True,'caller output injected'),
        ]
        for path,value,label in mutations:
            p=deepcopy(self.stage[n]);obj=p
            for k in path[:-1]:obj=obj[k]
            obj[path[-1]]=value
            with self.assertRaises((ValueError,KeyError,TypeError)) as caught:
                core.audit_group_reduction_HOST([n],{n:self.alloc[n]},{n:p},model=core.MODEL)
            DATA['rejections'].append({'kind':'stage','path':path,'value':value,'label':label,'reason':str(caught.exception)})
        for names,a,s,model,label in [
            ([n,n],{n:self.alloc[n]},{n:self.stage[n]},core.MODEL,'duplicate cases'),
            ([n],{n:self.alloc[n]},{},core.MODEL,'missing stage map'),
            (['unknown'],{'unknown':None},{'unknown':None},core.MODEL,'unknown case'),
            ([n],{n:self.alloc[n]},{n:self.stage[n]},'other','model opt-in missing'),
            ([n],{n:None},{n:self.stage[n]},core.MODEL,'stage without source allocation')]:
            with self.assertRaises(ValueError) as caught:core.audit_group_reduction_HOST(names,a,s,model=model)
            DATA['rejections'].append({'kind':'selection','label':label,'reason':str(caught.exception)})
    def test_reject_nonfinite_bool_overflow_empty_primitive(self):
        for w,label in [([], 'empty'),([[True,0]],'bool'),([[2**64,0]],'range'),
                        ([[0x7ff0000000000000,0]],'infinity'),([[0x7ff8000000000000,0]],'NaN'),
                        ([[0x7fefffffffffffff,0],[0x7fefffffffffffff,0]],'overflow')]:
            with self.assertRaises(ValueError) as caught:core.reduce_words(w,model=core.MODEL)
            DATA['rejections'].append({'kind':'primitive','words':w,'label':label,'reason':str(caught.exception)})
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReductionTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
