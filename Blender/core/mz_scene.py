"""Bounded, CPU-only Mach-Zehnder ray/field prototype for Neuro3D.

Geometry determines whether paths reach the combiner, their lengths and their
output rays. A lossless 2-port splitter combines complex scalar fields. RGB
are independent labelled power channels sharing one simulated frequency, not
three physical wavelengths. This is not a Maxwell or Blender render solver.
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
import math

Vec3 = tuple[float, float, float]
RGB = tuple[float, float, float]
EPS = 1e-9


def dot(a: Vec3, b: Vec3) -> float:
    return sum(x * y for x, y in zip(a, b))


def add(a: Vec3, b: Vec3) -> Vec3:
    return tuple(x + y for x, y in zip(a, b))  # type: ignore[return-value]


def sub(a: Vec3, b: Vec3) -> Vec3:
    return tuple(x - y for x, y in zip(a, b))  # type: ignore[return-value]


def scale(a: Vec3, k: float) -> Vec3:
    return tuple(x * k for x in a)  # type: ignore[return-value]


def unit(a: Vec3) -> Vec3:
    length = math.sqrt(dot(a, a))
    if length <= EPS or not math.isfinite(length):
        raise ValueError("Direction and normal must be finite and nonzero")
    return scale(a, 1.0 / length)


def distance(a: Vec3, b: Vec3) -> float:
    return math.sqrt(dot(sub(a, b), sub(a, b)))


def reflected(direction: Vec3, normal: Vec3) -> Vec3:
    n = unit(normal)
    return unit(sub(direction, scale(n, 2.0 * dot(direction, n))))


@dataclass(frozen=True)
class Source:
    position: Vec3
    direction: Vec3
    power: float = 1.0
    rgb: RGB = (1.0, 1.0, 1.0)
    frequency: float = 10.0
    phase: float = 0.0


@dataclass(frozen=True)
class Splitter:
    position: Vec3
    normal: Vec3
    radius: float = 0.4
    transmission: float = 0.5


@dataclass(frozen=True)
class Mirror:
    position: Vec3
    normal: Vec3
    radius: float = 0.4
    reflectance: RGB = (1.0, 1.0, 1.0)
    phase_shift: float = 0.0


@dataclass(frozen=True)
class Detector:
    position: Vec3
    radius: float = 0.2
    responsivity: RGB = (1.0, 1.0, 1.0)
    threshold: float = 0.25
    gain: float = 1.0


@dataclass(frozen=True)
class MZScene:
    source: Source
    bs1: Splitter
    mirror1: Mirror
    mirror2: Mirror
    bs2: Splitter
    detector_a: Detector
    detector_b: Detector
    speed: float = 10.0
    absorption: float = 0.0
    overlap_tolerance: float = 0.02
    direction_tolerance: float = 1e-6


@dataclass(frozen=True)
class MZResult:
    status: str
    interference_valid: bool
    path_lengths: tuple[float | None, float | None]
    optical_a: RGB
    optical_b: RGB
    signal_a: float
    signal_b: float
    activation_a: float
    activation_b: float
    input_rgb: RGB
    absorption_rgb: RGB
    mirror_loss_rgb: RGB
    escape_rgb: RGB
    unresolved_rgb: RGB
    residual_rgb: RGB


@dataclass(frozen=True)
class _DiscHit:
    point: Vec3
    length: float
    within: bool


def _disc_hit(origin: Vec3, direction: Vec3, position: Vec3, normal: Vec3, radius: float) -> _DiscHit | None:
    n = unit(normal)
    denominator = dot(direction, n)
    if abs(denominator) <= EPS:
        return None
    length = dot(sub(position, origin), n) / denominator
    if length <= EPS:
        return None
    point = add(origin, scale(direction, length))
    return _DiscHit(point, length, distance(point, position) <= radius + EPS)


def _sphere_hit(origin: Vec3, direction: Vec3, detector: Detector) -> bool:
    offset = sub(origin, detector.position)
    projection = dot(direction, offset)
    discriminant = projection * projection - (dot(offset, offset) - detector.radius ** 2)
    if discriminant < 0:
        return False
    root = math.sqrt(max(0.0, discriminant))
    return -projection + root > EPS


def _validate(scene: MZScene) -> RGB:
    src = scene.source
    if any(len(values) != 3 for values in
           (src.rgb, scene.mirror1.reflectance, scene.mirror2.reflectance,
            scene.detector_a.responsivity, scene.detector_b.responsivity)):
        raise ValueError("RGB parameters must have exactly three channels")
    scalars = (src.power, src.frequency, scene.speed, scene.absorption,
               scene.overlap_tolerance, scene.direction_tolerance,
               scene.bs1.radius, scene.bs2.radius, scene.mirror1.radius,
               scene.mirror2.radius, scene.detector_a.radius, scene.detector_b.radius,
               scene.detector_a.threshold, scene.detector_b.threshold,
               scene.detector_a.gain, scene.detector_b.gain)
    if not all(math.isfinite(x) and x >= 0 for x in scalars):
        raise ValueError("Scene scalars must be finite and nonnegative")
    if min(scene.speed, scene.bs1.radius, scene.bs2.radius,
           scene.mirror1.radius, scene.mirror2.radius,
           scene.detector_a.radius, scene.detector_b.radius) <= EPS:
        raise ValueError("Speed and apertures must be positive")
    if not all(math.isfinite(x) and 0 <= x <= 1 for x in
               (scene.bs1.transmission, scene.bs2.transmission,
                *scene.mirror1.reflectance, *scene.mirror2.reflectance,
                *scene.detector_a.responsivity, *scene.detector_b.responsivity)):
        raise ValueError("Transmissions, reflectances and responsivities must lie in [0, 1]")
    if not all(math.isfinite(x) and x >= 0 for x in src.rgb):
        raise ValueError("RGB weights must be finite and nonnegative")
    if not all(math.isfinite(x) for x in
               (src.phase, scene.mirror1.phase_shift, scene.mirror2.phase_shift)):
        raise ValueError("Phases must be finite")
    for obj in (src, scene.bs1, scene.mirror1, scene.mirror2, scene.bs2,
                scene.detector_a, scene.detector_b):
        if not all(math.isfinite(x) for x in obj.position):
            raise ValueError("Positions must be finite")
    weights = sum(src.rgb)
    if not math.isfinite(weights):
        raise ValueError("RGB weight sum must be finite")
    return tuple(src.power * (x / weights) if weights > EPS else 0.0 for x in src.rgb)  # type: ignore[return-value]


def default_scene() -> MZScene:
    """Square MZ with explicit 3D objects and two detector output ports."""

    n = (1.0, -1.0, 0.0)
    return MZScene(
        Source((-1.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
        Splitter((0.0, 0.0, 0.0), n),
        Mirror((2.0, 0.0, 0.0), n),
        Mirror((0.0, 2.0, 0.0), n),
        Splitter((2.0, 2.0, 0.0), n),
        Detector((2.0, 3.0, 0.0)),
        Detector((3.0, 2.0, 0.0)),
    )


def trace_mz(scene: MZScene) -> MZResult:
    """Trace two scene-defined arms, combine only overlapping output modes.

    Non-overlapping arrivals are *unresolved*, not a demonstrated interference
    or physical loss. They remain in the power ledger and block promotion.
    """

    source_power = _validate(scene)
    absorbed = [0.0] * 3
    mirror_loss = [0.0] * 3
    escaped = [0.0] * 3
    unresolved = [0.0] * 3
    optical = [[0.0] * 3, [0.0] * 3]
    source_dir = unit(scene.source.direction)
    first = _disc_hit(scene.source.position, source_dir, scene.bs1.position,
                      scene.bs1.normal, scene.bs1.radius)
    lengths: list[float | None] = [None, None]
    status = "ok"
    interference_valid = False
    if first is None or not first.within:
        escaped[:] = source_power
        status = "missed_bs1"
    else:
        after_first = [p * math.exp(-scene.absorption * first.length) for p in source_power]
        for c in range(3):
            absorbed[c] += source_power[c] - after_first[c]
        arm_starts = [(source_dir, scene.bs1.transmission, scene.mirror1),
                      (reflected(source_dir, scene.bs1.normal), 1 - scene.bs1.transmission, scene.mirror2)]
        arm_power: list[list[float]] = [[0.0] * 3, [0.0] * 3]
        arm_hit: list[_DiscHit | None] = [None, None]
        arm_direction: list[Vec3 | None] = [None, None]
        arm_phase = [0.0, 0.0]
        for k, (direction, fraction, mirror) in enumerate(arm_starts):
            current = [p * fraction for p in after_first]
            if fraction <= EPS:
                continue
            hit_mirror = _disc_hit(first.point, direction, mirror.position, mirror.normal, mirror.radius)
            if hit_mirror is None or not hit_mirror.within:
                for c in range(3):
                    escaped[c] += current[c]
                status = "missed_mirror"
                continue
            attenuation = math.exp(-scene.absorption * hit_mirror.length)
            for c in range(3):
                reduced = current[c] * attenuation
                absorbed[c] += current[c] - reduced
                mirror_loss[c] += reduced * (1 - mirror.reflectance[c])
                current[c] = reduced * mirror.reflectance[c]
            out_dir = reflected(direction, mirror.normal)
            hit_bs2 = _disc_hit(hit_mirror.point, out_dir, scene.bs2.position,
                                scene.bs2.normal, scene.bs2.radius)
            if hit_bs2 is None:
                for c in range(3):
                    escaped[c] += current[c]
                status = "missed_bs2"
                continue
            attenuation = math.exp(-scene.absorption * hit_bs2.length)
            for c in range(3):
                reduced = current[c] * attenuation
                absorbed[c] += current[c] - reduced
                current[c] = reduced
                if not hit_bs2.within:
                    escaped[c] += current[c]
            if not hit_bs2.within:
                status = "missed_bs2_aperture"
                continue
            arm_power[k] = current
            arm_hit[k] = hit_bs2
            arm_direction[k] = out_dir
            lengths[k] = first.length + hit_mirror.length + hit_bs2.length
            cycles = (scene.source.frequency / scene.speed) * lengths[k]
            if not math.isfinite(cycles):
                raise ValueError("Propagation phase is outside the finite numeric range")
            arm_phase[k] = (math.remainder(scene.source.phase, 2 * math.pi)
                            + math.remainder(mirror.phase_shift, 2 * math.pi)
                            + 2 * math.pi * math.remainder(cycles, 1.0))

        active = [k for k in range(2) if arm_hit[k] is not None]
        if len(active) == 2:
            dir_a_1 = arm_direction[0]
            dir_a_2 = reflected(arm_direction[1], scene.bs2.normal)  # type: ignore[arg-type]
            dir_b_1 = reflected(arm_direction[0], scene.bs2.normal)  # type: ignore[arg-type]
            dir_b_2 = arm_direction[1]
            interference_valid = (
                distance(arm_hit[0].point, arm_hit[1].point) <= scene.overlap_tolerance
                and distance(dir_a_1, dir_a_2) <= scene.direction_tolerance  # type: ignore[arg-type]
                and distance(dir_b_1, dir_b_2) <= scene.direction_tolerance
            )
            if not interference_valid:
                for c in range(3):
                    unresolved[c] += arm_power[0][c] + arm_power[1][c]
                status = "unresolved_mode_overlap"
        if active and (len(active) == 1 or interference_valid):
            t = math.sqrt(scene.bs2.transmission)
            r = math.sqrt(1 - scene.bs2.transmission)
            for c in range(3):
                e1 = math.sqrt(arm_power[0][c]) * cmath.exp(1j * arm_phase[0]) if 0 in active else 0j
                e2 = 1j * math.sqrt(arm_power[1][c]) * cmath.exp(1j * arm_phase[1]) if 1 in active else 0j
                optical[0][c] = abs(t * e1 + 1j * r * e2) ** 2
                optical[1][c] = abs(1j * r * e1 + t * e2) ** 2
            chosen = active[0]
            origin = arm_hit[chosen].point
            direction_a = arm_direction[0] if chosen == 0 else reflected(arm_direction[1], scene.bs2.normal)
            direction_b = reflected(arm_direction[0], scene.bs2.normal) if chosen == 0 else arm_direction[1]
            for port, detector, direction in ((0, scene.detector_a, direction_a),
                                               (1, scene.detector_b, direction_b)):
                if not _sphere_hit(origin, direction, detector):  # type: ignore[arg-type]
                    for c in range(3):
                        escaped[c] += optical[port][c]
                        optical[port][c] = 0.0
                    status = "missed_detector"
        elif not active and status == "ok":
            status = "no_arm_reached_combiner"

    signal_a = sum(optical[0][c] * scene.detector_a.responsivity[c] for c in range(3))
    signal_b = sum(optical[1][c] * scene.detector_b.responsivity[c] for c in range(3))
    activation_a = 1 - math.exp(-scene.detector_a.gain * max(0.0, signal_a - scene.detector_a.threshold))
    activation_b = 1 - math.exp(-scene.detector_b.gain * max(0.0, signal_b - scene.detector_b.threshold))
    residual = [source_power[c] - optical[0][c] - optical[1][c] - absorbed[c]
                - mirror_loss[c] - escaped[c] - unresolved[c] for c in range(3)]
    if not all(math.isfinite(x) for values in
               (optical[0], optical[1], absorbed, mirror_loss, escaped, unresolved, residual)
               for x in values):
        raise ValueError("Optical result exceeds the finite numeric range")
    return MZResult(status, interference_valid, tuple(lengths), tuple(optical[0]), tuple(optical[1]),
                    signal_a, signal_b, activation_a, activation_b, source_power,
                    tuple(absorbed), tuple(mirror_loss), tuple(escaped), tuple(unresolved), tuple(residual))
