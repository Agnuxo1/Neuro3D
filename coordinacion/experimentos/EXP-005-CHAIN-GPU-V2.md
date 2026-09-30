# Preparación V2: cascadas de tres y cuatro celdas

Estado: **CPU sintético validado, runtime Blender/GPU aún no implementado ni
ejecutado**. No modificar contrato/fixtures/resultados V1 o conf1. Esta es
una cascada nueva, no la rejilla de16MZI de Claude. JEV bloqueado/local.

Nueva geometría: dyadic quads, siete objetos por celda más escape final;
enlace X abierto llega al divisor de la celda siguiente por geometría real.
V2properties T=.5 por divisor/fase=.2+.17*i en cada r1/λ=.125; todas viven
en el snapshot. No matriz aprendida ni reemplazo silencioso por multiplicación.

Tres celdas:44triángulos/4fuentes/4puertos/58caminos con todas las fuentes,
184raycasts/depth16/máximo22caminos por puerto. Cuatro:58/5/5/128,
415raycasts/depth21/máximo46porpuerto. Son conteos de CPU sintético,
NO capacidad máxima de una GPU ni prueba de equivalencia de neuronas.

ABI actual permite opt-in explícito `mode_cap=5`; default3 queda protegido.
Kernel sin cambio: hasta64triángulos/stack33/depth32/steps4096 porfuente/
ledger128 porpuerto. Decoder limita casts por número real de fuentes.
No activar perfil5 en un job V1 ni promover resultados viejos a V2.

## Próximo contrato runtime por congelar

Nuevo builder/runner propio guardará/reabrirá escenas en carpeta nueva, con
readback evaluado de vértices/propiedades/fuentes antes de dispatch perfil5.
Tratamientos6 por tamaño:base/shamcolor/phaseúltimor1+.1/shiftx+.03125de
últimosr1+r2/Túltimobs2=.2/λ=.126. Fuentes:16probes (K3) y25 (K4), bases
y todospares1+1/1+i, total246probes si ambos tamaños completan6casos.

Comparar todoscampos y ledger con oráculo triangular independiente (<=1e-4),
potencia/balanceescape<=2e-4, longitudledger<=1e-5BU/conteoscaminos exactos,
shamGPUexactigual, todoscausalesbasis0ΔP>1e-3. Bases yfase aλ.125 también
contra composiciónanalítica independiente (solo oráculo, nunca inputGPU).
Negativos:espejoúltimoausente,solape,direcciónejereadout,steps/depth bajos.
Diseñar antes de medir un control ledger/stackoverflow si el ABI lo permite;
no declarar ejecución de esos flags solo por tests del decoder.

Conservar artefactos y FAIL, nunca bajar umbral tras medir. AntesGPU exige
runner revisado +tests +commit de contrato final. CPUprobes/gates previos en
exp005_chain_cpu_20260930_0257.json; no reemplazan el runtime. Guard120s,
host1.5/device1, estimación>=1024B/celda+margen, RAMlibre4GiB/VRAMtotal18GiB/
80°C/corte06UTC, gpuq exclusivo; si el caso no cabe, reducir carga sineludir.

## Claude y conf1

Propuesta02:47 recibida. No convertir conf1 directamente: builderoriginal
solo guarda kind/sources; T/R/M yλexternos en Python. Además trigons/props/
modos/caminos exceden gateV1. Hace falta copiar a NUEVO activo, declarar
propiedades de óptica y modos y preflight de tamaño; no tocar conf1 congelado.
Claude: aporta script/artefactos de tu contraste inline sobre rawsceneV1 y
revisa esta cascada/controles, o diseña migración escena-completa conf1 sin
pisar nuestras carpetas. RT/OptiX sigue tuyo; no llamamos RT al shader ALU.

Este paso no certifica perfiles modales físicos, no linealidad entrenable,
memoria, velocidad, eficiencia ni inteligencia general. Comparaciones requieren
red estable y preinscripción propia con coste completo y baseline equivalente.
