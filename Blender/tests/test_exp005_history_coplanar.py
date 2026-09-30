import copy
from fractions import Fraction as F
from itertools import permutations
import unittest
from exp005_history_coplanar_review import replay,old,new
from exp005_history_lineage_audit import fixture


class CoplanarHistory(unittest.TestCase):
    def test_retained_peer_refutation_and_original_gates(self):
        r=replay();self.assertEqual(len(r['cases']),2)
        self.assertEqual(len(r['old_negatives_rejected']),8)
        self.assertFalse(r['cases'][1]['v2']['native_exemption_allowed'])

    def test_closed_half_line_clipping_orientation_and_axes(self):
        # Analytic triangle 2<=x<=4, |y|<=(4-x)/2 in each coordinate plane.
        tri=[(2,-1),(2,1),(4,0)]
        cases=[((0,0),(1,0),True),((0,2),(1,0),False),((0,1),(1,0),True),
               ((0,0),(-1,0),False),((3,0),(1,0),True),((2,1),(0,1),True),
               ((0,1+F(1,2**30)),(1,0),False),((0,1-F(1,2**30)),(1,0),True)]
        for drop in range(3):
            keep=[i for i in range(3) if i!=drop]
            def lift(v):
                out=[F(0)]*3
                for i,x in zip(keep,v):out[i]=F(x)
                return tuple(out)
            for vertices in permutations(tri):
                for o,d,expected in cases:
                    with self.subTest(drop=drop,vertices=vertices,o=o,d=d):
                        self.assertEqual(new.coplanar_ray_touches(lift(o),lift(d),tuple(lift(v) for v in vertices)),expected)

    def test_actual_coplanar_contact_still_rejected(self):
        tri=tuple(new.vec(v) for v in ((2,-1,0),(2,1,0),(4,0,0)))
        for o,d in (((0,0,0),(1,0,0)),((2,1,0),(0,1,0)),((3,0,0),(1,0,0))):
            with self.assertRaisesRegex(ValueError,'coplanar triangle contact'):
                new.intersection(new.vec(o),new.vec(d),tri)
        self.assertIsNone(new.intersection(new.vec((0,2,0)),new.vec((1,0,0)),tri))

    def test_positive_gap_and_source_ancestry_not_relaxed(self):
        s,r=fixture(True);gap=2**-30
        s['objects']['T']['vertices_world_BU']=[[1+gap,y,z] for _,y,z in s['objects']['T']['vertices_world_BU']]
        s['objects']['T']['mode_origin_BU']=[1+gap,0,0];sha,_=new.scene_binding(s)
        for node in r:node['snapshot_sha256']=sha
        r[3]['origin_BU']=[1+gap,0,0]
        self.assertEqual(new.validate_history(s,r)['records'][3]['t_parameter_exact'],[1,2**30])
        s,r=fixture();s['sources'].append({**s['sources'][0],'id':'s2'});sha,_=new.scene_binding(s)
        for node in r:node['snapshot_sha256']=sha
        root=copy.deepcopy(r[0]);root.update(id=3,source_id='s2');r.insert(1,root);r[2]['source_id']='s2'
        with self.assertRaises(ValueError):new.validate_history(s,r)

    def test_new_version_does_not_mutate_v1_or_inputs(self):
        s,r=fixture();before=copy.deepcopy((s,r));result=new.validate_history(s,r)
        self.assertEqual((s,r),before);self.assertEqual(result['schema'],'exp005-history-lineage-CPU-v2')
        self.assertEqual(old.validate_history(s,r)['schema'],'exp005-history-lineage-CPU-v1')


if __name__=='__main__':unittest.main()
