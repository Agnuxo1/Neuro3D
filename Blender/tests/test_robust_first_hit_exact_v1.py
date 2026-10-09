import copy
from fractions import Fraction
import json
from pathlib import Path
import unittest

from Blender.benchmarks.capacity_audit import robust_first_hit_exact_v1 as exact

ROOT = Path(__file__).resolve().parents[2]
INPUTS = ROOT / "Docs" / "validation" / "scene-hilo-native-2026-10-06" / "inputs01"


def plane(x, *, scale=4.0):
    return exact.mirror([(x, 0.0, 0.0), (x, scale, 0.0), (x, 0.0, scale)])


def packet(objects, position=(1.0, 1.0, 1.0), direction=(-1.0, 0.0, 0.0), label="case"):
    snap = exact.make_snapshot(objects, [exact.source_row(position, direction)])
    return exact.synthetic_packet(snap, label=label)


def selected_object_id(p, result):
    ordinal = result["selected_object"]
    return next(row["id"] for row in p["manifest"]["objects"] if row["ordinal"] == ordinal)


class ExactFirstHitTests(unittest.TestCase):
    def test_real_k3_k4_internal_triangulation_ties_resolve_to_surface(self):
        observed = []
        for filename in ("k3_baseline.packet.json", "k4_baseline.packet.json"):
            p = json.loads((INPUTS / filename).read_text(encoding="utf-8"))
            for source in range(p["manifest"]["abi"]["source_count"]):
                r = exact.select(p, source)
                observed.append(r)
                self.assertEqual(r["status"], "SELECT")
                self.assertTrue(r["equivalent_surface_tie"])
                self.assertEqual(len(r["tie_primitive_ids"]), 2)
                self.assertEqual(r["tie_primitive_ids"][1], r["tie_primitive_ids"][0] + 1)
        self.assertEqual(len(observed), 9)

    def test_ultrathin_gaps_never_collapse_to_false_tie(self):
        for power in (53, 54, 60):
            delta = 2.0 ** -power
            p = packet({"a_far": plane(0.0), "z_near": plane(delta)}, label=f"gap-{power}")
            r = exact.select(p, 0)
            self.assertEqual(r["status"], "SELECT")
            self.assertEqual(selected_object_id(p, r), "z_near")
            self.assertEqual(Fraction(r["t"][0], r["t"][1]), Fraction.from_float(1.0) - Fraction.from_float(delta))

    def test_true_coincident_geometry_is_reported_not_arbitrarily_selected(self):
        p = packet({"a": plane(0.0), "b": plane(0.0)}, label="true-tie")
        r = exact.select(p, 0)
        self.assertEqual(r["status"], "TRUE_TIE")
        self.assertEqual(r["tie_primitive_ids"], [0, 1])
        self.assertFalse(r["equivalent_surface_tie"])

    def test_previous_contact_is_excluded_only_at_exact_zero(self):
        delta = 2.0 ** -60
        p = packet({"near": plane(delta), "previous": plane(0.0)},
                   position=(0.0, 1.0, 1.0), direction=(1.0, 0.0, 0.0), label="contact-gap")
        previous = exact.object_primitive(p, "previous")
        r = exact.select(p, 0, previous_primitive=previous, departure_event="mirror")
        self.assertEqual(r["status"], "SELECT")
        self.assertEqual(r["excluded_previous_contacts"], 1)
        self.assertEqual(selected_object_id(p, r), "near")
        self.assertEqual(Fraction(r["t"][0], r["t"][1]), Fraction.from_float(delta))

    def test_previous_primitive_is_not_globally_ignored_on_later_return(self):
        p = packet({"previous": plane(0.0)}, position=(-1.0, 1.0, 1.0),
                   direction=(1.0, 0.0, 0.0), label="later-return")
        previous = exact.object_primitive(p, "previous")
        r = exact.select(p, 0, previous_primitive=previous, departure_event="r")
        self.assertEqual(r["status"], "SELECT")
        self.assertEqual(r["selected_primitive"], previous)
        self.assertEqual(r["excluded_previous_contacts"], 0)
        self.assertEqual(Fraction(r["t"][0], r["t"][1]), 1)

    def test_unique_outer_edge_hit_is_fail_closed_boundary(self):
        p = packet({"only": plane(0.0, scale=2.0)}, label="outer-boundary")
        r = exact.select(p, 0)
        self.assertEqual(r["status"], "BOUNDARY")
        self.assertEqual(r["tie_primitive_ids"], [0])

    def test_coplanar_ray_is_fail_closed(self):
        p = packet({"only": plane(0.0)}, position=(0.0, 0.5, 0.5),
                   direction=(0.0, 1.0, 0.0), label="coplanar")
        r = exact.select(p, 0)
        self.assertEqual(r["status"], "COPLANAR")
        self.assertEqual(r["coplanar_primitive_ids"], [0])

    def test_degenerate_triangle_rejects_geometry(self):
        deg = exact.mirror([(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 2.0, 0.0)])
        p = packet({"bad": deg}, label="degenerate")
        r = exact.select(p, 0)
        self.assertEqual(r["status"], "INVALID_GEOMETRY")
        self.assertEqual(r["degenerate_primitive_ids"], [0])

    def test_near_parallel_direction_uses_exact_ratio(self):
        d = -(2.0 ** -100)
        p = packet({"only": plane(0.0)}, direction=(d, 0.0, 0.0), label="near-parallel")
        r = exact.select(p, 0)
        self.assertEqual(r["status"], "SELECT")
        self.assertEqual(Fraction(r["t"][0], r["t"][1]), Fraction(1, 1) / Fraction.from_float(-d))

    def test_extreme_declared_coordinate_control_does_not_overflow(self):
        x = 999999.0
        p = packet({"only": plane(x)}, position=(1000000.0, 1.0, 1.0),
                   direction=(-1.0, 0.0, 0.0), label="extreme")
        r = exact.select(p, 0)
        self.assertEqual(r["status"], "SELECT")
        self.assertEqual(Fraction(r["t"][0], r["t"][1]), 1)

    def test_wrong_departure_contract_is_rejected(self):
        p = packet({"only": plane(0.0)}, label="bad-departure")
        with self.assertRaises(exact.ExactRejected):
            exact.select(p, 0, previous_primitive=0, departure_event=None)
        with self.assertRaises(exact.ExactRejected):
            exact.select(p, 0, previous_primitive=None, departure_event="mirror")

    def test_wire_mutation_is_rejected_before_geometry(self):
        p = packet({"only": plane(0.0)}, label="wire-mutation")
        changed = copy.deepcopy(p)
        raw = bytearray.fromhex(changed["wire_hex"])
        raw[-1] ^= 1
        changed["wire_hex"] = raw.hex()
        with self.assertRaises(exact.ExactRejected):
            exact.select(changed, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
