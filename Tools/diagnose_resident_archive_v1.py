"""CPU ablation on immutable native readbacks; never claims native GPU repair."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
ARCHIVE=ROOT/"Docs/validation/native-resident-graph-2026-10-09/attempt03/worker"


def replay(graph,rows,inputs,source_ids):
    coefficients=[(complex(*row["first_reim"]),complex(*row["second_reim"])) for row in rows]
    if len(rows)!=len(graph["nodes"]) or graph["status"]!="COMPLETE":
        raise ValueError("Complete matching archive required")
    def sum_complex(values):
        return complex(math.fsum(v.real for v in values),math.fsum(v.imag for v in values))
    all_fields,traces=[],[]
    for sample in inputs:
        incoming=[[] for _ in rows];outputs=[[] for _ in graph["ports"]];trace=[]
        for root in graph["roots"]:
            incoming[root["node"]].append(sample[source_ids.index(root["source_id"])])
        for index in graph["topological_order"]:
            node=graph["nodes"][index];row=rows[index]
            if node["hit_object"]!=row["object"] or row["primitive_id"] not in node["coincident_primitives"]:
                raise ValueError("Archived selected surface differs")
            value=sum_complex(incoming[index]);first,second=[c*value for c in coefficients[index]]
            for edge in node["edges"]:
                incoming[edge["target"]].append(second if edge["event"]=="r" else first)
            if "terminal" in node:
                outputs[graph["ports"].index(node["terminal"])].append(first)
            trace.append({"state_id":index,"surface":row["object"],"primitive_id":row["primitive_id"],
                          "incoming_hex":[value.real.hex(),value.imag.hex()],
                          "coefficient_hex":[[c.real.hex(),c.imag.hex()] for c in coefficients[index]],
                          "first_hex":[first.real.hex(),first.imag.hex()],"second_hex":[second.real.hex(),second.imag.hex()]})
        all_fields.append([sum_complex(v) for v in outputs]);traces.append(trace)
    return np.asarray(all_fields),traces


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    def load(name):return json.loads((ARCHIVE/name).read_text(encoding="utf-8"))
    graph=load("actual_graph.json");observed=load("coherence_control_observations_before_gate.json")
    local=load("actual_local_coefficient_readback.json")
    prior=json.loads((ROOT/"Docs/validation/native-deferred-training-2026-10-09/attempt01/worker/result.json").read_text(encoding="utf-8"))
    complex_array=lambda x:np.asarray(x)[...,0]+1j*np.asarray(x)[...,1]
    fields,traces=replay(graph,local["rows"],complex_array(observed["inputs_reim"]),prior["source_ids"])
    cpu,gpu=complex_array(observed["cpu_fields_reim"]),complex_array(observed["gpu_fields_reim"])
    rounded=fields.real.astype(np.float32).astype(np.float64)+1j*fields.imag.astype(np.float32).astype(np.float64)
    difference=float(np.max(np.abs(fields-cpu)))
    report={"schema":"neuro3d.resident.archive_diagnostic.v1","id":"EXP-006-RESIDENT-ARCHIVE-DIAG-20261012-001",
            "gpu_coefficients_cpu_replay_vs_archived_cpu_max_field":difference,
            "gpu_coefficients_cpu_replay_vs_archived_gpu_max_field":float(np.max(np.abs(fields-gpu))),
            "rounded_final_replay_exactly_matches_archived_gpu":bool(np.array_equal(rounded,gpu)),
            "rounded_final_max_error":float(np.max(np.abs(rounded-gpu))),
            "fixed_field_budget":1e-11,"coefficient_cpu_replay_pass":difference<=1e-11,
            "states":len(graph["nodes"]),"controls":len(fields),
            "source_pins":{name:hashlib.sha256((ARCHIVE/name).read_bytes()).hexdigest() for name in
                           ("actual_graph.json","actual_local_coefficient_readback.json","coherence_control_observations_before_gate.json")},
            "first_native_divergence":None,"cause":"UNKNOWN_WITHOUT_NATIVE_STAGE_TRACE",
            "scope":"Actual historical GPU coefficients replayed in CPU binary64. This ablation does not run, repair or accept a GPU shader; archived tolerances and failures are unchanged."}
    for name,value in (("result.json",report),("cpu_replay_traces.json",traces)):
        (args.out/name).write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(report))


if __name__=="__main__":main()
