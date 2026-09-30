"""Bounded independent-field replay; never imports the peer's writer script.

Only two reviewed, SHA-pinned pure function definitions are compiled from
field_check.py. No imports, decorators, defaults, top-level loops or writes
from that script execute. Geometry oracle my_trace.py is separately pinned.
This is a synthetic float64 CPU check, not a native precision certificate.
"""
import argparse
import ast
import cmath
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PEER = Path('D:/PROJECTS/.cognition/neuro3d/trace_oracle_claude')
RESPONSE = ROOT.parent / 'coordinacion/respuestas/FIELD-ORACLE-CLAUDE.json'
PINS = {
    RESPONSE: 'c54d1f2d5a5146b75c028431aefaa766f93b789ff1f45b91480052de793aac23',
    PEER/'field_check.py': '6a67b672f28e8a442eeb3e795a08def564f3f3ffcdf79eb14523a3a19e50c558',
    PEER/'field_result.json': '871a0bf915c099dfcf4db9910bc1053e4bdb429b748214b99c4f5869eeb247c2',
    PEER/'my_trace.py': '320f25d7bb5c44203cc0d0201095cc8ef2d092ed432d014f94ad860ee2c65ad2',
    ROOT/'benchmarks/capacity_audit/history_fields_cpu_v1.py': '41d38c8c7f1bd56764728f50a3951ea4baa60fbe18ebadb316d497c553ec831c',
    ROOT/'benchmarks/capacity_audit/history_lengths_cpu_v1.py': 'af48ff659152b5055bb4b3091ccdfa5655d995a0fb7bf607c784f243ae912ce3',
    ROOT/'benchmarks/capacity_audit/history_trace_cpu_v1.py': '92ca7ddb64d95afc3205ddcfb129a5a129a9b5255ff51daf9917c0cceb9c1346',
}
PEER_TOL = 1e-10
ANALYTIC_TOL = 1e-13


def verify_pins():
    for path, expected in PINS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('changed pinned input: '+str(path))


def peer_functions():
    verify_pins()
    spec = importlib.util.spec_from_file_location('reviewed_peer_trace', PEER/'my_trace.py')
    peer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(peer)
    tree = ast.parse((PEER/'field_check.py').read_text(encoding='utf-8'))
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                   and node.name in {'my_fields', 'owner_of'}]
    if [node.name for node in definitions] != ['my_fields', 'owner_of']:
        raise ValueError('reviewed function set changed')
    for node in definitions:
        if node.decorator_list or node.args.defaults or node.args.kw_defaults:
            raise ValueError('definition-time evaluation prohibited')
    selected = ast.Module(body=definitions, type_ignores=[])
    namespace = {'math': math, 'cmath': cmath,
                 **{name: getattr(peer, name) for name in ('my_trace','Abort','fr','cross','dot')}}
    exec(compile(selected, str(PEER/'field_check.py')+'#reviewed-pure-functions', 'exec'), namespace)
    return namespace['my_fields'], hashlib.sha256(ast.dump(selected).encode()).hexdigest()


def compare_complete(codex, peer):
    """Compare every nonempty port/group, paths, fields and intensity explicitly."""
    wanted = {(p,g) for p,v in codex.items() for g,w in v['groups'].items()
              if w['path_count'] > 0}
    observed = {(p,g) for p,gs in peer.items() for g in gs}
    if observed != wanted:
        raise ValueError('complete port/group coverage mismatch')
    max_field = max_intensity = 0.
    for port, value in codex.items():
        powers = []
        for group, expected in value['groups'].items():
            actual = peer.get(port, {}).get(group, {'field':0j, 'paths':0})
            if actual['paths'] != expected['path_count']:
                raise ValueError('path count mismatch')
            z = actual['field']
            target = complex(*expected['field_reim'])
            numbers = [z.real, z.imag, target.real, target.imag, expected['intensity']]
            if not all(math.isfinite(x) for x in numbers):
                raise ValueError('nonfinite field/intensity')
            field_error = abs(z-target)
            intensity_error = abs(abs(z)**2-expected['intensity'])
            max_field = max(max_field, field_error)
            max_intensity = max(max_intensity, intensity_error)
            if field_error > PEER_TOL or intensity_error > PEER_TOL:
                raise ValueError('field/intensity tolerance exceeded')
            powers.append(abs(z)**2)
        if not math.isfinite(value['intensity']):
            raise ValueError('nonfinite total intensity')
        error = abs(math.fsum(powers)-value['intensity'])
        max_intensity = max(max_intensity, error)
        if error > PEER_TOL:
            raise ValueError('total intensity tolerance exceeded')
    return {'max_field_error':max_field, 'max_intensity_error':max_intensity,
            'port_groups':len(wanted)}


def audit():
    started = time.monotonic()
    verify_pins()
    response = json.loads(RESPONSE.read_text(encoding='utf-8'))
    retained = json.loads((PEER/'field_result.json').read_text(encoding='utf-8'))
    summary = {k:len(v) if isinstance(v,list) else v for k,v in retained.items()}
    if summary != response['results']:
        raise ValueError('retained aggregate differs from response')
    sys.path.insert(0, str(ROOT/'benchmarks/capacity_audit'))
    sys.path.insert(0, str(ROOT/'tests'))
    from exp005_history_mzi_audit import fixture, analytic
    from history_trace_cpu_v1 import trace_scene
    from history_fields_cpu_v1 import ideal_fields
    from history_lineage_cpu_v2 import scene_binding
    my_fields, ast_sha = peer_functions()
    cases = []
    for phase, shift in ((0.,0.),(math.pi,0.),(0.,.03125)):
        scene, _discarded_fixture_history = fixture(phase,shift)
        source2 = deepcopy(scene['sources'][0])
        source2.update(id='s2',field_reim=[.5,.25])
        scene['sources'].append(source2)
        _, packed = scene_binding(scene)
        rows = trace_scene(scene)['records']
        if len(rows) != 26:
            raise ValueError('both sources must retain complete 13-record trees')
        for coherent in (True,False):
            groups = {'s':'g', 's2':'g' if coherent else 'h'}
            own = ideal_fields(scene,rows,coherence_groups=groups)['ports']
            peer = my_fields(scene,list(packed.geometry.object_ids),groups)
            metrics = compare_complete(own,peer)
            analytical_error = 0.
            for port, unit in analytic(phase,shift).items():
                expected = {'g':unit*(1.5+.25j)} if coherent else {'g':unit,'h':unit*(.5+.25j)}
                for group,z in expected.items():
                    analytical_error = max(analytical_error,
                        abs(complex(*own[port]['groups'][group]['field_reim'])-z))
            if analytical_error > ANALYTIC_TOL:
                raise ValueError('unchanged 1e-13 analytic gate failed')
            cases.append({'snapshot':scene,'coherence_groups':groups,'record_count':len(rows),
                          'codex_ports':own,'peer_ports':{p:{g:{'paths':v['paths'],
                          'field_reim':[v['field'].real,v['field'].imag]} for g,v in gs.items()}
                          for p,gs in peer.items()}, **metrics,'analytic_error':analytical_error})
    # Negative controls apply only to this checker; not alleged wrong network outputs.
    negatives = {}
    def reject(name, own, peer):
        try:compare_complete(own,peer)
        except ValueError as e:negatives[name]=str(e)
        else:raise AssertionError('checker accepted negative '+name)
    own = cases[0]['codex_ports']
    def peer_copy():
        return {p:{g:{'field':complex(*v['field_reim']),'paths':v['paths']} for g,v in gs.items()}
                for p,gs in cases[0]['peer_ports'].items()}
    candidate = peer_copy(); candidate['Dx']['extra_group']={'field':1j,'paths':1}
    reject('extra_group_on_existing_port',own,candidate)
    candidate=peer_copy(); candidate['Dx']['g']['paths']+=1
    reject('wrong_path_count',own,candidate)
    candidate=peer_copy(); candidate['Dx']['g']['field']*=1j
    reject('same_power_wrong_phase',own,candidate)
    candidate=deepcopy(own); candidate['Dx']['groups']['g']['intensity']+=.1
    reject('group_intensity_only',candidate,peer_copy())
    candidate=deepcopy(own); candidate['Dx']['intensity']+=.1
    reject('total_intensity_only',candidate,peer_copy())
    candidate=peer_copy(); candidate['Dx']['g']['field']=complex(float('nan'),0)
    reject('nan_field',own,candidate)
    verify_pins()
    files = [Path(__file__), ROOT/'tests/exp005_history_mzi_audit.py',
             ROOT/'benchmarks/capacity_audit/history_lineage_cpu_v2.py',
             ROOT/'benchmarks/capacity_audit/history_completeness_cpu_v1.py']
    return {'timestamp_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'bounded synthetic float64 CPU replay; NOT Bpy/GPU/RT/native precision',
            'peer_results_retained_not_full_replay':summary,'replayed_cases':cases,
            'checker_negatives':negatives,'peer_tolerance':PEER_TOL,'analytic_tolerance':ANALYTIC_TOL,
            'selected_pure_ast_sha256':ast_sha,'peer_writer_executed':False,
            'verified_input_sha256':{str(p):s for p,s in PINS.items()},
            'own_code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            'no_jev_aval':True,'seconds':time.monotonic()-started}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); report=audit()
    with args.output.open('x',encoding='utf-8') as handle:
        json.dump(report,handle,indent=2,allow_nan=False);handle.write('\n')
    print(json.dumps({'cases':len(report['replayed_cases']),
        'checker_negatives':len(report['checker_negatives']),
        'field_error':max(c['max_field_error'] for c in report['replayed_cases']),
        'intensity_error':max(c['max_intensity_error'] for c in report['replayed_cases']),
        'analytic_error':max(c['analytic_error'] for c in report['replayed_cases']),
        'seconds':report['seconds'],'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
