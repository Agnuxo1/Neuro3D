"""Analisis P1-7 (Enmiendas 1 y 2): E_max por malla, diferencia entre mallas y decision (seccion 6).

E_max = maximo sobre puertos y desplazamientos del espejo de |P_solver - P_modelo|.
Decision para w = 8 lambda:
  - diferencia de E_max entre mallas >= 0,005            -> NO CONCLUYENTE (Enmienda 2)
  - E_max <= 0,02 en ambas mallas (y diferencia < 0,005) -> H0 NO REFUTADA
  - E_max  > 0,02 en ambas mallas (y diferencia < 0,005) -> H0 REFUTADA
  - otro caso                                           -> NO CONCLUYENTE
Escribe resultados/RESULTADOS_VALIDACION.json/.md y resultados/SHA256SUMS.txt (LF).
Uso: python analisis_validacion.py"""
from __future__ import annotations

import glob
import hashlib
import json
import os

import numpy as np

UMBRAL = 0.02
CONVERGENCIA = 0.005
RES = "resultados"


def cargar(ppl):
    fs = sorted(glob.glob(os.path.join(RES, f"mzi_fdtd_{ppl}_k*.json")))
    return [json.load(open(f)) for f in fs]


def resumen_malla(datos):
    if not datos:
        return None
    errs = [(max(d["err_P1"], d["err_P2"]), d) for d in datos]
    emax, peor = max(errs, key=lambda x: x[0])
    err_dif = [max(abs(d["P1_solver"] - d["P1_modelo_dif"]), abs(d["P2_solver"] - d["P2_modelo_dif"])) for d in datos]
    return dict(
        simulaciones=len(datos), E_max=float(emax), k_peor=peor["k"], dL_eff_peor=peor["dL_eff"],
        puerto_peor="P1" if peor["err_P1"] >= peor["err_P2"] else "P2",
        E_max_diagnostico_con_difraccion=float(max(err_dif)),
        perdida_solver_max=float(max(1 - d["suma_solver"] for d in datos)),
        perdida_solver_min=float(min(1 - d["suma_solver"] for d in datos)),
        dif_regimen_max=float(max(d["dif_regimen"] for d in datos)),
        t_cpu_total_s=float(sum(d["t_cpu_s"] for d in datos)),
        t_cpu_por_simulacion_s=float(np.mean([d["t_cpu_s"] for d in datos])),
        t_wall_medio_s=float(np.mean([d["t_wall_s"] for d in datos])),
        t_por_paso_medio_s=float(np.mean([d["t_por_paso_s"] for d in datos])),
        celdas=datos[0]["celdas"], pasos=datos[0]["pasos"], pico_memoria_gb=float(max(d["pico_memoria_gb"] for d in datos)),
        puntos=[dict(k=d["k"], dL_eff=d["dL_eff"], P1_solver=d["P1_solver"], P2_solver=d["P2_solver"],
                     P1_modelo=d["P1_modelo"], P2_modelo=d["P2_modelo"], err=max(d["err_P1"], d["err_P2"]))
                for d in datos])


def decidir(e16, e24):
    dif = abs(e16 - e24)
    if dif >= CONVERGENCIA:
        return "NO CONCLUYENTE", f"la diferencia de E_max entre mallas ({dif:.4f}) es >= {CONVERGENCIA}"
    if e16 <= UMBRAL and e24 <= UMBRAL:
        return "H0 NO REFUTADA", f"E_max <= {UMBRAL} en ambas mallas y diferencia {dif:.4f} < {CONVERGENCIA}"
    if e16 > UMBRAL and e24 > UMBRAL:
        return "H0 REFUTADA", f"E_max > {UMBRAL} en ambas mallas y diferencia {dif:.4f} < {CONVERGENCIA}"
    return "NO CONCLUYENTE", "E_max a ambos lados del umbral"


def hashes():
    base = os.path.abspath(".")
    archivos = ["solver2d.py", "calibracion.py", "mzi.py", "test_pml_vacio.py", "medicion_coste.py",
                "fdtd2d.py", "test_pml_vacio_fdtd.py", "calibracion_fdtd.py", "mzi_fdtd.py", "analisis_validacion.py",
                "calibracion_incidencia_normal.json", "calibracion_45.json", "calibracion_fdtd_45.json",
                "PREREGISTRO-P1-7.md", "INFORME-EJECUCION-P1-7.md", os.path.join("..", "..", "Blender", "tests", "test_validacion_onda.py")]
    archivos += sorted(glob.glob(os.path.join(RES, "*.json")) + glob.glob(os.path.join(RES, "RESULTADOS_VALIDACION.md")))
    lineas = []
    for a in archivos:
        if os.path.isfile(a) and not a.endswith("SHA256SUMS.txt"):
            hsh = hashlib.sha256(open(a, "rb").read()).hexdigest()
            lineas.append(f"{hsh}  {a.replace(os.sep, '/')}")
    with open(os.path.join(RES, "SHA256SUMS.txt"), "w", encoding="utf8", newline="\n") as fh:
        fh.write("\n".join(lineas) + "\n")
    return len(lineas)


def main():
    m16, m24 = resumen_malla(cargar(16)), resumen_malla(cargar(24))
    out = dict(umbral=UMBRAL, convergencia=CONVERGENCIA, w_lambda=8.0, mallas={"16": m16, "24": m24})
    if m16 and m24:
        decision, motivo = decidir(m16["E_max"], m24["E_max"])
        out.update(diferencia_E_max_entre_mallas=abs(m16["E_max"] - m24["E_max"]), decision=decision, motivo=motivo)
    else:
        out.update(decision="INCOMPLETO", motivo="faltan simulaciones")
    json.dump(out, open(os.path.join(RES, "RESULTADOS_VALIDACION.json"), "w"), indent=1)
    L = ["# Resultados de la validacion P1-7 (MZI a 45 grados, w = 8 lambda, FDTD)", "",
         f"**Decision: {out['decision']}** ({out['motivo']}).", "",
         "| Malla | Simulaciones | E_max | Punto peor (k, dL_eff, puerto) | Dif. regimen max | Perdida solver | CPU por simulacion | Memoria pico |",
         "|---|---|---|---|---|---|---|---|"]
    for p, m in (("lambda/16", m16), ("lambda/24", m24)):
        if m:
            L.append(f"| {p} | {m['simulaciones']} | {m['E_max']:.4f} | {m['k_peor']}, {m['dL_eff_peor']:.3f}, {m['puerto_peor']} | "
                     f"{m['dif_regimen_max']:.1e} | {m['perdida_solver_min']:.3f}-{m['perdida_solver_max']:.3f} | "
                     f"{m['t_cpu_por_simulacion_s']:.0f} s | {m['pico_memoria_gb']:.2f} GB |")
    if "diferencia_E_max_entre_mallas" in out:
        L += ["", f"Diferencia de E_max entre mallas: {out['diferencia_E_max_entre_mallas']:.4f} (criterio < {CONVERGENCIA}).",
              f"Umbral de H0: E_max <= {UMBRAL}.", "",
              "Diagnostico exploratorio (no preregistrado): E_max frente al mismo modelo con difraccion gaussiana libre: "
              + ", ".join(f"{p}: {m['E_max_diagnostico_con_difraccion']:.4f}" for p, m in (("lambda/16", m16), ("lambda/24", m24)) if m) + "."]
        for p, m in (("lambda/16", m16), ("lambda/24", m24)):
            if m:
                L += ["", f"## Puntos {p}", "", "| k | dL_eff | P1 solver | P1 modelo | P2 solver | P2 modelo | error |", "|---|---|---|---|---|---|---|"]
                L += [f"| {q['k']} | {q['dL_eff']:.4f} | {q['P1_solver']:.4f} | {q['P1_modelo']:.4f} | {q['P2_solver']:.4f} | {q['P2_modelo']:.4f} | {q['err']:.4f} |" for q in m["puntos"]]
    open(os.path.join(RES, "RESULTADOS_VALIDACION.md"), "w", encoding="utf8", newline="\n").write("\n".join(L) + "\n")
    n = hashes()
    print(out["decision"], "-", out["motivo"], "| hashes:", n)


if __name__ == "__main__":
    main()
