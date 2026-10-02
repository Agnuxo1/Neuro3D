"""New rational domain proof tests, retained producers never executed."""
import base64,hashlib,itertools,json,struct,sys,unittest
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_scene_parameter_domain_HOST_v1 as core
DATA={}
class DomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.old,cls.argument,cls.pins=core.load_retained()
        cls.before={n:core.allocation.digest(p) for n,p in cls.packets.items()}
        DATA['audit']=core.audit_scene_parameter_domain_HOST(list(cls.packets),model=core.MODEL)
        DATA['primitives']=[];DATA['rejections']=[]
        specs=[
          ([[4,1],[5,1]],[[0,1],[1,1]],[[-3,1],[-2,1]],[[0,1],[1,1]],[[1,1],[2,1]],1),
          ([[-5,1],[-4,1]],[[-1,1],[0,1]],[[2,1],[3,1]],[[-1,1],[0,1]],[[1,1],[2,1]],-1),
          ([[1,2**80],[1,2**80]],[[0,1],[0,1]],[[-1,1],[-1,1]],[[0,1],[0,1]],[[1,1],[1,1]],1),
          ([[0,1],[0,1]],[[0,1],[0,1]],[[-1,1],[-1,1]],[[0,1],[0,1]],[[1,1],[1,1]],1),
          ([[0,1],[1,1]],[[0,1],[0,1]],[[-1,1],[-1,1]],[[0,1],[0,1]],[[1,1],[1,1]],1),
          ([[4,1],[4,1]],[[0,1],[0,1]],[[2,1],[2,1]],[[0,1],[0,1]],[[1,1],[1,1]],1),
          ([[4,1],[4,1]],[[0,1],[0,1]],[[5,1],[5,1]],[[0,1],[0,1]],[[1,1],[1,1]],1)]
        for m,s,d,r,w,sg in specs:
            proof=core.domain_image(m,s,d,r,w,direction_sign=sg,model=core.MODEL)
            DATA['primitives'].append({'inputs':{'M':m,'S':s,'D':d,'R':r,'wavelength':w,'sign':sg},'proof':proof})
    def test_five_fresh_domains_and_14_stops(self):
        a=DATA['audit'];self.assertEqual(a['inherited_pins_verified'],263)
        self.assertEqual(a['restricted_coordinate_domains_proved'],5);self.assertEqual(a['retained_unit_STOPs'],14)
        self.assertEqual(len(a['cases']),17)
        for n,c in a['cases'].items():
            for s,old in zip(c['sources'],self.old['cases'][n]['sources']):
                self.assertEqual(s['source_id'],old['source_id'])
                self.assertEqual(s['retained_argument_rectangle_source_sha256'],core.allocation.digest(old))
                self.assertEqual(s['restricted_coordinate_box_to_parameter_rectangle_proved'],old['rectangle_evaluated'])
                self.assertEqual(s['retained_unit_polynomial_charge_fits'],old['retained_unit_polynomial_charge_fits'])
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
                if old['rectangle_evaluated']:
                    p=s['restricted_domain_proof']
                    self.assertTrue(p['ORIGINAL_inside_coordinate_box'])
                    self.assertFalse(p['radii_enlarged'])
                    self.assertEqual(p['uniform_affine_selector_proof']['same_D_coefficient_in_total_reference'],0)
                else:self.assertEqual(s['reason'],old['reason'])
        self.assertFalse(a['cases']['two_sources']['sources'][1]['restricted_coordinate_box_to_parameter_rectangle_proved'])
        self.assertEqual(self.before,{n:core.allocation.digest(p) for n,p in self.packets.items()})
    def test_shared_D_cancellation_two_signs_thin_gap_and_contact(self):
        self.assertEqual([v['proof']['restricted_shared_plane_selector_proved'] for v in DATA['primitives']],[True,True,True,False,False,False,False])
        p=DATA['primitives'][0]
        other=core.domain_image(p['inputs']['M'],p['inputs']['S'],[[-6,1],[-2,1]],p['inputs']['R'],p['inputs']['wavelength'],direction_sign=1,model=core.MODEL)
        self.assertEqual(other['effective_reference_length_interval'],p['proof']['effective_reference_length_interval'])
        self.assertNotEqual(other['geometric_length_interval'],p['proof']['geometric_length_interval'])
    def test_affine_full_box_extrema_exact_not_corner_RN_claim(self):
        for v in DATA['primitives']:
            p=v['proof'];i=v['inputs'];sg=i['sign']
            values=[]
            for M,S,D,R,W in itertools.product(*[[F(*x) for x in i[k]] for k in ('M','S','D','R','wavelength')]):
                values.append((sg*(2*M-S-D),sg*(D-R),sg*(2*M-S-R),W))
            for j,key in enumerate(('geometric_length_interval','reference_correction_interval','effective_reference_length_interval','wavelength_interval')):
                self.assertEqual(p[key],[core.pair(min(x[j] for x in values)),core.pair(max(x[j] for x in values))])
    def test_projection_boundaries_and_degenerate(self):
        a=[[0,0],[4,0],[0,4]]
        specs=[([1,1],'strict_interior'),([0,0],'boundary_FAIL'),([4,4],'miss')]
        DATA['projection_controls']=[]
        for point,kind in specs:
            q=core.projection(a,point);self.assertEqual(q['classification'],kind)
            DATA['projection_controls'].append({'vertices':a,'point':point,'proof':q})
        q=core.projection([[0,0],[1,0],[2,0]],[1,0])
        self.assertEqual(q['classification'],'degenerate_FAIL')
        DATA['projection_controls'].append({'vertices':[[0,0],[1,0],[2,0]],'point':[1,0],'proof':q})
    def test_malformed_contract_and_scene_override_rejected(self):
        def reject(label,fn,exc=ValueError):
            with self.assertRaises(exc) as caught:fn()
            DATA['rejections'].append({'label':label,'reason':str(caught.exception)})
        valid=[[0,1],[1,1]];wave=[[1,1],[2,1]]
        for names in ([],['positive','positive'],['unknown'],[True]):
            reject('names_'+str(names),lambda names=names:core.audit_scene_parameter_domain_HOST(names,model=core.MODEL))
        for key,v in [('packet',{}),('radii',[1,1]),('cap',[1,1]),('certificate',True)]:
            reject('caller_'+key,lambda key=key,v=v:core.audit_scene_parameter_domain_HOST(['positive'],model=core.MODEL,**{key:v}),TypeError)
        for sign in (True,0,2):
            reject('sign_'+str(sign),lambda sign=sign:core.domain_image(valid,valid,valid,valid,wave,direction_sign=sign,model=core.MODEL))
        reject('model',lambda:core.domain_image(valid,valid,valid,valid,wave,direction_sign=1,model='other'))
        reject('unordered',lambda:core.domain_image([[1,1],[0,1]],valid,valid,valid,wave,direction_sign=1,model=core.MODEL))
        reject('wavezero',lambda:core.domain_image(valid,valid,valid,valid,valid,direction_sign=1,model=core.MODEL))
        for w in (True,-1,2**32,1,0x7f800000):
            reject('word_'+str(w),lambda w=w:core.decode32(w))
        reject('negative_radius',lambda:core.interval([0,0],[0xffffffff]*16))
        reject('ORIGINALbool',lambda:core.scaled_original(True))
        reject('ORIGINALnan',lambda:core.scaled_original(float('nan')))
    def test_modified_INPUT_and_receipt_fail_closed(self):
        def reject(label,fn):
            with self.assertRaises(ValueError) as caught:fn()
            DATA['rejections'].append({'label':label,'reason':str(caught.exception)})
        n='positive';packet=self.packets[n];ctx=self.old['cases'][n]['context']
        src=self.old['cases'][n]['sources'][0];ref=self.argument[n]['upstream']['upstream']['sources'][0]['reference']
        for label,role,mut in [
          ('wrongYZ','triangles',lambda w:w.__setitem__(3,0)),
          ('subnormal','triangles',lambda w:w.__setitem__(1,1)),
          ('negative_radius','triangles',lambda w:w.__setitem__(34,0xffffffff)),
          ('wrongowner','triangles',lambda w:w.__setitem__(0,1)),
          ('directionzero','sources',lambda w:w.__setitem__(6,0)),
          ('refbits','reference',lambda w:w.__setitem__(2,0)),
          ('lambda_zero','wavelength',lambda w:w.__setitem__(0,0))]:
            p=deepcopy(packet);raw=base64.b64decode(p['buffers_base64'][role]);words=list(struct.unpack('<'+'I'*(len(raw)//4),raw));mut(words)
            raw=struct.pack('<'+'I'*len(words),*words);p['buffers_base64'][role]=base64.b64encode(raw).decode()
            p['manifest']['buffers'][role]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            c=dict(ctx,input_packet_sha256=core.allocation.digest(p))
            reject('mutated_'+label,lambda p=p,c=c:core.derive_restricted_domain(p,c,0,ref,src['parameter_branch'],ref['geometry']))
        p=deepcopy(packet);snap=json.loads(base64.b64decode(p['buffers_base64']['original_scene_json']))
        snap['sources'][0]['position_BU'][0]=100.0;raw=core.allocation.canon(snap)
        p['buffers_base64']['original_scene_json']=base64.b64encode(raw).decode();p['manifest']['buffers']['original_scene_json']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        meta=json.loads(base64.b64decode(p['buffers_base64']['input_metadata_json']));meta['original_snapshot_sha256']=hashlib.sha256(raw).hexdigest()
        raw=core.allocation.canon(meta);p['buffers_base64']['input_metadata_json']=base64.b64encode(raw).decode();p['manifest']['buffers']['input_metadata_json']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        c=dict(ctx,input_packet_sha256=core.allocation.digest(p))
        reject('mutated_ORIGINALoutside',lambda:core.derive_restricted_domain(p,c,0,ref,src['parameter_branch'],ref['geometry']))
        # Explicit profile repair control: every face must share the SAME ORIGINAL plane.
        n2='nonexact_geometry_phase_PASS';p=deepcopy(self.packets[n2])
        snap=json.loads(base64.b64decode(p['buffers_base64']['original_scene_json']))
        snap['objects']['M']['vertices_world_BU'][3][0]=0.10000000000000002
        raw=core.allocation.canon(snap);p['buffers_base64']['original_scene_json']=base64.b64encode(raw).decode()
        p['manifest']['buffers']['original_scene_json']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        meta=json.loads(base64.b64decode(p['buffers_base64']['input_metadata_json']));meta['original_snapshot_sha256']=hashlib.sha256(raw).hexdigest()
        raw=core.allocation.canon(meta);p['buffers_base64']['input_metadata_json']=base64.b64encode(raw).decode()
        p['manifest']['buffers']['input_metadata_json']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        c=dict(self.old['cases'][n2]['context'],input_packet_sha256=core.allocation.digest(p))
        s2=self.old['cases'][n2]['sources'][0];r2=self.argument[n2]['upstream']['upstream']['sources'][0]['reference']
        reject('mutated_ORIGINALnonshared_face',lambda:core.derive_restricted_domain(p,c,0,r2,s2['parameter_branch'],r2['geometry']))
        target=core.io.ROOT/core.PREVIOUS;original=Path.read_bytes;bad=original(target)+b' '
        with patch.object(Path,'read_bytes',lambda p:bad if p==target else original(p)):
            reject('changed_predecessor',lambda:core.audit_scene_parameter_domain_HOST(['positive'],model=core.MODEL))
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(DomainTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
