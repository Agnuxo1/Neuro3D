"""Own INPUT schema tests, CPU1/60s; no old producer, scope audit or cap comparison."""
import copy,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_domain_phase_INPUT_HOST_v1 as c
DATA={}
CAP=[1,1000000000000] # NEW synthetic variable-domain INPUT control; not migrated/fitted policy.
ZERO=[0,1]
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.amp,cls.point,cls.pins=c.load_retained()
        cls.real=list(cls.amp['real_missing']['case_order'])
        cls.domains=copy.deepcopy(cls.amp['synthetic_domain_INPUT_plans'])
        cls.names=list(cls.domains)+['two_sources']
        # NEW schema-only multi-source control: exact ORIGINAL singleton domains.
        # Not a replacement of old fixtures, not a box guard certificate or revived group.
        name='two_sources';packet=cls.packets[name]
        ctx=c.allocation.context_from_packet(packet,c.digest(packet),model=c.allocation.MODEL)
        snap,_=c.domain.original.snapshot_from_packet(packet,ctx)
        DATA['synthetic_multisource_ORIGINAL_snapshot_base64']=packet['buffers_base64']['original_scene_json']
        cls.domains[name]={'model':c.domain.MODEL,'units':c.domain.UNITS,'context_sha256':c.digest(ctx),
                          'scope':c.SCOPE,'sources':[]}
        for a,s in zip(ctx['assignments'],snap['sources']):
            singleton=[[c.domain.pair(F.from_float(x)),c.domain.pair(F.from_float(x))] for x in s['field_reim']]
            cls.domains[name]['sources'].append({**{k:a[k] for k in c.GAUGES},'box_reim':singleton})
        cls.plans={};validated={}
        for name in cls.names:
            ctx=c.allocation.context_from_packet(cls.packets[name],c.digest(cls.packets[name]),model=c.allocation.MODEL)
            dom=c.domain.validate_domain(cls.packets[name],ctx,cls.domains[name]);validated[name]=copy.deepcopy(dom)
            cls.plans[name]={'model':c.MODEL,'units':c.UNITS,'context_sha256':c.digest(ctx),
                'domain_sha256':c.digest(cls.domains[name]),'scope':c.SCOPE,
                'sources':[{**{k:s[k] for k in c.GAUGES},'domain_source_sha256':c.digest(s),
                            'reference_model':c.REFERENCE,'cap_rad':CAP.copy()} for s in dom['sources']]}
        DATA['synthetic_validated_domains']=validated
        DATA['synthetic_domain_INPUT_plans']=copy.deepcopy(cls.domains)
        DATA['synthetic_control_INPUT_plans']=copy.deepcopy(cls.plans)
        DATA['synthetic_multisource_domain_provenance']='NEW INPUT syntax control; ORIGINAL singleton; no previous domain changed'
    def audit(self,names,domains,plans):return c.audit_INPUT_HOST(names,domains,plans,self.packets,model=c.MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected rejection '+label)
    def test_a_missing(self):
        a=self.audit(self.real,{},{});b=self.audit(self.real,{},dict.fromkeys(self.real))
        self.assertEqual(a,b);self.assertEqual((a['valid_INPUT_cases'],a['missing_INPUT_cases']),(0,17))
        self.assertEqual(sum(len(v['context']['source_order']) for v in a['cases'].values()),19)
        self.assertTrue(all(v['INPUT']['sources'] is v['INPUT']['uniform_phase_INPUT_quota_fits'] is None for v in a['cases'].values()))
        DATA['real_missing']=a;DATA['explicit_None_missing']=b
        d=self.audit(self.names,self.domains,{})
        self.assertTrue(all(v['INPUT']['domain_INPUT_valid'] and not v['INPUT'][c.FLAG] for v in d['cases'].values()))
        DATA['domain_present_phase_missing']=d
    def test_b_synthetic_only(self):
        with patch.object(c.prior,'audit_reference_scope_HOST',side_effect=AssertionError('no prior audit')),patch.object(c.prior.schema,'validate_plan',side_effect=AssertionError('no point INPUT adapter')),patch.object(c.prior.prior,'reflected_phase_HOST',side_effect=AssertionError('no certificate construction')),patch.object(c.prior.prior.prior.producer,'execute',side_effect=AssertionError('no native SOURCE')):
            a=self.audit(self.names,self.domains,self.plans)
            zero=copy.deepcopy(self.plans)
            for p in zero.values():
                for s in p['sources']:s['cap_rad']=ZERO.copy()
            b=self.audit(self.names,self.domains,zero)
        for audit in (a,b):
            self.assertEqual((audit['valid_INPUT_cases'],audit['missing_INPUT_cases']),(3,0))
            self.assertTrue(all(v['INPUT']['uniform_phase_INPUT_quota_fits'] is None and v['INPUT']['uniform_executed_SOURCE_error_L1'] is None and v['status']=='STOP' for v in audit['cases'].values()))
            self.assertTrue(all(v[k] is False and v['INPUT'][k] is False for v in audit['cases'].values() for k in c.FALSE))
        self.assertEqual(len(a['cases']['two_sources']['INPUT']['sources']),2)
        DATA['synthetic_valid']=a;DATA['synthetic_zero_valid']=b;DATA['synthetic_zero_INPUT_plans']=zero
    def test_c_typed_caps(self):
        rows=[]
        bad=[('bool_num',[True,1]),('bool_den',[1,True]),('float',[1.0,1]),('negative',[-1,1]),
             ('den_zero',[0,0]),('den_negative',[1,-1]),('noncanonical',[2,2]),('zero_noncanonical',[0,2]),
             ('tuple',(1,2)),('missing',None),('scalar',0),('oversized',[1,1<<4097])]
        for label,cap in bad:
            p=copy.deepcopy(self.plans);p['two_sources']['sources'][-1]['cap_rad']=cap
            self.reject(label,lambda:self.audit(self.names,self.domains,p),rows)
        DATA['typed_cap_rejections']=rows
    def test_d_binding_and_atomic(self):
        rows=[]
        mutations=[
            ('phase_context',lambda ds,p:p['two_sources'].__setitem__('context_sha256','0'*64)),
            ('domain_plan_SHA',lambda ds,p:p['two_sources'].__setitem__('domain_sha256','0'*64)),
            ('source_domain_SHA',lambda ds,p:p['two_sources']['sources'][-1].__setitem__('domain_source_sha256','0'*64)),
            ('old_reference',lambda ds,p:p['two_sources']['sources'][-1].__setitem__('reference_model',c.prior.schema.REFERENCE)),
            ('source_gauge',lambda ds,p:p['two_sources']['sources'][-1].__setitem__('source_phase_reference_id','foreign')),
            ('terminal',lambda ds,p:p['two_sources']['sources'][-1].__setitem__('terminal_reference_id','foreign')),
            ('common_terminal',lambda ds,p:p['two_sources']['sources'][-1].__setitem__('common_terminal_reference_id','foreign')),
            ('identity',lambda ds,p:p['two_sources']['sources'][-1].__setitem__('source_id','foreign')),
            ('omission',lambda ds,p:p['two_sources']['sources'].pop()),
            ('order',lambda ds,p:p['two_sources']['sources'].reverse()),
            ('forged_PASS',lambda ds,p:p['two_sources'].__setitem__('uniform_phase_INPUT_quota_fits',True)),
            ('UNIT_alias',lambda ds,p:p['two_sources']['sources'][-1].__setitem__('UNIT_cap_rad',CAP)),
            ('phase_model',lambda ds,p:p['two_sources'].__setitem__('model','foreign')),
            ('phase_units',lambda ds,p:p['two_sources'].__setitem__('units','UNIT-phase-rad')),
            ('phase_scope',lambda ds,p:p['two_sources'].__setitem__('scope','geometry-variable')),
            ('missing_domain',lambda ds,p:ds.pop('two_sources')),
            ('domain_context',lambda ds,p:ds['two_sources'].__setitem__('context_sha256','0'*64)),
            ('changed_box',lambda ds,p:ds['two_sources']['sources'][-1]['box_reim'][0].__setitem__(1,[99,1]))]
        with patch.object(c.prior.prior,'reflected_phase_HOST',side_effect=AssertionError('no numeric certificate')) as spy:
            for label,mut in mutations:
                ds,p=copy.deepcopy(self.domains),copy.deepcopy(self.plans);mut(ds,p)
                self.reject(label,lambda:self.audit(self.names,ds,p),rows)
            self.assertEqual(spy.call_count,0)
        # Even singleton boxes reject the complete frozen point INPUT: no scope migration.
        self.reject('old_point_plan',lambda:self.audit(self.names,self.domains,self.point['synthetic_control_INPUT_plans']),rows)
        DATA['binding_rejections']=rows
    def test_e_boundaries_and_copy(self):
        rows=[]
        for label,fn in [
            ('model',lambda:c.audit_INPUT_HOST(self.names,self.domains,self.plans,self.packets,model='foreign')),
            ('duplicate_case',lambda:self.audit(self.names+self.names[:1],self.domains,self.plans)),
            ('foreign_phase_case',lambda:self.audit(self.names,self.domains,{**self.plans,'foreign':None})),
            ('foreign_domain_case',lambda:self.audit(self.names,{**self.domains,'foreign':None},self.plans)),
            ('packet_SHA',lambda:c.validate_plan(self.packets[self.names[0]],'0'*64,None,None,model=c.MODEL)),
            ('duplicate_JSON_key',lambda:c.allocation.parse('{"cap_rad":[0,1],"cap_rad":[1,1]}')),
            ('nonfinite_JSON',lambda:c.allocation.parse('{"cap_rad":NaN}'))]:
            self.reject(label,fn,rows)
        with patch.object(c,'PARENT_SHA','0'*64):self.reject('parent_SHA',c.load_retained,rows)
        p=copy.deepcopy(self.plans);a=self.audit(self.names,self.domains,p)
        p[self.names[0]]['sources'][0]['cap_rad'][0]=999
        self.assertEqual(a['cases'][self.names[0]]['INPUT']['sources'][0]['cap_rad'],CAP)
        DATA['boundary_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())
