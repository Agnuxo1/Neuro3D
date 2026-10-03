"""New wire-contract tests only: never execute sealed geometry/phase producers."""
import importlib.util, json, struct, unittest
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("pair64_wire", ROOT/"Blender/benchmarks/capacity_audit/axial_common_detector_pair64_wire_HOST_v1.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
PACKS = {}; CONSUMES = {}; INPUTS = {}; SELECTORS = {}; CONTROLS = {}; MODELS = {}; PACK_SELECTORS = {}
def consume_record(name, q, envelope, model=None):
    SELECTORS[name] = deepcopy(q); INPUTS[name] = deepcopy(envelope)
    MODELS[name] = m.MODEL if model is None else model
    value = m.consume(q, envelope, model=m.MODEL if model is None else model)
    CONSUMES[name] = value
    return value
def rehash(envelope, raw):
    value = deepcopy(envelope); value["payload_hex"] = raw.hex(); value["payload_sha256"] = m.sha(raw)
    return value
class Tests(unittest.TestCase):
    def reject(self, value):
        self.assertEqual(value["status"], "STOP")
        self.assertEqual(value["decoded_rows"], [])
        self.assertIsNone(value["envelope"])
        self.assertFalse(value["HOST_contract_certified"])
        self.assertEqual(value["phase_arithmetic_RN_executed"], 0)
    def test_01_all_retained_cases_atomic(self):
        data = m.load_retained()
        for name, old in data["results"].items():
            q = m.select(name); PACK_SELECTORS[name] = deepcopy(q)
            packed = m.pack(q, model=m.MODEL); PACKS[name] = packed
            if old["status"] == "STOP":
                self.reject(packed); self.assertIsNone(packed["transport_error_cycles"])
            else:
                self.assertEqual(packed["status"], "HOST_PAIR64_WIRE_PACK_ONLY")
                e = packed["envelope"]; self.assertEqual(len(bytes.fromhex(e["payload_hex"])), 48)
                value = consume_record(name, q, e)
                self.assertEqual(value["status"], "HOST_PAIR64_WIRE_ROUNDTRIP_ONLY")
                self.assertEqual(value["transport_error_cycles"], [0,1])
                self.assertEqual(len(value["decoded_rows"]), 3)
                self.assertEqual([x["pair_uint64"] for x in value["decoded_rows"]],
                                 [x["pair_uint64"] for x in old["rows"]]+[old["relative"]["pair_uint64"]])
                self.assertTrue(all(value[k] is False for k in m.FLAGS))
        self.assertEqual(sum(x["status"] != "STOP" for x in PACKS.values()), 11)
        self.assertEqual(sum(x["status"] == "STOP" for x in PACKS.values()), 19)
    def test_02_tiny_limb_not_collapsed(self):
        q = m.select("small_SOURCE_zero_STOP"); e = m.pack(q, model=m.MODEL)["envelope"]
        value = consume_record("tiny_roundtrip", q, e)
        row = value["decoded_rows"][0]; hi,lo = [m.ieee(w) for w in row["pair_uint64"]]
        exact = F(hi)+F(lo); collapsed = F(hi+lo)
        self.assertEqual(exact, F(14)+F(1,2**56)); self.assertEqual(exact-collapsed,F(1,2**56))
        CONTROLS["wrong_float64_add_decoder"] = {"exact_pair":m.pair(exact), "collapsed_RN64":m.pair(collapsed),
                                               "lost_cycles":m.pair(exact-collapsed),
                                               "synthetic_decoder_RN64_adds":1, "production_decoder_RN64_adds":0}
        raw=bytearray(bytes.fromhex(e["payload_hex"])); raw[8:16]=(0).to_bytes(8,"little")
        self.reject(consume_record("drop_low_rehashed",q,rehash(e,bytes(raw))))
    def test_03_rehashed_words_order_endian_second_source(self):
        q=m.select(); e=m.pack(q,model=m.MODEL)["envelope"]; raw=bytes.fromhex(e["payload_hex"])
        variants={"source_swap":raw[16:32]+raw[:16]+raw[32:],
                  "high_low_swap":raw[8:16]+raw[:8]+raw[16:],
                  "each_word_big_endian":b"".join(raw[i:i+8][::-1] for i in range(0,48,8)),
                  "each_limb_big_endian":b"".join(raw[i:i+4][::-1] for i in range(0,48,4)),
                  "second_source_bit":raw[:16]+(int.from_bytes(raw[16:24],"little")^1).to_bytes(8,"little")+raw[24:],
                  "relative_bit":raw[:32]+(int.from_bytes(raw[32:40],"little")^1).to_bytes(8,"little")+raw[40:],
                  "negative_zero_low":raw[:8]+(2**63).to_bytes(8,"little")+raw[16:],
                  "singleword_padded":raw[:8]+bytes(8)+raw[16:24]+bytes(8)+raw[32:40]+bytes(8)}
        # Exact case low words are zero: this padded variant is identical, so use the tiny case.
        tq=m.select("small_SOURCE_zero_STOP"); te=m.pack(tq,model=m.MODEL)["envelope"]; tr=bytes.fromhex(te["payload_hex"])
        variants.pop("singleword_padded")
        for name, altered in variants.items():
            self.reject(consume_record(name+"_rehashed",q,rehash(e,altered)))
        lost=tr[:8]+bytes(8)+tr[16:24]+bytes(8)+tr[32:40]+bytes(8)
        self.reject(consume_record("singleword_padded_rehashed",tq,rehash(te,lost)))
    def test_04_metadata_and_nonfinite(self):
        q=m.select(); e=m.pack(q,model=m.MODEL)["envelope"]; raw=bytes.fromhex(e["payload_hex"])
        changes={"abi":"PAIR_FLOAT64_CPU_NOT_GPU_ABI","endian":"big","record_stride_bytes":8,
                 "record_count":2,"payload_bytes":24,"record_ids":["S1","S0","S0-minus-S1"],
                 "branch_ids":["S0/mirror","S0/mirror","relative"],"units":"rad",
                 "phase_contract_sha256":"0"*64,"original_scene_sha256":"0"*64,
                 "literal_request_sha256":"0"*64,"parent_request_sha256":"0"*64,
                 "result_sha256":"0"*64,"parent_receipt_sha256":"0"*64,"model":"GPU",
                 "word_layout":["lo.lo32","lo.hi32","hi.lo32","hi.hi32"],
                 "record_count_bool":True}
        for key, value in changes.items():
            altered=deepcopy(e); altered["record_count" if key=="record_count_bool" else key]=value
            self.reject(consume_record("metadata_"+key,q,altered))
        for name,word in (("nan",0x7ff8000000000001),("inf",0x7ff0000000000000)):
            self.reject(consume_record(name+"_rehashed",q,rehash(e,raw[:24]+word.to_bytes(8,"little")+raw[32:])))
    def test_05_buffer_shape_hash_and_closed_keys(self):
        q=m.select(); e=m.pack(q,model=m.MODEL)["envelope"]; raw=bytes.fromhex(e["payload_hex"])
        for name, value in (("short",raw[:-1]),("long",raw+bytes(1)),("legacy32",raw[:24])):
            self.reject(consume_record("buffer_"+name,q,rehash(e,value)))
        for name, transform in (("hash",lambda x:x.update(payload_sha256="0"*64)),
                                ("missing",lambda x:x.pop("phase_contract_sha256")),
                                ("extra",lambda x:x.update(budget_override=[1,1])),
                                ("upperhex",lambda x:x.update(payload_hex=x["payload_hex"].upper())),
                                ("nonstring",lambda x:x.update(payload_hex=bytes.fromhex(x["payload_hex"])))):
            altered=deepcopy(e); transform(altered)
            # bytes input is not JSON serializable; record its harmless typed descriptor separately.
            if name=="nonstring":
                self.reject(m.consume(q,altered,model=m.MODEL)); CONTROLS["bytes_payload_rejected"]=True
            else:
                self.reject(consume_record("buffer_"+name,q,altered))
    def test_06_selector_and_cross_case(self):
        q=m.select(); e=m.pack(q,model=m.MODEL)["envelope"]
        for key, value in (("result_sha256","0"*64),("original_scene_sha256","0"*64),
                           ("literal_request_sha256","0"*64),("case","absent"),("abi","old"),("units","rad")):
            wrong=deepcopy(q); wrong[key]=value; self.reject(consume_record("selector_"+key,wrong,e))
        wrong=deepcopy(q); wrong["case"]=False; self.reject(consume_record("selector_bool",wrong,e))
        wrong=deepcopy(q); wrong["budget_override"]=[1,1]; self.reject(consume_record("selector_cap",wrong,e))
        wrong=deepcopy(q); wrong.pop("abi"); self.reject(consume_record("selector_missing",wrong,e))
        self.reject(consume_record("wrong_model",q,e,model="old"))
        self.reject(consume_record("cross_valid_case",m.select("explicit_zero"),e))
        self.reject(consume_record("STOP_input_cannot_borrow_buffer",m.select("retained_second_SOURCE_zero_STOP"),e))
    def test_07_dependency_failure_and_copy(self):
        from unittest.mock import patch
        sealed_selector=m.select()
        with patch.object(m,"PARENT_SHA","0"*64):
            self.reject(m.pack(sealed_selector, model=m.MODEL))
        q=m.select(); old=m.load_retained(); packed=m.pack(q,model=m.MODEL); packed["envelope"]["record_ids"][0]="foreign"
        self.assertEqual(m.load_retained(),old)
        again=m.pack(q,model=m.MODEL); self.assertEqual(again["envelope"]["record_ids"][0],"S0")
        CONTROLS["sealed_parent_dependency_rejection"]=True; CONTROLS["returned_copy_no_parent_mutation"]=True
    def test_08_signed_and_caps_unchanged(self):
        for name in ("signed_reference","quotient_partial","shared_material_SOURCE_STOP","shared_material_relative_STOP"):
            q=m.select(name); old=m.load_retained()["results"][name]; packed=m.pack(q,model=m.MODEL)
            value=consume_record("literal_"+name,q,packed["envelope"])
            self.assertEqual(value["status"],"HOST_PAIR64_WIRE_ROUNDTRIP_ONLY")
            for row,parent in zip(value["decoded_rows"],old["rows"]+[old["relative"]]):
                for key in ("original_declared_cycles","total_cycle_error_bound","total_phase_bound_rad","budget_rad"):
                    self.assertEqual(row[key],parent[key])
        value=m.pack(m.select("retained_second_SOURCE_zero_STOP"),model=m.MODEL)
        self.reject(value); self.assertEqual(value["reason"],"retained_STOP_no_buffer")
if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    run=unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({"status":"PASS" if run.wasSuccessful() else "FAIL","tests":run.testsRun,
                     "data":{"selectors":SELECTORS,"pack_selectors":PACK_SELECTORS,"pack_results":PACKS,"consume_inputs":INPUTS,
                             "consume_results":CONSUMES,"consume_models":MODELS,"controls":CONTROLS}},sort_keys=True,allow_nan=False))
    raise SystemExit(0 if run.wasSuccessful() else 1)
