"""Analisis de los logits crudos de nested_bench.py (raw/<tag>/S###.npz). CPU, segundos. Todas las selecciones se hacen AQUI y solo con
datos permitidos: N1 usa solo logits internos; N2 solo los otros sujetos. Estimadores declarados en PREINSCRIPCION.md.
Uso: python analyze_nested.py --tag full   (escribe results_<tag>.json y results_<tag>.txt)"""
import argparse, glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20260930)


def bce(z, y):     # log-loss estable con logits
    z = z.astype(np.float64); return np.logaddexp(0, z) - y * z


def load(tag):
    S = {}
    for f in sorted(glob.glob(os.path.join(HERE, "raw", tag, "S*.npz"))):
        R = np.load(f, allow_pickle=False); meta = json.loads(str(R["meta"])); S[meta["sid"]] = (R, meta)
    return S


def boot_ci(d, B=20000):
    n = len(d); idx = rng.integers(0, n, (B, n)); bs = d[idx].mean(1)
    signs = rng.choice([-1, 1], (B, n)); p = float((np.abs((signs * d).mean(1)) >= abs(d.mean()) - 1e-12).mean())
    return dict(diff=float(d.mean()), ee=float(d.std(ddof=1) / np.sqrt(n)), ci95=[float(v) for v in np.percentile(bs, [2.5, 97.5])],
                p_signflip=p, wins=int((d > 0).sum()), ties=int((d == 0).sum()), losses=int((d < 0).sum()))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="smoke"); a = ap.parse_args()
    S = load(a.tag); subs = sorted(S); assert subs, "sin datos"
    meta0 = S[subs[0]][1]; E = meta0["epochs"]; default = (meta0["default"][0], meta0["default"][1], f"{meta0['default'][2]:g}", meta0["default"][3])
    cfgs = [(k, f, f"{w:g}", e) for k, f, w in meta0["triples"] for e in E]; C = len(cfgs); ci = {c: i for i, c in enumerate(cfgs)}
    assert default in ci, f"config por defecto {default} fuera de la rejilla"
    inner_on = meta0["inner"]
    # --- recolectar por sujeto y fold
    n = len(subs); loro = np.zeros((n, C)); loro_n = np.zeros(n)
    fallback = 0; nfolds = 0
    spear = []; costsec = 0.0; ntr = 0
    folds = []          # (s, corr[C], nte, innerBCE[C] or None, innerACC[C] or None)
    for si, sid in enumerate(subs):
        R, meta = S[sid]; costsec += float(R["seconds"][0]); ntr += int(R["n_trainings"][0]); corr = np.zeros(C); tot = 0
        for r in meta["runs"]:
            y = R[f"y|{r}"]; tot += len(y); c_f = np.array([((R[f"o|{r}|{k}|{f}|{w}|{e}"] > 0).astype(int) == y).sum() for k, f, w, e in cfgs], float)
            corr += c_f; nfolds += 1
            ib = ia = None
            if inner_on:
                vs = [int(k.split("|")[2]) for k in R.files if k.startswith(f"iv|{r}|")]
                if vs:
                    sb = np.zeros(C); sa = np.zeros(C); nv = 0
                    for v in vs:
                        yv = R[f"yv|{r}|{v}"]; nv += len(yv)
                        for j, (k, f, w, e) in enumerate(cfgs):
                            z = R[f"i|{r}|{v}|{k}|{f}|{w}|{e}"]; sb[j] += bce(z, yv).sum(); sa[j] += ((z > 0).astype(int) == yv).sum()
                    ib, ia = sb / nv, sa / nv
            folds.append((si, c_f, len(y), ib, ia))
        loro[si] = corr / tot; loro_n[si] = tot
    # --- estimadores
    d0 = ci[default]
    accN1 = np.zeros(n); accN1b = np.zeros(n); tots = np.zeros(n); pickN1 = []; pickN1b = []
    for si, c_f, nte, ib, ia in folds:
        tots[si] += nte
        if ib is None: j1 = j1b = d0; fallback += 1
        else:
            j1 = int(np.lexsort((np.arange(C) != d0, ib))[0])                  # menor BCE interna; empate -> defecto
            j1b = int(np.lexsort((np.arange(C) != d0, ib, -ia))[0])            # mayor exactitud interna; desempate BCE, luego defecto
            if np.std(ib) > 0 and np.std(c_f) > 0:
                r1 = np.argsort(np.argsort(ib)); r2 = np.argsort(np.argsort(-c_f)); spear.append(float(np.corrcoef(r1, r2)[0, 1]))
        accN1[si] += c_f[j1]; accN1b[si] += c_f[j1b]; pickN1.append(j1); pickN1b.append(j1b)
    accN1 /= tots; accN1b /= tots
    accN2 = np.zeros(n); pickN2 = []
    for si in range(n):
        others = np.delete(np.arange(n), si); j2 = int(np.argmax(loro[others].mean(0))); accN2[si] = loro[si, j2]; pickN2.append(j2)
    accN3 = loro[:, d0]; jmax = int(np.argmax(loro.mean(0))); accMax = loro[:, jmax]
    accMean = loro.mean(1)                                                   # rendimiento medio de una config al azar de la rejilla
    oracle_sub = loro.max(1)                                                 # cota superior sesgada: mejor config por sujeto mirando el test
    res = dict(tag=a.tag, n_subjects=n, subjects=subs, n_configs=C, default="|".join(map(str, default)), inner=inner_on, n_outer_folds=nfolds,
               fallback_folds_default=fallback, cost=dict(train_seconds_total=costsec, n_trainings=ntr, sec_per_training=costsec / max(ntr, 1)))
    def mean(v): return dict(mean=float(v.mean()), ee=float(v.std(ddof=1) / np.sqrt(len(v))))
    res["estimates"] = {"N1_nested_per_subject_innerBCE": mean(accN1), "N1b_nested_per_subject_innerACC": mean(accN1b),
                        "N2_LOSO_global_config": mean(accN2), "N3_default_fixed": mean(accN3),
                        "MAX_LORO_grid_biased": dict(mean=float(accMax.mean()), cfg="|".join(map(str, cfgs[jmax]))),
                        "MEAN_over_grid": mean(accMean), "ORACLE_per_subject_biased": mean(oracle_sub)}
    res["contrasts_paired_by_subject"] = {"N1-N3": boot_ci(accN1 - accN3), "N2-N3": boot_ci(accN2 - accN3), "N1-N2": boot_ci(accN1 - accN2),
                                          "N1-MEANgrid": boot_ci(accN1 - accMean), "N3-MEANgrid": boot_ci(accN3 - accMean)}
    res["optimism_estimates"] = dict(MAX_minus_N2=float(accMax.mean() - accN2.mean()), MAX_minus_N1=float(accMax.mean() - accN1.mean()),
                                     default_minus_N2=float(accN3.mean() - accN2.mean()))
    def freq(picks):
        cnt = np.bincount(picks, minlength=C) / len(picks)
        out = {"|".join(map(str, cfgs[j])): float(cnt[j]) for j in np.argsort(-cnt)[:8]}
        dims = {}
        for di, nm in enumerate(("kind", "feat", "wd", "epochs")):
            dd = {}
            for j, p in enumerate(cnt): dd[str(cfgs[j][di])] = dd.get(str(cfgs[j][di]), 0.0) + float(p)
            dims[nm] = dd
        return dict(top=out, by_dimension=dims, distinct_configs_used=int((cnt > 0).sum()))
    res["selection_freq"] = {"N1": freq(pickN1), "N1b": freq(pickN1b), "N2": freq(pickN2)}
    res["inner_signal_spearman_BCE_vs_outer_acc"] = dict(mean=float(np.mean(spear)) if spear else None, frac_positive=float(np.mean(np.array(spear) > 0)) if spear else None,
                                                         n=len(spear), note="rho>0 = a menor BCE interna, mayor exactitud externa (la seleccion interna informa)")
    # --- tabla LORO por config y efectos marginales
    res["loro_by_config"] = {"|".join(map(str, c)): float(loro[:, ci[c]].mean()) for c in cfgs}
    marg = {}
    for di, nm in enumerate(("kind", "feat", "wd", "epochs")):
        levels = sorted({str(c[di]) for c in cfgs}); mm = {}
        for lv in levels: mm[lv] = loro[:, [j for j, c in enumerate(cfgs) if str(c[di]) == lv]].mean(1)
        marg[nm] = {lv: float(v.mean()) for lv, v in mm.items()}
        if len(levels) > 1:
            ref = levels[0]
            marg[nm]["paired_vs_" + ref] = {lv: boot_ci(mm[lv] - mm[ref]) for lv in levels[1:]}
    res["marginal_effects"] = marg
    # --- conjuntos (exploratorio, declarados): media de logits polar+lattice32 (fisicos) y polar+lattice32+libre, en la config por defecto
    ens = {}
    for name, kinds in (("E1_polar+lattice32", ["polar", "lattice32"]), ("E2_polar+lattice32+free", ["polar", "lattice32", "free"])):
        if not all((k, default[1], default[2], default[3]) in ci for k in kinds): continue
        acc = np.zeros(n)
        for si, sid in enumerate(subs):
            R, meta = S[sid]; c = 0; t = 0
            for r in meta["runs"]:
                y = R[f"y|{r}"]; z = sum(R[f"o|{r}|{k}|{default[1]}|{default[2]}|{default[3]}"] for k in kinds); c += ((z > 0).astype(int) == y).sum(); t += len(y)
            acc[si] = c / t
        ens[name] = dict(mean=float(acc.mean()), vs_default=boot_ci(acc - accN3))
    # --- exploratorio T1: umbral en la mediana de los logits del run de test (sin etiquetas; supone test equilibrado) solo en folds externos
    #     realmente equilibrados (mean(y)=0,5). Config por defecto. Sirve para juzgar la "calibracion por sujeto" con datos ya guardados.
    dz, dm, nb, bias = np.full(n, np.nan), np.full(n, np.nan), np.zeros(n), []
    for si, sid in enumerate(subs):
        R, meta = S[sid]; cz = cm = t = 0
        for r in meta["runs"]:
            y = R[f"y|{r}"]; z = R[f"o|{r}|{default[0]}|{default[1]}|{default[2]}|{default[3]}"]; bias.append(float((z > 0).mean() - y.mean()))
            if abs(y.mean() - 0.5) < 1e-9:
                cz += ((z > 0).astype(int) == y).sum(); cm += ((z > np.median(z)).astype(int) == y).sum(); t += len(y)
        if t: dz[si], dm[si], nb[si] = cz / t, cm / t, t
    ok = ~np.isnan(dz)
    res["T1_median_threshold_exploratory"] = dict(n_subjects=int(ok.sum()), acc_zero_threshold=float(dz[ok].mean()), acc_median_threshold=float(dm[ok].mean()),
        diff=boot_ci((dm - dz)[ok]) if ok.sum() > 2 else None, mean_pred_move_minus_true_move_fraction_all_folds=float(np.mean(bias)),
        mean_abs_prior_bias=float(np.mean(np.abs(bias))))
    res["ensembles_exploratory"] = ens
    json.dump(res, open(os.path.join(HERE, f"results_{a.tag}.json"), "w"), indent=1)
    # --- texto
    L = [f"== nested tag={a.tag}: {n} sujetos, {C} configuraciones, {nfolds} folds externos ({fallback} sin inner valido -> defecto {res['default']})",
         f"   coste: {ntr} entrenamientos, {costsec:.0f} s de entrenamiento ({costsec / max(ntr, 1):.2f} s/ent.)"]
    for k, v in res["estimates"].items(): L.append(f"   {k:38s} {v['mean']:.4f}" + (f"  ee {v['ee']:.4f}" if 'ee' in v else f"  [{v['cfg']}]"))
    for k, v in res["contrasts_paired_by_subject"].items(): L.append(f"   {k:14s} {v['diff']:+.4f} IC95 [{v['ci95'][0]:+.4f},{v['ci95'][1]:+.4f}] p_sf {v['p_signflip']:.3f}  {v['wins']}/{v['ties']}/{v['losses']}")
    L.append(f"   optimismo: {res['optimism_estimates']}")
    L.append(f"   senal interna Spearman {res['inner_signal_spearman_BCE_vs_outer_acc']}")
    for m in ("N1", "N2"): L.append(f"   frecuencia {m}: {res['selection_freq'][m]['top']} (configs distintas {res['selection_freq'][m]['distinct_configs_used']})")
    L.append(f"   ensembles: { {k: round(v['mean'], 4) for k, v in ens.items()} }")
    L.append(f"   T1 umbral mediana (folds equilibrados): { {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res['T1_median_threshold_exploratory'].items() if k != 'diff'} }")
    open(os.path.join(HERE, f"results_{a.tag}.txt"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
