"""Actual own CUDA loss/Jacobian/Adam, with exact CPU geometry at every state."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--profile', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); args.out.mkdir(exist_ok=False)
    total = time.perf_counter(); costs = {}
    start = time.perf_counter()
    import numpy as np
    import torch
    from Tools.train_captured_geometry_v1 import parameters_and_bases, quantize, load_data, audit_state
    from Tools.audit_captured_pilot_result_v1 import decode, need
    from Tools.trace_indexed_scene_v1 import wire
    from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
    from Blender.blender_lab.coherent_state_graph_v1 import build_graph, propagate_graph
    from Blender.blender_lab.torch_geometry_backend_v1 import TorchGeometryBackend
    from Blender.blender_lab.torch_training_arithmetic_v1 import cross_entropy, adam_proposal
    costs['imports'] = time.perf_counter() - start
    torch.set_num_threads(1); torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    need(torch.cuda.is_available(), 'Actual NVIDIA CUDA device required')
    device = torch.device('cuda:0'); properties = torch.cuda.get_device_properties(device)
    profile = json.loads(args.profile.read_bytes()); training = json.loads((ROOT / profile['training_profile']).read_bytes())
    need(profile['runtime']['python'] == list(sys.version_info[:3]) and profile['runtime']['numpy'] == np.__version__
         and profile['runtime']['torch'] == torch.__version__ and profile['runtime']['cuda'] == torch.version.cuda,
         'Frozen actual CUDA/Python/NumPy runtime required')
    measured_uuid = subprocess.check_output(['nvidia-smi', '--query-gpu=uuid', '--format=csv,noheader'], text=True).strip()
    need(measured_uuid == profile['device_uuid'], 'Frozen physical GPU identity required')
    driver = subprocess.check_output(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'], text=True).strip()
    need(driver == profile['runtime']['nvidia_driver'], 'Frozen NVIDIA driver required')
    torch.cuda.reset_peak_memory_stats(device)
    start = time.perf_counter()
    scene = decode(json.loads((ROOT / training['scene']).read_bytes())); graph = decode(json.loads((ROOT / training['graph_result']).read_bytes()))['graph']
    parameters, bases = parameters_and_bases(scene); net = AffineGeometryNetwork(scene, graph, parameters)
    backend = TorchGeometryBackend(net, device); torch.cuda.synchronize()
    costs['exact_geometry_affine_compile_and_device_coefficients'] = time.perf_counter() - start
    train, test = training['train_indices'], training['test_indices']
    need(len(train) == 120 and len(test) == 30 and set(train).isdisjoint(test) and set(train) | set(test) == set(range(150)), 'Complete frozen split required')
    x, y, scaler = load_data(ROOT / training['dataset'], train, net.source_ids)
    start = time.perf_counter()
    inputs = torch.tensor(x[train], dtype=torch.complex128, device=device)
    labels = torch.tensor(y[train], dtype=torch.int64, device=device)
    center = np.asarray(training['untrained_center_deltas_BU']); center_gpu = torch.tensor(center, dtype=torch.float64, device=device)
    d = quantize(training['initial_deltas_BU'], bases)
    first = torch.zeros(net.count, dtype=torch.float64, device=device); second = torch.zeros_like(first)
    columns = [net.ports.index(name) for name in training['detectors']]
    torch.cuda.synchronize(); costs['input_and_training_state_upload'] = time.perf_counter() - start
    costs.update(exact_geometry_audits=0, exact_phase_preparation_and_upload=0, cuda_loss_gradient_and_proposal=0,
                 readbacks=0, cpu_matched_controls=0, cpu_native_quantization=0)
    errors = {'field': 0., 'power': 0., 'loss': 0., 'gradient': 0.}
    history = []; initial_loss = None; initial_gradient = None
    with (args.out / 'progress.jsonl').open('x', encoding='utf-8') as stream:
        for step in range(training['steps'] + 1):
            start = time.perf_counter(); audit = audit_state(net, d, step)
            costs['exact_geometry_audits'] += time.perf_counter() - start
            start = time.perf_counter(); packed = backend.upload(backend.prepare(d)); torch.cuda.synchronize()
            costs['exact_phase_preparation_and_upload'] += time.perf_counter() - start
            start = time.perf_counter()
            with torch.no_grad():
                output = backend.forward(inputs, packed)
                loss_gpu, gradient_gpu = cross_entropy(output['powers'], output['power_jacobian'], labels, columns, training['loss_temperature'])
                if step < training['steps']:
                    proposal, first, second = adam_proposal(torch.tensor(d, dtype=torch.float64, device=device), gradient_gpu, first, second,
                                                           center_gpu, step + 1, training['learning_rate_BU'], training['translation_bound_BU'])
            torch.cuda.synchronize(); costs['cuda_loss_gradient_and_proposal'] += time.perf_counter() - start
            start = time.perf_counter()
            fields = output['fields'].cpu().numpy(); powers = output['powers'].cpu().numpy()
            gradient = gradient_gpu.cpu().numpy(); loss = loss_gpu.item()
            proposed = proposal.cpu().numpy() if step < training['steps'] else None
            torch.cuda.synchronize(); costs['readbacks'] += time.perf_counter() - start
            start = time.perf_counter(); cpu_loss, cpu_gradient, cpu = net.cross_entropy(x[train], y[train], d, training['detectors'], training['loss_temperature'])
            current = {'field': float(np.max(np.abs(fields - cpu['fields']))), 'power': float(np.max(np.abs(powers - cpu['powers']))),
                       'loss': abs(loss - cpu_loss), 'gradient': float(np.max(np.abs(gradient - cpu_gradient)))}
            costs['cpu_matched_controls'] += time.perf_counter() - start
            for key, error in current.items():
                errors[key] = max(errors[key], error); need(error <= profile['cpu_parity_tolerances'][key], 'CUDA matched control failed:' + key)
            need(audit['primary_metric'] == 1, 'Exact CPU geometry state audit required')
            if initial_loss is None: initial_loss = loss; initial_gradient = gradient.copy()
            row = {'step': step, 'train_loss': loss, 'gradient_max_abs': float(np.max(np.abs(gradient))), 'deltas_BU': d.tolist(),
                   'geometry_audit': audit, 'matched_cpu_errors': current}
            history.append(row); stream.write(json.dumps(row, allow_nan=False) + '\n'); stream.flush()
            print(json.dumps({'step': step, 'train_loss': loss, 'geometry_audit': audit['primary_metric']}), flush=True)
            if proposed is not None:
                start = time.perf_counter(); d = quantize(proposed, bases)
                costs['cpu_native_quantization'] += time.perf_counter() - start
                need(np.max(np.abs(d - center)) <= training['translation_bound_BU'] + training['native_quantization_allowance_BU'], 'Native quantized proposal outside fixed box')
    start = time.perf_counter(); fd_errors = []; h = training['gradient_difference_step_BU']
    initial_d = quantize(training['initial_deltas_BU'], bases)
    for j in range(net.count):
        delta = np.eye(net.count)[j] * h
        above = net.cross_entropy(x[train], y[train], initial_d + delta, training['detectors'], training['loss_temperature'])[0]
        below = net.cross_entropy(x[train], y[train], initial_d - delta, training['detectors'], training['loss_temperature'])[0]
        fd_errors.append(abs((above - below) / (2 * h) - initial_gradient[j]))
    costs['independent_cpu_initial_finite_difference_control'] = time.perf_counter() - start
    need(max(fd_errors) <= training['gradient_absolute_tolerance'], 'Initial CUDA own gradient finite difference control')
    start = time.perf_counter()
    all_inputs = torch.tensor(x, dtype=torch.complex128, device=device)
    final = backend.forward(all_inputs, backend.upload(backend.prepare(d)), gradients=False)
    fields = final['fields'].cpu().numpy(); powers = final['powers'].cpu().numpy(); torch.cuda.synchronize()
    costs['all150_final_cuda_inference_and_readback'] = time.perf_counter() - start
    predictions = np.argmax(powers[:, columns], axis=1)
    scene_final, _ = net.materialize(d)
    start = time.perf_counter(); rebuilt = build_graph(scene_final)
    need(rebuilt['status'] == 'COMPLETE', 'Fresh final full geometric rebuild required')
    basis_fields = []
    for basis in np.eye(len(net.source_ids), dtype=complex):
        output = propagate_graph(rebuilt, {sid: [value.real, value.imag] for sid, value in zip(net.source_ids, basis)})['fields']
        basis_fields.append([output[port] for port in net.ports])
    reference = np.asarray(basis_fields).T @ x.T
    error = float(np.max(np.abs(fields - reference.T))); costs['fresh_final_cpu_geometric_rebuild_and_propagation'] = time.perf_counter() - start
    need(error <= training['field_rebuild_tolerance'], 'Actual GPU fields differ from fresh geometry')
    passed = initial_loss - loss >= training['minimum_training_loss_drop']
    report = {'schema': 'optic_neuro_blender.captured_geometry_cuda_training.v1', 'status': 'PASS' if passed else 'FAIL_LOSS_DROP',
              'profile_sha256': hashlib.sha256(args.profile.read_bytes()).hexdigest(), 'gpu_executed': True,
              'precision': 'complex128/float64', 'torch_version': torch.__version__, 'torch_cuda_runtime': torch.version.cuda,
              'device_name': properties.name, 'device_uuid': measured_uuid, 'actual_readback_verified': True,
              'nvidia_driver': driver, 'python_version': sys.version, 'numpy_version': np.__version__,
              'cuda_peak_allocated_bytes': torch.cuda.max_memory_allocated(device), 'cuda_peak_reserved_bytes': torch.cuda.max_memory_reserved(device),
              'initial_train_loss': initial_loss, 'final_train_loss': loss, 'train_correct': int(np.sum(predictions[train] == y[train])),
              'test_correct': int(np.sum(predictions[test] == y[test])), 'predictions': predictions.tolist(), 'observed_powers': powers.tolist(),
              'observed_fields_reim': np.stack([fields.real, fields.imag], axis=-1).tolist(),
              'parameter_ids': net.parameter_ids, 'parameters': parameters, 'native_base_world_x_hex': [float(base).hex() for base in bases],
              'final_deltas_BU': d.tolist(), 'final_native_world_x_hex': [float(float(base) + float(delta)).hex() for base, delta in zip(bases, d)],
              'source_ids': net.source_ids, 'ports': net.ports, 'detectors': training['detectors'], 'scaler': scaler,
              'geometry_audited_states': len(history), 'field_rebuild_max_absolute_error': error,
              'gradient_difference_max_absolute_error': max(fd_errors), 'matched_cpu_max_errors': errors,
              'autograd_used_for_training': False, 'gpu_triangle_tracing': False, 'heldout_labels_used_for_scoring_only_after_final_update': True,
              'cost_seconds': costs, 'worker_seconds': time.perf_counter() - total,
              'scope': 'Own CUDA coherent graph, manual loss/Jacobian/Adam arithmetic from captured affine geometry; CPU exact phase preparation, native quantization, all61 geometry audits and fresh rebuild. Virtual represented geometry, separate actual Blender recapture required. No AMD, physical processor, energy or total-cost superiority assumed.'}
    need(report['cuda_peak_reserved_bytes'] <= profile['limits']['cuda_peak_reserved_mib'] * 2**20, 'Owned CUDA allocation envelope exceeded')
    (args.out / 'result.json').write_bytes((json.dumps(report, indent=2, allow_nan=False) + '\n').encode())
    (args.out / 'final_virtual_scene.json').write_bytes((json.dumps(wire(scene_final), indent=2) + '\n').encode())
    (args.out / 'final_virtual_graph.json').write_bytes((json.dumps(wire(rebuilt), indent=2) + '\n').encode())
    print(json.dumps({key: report[key] for key in ('status', 'initial_train_loss', 'final_train_loss', 'test_correct', 'worker_seconds')}), flush=True)
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
