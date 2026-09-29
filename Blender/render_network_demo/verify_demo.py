"""Fresh-process render readback. Expectations registered before the first run.

All power values below are independent ideal-model expectations, not inference.
No code writes material node outputs; only scene inputs are intervened upon.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import bpy
import gpu
from bpy_extras.object_utils import world_to_camera_view


EXPECTED = {
    'baseline': [(0, 1, 0), (1, 0, 1), (1, 0, 1), (0, 1, 0)],
    'phase_intervention': [(1, 0, 1), (1, 0, 1), (1, 0, 1), (0, 1, 0)],
    'visual_sham': [(0, 1, 0), (1, 0, 1), (1, 0, 1), (0, 1, 0)],
    'double_wavelength': [(0, 1, 0), (0.5, 0.5, 0), (0.5, 0.5, 0), (0, 1, 0)],
    'half_power': [(0, 0.5, 0), (0.5, 0, 0), (0.5, 0, 0), (0, 0.5, 0)],
}
TOLERANCE = 0.005  # absolute linear power; frozen before render, not display RGB


def read_detectors(scene, path):
    img = bpy.data.images.load(str(path), check_existing=False)
    width, height = img.size
    pixels = img.pixels[:]
    result = []
    for lane in range(4):
        row = []
        for port in range(3):
            obj = bpy.data.objects[f'Detector_{lane}_{port}']
            uv = world_to_camera_view(scene, scene.camera, obj.matrix_world.translation)
            x, y = int(uv.x*width), int(uv.y*height)
            # 3x3 central average, away from silhouette/anti-aliasing boundaries.
            values = [pixels[4*((y+dy)*width+x+dx)] for dy in (-1,0,1)
                      for dx in (-1,0,1)]
            row.append(sum(values)/len(values))
        result.append(row)
    bpy.data.images.remove(img)
    return result


def run(args):
    root = Path(args.evidence).resolve()
    root.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(Path(args.blend).resolve()))
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 480, 300
    scene.render.image_settings.file_format = 'OPEN_EXR'
    scene.render.image_settings.color_depth = '32'
    scene.render.image_settings.color_mode = 'RGBA'
    original_x = bpy.data.objects['Phase_A_0'].location.x
    original_y = bpy.data.objects['Phase_A_0'].location.y
    results = {}

    def render_read(name):
        scene.frame_set(scene.frame_current)
        bpy.context.view_layer.update()
        scene.render.filepath = str(root / f'{name}.exr')
        bpy.ops.render.render(write_still=True)
        return read_detectors(scene, root / f'{name}.exr')

    # Gate against a cached picture: every detector material must carry the
    # scene-bound graph, including COSINE, photodetection and activation.
    graph_check = []
    for lane in range(4):
        for port in range(3):
            mat = bpy.data.objects[f'Detector_{lane}_{port}'].active_material
            operations = {node.operation for node in mat.node_tree.nodes
                          if node.bl_idname == 'ShaderNodeMath'}
            drivers = mat.node_tree.animation_data.drivers
            targets = [driver.driver.variables[0].targets[0] for driver in drivers]
            valid = (len(drivers) == 5 and
                     {'COSINE', 'SUBTRACT', 'MULTIPLY', 'GREATER_THAN'} <= operations and
                     {t.id.name for t in targets if t.id_type == 'OBJECT'} ==
                     {f'Phase_A_{lane}', f'Phase_B_{lane}'})
            graph_check.append(valid)
    if not all(graph_check):
        raise RuntimeError('Missing live shader/scene bindings')
    for name, expected in EXPECTED.items():
        bpy.data.objects['Phase_A_0'].location.x = original_x
        bpy.data.objects['Phase_A_0'].location.y = original_y
        scene['wavelength_BU'], scene['input_power'] = 0.1, 1.0
        if name == 'phase_intervention':
            bpy.data.objects['Phase_A_0'].location.x = original_x + 0.05
        elif name == 'visual_sham':
            bpy.data.objects['Phase_A_0'].location.y = original_y + 0.15
        elif name == 'double_wavelength':
            scene['wavelength_BU'] = 0.2
        elif name == 'half_power':
            scene['input_power'] = 0.5
        start = time.monotonic()
        measured = render_read(name)
        error = max(abs(x-y) for row, ref in zip(measured, expected)
                    for x,y in zip(row, ref))
        balance = max(abs(row[0]+row[1]-scene['input_power']) for row in measured)
        results[name] = {'measured_linear_power': measured, 'expected': expected,
                         'max_abs_error': error, 'balance_error': balance,
                         'seconds': time.monotonic()-start,
                         'passed': error <= TOLERANCE and balance <= TOLERANCE}
    # Additional protocol, registered before this sweep's first measurement:
    # 17 points spanning one cycle and a common-mode X translation control.
    # Reference math is TEST-ONLY and never assigned to scene/material outputs.
    scene['wavelength_BU'], scene['input_power'] = 0.1, 1.0
    bpy.data.objects['Phase_A_0'].location.y = original_y
    sweep = []
    for step in range(17):
        offset = 0.1 * step / 16
        bpy.data.objects['Phase_A_0'].location.x = original_x + offset
        measured = render_read(f'sweep_{step:02}')[0]
        dark = 0.5*(1-math.cos(2*math.pi*step/16))
        expected = [dark, 1-dark, float(dark > 0.6)]
        error = max(abs(x-y) for x,y in zip(measured, expected))
        sweep.append({'offset_BU': offset, 'measured': measured,
                      'expected': expected, 'max_abs_error': error})
    sweep_error = max(r['max_abs_error'] for r in sweep)
    bpy.data.objects['Phase_A_0'].location.x = original_x + 0.0317
    arm_b = bpy.data.objects['Phase_B_0']
    original_b = arm_b.location.x
    arm_b.location.x = original_b + 0.0317
    gauge = render_read('common_phase_translation')[0]
    gauge_error = max(abs(x-y) for x,y in zip(gauge, [0,1,0]))
    arm_b.location.x = original_b
    # Restore scene before preview; do not overwrite the frozen saved file.
    bpy.data.objects['Phase_A_0'].location.x = original_x
    bpy.data.objects['Phase_A_0'].location.y = original_y
    scene['wavelength_BU'], scene['input_power'] = 0.1, 1.0
    scene.frame_set(scene.frame_current)
    bpy.context.view_layer.update()
    scene.render.resolution_x, scene.render.resolution_y = 1440, 900
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_depth = '8'
    scene.render.filepath = str(Path(args.preview).resolve())
    Path(args.preview).resolve().parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    report = {'blender_version': bpy.app.version_string, 'engine': scene.render.engine,
              'gpu': {'vendor': gpu.platform.vendor_get(),
                      'renderer': gpu.platform.renderer_get(),
                      'backend': gpu.platform.backend_type_get()},
              'tolerance_linear_power': TOLERANCE, 'tests': results,
              'live_shader_graphs': sum(graph_check),
              'phase_sweep': sweep, 'phase_sweep_max_error': sweep_error,
              'common_phase_translation': {'measured': gauge, 'max_abs_error': gauge_error},
              'passed': (all(r['passed'] for r in results.values()) and
                         sweep_error <= TOLERANCE and gauge_error <= TOLERANCE),
              'blend_sha256': hashlib.sha256(Path(args.blend).read_bytes()).hexdigest(),
              'scope': 'EEVEE material inference; CPU scene drivers; no physical optics'}
    (root/'verification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('NEURO3D_RESULT', json.dumps(report))
    if not report['passed']:
        raise RuntimeError('Render readback did not meet pre-registered tolerance')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--blend', required=True)
    parser.add_argument('--evidence', required=True)
    parser.add_argument('--preview', required=True)
    run(parser.parse_args(sys.argv[sys.argv.index('--')+1:]))
