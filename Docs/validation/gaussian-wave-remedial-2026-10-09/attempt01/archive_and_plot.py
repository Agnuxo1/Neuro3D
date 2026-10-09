import datetime
import hashlib
import json
import shutil
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

base = Path(__file__).resolve().parent
repo = Path('D:/PROJECTS/Neuro3D-Scientific-20261008')
private = base / 'gaussian-wave-remedial-20261009-run01'
report = json.loads((private / 'supervisor.json').read_bytes())
assert report['status'] == 'VALID_FROZEN_WAVE_REFERENCE_RESULT'
dest = repo / 'Docs/validation/gaussian-wave-remedial-2026-10-09/attempt01'
shutil.copytree(private, dest)
for name, pin in report['raw_file_sha256'].items():
    assert hashlib.sha256((dest / name).read_bytes()).hexdigest() == pin, name
for name in ['published-wave-remedial-v2-20261009.json', 'prepare_wave_remedial_v2_20261009.py', 'verify_published_frozen_profile_v1.py']:
    shutil.copyfile(base / name, dest / name)
result = json.loads((dest / 'worker/result.json').read_bytes())
assert len(result['rows']) == 36
failed = [row for row in result['gates'] if any(value is False for value in row.values())]
fine = [row for row in result['rows'] if row['size'] == 4096 and row['window_BU'] == 32]
expanded = [row for row in result['rows'] if row['size'] == 4096 and row['window_BU'] == 64]
prior = json.loads((repo / 'Docs/validation/gaussian-wave-reference-2026-10-09/attempt01/worker/result.json').read_bytes())
old = [row for row in prior['rows'] if row['size'] == 2048 and row['window_BU'] == 16]
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), layout='constrained', sharey=True)
for axis, wavelength in zip(axes, [.1, .025, .00625]):
    for rows, label, marker in [(old, 'Anterior: ventana 16 / 2048²', 'o'), (fine, 'Nuevo: ventana 32 / 4096²', 's'), (expanded, 'Nuevo: ventana 64 / 4096²', '^')]:
        selected = [row for row in rows if row['wavelength_BU'] == wavelength]
        axis.semilogy([row['distance_BU'] for row in selected], [row['independent_radial_field_max_absolute_difference'] for row in selected], marker + '-', label=label)
    axis.axhline(2e-6, color='red', ls='--', label='Tolerancia prefijada 2×10⁻⁶')
    axis.set(xlabel='Distancia [BU]', xticks=[1, 2, 4], title=f'λ = {wavelength:g} BU')
    axis.grid(alpha=.2)
axes[0].set_ylabel('Diferencia máxima absoluta de campo complejo')
axes[0].legend(fontsize=8)
fig.suptitle('Ensayo adaptativo de mayor ventana: referencia de Hankel en 65 puntos; no fidelidad de la red física')
asset = repo / 'Docs/assets/gaussian-wave-remedial-2026-10-09.png'
fig.savefig(asset, dpi=170, bbox_inches='tight')
plt.close(fig)
(dest / 'archive_and_plot.py').write_bytes(Path(__file__).read_bytes())
index = {path.relative_to(dest).as_posix(): {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size} for path in dest.rglob('*') if path.is_file()}
(dest / 'evidence_index.json').write_bytes((json.dumps(index, indent=2) + '\n').encode())
stats = {'status': report['status'], 'metric': report['primary_metric'], 'worker_seconds': report['worker_seconds'], 'peak_owned_rss_mib': report['peak_owned_rss_mib'], 'files': len(index), 'result_sha256': report['result_sha256'], 'failed': failed, 'fine_max_field': max(row['independent_radial_field_max_absolute_difference'] for row in fine), 'expanded_max_field': max(row['independent_radial_field_max_absolute_difference'] for row in expanded), 'max_aperture_error': max(row['independent_disk_fraction_absolute_difference'] for row in result['rows']), 'max_quad_refinement': max(row['reference_refinement_max_absolute_difference'] for row in result['rows'])}
(base / 'wave-remedial-summary-20261009.json').write_bytes((json.dumps(stats, indent=2) + '\n').encode())
with (base / 'CHECKPOINT.md').open('a', encoding='utf-8') as stream:
    stream.write('\n## ' + datetime.datetime.now(datetime.timezone.utc).isoformat() + ' — larger-window remedial outcome retained\nPublished573b69cb/source10/profilef11f1e2 beforeexecution. Allrawhashesverified; stats=' + json.dumps(stats) + '. Originalvalidnegativev1preserved; newprofileunchangedtolerances. Needpublishboundedresultnext, thenownBlenderUI/install/cleanrepro. NoAMD/externalIPFSIDs/specialistcritique/exceptionalnovelty.\n')
print(json.dumps(stats))
