"""Enforce own scalar-network units, coherence and modal readout.

No tracing, training, upstream code or physical calibration is performed here.
All input/readout arithmetic is exact rational arithmetic on represented values.
The existing prepared v1 pilot is deliberately not changed by this module.
"""
from fractions import Fraction as F

from .scene_capture_v1 import digest, need, validate_capture
from .scalar_scene_ingress_v1 import prepare_scalar_scene, represented_hex, input_real

SCHEMA = "optic_neuro_blender.coherent_contract.v1"
PHASE = {
    "time_dependence": "exp(-i*omega*t)",
    "propagation": "exp(+i*2*pi*L_BU/lambda_BU)",
    "reference": "COMMON_LAUNCH_PHASE",
    "mirror": "minus_one_times_exp_i_declared_phase",
    "splitter": "sqrt_tau_and_i_sqrt_one_minus_tau",
}


def _closed(value, keys, message):
    need(isinstance(value, dict) and set(value) == set(keys), message)


def validate_contract(capture, semantics, contract):
    """Validate semantic compatibility; this is not a transport certificate."""
    validate_capture(capture)
    _closed(contract, ("schema", "capture_state_sha256", "units", "phase", "encoding", "parameters", "detectors"),
            "closed coherent contract required")
    need(contract["schema"] == SCHEMA, "unsupported coherent contract")
    need(contract["capture_state_sha256"] == capture["state_sha256"] == semantics.get("capture_state_sha256"),
         "contract/semantics/capture identity mismatch")
    need(semantics.get("model") == "LOSSLESS_SCALAR_PLANAR_V1", "only declared ideal scalar n=1 transport supported")
    need(contract["phase"] == PHASE, "phase gauge, sign or component convention mismatch")
    units = contract["units"]
    _closed(units, ("geometry", "wavelength_BU_hex", "metres_per_BU_hex", "scale_status", "reference_power_watt_hex"),
            "closed units contract required")
    need(units["geometry"] == "BU", "geometry must use Blender units")
    wavelength = represented_hex(units["wavelength_BU_hex"])
    scale = represented_hex(units["metres_per_BU_hex"])
    need(wavelength > 0 and scale > 0, "positive wavelength and length scale required")
    need(wavelength == represented_hex(semantics["wavelength_BU_hex"]), "wavelength convention mismatch")
    captured_units = capture["state"].get("units")
    need(isinstance(captured_units, dict), "captured scene units required")
    need(scale == represented_hex(captured_units["scale_length_metres_per_BU_hex"]), "captured unit scale mismatch")
    need(units["scale_status"] in ("SCENE_DISPLAY_SCALE_ONLY", "DECLARED_SI_SCALE_UNVALIDATED"),
         "scale must not imply measured calibration")
    power = units["reference_power_watt_hex"]
    if power is not None:
        need(units["scale_status"] == "DECLARED_SI_SCALE_UNVALIDATED", "watts require explicit declared SI convention")
        need(represented_hex(power) > 0, "positive declared reference power required")
    network = capture["state"].get("network")
    need(isinstance(network, dict), "resolved own network bindings required")
    inputs = network["inputs"]
    source_map = {row["id"]: row["object"] for row in semantics["sources"]}
    need(len(source_map) == len(semantics["sources"]), "duplicate scalar source ID")
    need(source_map == {row["id"]: row["object"] for row in inputs}, "neural/scalar input bindings mismatch")
    encoding = contract["encoding"]
    _closed(encoding, ("kind", "normalization", "ports"), "closed input encoding required")
    need(encoding["kind"] == "EXPLICIT_COMPLEX_FIELDS" and encoding["normalization"] == "NONE",
         "explicit common-reference fields without implicit renormalization required")
    ports = encoding["ports"]
    need(isinstance(ports, dict) and set(ports) == set(source_map), "input port IDs mismatch")
    groups, references = set(), set()
    for port in ports.values():
        _closed(port, ("coherence_group", "phase_reference"), "explicit port coherence required")
        for key in ("coherence_group", "phase_reference"):
            need(isinstance(port[key], str) and 0 < len(port[key]) <= 128, "bounded nonempty coherence identifier required")
        groups.add(port["coherence_group"])
        references.add(port["phase_reference"])
    need(len(groups) == len(references) == 1, "own scalar network requires mutually coherent ports in one launch gauge")
    parameters = contract["parameters"]
    bindings = network["parameters"]
    need(isinstance(parameters, dict) and set(parameters) == {row["id"] for row in bindings},
         "every represented parameter binding requires explicit units")
    for binding in bindings:
        row = parameters[binding["id"]]
        _closed(row, ("unit", "role"), "closed parameter semantics required")
        need(row["unit"] == binding["unit"] == "BU" and row["role"] == "GEOMETRY_COORDINATE",
             "initial parameter contract admits geometry coordinates in BU only")
        need(binding["object"] in semantics["objects"], "parameter must bind admitted geometry")
        # A coordinate address does not assert an independent physical degree of freedom.
        need(binding["path"][0] in ("matrix_world", "location"), "supported geometric coordinate path required")
    detectors = contract["detectors"]
    detector_bindings = network["detectors"]
    need(isinstance(detectors, dict) and set(detectors) == {row["id"] for row in detector_bindings},
         "detector IDs mismatch")
    for binding in detector_bindings:
        row = detectors[binding["id"]]
        _closed(row, ("object", "measurement", "field_frame", "renormalize"), "closed detector semantics required")
        definition = semantics["objects"].get(binding["object"])
        need(row["object"] == binding["object"] and isinstance(definition, dict) and definition.get("kind") == "det",
             "detector must bind admitted scalar mode terminal")
        need(row["measurement"] == "NORMALIZED_MODAL_POWER" and row["field_frame"] == "COMMON_LAUNCH_PHASE",
             "only common-reference scalar modal readout is supported")
        need(row["renormalize"] is False, "detector power must not be silently renormalized")
        need("mode_origin_local_hex" in definition and "mode_direction_world_hex" in definition,
             "explicit terminal mode required")
    return {
        "schema": "optic_neuro_blender.semantic_admission.v1",
        "contract_sha256": digest(contract), "capture_state_sha256": capture["state_sha256"],
        "source_count": len(inputs), "parameter_binding_count": len(bindings), "detector_count": len(detector_bindings),
        "common_coherence_group": next(iter(groups)), "phase_reference": next(iter(references)),
        "wavelength_BU": wavelength, "metres_per_BU": scale,
        "declared_wavelength_metres": wavelength * scale,
        "scale_status": units["scale_status"], "reference_power_watt": represented_hex(power) if power is not None else None,
        "units_and_coherence_admitted": True, "optical_forward_executed": False,
        "training_executed": False, "field_certified": False, "physical_calibration_verified": False,
        "physical_optics_certified": False,
    }


def prepare_coherent_scene(capture, semantics, amplitudes, contract, **bounds):
    """Strict opt-in wrapper. Frozen scalar v1 sources and protocol stay intact."""
    admission = validate_contract(capture, semantics, contract)
    packet = prepare_scalar_scene(capture, semantics, amplitudes, **bounds)
    packet["blender_lab_optical_contract"] = admission
    return packet


def modal_power(contributions, *, expected_source_ids, reference_power_watt=None):
    """Read already projected fields in one common mode/gauge, not raw rays.

    Each expected source must be present, including an explicitly proved zero.
    The caller must establish path completeness, mode projection and transport
    separately. This helper returns an algebraic value, never a certificate.
    """
    need(isinstance(expected_source_ids, (list, tuple)) and len(expected_source_ids) > 0,
         "explicit expected source IDs required")
    need(all(isinstance(sid, str) and sid for sid in expected_source_ids) and
         len(set(expected_source_ids)) == len(expected_source_ids), "unique expected source IDs required")
    need(isinstance(contributions, dict) and set(contributions) == set(expected_source_ids),
         "missing or unknown source contributions")
    real = imag = F(0)
    for field in contributions.values():
        need(isinstance(field, (list, tuple)) and len(field) == 2, "explicit complex mode projection required")
        real += input_real(field[0])
        imag += input_real(field[1])
    normalized = real * real + imag * imag
    if reference_power_watt is not None:
        reference_power_watt = input_real(reference_power_watt)
        need(reference_power_watt > 0, "positive declared reference power required")
    return {"field_reim": (real, imag), "normalized_modal_power": normalized,
            "declared_power_watt": normalized * reference_power_watt if reference_power_watt is not None else None,
            "field_certified": False, "physical_calibration_verified": False}


def phase_cycles(optical_length_BU, wavelength_BU):
    """Exact phase in cycles, before any sin/cos approximation; n=1 model."""
    length, wavelength = input_real(optical_length_BU), input_real(wavelength_BU)
    need(length >= 0 and wavelength > 0, "nonnegative optical length and positive wavelength required")
    return length / wavelength
