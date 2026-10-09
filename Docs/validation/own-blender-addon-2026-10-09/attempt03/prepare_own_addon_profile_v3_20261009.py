import hashlib
import json
from pathlib import Path
import shutil
import uuid

repo = Path('D:/PROJECTS/Neuro3D-Scientific-20261008')
base = Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, value): path.write_bytes((json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode())
build = base / 'own-addon-prepared-build04'; release = repo / 'Blender/releases'
archive = release / 'optic-neuro-blender-0.1.1.zip'; assert not archive.exists()
shutil.copyfile(build / archive.name, archive)
manifest = release / 'optic-neuro-blender-0.1.1-manifest.json'; shutil.copyfile(build / 'optic_neuro_blender/package_manifest.json', manifest)
shutil.copyfile(build / 'build_receipt.json', release / 'optic-neuro-blender-0.1.1-build-receipt.json')
profile = json.loads((repo / 'Docs/research/own_blender_addon_profile_v2_2026-10-09.json').read_bytes())
sources = list(profile['pins'])
remove = ['Blender/addon/optic_neuro_blender/worker.py', 'Tools/build_own_blender_addon_v1.py', 'Tools/audit_installed_own_blender_addon_v2.py', 'Tools/run_frozen_own_addon_audit_v2.py', 'Blender/releases/optic-neuro-blender-0.1.0.zip', 'Blender/releases/optic-neuro-blender-0.1.0-manifest.json']
sources = [name for name in sources if name not in remove]
sources += ['Blender/addon/optic_neuro_blender/worker_v2.py', 'Tools/build_own_blender_addon_v2.py', 'Tools/audit_installed_own_blender_addon_v3.py', 'Tools/run_frozen_own_addon_audit_v3.py', archive.relative_to(repo).as_posix(), manifest.relative_to(repo).as_posix()]
profile.update(schema='optic_neuro_blender.installed_addon_profile.v3', profile_id=str(uuid.uuid4()), worker='Tools/audit_installed_own_blender_addon_v3.py', archive_relative=archive.relative_to(repo).as_posix(), archive_sha256=sha(archive), manifest_sha256=sha(manifest), pins={name: sha(repo / name) for name in sorted(sources)}, previous_invalid_profile_sha256='b793e9de42ce10f33a6acc962f2660d7620d64da333afb0cb4923003286c4c96', repair='Existing coherent wire converter now serializes complex fields for auditor and graph JSON. Separate worker_v2 and ZIP0.1.1; old worker and ZIP0.1.0 remain. Same native audit, scientific tolerances, geometry/training core and resource caps.')
path = repo / 'Docs/research/own_blender_addon_profile_v3_2026-10-09.json'; write(path, profile)
receipt = json.loads((repo / 'Docs/research/own_blender_addon_registration_v2_2026-10-09.json').read_bytes()); receipt.update(profile_id=profile['profile_id'], profile_sha256=sha(path))
write(repo / 'Docs/research/own_blender_addon_registration_v3_2026-10-09.json', receipt)
with (repo / '.gitattributes').open('a', encoding='utf-8') as stream:
    stream.write('\nDocs/research/own_blender_addon_profile_v3_2026-10-09.json -text !eol whitespace=cr-at-eol\nDocs/research/own_blender_addon_registration_v3_2026-10-09.json -text !eol whitespace=cr-at-eol\n')
print(json.dumps({'profile_id': profile['profile_id'], 'profile_sha256': sha(path), 'pins': len(profile['pins']), 'zip_sha256': sha(archive)}))
