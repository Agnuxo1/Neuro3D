"""Medicion de coste (tiempo, nnz(LU), memoria) de la factorizacion dispersa con dominios cuadrados
de tamano creciente (mismo operador con PML), y extrapolacion a los dominios del interferometro.
Uso: python medicion_coste.py [lados en celdas ...]  -> resultados/medicion_coste.json"""
import json, os, sys, time
import numpy as np
import psutil
import solver2d as s

def medir(lado):
    m = s.Malla(lado, lado, 1/16, pml_x=48, pml_y=48)
    pec = np.zeros((m.nx, m.ny), bool); pec[lado//2, lado//3:2*lado//3] = True
    A = s.construir_operador(m, pec=pec)
    p = psutil.Process()
    base = p.memory_info().rss
    t0 = time.time(); f = s.factorizar(A); t = time.time() - t0
    pico = p.memory_info().peak_wset
    return dict(lado=lado, N=m.nx*m.ny, t_wall_s=t, t_cpu_s=f.t_factor, nnz_lu=f.nnz_lu,
                pico_memoria_gb=pico/2**30, memoria_base_gb=base/2**30)

if __name__ == "__main__":
    lados = [int(a) for a in sys.argv[1:]] or [250, 400, 560, 750]
    res = []
    for l in lados:
        r = medir(l); res.append(r); print(json.dumps(r), flush=True)
    N = np.array([r["N"] for r in res], float)
    pt = np.polyfit(np.log(N), np.log([r["t_cpu_s"] for r in res]), 1)
    pn = np.polyfit(np.log(N), np.log([r["nnz_lu"] for r in res]), 1)
    out = dict(medidas=res, exponente_tiempo=pt[0], coef_tiempo=float(np.exp(pt[1])),
               exponente_nnz=pn[0], coef_nnz=float(np.exp(pn[1])))
    os.makedirs("resultados", exist_ok=True)
    json.dump(out, open(os.path.join("resultados", "medicion_coste.json"), "w"), indent=1)
    print("exp tiempo %.3f, exp nnz %.3f" % (pt[0], pn[0]))
