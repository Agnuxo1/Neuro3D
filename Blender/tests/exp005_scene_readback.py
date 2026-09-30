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


def evaluated_optics(scene, ids, depsgraph):
    """Reject divergence from the viewport depsgraph used for scene.ray_cast.

No graph is allowed for legacy CPU diagnostics, explicitly marked unchecked.
This does NOT validate render/OptiX geometry or optical propagation.
"""
    if depsgraph is None:
        return None
    if depsgraph.mode != 'VIEWPORT':
        raise ValueError('viewport raycast depsgraph required; render parity not implemented')
    evaluated = {}
    for ob in depsgraph.objects:
        original = ob.original
        if original.get('kind') in ('mirror','bs','det','escape'):
            if original.name not in ids or original.name in evaluated:
                raise ValueError('evaluated optical set differs or duplicates declared objects')
            evaluated[original.name] = ob
    if set(evaluated) != set(ids):
        raise ValueError('declared optics missing from evaluated depsgraph')
    for name, ob in evaluated.items():
        base = scene.objects[name]
        if hasattr(base,'as_pointer') and hasattr(ob.original,'as_pointer'):
            same = base.as_pointer() == ob.original.as_pointer()
        else:
            same = ob.original is base
        if not same or ob.type != 'MESH' or ob.get('kind') != base.get('kind'):
            raise ValueError('evaluated identity/kind mismatch')
        if base.get('kind') == 'mirror' and ob.get('phase_rad') != base.get('phase_rad'):
            raise ValueError('evaluated optical phase mismatch')
        if base.get('kind') == 'bs' and ob.get('power_transmittance') != base.get('power_transmittance'):
            raise ValueError('evaluated splitter transmittance mismatch')
        actual = [vector3(ob.matrix_world @ v.co,'evaluated vertex') for v in ob.data.vertices]
        declared = [vector3(base.matrix_world @ v.co,'base vertex') for v in base.data.vertices]
        if actual != declared or [list(p.vertices) for p in ob.data.polygons] != [list(p.vertices) for p in base.data.polygons]:
            raise ValueError('evaluated geometry differs from exported base mesh')
    return evaluated


def export_snapshot(scene, *, depsgraph=None, view_layer=None):
    """Duck-typed for lightweight tests; the production input is a bpy scene."""
    ids = json.loads(scene['optical_object_ids'])
    if (not isinstance(ids, list) or not ids or
            any(not isinstance(n, str) or not n for n in ids) or len(set(ids)) != len(ids)):
        raise ValueError('explicit unique optical object IDs required')
    if any(obj.get('kind') in ('mirror','bs','det','escape') and obj.name not in ids
           for obj in scene.objects):
        raise ValueError('optical object omitted from scene declaration')
    evaluated = evaluated_optics(scene,ids,depsgraph)
    schema=scene.get('optical_contract','exp005-readback-v1')
    if schema not in ('exp005-readback-v1','exp005-readback-v2'):
        raise ValueError('unsupported scene optical contract')
    result = {'schema': schema, 'lambda_BU': scene['lambda_BU'],
              'objects': {}, 'sources': [],
              'evaluated_optics_checked': evaluated is not None,
              'evaluated_optical_ids': sorted(evaluated) if evaluated is not None else [],
              'evaluation_scope': 'viewport raycast only; no render/RT or wave validation'}
    for name in ids:
        obj = scene.objects[name]  # missing declared object must fail closed
        if obj.type != 'MESH':
            raise ValueError(f'{name}: optical mesh required')
        if getattr(obj,'hide_viewport',False) or getattr(obj,'hide_render',False):
            raise ValueError(f'{name}: hidden optics unsupported')
        if hasattr(obj,'hide_get') and obj.hide_get(view_layer=view_layer):
            raise ValueError(f'{name}: optical object hidden in view layer')
        determinant = finite_number(obj.matrix_world.determinant(),'world determinant')
        if determinant <= 0:
            raise ValueError(f'{name}: negative/singular world orientation unsupported')
        if obj.modifiers:
            raise ValueError(f'{name}: evaluated modifiers unsupported; no silent base-mesh export')
        record = {'kind': obj['kind']}
        if record['kind']=='bs' and (schema=='exp005-readback-v2' or 'power_transmittance' in obj):
            record['power_transmittance']=obj['power_transmittance']
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
    bpy.context.view_layer.update()
    snapshot = export_snapshot(bpy.context.scene,
                               depsgraph=bpy.context.evaluated_depsgraph_get(),
                               view_layer=bpy.context.view_layer)
    snapshot['blend_sha256'] = hashlib.sha256(blend.read_bytes()).hexdigest()
    snapshot['blender_version'] = bpy.app.version_string
    Path(args.output).resolve().write_text(json.dumps(snapshot, indent=2)+'\n', encoding='utf-8')
    print('EXP005_READBACK_EXPORTED', len(snapshot['objects']))


if __name__ == '__main__':
    main()
