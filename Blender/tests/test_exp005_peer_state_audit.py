"""CPU audit fixture/oracle gates, no peer execution or torch import."""
import math
import unittest
from exp005_peer_state_audit import fixture, evaluate_fields
from exp005_triangle_oracle import trace_scene


class PeerStateAuditTests(unittest.TestCase):
    def test_simple_mirror_reference_is_three_units_with_phase(self):
        for w in (.125, .14):
            oracle = trace_scene(fixture(w), max_rays=4)
            expected = -complex(math.cos(6*math.pi/w), math.sin(6*math.pi/w))
            self.assertLess(abs(oracle['fields']['D']-expected), 1e-12)
            self.assertEqual(oracle['rays'], 2)
            self.assertEqual(oracle['paths'][0]['length_BU'], 3.)

    def test_wrong_lambda_may_pass_power_but_fails_complex_field(self):
        scene = fixture(.14)
        wrong = trace_scene(fixture(.125), max_rays=4)['fields']['D']
        row = evaluate_fields([scene], [[wrong.real, wrong.imag]])[0]
        self.assertGreater(row['complex_error'], 1.)
        self.assertLess(row['power_error'], 1e-12)

    def test_invalid_readbacks_fail_closed(self):
        for values in ([], [[float('nan'), 0]], [[1]], [[float('inf'), 0]]):
            with self.assertRaises(ValueError): evaluate_fields([fixture(.125)], values)


if __name__ == '__main__': unittest.main()
