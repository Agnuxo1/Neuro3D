"""Mock-object tests for absolute placement; no bpy, optics engine or GPU."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mz_exp001_plan import controls
from mz_exp002_geometry import (capture_baseline, place_u, place_sham_u,
                                scene_evaluator, verify_final_binding)


class FakeObject:
    def __init__(self, xyz, parent=None):
        self.location = list(xyz)
        self.parent = parent
        self.phase_shift = 0.0


def roles_a():
    group = FakeObject((2.0, 2.0, 0.0))
    mirror1 = FakeObject((2.0 - 2.0 / math.sqrt(3.0), 0.0, 0.0))
    return {
        "mz_combiner_group": group,
        "mz_mirror1": mirror1,
        "mz_mirror2": FakeObject((0.0, 2.0 - 2.0 / math.sqrt(3.0), 0.0)),
        "mz_source": FakeObject((-1.0, 0.0, 0.0)),
        "mz_bs1": FakeObject((0.0, 0.0, 0.0)),
        "mz_bs2": FakeObject((0.0, 0.0, 0.0), group),
        "mz_detector_a": FakeObject((1.0, 0.0, 0.0), group),
        "mz_detector_b": FakeObject((0.0, 1.0, 0.0), group),
    }


def record_at_u(u, power_a=.75):
    edit = controls()[1]
    objects = {}
    for role, base, delta in (
        ("mz_combiner_group", (2., 2., 0.), edit.group_delta),
        ("mz_mirror1", (2. - 2. / math.sqrt(3.), 0., 0.), edit.mirror1_delta),
    ):
        xyz = [base[i] + u * delta[i] for i in range(3)]
        objects[role] = {"matrix_world": [1., 0., 0., xyz[0],
                                          0., 1., 0., xyz[1],
                                          0., 0., 1., xyz[2],
                                          0., 0., 0., 1.]}
    return {"objects": objects,
            "result": {"status": "ok", "optical_a": [power_a, 0., 0.]}}


class EXP002GeometryTests(unittest.TestCase):
    def test_absolute_path_matches_frozen_bgeo_and_restores_a(self):
        roles = roles_a()
        baseline = capture_baseline(roles)
        before = {name: tuple(obj.location) for name, obj in roles.items()}
        edit = controls()[1]
        place_u(roles, baseline, 1.0)
        for i in range(3):
            self.assertAlmostEqual(roles["mz_combiner_group"].location[i],
                                   baseline.group[i] + edit.group_delta[i])
            self.assertAlmostEqual(roles["mz_mirror1"].location[i],
                                   baseline.mirror1[i] + edit.mirror1_delta[i])
        for name in before.keys() - {"mz_combiner_group", "mz_mirror1"}:
            self.assertEqual(tuple(roles[name].location), before[name])
        for u in (0.1, 0.9, 0.1, 0.0):
            place_u(roles, baseline, u)
        self.assertEqual(tuple(roles["mz_combiner_group"].location), baseline.group)
        self.assertEqual(tuple(roles["mz_mirror1"].location), baseline.mirror1)

    def test_repeated_gradient_probes_do_not_accumulate_motion(self):
        roles = roles_a()
        baseline = capture_baseline(roles)
        place_u(roles, baseline, .1001)
        place_u(roles, baseline, .0999)
        place_u(roles, baseline, .1)
        final = tuple(roles["mz_combiner_group"].location)
        direct = roles_a()
        place_u(direct, capture_baseline(direct), .1)
        self.assertEqual(final, tuple(direct["mz_combiner_group"].location))

    def test_reject_wrong_layout_or_parent_before_edit(self):
        roles = roles_a()
        roles["mz_mirror1"].location[0] = 2.0
        with self.assertRaisesRegex(ValueError, "nonrect60"):
            capture_baseline(roles)
        roles = roles_a()
        roles["mz_detector_a"].parent = None
        with self.assertRaisesRegex(ValueError, "parented"):
            capture_baseline(roles)

    def test_reject_bad_u_without_motion(self):
        roles = roles_a()
        baseline = capture_baseline(roles)
        for bad in (-.01, 1.01, float("nan"), float("inf")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                place_u(roles, baseline, bad)
        self.assertEqual(tuple(roles["mz_combiner_group"].location), baseline.group)
        self.assertEqual(tuple(roles["mz_mirror1"].location), baseline.mirror1)

    def test_evaluator_places_scene_before_calling_supplied_trace(self):
        roles = roles_a()
        baseline = capture_baseline(roles)
        seen = []
        token = object()
        def trace():
            seen.append((tuple(roles["mz_combiner_group"].location),
                         tuple(roles["mz_mirror1"].location)))
            return token
        evaluate = scene_evaluator(roles, baseline, trace)
        self.assertIs(evaluate(.25), token)
        edit = controls()[1]
        self.assertAlmostEqual(seen[0][0][0], baseline.group[0] + .25 * edit.group_delta[0])
        self.assertAlmostEqual(seen[0][1][0], baseline.mirror1[0] + .25 * edit.mirror1_delta[0])
        with self.assertRaises(ValueError):
            evaluate(float("nan"))
        self.assertEqual(len(seen), 1)

    def test_sham_moves_only_combiner_in_plane_without_accumulation(self):
        roles = roles_a()
        baseline = capture_baseline(roles)
        mirror_before = tuple(roles["mz_mirror1"].location)
        for u in (.2, .8, .2):
            place_sham_u(roles, baseline, u)
        tangent = .3 * .2 / math.sqrt(2.0)
        self.assertAlmostEqual(roles["mz_combiner_group"].location[0],
                               baseline.group[0] + tangent)
        self.assertAlmostEqual(roles["mz_combiner_group"].location[1],
                               baseline.group[1] + tangent)
        self.assertEqual(roles["mz_combiner_group"].location[2], baseline.group[2])
        self.assertEqual(tuple(roles["mz_mirror1"].location), mirror_before)
        place_sham_u(roles, baseline, 0.0)
        self.assertEqual(tuple(roles["mz_combiner_group"].location), baseline.group)

    def test_sham_evaluator_traces_edited_scene_and_rejects_bad_u(self):
        roles = roles_a()
        baseline = capture_baseline(roles)
        seen = []
        evaluate = scene_evaluator(
            roles, baseline,
            lambda: seen.append((tuple(roles["mz_combiner_group"].location),
                                 tuple(roles["mz_mirror1"].location))),
            sham=True,
        )
        evaluate(.5)
        self.assertAlmostEqual(seen[0][0][0], baseline.group[0] + .15 / math.sqrt(2.0))
        self.assertEqual(seen[0][1], baseline.mirror1)
        with self.assertRaises(ValueError):
            evaluate(float("nan"))
        self.assertEqual(len(seen), 1)

    def test_final_binding_accepts_reopened_matrices_and_power(self):
        verdict = verify_final_binding(record_at_u(0), record_at_u(2. / 3.),
                                       2. / 3., 2. / 3., .75)
        self.assertLessEqual(verdict["position_error_bu"], 1e-12)
        self.assertEqual(verdict["power_a_error"], 0.)

    def test_final_binding_rejects_last_gradient_probe_position(self):
        with self.assertRaisesRegex(AssertionError, "not bound"):
            verify_final_binding(record_at_u(0), record_at_u(.5001),
                                 .5, .5, .75)

    def test_final_binding_rejects_wrong_last_sample_or_retrace(self):
        with self.assertRaisesRegex(AssertionError, "Last optical observation"):
            verify_final_binding(record_at_u(0), record_at_u(.5),
                                 .5, .5001, .75)
        with self.assertRaisesRegex(AssertionError, "Reopened P_A"):
            verify_final_binding(record_at_u(0), record_at_u(.5, .74),
                                 .5, .5, .75)


if __name__ == "__main__":
    unittest.main()
