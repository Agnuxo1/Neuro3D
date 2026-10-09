"""CPU Torch controls; these do not constitute any GPU execution evidence."""
import numpy as np
import unittest
from Blender.tests.test_affine_geometry_network_v1 import network
from Blender.blender_lab.torch_geometry_backend_v1 import TorchGeometryBackend


class TorchGeometryTests(unittest.TestCase):
    def test_complex_forward_manual_jacobian_and_functional_autograd_control(self):
        import torch
        torch.set_num_threads(1)
        net=network();backend=TorchGeometryBackend(net,'cpu');d=[.003,-.005]
        inputs=np.asarray([[1,.2j,.3],[.2,1,.4j]],dtype=np.complex128)
        packed=backend.upload(backend.prepare(d));tensor=torch.tensor(inputs,dtype=torch.complex128)
        own=backend.forward(tensor,packed);reference=net.forward(inputs,d)
        for name in ('fields','powers','field_jacobian','power_jacobian'):
            np.testing.assert_allclose(own[name].numpy(),reference[name],atol=2e-12,rtol=2e-12)
        weights=torch.tensor([[1.,-.3,.7],[.2,.6,-.1]],dtype=torch.float64)
        fields,gradient=backend.autograd_reference(tensor,packed,weights)
        np.testing.assert_allclose(fields.detach().numpy(),reference['fields'],atol=2e-12)
        expected=np.einsum('nc,ncp->p',weights.numpy(),reference['power_jacobian'])
        np.testing.assert_allclose(gradient.numpy(),expected,atol=2e-12,rtol=2e-12)

    def test_wrong_precision_or_missing_source_rejected(self):
        import torch
        backend=TorchGeometryBackend(network(),'cpu');packed=backend.upload(backend.prepare([0,0]))
        for tensor in (torch.ones((1,3),dtype=torch.complex64),torch.ones((1,2),dtype=torch.complex128)):
            with self.assertRaises(ValueError):backend.forward(tensor,packed)


if __name__=='__main__':unittest.main()
