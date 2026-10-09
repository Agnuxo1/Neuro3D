"""New candidate packet composition from saved evidence; no old producers or queries."""
import base64
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Blender.benchmarks.capacity_audit import original_SOURCE_query_packet_CPU_v1_origin_20261006 as packet

PARENTS = {
    "PRECISION-ORIGINAL-SOURCE-POINT-HILO-CPU-001-CODEX.json":
        "e3d4a3e5f431b97fb83e121d4a9f06c9454e9f9849437721a7ed3e9b488fce07",
    "PRECISION-ORIGINAL-SOURCE-DIRECTION-ENDPOINTS-HILO-CPU-001-CODEX.json":
        "789c41b770050d1cdd25146e7efbcc9eb3216b17e3a730cc54f80012cb2a2a45",
}
RECORDS = []


def load(name, sha):
    raw = (ROOT / "coordinacion/respuestas" / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError("retained parent changed")
    cap = json.loads(raw)["test_run"]
    dec = zlib.decompressobj()
    data = dec.decompress(base64.b64decode(cap["stdout_zlib_base64"], validate=True), 1048577)
    if not (dec.eof and not dec.unused_data and not dec.unconsumed_tail and
            len(data) <= 1048576 and len(data) == cap["stdout_bytes"] and
            hashlib.sha256(data).hexdigest() == cap["stdout_sha256"] and
            cap["rc"] == 0 and not cap["timed_out"]):
        raise ValueError("retained capture invalid")
    return json.loads(data)["rows"]


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.points, cls.directions = [load(n, sha) for n, sha in PARENTS.items()]
        cls.by_slot = {(r["case"], r["source_id"]): r for r in cls.directions}

    def test_all_original_slots_composed_without_dedup(self):
        bindings, wires = set(), {}
        self.assertEqual(len(self.points), 12)
        for p in self.points:
            d = self.by_slot[p["case"], p["source_id"]]
            got = packet.make_packet(p, d, model=packet.MODEL)
            self.assertEqual(packet.audit_packet(got, expected=got, model=packet.MODEL), got)
            self.assertEqual(len(bytes.fromhex(got["wire_hex"])), 76)
            self.assertEqual(got["query_words"][:6], p["point_words"])
            self.assertEqual(got["query_words"][6:18], d["direction_endpoint_words"])
            self.assertEqual(got["query_words"][18], p["previous_primitive_id"])
            lo, hi = d["saved_direction_bounds"][0]
            width = Fraction(*hi) - Fraction(*lo)
            self.assertGreater(width, 0)
            bindings.add(got["CPU_packet_binding_sha256"])
            wires.setdefault(got["wire_sha256"], []).append([p["case"], p["source_id"]])
            RECORDS.append(dict(case=p["case"], source_id=p["source_id"], packet=got,
                                direction_x_width=[width.numerator, width.denominator]))
        self.assertEqual(len(bindings), 12)
        self.assertLess(len(wires), 12)  # Equal wire never removes SOURCE envelopes.

    def test_mixed_point_direction_slots_rejected(self):
        for p in self.points:
            same = self.by_slot[p["case"], p["source_id"]]
            for key, value in (("source_id", "S1" if p["source_id"] == "S0" else "S0"),
                               ("scene_sha256", "0"*64), ("previous_primitive_id", 2),
                               ("parent_point_CPU_slot_binding_sha256", "0"*64)):
                changed = copy.deepcopy(same)
                changed[key] = value
                with self.assertRaises(ValueError):
                    packet.make_packet(p, changed, model=packet.MODEL)
                RECORDS.append(dict(case=p["case"], source_id=p["source_id"],
                                    negative="mixed:"+key, status="REJECT"))

    def test_resealed_changes_cannot_replace_fixed_slot(self):
        for p in self.points:
            got = packet.make_packet(p, self.by_slot[p["case"], p["source_id"]], model=packet.MODEL)
            for kind in ("SOURCE_swap", "previous_primitive", "collapse_x_interval", "GPU_permission"):
                changed = copy.deepcopy(got)
                if kind == "SOURCE_swap":
                    changed["slot"]["source_id"] = "S1" if p["source_id"] == "S0" else "S0"
                elif kind == "previous_primitive":
                    changed["slot"]["previous_primitive_id"] = 2
                    changed["query_words"][18] = 2
                elif kind == "collapse_x_interval":
                    changed["query_words"][8:10] = changed["query_words"][6:8]
                    changed["slot"]["saved_direction_bounds"][0][1] = copy.deepcopy(
                        changed["slot"]["saved_direction_bounds"][0][0])
                else:
                    changed["GPU_launch_allowed"] = True
                raw = struct.pack("<19I", *changed["query_words"])
                changed.update(wire_hex=raw.hex(), wire_sha256=hashlib.sha256(raw).hexdigest())
                changed["CPU_packet_binding_sha256"] = packet.binding(changed)
                with self.assertRaises(ValueError):
                    packet.audit_packet(changed, expected=got, model=packet.MODEL)
                RECORDS.append(dict(case=p["case"], source_id=p["source_id"],
                                    negative="resealed:"+kind, status="REJECT"))

    def test_malformed_previous_and_nonfinite_words_stop(self):
        p0, d0 = self.points[0], self.by_slot[self.points[0]["case"], self.points[0]["source_id"]]
        for value in (True, -1, 2**32, None):
            p, d = copy.deepcopy(p0), copy.deepcopy(d0)
            p["previous_primitive_id"] = d["previous_primitive_id"] = value
            with self.assertRaises(ValueError):
                packet.make_packet(p, d, model=packet.MODEL)
        p = copy.deepcopy(p0)
        p["point_words"][0] = 0x7f800000
        p["point_wire_hex"] = struct.pack("<6I", *p["point_words"]).hex()
        with self.assertRaises(ValueError):
            packet.make_packet(p, d0, model=packet.MODEL)


if __name__ == "__main__":
    out = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps(dict(id="PRECISION-ORIGINAL-SOURCE-QUERY-PACKET-CPU-001",
                         status="PASS" if out.wasSuccessful() else "FAIL", tests=out.testsRun,
                         records=RECORDS, native_original_transport_joins=0,
                         packet_logical_bytes=76, all_SOURCE_logical_bytes_without_dedup=912,
                         GPU_launch_allowed=False, native_ABI_certified=False,
                         phase_error_bound=None, full_costs="UNKNOWN_NOT_ZERO"), sort_keys=True))
    raise SystemExit(0 if out.wasSuccessful() else 1)
