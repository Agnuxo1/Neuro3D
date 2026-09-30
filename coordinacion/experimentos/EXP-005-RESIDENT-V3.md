# RES-001 V3: entrada Blender con importación explícita

30/09/2026 05:12UTC. Fallback local; JEV bloqueado.

V2job0510 adquirió05:10:34UTC, liberó05:10:41rc2. Error antes del cálculo:
ModuleNotFoundError exp005_resident_runtime, al importar el wrapper V2.
El proceso Blender terminó limpiamente: NO270readbacks ni lifecycle nuevo;
guard0510 retiene child_failed. Esto NOvalida reparación del cierre V1.

V3 añade sys.path del propio script ANTES de importar V2. Mantiene intactos
V2 y runner numérico V1/shader/gates, inputs0315, contrastes y cuatro cambios
evaluados. Envelope nuevo entrypointSHA/lifecycleSHA/reportSHA. La preferencia
privada no persistente sigue V2. No bypass de salida ni ampliación de límites.

CPU regression importa vía runpy en Python aislado (-I), sin ruta hermana
inicial ni importación bpy/gpu. Antes de GPU: test y commit propios. Un job
gpuq exclusivo; guard110s (más estricto que piloto120), host1,5/device1GiB,
RAM4GiB traspresupuesto/VRAMtotal18GiB/temp80/deadline06UTC. Artefactos0510
y0426 permanecen intactos. Nuevos artifactsV3. Exigir guardrc0,270auditoría,
4invalidaciones/hashes/envelopes antes de afirmar cierre operacional PASS.
