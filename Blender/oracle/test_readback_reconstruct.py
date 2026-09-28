"""Self-checks of readback_reconstruct with synthetic records (no Blender). python -m unittest"""

import copy
import math
import unittest

from geometry_oracle import NonRectMZ
from readback_reconstruct import compare, direction_gaps, local_z, position
from mz_scene import Detector, MZScene, Mirror, Source, Splitter, trace_mz


def _matrix(pos, z):
    """Row-major 4x4 with local +Z = z (any orthonormal completion)."""
    z = [c / math.sqrt(sum(v * v for v in z)) for c in z]
    helper = (0.0, 0.0, 1.0) if abs(z[2]) < 0.9 else (1.0, 0.0, 0.0)
    x = [helper[1] * z[2] - helper[2] * z[1], helper[2] * z[0] - helper[0] * z[2], helper[0] * z[1] - helper[1] * z[0]]
    n = math.sqrt(sum(v * v for v in x)); x = [v / n for v in x]
    y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]]
    return [x[0], y[0], z[0], pos[0], x[1], y[1], z[1], pos[1], x[2], y[2], z[2], pos[2], 0.0, 0.0, 0.0, 1.0]


def synthetic_record(phase2=0.0, coherence=1.0):
    g = NonRectMZ(60, 2, 2).scene()
    P = g["bs2"]["position"]
    da = tuple(p + d for p, d in zip(P, g["port_a_direction"]))
    db = tuple(p + d for p, d in zip(P, g["port_b_direction"]))
    geo = {
        "mz_source": ((-1.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
        "mz_bs1": (g["bs1"]["position"], g["bs1"]["normal"]),
        "mz_bs2": (P, g["bs2"]["normal"]),
        "mz_mirror1": (g["mirror1"]["position"], g["mirror1"]["normal"]),
        "mz_mirror2": (g["mirror2"]["position"], g["mirror2"]["normal"]),
        "mz_detector_a": (da, (0.0, 0.0, 1.0)),
        "mz_detector_b": (db, (0.0, 0.0, 1.0)),
    }
    optics = {
        "mz_source": {"power": 1.0, "rgb": [1.0, 1.0, 1.0], "frequency": 100.0, "phase": 0.0,
                      "propagation_speed": 10.0, "absorption_per_unit": 0.0, "beam_waist": 0.2,
                      "mutual_coherence": coherence},
        "mz_bs1": {"radius": 0.4, "transmission": 0.5},
        "mz_bs2": {"radius": 0.4, "transmission": 0.5, "overlap_tolerance": 0.02, "direction_tolerance": 1e-6},
        "mz_mirror1": {"radius": 0.4, "reflectance_rgb": [1.0, 1.0, 1.0], "phase_shift": 0.0},
        "mz_mirror2": {"radius": 0.4, "reflectance_rgb": [1.0, 1.0, 1.0], "phase_shift": phase2},
        "mz_detector_a": {"radius": 0.2, "responsivity_rgb": [1.0, 1.0, 1.0], "activation_threshold": 0.25, "response_gain": 1.0},
        "mz_detector_b": {"radius": 0.2, "responsivity_rgb": [1.0, 1.0, 1.0], "activation_threshold": 0.25, "response_gain": 1.0},
    }
    s = optics["mz_source"]
    scene = MZScene(Source(*geo["mz_source"], 1.0, (1.0, 1.0, 1.0), 100.0, 0.0, beam_waist=0.2, mutual_coherence=coherence),
                    Splitter(*geo["mz_bs1"]), Mirror(*geo["mz_mirror1"]), Mirror(*geo["mz_mirror2"], phase_shift=phase2),
                    Splitter(*geo["mz_bs2"]), Detector(da), Detector(db), 10.0, 0.0, 0.02, 1e-6)
    r = trace_mz(scene)
    return {
        "objects": {role: {"matrix_world": _matrix(*geo[role])} for role in geo},
        "optics": optics,
        "result": {"status": r.status, **{k: list(getattr(r, k)) for k in
                   ("optical_a", "optical_b", "escape_rgb", "unresolved_rgb", "residual_rgb")}},
    }


class Readback(unittest.TestCase):
    def test_matrix_helpers(self):
        m = _matrix((1.0, 2.0, 3.0), (0.0, 3.0, 4.0))
        self.assertEqual(position(m), (1.0, 2.0, 3.0))
        for a, b in zip(local_z(m), (0.0, 0.6, 0.8)):
            self.assertAlmostEqual(a, b, places=15)

    def test_reconstruction_matches_for_controls(self):
        for phase2, coherence in ((0.0, 1.0), (math.pi, 1.0), (0.0, 0.0)):
            rep = compare(synthetic_record(phase2, coherence))
            self.assertTrue(rep["passes"], rep)
            self.assertEqual(rep["worst_abs_diff"], 0.0)

    def test_tampered_property_is_detected(self):
        rec = synthetic_record()
        rec["optics"]["mz_mirror2"]["phase_shift"] = math.pi   # stored result says B=1
        self.assertFalse(compare(rec)["passes"])

    def test_tampered_matrix_is_detected(self):
        rec = synthetic_record()
        rec["objects"]["mz_mirror1"]["matrix_world"][3] += 0.025   # move M1 by a quarter wavelength
        self.assertFalse(compare(rec)["passes"])

    def test_missing_roles_raise(self):
        rec = copy.deepcopy(synthetic_record())
        del rec["optics"]["mz_bs2"]
        with self.assertRaises(KeyError):
            compare(rec)

    def test_direction_gaps_are_diagnostic_not_acceptance(self):
        record = synthetic_record()
        record["optics"]["mz_bs2"]["direction_tolerance"] = 1e-5
        aligned = direction_gaps(record)
        self.assertTrue(aligned["within_tolerance"])
        self.assertLess(max(aligned["gap_a"], aligned["gap_b"]), 1e-12)
        # Move only the stored M2 orientation, not the stored output values.
        record["objects"]["mz_mirror2"]["matrix_world"] = _matrix(
            (0.0, 0.8452994616207483, 0.0), (0.8660254, -0.4999, 0.0))
        misaligned = direction_gaps(record)
        self.assertFalse(misaligned["within_tolerance"])
        self.assertGreater(max(misaligned["gap_a"], misaligned["gap_b"]), 1e-5)


if __name__ == "__main__":
    unittest.main()
