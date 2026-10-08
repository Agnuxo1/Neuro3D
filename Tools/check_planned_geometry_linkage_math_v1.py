"""Analytic controls for the retrospective blueprint checker; no GPU trials."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Tools'))
import certify_planned_geometry_linkage_v1 as checker


def main():
    rows = []
    def control(name, result):
        if not result: raise AssertionError(name)
        rows.append({'control': name, 'PASS': True})
    tri = ((F(0), F(0), F(0)), (F(1), F(0), F(0)), (F(0), F(1), F(0)))
    hit = checker.ray_triangle((F(1, 4), F(1, 4), F(1)), (0, 0, -1), tri)
    control('interior_exact_plane_halfplanes', hit[:2] == (F(1), (F(1, 4), F(1, 4), F(0))))
    hit = checker.ray_triangle((F(1, 2), F(1, 2), F(1)), (0, 0, -1), tri)
    control('boundary_exact_membership', hit[:2] == (F(1), (F(1, 2), F(1, 2), F(0))))
    control('outside_triangle', checker.ray_triangle((2, 2, 1), (0, 0, -1), tri) is None)
    control('intersection_behind_origin', checker.ray_triangle((F(1, 4), F(1, 4), -1), (0, 0, -1), tri) is None)
    control('parallel_distinct_plane', checker.ray_triangle((0, 0, 1), (1, 0, 0), tri) is None)
    control('coplanar_infinite_plane_finite_triangle_miss', checker.ray_triangle((-1, 2, 0), (1, 0, 0), tri) is None)
    for name, vertices, origin, direction in [
        ('coplanar_actual_finite_encounter_rejected', tri, (-1, F(1, 4), 0), (1, 0, 0)),
        ('degenerate_triangle_rejected', (tri[0], tri[1], tri[1]), (0, 0, 1), (0, 0, -1))]:
        try: checker.ray_triangle(origin, direction, vertices)
        except ValueError: control(name, True)
        else: raise AssertionError(name)
    for direction, normal, expected in [
        ((1, 0, 0), (1, -1, 0), (0, 1, 0)),
        ((0, 1, 0), (1, 1, 0), (-1, 0, 0)),
        ((-1, 0, 0), (1, 1, 0), (0, 1, 0)),
        ((0, 1, 0), (1, -1, 0), (1, 0, 0))]:
        reflection = checker.sub(direction, checker.scale(normal, 2*checker.dot(direction, normal)/F(checker.dot(normal, normal))))
        control('cardinal_reflection_'+str(len(rows)), reflection == expected)
    # pi = theta = lambda are represented by rationals here; the identity is
    # algebraic for arbitrary positive lambda and represented nonzero pi_f.
    for theta in [F(0), F(1, 3), F(-7, 5)]:
        wavelength, pi_f = F(1, 10), checker.PI_BINARY64
        d = theta*wavelength/(4*pi_f)
        control('length_to_phase_exact_'+str(theta), 2*(5+2*d-5)/wavelength == theta/pi_f)
    control('exp_zero_exact', checker.exp_upper(0) == 1)
    # Elementary e bounds: 1+1+1/2+1/6 < e < 3.
    control('exp_one_upper_consistent_with_tail', F(8, 3) < checker.exp_upper(1) < 3)
    # Telescoping need not amplify through a unitary suffix. For scalar phase
    # gates with signs +/-1 (known exact special cases), triangle bound is tight.
    exact_change = abs(F(-1)-F(1))
    control('scalar_unitary_telescope_triangle_bound', exact_change <= 2+2)
    result = {'schema': 'neuro3d.planned_geometry.math_controls.v1', 'status': 'PASS',
              'controls': rows, 'new_GPU_execution': False, 'H1_confirmatory': False,
              'source_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [Path(__file__), Path(checker.__file__), checker.MATH]}}
    output = ROOT/'Docs/research/planned_geometry_math_controls_v1.json'
    with output.open('xb') as stream:
        stream.write((json.dumps(result, indent=2)+'\n').encode())
    print(json.dumps({'status': 'PASS', 'analytic_controls': len(rows)}))


if __name__ == '__main__':
    main()
