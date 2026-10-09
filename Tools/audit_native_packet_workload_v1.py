"""Frozen secondary structural audit and CPU-only exact packet replay."""
import argparse, hashlib, json, math, struct, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Blender.blender_lab.native_graphics_gradient_v2 import uniform_bytes, exact_double
from Blender.blender_lab.optical_uniform_packet_v1 import optical_uniform_bytes
from Tools.audit_captured_pilot_result_v1 import decode, need


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(exist_ok=False)
    profile = json.loads(args.profile.read_bytes())
    for name, pin in profile['pins'].items():
        need(sha(ROOT / name) == pin, 'Frozen packet source mismatch: ' + name)
    start = time.perf_counter()
    trace = json.loads((ROOT / profile['trace']).read_bytes())
    old = decode(json.loads((ROOT / profile['trace_graph']).read_bytes()))
    old = old.get('graph', old)
    graph = decode(json.loads((ROOT / profile['graph']).read_bytes()))
    stages = json.loads((ROOT / profile['stages']).read_bytes())
    surface = json.loads((ROOT / profile['surface']).read_bytes())
    result = json.loads((ROOT / profile['scaling_result']).read_bytes())
    need(result['primary_metric'] == 1 and len(result['results']) == 6, 'Complete six-arm producer required')
    need(len(old['nodes']) == len(graph['nodes']) == 133, 'Complete represented graphs required')
    for a, b in zip(old['nodes'], graph['nodes']):
        for key in ('origin', 'direction', 'previous_plane', 'hit_object', 'edges'):
            need(a[key] == b[key], 'Historical trace and actual scaling geometry must match: ' + key)
    for batch in trace['batches']:
        need(batch['query_count'] == len(batch['node_ids']) * 150 == len(batch['incoming_reim']), 'Actual input trace extent required')
    need(sum(len(b['node_ids']) for b in trace['batches']) == 133 and len(trace['batches']) == 36, 'Every represented state exactly once required')
    sizes = profile['batch_sizes']
    chunks = queries = 0
    for size in sizes:
        for offset in range(0, size, 150):
            n = min(150, size - offset)
            chunks += 2 * sum(math.ceil(len(b['node_ids']) * n / 256) for b in trace['batches'])
            queries += 2 * 133 * n
    counts = stages['per_stage_counts']
    fills = len(surface['fills'])
    selectors = surface['native_triangle_surface_queries']
    need(chunks == counts['deferred_fullscreen_optical_draw'] == counts['deferred_fullscreen_derivative_echo_draw'], 'Exact deferred draw count required')
    need(fills == counts['instanced_triangle_draw'] == counts['derivative_echo_triangle_draw'], 'Exact selector draw count required')
    need(queries * 2 == surface['optical_fragment_queries_including_echo'], 'Exact optical fragment count required')
    need(chunks + fills == counts['ray_UBO_creation'] == counts['ray_textures_and_framebuffer_creation'], 'Exact actual packet allocation count required')
    total = chunks + fills
    structural = {
        'optical_chunks': chunks, 'selector_chunks': fills, 'all_chunks': total,
        'optical_queries_before_echo': queries, 'actual_selector_queries': selectors,
        'logical_ubo_bytes': total * 32768,
        'source_derived_integer_glReadPixels_calls': total * 6,
        'source_derived_float_texture_reads': total * 2,
        'logical_integer_readback_bytes': (queries + selectors) * 96,
        'logical_float_readback_bytes': (queries + selectors) * 32,
        'source_derived_texture_creations': chunks * 8 + fills * 7,
        'scope': 'Counts reconciled with actual GL stage and surface receipts; byte extents derived from frozen source. These are logical API payloads, not measured PCIe traffic, physical bandwidth, or causal runtime attribution.'}
    # Signed zeros, smallest subnormal, extreme finite values, and exact edge extents.
    adverse = [0., -0., math.ulp(0.), -math.ulp(0.), sys.float_info.max, -sys.float_info.max, 1., -1.]
    for n in (1, 255, 256):
        rows = [[adverse[(i + j) % len(adverse)] for j in range(14)] for i in range(n)]
        need(uniform_bytes(rows, 14) == optical_uniform_bytes(rows), 'Adversarial packet byte parity required')
    rejected = 0
    for rows in ([], [[0.] * 14] * 257, [[0.] * 13], [[float('nan')] * 14], [[float('inf')] * 14], [[-float('inf')] * 14]):
        for function in (uniform_bytes, optical_uniform_bytes):
            try:
                function(rows, 14)
            except ValueError:
                rejected += 1
            else:
                raise ValueError('Both packet implementations must reject invalid declared inputs')
    measurements = []
    all_equal = True
    # The replay uses archived incoming fields, cyclic rows and exact quarter turns.
    # It reproduces chunk shapes; it is NOT a transcript of the scaling producer.
    for size in sizes:
        for repetition in range(2):
            order = ['original', 'vectorized'] if repetition == 0 else ['vectorized', 'original']
            elapsed = dict.fromkeys(order, 0.)
            hashes = {name: hashlib.sha256() for name in order}
            packet_count = 0
            for offset in range(0, size, 150):
                n = min(150, size - offset)
                for batch in trace['batches']:
                    rows = []
                    for local, node_id in enumerate(batch['node_ids']):
                        node = graph['nodes'][node_id]
                        geometry = [exact_double(v) for v in (*node['origin'], *node['direction'])]
                        for sample in range(n):
                            index = (offset + sample) % 150
                            z = complex(*batch['incoming_reim'][local * 150 + index])
                            z *= (1, 1j, -1, -1j)[(offset + sample) % 4]
                            rows.append([*geometry, z.real, z.imag, exact_double(graph['wavelength']), 0., 0., 0., 0., 0.])
                    for lane in range(0, len(rows), 256):
                        packet = {}
                        for name in order:
                            before = time.perf_counter()
                            packet[name] = (uniform_bytes if name == 'original' else optical_uniform_bytes)(rows[lane:lane + 256], 14)
                            elapsed[name] += time.perf_counter() - before
                            hashes[name].update(packet[name])
                        all_equal &= packet['original'] == packet['vectorized']
                        packet_count += 1
            need(all_equal and hashes['original'].digest() == hashes['vectorized'].digest(), 'Every replayed packet byte must match')
            measurements.append({'batch_size': size, 'repetition': repetition, 'order': order, 'packet_count': packet_count,
                                 'packet_generation_seconds': elapsed, 'replay_packet_sha256': hashes['original'].hexdigest(), 'byte_identical': True})
    need(sum(r['packet_count'] for r in measurements) == chunks, 'Replay must reproduce every optical chunk extent')
    report = {'schema': 'optic_neuro_blender.native_packet_workload.v1', 'status': 'VALID_STRUCTURAL_COUNTS_AND_EXACT_PACKET_REPLAY',
              'primary_metric': 1, 'profile_sha256': sha(args.profile), 'structural': structural, 'measurements': measurements,
              'invalid_input_rejections': rejected, 'signed_zero_and_subnormal_parity': True, 'seconds': time.perf_counter() - start,
              'gpu_requested': False, 'gpu_integration_validated': False,
              'scope': 'CPU-only secondary synthetic packet replay from archived actual fields and matching rays. Packing timings exclude input-list construction, digest checks, allocation/upload/driver/readback/merges. No total GPU speedup, causal cost fraction, new generalization, or physical bandwidth claim.'}
    (args.out / 'result.json').write_bytes((json.dumps(report, indent=2, allow_nan=False) + '\n').encode())
    print(json.dumps({'status': report['status'], 'seconds': report['seconds'], 'structural': structural}))


if __name__ == '__main__':
    main()
