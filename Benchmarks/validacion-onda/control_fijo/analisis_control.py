"""Analisis del control P1-7 con dispositivo fijo. E_max con la misma funcion que analisis_validacion.py
(resumen_malla importada, no redefinida). Decision del preregistro: |E_max(16,fijo) - 0,0275| < 0,005."""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(AQUI)
sys.path.insert(0, BASE)
import analisis_validacion as av  # noqa: E402

RES = os.path.join(AQUI, "resultados")
E24_REF = 0.0275
CONV = 0.005


def main():
    datos = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(RES, "control_fijo_16_k*.json")))]
    assert len(datos) == 12
    # resumen_malla usa err_P1/err_P2 y otros campos; el control aporta los necesarios
    for d in datos:
        d.setdefault("P1_modelo_dif", d["P1_modelo"]); d.setdefault("P2_modelo_dif", d["P2_modelo"])
        d["suma_solver"] = d["P1_solver"] + d["P2_solver"]; d["t_por_paso_s"] = d["t_cpu_s"] / d["pasos"]
        d["pico_memoria_gb"] = 0.0
    m = av.resumen_malla(datos)
    emax = m["E_max"]
    ref = json.load(open(os.path.join(BASE, "resultados", "RESULTADOS_VALIDACION.json")))["mallas"]
    e24_json, e16_orig = ref["24"]["E_max"], ref["16"]["E_max"]
    dif = abs(emax - E24_REF)
    sostenida = dif < CONV
    cal = json.load(open(os.path.join(RES, "calibracion_n_fijo_16.json")))
    hashes = {f: hashlib.sha256(open(os.path.join(BASE, f), "rb").read()).hexdigest()
              for f in ("mzi_fdtd.py", "fdtd2d.py", "analisis_validacion.py")}
    out = dict(E_max_16_fijo=emax, k_peor=m["k_peor"], puerto_peor=m["puerto_peor"], E_max_24_referencia=E24_REF,
               E_max_24_json=e24_json, E_max_16_original_n_recalibrado=e16_orig, diferencia=dif, umbral_convergencia=CONV,
               umbral_H0=av.UMBRAL, E_max_16_fijo_sobre_umbral_H0=bool(emax > av.UMBRAL),
               decision="convergencia con dispositivo fijo SOSTENIDA" if sostenida else "convergencia con dispositivo fijo NO DEMOSTRADA",
               calibracion_n_fijo_16=dict(n=cal["n"], R=cal["R"], T=cal["T"], dif_R=cal["dif_R"], dif_T=cal["dif_T"],
                                          no_calibrado_en_lambda16=cal["no_calibrado_en_lambda16"]),
               t_cpu_total_s=m["t_cpu_total_s"], t_cpu_calibracion_s=cal["t_cpu_s"], dif_regimen_max=m["dif_regimen_max"],
               puntos=m["puntos"], sha256_scripts=hashes)
    json.dump(out, open(os.path.join(RES, "RESULTADOS_CONTROL.json"), "w"), indent=1)
    L = ["# Control P1-7 con dispositivo fijo (lambda/16, n = %.6f)" % cal["n"], "",
         f"**Decision: {out['decision']}.** E_max(16, fijo) = {emax:.4f}; E_max(24) = {E24_REF}; diferencia {dif:.4f} (criterio < {CONV}).", "",
         f"E_max(16, n recalibrado, original) = {e16_orig:.4f}. Umbral H0 {av.UMBRAL}: E_max(16, fijo) {'>' if emax > av.UMBRAL else '<='} umbral.",
         f"Calibracion con n fijo en lambda/16 (sin ajuste): |r|^2 = {cal['R']:.5f}, |t|^2 = {cal['T']:.5f}; "
         f"dif. con 0,5: {cal['dif_R']:+.5f} / {cal['dif_T']:+.5f}; "
         + ("**dispositivo no calibrado en lambda/16** (> 0,005)." if cal["no_calibrado_en_lambda16"] else "dentro de 0,005."), "",
         "| k | dL_eff | P1 solver | P1 modelo | P2 solver | P2 modelo | error | error original |", "|---|---|---|---|---|---|---|---|"]
    orig = {d["k"]: d["err_original_n_recalibrado"] for d in datos}
    L += [f"| {q['k']} | {q['dL_eff']:.4f} | {q['P1_solver']:.4f} | {q['P1_modelo']:.4f} | {q['P2_solver']:.4f} | {q['P2_modelo']:.4f} | {q['err']:.4f} | {orig[q['k']]:.4f} |" for q in m["puntos"]]
    open(os.path.join(RES, "RESULTADOS_CONTROL.md"), "w", encoding="utf8", newline="\n").write("\n".join(L) + "\n")
    lin = []
    for f in sorted(glob.glob(os.path.join(RES, "*"))):
        if os.path.isfile(f) and not f.endswith("SHA256SUMS.txt"):
            lin.append(f"{hashlib.sha256(open(f, 'rb').read()).hexdigest()}  {os.path.basename(f)}")
    open(os.path.join(RES, "SHA256SUMS.txt"), "w", encoding="utf8", newline="\n").write("\n".join(lin) + "\n")
    print(out["decision"], emax, dif)


if __name__ == "__main__":
    main()
