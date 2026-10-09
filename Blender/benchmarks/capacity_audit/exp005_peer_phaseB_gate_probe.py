"""Replay ONE reviewed AST expression, never execute/import peer writer.

Synthetic result-data adversary: missing all groups plus a recorded error.
This checks report-gate semantics, not an actual omitted scene or GPU result.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[3]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

PEER = NEURO3D_COGNITION / 'neuro3d/p0_scene_gpu/p03_harness_v2.py'
SHA = '1328b01307fb467bc4bf3d69886f01d5839c6d86ab92495ecf7056294f6b446e'


def audit():
    if hashlib.sha256(PEER.read_bytes()).hexdigest() != SHA:
        raise ValueError('review changed peer code before AST evaluation')
    tree = ast.parse(PEER.read_text(encoding='utf-8'))
    assignment = next(n for n in tree.body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == 'res'
        and isinstance(t.slice, ast.Constant) and t.slice.value == 'gate_results' for t in n.targets))
    # This exact pinned dictionary expression has only all/max/dict.get calls.
    gates = {'field_vs_oracle': 1e-10, 'conf1_vs_oracleB': 1e-9,
             'global': 1e-4, 'strict_control': 1e-8}
    synthetic = {'max_diff_vs_my_oracle': 0., 'max_diff_vs_codex': 0.,
                 'conf1': {'max_diff_vs_oracleB': 0.}, 'negatives': [{'aborted': True}]*4,
                 'errors': [{'group': 'omitted due to exception'}], 'groups': [], 'scenes_valid': 104}
    output = eval(compile(ast.Expression(assignment.value), '<reviewed-gate-expression>', 'eval'),
                  {'__builtins__': {}, 'all': all, 'max': max, 'res': synthetic, 'GATES': gates})
    if not all(output.values()): raise AssertionError('expected report-gate counterexample changed')
    return {'peer_script_sha256': SHA, 'synthetic_result': synthetic,
            'actual_gate_expression_result': output,
            'all_gate_values_true_despite_error_and_empty_groups': all(output.values()),
            'strict_control_used_in_gate_dictionary': any(isinstance(n, ast.Constant)
                and n.value == 'strict_control' for n in ast.walk(assignment.value)),
            'scope': 'single pinned AST gate expression only; no peer imports/writers, CUDA or factual omitted scene',
            'native_promotion_allowed': False, 'no_jev_aval': True}


if __name__ == '__main__': print(json.dumps(audit(), indent=2))
