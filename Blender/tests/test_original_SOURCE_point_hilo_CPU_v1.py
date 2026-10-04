"""New original-fixture point transport coverage; no scene query or native renderer."""
from pathlib import Path
from fractions import Fraction as F
import base64,copy,hashlib,json,struct,zlib
from Blender.benchmarks.capacity_audit import oblique_exact_scalar_hilo32_CPU_v1 as codec

ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-TRANSPORT-ORIGINAL-JOIN-AUDIT-001-CODEX.json"
SHA="eee52220549e3a1fc1cb31c5e0d06fb1b65a752574469d7cc6d542176bb66ae7"
ORIGINAL="coordinacion/respuestas/PRECISION-ORIGIN-BOX-ZERO-CPU-001-CODEX.json"
ANCHOR="coordinacion/respuestas/PRECISION-OBLIQUE-EXISTING-EVIDENCE-INVENTORY-HOST-001-CODEX.json"

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def capture(c):
    dec=zlib.decompressobj()
    raw=dec.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),1048577)
    assert dec.eof and not dec.unused_data and not dec.unconsumed_tail and len(raw)<=1048576
    assert c["rc"]==0 and not c["timed_out"] and len(raw)==c["stdout_bytes"]
    assert hashlib.sha256(raw).hexdigest()==c["stdout_sha256"]
    return json.loads(raw)

def slot_identity(row):
    # Test-only identity, pinned CPU fixture labels; NOT an authentication API.
    return {k:row[k] for k in ("case","source_id","scene_sha256","query_sha256",
       "input_sha256","previous_primitive_id","saved_point_bounds",
       "CPU_declared_error_budget","point_words","point_wire_hex")}

def run():
    raw=(ROOT/PARENT).read_bytes()
    assert len(raw)==209738 and hashlib.sha256(raw).hexdigest()==SHA
    parent=json.loads(raw);pins=dict(parent["code_doc_sha256"]);pins[PARENT]=SHA
    assert len(pins)==450
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    original=capture(json.loads((ROOT/ORIGINAL).read_bytes())["test_run"])["original_evidence"]
    anchors=capture(json.loads((ROOT/ANCHOR).read_bytes())["test_run"])["evidence"]["original"]["anchor_cases"]
    assert len(original)==12 and len(anchors)==6
    rows=[];encoder_calls=0;packet_audits=0
    for source in original:
        anchor=next(a for a in anchors if a["case"]==source["case"])
        assert anchor["source_ids"]==["S0","S1"]
        assert (source["scene_sha256"],source["query_sha256"],source["input_sha256"])==(
            anchor["scene_sha256"],anchor["query_sha256"],anchor["input_buffer_sha256"])
        assert source["source_id"] in anchor["source_ids"]
        assert source["result"]["CPU_box_zero_contact_proved"]is True
        assert source["old_ledger_SOURCE_decision_retained"]["status"]=="STOP_UNRESOLVED_ALL_PRIMITIVES"
        packets=[]
        for lower,upper in source["point_bounds"]:
            assert lower==upper  # No midpoint choice, widening, snap or invented point.
            packet=codec.encode_scalar(lower);encoder_calls+=1
            checked=codec.audit_packet(packet);encoder_calls+=1;packet_audits+=1
            assert checked==packet and packet["status"]=="EXACT_PAIR_CPU_ONLY"
            assert packet["residual_exact"]==[0,1]
            assert packet["native_origin_box_bound"]is None
            packets.append(packet)
        words=[w for packet in packets for w in (packet["hi_word"],packet["lo_word"])]
        wire=struct.pack("<6I",*words)
        assert len(wire)==24
        assert wire.hex()=="".join(packet["wire_hex"]for packet in packets)
        recovered=[codec.decode32(words[2*i])+codec.decode32(words[2*i+1])for i in range(3)]
        assert [[codec.pair(x),codec.pair(x)]for x in recovered]==source["point_bounds"]
        row={k:copy.deepcopy(source[k])for k in ("case","source_id","scene_sha256",
            "query_sha256","input_sha256","previous_primitive_id")}
        row.update(saved_point_bounds=copy.deepcopy(source["point_bounds"]),
            saved_direction_bounds=copy.deepcopy(source["direction_bounds"]),
            saved_triangle_words=copy.deepcopy(source["triangle_words"]),
            source_record_sha256=digest(source),scalar_packets=packets,point_words=words,
            point_wire_hex=wire.hex(),point_wire_sha256=hashlib.sha256(wire).hexdigest(),
            CPU_declared_error_budget=[[[0,1],[0,1]]for _ in range(3)],
            status="SOURCE_TAGGED_CPU_FIXTURE_POINT_ROUNDTRIP_ONLY",
            binding_authenticated=False,native_point_budget_authenticated=False,
            GPU_launch_allowed=False,launch_exclusion_allowed=False,nearest_hit_certified=False,
            phase_certified=False,phase_error_bound=None,full_costs="UNKNOWN_NOT_ZERO")
        row["CPU_slot_binding_sha256"]=digest(slot_identity(row))
        rows.append(row)
    negatives=[]
    for row in rows:
        for kind in ("SOURCE_swap","scene_substitution","previous_id_substitution","budget_substitution"):
            changed=copy.deepcopy(row)
            if kind=="SOURCE_swap":changed["source_id"]="S1"if row["source_id"]=="S0"else "S0"
            if kind=="scene_substitution":changed["scene_sha256"]="0"*64
            if kind=="previous_id_substitution":changed["previous_primitive_id"]+=1
            if kind=="budget_substitution":changed["CPU_declared_error_budget"][0][1]=[1,1]
            # Recompute, rather than merely detect a stale checksum.
            changed["CPU_slot_binding_sha256"]=digest(slot_identity(changed))
            assert changed["CPU_slot_binding_sha256"]!=row["CPU_slot_binding_sha256"]
            assert slot_identity(changed)!=slot_identity(row)
            negatives.append(dict(case=row["case"],source_id=row["source_id"],kind=kind,
                expected_binding_sha256=row["CPU_slot_binding_sha256"],
                changed_binding_sha256=changed["CPU_slot_binding_sha256"],status="REJECT_DIFFERENT_FIXED_CPU_SLOT"))
    for anchor in anchors:
        group=[r for r in rows if r["case"]==anchor["case"]]
        assert len(group)==2 and sorted(r["source_id"]for r in group)==["S0","S1"]
        assert group[0]["point_wire_hex"]==group[1]["point_wire_hex"]
        assert group[0]["CPU_slot_binding_sha256"]!=group[1]["CPU_slot_binding_sha256"]
    assert len({r["CPU_slot_binding_sha256"]for r in rows})==12
    groups={}
    for row in rows:groups.setdefault(row["point_wire_sha256"],[]).append([row["case"],row["source_id"]])
    assert sorted(len(v)for v in groups.values())==[4,8]
    assert len(negatives)==48 and encoder_calls==72 and packet_audits==36
    return dict(status="PASS_NEW_ORIGINAL_CPU_FIXTURE_POINT_ROUNDTRIP_SOURCE_SEPARATION_ONLY",
        context_pins=pins,rows=rows,negative_fixed_slot_substitutions=negatives,
        equal_wire_SOURCE_groups=groups,
        summary=dict(original_cases=6,source_rows=12,scalar_packets=36,point_wire_bytes_per_SOURCE=24,
            total_point_wire_bytes_without_deduplication=288,valid_encoder_calls_including_packet_audits=72,
            packet_consistency_checks=36,fixed_slot_substitutions_rejected=48,
            distinct_point_wires=2,distinct_CPU_slot_bindings=12,context_pins=450),
        previous_synthetic_transport_rows_unchanged=19,native_original_transport_joins=0,
        original_query_replays=0,new_geometric_evaluations=0,old_runner_or_producer_executions=0,
        GPU_used=False,Bpy_used=False,RT_used=False,launch_exclusion_allowed=False,
        native_point_budget_authenticated=False,phase_error_bound=None,full_costs="UNKNOWN_NOT_ZERO",
        prior_zero_error_gate=parent["prior_zero_error_gate"])

if __name__=="__main__":print(json.dumps(run(),sort_keys=True))
