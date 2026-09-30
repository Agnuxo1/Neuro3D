# Nearest V2: contrato de piloto nativo GPU

30/09/2026, Codex; fallback local JEV bloqueado. Congelar por commit después
de CPU gates y ANTES de ejecutar. No cambiar umbrales tras medir.

31 dispatches: 21 sintéticosV2 (6CE3,6ambigüedad lejana con ganador único,
2triángulos coplanares/winding,1miss,6empates exactos con normales canónicas)
+6CE3shaderV1 control histórico +4reaperturas read-only K3/K4basis0/all1.
Esperar12status2+camposcero/1status1+camposcero/8válidos en sintéticosV2;
legacyCE3 exactamente1acepta entre6 debe reproducir el fallo en runtime.
K3/K4: campos/ledger/oráculo analítico1e−4, potencia/balance2e−4,
longitud1e−5BU, contadores exactos. Defaults4096steps/32depth/128ledger,
perfil5 solo para reales; no ampliar conf1 ni borrar fallos anteriores.

Los adversarios1e−9 se suben como float64hi+lo crudos: NO son geometría de
objetos Blender float32 ni certifican readback geométrico a esa resolución.
Las cuatro pruebas reales sí leen depsgraph tras abrir0315 y validar snapshot
congelado. Los doce .blend0315/hashes deben seguir intactos. GPU descubre
impactos/rutas/ramas/fases/campos desde triángulos y óptica, no datos de hitsCPU.

Normal canónica empata distancias exactas de forma conservadora; su status2
es el contrato nuevo, no depender de primer triángulo del oráculo histórico.
No RT/BVH/Maxwell/generalidad ni ventaja de velocidad; dospasadas aumentan
tests de triángulos y casts históricos NO cuentan esos tests. Bias1e−6 y
umbral modal1e−6 NOreparados: fine-gap/modalgap pendientes siguenbloqueando.

Guardar snapshots, GPUreadbacks, errores específicos, backend/dispositivo,
SHAcompuesto/base/snippet/backend/runner/dependencias y private-exit prefs.
Numericalpassed no equivale a cierre: exigir guardcompleted/rc0 yreleasegpuq.
Gpuq exclusivo porjob; host1,5/device1GiB conservadores para<=58triángulos,
floorRAM4GiB traspresupuesto/VRAMtotal18GiB/temp80; guard110s/piloto<=120s,
deadline06UTC yshutdownmargin. Nunca TDRchanges, no instalar SDK/ni eludircola.
