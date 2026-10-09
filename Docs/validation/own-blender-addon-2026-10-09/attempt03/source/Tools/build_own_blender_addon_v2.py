"""Deterministic standalone ZIP with explicit original-source provenance."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Blender/addon/optic_neuro_blender'
CORE = [
    'Blender/blender_lab/__init__.py',
    'Blender/blender_lab/scene_capture_v1.py',
    'Blender/blender_lab/scalar_scene_ingress_v1.py',
    'Blender/blender_lab/coherent_contract_v1.py',
    'Blender/blender_lab/coherent_state_graph_v1.py',
    'Blender/blender_lab/affine_geometry_network_v1.py',
    'Blender/benchmarks/capacity_audit/robust_multipath_v1.py',
    'Blender/benchmarks/capacity_audit/exact_object_index_v1.py',
    'Tools/audit_captured_pilot_result_v1.py',
    'Tools/audit_coherent_state_graph_v1.py',
    'Tools/audit_graph_neighborhood_v1.py',
    'Tools/bind_network_capture_v1.py',
    'Tools/trace_indexed_scene_v1.py',
    'Tools/train_captured_geometry_v1.py',
]
DATA = {
    'network.json': 'Docs/research/iris_scene_coordinate_bindings_v1.json',
    'semantics.json': 'Docs/validation/captured-scalar-ingress-2026-10-08/semantics.json',
    'contract.json': 'Docs/research/iris_coherent_contract_v1.json',
    'training_profile.json': 'Docs/research/captured_geometry_training_profile_2026-10-09.json',
    'training_result.json': 'Docs/validation/captured-geometry-training-2026-10-09/attempt01/worker/result.json',
    'trained_geometry.blend': 'Docs/validation/trained-geometry-blender-reproduction-2026-10-09/attempt01/worker/trained_geometry.blend',
    'iris.csv': 'Blender/demo_lattice_iris/iris.csv',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(out):
    out = Path(out).resolve(); out.mkdir(exist_ok=False)
    package = out / 'optic_neuro_blender'; package.mkdir()
    provenance = {}
    for path in sorted(SOURCE.glob('*.py')):
        if path.name == 'worker.py':
            continue  # Historical failed worker belongs to immutable ZIP0.1.0.
        ast.parse(path.read_text(encoding='utf-8'))
        target = package / path.name; shutil.copyfile(path, target)
        provenance[path.name] = {'source': path.relative_to(ROOT).as_posix(), 'source_sha256': sha(path), 'namespace_rewrite': False}
    for name in CORE:
        source = ROOT / name; target = package / '_vendor' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        # Only isolated absolute package names and newline normalization change.
        text = source.read_text(encoding='utf-8').replace('from Tools.', 'from optic_neuro_blender._vendor.Tools.').replace('from Blender.', 'from optic_neuro_blender._vendor.Blender.')
        ast.parse(text)
        target.write_bytes(text.encode('utf-8'))
        provenance['_vendor/' + name] = {'source': name, 'source_sha256': sha(source), 'namespace_rewrite': True, 'rewrites': ['from Tools. → from optic_neuro_blender._vendor.Tools.', 'from Blender. → from optic_neuro_blender._vendor.Blender.', 'text newline normalization to LF']}
    for folder in ['', 'Blender', 'Blender/benchmarks', 'Blender/benchmarks/capacity_audit', 'Tools']:
        path = package / '_vendor' / folder / '__init__.py'
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(b'"""Isolated original OpticNeuroBlender dependency namespace."""\n')
    for name, source_name in DATA.items():
        target = package / 'data' / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source_name, target)
        provenance['data/' + name] = {'source': source_name, 'source_sha256': sha(ROOT / source_name), 'namespace_rewrite': False}
    shutil.copyfile(ROOT / 'LICENSE', package / 'LICENSE')
    (package / 'INSTALL.txt').write_bytes(('OpticNeuroBlender 0.1.1\nBlender 4.5, Windows/Linux, NumPy bundled with Blender.\nInstall this ZIP through Preferences > Add-ons > Install from Disk.\nOpen the OpticNeuro sidebar; open the own trained example only after preserving your current scene.\nChoose an existing evidence directory, set common-coherence amplitudes and phases, then infer.\nTraining uses the declared Iris 120/30 split and 60 audited geometry updates inside a background Blender.\nCancel stops only the owned process. Apply/recover checks the unchanged scene, inputs, package and evidence receipt.\nSave requires a NEW .blend path; evidence directories are never deleted automatically.\nUnit: BU, wavelength 0.1 BU, normalized scalar modal power; no calibrated watts or physical-network validation.\nUI runs are exploratory; scientific claims require separately frozen protocols.\nNo external BlenderPhotonics or BOS implementation is bundled. Original source MIT; see LICENSE.\n').encode())
    manifest = {'schema': 'optic_neuro_blender.package.v1', 'version': '0.1.1', 'runtime': 'Blender4.5 with bundled NumPy, stdlib, Windows or Linux resource supervision', 'files': {path.relative_to(package).as_posix(): {'sha256': sha(path), 'bytes': path.stat().st_size} for path in sorted(package.rglob('*')) if path.is_file()}, 'source_provenance': provenance, 'third_party_optical_code_bundled': False}
    (package / 'package_manifest.json').write_bytes((json.dumps(manifest, indent=2, ensure_ascii=False) + '\n').encode())
    archive = out / 'optic-neuro-blender-0.1.1.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
        for path in sorted(package.rglob('*')):
            if path.is_file():
                info = zipfile.ZipInfo('optic_neuro_blender/' + path.relative_to(package).as_posix(), (2026, 10, 9, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o100644 << 16
                stream.writestr(info, path.read_bytes())
    receipt = {'archive_sha256': sha(archive), 'archive_bytes': archive.stat().st_size, 'files': len(manifest['files']) + 1, 'manifest_sha256': sha(package / 'package_manifest.json')}
    (out / 'build_receipt.json').write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); print(json.dumps(build(args.out)))
