# Recursos y reservas

Último sondeo ligero: 2026-09-28 17:07 UTC. Las cifras son una instantánea,
no una reserva garantizada.

| Recurso | Estado | Reserva Neuro3D |
|---|---|---|
| GPU/VRAM local | Ocupada según el usuario; no se ha lanzado un sondeo ni una carga GPU en esta sesión. | Ninguna. OPT-005 pausada. |
| CPU | 25 % de carga en una muestra de 0,1 s. | Solo lecturas y cálculos pequeños. |
| RAM | 6,87 GiB disponibles en la muestra. | Evitar procesos múltiples o Blender ahora. |
| Disco D | 710,22 GiB libres en la muestra. | Documentos de coordinación y artefactos dentro del repositorio. |
| Claude Code | CLI 2.1.92 localizada; un intento OPT-001 no dio salida en 60 s y se interrumpió. Había otras sesiones Claude preexistentes; no se tocaron. | Ningún proceso nuevo reservado. Tarea en buzón. |
| JEV | Conectado con `provenance=jev` en DEC-002. | Consultas compactas para decisiones sustanciales. |

Antes de cualquier experimento pesado se repetirá el sondeo y se registrará
su reserva. No se inicia una carga GPU con la reserva actual.
