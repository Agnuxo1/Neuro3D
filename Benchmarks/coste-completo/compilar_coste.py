#!/usr/bin/env python3
"""P1-9: compila la tabla de coste de las comparaciones de Neuro3D.

Solo LEE resultados ya existentes (no re-ejecuta entrenamientos ni simulaciones).
Escribe, en esta carpeta: TABLA-COSTE.json, TABLA-COSTE.md, INFORME-P1-9.md y SHA256SUMS.txt.
Regla: lo que no esta registrado se escribe "no registrado"; nada se estima.
E_UB = t_CPU x 14 W (cota superior; la energia NO se mide). Ver PREREGISTRO-P1-9.md.
Uso: python compilar_coste.py
"""
import glob
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HERE)  # .../Benchmarks
P_NUCLEO_W = 14.0  # 140 W / 10 nucleos fisicos (preregistro, seccion 2)
NR = "no registrado"
NA = "no aplica (simulación sin parámetros entrenables)"
TICK = 1.0 / 64.0  # resolucion observada del reloj de CPU en Windows (0.015625 s)

EEG = "eeg-motor-imagery/evidencia-validacion-anidada"
LB = "lineas-base/resultados"
VO = "validacion-onda/resultados"


def jl(rel):
    with open(os.path.join(B, rel), encoding="utf-8") as f:
        return json.load(f)


def txt(rel):
    with open(os.path.join(B, rel), encoding="utf-8") as f:
        return f.read()


def r6(x):
    return round(float(x), 6)


ROWS = []


def add(comp, metodo, conjunto, unidad, n, t_total_cpu=None, mem=NR, nom=NR, ident=NR,
        act=NR, fuente="", nota="", reloj="CPU de proceso", t_pared=None, t_unit_override=None):
    """t_total_cpu: segundos de CPU del conjunto de unidades (None = no registrado)."""
    row = {
        "id": len(ROWS) + 1,
        "comparacion": comp,
        "metodo": metodo,
        "conjunto": conjunto,
        "unidad": unidad,
        "n_unidades": n,
        "reloj_registrado": reloj,
    }
    if t_total_cpu is None:
        row["t_cpu_por_unidad_s"] = NR
        row["t_cpu_total_s"] = NR
        row["E_UB_J"] = NR
        row["E_UB_Wh"] = NR
    else:
        row["t_cpu_por_unidad_s"] = r6(t_total_cpu / n if t_unit_override is None else t_unit_override)
        row["t_cpu_total_s"] = r6(t_total_cpu)
        row["E_UB_J"] = r6(t_total_cpu * P_NUCLEO_W)
        row["E_UB_Wh"] = r6(t_total_cpu * P_NUCLEO_W / 3600.0)
    row["t_pared_total_s"] = NR if t_pared is None else r6(t_pared)
    row["memoria_pico"] = mem
    row["parametros_nominales"] = nom
    row["parametros_identificables"] = ident
    row["actualizaciones_o_pasos"] = act
    row["fuente"] = fuente
    row["nota"] = nota
    ROWS.append(row)
    return row


# ---------------------------------------------------------------- P0-4 optico
oi = jl(f"{LB}/optical_iris.json")
parts = oi["partitions"]
assert len(parts) == 10
npar = {len(p["params"]) for p in parts}
assert len(npar) == 1
sens = jl(f"{LB}/SENSIBILIDAD_IRIS.json")
r_oi = add(
    "P0-4", "Óptico (geometría entrenable)", "Iris, 10 particiones 120/30", "partición (4 reinicios)", 10,
    t_total_cpu=sum(p["cpu_seconds"] for p in parts),
    nom=f"{npar.pop()} (longitud de params por partición)",
    act=f"{oi['steps']} pasos x {oi['restarts']} reinicios por partición",
    fuente=f"{LB}/optical_iris.json :: partitions[].cpu_seconds, partitions[].params, steps, restarts",
    nota=(f"SENSIBILIDAD_IRIS.json registra restart_cpu_seconds_total={sens['restart_cpu_seconds_total']:.6g} s "
          "(mismos reinicios, contabilidad aparte; no se suma)."),
)
IRIS_OPT_TOTAL = r_oi["t_cpu_total_s"]

prof = [jl(f"{LB}/perfiles/wine_profile_k{k}.json") for k in range(10)]
steps_wine = {p["steps"] for p in prof}
assert len(steps_wine) == 1
n_delays = {len(p["initializations"][0]["deltas_BU"]) for p in prof}
assert n_delays == {16}
steps_wine = steps_wine.pop()

prim = []
proc_prim = 0.0
for k in range(10):
    d = jl(f"{LB}/optical_wine_k{k}.json")
    proc_prim += d["process_cpu_seconds"]
    runs = [r for r in d["runs"] if r["seed"] == 1049]
    assert len(runs) == 1
    prim.append(runs[0]["cpu_seconds_seed_training_plus_rebuild"])
r_wp = add(
    "P0-4", "Óptico (geometría entrenable), semilla 1049 (primario)", "Wine, 10 particiones 141/37",
    "entrenamiento", 10, t_total_cpu=sum(prim),
    nom="16 retardos de espejo entrenables (initializations[].deltas_BU; PREREGISTRO-P0-4.md)",
    act=f"{steps_wine} actualizaciones Adam por entrenamiento (perfiles/wine_profile_k*.json :: steps)",
    fuente=f"{LB}/optical_wine_k*.json :: runs[seed=1049].cpu_seconds_seed_training_plus_rebuild",
    nota=(f"Suma de process_cpu_seconds de los 10 procesos primarios (k=0 ejecutó 3 semillas): {proc_prim:.6g} s. "
          "cpu_seconds_geometry_audits se registra aparte (p. ej. k=0: 339.7 s); el archivo no declara su relación "
          "con el campo usado."),
)

ext = []
for f in sorted(glob.glob(os.path.join(B, LB, "extension", "optical_wine_ext_*.json"))):
    with open(f, encoding="utf-8") as fh:
        d = json.load(fh)
    ext.append(d["run"]["cpu_seconds_seed_training_plus_rebuild"])
assert len(ext) == 20
r_we = add(
    "P0-4 (extensión exploratoria post hoc)", "Óptico, semillas 1050 y 1051", "Wine, 10 particiones 141/37",
    "entrenamiento", 20, t_total_cpu=sum(ext),
    nom="16 retardos de espejo entrenables", act=f"{steps_wine} actualizaciones Adam por entrenamiento",
    fuente=f"{LB}/extension/optical_wine_ext_k*_s*.json :: run.cpu_seconds_seed_training_plus_rebuild",
    nota="Las 2 semillas de k=0 se reutilizaron del proceso primario (reused_from_primary_process=true).",
)
r_w30 = add(
    "P0-4 + extensión", "Óptico, 3 semillas (suma de las dos filas anteriores)", "Wine, 10 particiones 141/37",
    "entrenamiento", 30, t_total_cpu=r_wp["t_cpu_total_s"] + r_we["t_cpu_total_s"],
    nom="16 retardos de espejo entrenables", act=f"{steps_wine} actualizaciones Adam por entrenamiento",
    fuente="suma de las filas %d y %d de esta tabla" % (r_wp["id"], r_we["id"]),
    nota="Fila derivada (suma); protocolo del benchmark P1-5 (media de 3 semillas).",
)

# ---------------------------------------------------------------- P0-4 baselines
bl = jl(f"{LB}/baselines.json")
for ds, nom_name, label in (("iris", "Iris, 10 particiones 120/30", "iris"), ("wine", "Wine, 10 particiones 141/37", "wine")):
    ps = bl[ds]
    assert len(ps) == 10
    nl = {p["linear"]["nominal_parameters"] for p in ps}
    nq = {p["quadratic"]["nominal_parameters"] for p in ps}
    assert nl == {15} and nq == {45}
    il = sum(p["linear"]["iterations"] for p in ps) / 10
    iq = sum(p["quadratic"]["iterations"] for p in ps) / 10
    cpus = [p["cpu_seconds"] for p in ps]
    add(
        "P0-4", "Líneas base softmax lineal + cuadrático (ajuste conjunto)", nom_name, "partición (2 ajustes)", 10,
        t_total_cpu=sum(cpus), nom="15 (lineal) + 45 (cuadrático)", ident="10 (lineal) + 30 (cuadrático) (PREREGISTRO-P0-4.md)",
        act=f"iteraciones del optimizador, media de 10 particiones: lineal {il:.6g}, cuadrático {iq:.6g} (maxiter 2000)",
        fuente=f"{LB}/baselines.json :: {label}[].cpu_seconds, {label}[].linear/quadratic.iterations, nominal_parameters",
        nota=("cpu_seconds cubre los dos ajustes de la partición; no hay tiempo separado en este archivo "
              "(el separado está en P1-5, B5 y B6)."
              + (f" k=0 registra {cpus[0]:.6g} s; el resto, entre {min(cpus[1:]):.6g} y {max(cpus[1:]):.6g} s." if ds == "wine" else "")),
    )

# ---------------------------------------------------------------- P1-5
raw = jl("benchmark-v1/resultados/benchmark_v1_raw.json")
MNAME = {
    "B1": "B1 softmax lineal L2=0.001",
    "B2": "B2 SVM RBF C=1 gamma=scale",
    "B3": "B3 random forest 200 árboles",
    "B4": "B4 MLP (32,) max_iter=500",
    "B5": "B5 softmax lineal P0-4",
    "B6": "B6 softmax cuadrático P0-4",
}
DSNAME = {
    "iris": "Iris, 10 particiones 120/30",
    "wine": "Wine, 10 particiones 141/37",
    "breast_cancer": "Breast Cancer, 10 particiones 455/114",
    "digits": "Digits, 10 particiones 1437/360",
}
P15 = {}  # (ds, modelo) -> fila
for ds in ("iris", "wine", "breast_cancer", "digits"):
    for m, recs in raw["datasets"][ds]["models"].items():
        assert len(recs) == 10
        tot = sum(r["cpu_seconds"] for r in recs)
        nom, ident, act = NR, NR, NR
        if m in ("B1", "B5", "B6"):
            nn = {r["nominal_parameters"] for r in recs}
            assert len(nn) == 1
            nom = str(nn.pop())
            its = [r["iterations"] for r in recs]
            act = f"iteraciones del optimizador, media {sum(its)/10:.6g} (min {min(its)}, máx {max(its)})"
            if ds in ("iris", "wine") and m in ("B1", "B5"):
                ident = "10 (PREREGISTRO-P0-4.md)"
            if ds in ("iris", "wine") and m == "B6":
                ident = "30 (PREREGISTRO-P0-4.md)"
        if m == "B4":
            ni = [r["n_iter"] for r in recs]
            act = f"n_iter medio {sum(ni)/10:.6g} (min {min(ni)}, máx {max(ni)}) de max_iter=500"
        P15[(ds, m)] = add(
            "P1-5", MNAME[m], DSNAME[ds], "partición (ajuste + predicción)", 10, t_total_cpu=tot,
            nom=nom, ident=ident, act=act,
            fuente=("benchmark-v1/resultados/benchmark_v1_raw.json :: datasets.%s.models.%s[].cpu_seconds" % (ds, m)
                    + (", nominal_parameters, iterations" if m in ("B1", "B5", "B6") else "")
                    + (", n_iter" if m == "B4" else "")),
            nota=f"Resolución del reloj de CPU ~{TICK:.6g} s (valores cuantizados); threads OMP/OPENBLAS/MKL=1.",
        )

# ---------------------------------------------------------------- P1-7
val = jl(f"{VO}/RESULTADOS_VALIDACION.json")
for ppl, nsim, key in ((16, 12, "16"), (24, 18, "24")):
    files = sorted(glob.glob(os.path.join(B, VO, f"mzi_fdtd_{ppl}_k*.json")))
    assert len(files) == nsim
    ds = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            ds.append(json.load(fh))
    tot = sum(d["t_cpu_s"] for d in ds)
    assert abs(tot - val["mallas"][key]["t_cpu_total_s"]) < 1e-6
    pas, cel, npp = ({d["pasos"] for d in ds}, {d["celdas"] for d in ds}, {d["n_p"] for d in ds})
    assert len(pas) == len(cel) == len(npp) == 1
    add(
        "P1-7", f"FDTD 2D MZI λ/{ppl}", f"MZI, {nsim} simulaciones (k=0..{nsim-1}), {cel.pop()} celdas", "simulación", nsim,
        t_total_cpu=tot, mem=f"{max(d['pico_memoria_gb'] for d in ds):.6g} GB (máximo de las simulaciones)",
        nom=NA, ident=NA, act=f"{pas.pop()} pasos de tiempo por simulación (n_p={npp.pop()})",
        fuente=f"{VO}/mzi_fdtd_{ppl}_k*.json :: t_cpu_s, pico_memoria_gb, pasos, celdas (coincide con RESULTADOS_VALIDACION.json :: mallas.{key}.t_cpu_total_s)",
        nota=f"Tiempo de pared total registrado: {sum(d['t_wall_s'] for d in ds):.6g} s. Carpeta _descartados excluida.",
        t_pared=sum(d["t_wall_s"] for d in ds),
    )

med = jl(f"{VO}/medicion_coste.json")
for m in med["medidas"]:
    add(
        "P1-7", "Solver directo (factorización LU, SuperLU 1 hilo)", f"{m['forma']}, N={m['N']} incógnitas", "factorización", 1,
        t_total_cpu=m["t_cpu_s"], mem=f"{m['pico_memoria_gb']:.6g} GB", nom=NA, ident=NA,
        act=f"no aplica (nnz_lu={m['nnz_lu']})",
        fuente=f"{VO}/medicion_coste.json :: medidas[N={m['N']}].t_cpu_s, pico_memoria_gb, nnz_lu",
        nota=f"Tiempo de pared registrado: {m['t_wall_s']:.6g} s. La sección 'proyeccion' del archivo es una proyección, no una medida: excluida de la tabla.",
        t_pared=m["t_wall_s"],
    )

pv = jl(f"{VO}/pml_vacio.json")["casos"]
add("P1-7", "Solver directo, prueba PML en vacío", f"{pv[0]['nx']}x{pv[0]['ny']} ({pv[0]['incognitas']} incógnitas), ángulos 0 y 10", "caso", len(pv),
    t_total_cpu=sum(c["t_cpu_total_s"] for c in pv), mem=f"{max(c['pico_memoria_gb'] for c in pv):.6g} GB (máximo)",
    nom=NA, ident=NA, act="no aplica",
    fuente=f"{VO}/pml_vacio.json :: casos[].t_cpu_total_s, pico_memoria_gb")
for ppl in (16, 24):
    pf = jl(f"{VO}/pml_vacio_fdtd_{ppl}.json")["casos"]
    add("P1-7", f"FDTD 2D λ/{ppl}, prueba PML en vacío", f"casos a ángulos {', '.join(str(c['angulo']) for c in pf)}", "caso", len(pf),
        t_total_cpu=sum(c["t_cpu_s"] for c in pf), mem=f"{max(c['pico_memoria_gb'] for c in pf):.6g} GB (máximo)",
        nom=NA, ident=NA, act="; ".join(f"{c['pasos']} pasos ({c['celdas']} celdas)" for c in pf),
        fuente=f"{VO}/pml_vacio_fdtd_{ppl}.json :: casos[].t_cpu_s, pico_memoria_gb, pasos, celdas")

# ---------------------------------------------------------------- P1-8
lim = jl("limite-lectura/resultados/resultados_raw.json")
info = lim["info"]
for conj, etq in (("cuadratica", "frontera cuadrática"), ("lineal", "control lineal")):
    ts = [t["seg"] for t in lim["tareas"] if t["conjunto"] == conj]
    assert len(ts) == 40
    add("P1-8", "Experimento sintético: generación + QDA + lectura óptica de rango 2", f"{etq}, 40 tareas", "tarea", 40,
        t_total_cpu=None, t_pared=sum(ts),
        nom="3 detectores con vectores complejos a_k de dimensión 5 (preregistro P1-8); cifra total no registrada",
        act=f"{info['pasos']} pasos Adam (tasa {info['lr']}) x {len(info['semillas_init_O'])} inicializaciones por tarea (óptico)",
        reloj="pared (time.time() en analisis.py); CPU no registrada",
        fuente="limite-lectura/resultados/resultados_raw.json :: tareas[].seg (conjunto=%s)" % conj,
        nota=(f"El tiempo no se separa entre generación, QDA y óptico. Tiempo total del experimento: "
              f"{jl('limite-lectura/resultados/RESULTADOS_LIMITE.json')['segundos_totales']:.6g} s (pared, RESULTADOS_LIMITE.json). "
              "Sin tiempo de CPU no se calcula E_UB."))

# ---------------------------------------------------------------- EEG
cost_full = jl(f"{EEG}/results_full.json")["cost"]
cost_s5 = jl(f"{EEG}/results_seeds5.json")["cost"]
for tag, c, desc, act in (
    ("full", cost_full, "rejilla de 36 configuraciones, 17 sujetos, 50 folds externos con bucle interno",
     "hasta 90 épocas por entrenamiento (instantáneas 30/60/90 de una trayectoria; INFORME-NESTED.md)"),
    ("seeds5", cost_s5, "3 configuraciones finalistas, 5 semillas, LORO externo sin bucle interno",
     "90 épocas por entrenamiento (ADDENDUM-SEEDS5.md)"),
):
    add("EEG", "Validación anidada (GPU, --dev cuda)", f"EEG motor-imagery, {desc}", "entrenamiento", c["n_trainings"],
        t_total_cpu=None, t_pared=c["train_seconds_total"], act=act,
        reloj="pared (time.time() en nested_bench.py); CPU no registrada",
        fuente=f"{EEG}/results_{tag}.json :: cost.train_seconds_total, cost.n_trainings, cost.sec_per_training",
        nota=(f"sec_per_training={c['sec_per_training']:.6g} s (pared). Potencia de GPU no registrada: sin energía de GPU. "
              "Memoria/VRAM no registrada. Sin tiempo de CPU no se calcula E_UB."))

probe = jl(f"{EEG}/bench-historico/time_cpu_probe.json")
for k in sorted(probe):
    model, feat = k.split("|")
    add("EEG", f"Sonda de coste en CPU ({model}, {feat})", "EEG motor-imagery, n_train=100 (smoke_logs/time_cpu_probe.log)", "entrenamiento (90 épocas)", 1,
        t_total_cpu=None, t_pared=probe[k], act="90 épocas",
        reloj="pared (time.time() en time_cpu_probe.py), CPU 4 hilos; CPU de proceso no registrada",
        fuente=f"{EEG}/bench-historico/time_cpu_probe.json :: {k}",
        nota="Sonda para extrapolar coste, no resultado científico (según su docstring). Sin CPU de proceso no se calcula E_UB.")

inf = txt(f"{EEG}/INFORME-NESTED.md")
assert "335 s = 100 entrenamientos" in inf and "3,35 s/entrenamiento" in inf
add("EEG", "LORO polar + lattice32 f12w3 (GPU)", "EEG motor-imagery, 17 sujetos, 60 épocas", "entrenamiento", 100,
    t_total_cpu=None, t_pared=335.0, act="60 épocas",
    reloj="no declarado (cifra citada en texto)",
    fuente=f"{EEG}/INFORME-NESTED.md §5 (cita bench_f12w3.log: 335 s = 100 entrenamientos, 3,35 s/entrenamiento)",
    nota="Cifra citada; el log original (bench_f12w3.log) no está en la carpeta de evidencia. Sin CPU ni potencia: sin E_UB.")

# ---------------------------------------------------------------- resumen de razones
def mean_unit(ds, m):
    return P15[(ds, m)]["t_cpu_por_unidad_s"]


def ratio(num, den):
    if den == 0:
        return "no definida (0 s registrado)"
    return float("%.3g" % (num / den))


RAT = {"iris": {}, "wine_semilla_1049": {}, "wine_3_semillas": {}}
opt = {
    "iris": r_oi["t_cpu_por_unidad_s"],
    "wine_semilla_1049": r_wp["t_cpu_por_unidad_s"],
    "wine_3_semillas": r_w30["t_cpu_por_unidad_s"],
}
for key, opt_t in opt.items():
    ds = "iris" if key == "iris" else "wine"
    for m in ("B1", "B2", "B3", "B4", "B5", "B6"):
        RAT[key][m] = ratio(opt_t, mean_unit(ds, m))
bl_pair = {}
for ds in ("iris", "wine"):
    r = [x for x in ROWS if x["comparacion"] == "P0-4" and x["metodo"].startswith("Líneas base softmax") and x["conjunto"].startswith(ds.capitalize())][0]
    bl_pair[ds] = r["t_cpu_por_unidad_s"]
RAT["P0-4_pareja_lineal_cuadratico"] = {
    "iris": ratio(opt["iris"], bl_pair["iris"]),
    "wine_semilla_1049": ratio(opt["wine_semilla_1049"], bl_pair["wine"]),
    "wine_3_semillas": ratio(opt["wine_3_semillas"], bl_pair["wine"]),
}

hdr = {
    "schema": "p1-9.tabla_coste",
    "preregistro": "Benchmarks/coste-completo/PREREGISTRO-P1-9.md",
    "potencia_por_nucleo_W": P_NUCLEO_W,
    "advertencia_energia": ("La energía NO se mide. E_UB = t_CPU x 14 W es una cota superior declarada en el preregistro "
                            "(140 W / 10 núcleos); sin medidor externo ni contadores de potencia. No se estima energía de GPU."),
    "resolucion_reloj_cpu_s": TICK,
    "filas": ROWS,
    "razones_coste_optico_sobre_linea_base": {
        "definicion": "t_CPU medio por unidad del óptico / t_CPU medio por partición de la línea base (P1-5), mismas particiones",
        "optico_t_cpu_por_unidad_s": opt,
        "frente_a_B1_a_B6": RAT,
        "advertencia": ("Las líneas base suman <=0.08 s en 10 particiones (pocos ticks de 1/64 s): las razones tienen error "
                        "relativo grande y valen como orden de magnitud."),
    },
}


def dump(path, s):
    with open(os.path.join(HERE, path), "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


dump("TABLA-COSTE.json", json.dumps(hdr, indent=1, ensure_ascii=False, sort_keys=False) + "\n")


# ---------------------------------------------------------------- MD
def cell(x):
    return str(x).replace("|", "/").replace("\n", " ")


def fm(x):
    return x if isinstance(x, str) else f"{x:.6g}"


L = []
L.append("# TABLA-COSTE · P1-9")
L.append("")
L.append("Generada por `compilar_coste.py` a partir de resultados existentes (sin re-ejecutar nada). "
         "**La energía NO se mide.** `E_UB` = t_CPU × 14 W es solo una cota superior (140 W / 10 núcleos, preregistro §2); "
         "se calcula únicamente donde hay tiempo de CPU de proceso. \"no registrado\" = el dato no está en la evidencia.")
L.append("")
L.append("| # | Comp. | Método | Conjunto | Unidad | n | t CPU/unidad (s) | t CPU total (s) | t pared total (s) | Mem. pico | Parám. nom. | Parám. ident. | Actualizaciones/pasos | E_UB (J, cota sup.) | Fuente |")
L.append("|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---:|---|")
for r in ROWS:
    L.append("| " + " | ".join(cell(x) for x in (
        r["id"], r["comparacion"], r["metodo"], r["conjunto"], r["unidad"], r["n_unidades"],
        fm(r["t_cpu_por_unidad_s"]), fm(r["t_cpu_total_s"]), fm(r["t_pared_total_s"]), r["memoria_pico"],
        r["parametros_nominales"], r["parametros_identificables"], r["actualizaciones_o_pasos"],
        fm(r["E_UB_J"]), r["fuente"])) + " |")
L.append("")
L.append("## Notas por fila")
L.append("")
for r in ROWS:
    L.append(f"- Fila {r['id']} (reloj: {r['reloj_registrado']}): {r['nota'] or '-'}")
L.append("")
dump("TABLA-COSTE.md", "\n".join(L) + "\n")


# ---------------------------------------------------------------- INFORME
def nr_count(col):
    return sum(1 for r in ROWS if r[col] == NR)


n_rows = len(ROWS)
n_noE = sum(1 for r in ROWS if r["E_UB_J"] == NR)
eeg_rows = [r for r in ROWS if r["comparacion"] == "EEG"]
p18 = [r for r in ROWS if r["comparacion"] == "P1-8"]
fi = opt["iris"]
fw1 = opt["wine_semilla_1049"]
fw3 = opt["wine_3_semillas"]
tot_opt = r_oi["t_cpu_total_s"], r_wp["t_cpu_total_s"], r_w30["t_cpu_total_s"]
rr = RAT


def rt(key, m):
    v = rr[key][m]
    return v if isinstance(v, str) else f"{v:.3g}"


I = []
I.append("# Informe P1-9 · coste completo y energía (cota superior)")
I.append("")
I.append("Análisis descriptivo, sin decisión de superioridad. Compilado por `compilar_coste.py` solo con lectura de resultados existentes "
         "(ningún entrenamiento ni simulación se re-ejecutó).")
I.append("")
I.append("## Qué se incluye")
I.append(f"- {n_rows} filas en `TABLA-COSTE.json` / `TABLA-COSTE.md` (formato del preregistro §3), cada una con archivo y campo de origen.")
I.append("- P0-4: óptico Iris (4 reinicios x 500 pasos), óptico Wine (semilla 1049, semillas 1050-1051 y suma de 3 semillas), lineal + cuadrático.")
I.append("- P1-5: B1 a B6 en Iris y Wine; B1 a B4 en Breast Cancer y Digits.")
I.append("- P1-7: FDTD λ/16 y λ/24 (memoria pico registrada), solver directo (`medicion_coste.json`, solo las medidas) y pruebas PML en vacío.")
I.append("- P1-8: experimento sintético (cuadrática y control lineal). EEG: validación anidada en GPU, sonda en CPU y una cifra citada.")
I.append("")
I.append("## Advertencia: la energía NO se mide")
I.append("No hay medidor externo ni contadores de potencia de CPU accesibles, y las comparaciones de esta fase no tienen registro de potencia de GPU. "
         "`E_UB` = t_CPU x 14 W (140 W / 10 núcleos) es una cota superior por construcción, no una medida ni una estimación de consumo. "
         "No se calcula energía de GPU.")
I.append(f"- `E_UB` se calcula en {n_rows - n_noE} filas (las que tienen tiempo de CPU de proceso) y queda \"no registrado\" en {n_noE}.")
I.append("")
I.append("## Campos no registrados")
I.append(f"- Memoria pico: solo registrada en P1-7 (FDTD, solver, PML); no registrada en óptico, líneas base ni EEG ({nr_count('memoria_pico')} filas).")
I.append("- Parámetros identificables: solo donde el preregistro P0-4 los declara (lineal 10, cuadrático 30); del óptico, B2-B4, P1-8 y EEG: no registrados.")
I.append(f"- P1-8 ({len(p18)} filas): solo tiempo de pared (`time.time`), sin CPU, sin separar generación/QDA/óptico: sin E_UB.")
I.append(f"- EEG ({len(eeg_rows)} filas): GPU con tiempo de pared (4118 s en 1368 entrenamientos; 2625 s en 750), sin CPU, sin potencia de GPU, sin VRAM; "
         "la sonda CPU y la cifra de 335 s tampoco tienen CPU de proceso. Nada se rellena con estimaciones.")
I.append("- La sección `proyeccion` de `medicion_coste.json` es una proyección y se excluye; las extrapolaciones de INFORME-NESTED.md también.")
I.append("")
I.append("## Coste relativo: óptico frente a líneas base (CPU por ajuste)")
I.append(f"Óptico Iris: {fi:.4g} s por partición (4 reinicios x 500 pasos; total {tot_opt[0]:.6g} s en 10). "
         f"Óptico Wine: {fw1:.4g} s por entrenamiento (semilla 1049; total {tot_opt[1]:.6g} s en 10); "
         f"{fw3:.4g} s de media en 30 entrenamientos (total {tot_opt[2]:.6g} s).")
I.append("")
I.append("Razón = t CPU por ajuste del óptico / t CPU por partición de la línea base (P1-5, mismas particiones):")
I.append("")
I.append("| Óptico frente a | B1 lineal | B5 lineal P0-4 | B6 cuadrático | B2 SVM | B3 RF | B4 MLP |")
I.append("|---|---:|---:|---:|---:|---:|---:|")
for key, etq in (("iris", "Iris"), ("wine_semilla_1049", "Wine (semilla 1049)"), ("wine_3_semillas", "Wine (3 semillas)")):
    I.append(f"| {etq} | " + " | ".join(rt(key, m) for m in ("B1", "B5", "B6", "B2", "B3", "B4")) + " |")
I.append("")
pp = rr["P0-4_pareja_lineal_cuadratico"]
I.append(f"Con el tiempo conjunto lineal + cuadrático de P0-4: Iris {pp['iris']:.3g}x; Wine {pp['wine_semilla_1049']:.3g}x (semilla 1049), {pp['wine_3_semillas']:.3g}x (3 semillas). "
         "Como el lineal solo es una parte de ese tiempo, la razón frente al lineal solo es mayor o igual.")
I.append(f"Cautela: las líneas base suman <=0.08 s en 10 particiones (pocos ticks de {TICK:.6g} s); las razones valen como orden de magnitud. "
         "Descriptivo: el coste óptico es de varios órdenes de magnitud mayor que el de las líneas base en estas tareas pequeñas.")
I.append("")
I.append("## Integridad")
I.append("`SHA256SUMS.txt` lista los hashes de script, salidas y preregistro. Ejecutar `python compilar_coste.py` regenera las salidas byte a byte.")
assert len(I) <= 60, len(I)
dump("INFORME-P1-9.md", "\n".join(I) + "\n")

# ---------------------------------------------------------------- SHA256SUMS
names = ["PREREGISTRO-P1-9.md", "compilar_coste.py", "TABLA-COSTE.json", "TABLA-COSTE.md", "INFORME-P1-9.md"]
out = []
for n in names:
    with open(os.path.join(HERE, n), "rb") as f:
        out.append(f"{hashlib.sha256(f.read()).hexdigest()}  {n}")
dump("SHA256SUMS.txt", "\n".join(out) + "\n")
print(f"OK filas={n_rows} sin_E_UB={n_noE}")
