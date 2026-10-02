"""New lineage checks only, no old proof construction/native arithmetic replay."""
from copy import deepcopy
import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_tree_lineage_HOST_v1 as core
import axial_amplitude_allocation_HOST_v1 as allocation
DATA={}
class TreeLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.products,cls.trees,cls.geometry,cls.events,cls.pins=core.load_retained()
        cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        DATA['audit']=core.audit_tree_lineage_HOST(list(cls.packets),model=core.MODEL)
        DATA['rejections']=[]
    def reject(self,target,path,value,label,rehash=False):
        objects={'packet':deepcopy(self.packets['positive']),'geometry':deepcopy(self.geometry['positive']),
                 'tree':deepcopy(self.trees['positive']),'events':deepcopy(self.events['positive'])}
        current=objects[target]
        for key in path[:-1]:current=current[key]
        current[path[-1]]=deepcopy(value)
        if rehash:
            objects['tree']['certificate_sha256']=allocation.digest(objects['tree']['certificate'])
        try:
            core.compare_bridge(objects['packet'],objects['geometry'],objects['tree'],objects['events'])
        except (ValueError,KeyError,TypeError) as error:
            DATA['rejections'].append({'target':target,'path':path,'value':value,'label':label,
                                       'rehash_tree':rehash,'type':type(error).__name__,'reason':str(error)})
        else:self.fail('invalid bridge accepted '+label)
    def test_original8bridges_9sources_5rejections_4missing_no_alias(self):
        cases=DATA['audit']['cases'];self.assertEqual(len(cases),17)
        self.assertEqual(sum(v[core.FLAG] for v in cases.values()),8)
        self.assertEqual(sum(len(v['sources']) for v in cases.values()),9)
        for n,v in cases.items():
            if n not in self.events:
                self.assertEqual(v['status'],'STOP');self.assertFalse(v[core.FLAG])
                self.assertIn('no same-snapshot alias borrowing',v['reason'])
            elif not self.trees[n]['geometric_tree_complete_restricted_CPU_only']:
                self.assertEqual(v['reason'],self.trees[n]['reason'])
                self.assertFalse(v[core.FLAG]);self.assertEqual(v['sources'],[])
            else:
                self.assertEqual(v['certificate_sha256'],self.trees[n]['certificate_sha256'])
                self.assertTrue(v[core.FLAG]);self.assertEqual(v['status'],'MATCH_RETAINED_CPU_TREE')
    def test_preserve_14source_STOP_5products_no_field_or_native_promotion(self):
        cases=DATA['audit']['cases']
        self.assertEqual(sum(sum(v['retained_source_product_evaluated']) for v in cases.values()),5)
        self.assertEqual(sum(sum(x is not None for x in v['retained_source_numerical_STOP_reasons']) for v in cases.values()),14)
        for n,v in cases.items():
            self.assertEqual(v['retained_source_product_row_sha256s'],[allocation.digest(s) for s in self.products[n]['sources']])
            self.assertEqual(v['retained_source_numerical_STOP_reasons'],[None if s['source_product_evaluated'] else s['reason'] for s in self.products[n]['sources']])
            for k in core.FALSE:self.assertIs(v[k],False)
        for k in core.FALSE:self.assertIs(DATA['audit'][k],False)
        self.assertEqual(DATA['audit']['inherited_pins_verified'],223)
        for k in ('new_ray_traces','new_barycentric_evaluations','new_products','new_trigonometry'):self.assertEqual(DATA['audit'][k],0)
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
    def test_rehashed_forged_tree_terminal_lineage_selectors_rejected(self):
        for path,value,label in [
            (['certificate','trees',0,2,'children'],['s:extra'],'nonabsorbing terminal'),
            (['certificate','trees',0,1,'children'],[],'pruned mirror child'),
            (['certificate','trees',0,1,'parent'],'other:root','foreign parent'),
            (['certificate','trees',0,0,'direction_sign'],True,'bool sign'),
            (['certificate','trees',0,1,'arrival_primitive_id'],0,'changed mirror selector'),
            (['certificate','trees',0,0,'next_primitive_partition',1,'distance_BU'],[[1,8],[1,8]],'changed root enclosure'),
            (['certificate','trees',0,0,'next_primitive_partition',0,'owner'],True,'bool primitive owner'),
            (['certificate','source_order'],['other'],'foreign source order')]:
            self.reject('tree',path,value,label,True)
    def test_event_INPUT_ABI_departure_partition_type_and_radius_rejected(self):
        for path,value,label in [
            (['input_packet_sha256'],'0'*64,'foreign packet'),
            (['word_ABI_sha256'],'0'*64,'foreign ABI'),
            (['source_order'],['other'],'source swap'),
            (['sources',0,'segments',0,'owner'],False,'bool owner'),
            (['sources',0,'segments',0,'primitive_id'],True,'bool selector'),
            (['sources',0,'segments',1,'same_owner_departures_skipped'],[True],'bool skip alias'),
            (['sources',0,'segments',0,'segment_interval_words',0],[0]*16,'changed endpoint'),
            (['sources',0,'departure_certificate','source_id'],'other','foreign departure source'),
            (['sources',0,'departure_certificate','input_packet_sha256'],'0'*64,'foreign departure packet')]:
            self.reject('events',path,value,label)
        self.reject('geometry',['word_ABI','triangles',0,'X_radius_scaled'],1,'silently expanded radius')
        self.reject('geometry',['scene_snapshot','sources',0,'field_reim'],[1.0,0.0],'foreign ORIGINAL field snapshot')
    def test_public_accepts_ONLY_case_selection_and_pins(self):
        for names,model,label in [([],core.MODEL,'empty'),(['positive','positive'],core.MODEL,'duplicate'),(['missing'],core.MODEL,'unknown'),(['positive'],'foreign','foreign model')]:
            with self.assertRaises(ValueError):core.audit_tree_lineage_HOST(names,model=model)
            DATA['rejections'].append({'target':'public','names':names,'model':model,'label':label})
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TreeLineageTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
