"""Actual evaluated geometry and explicit coherent fields, no legacy theta/ref."""
import copy
import json
import math
from pathlib import Path

from .bootstrap import PACKAGE
from .runtime import canonical, read_json
from ._vendor.Blender.blender_lab.scene_capture_v1 import capture_scene, digest
from ._vendor.Blender.blender_lab.coherent_contract_v1 import prepare_coherent_scene


SOURCE_IDS = ('r0', 'r1', 'c0', 'c1', 'c2')


def fields_from_controls(amplitudes, phases):
    if len(amplitudes) != 5 or len(phases) != 5 or not all(math.isfinite(v) for v in [*amplitudes, *phases]) or any(v < 0 for v in amplitudes):
        raise ValueError('Cinco amplitudes finitas no negativas y cinco fases finitas requeridas')
    return {sid: [amplitude * math.cos(phase), amplitude * math.sin(phase)] for sid, amplitude, phase in zip(SOURCE_IDS, amplitudes, phases)}


def capture_current():
    network = read_json(PACKAGE / 'data/network.json')
    capture = capture_scene(network=network)
    # This UI state carries no optical geometry. The request separately pins fields.
    capture['state']['scene_custom_properties'].pop('optic_neuro_settings', None)
    capture['state_sha256'] = digest(capture['state'])
    capture['provenance']['excluded_nonoptical_scene_properties'] = ['optic_neuro_settings']
    return capture


def prepare(capture, fields):
    semantics = read_json(PACKAGE / 'data/semantics.json')
    contract = read_json(PACKAGE / 'data/contract.json')
    semantics['capture_state_sha256'] = contract['capture_state_sha256'] = capture['state_sha256']
    return prepare_coherent_scene(capture, semantics, fields, contract)


def apply_positions(parameters, positions):
    import bpy
    if len(parameters) != len(positions) or len(parameters) != 16:
        raise ValueError('Se requieren los 16 parámetros geométricos completos')
    updates = []
    seen = set()
    for parameter, position in zip(parameters, positions):
        value = float.fromhex(position)
        if not math.isfinite(value):
            raise ValueError('Coordenada no finita')
        for name, direction in parameter['objects'].items():
            obj = bpy.data.objects.get(name)
            if obj is None or obj.animation_data or name in seen or tuple(direction) != (1, 0, 0):
                raise ValueError('Sólo pares estáticos con traslación mundial X admitida')
            seen.add(name)
            updates.append((obj, value, obj.matrix_world.copy()))
    # Validate all before changing any; rollback the entire update if bpy rejects it.
    try:
        for obj, value, old in updates:
            matrix = old.copy(); matrix[0][3] = value; obj.matrix_world = matrix
        bpy.context.view_layer.update()
        if any(obj.matrix_world[0][3].hex() != value.hex() for obj, value, old in updates):
            raise ValueError('Blender no conservó las coordenadas nativas declaradas')
    except Exception:
        for obj, value, old in updates:
            obj.matrix_world = old
        bpy.context.view_layer.update()
        raise


def save_copy(path):
    import bpy
    path = Path(path).resolve()
    if path.exists() or path.suffix.lower() != '.blend':
        raise ValueError('Guardar requiere un nuevo archivo .blend')
    path.parent.mkdir(parents=True, exist_ok=True)
    previous = bpy.data.filepath
    bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True, check_existing=False)
    if bpy.data.filepath != previous:
        raise ValueError('Guardar una copia cambió el archivo activo')
