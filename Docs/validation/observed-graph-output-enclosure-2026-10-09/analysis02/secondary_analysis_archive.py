from pathlib import Path
from fractions import Fraction as F
import hashlib,json,subprocess,sys
import mpmath as mp
root=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');sys.path.insert(0,str(root))
from Tools.audit_captured_pilot_result_v1 import decode
dest=root/'Docs/validation/observed-graph-output-enclosure-2026-10-09/analysis02'
dest.mkdir(parents=True,exist_ok=False)
cpath=Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/captured-graph-output-certificate-20261009-run02.json')
c=json.loads(cpath.read_text());(dest/'certificate.json').write_bytes(cpath.read_bytes())
r=decode(json.loads((root/'Docs/validation/coherent-state-graph-capture-2026-10-09/attempt01/result.json').read_text()))
scene=decode(json.loads((root/'Docs/validation/captured-scalar-ingress-2026-10-08/scene.json').read_text()))
def scalar(v):
    v=F(v);return mp.mpf(v.numerator)/v.denominator
with mp.workdps(90):
    g=r['graph'];incoming=[mp.mpc(0) for _ in g['nodes']];outputs={p:mp.mpc(0) for p in g['ports']}
    fields={s['id']:s['field_reim'] for s in scene['sources']}
    for rt in g['roots']:
        a=fields[rt['source_id']];incoming[rt['node']]+=mp.mpc(scalar(a[0]),scalar(a[1]))
    for i in g['topological_order']:
        n=g['nodes'][i];norm=mp.sqrt(sum(scalar(v)**2 for v in n['direction']))
        value=incoming[i]*mp.exp(2j*mp.pi*scalar(n['segment_parameter'])*norm/scalar(g['wavelength']))
        if 'terminal' in n:
            outputs[n['terminal']]+=value*mp.exp(2j*mp.pi*scalar(n['reference_parameter'])*norm/scalar(g['wavelength']))
        for edge in n['edges']:
            incoming[edge['target']]+=value*mp.sqrt(scalar(edge['power']))*(mp.j**edge['quarter_turns'])*mp.exp(mp.j*scalar(edge['phase_rad']))
    cross={}
    for p,v in outputs.items():
        checks=[]
        for name,expected in [('field_real',v.real),('field_imag',v.imag),('power',abs(v)**2)]:
            interval=c['ports'][p][name]
            checks.append(scalar(F(*interval['lo']))<=expected<=scalar(F(*interval['hi'])))
        cross[p]={'all_three_enclosures_contain_independent_90_digit_reference':all(checks),
                  'reference_real':mp.nstr(v.real,85),'reference_imag':mp.nstr(v.imag,85)}
    assert all(v['all_three_enclosures_contain_independent_90_digit_reference'] for v in cross.values())
cross['scope']='Numerical independent high-precision cross-check, not a substitute for outward rational proof; no producer/enclosure kernel imports'
(dest/'independent_mpmath_crosscheck.json').write_bytes((json.dumps(cross,indent=2)+'\n').encode())
test=subprocess.run([sys.executable,'-X','utf8','-m','unittest','Blender.tests.test_state_graph_enclosure_v1','-v'],cwd=root,capture_output=True)
(dest/'controls.log').write_bytes(test.stdout+test.stderr);assert test.returncode==0
sources=['Blender/blender_lab/state_graph_enclosure_v1.py','Blender/benchmarks/capacity_audit/rational_interval_v1.py','Tools/certify_captured_graph_outputs_v1.py','Tools/audit_coherent_state_graph_v1.py','Blender/tests/test_state_graph_enclosure_v1.py']
for name in sources:
    p=dest/'sources'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((root/name).read_bytes())
(dest/'secondary_analysis_archive.py').write_bytes(Path(__file__).read_bytes())
for name,pin in c['source_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==pin
index={p.relative_to(dest).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in dest.rglob('*') if p.is_file()}
(dest/'evidence_index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
accept=root/'Docs/research/optic_neuro_blender_acceptance_v1.json';a=json.loads(accept.read_text())
for entry in a['priorities']:
    if entry['id']==3:
        entry['status']='CAPTURED_GRAPH_COMPLETE_OBSERVED_FIELDS_AND_DECISION_CERTIFIED'
        entry['remaining']='Independent interior-neighborhood check and scientific training validation; original pilot deadline remains unchanged'
    if entry['id']==4:
        entry['status']='PARTIAL_OBSERVED_REPRESENTED_ERROR_CERTIFIED'
        entry['achieved']='Independent interval enclosure: observed native field L1<=4.9383434427813286e-15,power<=3.1372973883238074e-15; represented det.R1 argmax margin>=0.18933601504039158; seven adverse/enclosure controls plus full graph90-digit cross-check'
        entry['remaining']='Unknown intended-geometry/native Blender transform error and physical model error; independent fan interior-neighborhood audit; broader inputs/families/GPU'
a['latest_output_certificate']='Docs/validation/observed-graph-output-enclosure-2026-10-09/analysis02/certificate.json'
accept.write_bytes((json.dumps(a,indent=2)+'\n').encode())
print(json.dumps({'files':len(index),'independent_crosscheck_ports':len(outputs),'controls_exit':test.returncode}))
