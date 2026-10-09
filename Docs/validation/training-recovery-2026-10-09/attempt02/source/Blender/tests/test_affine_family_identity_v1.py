import copy,unittest
from fractions import Fraction as F
from Blender.tests.test_affine_box_audit_v1 import fixture
from Blender.blender_lab.affine_box_audit_v1 import IndependentAffineBox
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
from Blender.blender_lab.affine_family_identity_v1 import certify_affine_identity,require_box_membership

class FamilyIdentityControls(unittest.TestCase):
    def test_independent_exact_identity_and_tampered_phase_coefficient(self):
        scene,graph,parameters=fixture();ind=IndependentAffineBox(scene,graph,parameters);net=AffineGeometryNetwork(scene,graph,parameters)
        self.assertEqual(certify_affine_identity(ind,net)['status'],'CERTIFIED_EXACT_AFFINE_EXPRESSION_IDENTITY')
        broken=copy.deepcopy(net);broken.segment_jets[0]=tuple(v+1 for v in broken.segment_jets[0])
        with self.assertRaises(ValueError):certify_affine_identity(ind,broken)
        broken=copy.deepcopy(net);broken.segment_jets.pop()
        with self.assertRaises(ValueError):certify_affine_identity(ind,broken)

    def test_exact_membership_rejects_next_represented_value(self):
        import math
        box=[(F(-1),F(1))]
        self.assertEqual(require_box_membership(box,[1.0])['parameters'],1)
        with self.assertRaises(ValueError):require_box_membership(box,[math.nextafter(1.0,math.inf)])
        with self.assertRaises(ValueError):require_box_membership(box,[])

if __name__=='__main__':unittest.main()
