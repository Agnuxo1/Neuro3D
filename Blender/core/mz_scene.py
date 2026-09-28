"""Bounded, CPU-only Mach-Zehnder ray/field prototype for Neuro3D.

Geometry determines whether paths reach the combiner, their lengths and their
output rays. A lossless 2-port splitter combines complex scalar fields. RGB
are independent labelled power channels sharing one simulated frequency, not
three physical wavelengths. An optional constant-width Gaussian field-overlap
factor and declared mutual coherence attenuate interference. This is a
phenomenological CPU model, not beam propagation or a Maxwell solver.
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


def _wavefront_length(length_to_hit: float, hit: Vec3, arrival_dir: Vec3, reference: Vec3) -> float:
    """Carry plane-wave phase from an arm's BS2 hit to a shared surface point.

    Tangential phase is continuous at the splitter. Comparing raw distances
    to different hit points gives a false relative phase for offset rays.
    """
    return length_to_hit + dot(arrival_dir, sub(reference, hit))


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
    beam_waist: float | None = None  # constant 1/e^2 intensity radius, BU; None is legacy ideal mode
    mutual_coherence: float = 1.0  # declared real degree of coherence, not inferred from frequency


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
    """Power ledger; path_lengths are distances to each actual BS2 hit.

    They are not the shared-wavefront lengths used internally for phase.
    interference_valid means the two rays pass the model's geometry gates;
    effective_coherence says how much interference remains inside them.
    """

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
    transverse_separation: float | None
    mode_overlap: float | None
    effective_coherence: float | None


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
    if src.beam_waist is not None and (not math.isfinite(src.beam_waist) or src.beam_waist <= 0):
        raise ValueError("Beam waist must be finite and positive when provided")
    if not math.isfinite(src.mutual_coherence) or not 0 <= src.mutual_coherence <= 1:
        raise ValueError("Mutual coherence must lie in [0, 1]")
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
    or physical loss. A hit within overlap_tolerance is treated as a shared
    ideal mode only for CPU diagnosis. If beam_waist is supplied, its constant
    Gaussian width sets a partial mode overlap inside that conservative gate.
    Physical diffraction and detector-area integrals remain untested.
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
    transverse_separation: float | None = None
    mode_overlap: float | None = None
    effective_coherence: float | None = None
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
            if fraction == 0.0:
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
            referred_length = _wavefront_length(lengths[k], hit_bs2.point,
                                                 out_dir, scene.bs2.position)
            cycles = (scene.source.frequency / scene.speed) * referred_length
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
            if interference_valid:
                separation = sub(arm_hit[0].point, arm_hit[1].point)
                # Both impacts lie on one splitter plane. Reflection changes
                # only the normal component of direction, so a tangent
                # separation has the same transverse norm in ports A and B.
                transverse_separation = math.sqrt(max(0.0, dot(separation, separation)
                                                       - dot(separation, dir_a_1) ** 2))
                if not math.isfinite(transverse_separation):
                    raise ValueError("Transverse separation is outside the finite numeric range")
                mode_overlap = (1.0 if scene.source.beam_waist is None else
                                math.exp(-0.5 * (transverse_separation / scene.source.beam_waist) ** 2))
                effective_coherence = scene.source.mutual_coherence * mode_overlap
                all_detector_modes_reach = all((
                    _sphere_hit(arm_hit[0].point, dir_a_1, scene.detector_a),
                    _sphere_hit(arm_hit[1].point, dir_a_2, scene.detector_a),
                    _sphere_hit(arm_hit[0].point, dir_b_1, scene.detector_b),
                    _sphere_hit(arm_hit[1].point, dir_b_2, scene.detector_b),
                ))
                if not all_detector_modes_reach:
                    interference_valid = False
                    transverse_separation = None
                    mode_overlap = None
                    effective_coherence = None
                    status = "unresolved_detector_overlap"
            else:
                status = "unresolved_mode_overlap"
            if not interference_valid:
                for c in range(3):
                    unresolved[c] += arm_power[0][c] + arm_power[1][c]
        if active and (len(active) == 1 or interference_valid):
            t = math.sqrt(scene.bs2.transmission)
            r = math.sqrt(1 - scene.bs2.transmission)
            for c in range(3):
                e1 = math.sqrt(arm_power[0][c]) * cmath.exp(1j * arm_phase[0]) if 0 in active else 0j
                e2 = 1j * math.sqrt(arm_power[1][c]) * cmath.exp(1j * arm_phase[1]) if 1 in active else 0j
                coherent_a = abs(t * e1 + 1j * r * e2) ** 2
                coherent_b = abs(1j * r * e1 + t * e2) ** 2
                incoherent_a = t * t * abs(e1) ** 2 + r * r * abs(e2) ** 2
                incoherent_b = r * r * abs(e1) ** 2 + t * t * abs(e2) ** 2
                g = effective_coherence if effective_coherence is not None else 0.0
                optical[0][c] = g * coherent_a + (1 - g) * incoherent_a
                optical[1][c] = g * coherent_b + (1 - g) * incoherent_b
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
                    tuple(absorbed), tuple(mirror_loss), tuple(escaped), tuple(unresolved), tuple(residual),
                    transverse_separation, mode_overlap, effective_coherence)
