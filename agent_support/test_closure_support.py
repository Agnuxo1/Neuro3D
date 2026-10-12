"""Behavioral regressions for geometry, enclosures, coherence, and evidence."""
from __future__ import annotations

from fractions import Fraction as F
import hashlib
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from closure_reference import (Interval, rational, sqrt_interval, segment_length,
    pi_interval, phase_from_length, unit_phasor, coherent_field, modal_power,
    certified_argmax, field_to_power_error, exact_first_hit)
from closure_coherent import (coherent_sum, greedy_order, exact_roundoff_report,
    pack_complex64, unpack_complex64, first_trace_divergence, compile_operator, apply_operator)
from closure_statistics import (paired_bootstrap, corrected_resampled_interval,
    holm_adjust, comparison_label, exact_mcnemar)
from closure_wave import (gaussian_1d, angular_spectrum_1d, modal_amplitude,
    circular_phase_difference, observed_order)
from closure_evidence import check_pins, verify_closure
from extract_support import extract, materialize


def triangle(z, pid="0", object_id="plane"):
    """Build a large triangle crossed by the positive-z ray through the origin."""
    return {"primitive_id": pid, "object_id": object_id,
            "vertices": [(-2, -1, z), (2, -1, z), (0, 2, z)]}


class IntervalTests(unittest.TestCase):
    def test_binary64_and_hex_decode_identically(self):
        self.assertEqual(rational(0.1), rational(0.1.hex()))
        self.assertNotEqual(rational(0.1), F(1, 10))

    def test_square_handles_zero_crossing(self):
        self.assertEqual(Interval(-2, 1).square(), Interval(0, 4))
        with self.assertRaises(ValueError):
            Interval.point(1)/Interval(-1, 1)

    def test_serialized_bounds_remain_outward_for_large_denominators(self):
        original = Interval(-F(1, 10**5000), F(1, 10**5000))
        lo, hi = map(F, original.outward_wire())
        self.assertLessEqual(lo, original.lo)
        self.assertGreaterEqual(hi, original.hi)

    def test_sqrt_uses_verified_endpoint_inequalities(self):
        b = sqrt_interval(Interval.point(2))
        self.assertLessEqual(b.lo*b.lo, 2)
        self.assertGreaterEqual(b.hi*b.hi, 2)
        self.assertEqual(sqrt_interval(Interval.point(4)), Interval.point(2))

    def test_coordinate_uncertainty_reaches_segment_length(self):
        b = segment_length((0, 0, 0), (Interval(3, F(31, 10)), 4, 0))
        self.assertTrue(b.contains(5))
        self.assertGreater(b.hi, 5)

    def test_machin_pi_with_an_independent_decimal_bracket(self):
        decimal = "3.141592653589793238462643383279502884197169399375105820974944"
        lower = F(decimal)
        upper = lower+F(1, 10**60)
        p = pi_interval(256)
        self.assertGreater(p.lo, lower)
        self.assertLess(p.hi, upper)

    def test_large_cycle_reduction_preserves_quarter_turn(self):
        phase = phase_from_length(Interval.point(F(10**30)+F(1, 4)), Interval.point(1))
        c, s = unit_phasor(phase)
        self.assertTrue(c.contains(0))
        self.assertTrue(s.contains(1))
        self.assertLess(c.radius, F(1, 10**20))

    def test_destructive_interference_is_not_a_missing_branch(self):
        amplitude = (Interval.point(1), Interval.point(0))
        field = coherent_field([(amplitude, Interval.point(0)), (amplitude, pi_interval())])
        power = modal_power(field)
        self.assertTrue(power.contains(0))
        self.assertLess(power.hi, F(1, 10**20))

    def test_overlapping_decisions_remain_unknown(self):
        self.assertIsNone(certified_argmax([Interval(0, 1), Interval(0, 1)]))
        self.assertEqual(certified_argmax([Interval(2, 3), Interval(0, 1)]), 0)
        self.assertEqual(field_to_power_error(F(2), F(1, 10)), F(41, 100))


class GeometryTests(unittest.TestCase):
    def test_ultrathin_positive_hit_is_not_skipped(self):
        gap = F(1, 2**80)
        hit = exact_first_hit((0, 0, 0), (0, 0, 1), [triangle(gap)])
        self.assertEqual(hit["status"], "HIT")
        self.assertEqual(hit["parameter"], gap)

    def test_shared_seam_keeps_both_primitive_identities(self):
        a = {"primitive_id": "a", "object_id": "square", "vertices": [(-1, -1, 1), (1, -1, 1), (1, 1, 1)]}
        b = {"primitive_id": "b", "object_id": "square", "vertices": [(-1, -1, 1), (1, 1, 1), (-1, 1, 1)]}
        hit = exact_first_hit((0, 0, 0), (0, 0, 1), [a, b])
        self.assertEqual(hit["primitive_ids"], ["a", "b"])
        self.assertEqual(hit["status"], "HIT")

    def test_distinct_tie_and_contact_remain_unknown(self):
        tie = exact_first_hit((0, 0, 0), (0, 0, 1), [triangle(1, "a", "a"), triangle(1, "b", "b")])
        self.assertEqual(tie["reason"], "DISTINCT_SURFACE_TIE")
        self.assertEqual(exact_first_hit((0, 0, 0), (0, 0, 1), [triangle(0)])["reason"], "LAUNCH_CONTACT")

    def test_nearest_order_survives_below_float_ulp(self):
        near = F(1)+F(1, 2**80)
        far = F(1)+F(2, 2**80)
        hit = exact_first_hit((0, 0, 0), (0, 0, 1), [triangle(far, "far"), triangle(near, "near")])
        self.assertEqual(hit["primitive_ids"], ["near"])

    def test_coplanar_and_degenerate_queries_are_rejected(self):
        hit = exact_first_hit((0, 0, 1), (1, 0, 0), [triangle(1)])
        self.assertEqual(hit["reason"], "COPLANAR_QUERY")
        bad = {"primitive_id": "x", "object_id": "x", "vertices": [(0, 0, 1)]*3}
        self.assertEqual(exact_first_hit((0, 0, 0), (0, 0, 1), [bad])["reason"], "DEGENERATE_TRIANGLE")


class CoherenceTests(unittest.TestCase):
    def test_fsum_recovers_a_cancelled_small_component(self):
        terms = [complex(1e16, 1e16), 1+2j, complex(-1e16, -1e16)]
        self.assertEqual(coherent_sum(terms), 1+2j)
        self.assertEqual(exact_roundoff_report(terms)["observed_reduction_error_L1_exact"], "0")
        self.assertNotEqual(coherent_sum(terms, "naive"), 1+2j)

    def test_nonfinite_or_overflow_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            coherent_sum([complex(float("nan"), 0)])
        for method in ("naive", "pairwise"):
            with self.assertRaises(ValueError):
                coherent_sum([1e308, 1e308], method)

    def test_greedy_is_only_a_permutation(self):
        terms = [3+4j, -3-4j, 1j, -1j]
        order = greedy_order(terms)
        self.assertEqual(sorted(order), list(range(len(terms))))
        self.assertEqual(coherent_sum(terms), coherent_sum(terms[i] for i in order))

    def test_packet_roundtrip_is_bit_exact(self):
        packet = pack_complex64([complex(-0.0, 0.0), complex(0.1, -2.0)])
        self.assertEqual(pack_complex64(unpack_complex64(packet)), packet)
        with self.assertRaises(ValueError):
            unpack_complex64(packet[:-1])

    def test_trace_localizes_the_first_divergence(self):
        a = [{"state_id": 1, "components": {"local": [1, 0]}}, {"state_id": 2, "components": {"local": [2, 0]}}]
        b = [{"state_id": 1, "components": {"local": [1, 0]}}, {"state_id": 2, "components": {"local": [2.1, 0]}}]
        self.assertEqual(first_trace_divergence(a, b, 1e-11)["state_id"], 2)

    def test_compiled_operator_uses_transpose_not_adjoint(self):
        u = np.array([[1j, 2], [3, -1j]], dtype=np.complex128)
        compiled = compile_operator(lambda v: u@v, 2)
        x = np.array([[1+1j, 2-1j]], dtype=np.complex128)
        np.testing.assert_allclose(apply_operator(compiled, x), (u@x.T).T, atol=1e-14)


class StatisticsTests(unittest.TestCase):
    def test_bootstrap_is_paired_and_reproducible(self):
        a, b = [0.8, 0.9, 0.7], [0.7, 0.8, 0.6]
        self.assertEqual(paired_bootstrap(a, b, draws=1000), paired_bootstrap(a, b, draws=1000))
        self.assertAlmostEqual(paired_bootstrap(a, b, draws=1000)["mean_difference"], 0.1)

    def test_overlap_correction_increases_standard_error(self):
        a, b = [0.81, 0.92, 0.73, 0.84], [0.8]*4
        small = corrected_resampled_interval(a, b, test_train_ratio=0.01)
        large = corrected_resampled_interval(a, b, test_train_ratio=0.25)
        self.assertGreater(large["standard_error"], small["standard_error"])

    def test_multiplicity_and_equivalence(self):
        self.assertEqual(holm_adjust([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
        self.assertEqual(comparison_label([0.001, 0.009], 0.01), "EQUIVALENT_WITHIN_MARGIN")
        self.assertEqual(comparison_label([-0.1, -0.03], 0.01), "NEGATIVE_DIFFERENCE")

    def test_nonfinite_margin_and_unmatched_units_are_rejected(self):
        with self.assertRaises(ValueError):
            comparison_label([0, 1], float("nan"))
        with self.assertRaises(ValueError):
            paired_bootstrap([0.8, 0.7], [0.8])

    def test_exact_mcnemar_retains_pairing(self):
        p = exact_mcnemar([True]*10, [False]*10)["p_two_sided"]
        self.assertEqual(p, 2/1024)
        self.assertEqual(exact_mcnemar([True], [True])["p_two_sided"], 1)


class WaveTests(unittest.TestCase):
    def test_waist_control_and_paraxial_norm(self):
        y = np.linspace(-20, 20, 8192, endpoint=False)
        dy = y[1]-y[0]
        initial = gaussian_1d(y, 0, 0.1, 0.8)
        np.testing.assert_allclose(initial, np.exp(-(y/0.8)**2), atol=1e-14)
        propagated = gaussian_1d(y, 10, 0.1, 0.8)
        self.assertAlmostEqual(float(np.vdot(initial, initial).real*dy), float(np.vdot(propagated, propagated).real*dy), places=11)

    def test_spectrum_identity_and_declared_paraxial_agreement(self):
        y = np.linspace(-20, 20, 8192, endpoint=False)
        dy = y[1]-y[0]
        initial = gaussian_1d(y, 0, 0.1, 0.8)
        np.testing.assert_allclose(angular_spectrum_1d(initial, dy, 0, 0.1), initial, atol=1e-14)
        actual = angular_spectrum_1d(initial, dy, 2, 0.1)
        approximate = gaussian_1d(y, 2, 0.1, 0.8)
        self.assertLess(float(np.max(np.abs(actual-approximate))), 1e-4)

    def test_mode_projection_and_dark_phase(self):
        g = np.array([1, 2, 3], dtype=complex)
        self.assertAlmostEqual(abs(modal_amplitude((2+3j)*g, g, 0.1)-(2+3j)), 0)
        self.assertIsNone(circular_phase_difference(0, 1))
        self.assertAlmostEqual(circular_phase_difference(1j, 1), math.pi/2)

    def test_convergence_diagnostic_does_not_claim_a_proof(self):
        report = observed_order(1.04, 1.01, 1.0025, 2)
        self.assertAlmostEqual(report["order"], 2)
        self.assertEqual(observed_order(1, 1, 1, 2)["status"], "INCONCLUSIVE")


class EvidenceTests(unittest.TestCase):
    def test_changed_bytes_and_escapes_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/"receipt.json").write_bytes(b"{}")
            pins = {"receipt.json": hashlib.sha256(b"{}").hexdigest()}
            self.assertEqual(check_pins(root, pins)[0]["status"], "PASS")
            (root/"receipt.json").write_bytes(b"{ }")
            self.assertEqual(check_pins(root, pins)[0]["status"], "FAIL")
            self.assertEqual(check_pins(root, {"../secret": "0"*64})[0]["status"], "BLOCKED")

    def test_unresolved_fronts_cannot_be_complete(self):
        manifest = {"schema": "neuro3d.closure.manifest.v1", "objectives": [{"id": i, "state": "OPEN", "remaining": ["Independent evidence required"]} for i in range(1, 12)]}
        with tempfile.TemporaryDirectory() as directory:
            report = verify_closure(Path(directory), manifest)
        self.assertTrue(report["integrity_pass"])
        self.assertFalse(report["all_selected_fronts_pass"])

    def test_malformed_front_identifiers_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                verify_closure(Path(directory), {"schema": "neuro3d.closure.manifest.v1", "objectives": [{"id": None}]})

    def test_extraction_rejects_overwrite_and_path_traversal(self):
        text = '<!-- CODEFILE: agent_support/a.py -->\n```python\nprint("ready")\n```'
        blocks = extract(text)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertTrue(materialize(blocks, root)[0]["created"])
            self.assertFalse(materialize(blocks, root)[0]["created"])
            (root/"agent_support/a.py").write_text("different")
            with self.assertRaises(ValueError):
                materialize(blocks, root)
        with self.assertRaises(ValueError):
            extract(text.replace("agent_support/a.py", "../a.py"))


if __name__ == "__main__":
    unittest.main()
