"""P1-5: version multiclase generica del softmax lineal/cuadratico de fit_baseline (Blender/blender_lab/classifier_comparison_v1.py).

Mismo objetivo: media de la entropia cruzada + 0.5*l2*||W||^2 (el L2 penaliza todos los pesos, incluida la columna constante),
mismo optimizador (L-BFGS-B, W0 = 0) y mismas opciones. Cambios respecto a fit_baseline: numero de clases y de atributos
arbitrarios; las columnas de rango cero en entrenamiento se escalan a 0 (en lugar de abortar); no aborta si no converge,
sino que devuelve 'converged' y el gradiente maximo para que el llamante lo registre.
Codificacion (identica a encode_real_features generalizada): min-max con el rango de entrenamiento, sin recorte; se anade una
columna constante 1 al final; cada fila se normaliza a norma euclidiana 1.
"""
import time
import numpy as np

CONFIG = {'l2': 0.001, 'maxiter': 2000, 'gtol': 1e-08, 'ftol': 1e-12, 'maximum_gradient_abs': 1e-05}


def minmax_fit(x_train):
    x = np.asarray(x_train, dtype=np.float64)
    return x.min(axis=0), x.max(axis=0)


def minmax_apply(x, lo, hi):
    """Escalado min-max sin recorte; las columnas con hi==lo quedan en 0."""
    x = np.asarray(x, dtype=np.float64)
    span = hi - lo
    ok = span > 0
    out = np.zeros_like(x)
    out[:, ok] = (x[:, ok] - lo[ok]) / span[ok]
    return out


def coherent_encode(x_scaled):
    """Anade la columna constante 1 y normaliza cada fila a norma 1 (como encode_real_features)."""
    x = np.asarray(x_scaled, dtype=np.float64)
    z = np.column_stack([x, np.ones(len(x))])
    return z / np.sqrt(np.sum(z * z, axis=1, keepdims=True))


def design_matrix(z, kind):
    z = np.asarray(z, dtype=np.float64)
    if kind == 'linear':
        return z
    if kind != 'quadratic':
        raise ValueError('kind must be linear or quadratic')
    d = z.shape[1]
    return np.column_stack([z[:, i] * z[:, j] for i in range(d) for j in range(i, d)])


def softmax_objective(flat, z, y, regularization, n_classes):
    weights = np.asarray(flat).reshape(n_classes, z.shape[1])
    scores_ = z @ weights.T
    shifted = scores_ - scores_.max(axis=1, keepdims=True)
    e = np.exp(shifted)
    prob = e / e.sum(axis=1, keepdims=True)
    loss = np.mean(np.log(e.sum(axis=1)) - shifted[np.arange(len(y)), y]) + .5 * regularization * np.sum(weights * weights)
    diff = prob.copy()
    diff[np.arange(len(y)), y] -= 1
    gradient = diff.T @ z / len(y) + regularization * weights
    return float(loss), gradient.ravel()


def fit_softmax(z_train, y_train, n_classes, configuration=CONFIG):
    from scipy.optimize import minimize
    z = np.asarray(z_train, dtype=np.float64)
    y = np.asarray(y_train, dtype=np.int64)
    if y.shape != (len(z),) or set(np.unique(y).tolist()) != set(range(n_classes)):
        raise ValueError('all classes must be present in training')
    t = time.perf_counter()
    r = minimize(softmax_objective, np.zeros(n_classes * z.shape[1]), args=(z, y, configuration['l2'], n_classes), jac=True,
                 method='L-BFGS-B', options={'maxiter': configuration['maxiter'], 'gtol': configuration['gtol'],
                                             'ftol': configuration['ftol'], 'maxls': 50})
    gmax = float(np.max(np.abs(r.jac)))
    return {'weights': r.x.reshape(n_classes, z.shape[1]), 'objective': float(r.fun), 'iterations': int(r.nit),
            'function_evaluations': int(r.nfev), 'max_gradient_abs': gmax, 'success': bool(r.success),
            'converged': bool(r.success and gmax <= configuration['maximum_gradient_abs']),
            'fit_seconds': time.perf_counter() - t, 'nominal_parameters': n_classes * z.shape[1]}


def scores(model, z):
    return np.asarray(z) @ model['weights'].T


def probabilities(model, z):
    s = scores(model, z)
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def fit_generic(x_raw_train, y_train, n_classes, kind='linear', configuration=CONFIG):
    """Ajusta desde atributos crudos (escalado min-max con el entrenamiento); usar predict_generic para predecir."""
    lo, hi = minmax_fit(x_raw_train)
    z = design_matrix(coherent_encode(minmax_apply(x_raw_train, lo, hi)), kind)
    m = fit_softmax(z, y_train, n_classes, configuration)
    m.update({'kind': kind, 'lo': lo, 'hi': hi})
    return m


def encode_generic(model, x_raw):
    return design_matrix(coherent_encode(minmax_apply(x_raw, model['lo'], model['hi'])), model['kind'])


def predict_generic(model, x_raw):
    return np.argmax(scores(model, encode_generic(model, x_raw)), axis=1)
