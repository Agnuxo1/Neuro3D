"""Modelos P1-8: QDA cerrado (Q) y lectura optica de rango restringido (O). Solo numpy.

O: P_k(xt) = |a_k^T xt|^2 = (u_k.xt)^2 + (v_k.xt)^2, a_k = u_k + i v_k en C^5, xt=(x,1).
Parametros: U, V de forma (3,5). Gradientes analiticos, verificados por diferencias finitas.
Hiperparametros no fijados por el preregistro (elegidos a priori): inicializacion
U,V ~ N(0, 0.5^2); perdida = entropia cruzada media sobre softmax(P/T).
"""
import numpy as np

T = 0.05
LR = 0.01
STEPS = 3000
INIT_STD = 0.5
INIT_SEEDS = range(5)


# ---------------- Q: QDA ----------------
def qda_fit(X, y, K=3):
    d = X.shape[1]
    Qs, pri = [], []
    for k in range(K):
        Xk = X[y == k]
        m = Xk.mean(0)
        S = (Xk - m).T @ (Xk - m) / len(Xk)  # MLE
        Si = np.linalg.inv(S)
        _, ld = np.linalg.slogdet(S)
        # score_k(xt) = xt^T Qk xt, Qk 5x5 simetrica (la constante entra por xt=(x,1))
        Q = np.zeros((d + 1, d + 1))
        Q[:d, :d] = -0.5 * Si
        Q[:d, d] = Q[d, :d] = 0.5 * Si @ m
        Q[d, d] = -0.5 * m @ Si @ m - 0.5 * ld + np.log(len(Xk) / len(X))
        Qs.append(Q)
    return np.array(Qs)


def quad_scores(Qs, X):
    Xt = np.hstack([X, np.ones((len(X), 1))])
    return np.einsum('ni,kij,nj->nk', Xt, Qs, Xt)


def qda_predict(Qs, X):
    return quad_scores(Qs, X).argmax(1)


# ---------------- O ----------------
class MinMax:
    def fit(self, X):
        self.lo = X.min(0); self.hi = X.max(0)
        self.rng_ = np.where(self.hi - self.lo > 0, self.hi - self.lo, 1.0)
        return self

    def __call__(self, X):
        return (X - self.lo) / self.rng_


def aug(X):
    return np.hstack([X, np.ones((len(X), 1))])


def optical_P(U, V, Xt):
    return (Xt @ U.T) ** 2 + (Xt @ V.T) ** 2  # (n,3)


def loss_grad(U, V, Xt, y, temp=T):
    n = len(y)
    P = optical_P(U, V, Xt)
    z = P / temp
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    S = e / e.sum(1, keepdims=True)
    L = -np.mean(np.log(S[np.arange(n), y] + 1e-300))
    G = S.copy(); G[np.arange(n), y] -= 1.0
    G /= n  # dL/dz
    GP = G / temp  # dL/dP
    # dP_k/dU_k = 2 (u_k.xt) xt
    gU = 2.0 * ((GP * (Xt @ U.T)).T @ Xt)
    gV = 2.0 * ((GP * (Xt @ V.T)).T @ Xt)
    return L, gU, gV


def adam_train(Xt, y, seed, steps=STEPS, lr=LR):
    rng = np.random.default_rng(seed)
    U = INIT_STD * rng.standard_normal((3, 5))
    V = INIT_STD * rng.standard_normal((3, 5))
    th = np.concatenate([U.ravel(), V.ravel()])
    m = np.zeros_like(th); v = np.zeros_like(th)
    b1, b2, eps = 0.9, 0.999, 1e-8
    for t in range(1, steps + 1):
        U = th[:15].reshape(3, 5); V = th[15:].reshape(3, 5)
        L, gU, gV = loss_grad(U, V, Xt, y)
        g = np.concatenate([gU.ravel(), gV.ravel()])
        m = b1 * m + (1 - b1) * g
        v = b2 * v + (1 - b2) * g * g
        mh = m / (1 - b1 ** t); vh = v / (1 - b2 ** t)
        th = th - lr * mh / (np.sqrt(vh) + eps)
    U = th[:15].reshape(3, 5); V = th[15:].reshape(3, 5)
    L, _, _ = loss_grad(U, V, Xt, y)
    return U, V, L


def optical_fit(Xtr, ytr):
    """Entrena 5 inicializaciones; elige la de menor perdida de ENTRENAMIENTO."""
    sc = MinMax().fit(Xtr)
    Xt = aug(sc(Xtr))
    best = None
    losses = []
    for s in INIT_SEEDS:
        U, V, L = adam_train(Xt, ytr, s)
        losses.append(float(L))
        if best is None or L < best[2]:
            best = (U, V, L, s)
    return dict(U=best[0], V=best[1], loss=float(best[2]), seed=best[3], losses=losses, scaler=sc)


def optical_predict(model, X):
    Xt = aug(model['scaler'](X))
    return optical_P(model['U'], model['V'], Xt).argmax(1)


def optical_Q(U, V):
    """Matrices 5x5 M_k = u u^T + v v^T de cada detector."""
    return np.einsum('ki,kj->kij', U, U) + np.einsum('ki,kj->kij', V, V)


def num_rank(M, rtol=1e-9):
    s = np.linalg.svd(M, compute_uv=False)
    return int((s > rtol * max(s[0], 1e-300)).sum()) if s[0] > 0 else 0


def pair_ranks(Qs):
    return {f"{i}{j}": num_rank(Qs[i] - Qs[j]) for i in range(3) for j in range(i + 1, 3)}


# ---------------- verificacion de gradiente ----------------
def check_gradient(seed=0, h=1e-6, n=60):
    rng = np.random.default_rng(seed)
    Xt = aug(rng.random((n, 4)))
    y = rng.integers(0, 3, n)
    U = 0.5 * rng.standard_normal((3, 5)); V = 0.5 * rng.standard_normal((3, 5))
    L, gU, gV = loss_grad(U, V, Xt, y, temp=1.0)  # T=1 evita saturacion numerica en el chequeo
    L2, gU2, gV2 = loss_grad(U, V, Xt, y, temp=T)
    out = {}
    for name, temp, (gu, gv) in (("T=1", 1.0, (gU, gV)), ("T=0.05", T, (gU2, gV2))):
        maxrel = 0.0
        for arr, g in ((U, gu), (V, gv)):
            for idx in np.ndindex(arr.shape):
                old = arr[idx]
                arr[idx] = old + h; Lp = loss_grad(U, V, Xt, y, temp)[0]
                arr[idx] = old - h; Lm = loss_grad(U, V, Xt, y, temp)[0]
                arr[idx] = old
                fd = (Lp - Lm) / (2 * h)
                rel = abs(fd - g[idx]) / max(1e-8, abs(fd) + abs(g[idx]))
                maxrel = max(maxrel, rel)
        out[name] = maxrel
    return out
