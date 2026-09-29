"""Build a self-contained EEVEE coherent-neuron demonstration.

No Python field propagation runs at inference time. Scene drivers supply uniforms;
Blender material nodes compute interference, photodetection and activation.
This is an idealized digital shader model, NOT geometric ray/wave transport.
"""
import argparse
from pathlib import Path
import sys

import bpy


LANES = ((0, 0), (0, 1), (1, 0), (1, 1))
YS = (2.7, 0.9, -0.9, -2.7)
DETECTORS = (3.0, 4.35, 5.75)


def emission(name, color, strength=1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    light = nodes.new('ShaderNodeEmission')
    light.inputs['Color'].default_value = (*color, 1)
    light.inputs['Strength'].default_value = strength
    mat.node_tree.links.new(light.outputs[0], out.inputs['Surface'])
    return mat


def box(name, x, y, sx, sy, material, z=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (sx, sy, 0.04)
    obj.data.materials.append(material)
    return obj


def disk(name, x, y, radius, material, z=0.25):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius,
                                      depth=0.04, location=(x, y, z))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def text(label, x, y, size, material, align='LEFT'):
    curve = bpy.data.curves.new('Typography', 'FONT')
    curve.body = label
    curve.size = size
    curve.align_x = align
    obj = bpy.data.objects.new(label, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, 0.5)
    obj.data.materials.append(material)
    return obj


def line(name, points, material, width=0.025):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = width
    curve.bevel_resolution = 3
    poly = curve.splines.new('POLY')
    poly.points.add(len(points)-1)
    for p, (x, y) in zip(poly.points, points):
        p.co = (x, y, 0.2, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def uniform(tree, label, owner, data_path, index=None, expression='v'):
    node = tree.nodes.new('ShaderNodeValue')
    node.name = node.label = label
    driver = node.outputs[0].driver_add('default_value').driver
    driver.type = 'SCRIPTED'
    var = driver.variables.new()
    var.name = 'v'
    var.type = 'SINGLE_PROP'
    var.targets[0].id_type = 'SCENE' if isinstance(owner, bpy.types.Scene) else 'OBJECT'
    var.targets[0].id = owner
    var.targets[0].data_path = data_path + (f'[{index}]' if index is not None else '')
    driver.expression = expression
    return node.outputs[0]


def neuron_material(name, scene, arm_a, arm_b):
    """Two coherent hidden ports, square-law detection, threshold output."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    def op(kind, a, b=None, label=None):
        node = tree.nodes.new('ShaderNodeMath')
        node.operation = kind
        node.label = label or kind
        for socket, value in zip(node.inputs, (a, b)):
            if value is None:
                continue
            if isinstance(value, (float, int)):
                socket.default_value = value
            else:
                tree.links.new(value, socket)
        return node.outputs[0]

    a = uniform(tree, 'ARM A - scene X [BU]', arm_a, 'location', 0)
    b = uniform(tree, 'ARM B - scene X [BU]', arm_b, 'location', 0)
    k = uniform(tree, 'Wave number [rad/BU]', scene, '["wavelength_BU"]',
                expression='6.283185307179586 / max(v, 0.000001)')
    power = uniform(tree, 'Input power', scene, '["input_power"]')
    threshold = uniform(tree, 'Activation threshold', scene, '["threshold"]')
    phase = op('MULTIPLY', op('SUBTRACT', a, b), k, 'Relative optical phase')
    cosine = op('COSINE', phase)
    dark = op('MULTIPLY', op('SUBTRACT', 1.0, cosine), 0.5, 'Dark port |E|^2')
    bright = op('SUBTRACT', 1.0, dark, 'Bright port |E|^2')
    dark = op('MULTIPLY', dark, power, 'Dark detected power')
    bright = op('MULTIPLY', bright, power, 'Bright detected power')
    activation = op('GREATER_THAN', dark, threshold, 'Neuron activation')
    return mat, (dark, bright, activation)


def port_material(source, socket, name):
    # Copies preserve the driver target bindings; select the output by node name.
    mat = source.copy()
    mat.name = name
    tree = mat.node_tree
    port = tree.nodes[socket.node.name].outputs[socket.name]
    light = tree.nodes.new('ShaderNodeEmission')
    tree.links.new(port, light.inputs['Color'])
    light.inputs['Strength'].default_value = 1.0
    out = tree.nodes.new('ShaderNodeOutputMaterial')
    tree.links.new(light.outputs[0], out.inputs['Surface'])
    # Arrange the editable computational graph for inspection.
    for i, node in enumerate(tree.nodes):
        node.location = ((i // 4) * 230, -(i % 4) * 190)
    return mat


def build(destination):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.name = 'Neuro3D - Render Network'
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.world.color = (0, 0, 0)
    scene['wavelength_BU'] = 0.1
    scene['input_power'] = 1.0
    scene['threshold'] = 0.6
    scene['implementation'] = 'EEVEE shader arithmetic; no raycast propagation'
    scene['phase_encoding'] = 'Relative X offset in BU; half-wavelength represents bit 1'
    for key, low, high in [('wavelength_BU', 0.001, 1), ('input_power', 0, 1),
                           ('threshold', 0, 1)]:
        scene.id_properties_ui(key).update(min=low, max=high)
    base = emission('Midnight background', (0.005, 0.009, 0.02))
    panel = emission('Slate panels', (0.012, 0.021, 0.037))
    cyan = emission('Cyan source A', (0.03, 0.8, 1))
    violet = emission('Violet source B', (0.54, 0.17, 1))
    white = emission('Typography white', (0.78, 0.88, 1))
    muted = emission('Typography muted', (0.23, 0.37, 0.5))
    frame = emission('Detector rim', (0.055, 0.13, 0.2))
    box('Background', 0, 0, 20, 14, base, -0.1)
    text('NEURO3D', -6.65, 4.08, 0.55, white)
    text('COHERENT NEURON / RENDER-NATIVE LAB', -2.45, 4.18, 0.19, cyan)
    text('SCENE PHASES > INTERFERENCE > PHOTODETECTION > ACTIVATION',
         -6.65, 3.6, 0.15, muted)
    for x, label in zip(DETECTORS, ('DARK', 'BRIGHT', 'OUTPUT')):
        text(label, x, 3.57, 0.15, muted, 'CENTER')
    for lane, ((a, b), y) in enumerate(zip(LANES, YS)):
        box(f'Lane_{lane}', 0, y, 13.5, 1.55, panel)
        text(f'{a}  {b}', -6.25, y-0.12, 0.35, white)
        text(f'INPUT {lane+1:02}', -6.25, y-0.52, 0.12, muted)
        disk(f'SourceA_{lane}', -4.8, y+0.4, 0.12, cyan)
        disk(f'SourceB_{lane}', -4.8, y-0.4, 0.12, violet)
        aa = box(f'Phase_A_{lane}', -2.3+a*0.05, y+0.4, 0.18, 0.3, cyan, 0.28)
        bb = box(f'Phase_B_{lane}', -2.3+b*0.05, y-0.4, 0.18, 0.3, violet, 0.28)
        for obj, bit in ((aa, a), (bb, b)):
            obj['bit'] = bit
            obj['role'] = 'Scene-owned symbolic optical path offset; not traced mirror'
        line(f'ArmA_{lane}', [(-4.8,y+0.4),(-2.3,y+0.4),(0.15,y)], cyan)
        line(f'ArmB_{lane}', [(-4.8,y-0.4),(-2.3,y-0.4),(0.15,y)], violet)
        mixer = box(f'Mixer_{lane}', 0.15, y, 0.32, 0.32, white, 0.3)
        mixer.rotation_euler.z = 0.7853981633974483
        line(f'DetectorLink_{lane}', [(0.4,y),(5.75,y)], frame, 0.017)
        mat, ports = neuron_material(f'Neuron_{lane}', scene, aa, bb)
        for index, (x, socket) in enumerate(zip(DETECTORS, ports)):
            disk(f'Rim_{lane}_{index}', x, y, 0.37, frame)
            disk(f'Detector_{lane}_{index}', x, y, 0.29,
                 port_material(mat, socket, f'Neuron_{lane}_port_{index}'), 0.3)
        text('PHASE ENCODERS', -2.3, y-0.66, 0.12, muted, 'CENTER')
        text('MIX', 0.15, y-0.66, 0.12, muted, 'CENTER')
    text('XOR / 2 PHASE INPUTS / 2 COHERENT PORTS / 1 THRESHOLD',
         -6.65, -3.85, 0.16, white)
    text('DIGITAL GPU SHADER MODEL  -  NO PHYSICAL OPTICS OR SPEEDUP CLAIM',
         -6.65, -4.2, 0.135, muted)
    bpy.ops.object.camera_add(location=(0, 0, 20))
    camera = bpy.context.object
    camera.name = 'Lab overview'
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 14.8
    scene.camera = camera
    # Opening the .blend is enough; no external script/handler needed for inference.
    note = bpy.data.texts.new('START HERE - Neuro3D')
    note.write('Render with F12. Move Phase_A/B X to change relative phase.\n'
               'Scene custom properties control wavelength_BU, input_power, threshold.\n'
               'Material nodes compute outputs; drivers only deliver uniforms.\n'
               'This is an idealized digital coherent neuron, not raycast transport.\n')
    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
    bpy.context.preferences.filepaths.save_version = 0
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination))
    print(f'NEURO3D_BUILT {destination}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--blend', required=True)
    build(parser.parse_args(sys.argv[sys.argv.index('--')+1:]).blend)
