"""Generadores de tareas gaussianas sinteticas (P1-8). Solo numpy.

Parametros de generacion (fijados antes de ejecutar, no ajustados con resultados):
  medias de clase ~ N(0, 1.5^2 I_4); covarianza SPD: S = A A^T / 4 + 0.25 I, A ~ N(0,1) 4x4.
  Cada clase tiene 200 puntos; entrenamiento 133/133/134 y prueba 67/67/66 (400/200, estratificado).
"""
import numpy as np

D = 4
K = 3
PER_CLASS = 200
N_TRAIN = (133, 133, 134)
MEAN_SCALE = 1.5


def _spd(rng):
    A = rng.standard_normal((D, D))
    return A @ A.T / D + 0.25 * np.eye(D)


def make_task(seed, common_cov=False):
    rng = np.random.default_rng(seed)
    means = MEAN_SCALE * rng.standard_normal((K, D))
    if common_cov:
        S = _spd(rng)
        covs = [S.copy() for _ in range(K)]
    else:
        covs = [_spd(rng) for _ in range(K)]
    Xtr, ytr, Xte, yte = [], [], [], []
    for k in range(K):
        X = rng.multivariate_normal(means[k], covs[k], size=PER_CLASS)
        X = X[rng.permutation(PER_CLASS)]
        n = N_TRAIN[k]
        Xtr.append(X[:n]); ytr += [k] * n
        Xte.append(X[n:]); yte += [k] * (PER_CLASS - n)
    Xtr = np.vstack(Xtr); ytr = np.array(ytr)
    Xte = np.vstack(Xte); yte = np.array(yte)
    p = rng.permutation(len(ytr)); Xtr, ytr = Xtr[p], ytr[p]
    p = rng.permutation(len(yte)); Xte, yte = Xte[p], yte[p]
    return dict(seed=seed, Xtr=Xtr, ytr=ytr, Xte=Xte, yte=yte, means=means, covs=covs)


QUAD_SEEDS = list(range(0, 40))
LIN_SEEDS = list(range(100, 140))


def quad_tasks():
    return [make_task(s, False) for s in QUAD_SEEDS]


def lin_tasks():
    return [make_task(s, True) for s in LIN_SEEDS]
