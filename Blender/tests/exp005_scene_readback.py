"""EXP-005 export bridge; runtime execution is NOT yet validated.

The CLI explicitly reopens a supplied .blend. Export stores actual world-space
mesh vertices/faces rather than reconstructing geometry from an external fixture.
No GPU, rendering, raycast, propagation or oracle is implemented in this bridge.
Even a headless run must use the shared resource reservation before Blender starts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp005_scene_properties import decode_scene, finite_number


def vector3(value, label):
    if len(value) != 3:
        raise ValueError(f'{label}: three components required')
    return [finite_number(v, label) for v in value]


def export_snapshot(scene):
    """Duck-typed for lightweight tests; the production input is a bpy scene."""
    ids = json.loads(scene['optical_object_ids'])
    if (not isinstance(ids, list) or not ids or
            any(not isinstance(n, str) or not n for n in ids) or len(set(ids)) != len(ids)):
        raise ValueError('explicit unique optical object IDs required')
    if any(obj.get('kind') in ('mirror','bs','det','escape') and obj.name not in ids
           for obj in scene.objects):
        raise ValueError('optical object omitted from scene declaration')
    result = {'schema': 'exp005-readback-v1', 'lambda_BU': scene['lambda_BU'],
              'objects': {}, 'sources': []}
    for name in ids:
        obj = scene.objects[name]  # missing declared object must fail closed
        if obj.type != 'MESH':
            raise ValueError(f'{name}: optical mesh required')
        if obj.modifiers:
            raise ValueError(f'{name}: evaluated modifiers unsupported; no silent base-mesh export')
        record = {'kind': obj['kind']}
        if record['kind'] == 'mirror':
            record['phase_rad'] = obj['phase_rad']
        if record['kind'] in ('det','escape'):
            record['mode_origin_BU'] = vector3(obj['mode_origin_BU'],'mode reference')
            record['mode_direction'] = vector3(obj['mode_direction'],'mode direction')
            if sum(v*v for v in record['mode_direction']) <= 0:
                raise ValueError('nonzero terminal mode direction required')
        vertices = [vector3(obj.matrix_world @ vert.co, 'world vertex')
                    for vert in obj.data.vertices]
        faces = [list(face.vertices) for face in obj.data.polygons]
        if not vertices or not faces:
            raise ValueError(f'{name}: nonempty mesh required')
        for face in faces:
            if (len(face) < 3 or len(set(face)) != len(face) or
                    any(isinstance(i, bool) or not isinstance(i, int) or
                        i < 0 or i >= len(vertices) for i in face)):
                raise ValueError(f'{name}: invalid face indices')
        record.update(vertices_world_BU=vertices, faces=faces)
        result['objects'][name] = record
    optics = decode_scene(result)  # properties remain mandatory; no fixture defaults
    result['lambda_BU'] = optics.wavelength_BU
    for name, phase in optics.phases_rad.items():
        result['objects'][name]['phase_rad'] = phase
    sources = json.loads(scene['optical_sources'])
    if not isinstance(sources, list) or not sources:
        raise ValueError('nonempty scene-owned sources required')
    names = set()
    for source in sources:
        name = source['id']
        if not isinstance(name, str) or not name or name in names:
            raise ValueError('unique source IDs required')
        names.add(name)
        position = vector3(source['position_BU'], 'source position')
        direction = vector3(source['direction'], 'source direction')
        if sum(v*v for v in direction) <= 0:
            raise ValueError('nonzero source direction required')
        field = source['field_reim']
        if len(field) != 2:
            raise ValueError('source field needs real/imag pair')
        result['sources'].append({'id': name, 'position_BU': position,
                                  'direction': direction,
                                  'field_reim': [finite_number(v, 'source field') for v in field]})
    # Other meshes are recorded, not quietly asserted to be non-interacting.
    # The future runner/oracle must account for or explicitly exclude them.
    result['undeclared_meshes'] = [obj.name for obj in scene.objects
                                 if obj.type == 'MESH' and obj.name not in ids]
    return result


def main():
    import bpy  # imported ONLY inside Blender CLI execution, not CPU unit tests
    parser = argparse.ArgumentParser()
    parser.add_argument('--blend', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    blend = Path(args.blend).resolve()
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    snapshot = export_snapshot(bpy.context.scene)
    snapshot['blend_sha256'] = hashlib.sha256(blend.read_bytes()).hexdigest()
    snapshot['blender_version'] = bpy.app.version_string
    Path(args.output).resolve().write_text(json.dumps(snapshot, indent=2)+'\n', encoding='utf-8')
    print('EXP005_READBACK_EXPORTED', len(snapshot['objects']))


if __name__ == '__main__':
    main()
