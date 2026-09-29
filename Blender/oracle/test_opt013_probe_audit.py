"""OPT-013 audit checks of the GPU ray probe host code + FP64 shader port.

CPU only; stubs glfw/moderngl, never creates a GPU context. python -m unittest
"""

import copy
import math
import random
import struct
import unittest

import opt013_probe_audit as audit


def _f32(v):
    return struct.unpack("f", struct.pack("f", v))[0]


class Exp001Parity(unittest.TestCase):
    def test_seven_controls_accepted_by_ported_shader(self):
        for name, record in audit.exp001_records().items():
            with self.subTest(control=name):
                self.assertTrue(audit.run_probe_on(record)["accepted"])

    def test_d_loses_mirror2_arm(self):
        self.assertEqual(audit.run_probe_on(audit.exp001_records()["D"])["ray_status"], 1)

    def test_taylor_cosine_error_far_below_gate(self):
        self.assertLess(audit.taylor_error(20001), 1e-13)


class WhatEachControlProves(unittest.TestCase):
    """F2/F3: parity that is independent of the geometric phase."""

    def test_single_arm_powers_are_constants(self):
        rec = audit.exp001_records()["D"]
        x = audit.probe.input_record(rec)
        y1 = audit.emulate_shader(x)
        x2 = list(x)
        x2[18] *= 7.3          # frequency: would change any computed phase
        x2[16] += 1.1          # mirror-1 phase shift
        y2 = audit.emulate_shader(x2)
        self.assertEqual(y1[:9], y2[:9])

    def test_incoherent_controls_ignore_path_difference(self):
        rec = audit.exp001_records()["C-A"]
        x = audit.probe.input_record(rec)
        x2 = list(x)
        x2[17] += 0.9          # any phase shift
        self.assertEqual(audit.emulate_shader(x)[:9], audit.emulate_shader(x2)[:9])

    def test_quadrature_hides_ignored_mode_overlap(self):
        geo, opt = audit.base_geometry(), audit.base_optics()
        n = audit._normalize(geo["mz_bs2"][1])
        for role in ("mz_bs2", "mz_detector_a", "mz_detector_b"):
            geo[role][0] = audit._add(geo[role][0], audit._mul(n, 0.05))
        rec = audit.make_record(geo, opt)
        d0 = audit.emulate_shader(audit.probe.input_record(rec))[10]
        opt["mz_mirror2"]["phase_shift"] = math.pi / 2 - d0
        rec = audit.make_record(geo, opt)
        rebuilt = audit.trace_mz(audit.rebuild(rec))
        self.assertLess(rebuilt.mode_overlap, 0.95)
        self.assertTrue(audit.run_probe_on(rec)["accepted"])


class LoudFailures(unittest.TestCase):
    def test_counter_cases_are_rejected(self):
        for name, rec in audit.counter_cases().items():
            with self.subTest(case=name):
                self.assertFalse(audit.run_probe_on(rec)["accepted"])


class PhaseGuardFragility(unittest.TestCase):
    """F1: B-geo sits on the |delta| <= pi + 1e-9 edge; float32 noise trips it."""

    def test_float32_translation_jitter_trips_guard(self):
        base = audit.exp001_records()["B-geo"]
        rng = random.Random(13)
        raised = 0
        for _ in range(300):
            rec = copy.deepcopy(base)
            for obj in rec["objects"].values():
                m = obj["matrix_world"]
                for idx in (3, 7, 11):
                    v = _f32(m[idx])
                    ulp = math.ulp(v) * 2 ** 29 if v else 0.0
                    m[idx] = v + rng.choice((-1, 0, 1)) * ulp
            y = audit.emulate_shader(audit.probe.input_record(rec))
            raised += abs(y[10]) > math.pi + 1e-9
        self.assertGreater(raised, 30)


class RealGlslOnSoftwareGL(unittest.TestCase):
    """F7: runs the probe's actual GLSL text on Mesa llvmpipe (CPU, no GPU)."""

    @classmethod
    def setUpClass(cls):
        cls.records = list(audit.exp001_records().values())
        if audit.run_glsl(cls.records[:1]) is None:
            raise unittest.SkipTest("no headless OpenGL 4.3 context (Mesa llvmpipe/EGL)")

    def test_unsuffixed_two_pi_literal_is_single_precision(self):
        out = audit.run_glsl(self.records)
        b_geo = out[1]
        self.assertGreater(abs(b_geo[10]) - math.pi, 5e-8)   # float32 2*pi
        self.assertFalse(audit.host_accepts(b_geo, self.records[1]["result"])["accepted"])

    def test_lf_suffix_restores_bit_exact_fp64(self):
        original = audit.probe.SHADER
        try:
            audit.probe.SHADER = original.replace("6.2831853071795864769", "6.2831853071795864769LF")
            out = audit.run_glsl(self.records)
        finally:
            audit.probe.SHADER = original
        for rec, y in zip(self.records, out):
            self.assertEqual(y, audit.emulate_shader(audit.probe.input_record(rec)))
            self.assertTrue(audit.host_accepts(y, rec["result"])["accepted"])


if __name__ == "__main__":
    unittest.main()
