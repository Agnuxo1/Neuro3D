"""Own manual CE chain rule and Adam arithmetic; torch autograd is not used."""
import math


def cross_entropy(powers, power_jacobian, labels, columns, temperature):
    import torch
    if not math.isfinite(temperature) or temperature <= 0 or len(set(columns)) != len(columns):
        raise ValueError('Distinct detectors and positive finite temperature required')
    if powers.dtype != torch.float64 or power_jacobian.dtype != torch.float64 or powers.ndim != 2 or power_jacobian.ndim != 3:
        raise ValueError('Complete float64 powers and own Jacobian required')
    if power_jacobian.shape[:2] != powers.shape or labels.dtype != torch.int64 or labels.shape != (len(powers),):
        raise ValueError('Aligned training rows required')
    if powers.device != power_jacobian.device or powers.device != labels.device:
        raise ValueError('Loss, Jacobian and labels must use the same device')
    if not torch.isfinite(powers).all().item() or not torch.isfinite(power_jacobian).all().item() or not ((labels >= 0) & (labels < len(columns))).all().item():
        raise ValueError('Finite output and valid training labels required')
    scores = powers[:, columns] / temperature
    shifted = scores - scores.max(dim=1, keepdim=True).values
    exponents = shifted.exp(); probability = exponents / exponents.sum(dim=1, keepdim=True)
    rows = torch.arange(len(scores), device=powers.device)
    loss = (exponents.sum(dim=1).log() - shifted[rows, labels]).mean()
    weights = probability.clone(); weights[rows, labels] -= 1
    gradient = torch.einsum('nc,ncp->p', weights / (len(scores) * temperature), power_jacobian[:, columns, :])
    return loss, gradient


def adam_proposal(delta, gradient, first, second, center, step, learning_rate, bound):
    first = .9 * first + .1 * gradient
    second = .999 * second + .001 * gradient.square()
    update = learning_rate * (first / (1 - .9**step)) / ((second / (1 - .999**step)).sqrt() + 1e-8)
    return center + (delta - update - center).clamp(-bound, bound), first, second
