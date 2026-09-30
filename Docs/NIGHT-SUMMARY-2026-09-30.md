# Neuro3D: cierre del turno nocturno

Turno autorizado hasta30/09/2026 08:00 Europe/Madrid (06:00UTC).
Resumen de evidencia retenida, no una nueva ejecución ni un máximo de capacidad.

## Qué quedó demostrado

- El piloto nativo dentro de Blender deriva impactos, rutas, ramificación,
  longitudes, fases, campos e intensidades en shadersGPU desde escena cruda.
  El backend usa ALU/OpenGL: NO núcleosRT ni simulación óptica física.
  Exportación/preflight/empaquetado/transferencia/readback/oráculos quedan enCPU.
- K3/K4 y recorrido compartido superaron gates locales retenidos. Reducir
  búsquedas geométricas no produjo una mejora clara de latencia en el coste
  pareado previo; no confundir menos trabajo con speedup medido.
- ResidenciaV3:270 comprobaciones y4invalidaciones, guardrc0. Conservados
  V1timeout yV2importFAIL. Ratiosfresh/resident1,018–1,098 son descriptivos,
  no certificación de eficiencia energética ni ventaja frente a otras redes.
- NearestV2:31dispatches preinscritos,21adversarios/controles crudos sintéticos,
  seisV1históricos ycuatro probes reales de escenas reabiertas. Rechaza6/6
  órdenesCE3 donde V1acepta incorrectamente1/6. Auditoría retenida de12válidos:
  campo2,855e-7,balance1,252e-6. 174testsCPU en la última suite, sin repetirla
  durante el cierre. Contratoabbe543 antesGPU; auditor/informed80c3ac.
- ParcheClaude de longitud de onda por escena y colisiónhash contrastado SOLO
  CPU:lotemixto7,20e-15. La fusión de estados cuantizados no está certificada
  como equivalencia óptica exacta. Las cifras de su benchmark comparan contra
  su CPU, no contra una red convencional; su inferenciaU/GEMM es otro backend.

## Evidencia principal

- `Docs/EXP-005-NEAREST-GPU-V2-2026-09-30.md` y contrato correspondiente.
- Reporte `D:/PROJECTS/.cognition/neuro3d/exp005_nearest_native_20260930_0546.json`,
  SHA `b855a6ff5626149bc4744b377864f351debb0d585c7db904d1a2774c20d7accb`.
- Reauditoría `D:/PROJECTS/.cognition/neuro3d/exp005_nearest_audit_20260930_0550.json`.
- Guard0546:completed/rc0,7,521s,RAMmín9,916GiB/VRAMmáx0,815GiB/36°C;
  turno liberado05:47:34UTC. PID29224 terminado ysinBlender alpre-cierre05:57.
- RESV3 report0514 y audit0517; peerstate audit0534. Fixtures0119/0315 y
  fallos anteriores permanecen preservados. Tableros locales SINstage.

## Próximo trabajo, tras nueva autorización

1. Corregir/preinscribir bias que salta gaps1e-8 y discrepancia de tolerancia
   terminalGPU1e-6/oráculo1e-9. Crítica independiente retenida de Claude.
2. Probar fusión de dos ramas con presupuesto de error de fase dependiente de
   lambda, referencia, modo ycoherencia. No usar hash/clave cuantizada como prueba
   suficiente de igualdad física del estado.
3. Coordinar backendRT/BVH con Claude, conservando longitudes/fases/gates y
   costes de construir/actualizar estructura; no instalar SDK sin permiso.
4. Comparar batching/wavefront/residencia con protocolo pareado y costes
   completos. No usar DLSS/FSR como inferencias exactas ni sustituir escena porU
   silenciosamente. Elegir motor por resultados, no por FPS del visor.
5. Capacidad y comparación contra redes convencionales requieren operación,
   precisión, funcionalidad ypresupuestos equiparables. No se ha establecido
   un máximo de neuronas equivalente ni ventaja general con estas pruebas.

El informeMIanidado de Claude fue leído, no reauditado aquí: no enviar aKaggle
ni inferir ventaja del kernel a partir de sus métricas. JEV sigue bloqueado por
seguridad: fallbacklocal explícito, sin atribuir aval remoto. No publicación ni
merge de trabajo ajeno. Cerrar solo procesos propios ypausar el reloj al06UTC.
