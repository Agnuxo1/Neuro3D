# Preregistro P0-4 · lineas base con igual numero de parametros (Iris y Wine)

Fecha de compromiso: 2026-10-09, antes de ejecutar cualquier experimento de esta carpeta. El commit de este archivo fija el protocolo; cualquier cambio posterior se registra como enmienda con fecha.

## 1. Pregunta

¿El clasificador optico entrenado desde geometria iguala o supera a lineas base con parametros comparables en Iris y en Wine, cuando se evalua sobre particiones repetidas?

## 2. Hipotesis

- H0: la diferencia de exactitud de prueba (optico menos linea base) tiene media cero en las particiones.
- H1: la diferencia es distinta de cero.

Regla de decision, fijada aqui:
- **Superior**: IC95 bootstrap inferior > 0 y p de Wilcoxon corregida por Holm < 0,05, frente a las dos lineas base del conjunto.
- **Equivalente**: IC95 contenido en [-0,02; +0,02].
- **Inferior o inconcluso**: cualquier otro caso.

Cualquier resultado queda registrado tal cual; un resultado "no superior" es un resultado valido.

## 3. Datos

- **Wine**: `Docs/data/uci-wine/wine.data`, 178 filas, 13 atributos. Se usan las 4 primeras caracteristicas, igual que el protocolo optico publicado. SHA-256 `6be6b1203f3d51df0b553a70e57b8a723cd405683958204f96d23d7cd6aea659`.
- **Iris**: `Blender/demo_lattice_iris/iris.csv`, 150 filas, 4 caracteristicas.

## 4. Particiones (principal)

- **Wine**: 10 particiones estratificadas 141/37, semillas `20261009 + k`, k = 0..9. Cada particion se guarda con su hash de indices.
- **Iris**: 10 particiones estratificadas 120/30, semillas `k`, k = 0..9.

Sin particion de validacion: no hay seleccion de hiperparametros. Todos los hiperparametros se fijan aqui.

## 5. Modelos

**Optico (principal)**
- Wine: protocolo de `Tools/train_wine_comparison_v1.py` y el perfil `Docs/research/wine_comparison_profile_2026-10-09.json`: 16 retardos de espejo entrenables, 60 actualizaciones Adam, tasa 0,001, temperatura de perdida 0,05, recorte de geometria +-0,035 BU, entrenamiento solo con datos de entrenamiento y escalado min-max ajustado solo con entrenamiento. Semillas de inicializacion 1049, 1050, 1051.
- Iris: funcion `train()` de `Blender/demo_lattice_iris/neuro3d_iris_demo.py` con 500 pasos y 4 reinicios, semilla de cada reinicio `seed + r`. La funcion importa `bpy`; se extrae a un modulo numerico y debe comprobarse que reproduce el original con diferencia menor de 1e-12 en la particion historica (seed 0, 120/30 no estratificada).

**Lineas base (mismo conjunto de parametros)**
- Lineal softmax: 3x5 = 15 coeficientes nominales (10 identificables). Codigo: `Blender/blender_lab/classifier_comparison_v1.py`, funcion `fit_baseline`, configuracion lineal, L2 = 0,001, maxiter 2000, gtol 1e-8, ftol 1e-12.
- Cuadratico softmax: 3x15 = 45 coeficientes nominales (30 identificables). Misma funcion y configuracion, con monomios unicos.
- Escalado min-max ajustado solo con el entrenamiento, sin recorte en prueba, para todos los modelos.

## 6. Ejecuciones

- **Wine optico**: 10 particiones x 3 semillas de inicializacion = 30 entrenamientos.
- **Iris optico**: 10 particiones x 4 reinicios internos, cada uno con su semilla fija.
- **Lineas base**: una ejecucion por particion.

**Plan de respaldo, fijado ahora:** si medir un entrenamiento de Wine con el perfil completo supera 6 minutos de CPU, se reduce a 10 particiones x 1 semilla (1049) y se declara en el informe. El cambio queda registrado con fecha.

## 7. Analisis

- Exactitud de prueba por particion y modelo. Para el optico, la media de sus semillas o reinicios dentro de cada particion.
- Diferencia pareada optico menos linea base, por particion.
- IC95 con bootstrap por particion (10 000 remuestreos, semilla 0).
- Prueba de Wilcoxon de rangos con signo, bilateral, con correccion de Holm sobre las dos lineas base de cada conjunto de datos.
- Descriptivos: media, desviacion tipica y minimo y maximo por modelo.

## 8. Integridad

- El conjunto de prueba no se usa para elegir nada.
- Se registran el hash de cada particion, la version del codigo (hash de los archivos usados) y el hash de los resultados.
- El tiempo de CPU de cada entrenamiento se registra (coste completo para P1-9).
- No se usa GPU. No se usan datos de Kaggle.

## 9. Limitaciones conocidas (antes de ejecutar)

- Wine usa solo 4 de 13 caracteristicas. Iris tiene 150 ejemplos. Las conclusiones valen para estos conjuntos y este codificado.
- La prueba de Wilcoxon con 10 particiones tiene poca potencia: una ausencia de diferencia no prueba equivalencia.
- Los entrenamientos opticos de Wine usan la geometria capturada en el perfil; no se recapturan por particion. Esto se declara.
