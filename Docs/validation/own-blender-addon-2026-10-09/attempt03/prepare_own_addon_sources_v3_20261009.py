import ast
from pathlib import Path

repo = Path('D:/PROJECTS/Neuro3D-Scientific-20261008')
worker = repo / 'Blender/addon/optic_neuro_blender/worker_v2.py'
assert not worker.exists()
text = (worker.with_name('worker.py')).read_text(encoding='utf-8')
text = text.replace('from optic_neuro_blender._vendor.Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood', 'from optic_neuro_blender._vendor.Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood\nfrom optic_neuro_blender._vendor.Tools.trace_indexed_scene_v1 import wire')
text = text.replace("audit_graph_neighborhood(rational_wire(scene), rational_wire({'graph': graph, **propagated}))", "audit_graph_neighborhood(wire(scene), wire({'graph': graph, **propagated}))")
text = text.replace("canonical(rational_wire({'graph': graph, **propagated}))", "canonical(wire({'graph': graph, **propagated}))")
ast.parse(text); worker.write_bytes(text.encode())
initial = worker.with_name('__init__.py')
text = initial.read_text(encoding='utf-8').replace("'version': (0, 1, 0)", "'version': (0, 1, 1)").replace("str(PACKAGE / 'worker.py')", "str(PACKAGE / 'worker_v2.py')")
ast.parse(text); initial.write_bytes(text.encode())
builder = repo / 'Tools/build_own_blender_addon_v2.py'
assert not builder.exists()
text = (builder.with_name('build_own_blender_addon_v1.py')).read_text(encoding='utf-8').replace('0.1.0', '0.1.1')
text = text.replace("for path in sorted(SOURCE.glob('*.py')):\n", "for path in sorted(SOURCE.glob('*.py')):\n        if path.name == 'worker.py':\n            continue  # Historical failed worker belongs to immutable ZIP0.1.0.\n")
ast.parse(text); builder.write_bytes(text.encode())
audit = repo / 'Tools/audit_installed_own_blender_addon_v3.py'
assert not audit.exists(); audit.write_bytes((repo / 'Tools/audit_installed_own_blender_addon_v2.py').read_bytes())
supervisor = repo / 'Tools/run_frozen_own_addon_audit_v3.py'
assert not supervisor.exists()
text = (repo / 'Tools/run_frozen_own_addon_audit_v2.py').read_text(encoding='utf-8').replace('installed_addon_profile.v2', 'installed_addon_profile.v3').replace('installed_addon_supervision.v2', 'installed_addon_supervision.v3').replace('audit_installed_own_blender_addon_v2.py', 'audit_installed_own_blender_addon_v3.py').replace('run_frozen_own_addon_audit_v2.py', 'run_frozen_own_addon_audit_v3.py').replace('build_own_blender_addon_v1.py', 'build_own_blender_addon_v2.py')
ast.parse(text); supervisor.write_bytes(text.encode())
print('New worker_v2 and package0.1.1 sources prepared; v3 audit copied without numerical changes.')
