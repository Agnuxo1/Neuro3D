"""Auditoria P1-7 control: C2, C3, C4 (solo lectura sobre el repo). Uso: python -B audit_c4.py"""
import glob, json, os, sys, time
import numpy as np

BASE = r"D:\PROJECTS\9_NEBULA_NEW\Benchmarks\validacion-onda"
sys.dont_write_bytecode = True
sys.path.insert(0, BASE)
import analisis_validacion as av   # misma resumen_malla (E_max)
import calibracion_fdtd as cf
import calibracion as cal
import fdtd2d as f
import mzi_fdtd as m

def cargar(pat):
    return [json.load(open(x)) for x in sorted(glob.glob(pat))]

orig16 = cargar(os.path.join(BASE, "resultados", "mzi_fdtd_16_k*.json"))
orig24 = cargar(os.path.join(BASE, "resultados", "mzi_fdtd_24_k*.json"))
ctl = cargar(os.path.join(BASE, "control_fijo", "resultados", "control_fijo_16_k*.json"))

def emax(ds):  # funcion exacta de analisis_validacion
    return av.resumen_malla(ds)["E_max"]

# ---- C2
e24 = emax(orig24)
for d in ctl:
    d["P1_modelo_dif"], d["P2_modelo_dif"] = d["P1_modelo"], d["P2_modelo"]
    d["suma_solver"] = d["P1_solver"] + d["P2_solver"]; d["t_por_paso_s"] = 1.0; d["pico_memoria_gb"] = 0.0
e16f = emax(ctl)
e16o = emax(orig16)
print(f"C2 E_max(24)={e24:.5f} E_max(16 fijo)={e16f:.5f} E_max(16 orig recal)={e16o:.5f} dif={abs(e16f-e24):.5f}")
print("   n puntos 24/16/ctl:", len(orig24), len(orig16), len(ctl), " CPU control sum:", round(sum(d["t_cpu_s"] for d in ctl)))

# ---- C3: recalcular calibracion con n fijo en lambda/16
n = json.load(open(os.path.join(BASE, "calibracion_fdtd_45.json")))["mallas"]["24"]["n_usado"]
rs = cf.rt_fdtd(16, n, int(round(cal.D_NOMINAL * 16)))
R, T = abs(rs["r"]) ** 2, abs(rs["t"]) ** 2
print(f"C3 n={n!r} |r|^2={R:.5f} |t|^2={T:.5f} (recalculado, {rs['t_cpu_s']:.1f}s cpu)")
r_fix, t_fix = rs["r_c"], rs["t_c"]
c0 = json.load(open(os.path.join(BASE, "control_fijo", "resultados", "calibracion_n_fijo_16.json")))
print("   plano medio recalculado vs guardado:", abs(r_fix - complex(c0["plano_medio"]["r_re"], c0["plano_medio"]["r_im"])), abs(t_fix - complex(c0["plano_medio"]["t_re"], c0["plano_medio"]["t_im"])))

# ---- C4 (ii): solo se cambian r,t del modelo; el solver no se toca (potencias leidas de JSON)
pm = json.load(open(os.path.join(BASE, "calibracion_fdtd_45.json")))["mallas"]["16"]["plano_medio"]
r_rec, t_rec = complex(pm["r_re"], pm["r_im"]), complex(pm["t_re"], pm["t_im"])
n_p = f.pasos_por_periodo(16); ky0 = f.ky_diagonal(16, n_p)

def modelo_P(k, n_film, r, t):
    g = m.geometria(16, k, n_film)
    mod = m.modelo(g, r, t, ky0)
    return mod["P1"], mod["P2"]

def E(solver_ds, n_film, r, t):
    errs = []
    for d in solver_ds:
        P1, P2 = modelo_P(d["k"], n_film, r, t)
        errs.append(max(abs(d["P1_solver"] - P1), abs(d["P2_solver"] - P2)))
    return max(errs), errs

n_rec = orig16[0]["n_film"]
# control de coherencia: n_film no entra en el modelo -> misma salida con cualquier n
a = modelo_P(3, n, r_fix, t_fix); b = modelo_P(3, n_rec, r_fix, t_fix)
print("C4 modelo independiente de n_film (misma r,t):", a == b, a)
cases = {
    "A solver n fijo | modelo r,t n fijo   (control tal cual)": (ctl, n, r_fix, t_fix),
    "B solver n fijo | modelo r,t recalibrado (50/50)":        (ctl, n, r_rec, t_rec),
    "C solver recal  | modelo r,t n fijo":                      (orig16, n_rec, r_fix, t_fix),
    "D solver recal  | modelo r,t recalibrado (original P1-7)": (orig16, n_rec, r_rec, t_rec),
}
out = {}
for nom, (ds, nf, r, t) in cases.items():
    e, errs = E(ds, nf, r, t)
    out[nom] = e
    print(f"   {nom}: E_max={e:.4f}  (k0 err={errs[0]:.4f}, min={min(errs):.4f})")
# k=0: potencia del modelo vs 4RT y perdida del solver
for nom, (r, t) in (("fijo", (r_fix, t_fix)), ("recal", (r_rec, t_rec))):
    R_, T_ = abs(r) ** 2, abs(t) ** 2
    print(f"   {nom}: |r|^2={R_:.4f} |t|^2={T_:.4f} 4RT={4*R_*T_:.4f}")
sol = ctl[0]["P1_solver"] + ctl[0]["P2_solver"]; sol_o = orig16[0]["P1_solver"] + orig16[0]["P2_solver"]
print(f"   k0 solver suma: fijo={sol:.4f} recal={sol_o:.4f}; P1_solver fijo={ctl[0]['P1_solver']:.4f} recal={orig16[0]['P1_solver']:.4f}")
# contribucion de la perdida del solver al error: err vs (suma_modelo - suma_solver)
for d in ctl:
    pass
res = [(d["k"], max(d["err_P1"], d["err_P2"]), (d["P1_modelo"] + d["P2_modelo"]) - (d["P1_solver"] + d["P2_solver"])) for d in ctl]
print("   k, err, exceso de suma modelo-solver:", [(k, round(e, 4), round(x, 4)) for k, e, x in res])
json.dump(dict(E24=e24, E16fijo=e16f, E16orig=e16o, R=R, T=T, casos=out), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_c4.json"), "w"), indent=1)
