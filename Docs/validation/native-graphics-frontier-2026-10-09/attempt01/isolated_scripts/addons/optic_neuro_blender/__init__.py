"""OpticNeuroBlender: own coherent captured geometry, isolated from legacy demo."""
import atexit
import hashlib
import json
from pathlib import Path
import uuid

import bpy
from bpy.props import FloatVectorProperty, PointerProperty, StringProperty

from .bootstrap import PACKAGE, verify_bundle
from .runtime import OwnedJob, canonical, digest, read_json

bl_info = {'name': 'OpticNeuroBlender', 'author': 'Neuro3D contributors', 'version': (0, 1, 2),
           'blender': (4, 5, 0), 'location': 'View3D > Sidebar > OpticNeuro',
           'description': 'Red óptica coherente propia desde geometría evaluada', 'category': '3D View'}

_job = None
_last_folder = None
_status = 'Listo. Modelo escalar en BU; escala física sin calibrar.'
_registered = False


def _cleanup_owned_job():
    if _job is not None and _job.state == 'RUNNING':
        _job.cancel('BLENDER_EXIT')


atexit.register(_cleanup_owned_job)


class ONB_Settings(bpy.types.PropertyGroup):
    amplitudes: FloatVectorProperty(name='Amplitudes r0, r1, c0, c1, c2', size=5, min=0, default=(0, 0, 0, 0, 1))
    phases: FloatVectorProperty(name='Fases [rad], referencia común', size=5, default=(0, 0, 0, 0, 0))
    work_directory: StringProperty(name='Carpeta de evidencia', subtype='DIR_PATH')
    recover_directory: StringProperty(name='Trabajo que recuperar', subtype='DIR_PATH')
    save_path: StringProperty(name='Nueva copia .blend', subtype='FILE_PATH')


def controls(scene):
    from .model import fields_from_controls
    settings = scene.optic_neuro_settings
    return fields_from_controls(list(settings.amplitudes), list(settings.phases))


def _current_identity():
    from .model import capture_current
    return capture_current()['state_sha256'], digest(controls(bpy.context.scene))


def validate_recovery(folder):
    folder = Path(folder).resolve()
    request = read_json(folder / 'request.json', 2**20)
    result = read_json(folder / 'result.json')
    supervision = read_json(folder / 'supervision.json', 2**20)
    if supervision.get('state') != 'COMPLETED' or supervision.get('result_sha256') != hashlib.sha256((folder / 'result.json').read_bytes()).hexdigest():
        raise ValueError('El resultado no coincide con el recibo de supervisión')
    if result.get('schema') != 'optic_neuro_blender.job_result.v1' or result.get('status') != 'PASS':
        raise ValueError('El trabajo no tiene un resultado completo válido')
    if hashlib.sha256((folder / 'request.json').read_bytes()).hexdigest() != result['request_sha256']:
        raise ValueError('Petición modificada después de ejecutar')
    if request['package_manifest_sha256'] != hashlib.sha256((PACKAGE / 'package_manifest.json').read_bytes()).hexdigest():
        raise ValueError('El trabajo corresponde a otra versión del complemento')
    current, field_hash = _current_identity()
    if current != request['capture_state_sha256'] or field_hash != digest(request['fields']):
        raise ValueError('Resultado obsoleto: cambió la escena o cambiaron las entradas')
    return request, result


def start_job(action):
    global _job, _last_folder, _status
    if _job is not None and _job.state == 'RUNNING':
        raise ValueError('Ya hay un trabajo propio activo')
    verify_bundle()
    from .model import capture_current, save_copy, prepare
    scene = bpy.context.scene
    root = Path(bpy.path.abspath(scene.optic_neuro_settings.work_directory)).resolve()
    if not scene.optic_neuro_settings.work_directory or not root.is_dir():
        raise ValueError('Selecciona una carpeta existente para conservar la evidencia')
    fields = controls(scene); capture = capture_current()
    prepare(capture, fields)  # Reject unsupported scenes before creating a process.
    folder = root / ('optic-neuro-' + uuid.uuid4().hex)
    folder.mkdir(exist_ok=False)
    request = {'schema': 'optic_neuro_blender.job_request.v1', 'action': action,
               'capture_state_sha256': capture['state_sha256'], 'fields': fields,
               'coherence': 'COMMON_LAUNCH_PHASE', 'normalization': 'NONE',
               'training_policy': 'FROZEN_IRIS_120_30_60_STEPS_FROM_DECLARED_UNTRAINED_ABSOLUTE_GEOMETRY',
               'package_manifest_sha256': hashlib.sha256((PACKAGE / 'package_manifest.json').read_bytes()).hexdigest()}
    (folder / 'request.json').write_bytes(canonical(request))
    (folder / 'capture.json').write_bytes(canonical(capture))
    save_copy(folder / 'snapshot.blend')
    command = [bpy.app.binary_path, '--background', '--disable-autoexec', '--threads', '1', '-noaudio',
               str(folder / 'snapshot.blend'), '--python-exit-code', '3', '--python', str(PACKAGE / 'worker_v2.py'), '--', str(folder / 'request.json')]
    _job = OwnedJob(command, folder)
    _last_folder = folder; scene.optic_neuro_settings.recover_directory = str(folder)
    _status = 'Entrenando desde geometría…' if action == 'TRAIN' else 'Recorriendo la escena y calculando campos…'
    if not bpy.app.timers.is_registered(poll_job):
        bpy.app.timers.register(poll_job, first_interval=0.5)
    return folder


def poll_job():
    global _status
    if _job is None:
        return None
    state = _job.poll()
    if state == 'RUNNING':
        for area in bpy.context.screen.areas if bpy.context.screen else ():
            area.tag_redraw()
        return 0.5
    if state == 'COMPLETED':
        try:
            request, result = validate_recovery(_job.folder)
            decision = result['decision'] or 'indeterminada'
            _status = 'Completo. Decisión: ' + decision + '. Potencia de entrada: ' + format(result['input_total_normalized_power'], '.6g')
            if request['action'] == 'TRAIN':
                _status += '. Geometría lista para aplicar.'
        except Exception as exc:
            _status = str(exc)
    else:
        _status = state + ': ' + str(_job.reason) + '. Evidencia conservada.'
    return None


class ONB_OT_LoadExample(bpy.types.Operator):
    bl_idname = 'optic_neuro.load_example'; bl_label = 'Abrir ejemplo entrenado propio'
    def execute(self, context):
        global _status
        try:
            if _job is not None and _job.state == 'RUNNING':
                raise ValueError('Cancela el trabajo antes de abrir otra escena')
            verify_bundle()
            bpy.ops.wm.open_mainfile(filepath=str(PACKAGE / 'data/trained_geometry.blend'), use_scripts=False)
            _status = 'Ejemplo propio cargado. Define la carpeta y las entradas coherentes.'
            return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'}, str(exc)); return {'CANCELLED'}


class ONB_OT_Infer(bpy.types.Operator):
    bl_idname = 'optic_neuro.infer'; bl_label = 'Inferir desde la escena'
    def execute(self, context):
        try:
            start_job('INFER'); return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'}, str(exc)); return {'CANCELLED'}


class ONB_OT_Train(bpy.types.Operator):
    bl_idname = 'optic_neuro.train'; bl_label = 'Entrenar geometría propia con Iris'
    def execute(self, context):
        try:
            start_job('TRAIN'); return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'}, str(exc)); return {'CANCELLED'}


class ONB_OT_Cancel(bpy.types.Operator):
    bl_idname = 'optic_neuro.cancel'; bl_label = 'Cancelar trabajo propio'
    def execute(self, context):
        global _status
        if _job is not None:
            _status = _job.cancel() + '. Evidencia conservada.'
        return {'FINISHED'}


class ONB_OT_Apply(bpy.types.Operator):
    bl_idname = 'optic_neuro.apply'; bl_label = 'Aplicar entrenamiento / recuperar'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        global _status
        try:
            verify_bundle()
            folder = Path(bpy.path.abspath(context.scene.optic_neuro_settings.recover_directory))
            request, result = validate_recovery(folder)
            if request['action'] != 'TRAIN' or result['training'] is None:
                raise ValueError('Este trabajo no contiene entrenamiento')
            from .model import apply_positions, capture_current
            parameters = result['training']['parameters']; positions = result['training']['final_native_world_x_hex']
            old = [float(bpy.data.objects[next(iter(parameter['objects']))].matrix_world[0][3]).hex() for parameter in parameters]
            try:
                apply_positions(parameters, positions)
                if capture_current()['state_sha256'] != result['final_capture_state_sha256']:
                    raise ValueError('Aplicación nativa no reproduce la captura final')
            except Exception:
                apply_positions(parameters, old); raise
            _status = 'Entrenamiento aplicado. Guarda una nueva copia para conservarlo.'
            return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'}, str(exc)); return {'CANCELLED'}


class ONB_OT_Save(bpy.types.Operator):
    bl_idname = 'optic_neuro.save_copy'; bl_label = 'Guardar nueva copia'
    def execute(self, context):
        try:
            from .model import save_copy
            path = context.scene.optic_neuro_settings.save_path
            if not path:
                raise ValueError('Indica un nuevo archivo .blend')
            save_copy(bpy.path.abspath(path)); return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'}, str(exc)); return {'CANCELLED'}


class ONB_PT_Main(bpy.types.Panel):
    bl_label = 'OpticNeuroBlender'; bl_idname = 'ONB_PT_main'; bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'; bl_category = 'OpticNeuro'
    def draw(self, context):
        layout = self.layout; settings = context.scene.optic_neuro_settings
        layout.operator('optic_neuro.load_example')
        layout.label(text='Campo escalar coherente · λ = 0,1 BU')
        layout.label(text='Referencia común; potencia modal normalizada')
        layout.prop(settings, 'amplitudes'); layout.prop(settings, 'phases')
        layout.prop(settings, 'work_directory')
        row = layout.row(); row.enabled = _job is None or _job.state != 'RUNNING'
        row.operator('optic_neuro.infer'); row.operator('optic_neuro.train')
        layout.operator('optic_neuro.cancel')
        layout.label(text=_status)
        if _last_folder and (_last_folder / 'result.json').exists():
            try:
                result = read_json(_last_folder / 'result.json')
                box = layout.box()
                for port in result['detectors']:
                    box.label(text=port + ': ' + format(result['powers'][port], '.8g'))
            except Exception:
                layout.label(text='No se pudo leer la evidencia del trabajo')
        layout.label(text='Iris: 120/30, 60 pasos, auditoría por estado')
        layout.prop(settings, 'recover_directory'); layout.operator('optic_neuro.apply')
        layout.prop(settings, 'save_path'); layout.operator('optic_neuro.save_copy')
        layout.label(text='Escala física sin calibrar; ensayo exploratorio')


CLASSES = (ONB_Settings, ONB_OT_LoadExample, ONB_OT_Infer, ONB_OT_Train, ONB_OT_Cancel, ONB_OT_Apply, ONB_OT_Save, ONB_PT_Main)


def register():
    global _registered
    verify_bundle()
    if _registered:
        return
    created = []
    try:
        for cls in CLASSES:
            bpy.utils.register_class(cls)
            created.append(cls)
        bpy.types.Scene.optic_neuro_settings = PointerProperty(type=ONB_Settings)
        _registered = True
    except Exception:
        for cls in reversed(created):
            bpy.utils.unregister_class(cls)
        raise


def unregister():
    global _registered
    if _job is not None and _job.state == 'RUNNING':
        _job.cancel('ADDON_UNREGISTERED')
    if bpy.app.timers.is_registered(poll_job):
        bpy.app.timers.unregister(poll_job)
    if not _registered:
        return
    if hasattr(bpy.types.Scene, 'optic_neuro_settings'):
        del bpy.types.Scene.optic_neuro_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    _registered = False
