import unittest
import torch
from Blender.blender_lab.torch_training_arithmetic_v1 import cross_entropy, adam_proposal


class ManualTrainingControl(unittest.TestCase):
    def test_chain_rule_against_independent_autograd_loss(self):
        generator = torch.Generator().manual_seed(109)
        baseline = torch.rand((7, 5), generator=generator, dtype=torch.float64)
        jac = torch.randn((7, 5, 3), generator=generator, dtype=torch.float64)
        labels = torch.tensor([0, 1, 2, 0, 2, 1, 0], dtype=torch.int64)
        parameter = torch.zeros(3, dtype=torch.float64, requires_grad=True)
        perturbed = baseline + torch.einsum('ncp,p->nc', jac, parameter)
        reference = torch.nn.functional.cross_entropy(perturbed[:, [4, 0, 2]] / .07, labels)
        expected = torch.autograd.grad(reference, parameter)[0]
        loss, gradient = cross_entropy(baseline, jac, labels, [4, 0, 2], .07)
        self.assertLess(abs(loss.item() - reference.item()), 1e-13)
        self.assertLess(torch.max(torch.abs(gradient - expected)).item(), 1e-13)

    def test_zero_field_finite_and_invalid_labels_rejected(self):
        powers = torch.zeros((2, 3), dtype=torch.float64)
        jac = torch.zeros((2, 3, 4), dtype=torch.float64)
        labels = torch.tensor([0, 2], dtype=torch.int64)
        loss, gradient = cross_entropy(powers, jac, labels, [0, 1, 2], .02)
        self.assertAlmostEqual(loss.item(), __import__('math').log(3), places=14)
        self.assertTrue(torch.equal(gradient, torch.zeros(4, dtype=torch.float64)))
        with self.assertRaises(ValueError): cross_entropy(powers, jac, labels + 3, [0, 1, 2], .02)

    def test_adam_matches_independent_torch_optimizer_before_projection(self):
        parameter = torch.tensor([.03, -.02], dtype=torch.float64, requires_grad=True)
        initial = parameter.detach().clone(); center = torch.zeros_like(initial)
        first = torch.zeros_like(initial); second = torch.zeros_like(initial)
        own = initial.clone(); reference = torch.optim.Adam([parameter], lr=.0002)
        for step, gradient in enumerate(([.7, -.4], [-.3, .8], [.01, -.02]), 1):
            gradient = torch.tensor(gradient, dtype=torch.float64)
            parameter.grad = gradient; reference.step()
            own, first, second = adam_proposal(own, gradient, first, second, center, step, .0002, 1)
            self.assertLess(torch.max(torch.abs(own - parameter.detach())).item(), 1e-15)


if __name__ == '__main__':
    unittest.main()
