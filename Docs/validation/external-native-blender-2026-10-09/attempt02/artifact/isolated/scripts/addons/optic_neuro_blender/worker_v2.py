"""Run the own geometric model inside a separate Blender process."""
import os
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
import hashlib
import json
from pathlib import Path
import sys
import time

# The installed package is self-contained; no repository checkout is consulted.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from optic_neuro_blender.bootstrap import PACKAGE, verify_bundle
from optic_neuro_blender.runtime import canonical, digest, read_json
from optic_neuro_blender.model import capture_current, prepare, apply_positions, save_copy
from optic_neuro_blender._vendor.Tools.audit_captured_pilot_result_v1 import need
from optic_neuro_blender._vendor.Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from optic_neuro_blender._vendor.Tools.trace_indexed_scene_v1 import wire
from optic_neuro_blender._vendor.Tools.train_captured_geometry_v1 import parameters_and_bases, load_data, quantize
from optic_neuro_blender._vendor.Blender.blender_lab.scalar_scene_ingress_v1 import rational_wire
from optic_neuro_blender._vendor.Blender.blender_lab.coherent_state_graph_v1 import build_graph, propagate_graph
from optic_neuro_blender._vendor.Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
import numpy as np
import bpy


def compiled(capture, fields, out, stem):
    scene = prepare(capture, fields)
    graph = build_graph(scene)
    need(graph['status'] == 'COMPLETE', 'Recorrido geométrico incompleto; campos no publicados')
    propagated = propagate_graph(graph, fields)
    audit = audit_graph_neighborhood(wire(scene), wire({'graph': graph, **propagated}))
    need(audit['primary_metric'] == 1, 'Auditoría independiente de geometría fallida')
    (out / (stem + '_capture.json')).write_bytes(canonical(capture))
    (out / (stem + '_scene.json')).write_bytes(canonical(rational_wire(scene)))
    (out / (stem + '_graph.json')).write_bytes(canonical(wire({'graph': graph, **propagated})))
    parameters, bases = parameters_and_bases(scene)
    return scene, graph, AffineGeometryNetwork(scene, graph, parameters), bases, audit


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    request_path = Path(args[0]).resolve(); out = request_path.parent
    request = read_json(request_path, 2**20)
    need(request['schema'] == 'optic_neuro_blender.job_request.v1' and request['action'] in ('INFER', 'TRAIN'), 'Petición incompatible')
    verify_bundle()
    need(request['package_manifest_sha256'] == hashlib.sha256((PACKAGE / 'package_manifest.json').read_bytes()).hexdigest(), 'La petición corresponde a otra instalación')
    start = time.perf_counter()
    capture = capture_current()
    need(capture['state_sha256'] == request['capture_state_sha256'], 'La copia nativa no coincide con la captura solicitada')
    fields = request['fields']
    scene, graph, net, bases, audit = compiled(capture, fields, out, 'initial')
    training = None
    if request['action'] == 'TRAIN':
        profile = read_json(PACKAGE / 'data/training_profile.json')
        prior = read_json(PACKAGE / 'data/training_result.json')
        from fractions import Fraction as F
        old_bases = [F(float.fromhex(value)) for value in prior['native_base_world_x_hex']]
        # Restore the same declared untrained absolute positions, even from a trained file.
        profile['initial_deltas_BU'] = quantize([float(old + F(float(delta)) - new) for old, delta, new in zip(old_bases, profile['initial_deltas_BU'], bases)], bases).tolist()
        profile['untrained_center_deltas_BU'] = [float(old + F(float(delta)) - new) for old, delta, new in zip(old_bases, profile['untrained_center_deltas_BU'], bases)]
        profile['scene'] = str(out / 'initial_scene.json')
        profile['graph_result'] = str(out / 'initial_graph.json')
        profile['dataset'] = str(PACKAGE / 'data/iris.csv')
        dynamic_profile = out / 'native_training_profile.json'
        dynamic_profile.write_bytes(canonical(profile))
        from optic_neuro_blender._vendor.Tools import train_captured_geometry_v1 as trainer
        previous = sys.argv
        try:
            sys.argv = ['native_training', '--profile', str(dynamic_profile), '--out', str(out / 'training')]
            code = trainer.main()
        finally:
            sys.argv = previous
        need(code == 0, 'El entrenamiento no satisface sus puertas declaradas')
        training = read_json(out / 'training/result.json')
        apply_positions(training['parameters'], training['final_native_world_x_hex'])
        capture_final = capture_current()
        scene, graph, net, bases, audit = compiled(capture_final, fields, out, 'trained_native')
        saved = out / 'trained_geometry.blend'
        save_copy(saved)
    else:
        capture_final = capture
    ordered = np.asarray([[complex(*fields[source]) for source in net.source_ids]])
    output = net.forward(ordered, np.zeros(16), gradients=False)
    template = read_json(PACKAGE / 'data/training_profile.json')
    x, y, scaler = load_data(PACKAGE / 'data/iris.csv', template['train_indices'], net.source_ids)
    batch = net.forward(x, np.zeros(16), gradients=False)
    detectors = template['detectors']
    predictions = np.argmax(batch['powers'][:, [net.ports.index(port) for port in detectors]], axis=1)
    difference = None
    if training is not None:
        difference = float(np.max(np.abs(batch['powers'] - np.asarray(training['observed_powers']))))
        need(difference <= 1e-11 and predictions.tolist() == training['predictions'], 'Inferencia nativa después de entrenar difiere del resultado geométrico')
    decision_powers = {port: float(output['powers'][0, net.ports.index(port)]) for port in detectors}
    powers = output['powers'][0]
    unique = len([value for value in decision_powers.values() if value == max(decision_powers.values())]) == 1
    report = {'schema': 'optic_neuro_blender.job_result.v1', 'status': 'PASS', 'action': request['action'],
              'request_sha256': hashlib.sha256(request_path.read_bytes()).hexdigest(),
              'input_capture_state_sha256': request['capture_state_sha256'], 'final_capture_state_sha256': capture_final['state_sha256'],
              'fields': {port: [float(value.real), float(value.imag)] for port, value in zip(net.ports, output['fields'][0])},
              'powers': dict(zip(net.ports, powers.tolist())), 'input_total_normalized_power': float(np.abs(ordered).ravel() @ np.abs(ordered).ravel()),
              'decision': max(decision_powers, key=decision_powers.get) if unique and sum(decision_powers.values()) > 0 else None,
              'decision_unique': unique,
              'detectors': detectors, 'source_ids': net.source_ids, 'ports': net.ports, 'geometry_audit': audit,
              'all150_native_powers': batch['powers'].tolist(), 'all150_native_fields_reim': np.stack([batch['fields'].real, batch['fields'].imag], axis=-1).tolist(),
              'all150_encoded_inputs_reim': np.stack([x.real, x.imag], axis=-1).tolist(),
              'all150_predictions': predictions.tolist(), 'scaler': scaler,
              'training': training, 'training_native_power_max_difference': difference,
              'blender_version': bpy.app.version_string, 'blender_build_hash': bpy.app.build_hash.decode(),
              'seconds': time.perf_counter() - start, 'gpu_executed': False, 'legacy_analytic_matrix_used': False,
              'scope': 'Actual Blender coherent geometry inference and optional own geometry training; scalar BU model, exploratory UI, local execution, no physical or external certification'}
    temporary = out / 'result.pending.json'
    temporary.write_bytes(canonical(report)); temporary.replace(out / 'result.json')
    print(json.dumps({'status': 'PASS', 'action': request['action'], 'seconds': report['seconds'], 'decision': report['decision']}), flush=True)


if __name__ == '__main__':
    main()
