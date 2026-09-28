"""Small, deterministic CPU ray model driven by 3D scene properties.

Coordinates are Blender units. Frequency is cycles per simulated second and
``propagation_speed`` is Blender units per simulated second. This is geometric
optics with a single reflected path, not a Maxwell or renderer light solver.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

Vec3 = tuple[float, float, float]
RGB = tuple[float, float, float]
_EPS = 1e-9


def _dot(a: Vec3, b: Vec3) -> float:
    return sum(x * y for x, y in zip(a, b))


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return tuple(x - y for x, y in zip(a, b))  # type: ignore[return-value]


def _add(a: Vec3, b: Vec3) -> Vec3:
    return tuple(x + y for x, y in zip(a, b))  # type: ignore[return-value]


def _scale(a: Vec3, value: float) -> Vec3:
    return tuple(x * value for x in a)  # type: ignore[return-value]


def _unit(a: Vec3) -> Vec3:
    length = math.sqrt(_dot(a, a))
    if length <= _EPS or not math.isfinite(length):
        raise ValueError("A direction or surface normal must be finite and nonzero")
    return _scale(a, 1.0 / length)


def _rgb(values: RGB) -> RGB:
    if len(values) != 3 or not all(math.isfinite(v) and v >= 0 for v in values):
        raise ValueError("RGB channels must be finite and nonnegative")
    return values


@dataclass(frozen=True)
class Emitter:
    position: Vec3
    direction: Vec3
    intensity: float
    color: RGB
    frequency: float
    phase: float


@dataclass(frozen=True)
class Reflector:
    position: Vec3
    normal: Vec3
    radius: float
    reflectance: RGB
    phase_shift: float = 0.0


@dataclass(frozen=True)
class Receiver:
    position: Vec3
    radius: float
    responsivity: RGB = (1.0, 1.0, 1.0)
    activation_threshold: float = 0.25
    response_gain: float = 1.0


@dataclass(frozen=True)
class OpticalResult:
    hit: bool
    reason: str
    path_length: float
    intensity: float
    color_power: RGB
    frequency: float
    phase: float
    energy: float
    activation: float


def _miss(reason: str) -> OpticalResult:
    return OpticalResult(False, reason, 0.0, 0.0, (0.0, 0.0, 0.0), 0.0, 0.0, 0.0, 0.0)


def trace_single_reflection(
    emitter: Emitter,
    reflector: Reflector,
    receiver: Receiver,
    *,
    propagation_speed: float = 10.0,
    absorption_per_unit: float = 0.05,
) -> OpticalResult:
    """Trace an emitted ray to a finite disc, reflect it, and intersect a sphere.

    A hit transports RGB power. The mirror filters each channel; path length
    attenuates power and advances phase. Energy is received power in one
    simulated second. This deliberately models one path with no diffraction,
    refraction, scattering, occlusion or multi-path interference.
    """

    if not all(math.isfinite(v) for v in (*emitter.position, *reflector.position, *receiver.position)):
        raise ValueError("Positions must be finite")
    if not all(math.isfinite(v) and v >= 0 for v in (
        emitter.intensity, emitter.frequency, reflector.radius, receiver.radius,
        propagation_speed, absorption_per_unit, receiver.activation_threshold,
        receiver.response_gain,
    )) or propagation_speed <= _EPS or reflector.radius <= _EPS or receiver.radius <= _EPS:
        raise ValueError("Optical scalars must be finite and within their valid range")
    if not math.isfinite(emitter.phase) or not math.isfinite(reflector.phase_shift):
        raise ValueError("Phase values must be finite")
    source_color = _rgb(emitter.color)
    reflectance = _rgb(reflector.reflectance)
    responsivity = _rgb(receiver.responsivity)
    if any(value > 1.0 for value in (*reflectance, *responsivity)):
        raise ValueError("Reflectance and responsivity must not exceed one")

    direction = _unit(emitter.direction)
    normal = _unit(reflector.normal)
    denominator = _dot(direction, normal)
    if abs(denominator) <= _EPS:
        return _miss("ray_parallel_to_reflector")
    to_plane = _dot(_sub(reflector.position, emitter.position), normal) / denominator
    if to_plane <= _EPS:
        return _miss("reflector_behind_emitter")
    impact = _add(emitter.position, _scale(direction, to_plane))
    radial = _sub(impact, reflector.position)
    if _dot(radial, radial) > reflector.radius * reflector.radius:
        return _miss("missed_reflector_aperture")

    reflected = _unit(_sub(direction, _scale(normal, 2.0 * denominator)))
    from_center = _sub(impact, receiver.position)
    projection = _dot(reflected, from_center)
    discriminant = projection * projection - (_dot(from_center, from_center) - receiver.radius * receiver.radius)
    if discriminant < 0:
        return _miss("missed_receiver")
    root = math.sqrt(max(discriminant, 0.0))
    to_receiver = -projection - root
    if to_receiver <= _EPS:
        to_receiver = -projection + root
    if to_receiver <= _EPS:
        return _miss("receiver_behind_reflection")

    path_length = to_plane + to_receiver
    transmission = math.exp(-absorption_per_unit * path_length)
    color_total = sum(source_color)
    channels = tuple(
        emitter.intensity * (source_color[i] / color_total if color_total > _EPS else 0.0)
        * reflectance[i] * responsivity[i] * transmission
        for i in range(3)
    )
    power = sum(channels)
    activation = 1.0 - math.exp(-receiver.response_gain * max(0.0, power - receiver.activation_threshold))
    phase = math.remainder(
        emitter.phase + reflector.phase_shift
        + 2.0 * math.pi * emitter.frequency * path_length / propagation_speed,
        2.0 * math.pi,
    )
    return OpticalResult(True, "received", path_length, power, channels, emitter.frequency, phase, power, activation)
