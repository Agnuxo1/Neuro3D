"""Regressions for the v2 successors: each v1 defect is reproduced, then corrected."""
from __future__ import annotations

from fractions import Fraction as F
import json
import math
from pathlib import Path
import random
import tempfile
import unittest

import numpy as np
from scipy.stats import norm

from closure_coherent import coherent_sum
from closure_reference import Interval, exact_first_hit, phase_from_length, pi_interval, unit_phasor
from closure_wave import angular_spectrum_1d, gaussian_1d, modal_amplitude
from closure_v2 import (coherent_field_v2, coherent_sum_v2, exact_first_hit_v2, tighten,
    unit_phasor_v2, verify_frontier)
from closure_limits import (detection_energy_per_mac, detector_loss, effective_rank, is_passive,
    landauer_energy, numerical_jacobian, photon_energy, project_passive, shot_noise_photons,
    spectral_norm, train_detector_classifier)
from closure_inference_v2 import eprocess_decision, paired_sign_eprocess, tost_paired
from closure_integrity import (commit_labels, extract_identifiers, resolve_identifiers,
    validate_experiment_record, verify_reveal)

HERE = Path(__file__).resolve().parent


def triangle(z, pid="0", object_id="plane"):
    return {"primitive_id": pid, "object_id": object_id, "vertices": [(-2, -1, z), (2, -1, z), (0, 2, z)]}


class ReductionAndEnclosureV2(unittest.TestCase):
    def test_fsum_overflow_contract(self):
        with self.assertRaises(OverflowError):
            coherent_sum([1e308, 1e308], "fsum")  # v1 defect reproduced
        for method in ("fsum", "pairwise", "naive"):
            with self.assertRaises(ValueError):
                coherent_sum_v2([1e308, 1e308], method)
        self.assertEqual(coherent_sum_v2([complex(1e16, 1e16), 1+2j, complex(-1e16, -1e16)]), 1+2j)

    def test_tighten_is_outward_and_bounded(self):
        rng = random.Random(3)
        for _ in range(200):
            a = F(rng.randint(-10**40, 10**40), rng.randint(1, 10**60))
            b = a+F(rng.randint(0, 10**9), 10**rng.randint(1, 30))
            t = tighten(Interval(a, b), 96)
            self.assertLessEqual(t.lo, a)
            self.assertGreaterEqual(t.hi, b)
            self.assertLessEqual(t.lo.denominator.bit_length(), 97)
            self.assertLessEqual(t.hi-t.lo, b-a+F(2, 2**96))

    def test_v1_endpoint_growth_is_bounded_in_v2(self):
        phase = phase_from_length(Interval.point(F(10**30)+F(1, 4)), Interval.point(1))
        c1, _ = unit_phasor(phase)
        self.assertGreater(c1.lo.denominator.bit_length(), 4000)  # v1 behaviour reproduced
        c2, s2 = unit_phasor_v2(phase)
        self.assertLessEqual(c2.lo.denominator.bit_length(), 161)
        self.assertTrue(c2.contains(0) and s2.contains(1))
        self.assertLess(c2.hi-c2.lo, F(1, 2**100))
        self.assertTrue(max(c1.lo, c2.lo) <= min(c1.hi, c2.hi))

    def test_unit_phasor_v2_matches_floating_reference(self):
        rng = random.Random(11)
        for _ in range(100):
            x = rng.uniform(-1e6, 1e6)
            ph = F.from_float(x)  # exact binary64 value, so math.cos(x) refers to the same argument
            c, s = unit_phasor_v2(Interval.point(ph))
            # libm cos/sin are within a few ulp of the exact value; the enclosure must contain it.
            slack = 4e-16
            self.assertTrue(float(c.lo)-slack <= math.cos(x) <= float(c.hi)+slack)
            self.assertTrue(float(s.lo)-slack <= math.sin(x) <= float(s.hi)+slack)
            self.assertLess(c.hi-c.lo, F(1, 2**100))

    def test_dark_field_and_sixty_four_paths_stay_small(self):
        amp = (Interval.point(1), Interval.point(0))
        dark = coherent_field_v2([(amp, Interval.point(0)), (amp, pi_interval())])
        power = dark[0].square()+dark[1].square()
        self.assertTrue(power.contains(0))
        self.assertLess(power.hi, F(1, 2**100))
        field = coherent_field_v2([(amp, Interval.point(F(k, 7))) for k in range(64)])
        exact = sum(complex(math.cos(k/7), math.sin(k/7)) for k in range(64))
        self.assertLess(abs(float(field[0].midpoint)-exact.real), 1e-12)
        self.assertLess(abs(float(field[1].midpoint)-exact.imag), 1e-12)
        self.assertLessEqual(field[0].hi.denominator.bit_length(), 161)


class FirstHitV2(unittest.TestCase):
    near = triangle(1, "near", "A")
    far_degenerate = {"primitive_id": "far", "object_id": "B", "vertices": [(0, 0, 50)]*3}
    behind_coplanar = {"primitive_id": "behind", "object_id": "C", "vertices": [(0, -1, -5), (0, 1, -5), (0, 0, -6)]}
    front_coplanar = {"primitive_id": "front", "object_id": "D", "vertices": [(0, -1, F(1, 2)), (0, 1, F(1, 2)), (0, 0, F(3, 4))]}

    def test_v1_masking_reproduced_and_corrected(self):
        o, d = (0, 0, 0), (0, 0, 1)
        self.assertEqual(exact_first_hit(o, d, [self.near, self.far_degenerate])["status"], "UNKNOWN")
        self.assertEqual(exact_first_hit(o, d, [self.near, self.behind_coplanar])["status"], "UNKNOWN")
        for blocker in (self.far_degenerate, self.behind_coplanar):
            hit = exact_first_hit_v2(o, d, [self.near, blocker])
            self.assertEqual((hit["status"], hit["parameter"], hit["primitive_ids"]), ("HIT", 1, ["near"]))

    def test_possible_interference_still_blocks(self):
        o, d = (0, 0, 0), (0, 0, 1)
        hit = exact_first_hit_v2(o, d, [self.near, self.front_coplanar])
        self.assertEqual((hit["status"], hit["reason"], hit["primitive_ids"]), ("UNKNOWN", "COPLANAR_QUERY", ["front"]))
        self.assertEqual(exact_first_hit_v2(o, d, [self.far_degenerate])["status"], "UNKNOWN")
        behind_point = {"primitive_id": "p", "object_id": "E", "vertices": [(0, 0, -1)]*3}
        self.assertEqual(exact_first_hit_v2(o, d, [behind_point])["status"], "MISS")

    def test_duplicate_identifiers_rejected_anywhere(self):
        with self.assertRaises(ValueError):
            exact_first_hit_v2((0, 0, 0), (0, 0, 1), [self.far_degenerate, triangle(2, "x"), triangle(3, "x")])

    def test_v2_equals_v1_whenever_v1_met_no_deferred_primitive(self):
        rng = random.Random(2026)
        compared = 0
        for _ in range(600):
            tris = []
            for k in range(rng.randint(1, 4)):
                tris.append({"primitive_id": f"t{k}", "object_id": f"o{rng.randint(0, 1)}",
                             "vertices": [tuple(rng.randint(-3, 3) for _ in range(3)) for _ in range(3)]})
            o = tuple(rng.randint(-3, 3) for _ in range(3))
            d = tuple(rng.randint(-2, 2) for _ in range(3))
            if d == (0, 0, 0):
                continue
            v1 = exact_first_hit(o, d, tris)
            if v1.get("reason") in ("DEGENERATE_TRIANGLE", "COPLANAR_QUERY"):
                continue
            v2 = exact_first_hit_v2(o, d, tris)
            if v1["status"] in ("HIT", "MISS"):
                self.assertEqual(v1, v2)
            else:
                self.assertEqual((v1["status"], v1["reason"]), (v2["status"], v2["reason"]))
            compared += 1
        self.assertGreater(compared, 300)


class LimitsAndBaselines(unittest.TestCase):
    def test_reference_scales(self):
        self.assertAlmostEqual(photon_energy(1550e-9)/1.2816e-19, 1, places=3)
        self.assertAlmostEqual(landauer_energy(300)/2.8710e-21, 1, places=3)
        e4 = detection_energy_per_mac(4, 1550e-9, fan_in=5)
        self.assertAlmostEqual(detection_energy_per_mac(5, 1550e-9, fan_in=5)/e4, 4)
        self.assertAlmostEqual(detection_energy_per_mac(4, 1550e-9, fan_in=10)/e4, 0.5)

    def test_shot_noise_level_semantics_by_simulation(self):
        k, bits = 2.0, 4
        n_full = shot_noise_photons(bits, k)
        lower = n_full*(1-1/2**bits)
        threshold = (n_full+lower)/2
        rng = np.random.default_rng(5)
        error = float((rng.poisson(n_full, 40000) < threshold).mean())
        self.assertLess(abs(error-norm.cdf(-k/2)), 0.02)

    def test_passivity_tools(self):
        theta, phi = 0.7, 1.3
        mzi = np.array([[np.exp(1j*phi)*np.sin(theta), np.cos(theta)],
                        [np.exp(1j*phi)*np.cos(theta), -np.sin(theta)]])
        self.assertTrue(is_passive(mzi))
        self.assertAlmostEqual(spectral_norm(mzi), 1.0, places=12)
        np.testing.assert_allclose(project_passive(2*np.eye(2)), np.eye(2), atol=1e-14)
        c = 0.5*mzi
        np.testing.assert_allclose(project_passive(c), c, atol=1e-14)
        self.assertFalse(is_passive(1.01*mzi))

    def test_reachable_set_rank(self):
        mzi = lambda v: np.array([[np.exp(1j*v[1])*np.sin(v[0]), np.cos(v[0])],
                                  [np.exp(1j*v[1])*np.cos(v[0]), -np.sin(v[0])]])
        redundant = lambda v: np.array([[np.exp(1j*(v[0]+v[1])), 0], [0, 1]])
        self.assertEqual(effective_rank(numerical_jacobian(mzi, [0.7, 1.3]))["rank"], 2)
        self.assertEqual(effective_rank(numerical_jacobian(redundant, [0.7, 1.3]))["rank"], 1)

    def test_detector_gradient_matches_finite_differences(self):
        rng = np.random.default_rng(1)
        a, b = rng.normal(size=(3, 4)), rng.normal(size=(3, 4))
        x, y = rng.normal(size=(7, 4)), rng.integers(0, 3, 7)
        _, ga, gb = detector_loss(a, b, x, y, 2.0)
        h = 1e-6
        for (i, j) in ((0, 0), (1, 2), (2, 3)):
            for grad, which in ((ga, 0), (gb, 1)):
                p, m = [a.copy(), b.copy()], [a.copy(), b.copy()]
                p[which][i, j] += h
                m[which][i, j] -= h
                fd = (detector_loss(*p, x, y, 2.0)[0]-detector_loss(*m, x, y, 2.0)[0])/(2*h)
                self.assertAlmostEqual(grad[i, j], fd, places=6)

    def test_passive_trainer_recovers_a_teacher_network(self):
        rng = np.random.default_rng(4)
        q, _ = np.linalg.qr(rng.normal(size=(3, 3))+1j*rng.normal(size=(3, 3)))
        x = rng.normal(size=(300, 3))
        x /= np.linalg.norm(x, axis=1, keepdims=True)
        y = np.argmax(np.abs(x@q.T)**2, axis=1)
        result = train_detector_classifier(x, y, 3, passive=True, steps=600, scale=20.0, seed=0)
        self.assertGreaterEqual(result["train_accuracy"], 0.9)
        self.assertLessEqual(result["spectral_norm"], 1+1e-9)
        again = train_detector_classifier(x, y, 3, passive=True, steps=600, scale=20.0, seed=0)
        np.testing.assert_array_equal(result["W"], again["W"])


class InferenceV2(unittest.TestCase):
    def test_eprocess_exact_value_and_inputs(self):
        self.assertAlmostEqual(paired_sign_eprocess([1, 1], bets=[0.5])["e_value"], 2.25)
        with self.assertRaises(ValueError):
            paired_sign_eprocess([1, 0])
        with self.assertRaises(ValueError):
            paired_sign_eprocess([1], bets=[1.0])

    def test_eprocess_controls_error_and_has_power(self):
        rng = np.random.default_rng(9)
        null = rng.choice([-1, 1], size=(2000, 200))
        type1 = np.mean([eprocess_decision(paired_sign_eprocess(r), 0.05) == "REJECT_H0" for r in null])
        self.assertLessEqual(type1, 0.065)
        alt = np.where(rng.random((300, 200)) < 0.75, 1, -1)
        power = np.mean([eprocess_decision(paired_sign_eprocess(r), 0.05) == "REJECT_H0" for r in alt])
        self.assertGreaterEqual(power, 0.9)

    def test_tost(self):
        close = tost_paired([0.001, -0.002, 0.0015, 0.0, -0.001, 0.002], margin=0.01)
        self.assertTrue(close["equivalent"])
        self.assertLess(close["p_tost"], 0.05)
        far = tost_paired([0.05, 0.06, 0.04, 0.055, 0.045], margin=0.01)
        self.assertFalse(far["equivalent"])
        self.assertGreater(far["p_tost"], 0.05)


class IntegrityTools(unittest.TestCase):
    def test_commitment_round_trip_and_tampering(self):
        salt = bytes(range(32))
        labels = [0, 2, 1, 1, 3]
        c = commit_labels(labels, salt)
        self.assertTrue(verify_reveal(labels, salt, c["root"], c["count"]))
        self.assertFalse(verify_reveal([0, 2, 1, 1, 2], salt, c["root"], c["count"]))
        self.assertFalse(verify_reveal(labels, bytes(32), c["root"], c["count"]))
        with self.assertRaises(ValueError):
            commit_labels(labels, b"short")

    def _record(self):
        return {"id": "EXP-006-WAVE-CONFIRM-001", "hypothesis": "h", "alternative": "a",
                "protocol_commit": "a"*40, "sources": [{"path": "x.py", "sha256": "b"*64}], "inputs": {},
                "environment": {}, "seeds": [0], "resource_budget": {}, "deadline": "2026-11-01",
                "commands": ["python x.py"], "exit_codes": [0], "results": {}, "independent_oracle": "meep",
                "decision_rule": "E_max <= 0.02", "decision": "PASS", "deviations": [], "limitations": ["2D"],
                "published_commit": "c"*40, "status": "PASS"}

    def test_record_validation(self):
        self.assertEqual(validate_experiment_record(self._record()), [])
        bad = self._record() | {"id": "EXP-005-NEW", "independent_oracle": "", "sources": [{"path": "x", "sha256": "XYZ"}]}
        problems = " | ".join(validate_experiment_record(bad))
        for needle in ("EXP-005", "independent oracle", "sources[0]"):
            self.assertIn(needle, problems)
        self.assertIn("published commit", " ".join(validate_experiment_record(self._record() | {"published_commit": "PENDING"})))

    def test_identifier_extraction_and_resolution(self):
        text = ("See [Wright](https://doi.org/10.1038/s41586-021-04223-6), arXiv:2104.13386v1 and "
                "https://arxiv.org/abs/1812.07614. Also 10.1137/030601818.")
        ids = extract_identifiers(text)
        self.assertEqual(ids["doi"], ["10.1038/s41586-021-04223-6", "10.1137/030601818"])
        self.assertEqual(ids["arxiv"], ["2104.13386", "1812.07614"])
        def fake(url, headers):
            if "04223" in url:
                return 200, json.dumps({"responseCode": 1}).encode()
            if "030601818" in url:
                return 404, b""
            return (200, b"") if "2104.13386" in url else (503, b"")
        status = {r["id"]: r["status"] for r in resolve_identifiers(ids, fetch=fake)}
        self.assertEqual(status, {"10.1038/s41586-021-04223-6": "FOUND", "10.1137/030601818": "NOT_FOUND",
                                  "2104.13386": "FOUND", "1812.07614": "ERROR"})


class WaveCrossCheck(unittest.TestCase):
    def test_p17_free_space_overlap_is_reproduced(self):
        """P1-7 reports a 2.7 % free-diffraction loss for w = 8 lambda over ~95 lambda."""
        lam, w, z = 1.0, 8.0, 95.0
        zeta = 2*z/((2*math.pi/lam)*w*w)
        closed = 1/math.sqrt(1+zeta*zeta/4)
        y = np.linspace(-200, 200, 8192, endpoint=False)
        dy = y[1]-y[0]
        g0 = gaussian_1d(y, 0, lam, w)
        overlap = abs(modal_amplitude(angular_spectrum_1d(g0, dy, z, lam), g0, dy))**2
        self.assertLess(abs(overlap-closed), 1e-4)
        self.assertTrue(0.026 < 1-overlap < 0.028)


class FrontierManifest(unittest.TestCase):
    def test_initial_frontier_cannot_be_complete(self):
        doc = json.loads((HERE/"frontier-manifest.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            report = verify_frontier(Path(directory), doc)
        self.assertTrue(report["integrity_pass"])
        self.assertFalse(report["all_frontier_fronts_pass"])

    def test_replication_needs_external_evidence(self):
        doc = json.loads((HERE/"frontier-manifest.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/"verifier.json").write_text("{}")
            import hashlib
            pin = {"verifier.json": hashlib.sha256(b"{}").hexdigest()}
            for o in doc["objectives"]:
                if o["id"] == "F5":
                    o.update(state="PASS", remaining=[], pins=pin, scientific_verifier_record="verifier.json")
            report = verify_frontier(root, doc)
        self.assertIn("F5", [f["id"] for f in report["failures"]])
        with self.assertRaises(ValueError):
            verify_frontier(Path("."), {"schema": "neuro3d.frontier.manifest.v1", "objectives": [{"id": "F1"}]})


if __name__ == "__main__":
    unittest.main()
