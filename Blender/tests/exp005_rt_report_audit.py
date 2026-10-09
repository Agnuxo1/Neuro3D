"""CPU-only arithmetic/schema audit of retained peer RT timings, not rerun."""
import argparse
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

ROOT = Path(__file__).parents[2]
PEER = NEURO3D_COGNITION / 'neuro3d/rt'


def positive(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('positive finite measurement required')
    return value


def integer(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError('positive integer required')
    return value


def recalculate(rt, brute, brute_resolution):
    resolution, spp = integer(rt['RES']), integer(rt['spp'])
    rays = resolution*resolution*spp
    if rt['rays'] != rays or resolution != brute_resolution:
        raise ValueError('nominal workload metadata mismatch')
    base = [positive(t) for t in rt['base_T2_s']]
    if len(base) != 4 or rt['base_fixed_s'] != min(base[1:]):
        raise ValueError('baseline rule drift')
    br = {integer(row['T']): row for row in brute}
    if len(br) != len(brute) or len({row['T'] for row in rt['rows']}) != len(rt['rows']):
        raise ValueError('duplicate sizes')
    if set(br) != {row['T'] for row in rt['rows']}:
        raise ValueError('paired sizes required')
    rows = []
    brute_rays = brute_resolution**2
    for row in rt['rows']:
        size = integer(row['T']); b = br[size]
        first, build = positive(row['t1_s']), positive(row['python_build_s'])
        hot = [positive(x) for x in row['t2plus_s']]
        if len(hot) != 3: raise ValueError('three retained hot samples required')
        trace = positive(min(hot)-rt['base_fixed_s'])
        brute_s = positive(b['ms_median'])/1000.
        rt_rate, br_rate = rays/trace/1e6, brute_rays/brute_s/1e6
        checks = {'trace_only_s': abs(trace-row['trace_only_s']),
            'bvh_plus_first_s': abs((first-rt['base_fixed_s'])-row['bvh_plus_first_s']),
            'rt_rate': abs(rt_rate-row['Mrays_s_trace_only'])/rt_rate,
            'brute_rate': abs(br_rate-b['Mrays_s'])/br_rate,
            'brute_tests': abs(br_rate*size-b['Mtests_s'])/(br_rate*size)}
        if any(v > 1e-9 for v in checks.values()): raise ValueError('derived peer numbers inconsistent')
        raw_hot_rate = rays/statistics.median(hot)/1e6
        denom = 1/(br_rate*1e6)-1/(rt_rate*1e6)
        # Reproduce peer's conditional projection; not a measured crossing.
        projected = None if denom <= 0 else first/denom
        rows.append({'triangles': size, 'arithmetic_checks': checks,
            'rt_hot_samples_s': hot, 'rt_hot_min_s': min(hot), 'rt_hot_median_s': statistics.median(hot),
            'rt_nominal_rate_subtracted_min_Mrays_s': rt_rate,
            'rt_nominal_rate_raw_median_Mrays_s': raw_hot_rate,
            'brute_kernel_median_s': brute_s, 'brute_rate_Mrays_s': br_rate,
            'peer_derived_ratio': rt_rate/br_rate, 'raw_hot_median_ratio': raw_hot_rate/br_rate,
            'rt_python_build_plus_first_render_s': build+first,
            'brute_spp_times_single_batch_s_PROJECTION': spp*brute_s,
            'peer_break_even_rays_PROJECTION': projected,
            'coverage_only_at_this_size': row.get('check')})
    coverage = [r['coverage_only_at_this_size'] for r in rows if r['coverage_only_at_this_size'] is not None]
    for check in coverage:
        if check['pixels'] != resolution**2: raise ValueError('coverage dimensions mismatch')
        for key in ('brute_covered', 'cycles_covered'):
            if isinstance(check[key], bool) or not isinstance(check[key], int) or not 0 <= check[key] <= check['pixels']:
                raise ValueError('invalid coverage count')
        if not 0 <= check['disagree']['as_is'] <= check['pixels']: raise ValueError('invalid disagreement')
    return {'rows': rows, 'rt_nominal_samples_per_render': rays, 'brute_pixel_center_rays_per_batch': brute_rays,
        'coverage_cases': len(coverage), 'coverage_disagreement_fraction':
            None if not coverage else coverage[0]['disagree']['as_is']/coverage[0]['pixels']}


def audit():
    paths = [PEER/n for n in ('rt_final.json', 'brute_same.json', 'rt_cycles.py', 'brute_same.py', 'make_report.py')]
    paths += [ROOT/'coordinacion/respuestas/RT-CYCLES-VS-BRUTA-CLAUDE-2026-09-30.md']
    raw = {}
    for path in paths:
        if path.stat().st_size > 256*1024: raise ValueError('bounded report/script reader only')
        raw[path.name] = path.read_bytes()
    brute_ast = ast.parse(raw['brute_same.py'])
    resolutions = [n.value.value for n in brute_ast.body if isinstance(n, ast.Assign) and
        any(isinstance(t, ast.Name) and t.id == 'RES' for t in n.targets) and isinstance(n.value, ast.Constant)]
    if len(resolutions) != 1: raise ValueError('static brute resolution not uniquely defined')
    def generator(source):
        functions = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'tris']
        if len(functions) != 1: raise ValueError('static generator required')
        return ast.dump(functions[0], include_attributes=False)
    result = recalculate(json.loads(raw['rt_final.json']), json.loads(raw['brute_same.json']), resolutions[0])
    result.update(scope='CPU arithmetic + current-source inspection; NO GPU rerun/backend certification',
        peer_current_file_sha256={str(p): hashlib.sha256(raw[p.name]).hexdigest() for p in paths},
        triangle_generator_AST_equal=generator(raw['rt_cycles.py']) == generator(raw['brute_same.py']),
        limitations=['Current hashes are retention fingerprints, NOT historical code/data/backend linkage',
            'Pixel*spp is nominal sampling count, not measured hardware intersection counter',
            'Cycles multisample rendered coverage differs from deterministic pixel-center nearest-z output',
            'Only T1000 coverage counts retained; no per-ray ID/depth/length/phase parity at other sizes',
            'RT min minus baseline versus brute median is not paired equal-work end-to-end speedup',
            'Subtracted baseline contains two triangles, not proven pure fixed overhead',
            'Cold first includes sync/render/BVH; not isolated BVH time; projections assume linear ray scaling',
            'No retained device/backend proof, outer guard/job envelope or all brute timing samples in these JSONs',
            'Standalone RT script RAM2.5GiB floor insufficient for Codex policy; no rerun authorized',
            'No coherent fields, Neuro3D capacity, RT integration or optical physical advantage certified'])
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('new evidence required')
    result = audit()
    files = [Path(__file__), Path(__file__).with_name('test_exp005_rt_report.py')]
    result['own_code_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'rows': len(result['rows']), 'coverage_cases': result['coverage_cases'],
        'generators_equal': result['triangle_generator_AST_equal'],
        'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
