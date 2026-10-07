"""New opt-in SOURCE normalization graph in actual CPU runtime, not torch/GPU."""
import base64
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"Blender/benchmarks/capacity_audit"))
import original_SOURCE_normalization_CPU64_v1 as m
LITERAL = ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
LITERAL_SHA = "139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
RECORDS = []


def run(item):
    return m.observe(item["scene"], item["request"],
                     m.digest(item["scene"]), m.digest(item["request"]))


class SourceNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = LITERAL.read_bytes()
        assert len(raw) == 26731 and hashlib.sha256(raw).hexdigest() == LITERAL_SHA
        r = json.loads(raw)["test_run"]
        dec = zlib.decompressobj()
        data = dec.decompress(base64.b64decode(r["stdout_zlib_base64"],validate=True),1048577)
        assert dec.eof and not dec.unused_data and not dec.unconsumed_tail
        assert len(data) <= 1048576 and len(data) == r["stdout_bytes"]
        assert hashlib.sha256(data).hexdigest() == r["stdout_sha256"]
        assert r["rc"] == 0 and not r["timed_out"]
        cls.inputs = json.loads(data)["data"]["inputs"]

    def test_four_actual_original_input_cases(self):
        for case in ("oblique","direction_scaled","shared_ref1000","tiny_gap_2m60"):
            item = self.inputs[case]; r = run(item)
            self.assertEqual(r["status"], "CPU64_SOURCE_WORDS_OBSERVED_ONLY")
            self.assertEqual([row["source_id"] for row in r["records"]], ["S0","S1"])
            self.assertEqual(r["root_calls"], 2)
            self.assertFalse(r["native_GPU_precision_certified"])
            self.assertIsNone(r["native_phase_bound_rad"])
            for row in r["records"]:
                vals = [F.from_float(struct.unpack(">d",bytes.fromhex(w))[0])
                        for w in row["normalized_direction_words_hex"]]
                defect = F(1)-sum(v*v for v in vals)
                self.assertEqual(F(*map(int,row["one_minus_exact_word_norm_squared"])),defect)
                self.assertNotEqual(defect,0)
                self.assertEqual(row["SOURCE_position_input_loss_BU"],["0","1"])
                RECORDS.append(dict(kind="CPU64_SOURCE_WORD_CAPTURE",case=case,**row))
            RECORDS.append(dict(kind="CASE_SCOPE",case=case,**{k:v for k,v in r.items() if k!="records"}))

    def test_content_pin_mismatch_and_channel_order_stop(self):
        item = copy.deepcopy(self.inputs["oblique"])
        scene_sha,query_sha = m.digest(item["scene"]),m.digest(item["request"])
        for label in ("wrong_scene_pin","wrong_query_pin","swapped_channels"):
            s,q = copy.deepcopy(item["scene"]),copy.deepcopy(item["request"])
            if label == "swapped_channels":
                s["sources"].reverse(); q["original_scene_sha256"] = m.digest(s)
                result = m.observe(s,q,m.digest(s),m.digest(q))
            else:
                result = m.observe(s,q,"0"*64 if label=="wrong_scene_pin" else scene_sha,
                                   "0"*64 if label=="wrong_query_pin" else query_sha)
            self.assertEqual(result["status"],"STOP")
            self.assertEqual(result["records"],[])
            self.assertEqual(result["root_calls"],0)
            RECORDS.append(dict(kind="CONTENT_OR_CHANNEL_STOP",label=label,**result))

    def test_zero_and_cast_loss_are_atomic_stop(self):
        for label in ("zero_direction","position_one_third","direction_one_third","bool_rational","bad_query_link"):
            item = copy.deepcopy(self.inputs["oblique"])
            source = item["scene"]["sources"][1]  # Failure after S0: no partial output.
            if label=="zero_direction": source["direction"]=[[0,1]]*3
            elif label=="position_one_third": source["position_BU"][0]=[1,3]
            elif label=="direction_one_third": source["direction"][0]=[1,3]
            elif label=="bool_rational": source["direction"][0]=[True,1]
            item["request"]["original_scene_sha256"] = m.digest(item["scene"])
            if label=="bad_query_link": item["request"]["original_scene_sha256"]="0"*64
            result = run(item)
            self.assertEqual(result["status"],"STOP")
            self.assertEqual(result["records"],[])
            self.assertEqual(result["root_calls"],0)
            self.assertFalse(result["current_GPU_admission"])
            RECORDS.append(dict(kind="ATOMIC_INPUT_STOP",label=label,**result))


if __name__=="__main__":
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceNormalizationTests))
    print(json.dumps(dict(status="PASS" if result.wasSuccessful() else "FAIL",tests=result.testsRun,
                         records=RECORDS,GPU_used=False,foreign_code_executed=False,
                         new_source_normalization_roots=8,native_phase_budget_certified=False)))
    raise SystemExit(0 if result.wasSuccessful() else 1)
