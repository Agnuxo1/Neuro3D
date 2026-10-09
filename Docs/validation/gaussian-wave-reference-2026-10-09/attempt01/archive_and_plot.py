import datetime,hashlib,json,shutil
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
repo=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');base=Path(__file__).resolve().parent
private=base/'gaussian-wave-reference-20261009-run01';report=json.loads((private/'supervisor.json').read_bytes())
assert report['status']=='VALID_FROZEN_WAVE_REFERENCE_RESULT' and report['primary_metric']==0
dest=repo/'Docs/validation/gaussian-wave-reference-2026-10-09/attempt01';shutil.copytree(private,dest)
for name,pin in report['raw_file_sha256'].items():assert hashlib.sha256((dest/name).read_bytes()).hexdigest()==pin,name
for name in ['gaussian-wave-published-preexecution-verification-20261009.json','verify_published_frozen_profile_v1.py','wave-controls-development-receipt-20261009.json','prepare_wave_protocol_20261009.py','update_prepared_wave_guards_20261009.py','finalize_prepared_wave_window_20261009.py']:
    shutil.copyfile(base/name,dest/name)
for name in ['wave-prepared-prepublication01','wave-prepared-prepublication02']:shutil.copytree(base/name,dest/name)
shutil.copyfile(base/'wave-primary-sources-20261009/receipt.json',dest/'private_primary_source_retrieval_receipt.json')
result=json.loads((dest/'worker/result.json').read_bytes());assert len(result['rows'])==36
fine=[r for r in result['rows'] if r['size']==2048 and r['window_BU']==16]
expanded=[r for r in result['rows'] if r['size']==2048 and r['window_BU']==32]
plt.rcParams.update({'font.size':10});fig,(a,b,c)=plt.subplots(1,3,figsize=(14,4.3),layout='constrained')
for wavelength in [.1,.025,.00625]:
    rows=[r for r in fine if r['wavelength_BU']==wavelength]
    a.plot([r['distance_BU'] for r in rows],[r['hankel_reference']['disk_power_fraction'] for r in rows],'o-',label=f'λ={wavelength:g} BU')
    a.plot([r['distance_BU'] for r in rows],[r['paraxial_disk_fraction'] for r in rows],'--',alpha=.65)
a.set(xlabel='Distancia [BU]',ylabel='Fracción transversal dentro de radio 0,15 BU',title='Referencia continua / paraxial (trazos)');a.legend(fontsize=8);a.grid(alpha=.2)
positions=np.arange(9)
b.semilogy(positions,[r['independent_radial_field_max_absolute_difference'] for r in fine],'o-',label='2048² / ventana 16')
b.semilogy(positions,[r['independent_radial_field_max_absolute_difference'] for r in expanded],'s-',label='2048² / ventana 32')
b.axhline(2e-6,color='red',ls='--',label='Tolerancia prefijada')
b.set(xticks=positions,xticklabels=[f"{r['wavelength_BU']:g}\n{r['distance_BU']:g}" for r in fine],xlabel='λ [BU] / distancia [BU]',ylabel='Diferencia absoluta de campo complejo',title='65 puntos frente a Hankel independiente');b.legend(fontsize=8);b.grid(alpha=.2)
for row in [r for r in result['rows'] if r['wavelength_BU']==.1 and r['distance_BU']==4]:
    native=np.asarray(row['radial_field_real'])+1j*np.asarray(row['radial_field_imag']);ref=np.asarray(row['independent_radial_field_real'])+1j*np.asarray(row['independent_radial_field_imag'])
    c.plot(row['radial_radii_BU'],np.abs(native-ref),label=f"{row['size']}² / {row['window_BU']} BU")
c.axhline(2e-6,color='red',ls='--');c.set(xlabel='Radio [BU]',ylabel='Diferencia absoluta de campo',title='Caso adverso λ=0,1 BU, z=4 BU');c.legend(fontsize=8);c.grid(alpha=.2)
fig.suptitle('Familia gaussiana escalar declarada: fallo conservado de ventana, no certificación de la red física')
asset=repo/'Docs/assets/gaussian-wave-reference-2026-10-09.png';fig.savefig(asset,dpi=170,bbox_inches='tight');plt.close(fig)
(dest/'archive_and_plot.py').write_bytes(Path(__file__).read_bytes())
index={p.relative_to(dest).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in dest.rglob('*') if p.is_file()}
(dest/'evidence_index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
accept=repo/'Docs/research/optic_neuro_blender_acceptance_v1.json';policy=json.loads(accept.read_bytes())
for entry in policy['priorities']:
    if entry['id']==6:entry.update(status='PARTIAL_CAPACITY_STABILITY_AND_DECLARED_WAVE_REGIME_CHARACTERIZED',achieved='Realquadraticcapacity and3seedWinevariability; independentGaussianFFTvsHankel/paraxialstudy36casescompleted withvalidnegative metric0: window16fails2e-6radialbudgetatλ.1/z4; window32reduceserror. Fullnetworkphysicalfidelityremainsunknown',remaining='Resolve/freeze largerwindowfamily withoutrelaxingbudgets; parameter/inputrobustness andfullnetworkwave model/physicalmeasurements')
    if entry['id']==1:entry.update(achieved='Operationaljointgeometry/field/decisioncertificates implemented forcapturedDAG, actualowntrainingandobservedCUDA; directedprimaryreviewincludingHo2025/QAIBP2023/DEEPG2019 reinforcesNOVELTY_NOT_ESTABLISHED',remaining='Verifiableclosestmethodcomparison and106pendingliteratureextractions; exceptionaloriginality/impactnotproved')
policy['latest_wave_reference']='Docs/validation/gaussian-wave-reference-2026-10-09/attempt01/worker/result.json'
accept.write_bytes((json.dumps(policy,indent=2)+'\n').encode())
with (base/'CHECKPOINT.md').open('a',encoding='utf-8') as s:s.write('\n## '+datetime.datetime.now(datetime.timezone.utc).isoformat()+' — independent wave reference valid negative outcome\nFrozenfaa9b788/profile3cb6c42a/SHA6c138f2a/source10verified beforeexecution. Actual36cases32.9150s,RSS510.734MiB VALID_FROZEN_WAVE_REFERENCE_RESULT metric0; no interruption. Allnormgatespass; λ.1/z4 window16radialfielddifference2.231187415683493e-6>fixed2e-6, same-dxwindowcomparisonalsofails; expandedwindow32error4.0866538839358044e-7. 8othercasesallgatespass; norm/aperture gatesall36pass. Refining512/1024/2048 atwindow16failsidentically: window/frequencyresolutionproblem, notfixablebygridonly. Hankel512/1024refinement3.475e-15forthatcase. Allsource/rawhashesverified andplotprepared, needpublishbeforelargerwindowremedialprofile. No fullnetworkphysicalerrorzero or universalFFTcertification. Nextfixedlargerwindows32/64samethresholds, explicitRAMlimitif4096. ThenownBlenderUI/cleanreproduction/article; external/AMDstillopen.\n')
print(json.dumps({'files':len(index),'status':report['status'],'metric':report['primary_metric'],'seconds':report['worker_seconds'],'rss_mib':report['peak_owned_rss_mib'],'failed':[r for r in result['gates'] if any(v is False for v in r.values())]}))
