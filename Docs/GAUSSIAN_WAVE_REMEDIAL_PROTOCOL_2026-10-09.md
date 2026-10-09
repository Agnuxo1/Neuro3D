# Mayor ventana tras un resultado ondulatorio negativo

Estado: PREPARADO, todavía no ejecutado. Este ensayo adaptativo se prepara después de publicar el resultado negativo del perfil v1 en `30a835bbf6b0f2d3dbdbf8a34b49322d5bb15326`. No es una nueva comprobación ciega ni sustituye el ensayo anterior.

El perfil v1 obtuvo una diferencia máxima de campo de 2,231187415683493 × 10⁻⁶ para λ=0,1 BU y z=4 BU en una ventana de 16 BU, frente a la tolerancia fijada de 2 × 10⁻⁶. Las tres mallas de esa ventana fallaron con la misma diferencia. Ampliar la ventana a 32 BU redujo la diferencia a 4,0866538839358044 × 10⁻⁷. Ese patrón motiva cambiar la ventana y la resolución espectral, manteniendo los algoritmos y todas las tolerancias.

## Perfil fijado antes de ejecutar

- Perfil: [gaussian_wave_remedial_profile_2026-10-09.json](research/gaussian_wave_remedial_profile_2026-10-09.json), UUID `b4c698e7-5260-4e28-bc1a-d34d117fa38d`, SHA-256 `f11f1e2bd1aebf1cfc0ca4b62202025664a80cf5da934fee571bc358b7a9d5a6`.
- Misma familia de nueve pares λ/z, referencia de Hankel independiente, campo complejo coherente y detección escalar integrada. Se conservan las 36 observaciones, incluidos los fallos.
- Mallas N/ventana BU: 1024/32, 2048/32, 4096/32 y 4096/64. La comparación 2048/32 frente a 4096/64 conserva el paso espacial.
- Tolerancias idénticas a v1: campo 2 × 10⁻⁶ y los mismos límites de norma, potencia de apertura y convergencia de cuadratura. No se aumenta una tolerancia para aceptar el fallo conocido.
- Un núcleo CPU, sin GPU, 240 s; RAM libre inicial ≥6144 MiB, suelo ≥3500 MiB, RSS propio ≤3000 MiB y evidencia ≤64 MiB. El nuevo límite de memoria corresponde a las FFT mayores y se fija antes del ensayo. Una interrupción ambiental produce métrica nula.
- Autorización humana de continuidad GitHub aplicable; registro externo/IPFS pendiente, sin identificadores emitidos.

## Alcance y reproducción

Se evalúa la discretización de un campo gaussiano escalar declarado en un semiespacio homogéneo. BU sigue sin calibración física. El modo gaussiano de esta prueba no se ha derivado de la escena neuronal. La convergencia de cuadratura es evidencia numérica, no una cota rigurosa global ni una medición física del dispositivo completo.

```powershell
python -X utf8 Tools/run_frozen_wave_reference_v2.py --profile Docs/research/gaussian_wave_remedial_profile_2026-10-09.json --registration Docs/research/gaussian_wave_remedial_registration_2026-10-09.json --out D:/PROJECTS/.cognition/neuro3d-sequential-20261008/gaussian-wave-remedial-20261009-run01
```

Publicar y verificar el commit, las preimágenes y sus hashes antes de ejecutar. Después conservar el resultado íntegro, incluso si vuelve a fallar.
